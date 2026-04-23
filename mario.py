import pygame, sys, math, random, os

pygame.init()

WIN_W, WIN_H = 800, 480
TILE = 32
FPS = 60
WORLD_COLS = 240
WORLD_ROWS = WIN_H // TILE  # 15

GRAVITY   = 0.55
JUMP_VEL  = -13.0
WALK_SPD  = 4.5

# Tile IDs
EMPTY=0; GROUND=1; BRICK=2; COIN_BLK=3; USED_BLK=4
ITEM_W = 22; ITEM_H = 24   # spawned item size

# Colours
SKY    = (92, 148, 252)
WHITE  = (255,255,255)
BLACK  = (0,  0,  0  )
GND_T  = (106,190, 48)
GND_B  = (139, 90, 43)
BRICK_C= (185, 95, 32)
BRICK_D= (140, 55, 10)
CBLK_C = (230,155, 10)
USED_C = (150,120, 80)
COIN_C = (255,215,  0)
RED    = (200, 40, 40)
BLUE   = ( 40, 80,200)
SKIN   = (255,185,120)
BROWN  = (120, 70, 30)
GB1    = (162, 84, 14)   # warm brown body
GB2    = (68,  30,  4)   # very dark brown feet / shadow
GBTAN  = (225,185,128)   # tan belly patch
MUSH_CAP  = (210,  50,  30)  # mushroom red cap
MUSH_STEM = (240, 200, 150)  # mushroom pale stem
MUSH_DOT  = (255, 255, 255)  # white dots on cap
FLOWER_O  = (255, 130,   0)  # fire flower outer petals
FLOWER_Y  = (255, 220,   0)  # fire flower inner / center
# ── Pipe / Flagpole ───────────────────────────────────────────────────────────
PIPE_W     = TILE * 2               # 64 px wide
PIPE_H     = TILE * 3               # 96 px tall
PIPE_COLS  = [22, 44, 94, 145, 193] # world columns; pipe[0]→pipe[1] warp
PIPE_GREEN = (0,  160,   0)
PIPE_LIGHT = (80, 220,  80)
PIPE_DARK  = (0,   90,   0)
FLAG_COL   = WORLD_COLS - 6         # = 234
FLAG_TOP   = 5  * TILE              # y = 160
FLAG_BOT   = 12 * TILE              # y = 384 (ground level)
FLAG_X     = FLAG_COL * TILE        # world x of pole

# ── Fonts (init after pygame.init) ───────────────────────────────────────────
_fhud = _fq = None
def _fonts():
    global _fhud, _fq
    if _fhud is None:
        _fhud = pygame.font.SysFont('consolas', 18, bold=True)
        _fq   = pygame.font.SysFont('consolas', 16, bold=True)

