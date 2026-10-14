"""
[담당: 박건희 - 맵/데이터/밸런스]

맵 시스템 단위 테스트:
- 슬롯 유효성 검사
- 경로 검증
- 좌표 변환
- JSON 로드/저장
"""

import unittest
import os
import json
import tempfile
from game.map import GameMap


class TestGameMap(unittest.TestCase):
    """맵 시스템 테스트"""

    def setUp(self):
        """각 테스트 전 초기화"""
        self.map = GameMap()

    def test_map_dimensions(self):
        """맵 크기 테스트"""
        self.assertEqual(self.map.map_width, 20)
        self.assertEqual(self.map.map_height, 15)

    def test_slot_count(self):
        """슬롯 개수 테스트"""
        self.assertEqual(len(self.map.slots), 24)

    def test_is_valid_slot(self):
        """슬롯 유효성 검사 테스트"""
        self.assertTrue(self.map.is_valid_slot(0))
        self.assertTrue(self.map.is_valid_slot(23))
        self.assertFalse(self.map.is_valid_slot(24))
        self.assertFalse(self.map.is_valid_slot(-1))

    def test_get_slot_position(self):
        """슬롯 위치 조회 테스트"""
        pos = self.map.get_slot_position(0)
        self.assertIsInstance(pos, tuple)
        self.assertEqual(len(pos), 2)

    def test_path_validity(self):
        """경로 유효성 테스트"""
        path = self.map.get_path()
        self.assertGreaterEqual(len(path), 2)

        # 모든 경로 좌표가 맵 범위 내
        for x, y in path:
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, self.map.map_width)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, self.map.map_height)

    def test_start_base_position(self):
        """시작과 기지 위치 테스트"""
        start = self.map.get_start_position()
        base = self.map.get_base_position()

        self.assertEqual(len(start), 2)
        self.assertEqual(len(base), 2)
        self.assertNotEqual(start, base)

    def test_json_export_import(self):
        """JSON 저장/로드 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = os.path.join(tmpdir, "test_map.json")

            # 저장
            self.map.export_to_json(json_file)
            self.assertTrue(os.path.exists(json_file))

            # 로드
            new_map = GameMap()
            new_map.load_from_json(json_file)

            # 데이터 일치 확인
            self.assertEqual(len(new_map.slots), len(self.map.slots))
            self.assertEqual(len(new_map.path), len(self.map.path))


class TestMapValidation(unittest.TestCase):
    """맵 검증 테스트"""

    def test_map_validation_passes(self):
        """맵 검증이 통과해야 함"""
        map_obj = GameMap()
        # 예외가 발생하지 않으면 통과
        self.assertIsNotNone(map_obj)


class TestMapDataSafety(unittest.TestCase):
    def test_invalid_load_preserves_map(self):
        map_obj = GameMap()
        original = map_obj.get_path()
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "invalid.json")
            map_obj.export_to_json(filename)
            with open(filename, encoding="utf-8") as f:
                data = json.load(f)
            data["path"][0] = [20, 15]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f)
            with self.assertRaises(ValueError):
                map_obj.load_from_json(filename)
        self.assertEqual(map_obj.path, original)

    def test_slot_on_path_rejected(self):
        map_obj = GameMap()
        map_obj.slots[0] = (0, 3, 1, 1)
        with self.assertRaises(ValueError):
            map_obj._validate_map()

    def test_disconnected_path_rejected(self):
        map_obj = GameMap()
        map_obj.path.pop(1)
        with self.assertRaises(ValueError):
            map_obj._validate_map()

    def test_path_copy_and_invalid_slot_types(self):
        map_obj = GameMap()
        map_obj.get_path().clear()
        self.assertGreater(len(map_obj.path), 2)
        for value in (None, "0", True, 1.5):
            self.assertFalse(map_obj.is_valid_slot(value))

    def test_all_stage_data(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "data/stages.json").read_text(encoding="utf-8"))
        self.assertEqual({int(k) for k in data["stages"]}, set(range(1, 31)))
        for stage, record in data["stages"].items():
            self.assertEqual(any(w["boss"] for w in record["waves"]), int(stage) % 5 == 0)


if __name__ == "__main__":
    unittest.main()
