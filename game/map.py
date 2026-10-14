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
        self.load_from_json(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "map.json"))

    def _initialize_path(self) -> List[Tuple[int, int]]:
        """
        몬스터 경로 초기화
        (실제 게임에서는 data/map.json에서 로드)

        Returns:
            경로 좌표 리스트 [(x1, y1), (x2, y2), ...]
        """
        # 경로는 각 칸의 중심을 연결하며 모두 직교로 인접합니다.
        return ([(x + 0.5, 3.5) for x in range(20)]
                + [(19.5, y + 0.5) for y in range(4, 8)]
                + [(x + 0.5, 7.5) for x in range(18, -1, -1)]
                + [(0.5, y + 0.5) for y in range(8, 12)]
                + [(x + 0.5, 11.5) for x in range(1, 20)])

    def _initialize_slots(self) -> Dict[int, Tuple[float, float, float, float]]:
        """슬롯 ID와 (x, y, width, height) 형식을 유지합니다."""
        return {row * 8 + col: (1 + col * 2, y, 1, 1)
                for row, y in enumerate((2, 6, 10)) for col in range(8)}

    def _validate_map(self) -> None:
        """범위, 연속 경로, 슬롯 중복 및 경로 교차를 검사합니다."""
        import math
        def numeric(value):
            return (isinstance(value, (int, float)) and not isinstance(value, bool)
                    and math.isfinite(value))
        if (self.map_width != self.MAP_WIDTH or self.map_height != self.MAP_HEIGHT
                or not numeric(self.map_width) or not numeric(self.map_height)):
            raise ValueError("맵 크기는 20 x 15여야 합니다")
        if set(self.slots) != set(range(self.SLOT_COUNT)):
            raise ValueError("슬롯 ID는 0~23이어야 합니다")
        if len(self.path) < 2:
            raise ValueError("경로는 최소 두 점이 필요합니다")
        for point in self.path:
            if len(point) != 2 or not all(numeric(v) for v in point):
                raise ValueError("경로 좌표는 유한한 숫자 두 개여야 합니다")
            x, y = point
            if not (0 <= x < self.map_width and 0 <= y < self.map_height):
                raise ValueError("경로 좌표가 맵 범위를 벗어났습니다")
        if len(set(self.path)) != len(self.path):
            raise ValueError("경로 좌표가 중복됩니다")
        for start, end in zip(self.path, self.path[1:]):
            if abs(start[0] - end[0]) + abs(start[1] - end[1]) != 1:
                raise ValueError("경로는 직교로 인접한 칸을 연결해야 합니다")
        bounds_list = []
        for bounds in self.slots.values():
            if len(bounds) != 4 or not all(numeric(v) for v in bounds):
                raise ValueError("슬롯은 숫자 네 개의 경계여야 합니다")
            x, y, width, height = bounds
            if not (width > 0 and height > 0 and x >= 0 and y >= 0
                    and x + width <= self.map_width and y + height <= self.map_height):
                raise ValueError("슬롯 경계가 맵 범위를 벗어났습니다")
            for bx, by, bw, bh in bounds_list:
                if x < bx + bw and bx < x + width and y < by + bh and by < y + height:
                    raise ValueError("슬롯 영역이 중복됩니다")
            bounds_list.append(bounds)
            for px, py in self.path:
                if x <= px < x + width and y <= py < y + height:
                    raise ValueError("슬롯이 경로와 겹칩니다")

    def is_valid_slot(self, slot_id: int) -> bool:
        """
        슬롯이 유효한지 확인

        Args:
            slot_id: 슬롯 ID

        Returns:
            유효 여부
        """
        return type(slot_id) is int and slot_id in self.slots

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
        return list(self.path)

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

        # 먼저 후보를 검증하고 성공한 경우에만 현재 맵을 교체합니다.
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        candidate = object.__new__(GameMap)
        candidate.map_width = data["width"]
        candidate.map_height = data["height"]
        candidate.path = [tuple(p) for p in data["path"]]
        candidate.slots = {int(k): tuple(v) for k, v in data["slots"].items()}
        if len(candidate.slots) != len(data["slots"]):
            raise ValueError("슬롯 ID가 중복됩니다")
        candidate._validate_map()
        self.map_width, self.map_height = candidate.map_width, candidate.map_height
        self.path, self.slots = candidate.path, candidate.slots

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

        self._validate_map()
        try:
            os.makedirs(os.path.dirname(os.path.abspath(json_file)), exist_ok=True)
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"맵 저장 완료: {json_file}")
        except Exception as e:
            print(f"오류: 맵 저장 실패 - {e}")
