"""
[담당: 오승아 - 타워/전투 시스템]

전투 시스템: 타워의 공격과 적 피해 처리
- 공격 대상 선정 (거리 내 적 중 경로상 가장 앞서 진행한 적)
- 피해 계산 및 적 HP 감소
- 특수 효과 적용: 광역 공격(CANNON), 둔화(ICE), 연쇄 공격(LIGHTNING)
- 상태 이상 관리

tower.py와 함께 전투 시스템을 담당합니다.
"""

from typing import List, Dict, Optional, Any
from game.tower import TowerType
import math


class Combat:
    """전투 시스템 관리자"""

    def __init__(self):
        """전투 시스템 초기화"""
        pass

    def get_target(self, tower_pos: tuple, tower_range: float,
                   enemies: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        타워가 공격할 적 선정
        규칙: 사거리 내 적 중 경로상 가장 앞서 진행한 적

        Args:
            tower_pos: 타워 위치 (x, y)
            tower_range: 타워 사거리
            enemies: 현재 존재하는 적 목록

        Returns:
            공격 대상 적, 사거리 내 적이 없으면 None
        """
        targets_in_range = []

        for enemy in enemies:
            if enemy["health"] > 0:  # 생존한 적만
                enemy_pos = (enemy["x"], enemy["y"])
                distance = self._calculate_distance(tower_pos, enemy_pos)

                if distance <= tower_range:
                    targets_in_range.append(enemy)

        if not targets_in_range:
            return None

        # 경로상 가장 앞서 진행한 적 (progress 값이 높은 것)
        return max(targets_in_range, key=lambda e: e.get("progress", 0))

    def apply_damage(self, target: Dict[str, Any], damage: float) -> bool:
        """
        적에게 피해 적용

        Args:
            target: 대상 적
            damage: 피해량

        Returns:
            적이 사망했는지 여부
        """
        target["health"] -= damage
        return target["health"] <= 0

    def apply_slow_effect(self, target: Dict[str, Any],
                         slow_factor: float, duration: float) -> None:
        """
        둔화 효과 적용 (얼음 타워)

        Args:
            target: 대상 적
            slow_factor: 속도 배수 (0.5 = 50% 감소)
            duration: 지속 시간 (초)
        """
        # 상태 이상 정보 저장
        if "status_effects" not in target:
            target["status_effects"] = {}

        target["status_effects"]["slow"] = {
            "factor": slow_factor,
            "end_time": target.get("elapsed_time", 0) + duration
        }

    def apply_splash_damage(self, center_pos: tuple, splash_radius: float,
                           damage: float, enemies: List[Dict[str, Any]]) -> int:
        """
        광역 피해 적용 (대포 타워)

        Args:
            center_pos: 광역 중심 (x, y)
            splash_radius: 광역 반경
            damage: 피해량
            enemies: 대상 적 목록

        Returns:
            피해입은 적 수
        """
        damaged_count = 0

        for enemy in enemies:
            if enemy["health"] > 0:
                enemy_pos = (enemy["x"], enemy["y"])
                distance = self._calculate_distance(center_pos, enemy_pos)

                if distance <= splash_radius:
                    if self.apply_damage(enemy, damage):
                        damaged_count += 1

        return damaged_count

    def apply_chain_damage(self, target: Dict[str, Any], damage: float,
                          chain_count: int, enemies: List[Dict[str, Any]]) -> int:
        """
        연쇄 공격 적용 (번개 타워)

        Args:
            target: 첫 번째 대상
            damage: 각 체인당 피해량
            chain_count: 총 연쇄 횟수
            enemies: 모든 적 목록

        Returns:
            피해입은 적 수
        """
        damaged = set()
        current_target = target
        damaged_count = 0

        for i in range(chain_count):
            if current_target and current_target["health"] > 0:
                if self.apply_damage(current_target, damage):
                    damaged_count += 1
                damaged.add(id(current_target))

                # 다음 연쇄 대상 찾기 (피해를 입지 않은 가장 가까운 적)
                current_target = self._find_nearest_enemy(
                    (current_target["x"], current_target["y"]),
                    enemies,
                    exclude=damaged
                )
            else:
                break

        return damaged_count

    def update_status_effects(self, enemies: List[Dict[str, Any]], elapsed_time: float) -> None:
        """
        상태 이상 업데이트 (지속 시간 확인)

        Args:
            enemies: 모든 적 목록
            elapsed_time: 현재 경과 시간
        """
        for enemy in enemies:
            if "status_effects" not in enemy:
                continue

            effects = enemy["status_effects"]
            to_remove = []

            for effect_name, effect_data in effects.items():
                if effect_data.get("end_time", 0) <= elapsed_time:
                    to_remove.append(effect_name)

            for effect_name in to_remove:
                del effects[effect_name]

    def get_enemy_speed_modifier(self, enemy: Dict[str, Any]) -> float:
        """
        적의 현재 속도 배수 계산 (상태 이상 반영)

        Args:
            enemy: 적 데이터

        Returns:
            속도 배수 (1.0 = 정상, 0.5 = 50% 감소)
        """
        modifier = 1.0

        if "status_effects" in enemy:
            if "slow" in enemy["status_effects"]:
                modifier *= enemy["status_effects"]["slow"]["factor"]

        return modifier

    # ===== 내부 헬퍼 메서드 =====

    @staticmethod
    def _calculate_distance(pos1: tuple, pos2: tuple) -> float:
        """두 위치 간 거리 계산"""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    @staticmethod
    def _find_nearest_enemy(from_pos: tuple, enemies: List[Dict[str, Any]],
                           exclude: set = None) -> Optional[Dict[str, Any]]:
        """
        특정 위치에서 가장 가까운 적 찾기

        Args:
            from_pos: 기준 위치
            enemies: 적 목록
            exclude: 제외할 적 ID 집합

        Returns:
            가장 가까운 적, 없으면 None
        """
        if exclude is None:
            exclude = set()

        candidates = [
            e for e in enemies
            if e["health"] > 0 and id(e) not in exclude
        ]

        if not candidates:
            return None

        return min(candidates, key=lambda e: Combat._calculate_distance(
            from_pos, (e["x"], e["y"])
        ))
