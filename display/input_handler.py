"""
[담당: 박현규 - Pygame UI/입력]

입력 처리: 마우스/키보드 입력을 게임 행동으로 변환
- 마우스 클릭: 슬롯 선택, 버튼 클릭
- 키보드 입력: 게임 속도 조절, 일시 정지, 종료
- 입력을 Action 객체로 변환하여 엔진에 전달
- 입력 이벤트는 엔진에 직접 영향을 주지 않음 (엔진이 최종 검증)

renderer.py, ui.py와 함께 UI 시스템을 담당합니다.
"""

import pygame
from typing import Optional
from game.actions import Action, ActionType
from game.state import GameState
from display.ui import UIPanel


class InputHandler:
    """입력 처리자"""

    def __init__(self):
        """입력 처리자 초기화"""
        self.ui_panel = UIPanel()
        self.selected_slot: Optional[int] = None
        self.game_speed = 1.0  # 게임 속도 배수 (1.0 = 정상)

    def handle_event(self, event: pygame.event.Event,
                     state: GameState) -> Optional[Action]:
        """
        Pygame 이벤트 처리

        Args:
            event: Pygame 이벤트
            state: 현재 게임 상태

        Returns:
            생성된 Action, 또는 None
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event.pos, state)

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos, state)

        elif event.type == pygame.KEYDOWN:
            return self._handle_key_down(event.key, state)

        return None

    def _handle_mouse_down(self, mouse_pos: tuple,
                           state: GameState) -> Optional[Action]:
        """마우스 클릭 처리"""
        # UI 패널의 버튼 클릭 확인
        button_action = self.ui_panel.handle_click(mouse_pos)

        if button_action == "START_WAVE":
            return Action(ActionType.START_WAVE)

        elif button_action == "SELL":
            # 선택된 슬롯이 있으면 판매 행동 생성
            if self.selected_slot is not None:
                return Action(ActionType.SELL, slot_id=self.selected_slot)

        elif button_action == "SPEED_UP":
            self.game_speed = min(self.game_speed + 0.5, 3.0)
            print(f"게임 속도: {self.game_speed}x")
            return None

        elif button_action == "SPEED_DOWN":
            self.game_speed = max(self.game_speed - 0.5, 0.5)
            print(f"게임 속도: {self.game_speed}x")
            return None

        elif button_action == "EXIT":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return None

        # 게임 영역 클릭 (슬롯 선택 또는 구매)
        # 게임 영역 범위: (10, 10) ~ (SCREEN_WIDTH-210, SCREEN_HEIGHT-10)
        from config import SCREEN_WIDTH, SCREEN_HEIGHT
        game_area_right = SCREEN_WIDTH - 200

        if 10 < mouse_pos[0] < game_area_right and 10 < mouse_pos[1] < SCREEN_HEIGHT - 10:
            slot_id = self._get_slot_at_position(mouse_pos, state)

            if slot_id is not None:
                if self.selected_slot == slot_id:
                    # 같은 슬롯을 다시 클릭 → 구매 시도
                    return Action(ActionType.BUY, slot_id=slot_id)
                else:
                    # 슬롯 선택
                    self.selected_slot = slot_id
                    return None

        return None

    def _handle_mouse_motion(self, mouse_pos: tuple, state: GameState) -> None:
        """마우스 이동 처리"""
        self.ui_panel.update_hover(mouse_pos)

    def _handle_key_down(self, key: int, state: GameState) -> Optional[Action]:
        """키보드 입력 처리"""
        if key == pygame.K_SPACE:
            # 스페이스: 웨이브 시작
            return Action(ActionType.START_WAVE)

        elif key == pygame.K_UP:
            # 화살표 위: 속도 증가
            self.game_speed = min(self.game_speed + 0.5, 3.0)
            print(f"게임 속도: {self.game_speed}x")
            return None

        elif key == pygame.K_DOWN:
            # 화살표 아래: 속도 감소
            self.game_speed = max(self.game_speed - 0.5, 0.5)
            print(f"게임 속도: {self.game_speed}x")
            return None

        elif key == pygame.K_ESCAPE:
            # ESC: 게임 종료
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return None

        elif key == pygame.K_DELETE or key == pygame.K_d:
            # DEL 또는 D: 선택 슬롯 판매
            if self.selected_slot is not None:
                return Action(ActionType.SELL, slot_id=self.selected_slot)

        return None

    def _get_slot_at_position(self, mouse_pos: tuple,
                              state: GameState) -> Optional[int]:
        """
        마우스 위치에 해당하는 슬롯 ID 반환

        Args:
            mouse_pos: 마우스 위치
            state: 게임 상태

        Returns:
            슬롯 ID, 없으면 None
        """
        # 간단한 예시: 24개 슬롯을 3×8 격자로 배치
        game_area_width = 1000  # 대략값
        game_area_height = 780

        slot_width = game_area_width // 8
        slot_height = game_area_height // 3

        x = (mouse_pos[0] - 10) // slot_width
        y = (mouse_pos[1] - 10) // slot_height

        if 0 <= x < 8 and 0 <= y < 3:
            slot_id = y * 8 + x
            return slot_id

        return None

    def get_game_speed(self) -> float:
        """
        현재 게임 속도 배수 반환

        Returns:
            게임 속도 배수 (1.0 = 정상)
        """
        return self.game_speed

    def reset(self) -> None:
        """입력 상태 초기화"""
        self.selected_slot = None
        self.game_speed = 1.0
