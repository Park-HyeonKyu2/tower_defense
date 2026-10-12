"""
[담당: 윤재빈 - 경제/타워 관리]

경제 시스템 단위 테스트:
- 타워 구매 조건 검증
- 강화 비용 계산
- 판매 환급액 계산
- 행동 제한 (최대 20회)
- 유효성 검사
"""

import unittest
from game.economy import Economy
from game.state import GameState, GamePhase


class TestEconomy(unittest.TestCase):
    """경제 시스템 테스트"""

    def setUp(self):
        """각 테스트 전 초기화"""
        self.economy = Economy()
        self.state = GameState()
        self.state.phase = GamePhase.PREPARATION
        self.state.gold = 200

    def test_can_buy(self):
        """타워 구매 가능 여부 테스트"""
        # 충분한 골드, 빈 슬롯
        self.assertTrue(self.economy.can_buy(self.state, 0))

        # 골드 부족
        self.state.gold = 50
        self.assertFalse(self.economy.can_buy(self.state, 0))

    def test_can_upgrade(self):
        """타워 강화 가능 여부 테스트"""
        # 타워 배치
        self.state.gold = 500
        self.state.towers[0] = {"type": "ARCHER", "level": 1}
        self.state.tower_slots[0] = True

        # 강화 가능
        self.assertTrue(self.economy.can_upgrade(self.state, 0))

        # 최대 레벨
        self.state.towers[0]["level"] = 5
        self.assertFalse(self.economy.can_upgrade(self.state, 0))

    def test_upgrade_cost(self):
        """강화 비용 계산 테스트"""
        self.state.towers[0] = {"type": "ARCHER", "level": 1}
        cost = self.economy.get_upgrade_cost(self.state, 0)
        self.assertEqual(cost, 50)  # 50 * 1

        self.state.towers[0]["level"] = 2
        cost = self.economy.get_upgrade_cost(self.state, 0)
        self.assertEqual(cost, 100)  # 50 * 2

    def test_sell_refund(self):
        """판매 환급액 계산 테스트"""
        # 레벨 1 타워: 구매 100G
        self.state.towers[0] = {"type": "ARCHER", "level": 1}
        refund = self.economy.get_sell_refund(self.state, 0)
        self.assertEqual(refund, int(100 * 0.6))  # 60G

        # 레벨 3 타워: 구매 100G + 강화 50G + 100G = 250G
        self.state.towers[0]["level"] = 3
        refund = self.economy.get_sell_refund(self.state, 0)
        expected = int((100 + 50 + 100) * 0.6)
        self.assertEqual(refund, expected)

    def test_action_limit_per_wave(self):
        """준비 단계 행동 제한 테스트"""
        self.state.actions_taken_this_wave = 19

        # 20번째 행동 가능
        self.assertTrue(self.economy.can_buy(self.state, 0))

        # 21번째 행동 불가
        self.state.actions_taken_this_wave = 20
        self.assertFalse(self.economy.can_buy(self.state, 0))

    def test_can_sell(self):
        """타워 판매 가능 여부 테스트"""
        # 타워 배치
        self.state.towers[0] = {"type": "ARCHER", "level": 1}

        # 판매 가능
        self.assertTrue(self.economy.can_sell(self.state, 0))

        # 행동 제한 도달
        self.state.actions_taken_this_wave = 20
        self.assertFalse(self.economy.can_sell(self.state, 0))


class TestActionValidator(unittest.TestCase):
    """행동 검증 테스트"""

    def test_all_valid_actions(self):
        """유효한 행동 목록 테스트"""
        from game.actions import ActionValidator

        state = GameState()
        state.phase = GamePhase.PREPARATION
        state.gold = 500

        valid_actions = ActionValidator.get_all_valid_actions(state)

        # BUY 행동이 있어야 함
        buy_actions = [a for a in valid_actions if a.action_type.value == "BUY"]
        self.assertGreater(len(buy_actions), 0)


if __name__ == "__main__":
    unittest.main()
