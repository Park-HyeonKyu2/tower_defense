"""
[담당: 이서진 - 게임 엔진/통합]

게임 엔진: 전체 게임 루프와 상태 전이를 관리합니다.
- 게임 초기화 (reset)
- 행동 처리 (step): 구매, 강화, 판매, 재배치, 웨이브 시작
- 매 프레임 업데이트 (update): 시간 경과에 따른 몬스터 이동 및 자동 전투
- 게임 상태 조회 (get_state): UI용 현재 상태 반환
- 상태 전이 로직: 준비 → 웨이브 → 정산 → 준비

이 모듈은 다른 game/* 모듈들을 통합하여 게임 흐름을 제어합니다.
UI는 직접 게임 상태를 수정하지 않고 engine을 통해서만 상호작용합니다.
"""

from typing import Optional
from game.state import GameState, GamePhase
from game.actions import Action
from game.map import GameMap
from game.tower import Tower
from game.combat import Combat
from game.enemy import Enemy
from game.wave import WaveManager
from game.economy import Economy


class Game:
    """
    게임 엔진 클래스
    """

    def __init__(self):
        """게임 엔진 초기화"""
        self.state = None
        self.map = GameMap()
        self.combat = Combat()
        self.wave_manager = WaveManager()
        self.economy = Economy()
        self.elapsed_time = 0.0

    def reset(self, seed: Optional[int] = None) -> GameState:
        """
        게임을 초기 상태로 재설정합니다.

        Args:
            seed: 난수 재현성을 위한 시드값

        Returns:
            초기화된 GameState
        """
        self.state = GameState()
        self.elapsed_time = 0.0

        # 난수 시드 설정 (랜덤 타워 구매 재현용)
        if seed is not None:
            import random
            random.seed(seed)

        # 웨이브 매니저 초기화
        self.wave_manager.reset()

        return self.state

    def step(self, action: Action) -> GameState:
        """
        이산 행동 처리 (구매, 강화, 판매, 재배치, 웨이브 시작)

        Args:
            action: 수행할 행동

        Returns:
            업데이트된 GameState
        """
        if self.state.phase == GamePhase.PREPARATION:
            if action.type == "BUY":
                self._handle_buy(action.slot_id)
            elif action.type == "UPGRADE":
                self._handle_upgrade(action.slot_id)
            elif action.type == "SELL":
                self._handle_sell(action.slot_id)
            elif action.type == "RELOCATE":
                self._handle_relocate(action.from_slot_id, action.to_slot_id)
            elif action.type == "START_WAVE":
                self._start_wave()

        return self.state

    def update(self, dt: float) -> None:
        """
        시간 경과에 따른 게임 상태 업데이트
        - 몬스터 이동
        - 타워 자동 공격
        - 웨이브 진행 상황 확인

        Args:
            dt: 경과 시간 (초)
        """
        if self.state.phase != GamePhase.WAVE_ACTIVE:
            return

        self.elapsed_time += dt

        # 몬스터 이동 및 공격 처리
        self._update_wave(dt)

        # 웨이브 종료 확인
        if self.wave_manager.is_wave_complete():
            self._transition_to_settlement()

    def get_state(self) -> GameState:
        """
        UI용 현재 게임 상태 반환 (상태 변경하지 않음)

        Returns:
            GameState
        """
        return self.state

    # ===== 내부 메서드 =====

    def _handle_buy(self, slot_id: int) -> None:
        """타워 구매 처리"""
        # 유효성 검사는 economy 모듈에서 수행
        if self.economy.can_buy(self.state, slot_id):
            tower_type = self.economy.buy_random_tower(self.state, slot_id)
            self.state.gold -= 100
            self.state.tower_slots[slot_id] = True
            self.state.towers[slot_id] = {
                "type": tower_type,
                "level": 1,
                "slot_id": slot_id
            }
            self.state.actions_taken_this_wave += 1

    def _handle_upgrade(self, slot_id: int) -> None:
        """타워 강화 처리"""
        if self.economy.can_upgrade(self.state, slot_id):
            cost = self.economy.get_upgrade_cost(self.state, slot_id)
            self.state.gold -= cost
            self.state.towers[slot_id]["level"] += 1
            self.state.actions_taken_this_wave += 1

    def _handle_sell(self, slot_id: int) -> None:
        """타워 판매 처리"""
        if self.economy.can_sell(self.state, slot_id):
            refund = self.economy.get_sell_refund(self.state, slot_id)
            self.state.gold += refund
            del self.state.towers[slot_id]
            self.state.tower_slots[slot_id] = False
            self.state.actions_taken_this_wave += 1

    def _handle_relocate(self, from_slot: int, to_slot: int) -> None:
        """타워 재배치 처리"""
        if self.economy.can_relocate(self.state, from_slot, to_slot):
            tower = self.state.towers.pop(from_slot)
            tower["slot_id"] = to_slot
            self.state.towers[to_slot] = tower
            self.state.tower_slots[from_slot] = False
            self.state.tower_slots[to_slot] = True
            self.state.actions_taken_this_wave += 1

    def _start_wave(self) -> None:
        """웨이브 시작"""
        if self.economy.can_start_wave(self.state):
            self.state.phase = GamePhase.WAVE_ACTIVE
            self.state.current_wave += 1
            self.state.actions_taken_this_wave = 0
            # 웨이브 매니저에서 몬스터 스폰 시작
            self.wave_manager.start_wave(self.state.current_stage)

    def _update_wave(self, dt: float) -> None:
        """웨이브 진행 중 업데이트"""
        # 몬스터 이동
        for enemy in self.state.enemies:
            # enemy 업데이트 로직
            pass

        # 타워 공격
        for slot_id, tower_data in self.state.towers.items():
            # combat 모듈을 통한 공격 처리
            pass

    def _transition_to_settlement(self) -> None:
        """정산 단계로 전이"""
        self.state.phase = GamePhase.SETTLEMENT
        # 스테이지 진행 여부 확인
        if self.state.current_stage >= 30:  # 최대 스테이지
            self.state.phase = GamePhase.VICTORY
        else:
            # 정산 처리 후 다시 준비 단계로
            self.state.current_stage += 1
            self.state.phase = GamePhase.PREPARATION
            self.state.actions_taken_this_wave = 0
