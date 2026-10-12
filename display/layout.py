CELL = 50   # 한 칸의 크기
MAP_X = 0   # 맵 왼쪽 위 픽셀 위치
MAP_Y = 25  # 맵 왼쪽 위 픽셀 위치
MAP_COLS, MAP_ROWS = 20, 15 # 20 x 15 맵

def grid_to_pixel(col, row):
    """해당 칸의 왼쪽 위 픽셀 좌표를 반환"""
    return MAP_X + col * CELL, MAP_Y + row * CELL

def cell_center(col, row):
    """
    해당 칸의 중심 픽셀 좌표를 반환
    타워, 적 그릴 때 사용
    """
    x, y = grid_to_pixel(col, row)
    return x + CELL // 2, y + CELL // 2

def pixel_to_grid(x, y):
    """
    해당 픽셀 좌표가 어느 칸에 속하는지 반환
    맵 밖이면 None 반환
    """
    col, row = (x - MAP_X) // CELL, (y - MAP_Y) // CELL
    if 0 <= col < MAP_COLS and 0 <= row < MAP_ROWS:
        return col, row
    return None

# 임시 맵 데이터======================================================

# 경로: 꺾이는 지점만 (col, row). S(0,3) → E(19,11)
# 꺾이는 지점만 저장하면 적이 이동할 때도 이 값을 참고하여 이동할 수 있음
PATH_WAYPOINTS = [(0, 3), (16, 3), (16, 7), (3, 7), (3, 11), (19, 11)]

# 타워 설치 슬롯 좌표 (col, row) 리스트
SLOTS = [(2,1), (6,1), (10,1), (14,1), (4,2), (8,2), (12,2), (16,2),
         (18,3), (4,4), (8,4), (12,4), (2,5), (6,5), (10,5), (14,5),
         (18,5), (4,6), (8,6), (12,6), (2,7), (2,9), (18,7), (4,8), 
         (8,8), (12, 8), (16,8), (6,9), (10,9), (14,9), (4,10), (8,10), 
         (12,10), (16,10), (2,11), (4,12), (8,12), (12,12), (16,12), 
         (6,13), (10,13), (14,13), (18,13)]

# ====================================================================

def expand_path(waypoints):
    cells = [waypoints[0]]
    for (c1, r1), (c2, r2) in zip(waypoints, waypoints[1:]):
        # 가로 방향 정하기
        if c2 > c1:
            dc = 1      # 오른쪽으로
        elif c2 < c1:
            dc = -1     # 왼쪽으로
        else:
            dc = 0      # 안 움직임

        # 세로 방향 정하기
        if r2 > r1:
            dr = 1      # 아래로 (row가 커질수록 화면 아래)
        elif r2 < r1:
            dr = -1     # 위로
        else:
            dr = 0      # 안 움직임
        c, r = c1, r1

        while (c, r) != (c2, r2):
            c += dc
            r += dr
            cells.append((c, r))
    return cells