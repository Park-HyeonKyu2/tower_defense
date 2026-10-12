"""
[담당: 이승연 - 몬스터/웨이브 시스템]

웨이브 시스템 단위 테스트:
- 웨이브 시작 및 종료
- 몬스터 스폰
- 경로 진행
- 보스 생성
"""

import unittest
from game.wave import WaveManager
from game.enemy import Enemy, EnemyType


class TestWaveManager(unittest.TestCase):
    """웨이브 매니저 테스트"""

    def setUp(self):
        """각 테스트 전 초기화"""
        self.wave_manager = WaveManager()
        self.path = [(0, 7), (5, 7), (10, 3), (15, 8), (19, 15)]

    def test_wave_start(self):
        """웨이브 시작 테스트"""
        self.wave_manager.start_wave(stage=1)
        self.assertEqual(self.wave_manager.current_wave, 1)
        self.assertGreater(len(self.wave_manager.spawn_queue), 0)

    def test_spawn_enemies(self):
        """몬스터 스폰 테스트"""
        self.wave_manager.start_wave(stage=1)
        spawned = self.wave_manager.update(dt=2.0, path=self.path)

        self.assertGreater(len(spawned), 0)

    def test_wave_complete(self):
        """웨이브 완료 확인 테스트"""
        self.wave_manager.start_wave(stage=1)

        # 초기에는 미완료
        self.assertFalse(self.wave_manager.is_wave_complete([]))

        # 모든 몬스터가 처치되고 스폰 완료 후 완료
        while self.wave_manager.spawn_queue:
            self.wave_manager.update(dt=1.0, path=self.path)

        self.assertTrue(self.wave_manager.is_wave_complete([]))


class TestEnemy(unittest.TestCase):
    """몬스터 테스트"""

    def setUp(self):
        """각 테스트 전 초기화"""
        self.path = [(0, 0), (5, 5), (10, 0), (15, 5)]

    def test_enemy_creation(self):
        """몬스터 생성 테스트"""
        enemy = Enemy(EnemyType.BASIC, self.path)
        self.assertEqual(enemy.max_health, 30)
        self.assertEqual(enemy.speed, 1.0)
        self.assertTrue(enemy.is_alive)

    def test_enemy_movement(self):
        """몬스터 이동 테스트"""
        enemy = Enemy(EnemyType.BASIC, self.path)
        pos_before = enemy.get_current_position()

        # 1초 이동
        reached = enemy.move(dt=1.0)
        pos_after = enemy.get_current_position()

        self.assertNotEqual(pos_before, pos_after)
        self.assertFalse(reached)  # 아직 경로 완주 안 함

    def test_enemy_take_damage(self):
        """몬스터 피해 테스트"""
        enemy = Enemy(EnemyType.BASIC, self.path)
        result = enemy.take_damage(10)

        self.assertEqual(enemy.health, 20)
        self.assertFalse(result)  # 아직 살아있음

        # 처치
        result = enemy.take_damage(30)
        self.assertTrue(result)
        self.assertFalse(enemy.is_alive)


if __name__ == "__main__":
    unittest.main()
