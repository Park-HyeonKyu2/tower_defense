"""
[담당: 윤재빈 - 경제/타워 관리]

게임 행동 정의 및 처리:
- Action 클래스: 게임 행동의 표준 형식 정의
- 행동 종류: BUY(구매), UPGRADE(강화), SELL(판매), RELOCATE(재배치), START_WAVE(웨이브 시작)
- 행동 유효성 검사: economy.py의 검증 함수와 통합
- 향후 강화학습의 행동 공간 정의에 사용됨

economy.py와 함께 타워 관리를 담당합니다.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class ActionType(Enum):
    """행동 종류"""
    BUY = "BUY"              # 타워 구매
    UPGRADE = "UPGRADE"      # 타워 강화
    SELL = "SELL"            # 타워 판매
    RELOCATE = "RELOCATE"    # 타워 재배치
    START_WAVE = "START_WAVE"  # 웨이브 시작


@dataclass
class Action:
    """
    게임 행동을 나타내는 클래스
    engine.py의 step() 함수에 전달됩니다.
    """
    action_type: ActionType
    slot_id: Optional[int] = None      # BUY, UPGRADE, SELL에서 사용
    from_slot_id: Optional[int] = None  # RELOCATE에서 사용
    to_slot_id: Optional[int] = None    # RELOCATE에서 사용

    # 호환성을 위한 string 속성
    @property
    def type(self) -> str:
        """문자열 형식의 행동 타입"""
        return self.action_type.value


class ActionValidator:
    """행동 유효성 검사자"""

    @staticmethod
    def is_valid_action(action: Action, state) -> bool:
        """
        행동이 유효한지 검사

        Args:
            action: 검사할 행동
            state: 현재 게임 상태

        Returns:
            유효 여부
        """
        if action.action_type == ActionType.BUY:
            from game.economy import Economy
            economy = Economy()
            return economy.can_buy(state, action.slot_id)

        elif action.action_type == ActionType.UPGRADE:
            from game.economy import Economy
            economy = Economy()
            return economy.can_upgrade(state, action.slot_id)

        elif action.action_type == ActionType.SELL:
            from game.economy import Economy
            economy = Economy()
            return economy.can_sell(state, action.slot_id)

        elif action.action_type == ActionType.RELOCATE:
            from game.economy import Economy
            economy = Economy()
            return economy.can_relocate(state, action.from_slot_id, action.to_slot_id)

        elif action.action_type == ActionType.START_WAVE:
            from game.economy import Economy
            economy = Economy()
            return economy.can_start_wave(state)

        return False

    @staticmethod
    def get_all_valid_actions(state) -> list:
        """
        현재 상태에서 가능한 모든 행동 반환
        (강화학습의 행동 마스킹에 사용)

        Args:
            state: 현재 게임 상태

        Returns:
            가능한 Action 리스트
        """
        from game.economy import Economy
        from game.state import GamePhase

        valid_actions = []
        economy = Economy()

        # 준비 단계에서만 행동 가능
        if state.phase != GamePhase.PREPARATION:
            # START_WAVE만 가능한 경우도 추가 가능
            if economy.can_start_wave(state):
                valid_actions.append(Action(ActionType.START_WAVE))
            return valid_actions

        # BUY 행동: 모든 빈 슬롯
        for slot_id in range(24):
            if economy.can_buy(state, slot_id):
                valid_actions.append(Action(ActionType.BUY, slot_id=slot_id))

        # UPGRADE 행동: 모든 타워
        for slot_id in range(24):
            if economy.can_upgrade(state, slot_id):
                valid_actions.append(Action(ActionType.UPGRADE, slot_id=slot_id))

        # SELL 행동: 모든 타워
        for slot_id in range(24):
            if economy.can_sell(state, slot_id):
                valid_actions.append(Action(ActionType.SELL, slot_id=slot_id))

        # RELOCATE 행동: 모든 타워 → 모든 빈 슬롯
        for from_slot in range(24):
            for to_slot in range(24):
                if economy.can_relocate(state, from_slot, to_slot):
                    valid_actions.append(
                        Action(ActionType.RELOCATE, from_slot_id=from_slot, to_slot_id=to_slot)
                    )

        # START_WAVE 행동
        if economy.can_start_wave(state):
            valid_actions.append(Action(ActionType.START_WAVE))

        return valid_actions