# ── Level ────────────────────────────────────────────────────────────────────
def make_level():
    w = [[EMPTY]*WORLD_COLS for _ in range(WORLD_ROWS)]
    for r in range(12, WORLD_ROWS):
        for c in range(WORLD_COLS):
            w[r][c] = GROUND
    # Gaps
    for g in [30, 65, 105, 148, 187, 218]:
        for c in range(g, g+3):
            for r in range(12, WORLD_ROWS):
                w[r][c] = EMPTY
    # Pipe clear zones: 1-tile margin on each side of every pipe (pipe is 2 tiles wide)
    pipe_clear = set()
    for pc in PIPE_COLS:
        for c in range(pc - 1, pc + PIPE_W // TILE + 1):
            pipe_clear.add(c)

    # Platforms — 3-tier staircase layout:
    #   tier 1 (row 9, COIN_BLK): jumpable from ground
    #   tier 2 (row 7, COIN_BLK): reachable from tier 1, not from ground
    #   tier 3 (row 5, BRICK   ): reachable from tier 1/2, brick-only platform
    defs = [
        # ── Cluster 1  (before pipe@22) ───────────────────────────────────
        (4,  9, 2, COIN_BLK), (8,  7, 2, COIN_BLK), (12, 5, 4, BRICK),
        (17, 9, 1, COIN_BLK),

        # ── Cluster 2  (gap@30 → pipe@44) ─────────────────────────────────
        (33, 9, 2, COIN_BLK), (37, 7, 3, COIN_BLK),

        # ── Cluster 3  (pipe@44 → gap@65) ─────────────────────────────────
        (47, 9, 2, COIN_BLK), (51, 7, 2, COIN_BLK), (55, 5, 4, BRICK),
        (61, 9, 1, COIN_BLK),

        # ── Cluster 4  (gap@65 → pipe@94) ─────────────────────────────────
        (68, 9, 2, COIN_BLK), (72, 7, 2, COIN_BLK), (76, 5, 4, BRICK),
        (82, 9, 2, COIN_BLK), (86, 7, 3, BRICK),

        # ── Cluster 5  (pipe@94 → gap@105) ────────────────────────────────
        (97, 9, 2, COIN_BLK), (101, 7, 2, BRICK),

        # ── Cluster 6  (gap@105 → pipe@145) ───────────────────────────────
        (108, 9, 2, COIN_BLK), (112, 7, 2, COIN_BLK), (116, 5, 4, BRICK),
        (123, 9, 3, COIN_BLK), (128, 7, 2, BRICK),    (132, 5, 4, BRICK),
        (138, 9, 2, COIN_BLK), (141, 7, 2, BRICK),

        # ── Cluster 7  (gap@148 → gap@187) ────────────────────────────────
        (151, 9, 2, COIN_BLK), (155, 7, 2, COIN_BLK), (159, 5, 4, BRICK),
        (165, 9, 2, COIN_BLK), (169, 7, 2, BRICK),    (173, 5, 4, BRICK),
        (180, 9, 3, COIN_BLK), (184, 7, 2, BRICK),

        # ── Cluster 8  (pipe@193 → gap@218) ───────────────────────────────
        (196, 9, 2, COIN_BLK), (200, 7, 2, COIN_BLK), (204, 5, 4, BRICK),
        (210, 9, 3, COIN_BLK), (214, 7, 2, BRICK),

        # ── Cluster 9  (gap@218 → flagpole@234) ───────────────────────────
        (221, 9, 2, COIN_BLK), (225, 7, 2, BRICK),    (229, 5, 3, BRICK),
    ]
    for col,row,width,t in defs:
        for c in range(col, min(col+width, WORLD_COLS)):
            if c not in pipe_clear:
                w[row][c] = t
    return w

def is_solid(t):
    return t in (GROUND, BRICK, COIN_BLK, USED_BLK)

def tile_at(world, c, r):
    if 0 <= c < WORLD_COLS and 0 <= r < WORLD_ROWS:
        return world[r][c]
    if r >= WORLD_ROWS: return GROUND
    return EMPTY

# ── Underground level ────────────────────────────────────────────────────────
UG_COLS = 100   # underground map width in tiles

def make_underground():
    w = [[EMPTY]*UG_COLS for _ in range(WORLD_ROWS)]
    # Ceiling (rows 0-1)
    for c in range(UG_COLS):
        w[0][c] = BRICK
        w[1][c] = BRICK
    # Floor (rows 13-14)
    for c in range(UG_COLS):
        for r in range(13, WORLD_ROWS):
            w[r][c] = GROUND
    # Left/right boundary walls
    for r in range(WORLD_ROWS):
        w[r][0] = BRICK; w[r][1] = BRICK
        w[r][UG_COLS-1] = BRICK; w[r][UG_COLS-2] = BRICK
    # Pipe clear columns (entry=5, decor=30,55, exit=82; 2-tile wide + 1 margin each side)
    ug_pipe_clear = set()
    for pc in (5, 30, 55, 82):
        for c in range(pc-1, pc+3):
            ug_pipe_clear.add(c)
    # Platforms: row 9 (low) BRICK/COIN, row 7 (mid), row 5 (high, near ceiling)
    ug_defs = [
        (8,  9, 2, BRICK),    (21, 9, 3, COIN_BLK), (35, 9, 4, BRICK),
        (50, 9, 3, COIN_BLK), (64, 9, 3, BRICK),    (78, 9, 3, COIN_BLK),
        (14, 7, 3, BRICK),    (25, 7, 3, COIN_BLK),  (39, 7, 4, BRICK),
        (58, 7, 3, COIN_BLK), (74, 7, 3, BRICK),
        (10, 5, 3, COIN_BLK), (45, 5, 3, COIN_BLK),  (68, 5, 3, COIN_BLK),
    ]
    for col, row, width, t in ug_defs:
        for c in range(col, min(col+width, UG_COLS)):
            if c not in ug_pipe_clear:
                w[row][c] = t
    return w

# ── Cloud helpers ─────────────────────────────────────────────────────────────
def make_clouds():
    clouds = []
    for i in range(60):
        x = random.randint(0, WORLD_COLS * TILE)
        y = random.randint(20, 120)
        w = random.randint(60, 140)
        clouds.append((x, y, w))
    return clouds

def draw_clouds(surf, clouds, cam_x):
    for cx, cy, cw in clouds:
        px = cx - cam_x
        if -cw < px < WIN_W + cw:
            ch = cw // 3
            pygame.draw.ellipse(surf, WHITE, (px, cy, cw, ch))
            pygame.draw.ellipse(surf, WHITE, (px + cw//4, cy - ch//2, cw//2, ch))

# ── Tile drawing ──────────────────────────────────────────────────────────────
def draw_tile(surf, tile, px, py, underground=False):
    _fonts()
    if underground:
        if tile == GROUND:
            pygame.draw.rect(surf, (75, 75, 85), (px, py, TILE, TILE))
            pygame.draw.rect(surf, (50, 50, 60), (px, py, TILE, TILE), 2)
        elif tile == BRICK:
            pygame.draw.rect(surf, (105, 105, 118), (px, py, TILE, TILE))
            pygame.draw.line(surf, (70, 70, 82), (px, py+TILE//2), (px+TILE, py+TILE//2), 1)
            pygame.draw.line(surf, (70, 70, 82), (px+TILE//2, py), (px+TILE//2, py+TILE//2), 1)
            pygame.draw.line(surf, (70, 70, 82), (px, py+TILE//2), (px, py+TILE), 1)
            pygame.draw.rect(surf, (138, 138, 150), (px, py, TILE, TILE), 1)
        elif tile == COIN_BLK:
            pygame.draw.rect(surf, CBLK_C, (px, py, TILE, TILE))
            pygame.draw.rect(surf, (170, 110, 0), (px, py, TILE, TILE), 2)
            t = _fq.render('?', True, WHITE)
            surf.blit(t, (px+TILE//2-t.get_width()//2, py+TILE//2-t.get_height()//2))
        elif tile == USED_BLK:
            pygame.draw.rect(surf, USED_C, (px, py, TILE, TILE))
            pygame.draw.rect(surf, (120, 90, 60), (px, py, TILE, TILE), 2)
        return
    if tile == GROUND:
        pygame.draw.rect(surf, GND_T, (px, py, TILE, 8))
        pygame.draw.rect(surf, GND_B, (px, py+8, TILE, TILE-8))
        pygame.draw.line(surf, (80,155,30), (px,py+8),(px+TILE,py+8), 2)
    elif tile == BRICK:
        pygame.draw.rect(surf, BRICK_C, (px,py,TILE,TILE))
        pygame.draw.line(surf, BRICK_D, (px,py+TILE//2),(px+TILE,py+TILE//2),1)
        pygame.draw.line(surf, BRICK_D, (px+TILE//2,py),(px+TILE//2,py+TILE//2),1)
        pygame.draw.line(surf, BRICK_D, (px,py+TILE//2),(px,py+TILE),1)
        pygame.draw.rect(surf, (220,130,60),(px,py,TILE,TILE),1)
    elif tile == COIN_BLK:
        pygame.draw.rect(surf, CBLK_C, (px,py,TILE,TILE))
        pygame.draw.rect(surf, (170,110,0),(px,py,TILE,TILE),2)
        t = _fq.render('?', True, WHITE)
        surf.blit(t, (px+TILE//2-t.get_width()//2, py+TILE//2-t.get_height()//2))
    elif tile == USED_BLK:
        pygame.draw.rect(surf, USED_C, (px,py,TILE,TILE))
        pygame.draw.rect(surf,(120,90,60),(px,py,TILE,TILE),2)

# ── Mario drawing ─────────────────────────────────────────────────────────────
MARIO_H_SMALL = 36
MARIO_H_BIG   = 64

def draw_mario(surf, x, y, facing, frame, dead=False, big=False):
    bx, by = int(x), int(y)
    if dead:
        pygame.draw.ellipse(surf, RED, (bx+2, by+4, 28, 28))
        pygame.draw.rect(surf, RED, (bx+4, by, 20, 6))
        return

    if big:
        # ── Big Mario (28×64) ──────────────────────────────────────────────
        pygame.draw.rect(surf, RED,        (bx+6,  by-8,  16, 12))  # hat crown
        pygame.draw.rect(surf, RED,        (bx+2,  by+3,  24,  8))  # hat brim
        pygame.draw.rect(surf, (80,50,20), (bx+2,  by+10,  6,  5))  # hair
        pygame.draw.rect(surf, SKIN,       (bx+4,  by+10, 20, 14))  # face
        ex = bx+18 if facing==1 else bx+6
        pygame.draw.rect(surf, BLACK,      (ex,    by+13,  4,  4))  # eye
        pygame.draw.rect(surf, SKIN,       (bx+10, by+17,  8,  5))  # nose
        pygame.draw.rect(surf, (80,50,20), (bx+4,  by+22, 20,  4))  # moustache
        pygame.draw.rect(surf, BLUE,       (bx+2,  by+26, 24, 18))  # overalls
        pygame.draw.rect(surf, RED,        (bx+2,  by+26,  8,  6))  # susp L
        pygame.draw.rect(surf, RED,        (bx+18, by+26,  8,  6))  # susp R
        arm_x = bx+26 if facing==1 else bx-4
        pygame.draw.rect(surf, RED,        (arm_x, by+26,  6, 12))  # arm
        pygame.draw.rect(surf, SKIN,       (arm_x, by+36,  6,  6))  # hand
        step = frame % 2
        if step == 0:
            pygame.draw.rect(surf, BLUE,  (bx+2,  by+44, 12, 15))
            pygame.draw.rect(surf, BLUE,  (bx+16, by+39, 12, 20))
            pygame.draw.rect(surf, BROWN, (bx+0,  by+57, 14,  7))
            pygame.draw.rect(surf, BROWN, (bx+14, by+57, 14,  7))
        else:
            pygame.draw.rect(surf, BLUE,  (bx+2,  by+39, 12, 20))
            pygame.draw.rect(surf, BLUE,  (bx+16, by+44, 12, 15))
            pygame.draw.rect(surf, BROWN, (bx+0,  by+57, 14,  7))
            pygame.draw.rect(surf, BROWN, (bx+14, by+57, 14,  7))
        return

    # ── Small Mario (28×36) ───────────────────────────────────────────────
    # Hat
    pygame.draw.rect(surf, RED, (bx+3,by+2,26,5))
    pygame.draw.rect(surf, RED, (bx+7,by-5,16,8))
    # Hair
    pygame.draw.rect(surf, (80,50,20),(bx+3,by+6,5,4))
    # Face
    pygame.draw.rect(surf, SKIN,(bx+4,by+6,22,8))
    # Eye
    ex = bx+20 if facing==1 else bx+8
    pygame.draw.rect(surf, BLACK,(ex,by+7,3,3))
    # Nose
    pygame.draw.rect(surf, SKIN,(bx+12,by+9,6,3))
    # Moustache
    pygame.draw.rect(surf,(80,50,20),(bx+6,by+12,18,3))
    # Overalls
    pygame.draw.rect(surf, BLUE,(bx+3,by+14,26,10))
    pygame.draw.rect(surf, RED,(bx+3,by+14,7,4))
    pygame.draw.rect(surf, RED,(bx+22,by+14,7,4))
    # Arm
    arm_x = bx+27 if facing==1 else bx-3
    pygame.draw.rect(surf, RED,(arm_x,by+14,6,7))
    pygame.draw.rect(surf, SKIN,(arm_x,by+19,6,4))
    # Legs
    step = frame % 2
    if step == 0:
        pygame.draw.rect(surf, BLUE,(bx+3,by+24,11,9))
        pygame.draw.rect(surf, BLUE,(bx+18,by+21,11,12))
        pygame.draw.rect(surf, BROWN,(bx+1,by+31,13,5))
        pygame.draw.rect(surf, BROWN,(bx+16,by+31,13,5))
    else:
        pygame.draw.rect(surf, BLUE,(bx+3,by+21,11,12))
        pygame.draw.rect(surf, BLUE,(bx+18,by+24,11,9))
        pygame.draw.rect(surf, BROWN,(bx+1,by+31,13,5))
        pygame.draw.rect(surf, BROWN,(bx+16,by+31,13,5))

# ── Goomba drawing ────────────────────────────────────────────────────────────
def draw_goomba(surf, x, y, frame, stomped):
    bx, by = int(x), int(y)

    if stomped:
        # 납작하게 밟힌 상태
        pygame.draw.ellipse(surf, GB1, (bx+2,  by+26, 26, 7))
        pygame.draw.ellipse(surf, GB2, (bx+5,  by+28, 20, 4))
        # X 눈
        for ex in (bx+8, bx+20):
            ey = by + 24
            pygame.draw.line(surf, BLACK, (ex,   ey),   (ex+4, ey+4), 2)
            pygame.draw.line(surf, BLACK, (ex+4, ey),   (ex,   ey+4), 2)
        return

    step = frame % 2

    # === 발 (어두운 갈색, 걷기 애니메이션) ===
    if step == 0:
        pygame.draw.ellipse(surf, GB2, (bx+0,  by+25, 13, 8))
        pygame.draw.ellipse(surf, GB2, (bx+17, by+22, 13, 8))
    else:
        pygame.draw.ellipse(surf, GB2, (bx+0,  by+22, 13, 8))
        pygame.draw.ellipse(surf, GB2, (bx+17, by+25, 13, 8))

    # === 몸체 (둥근 버섯 모양, 갈색) ===
    pygame.draw.ellipse(surf, GB1, (bx+1,  by+13, 28, 19))  # 하체
    pygame.draw.circle(surf, GB1,  (bx+15, by+13), 13)       # 둥근 머리

    # === 배 패치 (밝은 베이지색) ===
    pygame.draw.ellipse(surf, GBTAN, (bx+8, by+18, 14, 11))

    # === 눈 (큰 흰 타원) ===
    pygame.draw.ellipse(surf, WHITE, (bx+4,  by+7, 11, 10))  # 왼쪽 눈
    pygame.draw.ellipse(surf, WHITE, (bx+17, by+7, 11, 10))  # 오른쪽 눈

    # === 동공 ===
    pygame.draw.circle(surf, BLACK, (bx+10, by+12), 3)
    pygame.draw.circle(surf, BLACK, (bx+22, by+12), 3)

    # 눈 하이라이트 (작은 흰 점)
    pygame.draw.circle(surf, WHITE, (bx+9,  by+10), 1)
    pygame.draw.circle(surf, WHITE, (bx+21, by+10), 1)

    # === 화난 눈썹 (V자형, 두꺼운 대각선) ===
    pygame.draw.line(surf, BLACK, (bx+2,  by+8), (bx+12, by+3), 3)  # 왼쪽 눈썹
    pygame.draw.line(surf, BLACK, (bx+18, by+3), (bx+28, by+8), 3)  # 오른쪽 눈썹

    # === 엄니 두 개 (흰 삼각형) ===
    pygame.draw.polygon(surf, WHITE, [
        (bx+11, by+23), (bx+14, by+18), (bx+17, by+23)
    ])
    pygame.draw.polygon(surf, WHITE, [
        (bx+15, by+23), (bx+18, by+18), (bx+21, by+23)
    ])
    # 엄니 외곽선
    pygame.draw.polygon(surf, GB2, [(bx+11, by+23), (bx+14, by+18), (bx+17, by+23)], 1)
    pygame.draw.polygon(surf, GB2, [(bx+15, by+23), (bx+18, by+18), (bx+21, by+23)], 1)

# ── Coin drawing ──────────────────────────────────────────────────────────────
def draw_coin(surf, x, y, t):
    w = max(3, int(12 * abs(math.sin(t))))
    pygame.draw.ellipse(surf, COIN_C, (x+8-w//2, y, w, 18))
    if w > 5:
        pygame.draw.ellipse(surf, WHITE, (x+8-w//2+1, y+2, max(1,w-4), 7))

# ── Mushroom drawing ──────────────────────────────────────────────────────────
def draw_mushroom(surf, x, y):
    bx, by = int(x), int(y)
    # Stem
    pygame.draw.rect(surf, MUSH_STEM, (bx+3, by+12, 16, 12))
    pygame.draw.rect(surf, (180,140,100), (bx+3, by+12, 16, 12), 1)
    # Eyes on stem
    pygame.draw.rect(surf, BLACK, (bx+5,  by+14, 3, 4))
    pygame.draw.rect(surf, BLACK, (bx+14, by+14, 3, 4))
    pygame.draw.circle(surf, WHITE, (bx+6,  by+15), 1)
    pygame.draw.circle(surf, WHITE, (bx+15, by+15), 1)
    # Cap underside (pale strip)
    pygame.draw.ellipse(surf, MUSH_STEM, (bx+2, by+11, 18, 5))
    # Cap (red)
    pygame.draw.ellipse(surf, MUSH_CAP, (bx, by, 22, 14))
    # White dots on cap
    pygame.draw.circle(surf, MUSH_DOT, (bx+5,  by+6),  3)
    pygame.draw.circle(surf, MUSH_DOT, (bx+16, by+5),  3)
    pygame.draw.circle(surf, MUSH_DOT, (bx+11, by+10), 2)

# ── Fire flower drawing ───────────────────────────────────────────────────────
def draw_flower(surf, x, y):
    bx, by = int(x), int(y)
    # Stem
    pygame.draw.rect(surf, (50, 160, 50), (bx+9, by+12, 4, 12))
    # 5 petals (top, upper-left, lower-left, lower-right, upper-right)
    for dx, dy in ((0,-7), (-7,-2), (-4,6), (4,6), (7,-2)):
        pygame.draw.circle(surf, FLOWER_O, (bx+11+dx, by+8+dy), 5)
        pygame.draw.circle(surf, FLOWER_Y, (bx+11+dx, by+8+dy), 3)
    # Center
    pygame.draw.circle(surf, FLOWER_Y, (bx+11, by+8), 5)
    pygame.draw.circle(surf, WHITE,    (bx+11, by+8), 2)

# ── Pipe drawing ──────────────────────────────────────────────────────────────
def draw_pipe(surf, sx, sy):
    sw, sh = PIPE_W, PIPE_H
    # Body (below cap)
    pygame.draw.rect(surf, PIPE_DARK,  (sx + 4,  sy + 16, sw - 8,  sh - 16))
    pygame.draw.rect(surf, PIPE_GREEN, (sx + 6,  sy + 18, sw - 12, sh - 18))
    pygame.draw.rect(surf, PIPE_LIGHT, (sx + 8,  sy + 20, 10,       sh - 22))
    # Cap
    pygame.draw.rect(surf, PIPE_DARK,  (sx,      sy,      sw,      16))
    pygame.draw.rect(surf, PIPE_GREEN, (sx + 2,  sy + 2,  sw - 4,  12))
    pygame.draw.rect(surf, PIPE_LIGHT, (sx + 4,  sy + 4,  14,       6))

# ── Flagpole drawing ──────────────────────────────────────────────────────────
def draw_flagpole(surf, cam_x):
    px = FLAG_X - int(cam_x)
    if not (-20 < px < WIN_W + 60):
        return
    # Pole
    pygame.draw.rect(surf, (150, 150, 150), (px + 1, FLAG_TOP,     4, FLAG_BOT - FLAG_TOP))
    pygame.draw.rect(surf, WHITE,           (px + 2, FLAG_TOP + 2, 2, FLAG_BOT - FLAG_TOP - 4))
    # Gold ball at top
    pygame.draw.circle(surf, COIN_C,       (px + 3, FLAG_TOP), 6)
    pygame.draw.circle(surf, (200, 160, 0),(px + 3, FLAG_TOP), 4)
    # Green triangular flag (right side of pole)
    fx, fy = px + 6, FLAG_TOP + 2
    pygame.draw.polygon(surf, (0, 180, 60), [(fx, fy), (fx+30, fy+14), (fx, fy+28)])
    pygame.draw.polygon(surf, (0, 110, 35), [(fx, fy), (fx+30, fy+14), (fx, fy+28)], 1)

# ── Game ──────────────────────────────────────────────────────────────────────
class MarioGame:
    MARIO_W = 28
    MARIO_H = 36   # kept for backward compat; use _mario_h for live hitbox
    GOOMBA_W, GOOMBA_H = 30, 32

    @property
    def _mario_h(self):
        return MARIO_H_BIG if self.mario_big else MARIO_H_SMALL

    def __init__(self):
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption('슈퍼마리오')
        self.clock = pygame.time.Clock()
        _fonts()
        self.world = make_level()
        self.clouds = make_clouds()
        self.cleared_stages  = [False, False, False]
        self.worldmap_cursor = 0
        self.current_stage   = 0
        self._wm_anim_t      = 0
        self._wm_anim_frame  = 0
        self.state = 'title'
        self.reset()

    def reset(self):
        """Full reset — new game from scratch."""
        self.cleared_stages  = [False, False, False]
        self.worldmap_cursor = 0
        self.score  = 0
        self.lives  = 3
        self.coins  = 0
        self._start_stage(0)

    def _start_stage(self, idx):
        """Per-stage reset — keeps score/lives/coins/cleared_stages."""
        self.current_stage = idx
        self.mx   = float(2 * TILE)
        self.my   = float(10 * TILE)
        self.mvx  = 0.0
        self.mvy  = 0.0
        self.on_ground = False
        self.facing    = 1
        self.anim_t    = 0
        self.anim_frame= 0
        self.dead      = False
        self.dead_t    = 0
        self.cam_x  = 0.0
        self.world = make_level()
        self.block_bumps = []
        self.items       = []
        self.mario_big   = False
        self.mario_fire  = False
        self.grow_t      = 0    # ms remaining for grow/shrink blink animation
        # Pipes
        _gy = 12 * TILE
        self.pipes = [pygame.Rect(col * TILE, _gy - PIPE_H, PIPE_W, PIPE_H)
                      for col in PIPE_COLS]
        # Transition state
        self.fade_alpha   = 0
        self.pipe_enter_t = 0
        self.pipe_exit_t  = 0
        self.flag_t       = 0
        # Goombas
        goomba_cols = [14,24,38,53,63,76,92,103,118,133,146,163,177,205,215,226]
        self.goombas = []
        for col in goomba_cols:
            for row in range(WORLD_ROWS-1,-1,-1):
                if is_solid(tile_at(self.world, col, row)):
                    gx = float(col * TILE)
                    gy = float(row * TILE - self.GOOMBA_H)
                    self.goombas.append({
                        'x': gx, 'y': gy, 'vx': -1.5, 'vy': 0.0,
                        'alive': True, 'stomped': False, 'stomp_t': 0,
                        'frame': 0, 'frame_t': 0,
                    })
                    break

        # ── Underground stage init ────────────────────────────────────────────
        self.current_map = 'surface'
        self.world_cols  = WORLD_COLS
        self.ug_world    = make_underground()
        _ug_gy           = 13 * TILE
        _ug_pipe_cols    = [5, 30, 55, 82]
        self.ug_pipes    = [pygame.Rect(c * TILE, _ug_gy - PIPE_H, PIPE_W, PIPE_H)
                            for c in _ug_pipe_cols]
        ug_goomba_cols   = [12, 22, 38, 48, 62, 72, 86]
        self.ug_goombas  = []
        for col in ug_goomba_cols:
            for row in range(WORLD_ROWS - 1, -1, -1):
                if is_solid(tile_at(self.ug_world, col, row)):
                    self.ug_goombas.append({
                        'x': float(col * TILE), 'y': float(row * TILE - self.GOOMBA_H),
                        'vx': -1.5, 'vy': 0.0,
                        'alive': True, 'stomped': False, 'stomp_t': 0,
                        'frame': 0, 'frame_t': 0,
                    })
                    break
        # Save surface references for restoration when returning from underground
        self.surface_world   = self.world
        self.surface_pipes   = self.pipes
        self.surface_goombas = self.goombas

    # ── Collision ─────────────────────────────────────────────────────────────
    def _get_tile_overlaps(self, rect):
        c1 = max(0, rect.left   // TILE)
        c2 = min(self.world_cols-1, (rect.right-1)  // TILE)
        r1 = max(0, rect.top    // TILE)
        r2 = min(WORLD_ROWS,   (rect.bottom-1) // TILE)
        return c1, c2, r1, r2

    def _move(self, rect, vx, vy):
        on_ground = False
        hit_ceiling_tiles = []

        # ── Horizontal ──
        rect.x += round(vx)
        c1,c2,r1,r2 = self._get_tile_overlaps(rect)
        for r in range(r1, r2+1):
            for c in range(c1, c2+1):
                if is_solid(tile_at(self.world, c, r)):
                    if vx > 0:
                        rect.right = c * TILE; vx = 0
                    elif vx < 0:
                        rect.left  = (c+1) * TILE; vx = 0
        rect.x = max(0, rect.x)
        # Pipe collision (horizontal)
        for pipe in self.pipes:
            if rect.colliderect(pipe):
                if vx > 0: rect.right = pipe.left; vx = 0
                elif vx < 0: rect.left  = pipe.right; vx = 0

        # ── Vertical ──
        rect.y += round(vy)
        c1,c2,r1,r2 = self._get_tile_overlaps(rect)
        for r in range(r1, r2+1):
            for c in range(c1, c2+1):
                t = tile_at(self.world, c, r)
                if is_solid(t):
                    if vy > 0:
                        rect.bottom = r * TILE
                        on_ground = True; vy = 0
                    elif vy < 0:
                        rect.top = (r+1) * TILE
                        hit_ceiling_tiles.append((c, r))
                        vy = 0
        # Pipe collision (vertical)
        for pipe in self.pipes:
            if rect.colliderect(pipe):
                if vy > 0: rect.bottom = pipe.top; on_ground = True; vy = 0
                elif vy < 0: rect.top = pipe.bottom; vy = 0

        return vx, vy, on_ground, hit_ceiling_tiles

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt, keys):
        if self.state in ('title', 'gameover', 'win', 'worldmap'):
            return

        # ── Pipe enter (지상 → 지하: 마리오가 파이프 속으로 내려감) ─────────────
        if self.state == 'pipe_enter':
            self.pipe_enter_t += dt
            self.my += 1.5
            self.fade_alpha = min(255, int(self.pipe_enter_t / 500 * 255))
            if self.pipe_enter_t >= 700:
                # Save current surface state and activate underground
                self.surface_world   = self.world
                self.surface_pipes   = self.pipes
                self.surface_goombas = self.goombas
                self.surface_cam_x   = self.cam_x
                self.world      = self.ug_world
                self.pipes      = self.ug_pipes
                self.goombas    = self.ug_goombas
                self.world_cols = UG_COLS
                self.current_map = 'underground'
                self.block_bumps = []
                self.items       = []
                ep = self.pipes[0]   # underground entry pipe (col 5)
                self.mx       = float(ep.left + (PIPE_W - self.MARIO_W) // 2)
                self.my       = float(ep.top + 8)
                target_cam    = self.mx - WIN_W // 3
                self.cam_x    = max(0.0, min(float(target_cam),
                                             float(UG_COLS * TILE - WIN_W)))
                self.state       = 'pipe_exit'
                self.pipe_exit_t = 0
                self.fade_alpha  = 255
            return

        # ── Pipe exit (파이프에서 나타남) ─────────────────────────────────────
        if self.state == 'pipe_exit':
            self.pipe_exit_t += dt
            self.my -= 1.5
            self.fade_alpha = max(0, 255 - int(self.pipe_exit_t / 400 * 255))
            if self.pipe_exit_t >= 600:
                self.state      = 'playing'
                self.fade_alpha = 0
                self.mvy        = 0
            return

        # ── Underground exit (지하 → 지상: 마리오가 파이프를 타고 올라감) ──────
        if self.state == 'ug_pipe_enter':
            self.pipe_enter_t += dt
            self.my -= 1.5
            self.fade_alpha = min(255, int(self.pipe_enter_t / 500 * 255))
            if self.pipe_enter_t >= 700:
                # Restore surface state
                self.ug_world   = self.world
                self.ug_pipes   = self.pipes
                self.ug_goombas = self.goombas
                self.world      = self.surface_world
                self.pipes      = self.surface_pipes
                self.goombas    = self.surface_goombas
                self.world_cols = WORLD_COLS
                self.current_map = 'surface'
                self.block_bumps = []
                self.items       = []
                sp = self.pipes[0]   # surface pipe[0] (col 22)
                self.mx       = float(sp.left + (PIPE_W - self.MARIO_W) // 2)
                self.my       = float(sp.top + 8)
                target_cam    = self.mx - WIN_W // 3
                self.cam_x    = max(0.0, min(float(target_cam),
                                             float(WORLD_COLS * TILE - WIN_W)))
                self.state       = 'pipe_exit'
                self.pipe_exit_t = 0
                self.fade_alpha  = 255
            return

        # ── Flagpole slide (폴을 타고 내려감) ───────────────────────────────────
        if self.state == 'flagpole':
            self.flag_t += dt
            if int(self.my) + self._mario_h < FLAG_BOT:
                self.my    += 2.5
                self.mx     = float(FLAG_X - self.MARIO_W + 4)
                self.facing = 1
            if self.flag_t >= 1800:
                self.state = 'win'
            return

        if self.dead:
            self.dead_t -= dt
            self.mvy += GRAVITY * 0.5
            self.my  += self.mvy
            if self.dead_t <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = 'gameover'
                else:
                    self._start_stage(self.current_stage)
                    self.state = 'playing'
            return

        # ── Grow animation timer ─────────────────────────────────────────────
        if self.grow_t > 0:
            self.grow_t = max(0, self.grow_t - dt)

        # ── Underground exit check (↑ key at exit pipe, before jump) ─────────
        if self.current_map == 'underground' and keys[pygame.K_UP] and self.on_ground:
            exit_pipe  = self.pipes[3]
            mario_cx   = int(self.mx) + self.MARIO_W // 2
            mario_feet = int(self.my) + self._mario_h
            if exit_pipe.left < mario_cx < exit_pipe.right and abs(mario_feet - exit_pipe.top) <= 6:
                self.state        = 'ug_pipe_enter'
                self.pipe_enter_t = 0
                self.fade_alpha   = 0
                self.mvx = 0; self.mvy = 0
                return

        # ── Mario movement ────────────────────────────────────────────────────
        self.mvy += GRAVITY
        accel = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            accel = -1; self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            accel = 1;  self.facing = 1

        self.mvx += accel * 1.2
        self.mvx *= 0.82
        self.mvx = max(-WALK_SPD, min(WALK_SPD, self.mvx))

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.mvy = JUMP_VEL
            self.on_ground = False

        mrect = pygame.Rect(int(self.mx), int(self.my), self.MARIO_W, self._mario_h)
        nvx, nvy, on_gnd, ceiling_tiles = self._move(mrect, self.mvx, self.mvy)
        self.mvx = nvx; self.mvy = nvy
        self.mx = float(mrect.x); self.my = float(mrect.y)
        self.on_ground = on_gnd

        # Hit coin blocks from below
        for (c, r) in ceiling_tiles:
            if self.world[r][c] == COIN_BLK:
                self.world[r][c] = USED_BLK
                # Block bump animation
                self.block_bumps.append({'col': c, 'row': r, 'vy': -5.0, 'offset': 0.0})
                # Spawn item: 70% coin, 30% mushroom (or flower if mario_big)
                ix = float(c * TILE + (TILE - ITEM_W) // 2)
                if random.random() < 0.70:
                    self.items.append({
                        'type': 'coin', 'x': ix, 'y': float(r * TILE - ITEM_H),
                        'vy': -10.0, 'alive': True, 'lifetime': 0,
                    })
                else:
                    itype = 'flower' if self.mario_big else 'mushroom'
                    self.items.append({
                        'type': itype,
                        'x': ix, 'y': float(r * TILE),
                        'vx': 1.5, 'vy': 0.0, 'alive': True,
                        'popping': True,
                        'pop_target': float(r * TILE - ITEM_H),
                        'on_ground': False,
                    })

        # Fall into gap
        if self.my > WIN_H + 50:
            self._die()
            return

        # Animation
        if abs(self.mvx) > 0.3 and self.on_ground:
            self.anim_t += dt
            if self.anim_t > 120:
                self.anim_t = 0
                self.anim_frame = (self.anim_frame + 1) % 2
        else:
            self.anim_frame = 0

        # Camera
        target_cam = self.mx - WIN_W // 3
        max_cam = self.world_cols * TILE - WIN_W
        self.cam_x = max(0.0, min(float(target_cam), float(max_cam)))

        # ── Goombas ──────────────────────────────────────────────────────────
        mario_rect = pygame.Rect(int(self.mx), int(self.my), self.MARIO_W, self._mario_h)
        for g in self.goombas:
            if not g['alive']: continue

            if g['stomped']:
                g['stomp_t'] -= dt
                if g['stomp_t'] <= 0: g['alive'] = False
                continue

            g['vy'] += GRAVITY
            g['x']  += g['vx']
            gr = pygame.Rect(int(g['x']), int(g['y']), self.GOOMBA_W, self.GOOMBA_H)

            # Horizontal tile collision
            c1,c2,r1,r2 = self._get_tile_overlaps(gr)
            for row in range(r1,r2+1):
                for col in range(c1,c2+1):
                    if is_solid(tile_at(self.world,col,row)):
                        if g['vx'] > 0: gr.right = col*TILE; g['vx'] *= -1
                        elif g['vx'] < 0: gr.left = (col+1)*TILE; g['vx'] *= -1
            if gr.left <= 0: gr.left = 0; g['vx'] = abs(g['vx'])
            if gr.right >= self.world_cols*TILE: gr.right = self.world_cols*TILE; g['vx'] = -abs(g['vx'])
            for pipe in self.pipes:
                if gr.colliderect(pipe):
                    if g['vx'] > 0: gr.right = pipe.left; g['vx'] = -abs(g['vx'])
                    elif g['vx'] < 0: gr.left = pipe.right; g['vx'] = abs(g['vx'])
            g['x'] = float(gr.x)

            g['y'] += g['vy']
            gr.y = int(g['y'])
            c1,c2,r1,r2 = self._get_tile_overlaps(gr)
            for row in range(r1,r2+1):
                for col in range(c1,c2+1):
                    if is_solid(tile_at(self.world,col,row)):
                        if g['vy'] > 0:
                            gr.bottom = row*TILE; g['vy'] = 0
                        elif g['vy'] < 0:
                            gr.top = (row+1)*TILE; g['vy'] = 0
            for pipe in self.pipes:
                if gr.colliderect(pipe):
                    if g['vy'] >= 0: gr.bottom = pipe.top; g['vy'] = 0
                    else: gr.top = pipe.bottom; g['vy'] = 0
            g['y'] = float(gr.y)

            # Fall out of world
            if g['y'] > WIN_H + 100: g['alive'] = False; continue

            # Animation
            g['frame_t'] += dt
            if g['frame_t'] > 300: g['frame_t'] = 0; g['frame'] = (g['frame']+1)%2

            # Mario-Goomba collision
            if mario_rect.colliderect(gr):
                if self.mvy > 0 and mario_rect.bottom <= gr.centery + 8:
                    g['stomped'] = True; g['stomp_t'] = 400
                    self.mvy = JUMP_VEL * 0.5
                    self.score += 100
                elif self.grow_t <= 0:   # invincible during grow blink
                    self._die()
                    return

        # ── Block bump animations ─────────────────────────────────────────────
        for bump in self.block_bumps[:]:
            bump['offset'] += bump['vy']
            bump['vy']     += 1.0
            if bump['vy'] > 0 and bump['offset'] >= 0:
                bump['offset'] = 0.0
                self.block_bumps.remove(bump)

        # ── Items (coins / mushrooms / fire flowers) ──────────────────────────
        for item in self.items[:]:
            if not item['alive']:
                continue

            if item['type'] == 'coin':
                item['vy']       += 0.7
                item['y']        += item['vy']
                item['lifetime'] += dt
                if item['lifetime'] > 600 or item['y'] > WIN_H + 32:
                    item['alive'] = False
                    self.score   += 100
                    self.coins   += 1
                    continue
                cr = pygame.Rect(int(item['x']), int(item['y']), ITEM_W, ITEM_H)
                if mario_rect.colliderect(cr):
                    item['alive'] = False
                    self.score   += 100
                    self.coins   += 1

            else:  # mushroom or flower
                if item.get('popping'):
                    item['y'] -= 1.5
                    if item['y'] <= item['pop_target']:
                        item['y']       = item['pop_target']
                        item['popping'] = False
                        if item['type'] == 'flower':
                            item['vx'] = 0.0
                    continue  # no physics / collection while popping

                if item['type'] == 'mushroom':
                    # Horizontal movement + wall collision
                    item['x'] += item['vx']
                    ir = pygame.Rect(int(item['x']), int(item['y']), ITEM_W, ITEM_H)
                    c1, c2, r1, r2 = self._get_tile_overlaps(ir)
                    for row in range(r1, r2 + 1):
                        for col in range(c1, c2 + 1):
                            if is_solid(tile_at(self.world, col, row)):
                                if item['vx'] > 0:
                                    ir.right = col * TILE;      item['vx'] = -abs(item['vx'])
                                elif item['vx'] < 0:
                                    ir.left  = (col+1) * TILE;  item['vx'] =  abs(item['vx'])
                    if ir.left  <= 0:                    ir.left  = 0;                        item['vx'] =  abs(item['vx'])
                    if ir.right >= self.world_cols*TILE: ir.right = self.world_cols*TILE; item['vx'] = -abs(item['vx'])
                    for pipe in self.pipes:
                        if ir.colliderect(pipe):
                            if item['vx'] > 0: ir.right = pipe.left; item['vx'] = -abs(item['vx'])
                            elif item['vx'] < 0: ir.left = pipe.right; item['vx'] = abs(item['vx'])
                    item['x'] = float(ir.x)
                    # Gravity + vertical collision
                    item['vy'] += GRAVITY
                    item['y']  += item['vy']
                    ir.y = int(item['y'])
                    c1, c2, r1, r2 = self._get_tile_overlaps(ir)
                    for row in range(r1, r2 + 1):
                        for col in range(c1, c2 + 1):
                            if is_solid(tile_at(self.world, col, row)):
                                if item['vy'] >= 0:
                                    ir.bottom = row * TILE;     item['vy'] = 0
                                else:
                                    ir.top    = (row+1) * TILE; item['vy'] = 0
                    for pipe in self.pipes:
                        if ir.colliderect(pipe):
                            if item['vy'] >= 0: ir.bottom = pipe.top; item['vy'] = 0
                            else: ir.top = pipe.bottom; item['vy'] = 0
                    item['y'] = float(ir.y)
                    if item['y'] > WIN_H + 64:
                        item['alive'] = False
                        continue

                # Collect on touch
                ir = pygame.Rect(int(item['x']), int(item['y']), ITEM_W, ITEM_H)
                if mario_rect.colliderect(ir):
                    item['alive'] = False
                    if item['type'] == 'mushroom':
                        self.score += 500
                        if not self.mario_big:
                            # Shift mario up so feet stay on the ground
                            self.my    -= (MARIO_H_BIG - MARIO_H_SMALL)
                            self.mario_big = True
                            self.grow_t    = 500
                    elif item['type'] == 'flower':
                        self.score += 200
                        if not self.mario_big:
                            self.my    -= (MARIO_H_BIG - MARIO_H_SMALL)
                            self.grow_t = 500
                        self.mario_fire = True
                        self.mario_big  = True

        # ── Pipe entry check (↓ 키, 지상에서만 첫 번째 파이프 입장) ────────────
        if self.current_map == 'surface' and keys[pygame.K_DOWN] and self.on_ground:
            pipe0      = self.pipes[0]
            mario_cx   = int(self.mx) + self.MARIO_W // 2
            mario_feet = int(self.my) + self._mario_h
            if pipe0.left < mario_cx < pipe0.right and abs(mario_feet - pipe0.top) <= 6:
                self.state        = 'pipe_enter'
                self.pipe_enter_t = 0
                self.fade_alpha   = 0
                self.mvx = 0; self.mvy = 0

        # ── Flagpole collision (지상에서만) ───────────────────────────────────
        if self.current_map == 'surface':
            pole_rect = pygame.Rect(FLAG_X, FLAG_TOP, 8, FLAG_BOT - FLAG_TOP)
            if mario_rect.colliderect(pole_rect):
                self.state  = 'flagpole'
                self.flag_t = 0
                self.score += 500
                self.mvx = 0; self.mvy = 0

    def _die(self):
        self.dead      = True
        self.dead_t    = 1500
        self.mvy       = JUMP_VEL * 0.8
        self.mvx       = 0
        self.mario_big  = False
        self.mario_fire = False

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self):
        if self.state == 'worldmap':
            self._draw_worldmap()
            pygame.display.flip()
            return

        underground = self.current_map == 'underground'
        self.screen.fill(BLACK if underground else SKY)
        if not underground:
            draw_clouds(self.screen, self.clouds, self.cam_x)

        # Tiles (with bump offset)
        c_start = max(0, int(self.cam_x // TILE) - 1)
        c_end   = min(self.world_cols, c_start + (WIN_W // TILE) + 3)
        bump_offsets = {(b['col'], b['row']): int(b['offset']) for b in self.block_bumps}
        for r in range(WORLD_ROWS):
            for c in range(c_start, c_end):
                t = self.world[r][c]
                if t != EMPTY:
                    py = r * TILE + bump_offsets.get((c, r), 0)
                    draw_tile(self.screen, t, c*TILE - int(self.cam_x), py, underground)

        # Pipes
        for pipe in self.pipes:
            px = pipe.x - int(self.cam_x)
            if -PIPE_W < px < WIN_W + PIPE_W:
                draw_pipe(self.screen, px, pipe.y)

        # Flagpole (지상에서만)
        if not underground:
            draw_flagpole(self.screen, self.cam_x)

        # Items (spawned coins / mushrooms / flowers)
        for item in self.items:
            if not item['alive']:
                continue
            ix = item['x'] - self.cam_x
            if -TILE * 2 < ix < WIN_W + TILE * 2:
                if item['type'] == 'coin':
                    draw_coin(self.screen, ix, item['y'], math.pi / 2)
                elif item['type'] == 'mushroom':
                    draw_mushroom(self.screen, ix, item['y'])
                elif item['type'] == 'flower':
                    draw_flower(self.screen, ix, item['y'])

        # Goombas
        for g in self.goombas:
            if not g['alive']: continue
            gx = g['x'] - self.cam_x
            if -TILE*2 < gx < WIN_W + TILE*2:
                draw_goomba(self.screen, gx, g['y'], g['frame'], g['stomped'])

        # Mario — blink between small/big during grow_t window
        mx_screen = self.mx - self.cam_x
        if self.grow_t > 0:
            show_big = (self.grow_t // 80) % 2 == 0
        else:
            show_big = self.mario_big
        draw_mario(self.screen, mx_screen, self.my, self.facing, self.anim_frame,
                   self.dead, big=show_big)

        # HUD
        self._draw_hud()

        # Overlays
        if self.state == 'title':      self._draw_title()
        elif self.state == 'gameover': self._draw_gameover()
        elif self.state == 'win':      self._draw_win()

        # Pipe transition fade
        if self.fade_alpha > 0:
            fs = pygame.Surface((WIN_W, WIN_H))
            fs.fill(BLACK)
            fs.set_alpha(self.fade_alpha)
            self.screen.blit(fs, (0, 0))

        pygame.display.flip()

    def _draw_hud(self):
        _fonts()
        hud_items = [
            (f'SCORE  {self.score:06d}', 12),
            (f'COINS  x{self.coins:02d}',  220),
            (f'LIVES  x{self.lives}',      420),
        ]
        for text, x in hud_items:
            s = _fhud.render(text, True, WHITE)
            self.screen.blit(s, (x, 6))

    def _overlay(self, alpha=160):
        s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        s.fill((0,0,0,alpha))
        self.screen.blit(s,(0,0))

    def _draw_title(self):
        self._overlay()
        fn = pygame.font.SysFont('consolas', 52, bold=True)
        fm = pygame.font.SysFont('consolas', 22, bold=True)
        fs = pygame.font.SysFont('consolas', 14)
        t = fn.render('SUPER MARIO', True, RED)
        self.screen.blit(t,(WIN_W//2-t.get_width()//2, WIN_H//2-100))
        s = fm.render('[ ENTER ] 게임 시작', True, WHITE)
        self.screen.blit(s,(WIN_W//2-s.get_width()//2, WIN_H//2-20))
        c = fs.render('← → A D  이동  |  ↑ W Space  점프', True, (180,180,180))
        self.screen.blit(c,(WIN_W//2-c.get_width()//2, WIN_H//2+30))

    def _draw_gameover(self):
        self._overlay()
        fn = pygame.font.SysFont('consolas', 48, bold=True)
        fm = pygame.font.SysFont('consolas', 20, bold=True)
        fs = pygame.font.SysFont('consolas', 14)
        t = fn.render('GAME OVER', True, RED)
        self.screen.blit(t,(WIN_W//2-t.get_width()//2, WIN_H//2-90))
        sc = fm.render(f'최종 점수: {self.score}', True, COIN_C)
        self.screen.blit(sc,(WIN_W//2-sc.get_width()//2, WIN_H//2-20))
        r = fs.render('[ R ] 재시작   [ ESC ] 메인메뉴', True, (180,180,180))
        self.screen.blit(r,(WIN_W//2-r.get_width()//2, WIN_H//2+30))

    def _draw_win(self):
        self._overlay(120)
        fn = pygame.font.SysFont('consolas', 48, bold=True)
        fm = pygame.font.SysFont('consolas', 20, bold=True)
        fs = pygame.font.SysFont('consolas', 14)
        t = fn.render('STAGE CLEAR!', True, COIN_C)
        self.screen.blit(t,(WIN_W//2-t.get_width()//2, WIN_H//2-90))
        sc = fm.render(f'점수: {self.score}  코인: {self.coins}', True, WHITE)
        self.screen.blit(sc,(WIN_W//2-sc.get_width()//2, WIN_H//2-20))
        r = fs.render('[ R ] 월드맵으로   [ ESC ] 종료', True, (180,180,180))
        self.screen.blit(r,(WIN_W//2-r.get_width()//2, WIN_H//2+30))

    # ── World Map ────────────────────────────────────────────────────────────
    def _draw_worldmap(self):
        _fonts()
        # Checkerboard grass background
        for row in range(WIN_H // 40 + 1):
            for col in range(WIN_W // 40 + 1):
                shade = (38, 155, 38) if (col + row) % 2 == 0 else (50, 170, 50)
                pygame.draw.rect(self.screen, shade, (col * 40, row * 40, 40, 40))
        pygame.draw.rect(self.screen, (20, 100, 20), (0, 0, WIN_W, WIN_H), 5)

        # Title
        fn = pygame.font.SysFont('consolas', 36, bold=True)
        fm = pygame.font.SysFont('consolas', 16, bold=True)
        fs = pygame.font.SysFont('consolas', 14)

        shadow = fn.render('WORLD  1', True, (80, 50, 0))
        title  = fn.render('WORLD  1', True, COIN_C)
        tx = WIN_W // 2 - title.get_width() // 2
        self.screen.blit(shadow, (tx + 2, 32))
        self.screen.blit(title,  (tx,     30))

        # Stage layout
        stage_names = ['1-1', '1-2', '1-3']
        stage_x     = [160,   400,   640  ]
        stage_y     = 260
        node_r      = 32

        # Connecting dashed paths
        for i in range(2):
            x1 = stage_x[i] + node_r
            x2 = stage_x[i + 1] - node_r
            path_color = WHITE if self.cleared_stages[i] else (80, 110, 80)
            dash, gap, x = 12, 7, x1
            while x < x2:
                ex = min(x + dash, x2)
                pygame.draw.line(self.screen, path_color, (x, stage_y), (ex, stage_y), 4)
                x += dash + gap

        # Stage nodes
        for i, (name, sx) in enumerate(zip(stage_names, stage_x)):
            accessible = (i == 0) or self.cleared_stages[i - 1]
            cleared    = self.cleared_stages[i]
            selected   = self.worldmap_cursor == i

            # Drop shadow
            pygame.draw.circle(self.screen, (0, 60, 0), (sx + 3, stage_y + 3), node_r)

            # Selection ring
            if selected:
                pygame.draw.circle(self.screen, WHITE, (sx, stage_y), node_r + 7, 3)

            # Fill colour
            if cleared:
                fill   = (255, 200, 50)
                border = (200, 140, 0)
            elif accessible:
                fill   = (230, 230, 230)
                border = (160, 160, 160)
            else:
                fill   = (70, 70, 70)
                border = (50, 50, 50)

            pygame.draw.circle(self.screen, fill,   (sx, stage_y), node_r)
            pygame.draw.circle(self.screen, border, (sx, stage_y), node_r, 2)

            # Content inside node
            if not accessible:
                ql = pygame.font.SysFont('consolas', 24, bold=True)
                q  = ql.render('?', True, (150, 150, 150))
                self.screen.blit(q, (sx - q.get_width() // 2, stage_y - q.get_height() // 2))
            else:
                nt = fm.render(name, True, BLACK)
                self.screen.blit(nt, (sx - nt.get_width() // 2, stage_y - nt.get_height() // 2))

            # Star above cleared node
            if cleared:
                sf  = pygame.font.SysFont('consolas', 26, bold=True)
                star = sf.render('★', True, COIN_C)
                self.screen.blit(star, (sx - star.get_width() // 2, stage_y - node_r - 38))

            # Mario icon above selected node
            if selected:
                draw_mario(self.screen,
                           sx - 14, stage_y - node_r - 56,
                           1, self._wm_anim_frame)

        # HUD strip
        hud = fm.render(f'SCORE {self.score:06d}   LIVES x{self.lives}   COINS x{self.coins:02d}',
                        True, WHITE)
        pygame.draw.rect(self.screen, (0, 80, 0), (0, WIN_H - 56, WIN_W, 56))
        pygame.draw.line(self.screen, (0, 120, 0), (0, WIN_H - 56), (WIN_W, WIN_H - 56), 2)
        self.screen.blit(hud, (WIN_W // 2 - hud.get_width() // 2, WIN_H - 46))

        hint = fs.render('← → 스테이지 선택   Enter 진입   ESC 종료', True, (200, 200, 200))
        self.screen.blit(hint, (WIN_W // 2 - hint.get_width() // 2, WIN_H - 22))

    # ── Event ─────────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.QUIT: return False
        if event.type == pygame.KEYDOWN:
            if self.state == 'title':
                if event.key == pygame.K_ESCAPE: return False
                if event.key == pygame.K_RETURN:
                    self.reset()
                    self.state = 'worldmap'
            elif self.state == 'worldmap':
                if event.key == pygame.K_ESCAPE: return False
                elif event.key == pygame.K_LEFT:
                    self.worldmap_cursor = max(0, self.worldmap_cursor - 1)
                elif event.key == pygame.K_RIGHT:
                    self.worldmap_cursor = min(2, self.worldmap_cursor + 1)
                elif event.key == pygame.K_RETURN:
                    i = self.worldmap_cursor
                    accessible = (i == 0) or self.cleared_stages[i - 1]
                    if accessible:
                        self._start_stage(i)
                        self.state = 'playing'
            elif self.state == 'win':
                if event.key == pygame.K_ESCAPE: return False
                if event.key == pygame.K_r:
                    self.cleared_stages[self.current_stage] = True
                    self.worldmap_cursor = min(self.current_stage + 1, 2)
                    self.state = 'worldmap'
            elif self.state == 'gameover':
                if event.key == pygame.K_ESCAPE: return False
                if event.key == pygame.K_r:
                    self.reset()
                    self.state = 'worldmap'
            else:
                if event.key == pygame.K_ESCAPE: return False
        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
            if self.state == 'worldmap':
                self._wm_anim_t += dt
                if self._wm_anim_t > 300:
                    self._wm_anim_t = 0
                    self._wm_anim_frame = (self._wm_anim_frame + 1) % 2
            if self.state in ('playing', 'pipe_enter', 'pipe_exit', 'flagpole', 'ug_pipe_enter'):
                keys = pygame.key.get_pressed()
                self.update(dt, keys)
            self.draw()
        pygame.quit()


def main():
    MarioGame().run()

if __name__ == '__main__':
    main()
