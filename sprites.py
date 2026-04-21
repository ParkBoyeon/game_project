"""
mario/sprites.py — NES 스타일 픽셀 아트 스프라이트
각 스프라이트는 문자열 리스트(1문자 = NES 1픽셀)로 정의.
SCALE=2: 16×16 NES 타일 → 32×32 화면 픽셀 (TILE_SIZE와 일치)
"""
import pygame

SCALE = 2  # NES 1픽셀 = 화면 SCALE×SCALE 픽셀

_PAL = {
    '.': None,
    'D': (140,  44,   0),   # 모르타르 (어두운)
    'B': (200,  88,   0),   # 벽돌 오렌지
    'Q': (224, 156,   0),   # ? 블록 금색
    'q': (252, 200,  60),   # ? 블록 밝은 금색
    'b': (148,  68,   0),   # ? 블록 테두리
    'e': (120,  72,  16),   # used 블록 채움
    'n': (  0, 168,   0),   # 풀 녹색
    'N': (  0, 110,   0),   # 풀 어두운
    'w': (252, 252, 252),   # 흰색
    'R': (200,   0,   0),   # 마리오 빨강
    'K': (252, 188, 116),   # 마리오 피부
    'O': ( 80,  40,   0),   # 눈/콧수염 어두운
    'U': ( 24,  24, 252),   # 마리오 파랑 오버롤
    'W': (100,  60,   0),   # 마리오 갈색 신발
    'G': (172, 104,  28),   # 굼바 몸통
    'g': ( 88,  40,   0),   # 굼바 어두운
    'f': ( 60,  30,   0),   # 굼바 발
    'p': ( 20,  10,   0),   # 굼바 눈 윤곽 (거의 검정)
    'M': (220,   0,   0),   # 버섯 빨간 캡
    'H': (252, 220, 180),   # 버섯 줄기
}

_cache: dict = {}


def _build(rows: list[str], scale: int = SCALE) -> pygame.Surface:
    h, w = len(rows), len(rows[0])
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            color = _PAL.get(ch)
            if color is not None:
                pygame.draw.rect(surf, color,
                                 (c * scale, r * scale, scale, scale))
    return surf


def get(name: str, flip_h: bool = False) -> pygame.Surface:
    """스프라이트 Surface 반환. flip_h=True이면 좌우 반전 (왼쪽 방향)."""
    key = (name, flip_h)
    if key not in _cache:
        surf = _build(_DATA[name])
        if flip_h:
            surf = pygame.transform.flip(surf, True, False)
        _cache[key] = surf
    return _cache[key]


