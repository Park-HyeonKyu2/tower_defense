"""
[담당: 박건희 - 맵/데이터/밸런스]

자동 게임 시뮬레이션 및 밸런스 검증:
- UI 없이 게임을 여러 판 실행
- 게임 통계 수집 (평균 생존 스테이지, 클리어율 등)
- 밸런스 분석 및 개선안 도출
- 데이터 수정 없이 로직만 테스트

실행: python scripts/balance.py
"""

import sys
import os
import random
import argparse
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.engine import Game
from game.actions import Action, ActionType
from game.state import GamePhase


class BalanceAnalyzer:
    """밸런스 분석기"""

    def __init__(self, num_games: int = 10, stages_per_game: int = 5):
        """
        초기화

        Args:
            num_games: 시뮬레이션 게임 수
            stages_per_game: 각 게임에서 시뮬레이션할 스테이지 수
        """
        if num_games <= 0 or not 1 <= stages_per_game <= 30:
            raise ValueError("게임 수는 양수, 스테이지 수는 1~30이어야 합니다")
        self.num_games = num_games
        self.stages_per_game = stages_per_game
        self.results = []

    def run_simulation(self) -> None:
        """게임 시뮬레이션 실행"""
        print(f"{'='*60}")
        print(f"밸런스 시뮬레이션: {self.num_games}판, 각 {self.stages_per_game}스테이지")
        print(f"{'='*60}\n")

        self.results = []
        for game_num in range(self.num_games):
            print(f"[게임 {game_num + 1}/{self.num_games}]")
            result = self._run_single_game(seed=game_num)
            self.results.append(result)
            print(f"  → 생존: {result['survived_stages']}스테이지, "
                  f"처치: {result['enemies_killed']}마리, "
                  f"최종 골드: {result['final_gold']}G\n")

    def _run_single_game(self, seed: int) -> Dict[str, Any]:
        """
        단일 게임 시뮬레이션

        Args:
            seed: 난수 시드

        Returns:
            게임 결과 정보
        """
        game = Game()
        state = game.reset(seed=seed)
        self._random = random.Random(seed)
        survived_stages = 0
        stage_results = []
        status, error = "completed", ""
        try:
            while survived_stages < self.stages_per_game:
                if state.phase in (GamePhase.GAME_OVER, GamePhase.VICTORY):
                    break
                stage = state.current_stage
                gold_before = state.gold
                life_before = state.life
                self._prepare_stage(game, state)
                self._simulate_waves(game, state)
                state = game.get_state()
                completed = (state.phase == GamePhase.VICTORY or
                             state.current_stage > stage)
                stage_results.append({"stage": stage, "gold_before": gold_before,
                                      "gold_after": state.gold, "life_lost": life_before - state.life,
                                      "completed": completed})
                if completed:
                    survived_stages += 1
                elif state.phase == GamePhase.GAME_OVER or state.life <= 0:
                    break
                else:
                    raise RuntimeError("엔진이 스테이지를 진행하지 않았습니다")
            if state.phase == GamePhase.GAME_OVER or state.life <= 0:
                status = "game_over"
        except (TypeError, AttributeError, RuntimeError) as exc:
            status, error = "error", str(exc)
        return {"seed": seed, "status": status, "error": error,
                "survived_stages": survived_stages,
                "enemies_killed": state.enemies_killed,
                "enemies_reached": state.enemies_reached_base,
                "final_gold": state.gold, "final_life": state.life,
                "stage_results": stage_results}

    def _prepare_stage(self, game: Game, state) -> None:
        """준비 단계 시뮬레이션"""
        # 랜덤하게 타워 구매
        for i in range(self._random.randint(2, 5)):
            empty_slots = [s for s in range(24) if not state.tower_slots[s]]
            if empty_slots and state.gold >= 100:
                slot = self._random.choice(empty_slots)
                action = Action(ActionType.BUY, slot_id=slot)
                game.step(action)

    def _simulate_waves(self, game: Game, state) -> None:
        """웨이브 진행 시뮬레이션"""
        action = Action(ActionType.START_WAVE)
        game.step(action)

        if state.phase != GamePhase.WAVE_ACTIVE:
            raise RuntimeError("웨이브 시작에 실패했습니다")
        # 고정 시간 간격, 웨이브당 최대 600초. 미완료를 클리어로 세지 않습니다.
        for _ in range(36000):
            game.update(1 / 60)

            if state.phase != GamePhase.WAVE_ACTIVE:
                return
        raise RuntimeError("웨이브가 600초 안에 종료되지 않았습니다")

    def print_statistics(self) -> None:
        """통계 출력"""
        if not self.results:
            print("실행 결과가 없습니다.")
            return

        print(f"\n{'='*60}")
        print("시뮬레이션 결과")
        print(f"{'='*60}\n")

        errors = [r for r in self.results if r["status"] == "error"]
        if errors:
            print(f"실행 오류: {len(errors)}판 (밸런스 판단에서 제외 필요)")
            for message in sorted({r["error"] for r in errors}):
                print(f"  {message}")
            if len(errors) == len(self.results):
                print("엔진 연결이 완료되지 않아 클리어율을 계산하지 않습니다.")
                return

        results = [r for r in self.results if r["status"] != "error"]
        # 기본 통계
        avg_stages = sum(r["survived_stages"] for r in results) / len(results)
        avg_kills = sum(r["enemies_killed"] for r in results) / len(results)
        avg_gold = sum(r["final_gold"] for r in results) / len(results)
        max_stages = max(r["survived_stages"] for r in results)

        print(f"평균 생존 스테이지: {avg_stages:.1f}")
        print(f"최고 생존 스테이지: {max_stages}")
        print(f"평균 처치 몬스터: {avg_kills:.1f}마리")
        print(f"평균 최종 골드: {avg_gold:.1f}G")

        # 분포
        stage_distribution = {}
        for r in results:
            stage = r["survived_stages"]
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1

        print(f"\n생존 스테이지 분포:")
        for stage in sorted(stage_distribution.keys()):
            count = stage_distribution[stage]
            percentage = (count / len(results)) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {stage:2d}스테이지: {count}판 ({percentage:5.1f}%) {bar}")

        print(f"\n클리어 통계:")
        cleared = sum(1 for r in results if r["survived_stages"] >= self.stages_per_game)
        clear_rate = (cleared / len(results)) * 100
        print(f"  클리어: {cleared}/{len(results)} ({clear_rate:.1f}%)")


def main():
    """기존 실행 방법을 유지하고 JSON/CSV 결과 저장을 지원합니다."""
    parser = argparse.ArgumentParser(description="화면 없는 밸런스 시뮬레이션")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--stages", type=int, default=5)
    parser.add_argument("--output", help="결과 JSON 파일 경로 (CSV도 함께 저장)")
    args = parser.parse_args()
    analyzer = BalanceAnalyzer(args.games, args.stages)
    analyzer.run_simulation()
    analyzer.print_statistics()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(analyzer.results, ensure_ascii=False, indent=2), encoding="utf-8")
        fields = [key for key in analyzer.results[0] if key != "stage_results"]
        with output.with_suffix(".csv").open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(analyzer.results)
    return 1 if any(r["status"] == "error" for r in analyzer.results) else 0


if __name__ == "__main__":
    sys.exit(main())
