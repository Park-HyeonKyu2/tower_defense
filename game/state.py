"""
[담당: 이서진 - 게임 엔진/통합]

공통 게임 상태 정의:
- 현재 스테이지, 라이프, 골드
- 타워와 몬스터 목록
- 게임 단계 (준비, 웨이브 진행, 정산 등)
- UI에서 조회할 수 있는 모든 정보를 담습니다.

이 클래스는 게임의 "진실의 원천(Single Source of Truth)"입니다.
"""

from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass, field


class GamePhase(Enum):
    """게임 단계"""
    PREPARATION = "preparation"  # 준비 단계 (구매, 강화, 배치)
    WAVE_ACTIVE = "wave_active"  # 웨이브 진행 중 (자동 전투)
    SETTLEMENT = "settlement"    # 정산 단계
    GAME_OVER = "game_over"      # 게임 오버
    VICTORY = "victory"          # 승리


@dataclass
class GameState:
    """게임의 모든 상태를 담는 클래스"""

    # 기본 게임 정보
    current_stage: int = 1
    current_wave: int = 0
    phase: GamePhase = GamePhase.PREPARATION

    # 자원
    gold: int = 100
    life: int = 20

    # 맵 및 타워
    towers: Dict[int, Dict[str, Any]] = field(default_factory=dict)  # slot_id → 타워 데이터
    tower_slots: List[bool] = field(default_factory=lambda: [False] * 24)  # 슬롯별 점유 상태

    # 몬스터
    enemies: List[Dict[str, Any]] = field(default_factory=list)

    # 통계
    enemies_killed: int = 0
    enemies_reached_base: int = 0

    # 준비 단계 행동 횟수 추적
    actions_taken_this_wave: int = 0

    def is_valid_slot(self, slot_id: int) -> bool:
        """슬롯이 유효한지 확인"""
        return 0 <= slot_id < 24

    def is_slot_empty(self, slot_id: int) -> bool:
        """슬롯이 비어있는지 확인"""
        return not self.tower_slots[slot_id]

    def has_tower(self, slot_id: int) -> bool:
        """슬롯에 타워가 있는지 확인"""
        return slot_id in self.towers