# ── 스프라이트 픽셀 데이터 ────────────────────────────────────────────────────
_DATA: dict[str, list[str]] = {

    # ── 벽돌 타일 (16×16 → 32×32) ────────────────────────────────────────────
    'brick': [
        "DDDDDDDDDDDDDDDD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DDDDDDDDDDDDDDDD",
        "BBDDBBBBBBBDDBBB",
        "BBDDBBBBBBBDDBBB",
        "BBDDBBBBBBBDDBBB",
        "DDDDDDDDDDDDDDDD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DDDDDDDDDDDDDDDD",
        "BBDDBBBBBBBDDBBB",
        "BBDDBBBBBBBDDBBB",
        "BBDDBBBBBBBDDBBB",
    ],

    # ── 지면 타일 (16×16 → 32×32) 상단 2줄 풀 ───────────────────────────────
    'ground': [
        "nnnnnnnnnnnnnnnn",
        "nNnnNnnnNnnnNnnn",
        "DDDDDDDDDDDDDDDD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DDDDDDDDDDDDDDDD",
        "BBDDBBBBBBBDDBBB",
        "BBDDBBBBBBBDDBBB",
        "BBDDBBBBBBBDDBBB",
        "DDDDDDDDDDDDDDDD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DBBBBBBDDBBBBBBD",
        "DDDDDDDDDDDDDDDD",
        "BBDDBBBBBBBDDBBB",
    ],

    # ── ? 블록 (16×16 → 32×32) ───────────────────────────────────────────────
    'qblock': [
        "bbbbbbbbbbbbbbbb",
        "bQQQQQQQQQQQQQQb",
        "bQQQQQQQQQQQQQQb",
        "bQQQQwwwQQQQQQQb",
        "bQQQwQQQwQQQQQQb",
        "bQQQQQQwQQQQQQQb",
        "bQQQQQwQQQQQQQQb",
        "bQQQQwQQQQQQQQQb",
        "bQQQQwQQQQQQQQQb",
        "bQQQQQQQQQQQQQQb",
        "bQQQQwwQQQQQQQQb",
        "bQQQQwwQQQQQQQQb",
        "bQQQQQQQQQQQQQQb",
        "bQQQQQQQQQQQQQQb",
        "bqQqQqQqQqQqQqQb",
        "bbbbbbbbbbbbbbbb",
    ],

    # ── used 블록 (16×16 → 32×32) ────────────────────────────────────────────
    'used_block': [
        "bbbbbbbbbbbbbbbb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "beeeeeeeeeeeeeeb",
        "bbbbbbbbbbbbbbbb",
    ],

    # ── 마리오 small 프레임 0 — 서기 / 걷기 A (13×15 → 26×30) ───────────────
    'mario_s0': [
        ".....RRR.....",
        "....RRRRR....",
        "....RRRRR....",
        "...WWKKKWW...",
        "..WKKKKKKKW..",
        "..WKOKKKKKW..",
        "..WKKOOKKWW..",
        "....RRRRR....",
        "...RRRRRRR...",
        "..UURRRUURRR.",
        ".UUUUUUUUUU..",
        "..UUU...UUU..",
        "..UUU...UUU..",
        "..WWW...WWW..",
        ".WWWW...WWWW.",
    ],

    # ── 마리오 small 프레임 1 — 걷기 B (다리 교차) ───────────────────────────
    'mario_s1': [
        ".....RRR.....",
        "....RRRRR....",
        "....RRRRR....",
        "...WWKKKWW...",
        "..WKKKKKKKW..",
        "..WKOKKKKKW..",
        "..WKKOOKKWW..",
        "....RRRRR....",
        "...RRRRRRR...",
        "..UURRRUURRR.",
        ".UUUUUUUUUU..",
        ".UUU....UUUU.",
        "..UUUUUUUU...",
        "...WWWWWW....",
        "..WWWW.WWWW..",
    ],

    # ── 마리오 small 점프 ─────────────────────────────────────────────────────
    'mario_sj': [
        ".....RRR.....",
        "....RRRRR....",
        "....RRRRR....",
        "...WWKKKWW...",
        "..WKKKKKKKW..",
        "..WKOKKKKKW..",
        "..WKKOOKKWW..",
        "....RRRRR....",
        "...RRRRRRR...",
        "..UURRRUURRR.",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUUU.",
        "..UUUUUUUUU..",
        "..WWWW.WWWW..",
        ".WWWWW.WWWWW.",
    ],

    # ── 마리오 big 프레임 0 — 서기 / 걷기 A (13×28 → 26×56) ─────────────────
    'mario_b0': [
        ".....RRR.....",
        "....RRRRR....",
        "...RRRRRRR...",
        "...RRRRRRR...",
        "...WWKKKWW...",
        "..WKKKKKKKW..",
        "..WKOKKKKKW..",
        "..WKKOOKKWW..",
        "..WKKKKKWWW..",
        "...RRRRRRR...",
        "...RRRRRRR...",
        "..RRRRRRRR...",
        ".UURRRUURRR..",
        ".UURRRUURRR..",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUU..",
        "..RRRRRRRR...",
        "..RRRRRRRR...",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUU..",
        "..UUU...UUU..",
        "..UUU...UUU..",
        "..UUU...UUU..",
        "..UUU...UUU..",
        "..WWW...WWW..",
        "..WWW...WWW..",
        ".WWWW...WWWW.",
        "WWWWW...WWWWW",
    ],

    # ── 마리오 big 프레임 1 — 걷기 B ─────────────────────────────────────────
    'mario_b1': [
        ".....RRR.....",
        "....RRRRR....",
        "...RRRRRRR...",
        "...RRRRRRR...",
        "...WWKKKWW...",
        "..WKKKKKKKW..",
        "..WKOKKKKKW..",
        "..WKKOOKKWW..",
        "..WKKKKKWWW..",
        "...RRRRRRR...",
        "...RRRRRRR...",
        "..RRRRRRRR...",
        ".UURRRUURRR..",
        ".UURRRUURRR..",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUU..",
        "..RRRRRRRR...",
        "..RRRRRRRR...",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUU..",
        ".UUU....UUUU.",
        "..UUUUUUUU...",
        "..UUUUUUUU...",
        "..UUUUUUUU...",
        "...WWWWWW....",
        "..WWWW.WWWW..",
        ".WWWWW.WWWWW.",
        "WWWWWW.WWWWWW",
    ],

    # ── 마리오 big 점프 ───────────────────────────────────────────────────────
    'mario_bj': [
        ".....RRR.....",
        "....RRRRR....",
        "...RRRRRRR...",
        "...RRRRRRR...",
        "...WWKKKWW...",
        "..WKKKKKKKW..",
        "..WKOKKKKKW..",
        "..WKKOOKKWW..",
        "..WKKKKKWWW..",
        "...RRRRRRR...",
        "...RRRRRRR...",
        "..RRRRRRRR...",
        ".UURRRUURRR..",
        ".UURRRUURRR..",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUU..",
        "..RRRRRRRR...",
        "..RRRRRRRR...",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUU..",
        ".UUUUUUUUUUU.",
        ".UUUUUUUUUUU.",
        "..UUUUUUUUU..",
        "..UUUUUUUUU..",
        "..WWWW.WWWW..",
        ".WWWWW.WWWWW.",
        "WWWWWW.WWWWWW",
        ".............",
    ],

    # ── 굼바 프레임 0 (14×13 → 28×26) ────────────────────────────────────────
    # 눈 윤곽: 'p'(거의 검정), 흰자: 'w', 눈동자: 'O'
    # 눈썹: 'p' 2px 두께로 \ / 대각선
    'goomba_0': [
        "..gggggggggg..",
        ".gGGGGGGGGGGg.",
        "gGGGGGGGGGGGGg",
        "gGppGGGGGGppGg",   # 눈썹 바깥쪽(높음) \ /
        "gGGppGGGGppGGg",   # 눈썹 안쪽(낮음)
        "gpwwwpGGpwwwpg",   # 눈 상단 — p 윤곽 + w 흰자
        "gpwOwpGGpwOwpg",   # 눈동자
        "gpwOwpGGpwOwpg",   # 눈동자
        "gpwwwpGGpwwwpg",   # 눈 하단
        ".gGGGGGGGGGGg.",
        "..GGGGGGGGGG..",
        "..fGGGGGGGff..",
        ".ffGGGGGGfff..",
    ],

    # ── 굼바 프레임 1 — 발 위치 다름 ─────────────────────────────────────────
    'goomba_1': [
        "..gggggggggg..",
        ".gGGGGGGGGGGg.",
        "gGGGGGGGGGGGGg",
        "gGppGGGGGGppGg",
        "gGGppGGGGppGGg",
        "gpwwwpGGpwwwpg",
        "gpwOwpGGpwOwpg",
        "gpwOwpGGpwOwpg",
        "gpwwwpGGpwwwpg",
        ".gGGGGGGGGGGg.",
        "..GGGGGGGGGG..",
        "..GGfGGGGfGG..",   # 발 위치 반대 스텝
        "..GGffGGffGG..",
    ],

    # ── 굼바 납작 (밟혔을 때) ─────────────────────────────────────────────────
    'goomba_squish': [
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..gggggggggg..",
        ".gGGGGGGGGGGg.",
        "gpwpGGGGGpwpGg",   # 납작해진 눈 (p윤곽+흰자 1px)
        "gGGGGGGGGGGGGg",
        ".gGGGGGGGGGGg.",
        "ggGGGGGGGGGggg",
    ],

    # ── 버섯 (14×14 → 28×28) ─────────────────────────────────────────────────
    'mushroom': [
        "...MMMMMMMM...",
        "..MMMMMMMMMM..",
        ".MMwwMMMMwwMMM",
        ".MMwwMMMMwwMMM",
        ".MMMMMMMMMMMM.",
        "MMMMMMMMMMMMMM",
        ".MMMMMMMMMMMM.",
        "..HHHHHHHHHH..",
        "..HHHHHHHHHH..",
        ".HHHHHHHHHHHH.",
        "HHHHHHHHHHHHHH",
        ".HHHHHHHHHHHH.",
        "..HHHHHHHHHH..",
        "..............",
    ],
}
