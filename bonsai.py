# bonsai.py -- generative ASCII bonsai for NumWorks (Epsilon)
# inspired by cbonsai (linux)
# UP/DOWN pick a line, LEFT/RIGHT change it, OK grow, DEL back/exit

from kandinsky import fill_rect, draw_string
from ion import *
from time import sleep
from random import randint

W = 320
H = 222

# ---- font detection (the small font is not on every Epsilon version) ----
try:
    draw_string("", 0, 0, (0, 0, 0), (0, 0, 0), "small")
    SMALL = True
except:
    SMALL = False

if SMALL:
    CW = 7
    CH = 14

    def putstr(s, x, y, f, b):
        draw_string(s, x, y, f, b, "small")
else:
    CW = 10
    CH = 18

    def putstr(s, x, y, f, b):
        draw_string(s, x, y, f, b)

COLS = W // CW
ROWS = H // CH
XOFF = (W - COLS * CW) // 2
YOFF = H - ROWS * CH

# ---------------- themes ----------------
DARK = {
    "bg": (16, 18, 22),
    "fg": (226, 229, 233),
    "dim": (122, 130, 142),
    "acc": (118, 208, 255),
    "trunk": ((152, 114, 76), (108, 79, 51)),
    "pot": (150, 156, 166),
    "soil": (126, 90, 58),
    "leafsets": (
        ((62, 190, 82), (124, 222, 92), (176, 230, 112), (38, 148, 70)),
        ((255, 170, 205), (250, 130, 180), (255, 210, 228), (228, 105, 160)),
        ((242, 150, 50), (226, 80, 45), (246, 198, 72), (190, 95, 40)),
    ),
}

LIGHT = {
    "bg": (246, 245, 240),
    "fg": (32, 34, 38),
    "dim": (128, 128, 128),
    "acc": (0, 118, 188),
    "trunk": ((124, 86, 52), (92, 62, 38)),
    "pot": (88, 90, 96),
    "soil": (112, 80, 50),
    "leafsets": (
        ((32, 140, 52), (62, 170, 62), (18, 108, 44), (104, 182, 60)),
        ((222, 88, 148), (240, 122, 176), (196, 56, 122), (246, 150, 192)),
        ((198, 92, 24), (176, 48, 28), (212, 148, 32), (148, 68, 22)),
    ),
}

THEMES = (DARK, LIGHT)
THEME_NAMES = ("Dark", "Light")
PAL_NAMES = ("Green", "Sakura", "Autumn", "Random")
AUTO_NAMES = ("Off", "Instant", "2 sec", "5 sec")
AUTO_WAIT = (0, 0.25, 2.0, 5.0)

# ---------------- helpers ----------------


def rnd(n):
    return randint(0, n - 1)


def cell(col, row, s, f, bg):
    if row < 0 or row >= ROWS:
        return
    for i in range(len(s)):
        c = col + i
        if 0 <= c < COLS:
            putstr(s[i], XOFF + c * CW, YOFF + row * CH, f, bg)


try:
    KEY_DEL = KEY_BACKSPACE        # the "delete" key
except NameError:
    KEY_DEL = KEY_BACK

KEYS = (KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_EXE,
        KEY_BACK, KEY_DEL)


def back_down():
    return keydown(KEY_DEL) or keydown(KEY_BACK)


def anykey():
    for k in KEYS:
        if keydown(k):
            return KEY_BACK if k == KEY_DEL else k
    return None


def wait_release():
    while anykey() is not None:
        sleep(0.02)


def wait_key():
    wait_release()
    while True:
        k = anykey()
        if k is not None:
            return k
        sleep(0.02)


def wait_key_t(sec):
    # same, but gives up after sec seconds and returns None
    wait_release()
    n = int(sec * 20)
    for i in range(n):
        k = anykey()
        if k is not None:
            return k
        sleep(0.05)
    return None


# ---------------- the tree ----------------
TRUNK = 0
SHOOT_L = 1
SHOOT_R = 2
DYING = 3
DEAD = 4

# size presets:
# (life, mult, shoots, shoot bonus, half width, min trunk, max height, delay)
SIZES = ((13, 3, 4, 3, 9, 4, 7, 0.04),
         (15, 3, 5, 3, 12, 4, 9, 0.05),
         (19, 4, 7, 4, 15, 5, 10, 0.03),
         (26, 5, 9, 5, 20, 6, 99, 0.02))
