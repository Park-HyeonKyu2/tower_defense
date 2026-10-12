"""
[담당: 이서진 - 게임 엔진/통합]

실행 진입점: Pygame UI와 게임 엔진을 연결합니다.
- 게임 루프 구성: 입력 처리 → 게임 상태 업데이트 → 화면 렌더링
- Pygame 이벤트 루프를 관리합니다.
- 엔진과 디스플레이 모듈을 통합합니다.
"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.engine import Game
from display.renderer import Renderer
from display.input_handler import InputHandler


def main():
    """게임 메인 루프"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Random Tower Defense")
    clock = pygame.time.Clock()

    # 게임 엔진, 렌더러, 입력 핸들러 초기화
    game = Game()
    renderer = Renderer(screen)
    input_handler = InputHandler()

    # 게임 시작
    state = game.reset(seed=42)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0  # 프레임 시간 (초)

        # 입력 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                action = input_handler.handle_event(event, state)
                if action:
                    state = game.step(action)

        # 게임 상태 업데이트 (자동 전투, 몬스터 이동 등)
        game.update(dt)
        state = game.get_state()

        # 화면 렌더링
        renderer.render(state)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
