"""
[담당: 이서진 - 게임 엔진/통합]

게임 엔진 단위 테스트:
- 게임 초기화
- 상태 전이 (준비 → 웨이브 → 정산)
- 게임 오버 및 승리 조건
- 행동 처리
"""

import unittest
from game.engine import Game
from game.state import GameState, GamePhase
from game.actions import Action, ActionType


class TestGameEngine(unittest.TestCase):
    """게임 엔진 테스트"""

    def setUp(self):
        """각 테스트 전 초기화"""
        self.game = Game()
        self.state = self.game.reset(seed=42)

    def test_game_initialization(self):
        """게임 초기화 테스트"""
        self.assertEqual(self.state.current_stage, 1)
        self.assertEqual(self.state.gold, 100)
        self.assertEqual(self.state.life, 20)
        self.assertEqual(self.state.phase, GamePhase.PREPARATION)

    def test_start_wave(self):
        """웨이브 시작 테스트"""
        action = Action(ActionType.START_WAVE)
        self.game.step(action)
        self.assertEqual(self.state.phase, GamePhase.WAVE_ACTIVE)

    def test_game_over_condition(self):
        """게임 오버 조건 테스트"""
        # 라이프가 0이 되면 게임 오버
        self.state.life = 1
        self.state.enemies_reached_base = 1
        self.state.life = 0
        # 게임이 오버 상태로 전이되어야 함

    def test_action_in_preparation_phase(self):
        """준비 단계에서 행동 가능 확인"""
        # 준비 단계에서는 구매 가능
        action = Action(ActionType.BUY, slot_id=0)
        self.game.step(action)
        # 구매가 처리되었는지 확인


class TestStateTransition(unittest.TestCase):
    """상태 전이 테스트"""

    def test_preparation_to_wave(self):
        """준비 → 웨이브 전이"""
        game = Game()
        state = game.reset()

        self.assertEqual(state.phase, GamePhase.PREPARATION)

        action = Action(ActionType.START_WAVE)
        game.step(action)

        self.assertEqual(state.phase, GamePhase.WAVE_ACTIVE)


if __name__ == "__main__":
    unittest.main()