SIZE_NAMES = ("Tiny", "Small", "Medium", "Big")

BASE = ("(---./~~\\.---)",
        " (           )",
        "  (_________)")

MSGS = ("stay green.", "grow slowly.", "one more branch.",
        "breathe in.", "zen loading...", "no two alike.")


def deltas(t, life, age, mult):
    if t == TRUNK:
        if age <= 2:
            dy = 0 if age == 1 else -1   # sit on the pot, then go up
            dx = 0
        elif life < 4:
            dy = 0
            dx = rnd(3) - 1
        elif age < mult * 3:
            dy = -1 if (age % 2) == 0 else 0
            d = rnd(10)
            if d == 0:
                dx = -2
            elif d < 3:
                dx = -1
            elif d < 7:
                dx = 0
            elif d < 9:
                dx = 1
            else:
                dx = 2
        else:
            dy = -1 if rnd(10) > 2 else 0
            dx = rnd(3) - 1
    elif t == SHOOT_L:
        d = rnd(10)
        dy = -1 if d < 4 else (0 if d < 8 else 1)
        d = rnd(10)
        dx = -2 if d < 2 else (-1 if d < 7 else 0)
    elif t == SHOOT_R:
        d = rnd(10)
        dy = -1 if d < 4 else (0 if d < 8 else 1)
        d = rnd(10)
        dx = 2 if d < 2 else (1 if d < 7 else 0)
    elif t == DYING:
        d = rnd(10)
        dy = -1 if d < 4 else (0 if d < 8 else 1)
        d = rnd(12)
        dx = -2 if d < 3 else (-1 if d < 5 else (0 if d < 7 else (1 if d < 9 else 2)))
    else:  # DEAD
        d = rnd(10)
        dy = -1 if d < 3 else (0 if d < 6 else 1)
        dx = rnd(3) - 1
    return dx, dy


def glyph(t, dx, dy, life):
    if life < 4:
        t = DYING
    if t == TRUNK:
        if dy == 0:
            return "/~"
        if dx < 0:
            return "\\|"
        if dx == 0:
            return "/|\\"
        return "|/"
    if t == SHOOT_L:
        if dy > 0:
            return "\\"
        if dy == 0:
            return "\\_"
        if dx < 0:
            return "\\|"
        if dx == 0:
            return "/|"
        return "/"
    if t == SHOOT_R:
        if dy > 0:
            return "/"
        if dy == 0:
            return "_/"
        if dx < 0:
            return "\\|"
        if dx == 0:
            return "/|"
        return "/"
    return "&"


def draw_base(th):
    col = (COLS - 14) // 2
    row = ROWS - 3
    for r in range(3):
        line = BASE[r]
        for i in range(len(line)):
            ch = line[i]
            if ch == " ":
                continue
            c = th["soil"] if (r == 0 and ch in "./~\\") else th["pot"]
            cell(col + i, row + r, ch, c, th["bg"])


ZX = 3        # the canvas is split into ZX x ZY zones
ZY = 2


