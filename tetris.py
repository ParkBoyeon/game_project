import pygame
import random
import json
import os
import sys

pygame.init()

# ── 상수 ──────────────────────────────────────────────────────────────────────
COLS, ROWS = 10, 20
CELL = 30
BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL
SIDE_W = 180
WIN_W = BOARD_W + SIDE_W
WIN_H = BOARD_H
FPS = 60

BLACK   = (8, 8, 24)
DARK    = (16, 16, 40)
GRID    = (26, 26, 60)
WHITE   = (220, 220, 220)
GRAY    = (80, 80, 100)

COLORS = {
    'I': (0,   229, 255),
    'O': (255, 234,   0),
    'T': (224,  64, 251),
    'S': (105, 240, 174),
    'Z': (255,  82,  82),
    'J': (68,  138, 255),
    'L': (255, 145,   0),
}

PIECES = {
    'I': [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    'O': [[1,1],[1,1]],
    'T': [[0,1,0],[1,1,1],[0,0,0]],
    'S': [[0,1,1],[1,1,0],[0,0,0]],
    'Z': [[1,1,0],[0,1,1],[0,0,0]],
    'J': [[1,0,0],[1,1,1],[0,0,0]],
    'L': [[0,0,1],[1,1,1],[0,0,0]],
}

SCORE_TABLE = [0, 100, 300, 500, 800]
BEST_FILE = os.path.join(os.path.dirname(__file__), '.tetris_best')

# ── 유틸 ──────────────────────────────────────────────────────────────────────
def load_best():
    try:
        with open(BEST_FILE) as f:
            return int(f.read())
    except Exception:
        return 0

def save_best(v):
    try:
        with open(BEST_FILE, 'w') as f:
            f.write(str(v))
    except Exception:
        pass

def rotate(mat):
    return [list(row) for row in zip(*mat[::-1])]

def new_board():
    return [[None] * COLS for _ in range(ROWS)]

def rand_piece():
    key = random.choice(list(PIECES.keys()))
    return {'type': key, 'mat': [row[:] for row in PIECES[key]], 'x': 3, 'y': 0}

def draw_glow(surf, color, rect, radius=6):
    glow = pygame.Surface((rect.width + radius*2, rect.height + radius*2), pygame.SRCALPHA)
    dim = tuple(max(0, min(255, int(c * 0.5))) for c in color)
    pygame.draw.rect(glow, (*dim, 80), glow.get_rect(), border_radius=radius)
    surf.blit(glow, (rect.x - radius, rect.y - radius))

def draw_cell(surf, gx, gy, color, alpha=255, cell_size=CELL, offset_x=0, offset_y=0):
    x = offset_x + gx * cell_size + 1
    y = offset_y + gy * cell_size + 1
    w = h = cell_size - 2
    if alpha < 255:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((*color, alpha))
        surf.blit(s, (x, y))
        return
    pygame.draw.rect(surf, color, (x, y, w, h))
    # 하이라이트 (상단)
    light = tuple(min(255, c + 80) for c in color)
    pygame.draw.rect(surf, light, (x, y, w, 4))
    # 그림자 (하단)
    dark = tuple(max(0, c - 60) for c in color)
    pygame.draw.rect(surf, dark, (x, y + h - 4, w, 4))
    # 테두리 글로우
    bright = tuple(min(255, c + 40) for c in color)
    pygame.draw.rect(surf, bright, (x, y, w, h), 1)

# ── 게임 클래스 ───────────────────────────────────────────────────────────────
class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption('테트리스')
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont('consolas', 28, bold=True)
        self.font_md = pygame.font.SysFont('consolas', 18, bold=True)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.best = load_best()
        self.state = 'title'  # title | playing | paused | gameover
        self.reset()

    def reset(self):
        self.board = new_board()
        self.score = 0
        self.level = 1
        self.lines = 0
        self.drop_interval = 1000
        self.accumulated = 0
        self.next = rand_piece()
        self.spawn()
        self.das_dir = 0       # delayed auto-shift direction
        self.das_timer = 0
        self.arr_timer = 0

    def spawn(self):
        self.cur = self.next
        self.cur['x'] = (COLS - len(self.cur['mat'][0])) // 2
        self.cur['y'] = 0
        self.next = rand_piece()
        if not self.valid(self.cur):
            self.state = 'gameover'
            if self.score > self.best:
                self.best = self.score
                save_best(self.best)

    def valid(self, piece, dx=0, dy=0, mat=None):
        m = mat or piece['mat']
        for r, row in enumerate(m):
            for c, v in enumerate(row):
                if not v:
                    continue
                nx = piece['x'] + c + dx
                ny = piece['y'] + r + dy
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and self.board[ny][nx]:
                    return False
        return True

    def ghost_y(self):
        dy = 0
        while self.valid(self.cur, 0, dy + 1):
            dy += 1
        return self.cur['y'] + dy

    def try_rotate(self):
        rot = rotate(self.cur['mat'])
        for kick in [0, 1, -1, 2, -2]:
            if self.valid(self.cur, kick, 0, rot):
                self.cur['mat'] = rot
                self.cur['x'] += kick
                return

    def lock(self):
        for r, row in enumerate(self.cur['mat']):
            for c, v in enumerate(row):
                if v:
                    ny = self.cur['y'] + r
                    if ny < 0:
                        self.state = 'gameover'
                        return
                    self.board[ny][self.cur['x'] + c] = self.cur['type']
        self.clear_lines()
        self.spawn()

    def clear_lines(self):
        cleared = 0
        r = ROWS - 1
        while r >= 0:
            if all(self.board[r]):
                del self.board[r]
                self.board.insert(0, [None] * COLS)
                cleared += 1
            else:
                r -= 1
        if cleared:
            self.lines += cleared
            self.score += SCORE_TABLE[cleared] * self.level
            self.level = self.lines // 10 + 1
            self.drop_interval = max(80, 1000 - (self.level - 1) * 90)
            if self.score > self.best:
                self.best = self.score
                save_best(self.best)

    def hard_drop(self):
        while self.valid(self.cur, 0, 1):
            self.cur['y'] += 1
            self.score += 1
        self.lock()
        self.accumulated = 0

    # ── 업데이트 ───────────────────────────────────────────────────────────────
    def update(self, dt):
        if self.state != 'playing':
            return

        self.accumulated += dt
        if self.accumulated >= self.drop_interval:
            if self.valid(self.cur, 0, 1):
                self.cur['y'] += 1
            else:
                self.lock()
            self.accumulated = 0

        # DAS (Delayed Auto Shift)
        DAS = 170
        ARR = 50
        if self.das_dir:
            self.das_timer += dt
            if self.das_timer >= DAS:
                self.arr_timer += dt
                while self.arr_timer >= ARR:
                    if self.valid(self.cur, self.das_dir, 0):
                        self.cur['x'] += self.das_dir
                    self.arr_timer -= ARR

    # ── 렌더링 ────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_board()
        self.draw_side()
        if self.state == 'title':
            self.draw_title()
        elif self.state == 'paused':
            self.draw_overlay('PAUSED', '[ P ] 계속하기')
        elif self.state == 'gameover':
            self.draw_gameover()
        pygame.display.flip()

    def draw_board(self):
        # 배경
        pygame.draw.rect(self.screen, DARK, (0, 0, BOARD_W, BOARD_H))
        # 그리드
        for r in range(ROWS):
            for c in range(COLS):
                pygame.draw.rect(self.screen, GRID, (c*CELL, r*CELL, CELL, CELL), 1)

        # 고정 블록
        for r in range(ROWS):
            for c in range(COLS):
                t = self.board[r][c]
                if t:
                    draw_cell(self.screen, c, r, COLORS[t])

        if self.state in ('playing', 'paused'):
            # 고스트
            gy = self.ghost_y()
            if gy != self.cur['y']:
                for r, row in enumerate(self.cur['mat']):
                    for c, v in enumerate(row):
                        if v:
                            draw_cell(self.screen, self.cur['x']+c, gy+r,
                                      COLORS[self.cur['type']], 50)

            # 현재 블록
            for r, row in enumerate(self.cur['mat']):
                for c, v in enumerate(row):
                    if v:
                        draw_cell(self.screen, self.cur['x']+c, self.cur['y']+r,
                                  COLORS[self.cur['type']])

        # 테두리
        pygame.draw.rect(self.screen, (0, 150, 200), (0, 0, BOARD_W, BOARD_H), 2)

    def draw_side(self):
        sx = BOARD_W + 10
        w = SIDE_W - 20

        def box(y, h):
            pygame.draw.rect(self.screen, DARK, (sx, y, w, h), border_radius=6)
            pygame.draw.rect(self.screen, GRID, (sx, y, w, h), 1, border_radius=6)

        def label(text, y):
            s = self.font_sm.render(text, True, GRAY)
            self.screen.blit(s, (sx + 8, y))

        def value(text, y, color=(0, 229, 255)):
            s = self.font_lg.render(text, True, color)
            self.screen.blit(s, (sx + 8, y))

        # 점수
        box(10, 65)
        label('SCORE', 14)
        value(str(self.score), 28)

        # 최고 점수
        box(85, 65)
        label('BEST', 89)
        value(str(self.best), 103, (180, 80, 255))

        # 레벨
        box(160, 50)
        label('LEVEL', 164)
        value(str(self.level), 176, (105, 240, 174))

        # 줄 수
        box(220, 50)
        label('LINES', 224)
        value(str(self.lines), 236, (255, 145, 0))

        # 다음 블록
        box(280, 110)
        label('NEXT', 284)
        self.draw_next(sx, 298, w)

        # 조작 안내
        box(400, 185)
        label('CONTROLS', 404)
        controls = [
            ('← →', '이동'),
            ('↑ / Z', '회전'),
            ('↓', '소프트 드롭'),
            ('SPACE', '하드 드롭'),
            ('P', '일시정지'),
            ('R', '재시작'),
        ]
        for i, (k, v) in enumerate(controls):
            ks = self.font_sm.render(k, True, (120, 120, 255))
            vs = self.font_sm.render(v, True, GRAY)
            self.screen.blit(ks, (sx + 8, 418 + i * 27))
            self.screen.blit(vs, (sx + 60, 418 + i * 27))

    def draw_next(self, sx, sy, w):
        if not self.next:
            return
        m = self.next['mat']
        cs = 24
        cols = len(m[0])
        rows = len(m)
        ox = sx + (w - cols * cs) // 2
        oy = sy + (80 - rows * cs) // 2 + 8
        color = COLORS[self.next['type']]
        for r, row in enumerate(m):
            for c, v in enumerate(row):
                if v:
                    x = ox + c * cs + 1
                    y = oy + r * cs + 1
                    s = cs - 2
                    pygame.draw.rect(self.screen, color, (x, y, s, s))
                    pygame.draw.rect(self.screen, tuple(min(255,c+60) for c in color), (x,y,s,s), 1)

    def draw_overlay(self, title, sub):
        surf = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        self.screen.blit(surf, (0, 0))
        t = self.font_lg.render(title, True, (0, 229, 255))
        self.screen.blit(t, (WIN_W//2 - t.get_width()//2, WIN_H//2 - 30))
        s = self.font_sm.render(sub, True, GRAY)
        self.screen.blit(s, (WIN_W//2 - s.get_width()//2, WIN_H//2 + 10))

    def draw_title(self):
        surf = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 200))
        self.screen.blit(surf, (0, 0))

        title = self.font_lg.render('T E T R I S', True, (0, 229, 255))
        self.screen.blit(title, (WIN_W//2 - title.get_width()//2, WIN_H//2 - 80))

        sub = self.font_md.render('[ ENTER ] 게임 시작', True, (180, 180, 200))
        self.screen.blit(sub, (WIN_W//2 - sub.get_width()//2, WIN_H//2 - 20))

        hint = self.font_sm.render('네온 레트로 테트리스', True, GRAY)
        self.screen.blit(hint, (WIN_W//2 - hint.get_width()//2, WIN_H//2 + 20))

    def draw_gameover(self):
        surf = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 180))
        self.screen.blit(surf, (0, 0))

        t = self.font_lg.render('GAME OVER', True, (255, 82, 82))
        self.screen.blit(t, (WIN_W//2 - t.get_width()//2, WIN_H//2 - 80))

        sc = self.font_md.render(f'점수: {self.score}', True, (0, 229, 255))
        self.screen.blit(sc, (WIN_W//2 - sc.get_width()//2, WIN_H//2 - 30))

        bt = self.font_md.render(f'최고: {self.best}', True, (180, 80, 255))
        self.screen.blit(bt, (WIN_W//2 - bt.get_width()//2, WIN_H//2 + 5))

        r = self.font_sm.render('[ R ] 재시작   [ ESC ] 종료', True, GRAY)
        self.screen.blit(r, (WIN_W//2 - r.get_width()//2, WIN_H//2 + 50))

    # ── 이벤트 ────────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

            if self.state == 'title':
                if event.key == pygame.K_RETURN:
                    self.state = 'playing'
                return True

            if self.state == 'gameover':
                if event.key == pygame.K_r:
                    self.reset()
                    self.state = 'playing'
                return True

            if event.key == pygame.K_p:
                if self.state == 'playing':
                    self.state = 'paused'
                elif self.state == 'paused':
                    self.state = 'playing'

            if event.key == pygame.K_r:
                self.reset()
                self.state = 'playing'

            if self.state != 'playing':
                return True

            if event.key == pygame.K_LEFT:
                if self.valid(self.cur, -1, 0):
                    self.cur['x'] -= 1
                self.das_dir = -1
                self.das_timer = 0
                self.arr_timer = 0
            elif event.key == pygame.K_RIGHT:
                if self.valid(self.cur, 1, 0):
                    self.cur['x'] += 1
                self.das_dir = 1
                self.das_timer = 0
                self.arr_timer = 0
            elif event.key == pygame.K_DOWN:
                if self.valid(self.cur, 0, 1):
                    self.cur['y'] += 1
                    self.accumulated = 0
                    self.score += 1
            elif event.key in (pygame.K_UP, pygame.K_z):
                self.try_rotate()
            elif event.key == pygame.K_SPACE:
                self.hard_drop()

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.das_dir = 0
                self.das_timer = 0
                self.arr_timer = 0

        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
            self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == '__main__':
    Tetris().run()
