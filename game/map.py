"""
[담당: 박건희 - 맵/데이터/밸런스]

맵 및 경로 관리:
- 20×15 고정 맵 그리드
- 몬스터가 따라갈 경로 (좌표 리스트)
- 24개의 타워 설치 가능 슬롯 및 위치
- 맵 유효성 검증
- 좌표 변환 (그리드 ↔ 픽셀)

data/map.json에서 데이터를 로드하거나 하드코딩으로 정의합니다.
"""

from typing import List, Tuple, Dict
import json
import os


class GameMap:
    """게임 맵 및 경로 관리자"""

    MAP_WIDTH = 20   # 맵 가로 칸 수
    MAP_HEIGHT = 15  # 맵 세로 칸 수
    SLOT_COUNT = 24  # 타워 설치 슬롯 수

    def __init__(self):
        """맵 초기화"""
        self.map_width = self.MAP_WIDTH
        self.map_height = self.MAP_HEIGHT

        # 몬스터 경로: 맵 시작점 → 기지까지의 좌표 리스트
        self.path = self._initialize_path()

        # 타워 설치 슬롯: 슬롯 ID → (x, y, width, height)
        self.slots = self._initialize_slots()

        # 맵 검증
        self._validate_map()

    def _initialize_path(self) -> List[Tuple[int, int]]:
        """
        몬스터 경로 초기화
        (실제 게임에서는 data/map.json에서 로드)

        Returns:
            경로 좌표 리스트 [(x1, y1), (x2, y2), ...]
        """
        # 예시: 맵 좌상단에서 시작해서 우상단으로, 다시 우하단으로, 그리고 좌하단으로
        path = [
            (0, 7),     # 시작점
            (5, 7),
            (10, 3),
            (15, 8),
            (19, 15)    # 기지 위치
        ]
        return path

    def _initialize_slots(self) -> Dict[int, Tuple[int, int, int, int]]:
        """
        타워 설치 슬롯 초기화
        (실제 게임에서는 data/map.json에서 로드)

        Returns:
            슬롯 ID → (x, y, width, height) 맵
        """
        # 예시: 3×8 = 24개 슬롯
        slots = {}
        slot_id = 0

        for row in range(3):
            for col in range(8):
                # 슬롯 위치 (타워 설치 가능 영역)
                x = col * 2.5
                y = row * 5
                width = 2.0
                height = 4.5
                slots[slot_id] = (x, y, width, height)
                slot_id += 1

        return slots

    def _validate_map(self) -> None:
        """맵 유효성 검증"""
        # 슬롯 수 확인
        assert len(self.slots) == self.SLOT_COUNT, \
            f"슬롯 수가 {self.SLOT_COUNT}개여야 함, 현재 {len(self.slots)}개"

        # 경로 유효성 확인
        assert len(self.path) >= 2, "경로는 최소 2개 이상의 점을 포함해야 함"

        # 각 경로 좌표가 맵 범위 내에 있는지 확인
        for x, y in self.path:
            assert 0 <= x <= self.map_width and 0 <= y <= self.map_height, \
                f"경로 좌표 ({x}, {y})가 맵 범위를 벗어남"

    def is_valid_slot(self, slot_id: int) -> bool:
        """
        슬롯이 유효한지 확인

        Args:
            slot_id: 슬롯 ID

        Returns:
            유효 여부
        """
        return 0 <= slot_id < self.SLOT_COUNT

    def get_slot_position(self, slot_id: int) -> Tuple[float, float]:
        """
        슬롯의 중심 좌표 반환

        Args:
            slot_id: 슬롯 ID

        Returns:
            (x, y) 좌표
        """
        if not self.is_valid_slot(slot_id):
            return (0, 0)

        x, y, width, height = self.slots[slot_id]
        return (x + width / 2, y + height / 2)

    def get_slot_bounds(self, slot_id: int) -> Tuple[float, float, float, float]:
        """
        슬롯의 경계 반환 (x, y, width, height)

        Args:
            slot_id: 슬롯 ID

        Returns:
            (x, y, width, height)
        """
        if not self.is_valid_slot(slot_id):
            return (0, 0, 0, 0)

        return self.slots[slot_id]

    def get_path(self) -> List[Tuple[int, int]]:
        """
        몬스터 경로 반환

        Returns:
            경로 좌표 리스트
        """
        return self.path

    def get_start_position(self) -> Tuple[float, float]:
        """
        몬스터 시작 위치

        Returns:
            (x, y) 좌표
        """
        if len(self.path) > 0:
            return self.path[0]
        return (0, 0)

    def get_base_position(self) -> Tuple[float, float]:
        """
        기지 위치 (몬스터 도착 지점)

        Returns:
            (x, y) 좌표
        """
        if len(self.path) > 0:
            return self.path[-1]
        return (0, 0)

    def load_from_json(self, json_file: str) -> None:
        """
        JSON 파일에서 맵 데이터 로드

        Args:
            json_file: 맵 데이터 JSON 파일 경로
        """
        if not os.path.exists(json_file):
            print(f"경고: {json_file}을 찾을 수 없습니다. 기본값 사용")
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 경로 로드
            if "path" in data:
                self.path = [tuple(p) for p in data["path"]]

            # 슬롯 로드
            if "slots" in data:
                self.slots = {}
                for slot_id, bounds in data["slots"].items():
                    self.slots[int(slot_id)] = tuple(bounds)

            # 검증
            self._validate_map()

        except json.JSONDecodeError:
            print(f"오류: {json_file}이 유효한 JSON이 아닙니다")
        except Exception as e:
            print(f"오류: 맵 로드 실패 - {e}")

    def export_to_json(self, json_file: str) -> None:
        """
        현재 맵을 JSON 파일로 저장

        Args:
            json_file: 저장할 파일 경로
        """
        data = {
            "width": self.map_width,
            "height": self.map_height,
            "path": self.path,
            "slots": {
                str(slot_id): list(bounds)
                for slot_id, bounds in self.slots.items()
            }
        }

        try:
            os.makedirs(os.path.dirname(json_file), exist_ok=True)
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"맵 저장 완료: {json_file}")
        except Exception as e:
            print(f"오류: 맵 저장 실패 - {e}")
