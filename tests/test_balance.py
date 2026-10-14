import unittest
from unittest.mock import patch
from scripts.balance import BalanceAnalyzer
from game.state import GamePhase


class TestBalanceAnalyzer(unittest.TestCase):
    def test_engine_error_is_not_a_clear(self):
        result = BalanceAnalyzer(1, 5)._run_single_game(42)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["survived_stages"], 0)
        self.assertIn("alive_enemies", result["error"])

    def test_stage_progression_is_owned_by_engine(self):
        analyzer = BalanceAnalyzer(1, 5)
        def complete(game, state):
            state.current_stage += 1
            state.phase = GamePhase.PREPARATION
        with patch.object(analyzer, "_simulate_waves", side_effect=complete):
            result = analyzer._run_single_game(42)
        self.assertEqual(result["survived_stages"], 5)
        self.assertEqual([s["stage"] for s in result["stage_results"]], [1, 2, 3, 4, 5])

    def test_invalid_settings(self):
        for games, stages in [(0, 5), (1, 0), (1, 31)]:
            with self.assertRaises(ValueError):
                BalanceAnalyzer(games, stages)
