import pygame
import sys
import os
import subprocess

pygame.init()

WIN_W, WIN_H = 600, 400
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption('게임 선택')
clock = pygame.time.Clock()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

# ── Colours ──────────────────────────────────────────────────────────────────
BG       = (8,   8,  24)
PANEL    = (16,  16, 40)
BORDER   = (30,  30, 70)
WHITE    = (220,220,220)
GRAY     = (120,120,150)
CYAN     = (0,  229,255)
RED      = (220, 50, 50)
CYAN_D   = (0,  160,200)
RED_D    = (160, 30, 30)

# ── Fonts ─────────────────────────────────────────────────────────────────────
f_title = pygame.font.SysFont('consolas', 38, bold=True)
f_sub   = pygame.font.SysFont('consolas', 13)
f_btn   = pygame.font.SysFont('consolas', 24, bold=True)
f_hint  = pygame.font.SysFont('consolas', 12)

# ── Button definitions ────────────────────────────────────────────────────────
BTN_W, BTN_H = 220, 90
GAP = 40
btn_y = WIN_H // 2 - BTN_H // 2 + 30

BUTTONS = [
    {
        'label'  : 'TETRIS',
        'sub'    : '블록 쌓기 퍼즐',
        'script' : 'tetris.py',
        'color'  : CYAN,
        'dark'   : CYAN_D,
        'rect'   : pygame.Rect(WIN_W//2 - BTN_W - GAP//2, btn_y, BTN_W, BTN_H),
    },
    {
        'label'  : 'MARIO',
        'sub'    : '사이드 스크롤 액션',
        'script' : 'mario.py',
        'color'  : RED,
        'dark'   : RED_D,
        'rect'   : pygame.Rect(WIN_W//2 + GAP//2,           btn_y, BTN_W, BTN_H),
    },
]

def draw_button(btn, hovered):
    r = btn['rect']
    c = btn['color']
    d = btn['dark']

    # Shadow / glow
    glow = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
    alpha = 80 if hovered else 30
    glow.fill((*c, alpha))
    screen.blit(glow, (r.x - 10, r.y - 10))

    # Body
    bg_col = (c[0]//6, c[1]//6, c[2]//6)
    pygame.draw.rect(screen, bg_col, r, border_radius=10)

    # Border
    border_col = c if hovered else d
    pygame.draw.rect(screen, border_col, r, 2, border_radius=10)

    # Top highlight
    hl = pygame.Surface((r.w - 4, 3), pygame.SRCALPHA)
    hl.fill((*c, 120))
    screen.blit(hl, (r.x+2, r.y+2))

    # Label
    lbl = f_btn.render(btn['label'], True, c)
    screen.blit(lbl, (r.centerx - lbl.get_width()//2, r.y + 20))

    # Sub label
    sub = f_hint.render(btn['sub'], True, GRAY)
    screen.blit(sub, (r.centerx - sub.get_width()//2, r.y + 58))

def draw_bg():
    screen.fill(BG)

    # Subtle grid
    for x in range(0, WIN_W, 40):
        pygame.draw.line(screen, (18,18,40), (x,0),(x,WIN_H))
    for y in range(0, WIN_H, 40):
        pygame.draw.line(screen, (18,18,40), (0,y),(WIN_W,y))

    # Title
    t = f_title.render('GAME SELECT', True, WHITE)
    screen.blit(t, (WIN_W//2 - t.get_width()//2, 60))

    # Underline
    pygame.draw.line(screen, CYAN, (WIN_W//2 - 120, 106),(WIN_W//2 + 120, 106), 2)

    # Hint
    h = f_sub.render('클릭하거나 [ 1 ] / [ 2 ] 키로 선택', True, GRAY)
    screen.blit(h, (WIN_W//2 - h.get_width()//2, 340))

    esc = f_sub.render('[ ESC ] 종료', True, (70,70,90))
    screen.blit(esc, (WIN_W//2 - esc.get_width()//2, 365))

def launch(script):
    pygame.quit()
    subprocess.run([PYTHON, os.path.join(SCRIPT_DIR, script)])
    # Re-init after game closes
    pygame.init()
    global screen, clock, f_title, f_sub, f_btn, f_hint
    screen  = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption('게임 선택')
    clock   = pygame.time.Clock()
    f_title = pygame.font.SysFont('consolas', 38, bold=True)
    f_sub   = pygame.font.SysFont('consolas', 13)
    f_btn   = pygame.font.SysFont('consolas', 24, bold=True)
    f_hint  = pygame.font.SysFont('consolas', 12)

def main():
    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    launch('tetris.py')
                elif event.key == pygame.K_2:
                    launch('mario.py')
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in BUTTONS:
                    if btn['rect'].collidepoint(event.pos):
                        launch(btn['script'])

        draw_bg()
        for btn in BUTTONS:
            hovered = btn['rect'].collidepoint(mx, my)
            draw_button(btn, hovered)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
