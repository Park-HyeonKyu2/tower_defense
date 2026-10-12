"""
[담당: 박현규 - Pygame UI/입력]

화면 렌더링: 게임 상태를 Pygame 화면에 그리기
- 맵을 사각형, 선, 텍스트로 표시
- 타워와 몬스터를 화면에 표시
- 현재 게임 상태 시각화 (골드, 라이프, 스테이지 등)
- 사각형/원/선 등 기본 도형으로 표현 (아트 제외)
- 렌더러는 게임 상태를 읽기만 하고 수정하지 않음

ui.py와 함께 UI 시스템을 담당합니다.
"""

import pygame
from game.state import GameState
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_GREEN, COLOR_RED


class Renderer:
    """게임 화면 렌더러"""

    def __init__(self, screen: pygame.Surface):
        """
        렌더러 초기화

        Args:
            screen: Pygame 화면 객체
        """
        self.screen = screen
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)

    def render(self, state: GameState) -> None:
        """
        게임 상태를 화면에 렌더링

        Args:
            state: 현재 게임 상태
        """
        # 배경 색칠
        self.screen.fill(COLOR_BLACK)

        # 게임 영역 렌더링
        self._render_game_area(state)

        # UI 패널 렌더링
        self._render_ui_panel(state)

        # 게임 상태에 따른 추가 렌더링
        self._render_phase_specific(state)

    def _render_game_area(self, state: GameState) -> None:
        """게임 맵, 타워, 몬스터 렌더링"""
        # 맵 경계 그리기
        game_area_width = SCREEN_WIDTH - 200  # 우측 200px는 UI 패널
        pygame.draw.rect(self.screen, COLOR_WHITE, (10, 10, game_area_width - 20, SCREEN_HEIGHT - 20), 2)

        # 경로 그리기 (흰색 선)
        # 예시: 경로 좌표를 픽셀로 변환하여 그리기
        # path = state.map.get_path()
        # ...

        # 타워 렌더링
        self._render_towers(state)

        # 몬스터 렌더링
        self._render_enemies(state)

    def _render_towers(self, state: GameState) -> None:
        """타워 렌더링"""
        for slot_id, tower_data in state.towers.items():
            # 슬롯 위치 계산 (예시)
            x = 50 + (slot_id % 8) * 100
            y = 100 + (slot_id // 8) * 100

            # 타워 유형에 따라 색상 결정
            tower_type = tower_data["type"]
            if tower_type == "ARCHER":
                color = COLOR_GREEN
            elif tower_type == "CANNON":
                color = (255, 165, 0)  # 주황색
            elif tower_type == "ICE":
                color = (0, 255, 255)  # 시안색
            else:  # LIGHTNING
                color = (255, 255, 0)  # 노란색

            # 타워를 원으로 표시
            pygame.draw.circle(self.screen, color, (x, y), 15)

            # 레벨 표시
            level_text = self.font_small.render(str(tower_data["level"]), True, COLOR_BLACK)
            self.screen.blit(level_text, (x - 5, y - 5))

    def _render_enemies(self, state: GameState) -> None:
        """몬스터 렌더링"""
        for enemy_data in state.enemies:
            if enemy_data.get("health", 0) <= 0:
                continue

            # 몬스터 위치 계산 (경로상 진행도 기반)
            # 예시: x, y는 game/enemy.py에서 계산된 위치
            x = enemy_data.get("x", 0)
            y = enemy_data.get("y", 0)

            # 몬스터 유형에 따라 색상 결정
            enemy_type = enemy_data.get("type", "BASIC")
            if enemy_type == "FAST":
                color = (255, 100, 100)  # 밝은 빨강
            elif enemy_type == "TANK":
                color = (100, 100, 255)  # 밝은 파랑
            elif enemy_type == "BOSS":
                color = (255, 0, 255)  # 마젠타
            else:  # BASIC
                color = COLOR_RED

            # 몬스터를 사각형으로 표시
            size = 10 if enemy_type != "BOSS" else 20
            pygame.draw.rect(self.screen, color, (x - size // 2, y - size // 2, size, size))

            # HP 바 표시 (선택사항)
            max_hp = enemy_data.get("max_health", 30)
            current_hp = enemy_data.get("health", 30)
            hp_ratio = current_hp / max_hp if max_hp > 0 else 0

            hp_bar_width = 20
            hp_bar_height = 3
            pygame.draw.rect(self.screen, COLOR_RED,
                           (x - hp_bar_width // 2, y - size // 2 - 10, hp_bar_width, hp_bar_height))
            pygame.draw.rect(self.screen, COLOR_GREEN,
                           (x - hp_bar_width // 2, y - size // 2 - 10, hp_bar_width * hp_ratio, hp_bar_height))

    def _render_ui_panel(self, state: GameState) -> None:
        """우측 UI 패널 렌더링"""
        panel_x = SCREEN_WIDTH - 200
        panel_width = 200
        panel_height = SCREEN_HEIGHT

        # 패널 배경
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, 0, panel_width, panel_height))

        # 텍스트 정보
        y_offset = 20

        # 스테이지 정보
        stage_text = self.font_medium.render(f"Stage: {state.current_stage}", True, COLOR_WHITE)
        self.screen.blit(stage_text, (panel_x + 10, y_offset))
        y_offset += 40

        # 웨이브 정보
        wave_text = self.font_medium.render(f"Wave: {state.current_wave}", True, COLOR_WHITE)
        self.screen.blit(wave_text, (panel_x + 10, y_offset))
        y_offset += 40

        # 골드 정보
        gold_text = self.font_medium.render(f"Gold: {state.gold}", True, (255, 215, 0))  # 골드색
        self.screen.blit(gold_text, (panel_x + 10, y_offset))
        y_offset += 40

        # 라이프 정보
        life_text = self.font_medium.render(f"Life: {state.life}", True, COLOR_RED)
        self.screen.blit(life_text, (panel_x + 10, y_offset))
        y_offset += 40

        # 게임 단계
        phase_text = self.font_small.render(f"Phase: {state.phase.value}", True, COLOR_WHITE)
        self.screen.blit(phase_text, (panel_x + 10, y_offset))
        y_offset += 40

        # 버튼 영역 (UI.py에서 렌더링)

    def _render_phase_specific(self, state: GameState) -> None:
        """게임 단계에 따른 추가 렌더링"""
        from game.state import GamePhase

        if state.phase == GamePhase.GAME_OVER:
            self._render_game_over()
        elif state.phase == GamePhase.VICTORY:
            self._render_victory()

    def _render_game_over(self) -> None:
        """게임 오버 화면"""
        text = self.font_large.render("GAME OVER", True, COLOR_RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def _render_victory(self) -> None:
        """승리 화면"""
        text = self.font_large.render("VICTORY!", True, COLOR_GREEN)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
