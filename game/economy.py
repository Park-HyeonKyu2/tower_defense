"""
[담당: 윤재빈 - 경제/타워 관리]

경제 시스템: 골드 관리 및 타워 구매/강화/판매/재배치
- 골드 획득 (몬스터 처치)
- 골드 소비 (타워 구매, 강화)
- 타워 판매 (투자액의 60% 환급)
- 빈 슬롯 재배치 (무료)
- 행동 조건 검증 (골드 부족, 슬롯 점유, 최대 레벨 등)
- 준비 단계 행동 제한 (최대 20회)

향후 강화학습의 행동 마스킹에 동일한 유효성 검사 함수를 재사용할 수 있도록 설계합니다.
"""

from typing import Optional
from game.state import GameState
from game.tower import Tower


class Economy:
    """경제 시스템 관리자"""

    # 타워 구매 비용
    TOWER_BUY_COST = 100

    # 환급률 (판매 시 투자액의 60% 반환)
    SELL_REFUND_RATE = 0.6

    def __init__(self):
        """경제 시스템 초기화"""
    # ===== 검증 함수 (유효성 검사) =====

    def can_buy(self, state: GameState, slot_id: int) -> bool:
        """
        타워 구매 가능 여부 확인

        Args:
            state: 게임 상태
            slot_id: 구매할 슬롯 ID

        Returns:
            구매 가능 여부
        """

        # 유효한 슬롯인지 확인
        if not state.is_valid_slot(slot_id):
            return False

        # 슬롯이 비어있는지 확인
        if not state.is_slot_empty(slot_id):
            return False

        # 골드 충분한지 확인
        if state.gold < self.TOWER_BUY_COST:
            return False

        # 준비 단계 행동 제한 확인
        if state.actions_taken_this_wave >= 20:
            return False

        return True

    def can_upgrade(self, state: GameState, slot_id: int) -> bool:
        """
        타워 강화 가능 여부 확인

        Args:
            state: 게임 상태
            slot_id: 강화할 타워의 슬롯 ID

        Returns:
            강화 가능 여부
        """
        # 슬롯에 타워가 있는지 확인
        if not state.has_tower(slot_id):
            return False

        tower = state.towers[slot_id]

        # 최대 레벨 확인
        if tower["level"] >= 5:
            return False

        # 강화 비용 확인
        cost = self.get_upgrade_cost(state, slot_id)
        if state.gold < cost:
            return False

        # 준비 단계 행동 제한 확인
        if state.actions_taken_this_wave >= 20:
            return False

        return True

    def can_sell(self, state: GameState, slot_id: int) -> bool:
        """
        타워 판매 가능 여부 확인

        Args:
            state: 게임 상태
            slot_id: 판매할 타워의 슬롯 ID

        Returns:
            판매 가능 여부
        """
        # 슬롯에 타워가 있는지 확인
        if not state.has_tower(slot_id):
            return False

        # 준비 단계 행동 제한 확인
        if state.actions_taken_this_wave >= 20:
            return False

        return True

    def can_relocate(self, state: GameState, from_slot: int, to_slot: int) -> bool:
        """
        타워 재배치 가능 여부 확인
        (빈 슬롯으로 무료 이동)

        Args:
            state: 게임 상태
            from_slot: 현재 타워의 슬롯 ID
            to_slot: 이동할 슬롯 ID

        Returns:
            재배치 가능 여부
        """
        
        # 두 슬롯 모두 유효한지 확인
        if not state.is_valid_slot(from_slot) or not state.is_valid_slot(to_slot):
            return False

        # from_slot에 타워가 있는지 확인
        if not state.has_tower(from_slot):
            return False

        # to_slot이 비어있는지 확인
        if not state.is_slot_empty(to_slot):
            return False

        # 준비 단계 행동 제한 확인
        if state.actions_taken_this_wave >= 20:
            return False
        
        return True

    def can_start_wave(self, state: GameState) -> bool:
        """
        웨이브 시작 가능 여부 확인

        Args:
            state: 게임 상태

        Returns:
            웨이브 시작 가능 여부
        """
        # 준비 단계인지 확인
        from game.state import GamePhase
        if state.phase != GamePhase.PREPARATION:
            return False

        return True

    # ===== 비용 계산 함수 =====

    def get_upgrade_cost(self, state: GameState, slot_id: int) -> int:
        """
        타워 강화 비용 계산

        Args:
            state: 게임 상태
            slot_id: 타워의 슬롯 ID

        Returns:
            강화 비용 (골드)
        """
        if not state.has_tower(slot_id):
            return 0

        tower = state.towers[slot_id]
        level = tower["level"]

        # 비용 = 50 * 현재 레벨
        return 50 * level

    def get_sell_refund(self, state: GameState, slot_id: int) -> int:
        """
        타워 판매 환급액 계산
        (누적 투자액의 60%)

        Args:
            state: 게임 상태
            slot_id: 판매할 타워의 슬롯 ID

        Returns:
            환급액 (골드)
        """
        if not state.has_tower(slot_id):
            return 0

        tower = state.towers[slot_id]

        # 누적 투자액 계산
        # 구매: 100G + 강화: 50G*(레벨-1)
        purchase_cost = 100
        upgrade_costs = sum(50 * i for i in range(1, tower["level"]))
        total_investment = purchase_cost + upgrade_costs

        # 60% 환급
        return int(total_investment * self.SELL_REFUND_RATE)

    # ===== 타워 구매 로직 =====

    def buy_random_tower(self, state: GameState, slot_id: int) -> str:
        """
        4가지 타워 중 랜덤 선택하여 구매

        Args:
            state: 게임 상태
            slot_id: 구매할 슬롯 ID

        Returns:
            선택된 타워 종류 (문자열: "ARCHER", "CANNON", "ICE", "LIGHTNING")
        """
        import random

        tower_types = ["ARCHER", "CANNON", "ICE", "LIGHTNING"]
        selected = random.choice(tower_types)

        return selected

    # ===== 행동 실행 함수 (경제 처리만, 상태는 engine.py에서 관리) =====

    def apply_buy(self, state: GameState, slot_id: int, tower_type: str) -> bool:
        """
        타워 구매 경제 처리

        Args:
            state: 게임 상태
            slot_id: 구매할 슬롯 ID
            tower_type: 타워 종류

        Returns:
            성공 여부
        """
        if not self.can_buy(state, slot_id):
            return False

        state.gold -= self.TOWER_BUY_COST
        return True

    def apply_upgrade(self, state: GameState, slot_id: int) -> bool:
        """
        타워 강화 경제 처리

        Args:
            state: 게임 상태
            slot_id: 강화할 타워의 슬롯 ID

        Returns:
            성공 여부
        """
        if not self.can_upgrade(state, slot_id):
            return False

        cost = self.get_upgrade_cost(state, slot_id)
        state.gold -= cost
        return True

    def apply_sell(self, state: GameState, slot_id: int) -> bool:
        """
        타워 판매 경제 처리

        Args:
            state: 게임 상태
            slot_id: 판매할 타워의 슬롯 ID

        Returns:
            성공 여부
        """
        if not self.can_sell(state, slot_id):
            return False

        refund = self.get_sell_refund(state, slot_id)
        state.gold += refund
        return True

    #=========돈 획득 여부 및 갱신=======
    def get_money(self,gold,state):
        state.gold+=gold
        return True
