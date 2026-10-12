"""
[담당: 이승연 - 몬스터/웨이브 시스템]

웨이브 시스템: 스테이지별 몬스터 관리
- 웨이브별 몬스터 생성 목록 및 타이밍
- 몬스터 스폰 관리
- 보스 출현 (5스테이지마다)
- 웨이브 완료 조건
- 적 처치 및 기지 도달 이벤트

enemy.py와 함께 웨이브 시스템을 담당합니다.
"""

from typing import List, Dict, Any
from game.enemy import Enemy, EnemyType


class WaveManager:
    """웨이브 관리자"""

    # 스테이지별 웨이브 구성
    STAGE_WAVES = {
        1: [
            {"enemies": [("BASIC", 1.0), ("BASIC", 1.5)], "boss": False},
            {"enemies": [("BASIC", 1.0), ("BASIC", 1.5), ("BASIC", 2.0)], "boss": False}
        ],
        2: [
            {"enemies": [("BASIC", 1.0), ("FAST", 2.0)], "boss": False},
            {"enemies": [("FAST", 1.0), ("FAST", 1.5), ("BASIC", 2.0)], "boss": False}
        ],
        3: [
            {"enemies": [("TANK", 1.0), ("BASIC", 2.0)], "boss": False},
            {"enemies": [("BASIC", 1.0), ("TANK", 2.0), ("BASIC", 3.0)], "boss": False}
        ],
        4: [
            {"enemies": [("FAST", 1.0), ("TANK", 2.0)], "boss": False},
            {"enemies": [("FAST", 1.0), ("BASIC", 1.5), ("TANK", 2.5)], "boss": False}
        ],
        5: [
            {"enemies": [("BASIC", 1.0), ("FAST", 1.5), ("TANK", 2.0)], "boss": True}
        ],
        # 이후 스테이지는 동적으로 생성하거나 데이터 파일에서 로드
    }

    def __init__(self):
        """웨이브 매니저 초기화"""
        self.current_wave = 0
        self.spawn_queue = []  # (spawn_time, enemy_type)
        self.current_time = 0.0
        self.spawned_enemies = []
        self.boss_spawned = False

    def reset(self) -> None:
        """웨이브 매니저 초기화"""
        self.current_wave = 0
        self.spawn_queue = []
        self.current_time = 0.0
        self.spawned_enemies = []
        self.boss_spawned = False

    def start_wave(self, stage: int) -> None:
        """
        새로운 웨이브 시작

        Args:
            stage: 현재 스테이지
        """
        self.current_wave += 1
        self.current_time = 0.0
        self.spawn_queue = []
        self.boss_spawned = False

        # 웨이브 데이터 로드
        if stage in self.STAGE_WAVES:
            wave_index = min(self.current_wave - 1, len(self.STAGE_WAVES[stage]) - 1)
            wave_data = self.STAGE_WAVES[stage][wave_index]
        else:
            # 기본값: 난이도 증가
            wave_data = self._generate_wave(stage, self.current_wave)

        # 스폰 큐 구성
        for enemy_type_str, spawn_time in wave_data.get("enemies", []):
            self.spawn_queue.append((spawn_time, enemy_type_str, False))

        # 보스 추가
        if wave_data.get("boss", False):
            self.spawn_queue.append((len(wave_data["enemies"]) + 2.0, "BOSS", True))

    def update(self, dt: float, path: List[tuple]) -> List[Enemy]:
        """
        웨이브 업데이트: 스폰할 몬스터 생성

        Args:
            dt: 경과 시간
            path: 몬스터가 따라갈 경로

        Returns:
            새로 스폰된 몬스터 리스트
        """
        self.current_time += dt
        spawned = []

        # 스폰 큐에서 시간이 도래한 몬스터 스폰
        remaining_queue = []
        for spawn_time, enemy_type_str, is_boss in self.spawn_queue:
            if self.current_time >= spawn_time:
                enemy_type = EnemyType[enemy_type_str]
                enemy = Enemy(enemy_type, path)
                self.spawned_enemies.append(enemy)
                spawned.append(enemy)
                if is_boss:
                    self.boss_spawned = True
            else:
                remaining_queue.append((spawn_time, enemy_type_str, is_boss))

        self.spawn_queue = remaining_queue
        return spawned

    def is_wave_complete(self, alive_enemies: List[Enemy]) -> bool:
        """
        웨이브 완료 여부 확인
        (더 이상 스폰할 몬스터 없고, 모든 몬스터 처치 또는 기지 도달)

        Args:
            alive_enemies: 현재 생존한 적 목록

        Returns:
            웨이브 완료 여부
        """
        # 아직 스폰할 몬스터가 있으면 미완료
        if self.spawn_queue:
            return False

        # 모든 적이 처리되었으면 완료
        return len(alive_enemies) == 0

    def get_remaining_spawns(self) -> int:
        """
        남은 스폰 횟수

        Returns:
            스폰 예정인 몬스터 수
        """
        return len(self.spawn_queue)

    # ===== 내부 헬퍼 메서드 =====

    @staticmethod
    def _generate_wave(stage: int, wave_number: int) -> Dict[str, Any]:
        """
        스테이지 5 이상에서 동적으로 웨이브 생성

        Args:
            stage: 스테이지 번호
            wave_number: 웨이브 번호

        Returns:
            웨이브 데이터
        """
        # 스테이지가 높아질수록 더 많은 몬스터 생성
        enemy_count = 2 + (stage - 5) // 5

        enemies = []
        for i in range(enemy_count):
            spawn_time = i * 1.5
            # 스테이지에 따라 몬스터 종류 결정
            if stage <= 10:
                enemy_type = "BASIC" if i % 2 == 0 else "FAST"
            elif stage <= 20:
                enemy_type = "FAST" if i % 2 == 0 else "TANK"
            else:
                enemy_type = "TANK" if i % 2 == 0 else "FAST"

            enemies.append((enemy_type, spawn_time))

        # 보스 스폰 (매 5스테이지마다)
        is_boss = stage % 5 == 0

        return {
            "enemies": enemies,
            "boss": is_boss
        }
