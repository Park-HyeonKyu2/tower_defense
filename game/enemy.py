"""
[담당: 이승연 - 몬스터/웨이브 시스템]

몬스터 데이터와 이동:
- 몬스터 종류별 스탯 (HP, 속도, 골드 보상)
- 경로 진행 (path 따라 이동)
- 기지 도달 시 라이프 감소
- 상태 이상 적용 (둔화 등)
- 스테이지별로 다른 몬스터 구성

wave.py와 함께 웨이브 시스템을 담당합니다.
"""

from typing import Dict, List, Any
from enum import Enum


class EnemyType(Enum):
    """몬스터 종류"""
    BASIC = "BASIC"          # 기본 몬스터
    FAST = "FAST"            # 빠른 몬스터 (속도 높음, HP 낮음)
    TANK = "TANK"            # 탱크 (HP 높음, 속도 낮음)
    BOSS = "BOSS"            # 보스 (매우 높은 HP, 높은 보상)


class Enemy:
    """몬스터 클래스"""

    # 몬스터별 기본 스탯
    BASE_STATS = {
        EnemyType.BASIC: {
            "health": 30,
            "speed": 1.0,         # 칸/초
            "gold_reward": 10,
            "description": "기본 몬스터"
        },
        EnemyType.FAST: {
            "health": 15,
            "speed": 2.0,
            "gold_reward": 15,
            "description": "빠른 몬스터"
        },
        EnemyType.TANK: {
            "health": 60,
            "speed": 0.5,
            "gold_reward": 25,
            "description": "탱크 몬스터"
        },
        EnemyType.BOSS: {
            "health": 150,
            "speed": 0.8,
            "gold_reward": 100,
            "description": "보스 몬스터"
        }
    }

    def __init__(self, enemy_type: EnemyType, path: List[tuple], stage: int = 1):
        """
        몬스터 초기화

        Args:
            enemy_type: 몬스터 종류
            path: 이동할 경로 (좌표 리스트)
            stage: 현재 스테이지 (높을수록 강해짐)
        """
        self.enemy_type = enemy_type
        self.path = path
        self.stage = stage
        self.path_index = 0  # 현재 경로상 위치 인덱스
        self.progress_in_segment = 0.0  # 현재 경로 세그먼트 내 진행도 (0~1)

        # 스테이지에 따른 스탯 상향
        base_stats = self.BASE_STATS[enemy_type].copy()
        stage_multiplier = 1.0 + (stage - 1) * 0.05
        self.max_health = int(base_stats["health"] * stage_multiplier)
        self.health = self.max_health
        self.speed = base_stats["speed"]
        self.gold_reward = int(base_stats["gold_reward"] * stage_multiplier)

        # 상태
        self.is_alive = True
        self.status_effects = {}  # 둔화 등

    def get_current_position(self) -> tuple:
        """
        현재 좌표 계산

        Returns:
            (x, y) 좌표
        """
        if self.path_index >= len(self.path):
            # 경로 완주
            return self.path[-1]

        current = self.path[self.path_index]
        next_pos = self.path[self.path_index + 1] if self.path_index + 1 < len(self.path) else current

        # 선형 보간
        x = current[0] + (next_pos[0] - current[0]) * self.progress_in_segment
        y = current[1] + (next_pos[1] - current[1]) * self.progress_in_segment

        return (x, y)

    def move(self, dt: float, speed_modifier: float = 1.0) -> bool:
        """
        dt 시간만큼 이동

        Args:
            dt: 경과 시간 (초)
            speed_modifier: 속도 배수 (상태 이상 반영)

        Returns:
            경로 완주했는지 여부
        """
        effective_speed = self.speed * speed_modifier
        distance = effective_speed * dt  # 이동 거리 (칸 단위)

        while distance > 0:
            if self.path_index >= len(self.path) - 1:
                # 경로 완주
                return True

            current = self.path[self.path_index]
            next_pos = self.path[self.path_index + 1]

            # 현재 세그먼트의 길이
            segment_length = self._calculate_distance(current, next_pos)
            remaining_distance = segment_length * (1.0 - self.progress_in_segment)

            if distance >= remaining_distance:
                # 다음 세그먼트로 이동
                distance -= remaining_distance
                self.path_index += 1
                self.progress_in_segment = 0.0
            else:
                # 현재 세그먼트 내에서 이동
                self.progress_in_segment += distance / segment_length
                distance = 0

        return False

    def take_damage(self, damage: float) -> bool:
        """
        피해 입히기

        Args:
            damage: 피해량

        Returns:
            사망했는지 여부
        """
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False
            return True
        return False

    def apply_slow_effect(self, slow_factor: float, duration: float, current_time: float) -> None:
        """
        둔화 효과 적용

        Args:
            slow_factor: 속도 배수
            duration: 지속 시간 (초)
            current_time: 현재 게임 시간
        """
        self.status_effects["slow"] = {
            "factor": slow_factor,
            "end_time": current_time + duration
        }

    def get_speed_modifier(self, current_time: float) -> float:
        """
        현재 속도 배수 계산 (상태 이상 반영)

        Args:
            current_time: 현재 게임 시간

        Returns:
            속도 배수
        """
        # 만료된 효과 제거
        expired = [k for k, v in self.status_effects.items()
                   if v.get("end_time", 0) <= current_time]
        for key in expired:
            del self.status_effects[key]

        modifier = 1.0
        if "slow" in self.status_effects:
            modifier *= self.status_effects["slow"]["factor"]

        return modifier

    def has_reached_base(self) -> bool:
        """기지에 도달했는지 확인"""
        return self.path_index >= len(self.path) - 1

    # ===== 내부 헬퍼 메서드 =====

    @staticmethod
    def _calculate_distance(pos1: tuple, pos2: tuple) -> float:
        """두 위치 간 거리 계산"""
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
