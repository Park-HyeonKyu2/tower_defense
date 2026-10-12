"""
[담당: 오승아 - 타워/전투 시스템]

타워 데이터와 공격 속성 정의:
- 4가지 타워 종류: 궁수(ARCHER), 대포(CANNON), 빙결(ICE), 번개(LIGHTNING)
- 각 타워의 공격력, 사거리, 공격 간격, 특수 능력
- 강화 시 스탯 향상
- 타워 능력: 광역 공격, 둔화, 연쇄 공격 등

combat.py와 함께 전투 시스템을 담당합니다.
"""

from typing import Dict, List, Any
from enum import Enum


class TowerType(Enum):
    """타워 종류"""
    ARCHER = "ARCHER"          # 궁수: 단일 대상 공격
    CANNON = "CANNON"          # 대포: 광역 공격
    ICE = "ICE"                # 빙결: 둔화 효과
    LIGHTNING = "LIGHTNING"    # 번개: 연쇄 공격


class Tower:
    """타워 클래스"""

    # 타워별 기본 스탯 (레벨 1)
    BASE_STATS = {
        TowerType.ARCHER: {
            "damage": 10,
            "attack_speed": 1.0,  # 공격/초
            "range": 3,            # 칸 단위
            "cost": 100,
            "description": "단일 대상에 공격"
        },
        TowerType.CANNON: {
            "damage": 15,
            "attack_speed": 0.8,
            "range": 2.5,
            "splash_radius": 1.5,  # 광역 반경
            "cost": 120,
            "description": "광역 공격"
        },
        TowerType.ICE: {
            "damage": 8,
            "attack_speed": 1.2,
            "range": 2.5,
            "slow_factor": 0.5,    # 속도 50% 감소
            "slow_duration": 2.0,  # 둔화 지속 시간 (초)
            "cost": 110,
            "description": "둔화 효과"
        },
        TowerType.LIGHTNING: {
            "damage": 12,
            "attack_speed": 0.9,
            "range": 2.0,
            "chain_count": 2,      # 연쇄 공격 횟수
            "cost": 130,
            "description": "연쇄 공격"
        }
    }

    def __init__(self, tower_type: TowerType, slot_id: int, level: int = 1):
        """
        타워 초기화

        Args:
            tower_type: 타워 종류
            slot_id: 배치된 슬롯 ID
            level: 타워 레벨 (기본값 1)
        """
        self.tower_type = tower_type
        self.slot_id = slot_id
        self.level = level
        self.time_since_last_attack = 0.0
        self.targets = []  # 현재 공격 중인 적 목록

    def get_stats(self) -> Dict[str, float]:
        """
        현재 레벨에 따른 타워 스탯 반환

        Returns:
            강화된 스탯 사전
        """
        base = self.BASE_STATS[self.tower_type].copy()

        # 레벨에 따른 스탯 증가 (예: 10%씩 증가)
        level_multiplier = 1.0 + (self.level - 1) * 0.1
        base["damage"] *= level_multiplier
        base["attack_speed"] *= (1.0 + (self.level - 1) * 0.05)

        return base

    def can_attack(self) -> bool:
        """공격 가능 여부 확인"""
        stats = self.get_stats()
        attack_interval = 1.0 / stats["attack_speed"]
        return self.time_since_last_attack >= attack_interval

    def reset_attack_cooldown(self) -> None:
        """공격 쿨다운 초기화"""
        self.time_since_last_attack = 0.0

    def update(self, dt: float) -> None:
        """시간 경과에 따른 업데이트"""
        self.time_since_last_attack += dt

    @staticmethod
    def get_upgrade_cost(level: int) -> int:
        """
        현재 레벨에서 다음 레벨로의 강화 비용

        Args:
            level: 현재 레벨

        Returns:
            강화 비용
        """
        return 50 * level  # 예: 레벨 1→2: 50G, 2→3: 100G
