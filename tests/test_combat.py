"""
[담당: 오승아 - 타워/전투 시스템]

전투 시스템 단위 테스트:
- 공격 대상 선정
- 피해 계산
- 광역 공격
- 둔화 효과
- 연쇄 공격
"""

import unittest
from game.combat import Combat
from game.tower import Tower, TowerType


class TestCombat(unittest.TestCase):
    """전투 시스템 테스트"""

    def setUp(self):
        """각 테스트 전 초기화"""
        self.combat = Combat()

    def test_get_target_in_range(self):
        """사거리 내 적 선정 테스트"""
        tower_pos = (10, 10)
        tower_range = 5.0

        enemies = [
            {"health": 30, "x": 12, "y": 10, "progress": 0.5},  # 사거리 내
            {"health": 30, "x": 20, "y": 10, "progress": 0.3}   # 사거리 외
        ]

        target = self.combat.get_target(tower_pos, tower_range, enemies)
        self.assertIsNotNone(target)
        self.assertEqual(target["x"], 12)

    def test_apply_damage(self):
        """피해 적용 테스트"""
        enemy = {"health": 30}
        result = self.combat.apply_damage(enemy, 10)

        self.assertEqual(enemy["health"], 20)
        self.assertFalse(result)  # 아직 살아있음

        # 적 처치
        result = self.combat.apply_damage(enemy, 30)
        self.assertTrue(result)  # 사망

    def test_apply_slow_effect(self):
        """둔화 효과 테스트"""
        enemy = {"elapsed_time": 0}
        self.combat.apply_slow_effect(enemy, 0.5, 2.0)

        self.assertIn("status_effects", enemy)
        self.assertIn("slow", enemy["status_effects"])

    def test_apply_splash_damage(self):
        """광역 피해 테스트"""
        enemies = [
            {"health": 30, "x": 10, "y": 10},  # 중심
            {"health": 30, "x": 12, "y": 10},  # 반경 내
            {"health": 30, "x": 20, "y": 10}   # 반경 외
        ]

        damage_count = self.combat.apply_splash_damage((10, 10), 2.0, 15, enemies)

        self.assertEqual(damage_count, 2)  # 2마리 피해


if __name__ == "__main__":
    unittest.main()
