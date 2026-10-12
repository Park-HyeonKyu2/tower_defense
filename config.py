"""
[담당: 공통 - 전체 팀]

공통 설정 및 상수들을 정의합니다.
게임의 화면 크기, FPS, 그리드 크기 등 전역 설정값을 관리합니다.
"""

# ===== 화면 설정 =====
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# ===== 맵 설정 =====
MAP_WIDTH = 20  # 맵 가로 칸 수
MAP_HEIGHT = 15  # 맵 세로 칸 수
SLOT_COUNT = 24  # 타워 설치 가능한 슬롯 수
MAX_STAGES = 30  # 최대 스테이지 수

# ===== 게임 설정 =====
INITIAL_LIFE = 20  # 시작 라이프
MAX_LIFE = 30  # 최대 라이프
INITIAL_GOLD = 100  # 시작 골드

# ===== 타워 설정 =====
MAX_TOWER_LEVEL = 5  # 타워 최대 강화 레벨
TOWER_TYPES = ["ARCHER", "CANNON", "ICE", "LIGHTNING"]  # 4가지 타워

# ===== 전투 설정 =====
MAX_ACTIONS_PER_WAVE = 20  # 준비 단계에서 최대 행동 가능 횟수 (구매/강화/판매/재배치)

# ===== 색상 정의 (RGB) =====
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
