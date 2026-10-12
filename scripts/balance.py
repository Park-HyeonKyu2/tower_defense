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
        self.num_games = num_games
        self.stages_per_game = stages_per_game
        self.results = []

    def run_simulation(self) -> None:
        """게임 시뮬레이션 실행"""
        print(f"{'='*60}")
        print(f"밸런스 시뮬레이션: {self.num_games}판, 각 {self.stages_per_game}스테이지")
        print(f"{'='*60}\n")

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

        for stage in range(1, self.stages_per_game + 1):
            # 준비 단계: 랜덤 타워 배치
            self._prepare_stage(game, state)

            # 웨이브 진행
            self._simulate_waves(game, state)

            # 게임 오버 확인
            if state.phase == GamePhase.GAME_OVER or state.life <= 0:
                break

            # 다음 스테이지로
            state.current_stage += 1

        result = {
            "survived_stages": state.current_stage - 1,
            "enemies_killed": state.enemies_killed,
            "enemies_reached": state.enemies_reached_base,
            "final_gold": state.gold,
            "final_life": state.life
        }

        return result

    def _prepare_stage(self, game: Game, state) -> None:
        """준비 단계 시뮬레이션"""
        # 랜덤하게 타워 구매
        for i in range(random.randint(2, 5)):
            empty_slots = [s for s in range(24) if not state.tower_slots[s]]
            if empty_slots and state.gold >= 100:
                slot = random.choice(empty_slots)
                action = Action(ActionType.BUY, slot_id=slot)
                game.step(action)

    def _simulate_waves(self, game: Game, state) -> None:
        """웨이브 진행 시뮬레이션"""
        action = Action(ActionType.START_WAVE)
        game.step(action)

        # 웨이브 진행 (1초씩 100번 업데이트)
        for _ in range(100):
            game.update(0.1)

            if state.phase != GamePhase.WAVE_ACTIVE:
                break

    def print_statistics(self) -> None:
        """통계 출력"""
        if not self.results:
            print("실행 결과가 없습니다.")
            return

        print(f"\n{'='*60}")
        print("시뮬레이션 결과")
        print(f"{'='*60}\n")

        # 기본 통계
        avg_stages = sum(r["survived_stages"] for r in self.results) / len(self.results)
        avg_kills = sum(r["enemies_killed"] for r in self.results) / len(self.results)
        avg_gold = sum(r["final_gold"] for r in self.results) / len(self.results)
        max_stages = max(r["survived_stages"] for r in self.results)

        print(f"평균 생존 스테이지: {avg_stages:.1f}")
        print(f"최고 생존 스테이지: {max_stages}")
        print(f"평균 처치 몬스터: {avg_kills:.1f}마리")
        print(f"평균 최종 골드: {avg_gold:.1f}G")

        # 분포
        stage_distribution = {}
        for r in self.results:
            stage = r["survived_stages"]
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1

        print(f"\n생존 스테이지 분포:")
        for stage in sorted(stage_distribution.keys()):
            count = stage_distribution[stage]
            percentage = (count / len(self.results)) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {stage:2d}스테이지: {count}판 ({percentage:5.1f}%) {bar}")

        print(f"\n클리어 통계:")
        cleared = sum(1 for r in self.results if r["survived_stages"] >= self.stages_per_game)
        clear_rate = (cleared / len(self.results)) * 100
        print(f"  클리어: {cleared}/{len(self.results)} ({clear_rate:.1f}%)")


def main():
    """메인 함수"""
    # 시뮬레이션 실행
    analyzer = BalanceAnalyzer(num_games=10, stages_per_game=5)
    analyzer.run_simulation()
    analyzer.print_statistics()

    print(f"\n{'='*60}")
    print("시뮬레이션 완료")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
