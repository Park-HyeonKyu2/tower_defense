"""
[담당: 박현규 - Pygame UI/입력]

UI 요소: 버튼, 패널, 텍스트 등
- 정보 패널 (골드, 라이프, 스테이지)
- 기능 버튼 (구매, 강화, 판매, 재배치, 웨이브 시작)
- 슬롯 표시 및 선택 피드백
- 게임 속도 조절 버튼
- 종료 버튼

renderer.py와 함께 UI 시스템을 담당합니다.
"""

import pygame
from typing import List, Tuple, Optional, Callable
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_GRAY


class Button:
    """버튼 클래스"""

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, callback: Callable = None):
        """
        버튼 초기화

        Args:
            x, y: 버튼 위치
            width, height: 버튼 크기
            text: 버튼 텍스트
            callback: 클릭 시 실행할 함수
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.Font(None, 20)

    def render(self, screen: pygame.Surface) -> None:
        """버튼 렌더링"""
        # 상태에 따라 색상 결정
        if self.is_pressed:
            color = (100, 100, 100)
        elif self.is_hovered:
            color = (150, 150, 150)
        else:
            color = COLOR_GRAY

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_WHITE, self.rect, 2)

        # 텍스트 렌더링
        text_surface = self.font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """
        클릭 감지

        Args:
            pos: 마우스 위치

        Returns:
            클릭됨 여부
        """
        if self.rect.collidepoint(pos):
            if self.callback:
                self.callback()
            return True
        return False

    def update_hover(self, pos: Tuple[int, int]) -> None:
        """호버 상태 업데이트"""
        self.is_hovered = self.rect.collidepoint(pos)


class UIPanel:
    """UI 패널"""

    def __init__(self):
        """UI 패널 초기화"""
        self.buttons: List[Button] = []
        self._initialize_buttons()

    def _initialize_buttons(self) -> None:
        """버튼들 초기화"""
        panel_x = SCREEN_WIDTH - 180
        button_width = 160
        button_height = 30
        y_offset = 200

        # START WAVE 버튼
        self.start_wave_button = Button(
            panel_x, y_offset, button_width, button_height,
            "Start Wave", None
        )
        self.buttons.append(self.start_wave_button)
        y_offset += 40

        # CLEAR SLOT 버튼 (판매)
        self.sell_button = Button(
            panel_x, y_offset, button_width, button_height,
            "Sell", None
        )
        self.buttons.append(self.sell_button)
        y_offset += 40

        # 속도 조절 버튼
        self.speed_up_button = Button(
            panel_x, y_offset, button_width // 2 - 2, button_height,
            "Speed +", None
        )
        self.buttons.append(self.speed_up_button)

        self.speed_down_button = Button(
            panel_x + button_width // 2 + 2, y_offset, button_width // 2 - 2, button_height,
            "Speed -", None
        )
        self.buttons.append(self.speed_down_button)
        y_offset += 40

        # 종료 버튼
        self.exit_button = Button(
            panel_x, y_offset, button_width, button_height,
            "Exit", None
        )
        self.buttons.append(self.exit_button)

    def render(self, screen: pygame.Surface) -> None:
        """모든 버튼 렌더링"""
        for button in self.buttons:
            button.render(screen)

    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """호버 상태 업데이트"""
        for button in self.buttons:
            button.update_hover(mouse_pos)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        클릭 처리

        Args:
            mouse_pos: 마우스 위치

        Returns:
            클릭된 버튼의 액션 이름, 클릭 없으면 None
        """
        for button in self.buttons:
            if button.is_clicked(mouse_pos):
                if button == self.start_wave_button:
                    return "START_WAVE"
                elif button == self.sell_button:
                    return "SELL"
                elif button == self.speed_up_button:
                    return "SPEED_UP"
                elif button == self.speed_down_button:
                    return "SPEED_DOWN"
                elif button == self.exit_button:
                    return "EXIT"
        return None


class SlotHighlight:
    """슬롯 선택 강조 표시"""

    def __init__(self):
        """슬롯 강조 초기화"""
        self.selected_slot: Optional[int] = None
        self.hover_slot: Optional[int] = None

    def set_selected(self, slot_id: int) -> None:
        """슬롯 선택"""
        self.selected_slot = slot_id

    def set_hover(self, slot_id: int) -> None:
        """슬롯 호버"""
        self.hover_slot = slot_id

    def clear_hover(self) -> None:
        """호버 초기화"""
        self.hover_slot = None

    def is_slot_selected(self, slot_id: int) -> bool:
        """슬롯이 선택되었는지 확인"""
        return self.selected_slot == slot_id

    def is_slot_hovered(self, slot_id: int) -> bool:
        """슬롯이 호버 상태인지 확인"""
        return self.hover_slot == slot_id