def grow(th, leaf, si, anim):
    life0, mult, max_shoots, shoot_add, spread, min_h, hmax, delay = SIZES[si]
    if not SMALL:                      # fewer rows -> shorter tree
        life0 = life0 * 3 // 4
        min_h = min_h - 1
        hmax = hmax * 3 // 4
    bg = th["bg"]
    ground = ROWS - 4
    if min_h > ground - 1:
        min_h = ground - 1
    mid = COLS // 2
    xmin = mid - spread
    xmax = mid + spread
    if xmin < 1:
        xmin = 1
    if xmax > COLS - 3:
        xmax = COLS - 3
    ymin = ground - hmax
    if ymin < 1:
        ymin = 1
    if min_h > ground - ymin:
        min_h = ground - ymin
    zw = xmax - xmin + 1
    zh = ground - ymin + 1
    zone = [0] * (ZX * ZY)             # how full each zone is

    def mark(col, row):
        zx = (col - xmin) * ZX // zw
        zy = (row - ymin) * ZY // zh
        if zx < 0:
            zx = 0
        elif zx >= ZX:
            zx = ZX - 1
        if zy < 0:
            zy = 0
        elif zy >= ZY:
            zy = ZY - 1
        zone[zy * ZX + zx] += 1

    def target():
        # aim at the emptiest zone, scanning from a random place for variety
        n = ZX * ZY
        o = rnd(n)
        best = o
        for i in range(n):
            j = (o + i) % n
            if zone[j] < zone[best]:
                best = j
        zx = best % ZX
        zy = best // ZX
        return (xmin + zx * zw // ZX + zw // (2 * ZX),
                ymin + zy * zh // ZY + zh // (2 * ZY))

    stack = [[mid, ground, TRUNK, life0, 1 if rnd(2) else -1, -1, -1]]
    shoots = 0
    cool = 0
    steps = 0
    armed = False      # OK only skips once it has been released first
    while stack:
        b = stack[-1]
        if b[3] <= 0:
            stack.pop()
            continue
        b[3] -= 1
        life = b[3]
        t = b[2]
        age = life0 - life
        if age < 0:
            age = 0
        low = (t == TRUNK) and (ground - b[1] < min_h)
        dx, dy = deltas(t, life, age, mult)
        if t == TRUNK and age > 2 and life >= 4:
            # the trunk leans one way for a while, then swings back
            if rnd(5) == 0:
                b[4] = -b[4]
            d = rnd(10)
            if d < 4:
                dx = b[4] * 2
            elif d < 8:
                dx = b[4]
            elif d < 9:
                dx = 0
            else:
                dx = -b[4]
        elif b[5] >= 0:
            # a branch heading for an empty zone
            tx = b[5]
            ty = b[6]
            if b[0] > tx - 2 and b[0] < tx + 2 and \
               b[1] > ty - 2 and b[1] < ty + 2:
                b[5] = -1              # arrived, grow freely from here
            else:
                if rnd(10) < 7:
                    if b[0] < tx:
                        dx = 2 if rnd(3) else 1
                    elif b[0] > tx:
                        dx = -2 if rnd(3) else -1
                    else:
                        dx = 0
                if rnd(10) < 6:
                    dy = 1 if b[1] < ty else (-1 if b[1] > ty else 0)
        if low and age > 1 and rnd(4) > 0:
            dy = -1                    # keep the trunk climbing out of the pot
        if b[1] + dy < ymin:
            dy = 0
        if b[1] + dy > ground:
            dy = 0
        b[0] += dx
        b[1] += dy
        if b[0] < xmin:
            b[0] = xmin
            b[4] = 1                   # bounce off the edge instead of dying
            if b[3] > 2 and not low and t != TRUNK and b[5] < 0:
                b[3] = 2
        elif b[0] > xmax:
            b[0] = xmax
            b[4] = -1
            if b[3] > 2 and not low and t != TRUNK and b[5] < 0:
                b[3] = 2
        if t >= DYING or life < 4:
            c = leaf[rnd(len(leaf))]
        else:
            c = th["trunk"][rnd(2)]
        if dx > 1 or dx < -1:          # bridge the gap of a wide sideways step
            step = 1 if dx > 0 else -1
            fill = "_" if dy == 0 else ("/" if dx > 0 else "\\")
            for j in range(1, dx if dx > 0 else -dx):
                cell(b[0] - step * j, b[1], fill, c, bg)
        cell(b[0], b[1], glyph(t, dx, dy, life), c, bg)
        mark(b[0], b[1])
        steps += 1
        if steps % 3 == 0:
            if back_down():           # bail out of the whole tree
                return True
            if anim:
                if not armed:
                    armed = not keydown(KEY_OK)
                elif keydown(KEY_OK):
                    anim = False
                    wait_release()
        if anim:
            sleep(delay)
        if cool > 0:
            cool -= 1
        x = b[0]
        y = b[1]
        if t == TRUNK and (ground - y) < min_h and life < mult + 2:
            b[3] = life + 2            # too short yet: let the trunk live on
        elif life < 3:
            stack.append([x, y, DEAD, life, 0, -1, -1])
        elif t == TRUNK and life < mult + 2:
            stack.append([x, y, DYING, life, 0, -1, -1])
        elif (t == SHOOT_L or t == SHOOT_R) and life < mult + 2:
            stack.append([x, y, DYING, life, 0, b[5], b[6]])
        elif shoots < max_shoots and cool <= 0 and \
                ((t == TRUNK and age > 2 and
                  (life % mult == 0 or rnd(3) == 0)) or
                 (t != TRUNK and life % mult == 0 and rnd(3) == 0)):
            cool = mult
            shoots += 1
            tx, ty = target()
            stack.append([x, y, SHOOT_L if tx < x else SHOOT_R,
                          life + shoot_add, 0, tx, ty])
    return False


def draw_msg(th):
    m = MSGS[rnd(len(MSGS))]
    w = len(m) + 4
    bx = COLS - w - 1
    by = 2
    cell(bx, by, "." + "-" * (w - 2) + ".", th["dim"], th["bg"])
    cell(bx, by + 1, "| " + m + " |", th["fg"], th["bg"])
    cell(bx, by + 2, "'" + "-" * (w - 2) + "'", th["dim"], th["bg"])


def pick_leaf(th, li):
    return th["leafsets"][rnd(3) if li == 3 else li]


def bonsai(th, li, si, ai):
    fill_rect(0, 0, W, H, th["bg"])
    draw_base(th)
    if grow(th, pick_leaf(th, li), si, True):
        wait_release()
        return KEY_BACK
    draw_msg(th)
    if ai:
        cell(1, 0, "auto   DEL stop", th["dim"], th["bg"])
        k = wait_key_t(AUTO_WAIT[ai])
        return KEY_OK if k is None else k
    cell(1, 0, "OK new tree   DEL menu", th["dim"], th["bg"])
    return wait_key()


# ---------------- menu ----------------
MINI = ("  &&&&& ",
        " &&&/&&&",
        "  \\&|&/ ",
        "   \\|/  ",
        "    |   ",
        " (-___-)")


def draw_art(lines, col, row, th, leaf):
    for r in range(len(lines)):
        ln = lines[r]
        for i in range(len(ln)):
            ch = ln[i]
            if ch == " ":
                continue
            if ch == "&":
                c = leaf[rnd(len(leaf))]
            elif ch in "()_-":
                c = th["pot"]
            else:
                c = th["trunk"][0]
            cell(col + i, row + r, ch, c, th["bg"])


def draw_menu(cur, ti, li, si, ai):
    th = THEMES[ti]
    bg = th["bg"]
    fill_rect(0, 0, W, H, bg)

    t = "B O N S A I"
    draw_string(t, max(0, (W - len(t) * 10) // 2), 8, th["acc"], bg)
    sub = "random tree generator"
    putstr(sub, max(0, (W - len(sub) * CW) // 2), 34, th["dim"], bg)

    rows = ("Theme  < " + THEME_NAMES[ti] + " >",
            "Leaves < " + PAL_NAMES[li] + " >",
            "Size   < " + SIZE_NAMES[si] + " >",
            "Auto   < " + AUTO_NAMES[ai] + " >",
            "[ Grow ]")
    y0 = 66
    for i in range(5):
        c = th["acc"] if i == cur else th["fg"]
        putstr(rows[i], 30, y0 + i * 24, c, bg)
        if i == cur:
            fill_rect(20, y0 + i * 24 + 2, 4, CH - 4, th["acc"])

    draw_art(MINI, COLS - (9 if SMALL else 8), 3, th, pick_leaf(th, li))

    if SMALL:
        hint = "LEFT/RIGHT change   OK grow   DEL exit"
    else:
        hint = "OK grow   DEL exit"
    putstr(hint, max(0, (W - len(hint) * CW) // 2), H - 20, th["dim"], bg)


def menu(ti, li, si, ai):
    cur = 0
    redraw = True
    while True:
        if redraw:
            draw_menu(cur, ti, li, si, ai)
            redraw = False
        k = wait_key()
        if k == KEY_UP:
            cur = (cur + 4) % 5
            redraw = True
        elif k == KEY_DOWN:
            cur = (cur + 1) % 5
            redraw = True
        elif k == KEY_LEFT or k == KEY_RIGHT:
            d = 1 if k == KEY_RIGHT else -1
            if cur == 0:
                ti = 1 - ti
            elif cur == 1:
                li = (li + d) % 4
            elif cur == 2:
                si = (si + d) % 4
            elif cur == 3:
                ai = (ai + d) % 4
            redraw = True
        elif k == KEY_OK or k == KEY_EXE:
            return ti, li, si, ai, True
        elif k == KEY_BACK:
            return ti, li, si, ai, False


def main():
    ti = 0
    li = 0
    si = 0
    ai = 0
    while True:
        ti, li, si, ai, go = menu(ti, li, si, ai)
        if not go:
            fill_rect(0, 0, W, H, (255, 255, 255))
            return
        while True:
            if bonsai(THEMES[ti], li, si, ai) == KEY_BACK:
                break


main()
