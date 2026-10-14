import pygame
from pathlib import Path

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Moon Guardians - Sprite Test")

clock = pygame.time.Clock()

# 캐릭터 파일
SPRITES = {
    1: "백호.png",
    2: "주작.png",
    3: "청룡.png",
    4: "현무.png",
}

# 행 순서
DIRECTIONS = {
    pygame.K_w: 0,  # 북서
    pygame.K_e: 1,  # 북동
    pygame.K_a: 2,  # 남서
    pygame.K_d: 3,  # 남동
}

DIRECTION_NAMES = ["NW", "NE", "SW", "SE"]

FRAMES = 4
ANIMATION_SPEED = 200  # ms
DISPLAY_SIZE = 220


def load_sprite_sheet(filename):
    path = Path("assets") / filename
    sheet = pygame.image.load(str(path)).convert_alpha()

    frame_width = sheet.get_width() // 4
    frame_height = sheet.get_height() // 4

    animations = []

    for row in range(4):
        direction_frames = []

        for col in range(4):
            rect = pygame.Rect(
                col * frame_width,
                row * frame_height,
                frame_width,
                frame_height
            )

            frame = sheet.subsurface(rect).copy()

            frame = pygame.transform.smoothscale(
                frame, (DISPLAY_SIZE, DISPLAY_SIZE)
            )

            direction_frames.append(frame)

        animations.append(direction_frames)

    return animations


# 4종 캐릭터 로드
characters = {
    key: load_sprite_sheet(filename)
    for key, filename in SPRITES.items()
}

selected_character = 1
direction = 2
frame_index = 0
playing = True
elapsed = 0

font = pygame.font.SysFont(None, 30)

running = True

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if pygame.K_1 <= event.key <= pygame.K_4:
                selected_character = event.key - pygame.K_0
                frame_index = 0

            if event.key in DIRECTIONS:
                direction = DIRECTIONS[event.key]
                frame_index = 0

            if event.key == pygame.K_SPACE:
                playing = not playing

            if event.key == pygame.K_LEFT:
                playing = False
                frame_index = (frame_index - 1) % FRAMES

            if event.key == pygame.K_RIGHT:
                playing = False
                frame_index = (frame_index + 1) % FRAMES

    # 애니메이션 진행
    if playing:
        elapsed += dt

        if elapsed >= ANIMATION_SPEED:
            elapsed %= ANIMATION_SPEED
            frame_index = (frame_index + 1) % FRAMES

    # 배경
    screen.fill((32, 48, 65))

    # 타일 받침
    pygame.draw.ellipse(
        screen,
        (67, 86, 104),
        (280, 390, 240, 55)
    )

    # 현재 프레임
    image = characters[selected_character][direction][frame_index]

    rect = image.get_rect(center=(400, 300))
    screen.blit(image, rect)

    # 상태 텍스트
    info = [
        f"Character: {selected_character}",
        f"Direction: {DIRECTION_NAMES[direction]}",
        f"Frame: {frame_index + 1}/4",
        f"Playing: {playing}",
        "1-4: Character | W/E/A/D: Direction",
        "SPACE: Play/Pause | LEFT/RIGHT: Frame"
    ]

    for i, line in enumerate(info):
        text = font.render(line, True, (240, 240, 240))
        screen.blit(text, (20, 20 + i * 32))

    pygame.display.flip()

pygame.quit()
