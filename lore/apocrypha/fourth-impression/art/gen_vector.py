#!/usr/bin/env python3
"""Vector plates for the second impression. Every plate is drawn from a fixed
seed, so the book rebuilds identically. Output: art/*.svg"""
import math, random, pathlib
import numpy as np

A = pathlib.Path(__file__).resolve().parent
PAPER, RAG, INK = '#f4eddf', '#e6d9bb', '#1c1a17'
OX, OCHRE, LAKE, SLATE, PENCIL = '#8b2a20', '#a47418', '#1f4e3d', '#3c5261', '#6d6252'
MONO, SERIF = 'IBM Plex Mono', 'EB Garamond 12'
W, H = 900, 1260


class S:
    def __init__(self, w=W, h=H, bg=None):
        self.w, self.h, self.o = w, h, []
        if bg:
            self.rect(0, 0, w, h, fill=bg, stroke='none')

    def add(self, s): self.o.append(s)

    def line(self, x1, y1, x2, y2, c=INK, sw=1.2, dash=None, op=1, cap='round'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{sw}" stroke-linecap="{cap}" opacity="{op}"{d}/>')

    def poly(self, pts, c=INK, sw=1.2, fill='none', close=False, dash=None, op=1):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + (' Z' if close else '')
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" opacity="{op}"{da}/>')

    def path(self, d, c=INK, sw=1.2, fill='none', op=1, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"{da}/>')

    def rect(self, x, y, w, h, c=INK, sw=1.2, fill='none', stroke=None, dash=None, op=1, rx=0):
        st = stroke if stroke is not None else c
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{st}" stroke-width="{sw}" opacity="{op}"{da}/>')

    def circ(self, x, y, r, c=INK, sw=1.2, fill='none', op=1):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{fill}" stroke="{c}" stroke-width="{sw}" opacity="{op}"/>')

    def dot(self, x, y, r, c=INK, op=1):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}" opacity="{op}"/>')

    def text(self, x, y, s, size=15, c=INK, font=MONO, anchor='start', rot=None, ls=0.5, style='normal', weight='normal'):
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ''
        s = s.replace('&', '&amp;').replace('<', '&lt;')
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{c}" text-anchor="{anchor}" letter-spacing="{ls}" font-style="{style}" font-weight="{weight}"{tr}>{s}</text>')

    def save(self, name):
        (A / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">' + '\n'.join(self.o) + '</svg>')
        print(name, len(self.o))


def frame(s, title=None):
    s.rect(18, 18, s.w - 36, s.h - 36, c=INK, sw=1.4)
    s.rect(26, 26, s.w - 52, s.h - 52, c=INK, sw=0.5)
    if title:
        s.text(s.w / 2, 58, title, size=13, anchor='middle', ls=3, c=PENCIL)


# ------------------------------------------------------------------ I. foreign leaf
def glyph(rnd, s, x, y, h, c, sw):
    """one asemic letter from a small grammar of strokes"""
    w = h * rnd.choice([0.35, 0.45, 0.55, 0.7])
    k = rnd.random()
    if k < 0.3:
        s.path(f'M{x:.1f},{y - h:.1f} q{w * 0.1:.1f},{h * 0.6:.1f} {w * 0.5:.1f},{h:.1f} q{w * 0.4:.1f},{-h * 0.2:.1f} {w * 0.5:.1f},{-h * 0.55:.1f}', c=c, sw=sw)
    elif k < 0.55:
        s.path(f'M{x:.1f},{y - h * 0.55:.1f} c{w * 0.5:.1f},{-h * 0.5:.1f} {w:.1f},{h * 0.1:.1f} {w * 0.45:.1f},{h * 0.55:.1f} c{-w * 0.5:.1f},{h * 0.1:.1f} {-w * 0.3:.1f},{-h * 0.5:.1f} {w * 0.5:.1f},{-h * 0.3:.1f}', c=c, sw=sw)
    elif k < 0.75:
        d = rnd.choice([-1, 1]) * h * rnd.choice([0.35, 0.6])
        s.path(f'M{x + w * 0.2:.1f},{y - h * 0.6 - max(0, -d):.1f} l0,{h * 0.6 + abs(d):.1f} m0,{-h * 0.35 - (d if d > 0 else 0):.1f} q{w * 0.5:.1f},{-h * 0.5:.1f} {w * 0.7:.1f},{h * 0.3:.1f}', c=c, sw=sw)
    elif k < 0.9:
        s.path(f'M{x:.1f},{y:.1f} l{w * 0.5:.1f},{-h * 0.6:.1f} l{w * 0.4:.1f},{h * 0.6:.1f}', c=c, sw=sw)
        s.dot(x + w * 0.5, y - h * 0.85, sw * 0.9, c)
    else:
        s.path(f'M{x:.1f},{y - h * 0.3:.1f} a{w * 0.4:.1f},{h * 0.3:.1f} 0 1 0 {w * 0.8:.1f},0 a{w * 0.4:.1f},{h * 0.3:.1f} 0 1 0 {-w * 0.8:.1f},0', c=c, sw=sw)
    return w + h * 0.14


def textline(rnd, s, x0, x1, y, h, c=INK, sw=1.0, fill=1.0):
    x = x0
    end = x0 + (x1 - x0) * fill
    while x < end - h:
        n = rnd.randint(2, 7)
        for _ in range(n):
            if x > end - h * 0.6:
                break
            x += glyph(rnd, s, x, y, h, c, sw)
        x += h * 0.55


def leaf():
    rnd = random.Random(1898)
    s = S(bg=RAG)
    for y in range(40, H, 7):
        s.line(0, y, W, y, c='#b9a67c', sw=0.35, op=0.55)
    for x in range(70, W, 118):
        s.line(x, 0, x, H, c='#a8935f', sw=0.5, op=0.5)
    for i in range(14):
        y = 90 + i * 80
        s.line(34, y, 34, y + 46, c=OCHRE, sw=4.2, op=0.95)
        s.line(34, y + 46, 44, y + 60, c=OCHRE, sw=1.2, op=0.6)
    s.text(W - 110, 92, '19', size=22, font=SERIF, c=INK)
    y = 150
    for row in range(13):                      # the verse, which breaks off
        if row % 4 == 0:
            textline(rnd, s, 330, 560, y, 15, c=OX, sw=1.3)
            y += 34
        textline(rnd, s, 120, 800, y, 16, sw=1.15, fill=rnd.uniform(0.55, 1.0))
        y += 34
    textline(rnd, s, 120, 800, y, 16, sw=1.15, fill=0.22)
    y += 40
    s.line(96, y, W - 70, y, c=INK, sw=3.4)
    s.line(96, y + 5, W - 300, y + 5, c=INK, sw=1.6, op=0.7)
    y += 46
    cols = [(120, 300), (350, 530), (580, 780)]   # narrow columns of rubric
    for (a, b) in cols:
        yy = y
        textline(rnd, s, a, b, yy, 11, c=OX, sw=1.0, fill=0.7)
        yy += 26
        for r in range(22):
            textline(rnd, s, a, b, yy, 10.5, sw=0.85, fill=1.0 if r % 6 != 5 else 0.5)
            yy += 22
    rr = np.random.default_rng(7)
    for _ in range(2600):                      # the deposit along the foot
        x = rr.uniform(60, W - 40)
        d = abs(rr.normal(0, 16))
        yy = H - 46 - d - 14 * math.sin(x / 90.0) ** 2
        s.dot(x, yy, rr.uniform(0.5, 1.7), c=rr.choice(['#b8860b', '#c99a1e', '#9a7412']), op=rr.uniform(0.35, 0.9))
    s.save('p01-leaf.svg')


# ------------------------------------------------------------------ II. plat
def field(n=220, seed=16):
    rg = np.random.default_rng(seed)
    y, x = np.mgrid[0:1:n * 1j, 0:1:n * 1j]
    z = np.zeros_like(x)
    for k in range(1, 7):
        for _ in range(3):
            fx, fy = rg.normal(0, k * 1.6, 2)
            z += np.sin(2 * math.pi * (fx * x + fy * y) + rg.uniform(0, 6.28)) / (k ** 1.35)
    z += 2.2 * np.exp(-(((x - 0.5) ** 2 + (y - 0.5) ** 2) / 0.05))      # the ridge the ice went round
    return x, y, z


def contours(s, x0, y0, size, levels, c=INK, sw=0.6, seed=16, op=0.8, clip=None):
    import contourpy
    x, y, z = field(seed=seed)
    cg = contourpy.contour_generator(x, y, z)
    for i, lv in enumerate(np.linspace(z.min(), z.max(), levels)[1:-1]):
        for ln in cg.lines(lv):
            pts = [(x0 + px * size, y0 + py * size) for px, py in ln]
            if clip:
                pts = [p for p in pts if clip(p)]
                if len(pts) < 2:
                    continue
            s.poly(pts, c=c, sw=sw * (1.8 if i % 5 == 0 else 1), op=op)


def plat():
    rg = np.random.default_rng(1891)
    s = S(bg=PAPER)
    frame(s, 'HAWKSMOOR COUNTY  --  TOWNSHIP 5 NORTH, RANGE 8 WEST')
    x0, y0, size = 90, 130, 720
    contours(s, x0, y0, size, 26, c=PENCIL, sw=0.55)
    c3 = size / 3
    for i in range(4):
        s.line(x0 + i * c3, y0, x0 + i * c3, y0 + size, c=INK, sw=0.9, dash='7 5')
        s.line(x0, y0 + i * c3, x0 + size, y0 + i * c3, c=INK, sw=0.9, dash='7 5')
    nums = [[9, 10, 11], [16 - 1 + 0, 16, 16 + 1 - 2 + 1], [21, 22, 23]]
    nums = [[8, 9, 10], [17, 16, 15], [20, 21, 22]]
    for r in range(3):
        for q in range(3):
            cx, cy = x0 + q * c3, y0 + r * c3
            s.text(cx + 12, cy + 26, f'SEC. {nums[r][q]}', size=12, c=PENCIL)
            if (r, q) != (1, 1):               # glacial drift on every neighbouring section
                for _ in range(520):
                    s.dot(cx + rg.uniform(4, c3 - 4), cy + rg.uniform(4, c3 - 4), rg.uniform(0.6, 1.5), c=INK, op=0.5)
    ax, ay = x0 + c3, y0 + c3
    s.rect(ax, ay, c3, c3, c=INK, sw=2.2)
    s.text(ax + c3 / 2, ay - 9, 'DRIFT: NIL', size=13, anchor='middle', c=OX, ls=2)
    # traverse: Mon.4 (NW) east 80, south 80, west 77.12, north 77.84; error drawn x3
    k = (c3 - 30) / 80.0
    p = [(ax + 15, ay + 15)]
    for dx, dy in [(80, 0), (0, 80), (-77.12 + 2.88 * -2, 0), (0, -77.84 + 2.16 * 2)]:
        p.append((p[-1][0] + dx * k, p[-1][1] + dy * k))
    s.poly(p, c=OX, sw=1.8)
    s.line(p[-1][0], p[-1][1], p[0][0], p[0][1], c=OX, sw=1.1, dash='3 4')
    for i, (px, py) in enumerate(p[:4]):
        s.rect(px - 6, py - 6, 12, 12, c=INK, sw=1.4, fill=PAPER)
        s.text(px + (12 if i in (0, 3) else -12), py + (-12 if i < 2 else 24), f'MON. {[4, 1, 2, 3][i]}', size=11, anchor='start' if i in (0, 3) else 'end')
    cx, cy = ax + c3 / 2 + 6, ay + c3 / 2 + 4
    s.circ(cx, cy, 6, c=OX, sw=1.6, fill=PAPER); s.dot(cx, cy, 2, OX)
    s.text(cx + 12, cy + 4, 'IRON PIN, 13 OCT 1891', size=10.5, c=OX)
    s.circ(cx - 30, cy + 26, 11, c=INK, sw=0.9); s.text(cx - 16, cy + 44, 'dry sink', size=10.5, font=SERIF, style='italic')
    for i in range(9):                         # needles that will not settle, near Mon. 3
        a = rg.uniform(0, 6.28)
        nx, ny = p[3][0] + 26 + (i % 3) * 22, p[3][1] - 70 + (i // 3) * 22
        s.line(nx - 8 * math.cos(a), ny - 8 * math.sin(a), nx + 8 * math.cos(a), ny + 8 * math.sin(a), c=INK, sw=1)
        s.dot(nx + 8 * math.cos(a), ny + 8 * math.sin(a), 1.8, OX)
    wx, wy = ax - 70, ay + c3 * 0.42            # low banks west of the works
    for j in range(3):
        o = j * 6
        s.path(f'M{wx - 60 + o:.0f},{wy - 46 + o * .6:.0f} q30,34 60,40 q-16,22 -66,44 M{wx:.0f},{wy - 6:.0f} q28,2 46,-10 M{wx:.0f},{wy - 6:.0f} q-40,2 -92,-6', c=INK, sw=0.8, op=0.85)
    s.text(wx - 96, wy + 62, 'entered as wash', size=11, font=SERIF, style='italic')
    s.text(x0, y0 + size + 34, 'SCALE: 80 CHAINS TO THE SECTION SIDE.  CLOSURE ERROR 3.60 CH, FALLING INWARD; DRAWN AT THREE TIMES.', size=10.5, c=PENCIL)
    s.text(x0, y0 + size + 54, 'RE-CHAINED 8, 11 AND 19 FEB 1892 IN CLEAR WEATHER.  -- E. T. PAIGE, DEPUTY SURVEYOR', size=10.5, c=PENCIL)
    nx, ny = x0 + size - 46, y0 + size + 150
    s.line(nx, ny + 60, nx, ny - 60, sw=1.2); s.poly([(nx - 9, ny - 38), (nx, ny - 62), (nx + 9, ny - 38)], sw=1.2)
    s.text(nx, ny - 72, 'N', size=13, anchor='middle')
    s.text(x0, y0 + size + 150, 'Section 16, with the five monuments', size=25, font=SERIF, style='italic')
    s.text(x0, y0 + size + 184, 'and the traverse as run.', size=25, font=SERIF, style='italic')
    s.save('p02-plat.svg')


# ------------------------------------------------------------------ III. hotel
def hotel():
    rnd = random.Random(1913)
    s = S(bg=PAPER)
    frame(s, 'PALACE SPRINGS HOTEL  --  LAKE ELEVATION AND STAIR')
    x0, base, bw, fh, bays = 100, 980, 62, 150, 9
    wdt = bays * bw
    for f in range(4):
        y = base - (f + 1) * fh
        ghost = f == 3
        col, dash, op = (OCHRE, '6 5', 0.9) if ghost else (INK, None, 1)
        s.rect(x0, y, wdt, fh, c=col, sw=1.6, dash=dash, op=op)
        for b in range(bays):
            wx = x0 + b * bw + 15
            lit = ghost and b == 6
            s.rect(wx, y + 34, bw - 30, fh - 74, c=col, sw=1.1, dash=dash, fill=('#e9c46a' if lit else 'none'), op=op)
            s.line(wx + (bw - 30) / 2, y + 34, wx + (bw - 30) / 2, y + fh - 40, c=col, sw=0.6, op=op)
            s.line(wx, y + 34 + (fh - 74) * .45, wx + bw - 30, y + 34 + (fh - 74) * .45, c=col, sw=0.6, op=op)
            if not ghost and f < 3:
                for k in range(5):
                    s.line(x0 + b * bw + k * bw / 5, y + fh - 26, x0 + b * bw + k * bw / 5, y + fh - 4, c=INK, sw=0.5)
        if not ghost:
            s.line(x0 - 14, y + fh - 26, x0 + wdt + 14, y + fh - 26, sw=1)
        s.text(x0 - 22, y + fh / 2 + 5, ['GROUND', 'FIRST', 'SECOND', 'FOURTH'][f], size=11, anchor='end', c=OCHRE if ghost else PENCIL)
    s.poly([(x0 - 20, base - 3 * fh), (x0 + 40, base - 3 * fh - 46), (x0 + wdt - 40, base - 3 * fh - 46), (x0 + wdt + 20, base - 3 * fh)], sw=1.2, op=0.35)
    s.text(x0 + 6.5 * bw, base - 4 * fh - 14, 'SUITE 400', size=12, c=OCHRE, anchor='middle')
    s.line(x0 - 40, base, x0 + wdt + 40, base, sw=2)
    for i in range(46):
        xx = x0 - 40 + i * (wdt + 80) / 46
        s.line(xx, base + 3, xx - 9, base + 15, sw=0.6)
    dx = x0 + wdt + 44
    s.line(dx, base, dx, base - 3 * fh, sw=0.8); s.line(dx - 6, base, dx + 6, base, sw=0.8); s.line(dx - 6, base - 3 * fh, dx + 6, base - 3 * fh, sw=0.8)
    s.text(dx + 14, base - 1.5 * fh, 'THREE FLOORS (AS REGISTERED)', size=11, rot=-90, anchor='middle')
    # the stair: four landings between ground and first
    sx, sy = 150, 1180
    s.text(sx - 40, sy - 138, 'STAIR, GROUND TO FIRST: LANDINGS COUNTED', size=11, c=PENCIL)
    x, y = sx, sy
    pts = [(x, y)]
    for l in range(4):
        for st in range(5):
            x += 16; pts.append((x, y)); y -= 5.5; pts.append((x, y))
        x += 52; pts.append((x, y))
        s.text(x - 26, y - 9, str(l + 1), size=12, anchor='middle', c=OX if l > 1 else INK)
    s.poly(pts, sw=1.3)
    s.text(sx + 590, sy - 70, 'KEY 118', size=12, c=OX)
    s.circ(sx + 560, sy - 74, 9, c=OX, sw=1.5); s.line(sx + 569, sy - 74, sx + 600, sy - 74, c=OX, sw=1.5); s.line(sx + 592, sy - 74, sx + 592, sy - 66, c=OX, sw=1.5)
    s.save('p03-hotel.svg')


# ------------------------------------------------------------------ IV. morse tape
MORSE = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..'}


def tape():
    s = S(bg=PAPER)
    frame(s, 'WESTERN UNION REPEATER, JERSEY CITY  --  TAPE AS RECOVERED')
    msg = ('ROOK SYNDICATE HAS ACQUIRED FULL GALLEY PROOFS OF THE MONTMARTRE TWO ACT STOP SETTING TYPE IN JERSEY CITY LOFT '
           'ADJACENT TO WESTERN UNION REPEATER STOP PLANS TO TRANSMIT ACT II AS SERIALIZED MORSE WIRE NOV 1 STOP '
           'IF IT ENTERS THE CABLE THE TEXT WILL NOT STAY ON PAPER STOP SEND MARGINALS IMMEDIATELY')
    units = []
    for word in msg.split():
        for ch in word:
            for sym in MORSE.get(ch, ''):
                units.append(1 if sym == '.' else 3); units.append(0)
            units.append(-2)
        units.append(-4)
    x0, x1, y, u = 80, W - 80, 120, 4.1
    x, row = x0, 0
    rows = 24

    def strip(yy):
        s.rect(x0 - 12, yy - 15, x1 - x0 + 24, 30, c=PENCIL, sw=0.5, fill='#efe5cf')
    strip(y)
    for v in units:
        wdt = (abs(v) if v else 1) * u
        if x + wdt > x1:
            row += 1; x = x0; y += 42
            if row >= rows:
                break
            strip(y)
        if v > 0:
            s.rect(x, y - 4.5, wdt, 9, c='none', sw=0, fill=INK, stroke='none', rx=4)
        x += wdt
    y += 42
    for r in range(row + 1, rows):                # the second act, which was keyed and is not on the tape
        strip(y)
        s.rect(x0 - 12, y - 15, x1 - x0 + 24, 30, c='none', sw=0, fill=OX, stroke='none', op=0.86)
        if r == row + 2:
            s.text(W / 2, y + 5, 'ACT II', size=13, c=PAPER, anchor='middle', ls=6)
        y += 42
    s.save('p04-tape.svg')


# ------------------------------------------------------------------ V. the stacks
def stacks():
    rnd = random.Random(409)
    s = S(bg=PAPER)
    frame(s, 'SLEEPING STACKS  --  AISLE 409, BAY 14, AS FOUND')
    x0, x1 = 80, W - 80
    hx, hrow = 0, 4
    for row in range(8):
        yb = 215 + row * 128
        heavy = row == hrow
        x = x0 + 6
        spines = []
        while x < x1 - 20:
            w = rnd.uniform(11, 34); h = rnd.uniform(70, 108)
            spines.append([x, w, h]); x += w + rnd.uniform(0.5, 2.5)
        if heavy:
            k = len(spines) // 2 + 3
            hx = spines[k][0] + spines[k][1] / 2
        def sag(xx):
            return 30 * math.exp(-((xx - hx) / 170) ** 2) if heavy else 0
        s.path('M' + ' L'.join(f'{xx:.1f},{yb + sag(xx):.1f}' for xx in range(x0, x1 + 1, 8)), sw=2.4)
        s.path('M' + ' L'.join(f'{xx:.1f},{yb + 9 + sag(xx):.1f}' for xx in range(x0, x1 + 1, 8)), sw=0.8)
        for i, (x, w, h) in enumerate(spines):
            d = abs(x + w / 2 - hx) if (heavy or abs(row - hrow) == 1) else 9999
            stain = max(0, 1 - d / (150 if heavy else 80)) * (1 if heavy else 0.5)
            the = heavy and i == k
            lean = (4 if x < hx else -4) * math.exp(-((x - hx) / 90) ** 2) if heavy else rnd.uniform(-0.6, 0.6)
            yy = yb + sag(x + w / 2)
            fill = OCHRE if the else PAPER
            s.add(f'<g transform="rotate({lean:.2f} {x + w / 2:.1f} {yy:.1f})">')
            s.rect(x, yy - h, w, h, sw=1.0, fill=fill)
            if stain > 0 and not the:
                s.rect(x, yy - h, w, h, c='none', sw=0, stroke='none', fill=OCHRE, op=stain * 0.55)
            n = rnd.randint(1, 3)
            for j in range(n):
                s.line(x + 2, yy - h + 10 + j * 7, x + w - 2, yy - h + 10 + j * 7, sw=0.5, c=PAPER if the else INK)
            if rnd.random() < 0.3:
                for j in range(int(h / 9)):
                    s.line(x + w / 2, yy - h + 34 + j * 6, x + w / 2 + rnd.uniform(-3, 3), yy - h + 37 + j * 6, sw=0.4)
            s.add('</g>')
    s.text(hx, 215 + hrow * 128 + 62, 'nearly eleven pounds', size=15, font=SERIF, style='italic', anchor='middle', c=OX)
    s.save('p05-stacks.svg')


# ------------------------------------------------------------------ VII. the dry tank
def tank():
    rg = np.random.default_rng(14)
    s = S(bg=PAPER)
    frame(s, 'TANK 2  --  DRY BALLAST ONLY  --  SECTION ON THE CENTRE LINE')
    gx0, gx1, gy = 90, W - 90, 210
    tx0, tx1 = 330, 570
    ft = 21.0
    fy = gy + 10.5 * ft
    s.line(gx0, gy, tx0, gy, sw=2); s.line(tx1, gy, gx1, gy, sw=2)
    for xx in list(range(gx0, tx0 - 8, 16)) + list(range(tx1 + 12, gx1, 16)):
        s.line(xx, gy + 3, xx - 12, gy + 17, sw=0.6)
    s.poly([(tx0, gy), (tx0, fy), (tx1, fy), (tx1, gy)], sw=2.4)
    for r in (3.5, 7):
        s.line(tx0, gy + r * ft, tx0 + 34, gy + r * ft, sw=3)
    for i in range(5):
        s.line(tx0 + 60 + i * 5, fy - 52, tx0 + 60 + i * 5, fy - 34, sw=1)       # chalk tally
    s.line(tx0 + 56, fy - 38, tx0 + 84, fy - 48, sw=1)
    s.text((tx0 + tx1) / 2, fy + 20, 'floor: dry, swept Monday', size=13, font=SERIF, style='italic', anchor='middle')
    dx = tx0 - 60                                 # steel tape
    s.line(dx, gy, dx, fy, sw=1); s.line(dx - 7, gy, dx + 7, gy, sw=1); s.line(dx - 7, fy, dx + 7, fy, sw=1)
    s.text(dx - 12, (gy + fy) / 2, '10 FT 6 IN  BY CERTIFIED STEEL TAPE  =  3.2004 M', size=11.5, rot=-90, anchor='middle')
    lx = (tx0 + tx1) / 2 + 40                     # the line
    s.line(lx, gy - 60, lx, fy, c=OX, sw=1.6)
    s.rect(lx - 28, gy - 92, 56, 32, c=OX, sw=1.4); s.circ(lx, gy - 76, 9, c=OX, sw=1.2)
    s.text(lx + 38, gy - 70, 'SOUNDING LINE 14', size=11.5, c=OX)
    yd = 3 * ft * 0.268
    bot = gy + 38 * yd
    s.line(lx, fy, lx, bot, c=OX, sw=1.6, dash='5 5')
    for t in (5, 10, 20, 30, 38):
        yy = gy + t * yd
        s.line(lx - 8, yy, lx + 8, yy, c=OX, sw=1.4)
        s.text(lx + 16, yy + 4, f'{t} YD', size=11, c=OX)
    s.poly([(lx - 9, fy - 20), (lx + 9, fy - 20), (lx + 6, fy), (lx - 6, fy)], c=OX, sw=1.2, fill=PAPER)
    s.text(lx - 20, fy - 6, 'weight, as seen', size=12, font=SERIF, style='italic', anchor='end', c=OX)
    for i in range(1700):                         # ground the line passes through
        x = rg.uniform(gx0, gx1); y = rg.uniform(fy + 34, bot - 26)
        if abs(x - lx) < 9:
            continue
        a = rg.uniform(-0.3, 0.3)
        s.line(x, y, x + 12 * math.cos(a), y + 12 * math.sin(a), sw=0.45, op=0.55, c=PENCIL)
    for j in range(7):                            # water
        yy = bot + j * 9
        s.path('M' + ' L'.join(f'{xx},{yy + 2.4 * math.sin(xx / 17 + j):.1f}' for xx in range(gx0, gx1 + 1, 6)), c=LAKE, sw=1.0, op=0.9 - j * 0.09)
    for i in range(900):
        s.dot(rg.uniform(gx0, gx1), bot + 66 + abs(rg.normal(0, 12)), rg.uniform(0.6, 1.6), c=PENCIL, op=0.7)
    s.text(gx0, bot + 112, 'AT 38 YD THE TENSION WENT OUT OF THE SPOOL.  34.7472 M.  FACTOR 0.0921.', size=11.5)
    s.text(gx0, bot + 132, 'WEIGHT RETURNED DRY, WITH SILT ON ITS BASE THAT WAS NOT ON THE TANK FLOOR.', size=11.5)
    s.save('p07-tank.svg')


# ------------------------------------------------------------------ VIII. tally of 206
def tally():
    rnd = random.Random(311)
    s = S(bg=PAPER)
    frame(s, 'LOWER FORGE  --  MARKING-PLATE TALLY  --  206 PIECES')
    cols, cw, ch = 13, 58, 62
    x0, y0 = (W - cols * cw) / 2, 110
    missing = 57
    for n in range(1, 207):
        r, c = divmod(n - 1, cols)
        x, y = x0 + c * cw, y0 + r * ch
        if n == missing:
            s.rect(x + 6, y + 8, cw - 12, ch - 20, c=OX, sw=1.2, dash='4 4')
            for k in range(7):
                s.line(x + 9 + k * 6, y + ch - 15, x + 15 + k * 6, y + 11, c=LAKE, sw=0.9)
            s.text(x + cw / 2, y + ch - 2, 'L. COLLAR', size=7, anchor='middle', c=OX, ls=0)
            continue
        a = rnd.uniform(-5, 5)
        s.add(f'<g transform="rotate({a:.1f} {x + cw / 2:.1f} {y + ch / 2:.1f})">')
        kind = rnd.random()
        cx, cy = x + cw / 2, y + ch / 2 - 6
        if kind < 0.4:
            s.rect(cx - 17, cy - 8, 34, 16, sw=1.1, rx=7); s.circ(cx - 11, cy, 2.2, sw=0.8); s.circ(cx + 11, cy, 2.2, sw=0.8)
        elif kind < 0.65:
            s.poly([(cx - 18, cy + 9), (cx - 12, cy - 9), (cx + 12, cy - 9), (cx + 18, cy + 9)], close=True, sw=1.1)
        elif kind < 0.85:
            s.circ(cx, cy, 11, sw=1.1); s.circ(cx, cy, 4, sw=0.8)
        else:
            s.path(f'M{cx - 18},{cy + 6} q18,-22 36,0 l-5,4 q-13,-14 -26,0 z', sw=1.1)
        s.add('</g>')
        s.text(x + cw / 2, y + ch - 6, f'{n:03d}', size=8.5, anchor='middle', c=PENCIL, ls=0.5)
    s.text(x0, y0 + 16 * ch + 26, 'SIGNED FOR 206.  COUNTED 205.  ONE SHORT AT THE LEFT COLLAR; GAP SHIMMED, CHLORITE AND GREEN FIBRE.', size=10.5)
    s.save('p08-tally.svg')


# ------------------------------------------------------------------ IX. the reel
def score():
    rnd = random.Random(1872)
    s = S(bg=PAPER)
    frame(s, 'REEL 1872-TT1  --  "THE TWELVE PIPES"  --  TRANSCRIBED FROM THE TAPE')
    theme = [0]
    while len(theme) < 12:
        nx = theme[-1] + rnd.choice([-3, -2, -1, 1, 2, 3])
        if -4 <= nx <= 8 and nx not in theme[-2:]:
            theme.append(nx)
    fwd = []
    for rep in range(4):
        fwd += [t + [0, 2, -1, 1][rep] for t in theme]
    retro = fwd[::-1]
    x0, x1 = 100, W - 100
    for sys in range(4):                      # four systems of two bars (12 beats each)
        yt = 170 + sys * 235
        yb = yt + 96
        for yy0 in (yt, yb):
            for l in range(5):
                s.line(x0, yy0 + l * 10, x1 + (46 if sys == 3 else 0), yy0 + l * 10, sw=0.7)
        s.line(x0, yt, x0, yb + 40, sw=1.6)
        bw = (x1 - x0) / 12
        for bar in (6, 12):
            s.line(x0 + bar * bw, yt, x0 + bar * bw, yt + 40, sw=1); s.line(x0 + bar * bw, yb, x0 + bar * bw, yb + 40, sw=1)
        s.text(x0 - 14, yt + 25, 'F', size=13, anchor='end', c=OX); s.text(x0 - 14, yb + 25, 'R', size=13, anchor='end', c=LAKE)
        for b in range(12):
            i = sys * 12 + b
            for (seq, y0, col, shift) in ((fwd, yt, INK, 0), (retro, yb, LAKE, 1)):
                j = i - shift
                if j < 0:
                    continue
                n = seq[j]
                nx = x0 + (b + 0.5) * bw
                ny = y0 + 40 - (n + 2) * 5
                s.add(f'<ellipse cx="{nx:.1f}" cy="{ny:.1f}" rx="6.3" ry="4.6" transform="rotate(-20 {nx:.1f} {ny:.1f})" fill="{col}"/>')
                up = n < 4
                s.line(nx + (6 if up else -6), ny, nx + (6 if up else -6), ny + (-30 if up else 30), c=col, sw=1.1)
                if ny > y0 + 44 or ny < y0 - 4:
                    s.line(nx - 10, ny if (n % 2 == 0) else ny + 5, nx + 10, ny if (n % 2 == 0) else ny + 5, c=col, sw=0.7)
        if sys == 3:                           # the seventh beat
            nx = x1 + 26; n = retro[47]; ny = yb + 40 - (n + 2) * 5
            s.add(f'<ellipse cx="{nx:.1f}" cy="{ny:.1f}" rx="6.3" ry="4.6" transform="rotate(-20 {nx:.1f} {ny:.1f})" fill="{OX}"/>')
            s.line(nx + 6, ny, nx + 6, ny - 30, c=OX, sw=1.1)
            s.text(nx, yb + 70, '7', size=17, font=SERIF, c=OX, anchor='middle')
            s.text(x1 - 6, yt - 14, '48.0 s', size=11, anchor='end'); s.text(x1 + 46, yb - 12, '49.0 s', size=11, anchor='end', c=OX)
    yh = 1125
    s.path('M' + ' L'.join(f'{x},{yh + 13 * math.sin((x - x0) / 5.8):.1f}' for x in range(x0, x1 + 1, 2)), c=SLATE, sw=0.9)
    s.text(x0, yh + 44, 'UNDER THE HISS: 69.0 HZ, CONTINUOUS.  THE REEL WAS NOT RECORDED IN THE LOBBY, OR THE LOBBY ANSWERS IT.', size=10.5, c=SLATE)
    s.save('p09-score.svg')


# ------------------------------------------------------------------ X. the caller
def caller():
    rg = np.random.default_rng(20)
    s = S(bg=PAPER)
    frame(s)
    cx, top, hem = W / 2 + 30, 300, 1010

    def half(y):                                  # half-width of the coat at height y
        if y < top:
            return 0
        if y < top + 60:
            return 26 + 4 * math.sin((y - top) / 60 * math.pi)        # turned-up collar and head
        if y < top + 110:
            return 30 + (y - top - 60) / 50 * 78
        return 108 + (y - top - 110) / (hem - top - 110) * 42
    for y in range(70, 1150, 6):                  # the night, hatched; the coat is where it stops
        hw = half(y) if y < hem else 0
        jit = rg.uniform(-2, 2)
        if hw:
            s.line(60, y, cx - hw + jit, y, sw=0.75, op=0.82); s.line(cx + hw + jit, y, W - 60, y, sw=0.75, op=0.82)
        else:
            if y > hem + 16:
                x = 60
                while x < W - 60:
                    ln = rg.uniform(8, 60)
                    s.line(x, y, min(W - 60, x + ln), y, sw=0.75, op=0.6); x += ln + rg.uniform(3, 14)
            else:
                s.line(60, y, W - 60, y, sw=0.75, op=0.82)
    for i in range(-9, 10):                       # pleats
        xt = cx + i * 11.2
        pts = []
        for y in range(top + 112, hem, 14):
            k = half(y) / 108.0
            pts.append((cx + i * 11.2 * k, y))
        s.poly(pts, sw=0.8, c=INK, op=0.85)
    s.rect(cx - 13, top + 148, 26, 26, sw=1.1, fill=PAPER)        # the tag between the shoulder blades
    for k in range(4):
        s.line(cx - 13 + k * 8.6, top + 148, cx - 13 + k * 8.6, top + 146, sw=0.6)
    for xx in (60, W / 3 + 10, 2 * W / 3 - 10, W - 60):            # the outer glass
        s.line(xx, 70, xx, 1150, sw=2.2, c=PAPER); s.line(xx, 70, xx, 1150, sw=0.9)
    for i in range(7):                            # pilot lamp over the rear arch, red to amber
        t = i / 6
        col = '#%02x%02x%02x' % (int(139 + (201 - 139) * t), int(42 + (150 - 42) * t), int(32 + (60 - 32) * t))
        s.circ(250 + i * 66, 1195, 13, c=INK, sw=0.8, fill=col)
    s.text(W / 2, 1232, '14 DEC          18 DEC          20 DEC, 22:00          01:00', size=10.5, anchor='middle', c=PENCIL)
    s.save('p10-caller.svg')


# ------------------------------------------------------------------ XI. the field book
def fieldbook():
    s = S(bg='#efe6d2')
    for y in range(120, H - 60, 34):
        s.line(60, y, W - 60, y, c='#9db0b8', sw=0.6)
    s.line(150, 60, 150, H - 60, c=OX, sw=0.7, op=0.6)
    s.text(170, 104, 'Sec. 16, T5N R8W.   19 Feb. 1892.   Clear, 18 deg.', size=21, font=SERIF, style='italic')
    k = 4.6
    ox, oy = 250, 190
    p = [(ox, oy)]
    for dx, dy in [(80, 0), (0, 80), (-77.12, 0), (0, -77.84)]:
        p.append((p[-1][0] + dx * k, p[-1][1] + dy * k))
    s.poly(p, sw=1.6)
    for i, (a, b) in enumerate(zip(p[:-1], p[1:])):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        lab = ['E 80.00', 'S 80.00', 'W 77.12', 'N 77.84'][i]
        off = [(0, -10), (14, 0), (0, 26), (-14, 0)][i]
        s.text(mx + off[0], my + off[1], lab, size=19, font=SERIF, style='italic', anchor=['middle', 'start', 'middle', 'end'][i])
    for i, (x, y) in enumerate(p[:4]):
        s.rect(x - 6, y - 6, 12, 12, sw=1.4, fill='#efe6d2')
        s.text(x + [-14, 14, 14, -14][i], y + [-10, -10, 26, 26][i], f'Mon. {[4, 1, 2, 3][i]}', size=16, font=SERIF, anchor=['end', 'start', 'start', 'end'][i])
    s.circ(p[4][0], p[4][1], 5, c=OX, sw=1.5)
    s.line(p[4][0], p[4][1], p[0][0], p[0][1], c=OX, sw=1.4, dash='3 3')
    s.circ(ox + 40 * k, oy + 40 * k, 6, c=OX, sw=1.5); s.text(ox + 40 * k + 14, oy + 40 * k + 6, 'pin', size=18, font=SERIF, style='italic', c=OX)
    # the closure triangle, enlarged, with the squares on its sides
    u = 62.0
    tx, ty = 330, 1060
    a, b = (tx, ty), (tx + 2.88 * u, ty)
    c = (tx + 2.88 * u, ty - 2.16 * u)
    s.poly([a, b, c], close=True, c=OX, sw=2)
    s.poly([a, b, (b[0], b[1] + 2.88 * u), (a[0], a[1] + 2.88 * u)], close=True, sw=0.8, dash='4 3')
    s.poly([b, c, (c[0] + 2.16 * u, c[1]), (b[0] + 2.16 * u, b[1])], close=True, sw=0.8, dash='4 3')
    nx, ny = -(c[1] - a[1]), (c[0] - a[0])
    ln = math.hypot(nx, ny); nx, ny = -nx / ln * 3.6 * u, -ny / ln * 3.6 * u
    s.poly([a, c, (c[0] + nx, c[1] + ny), (a[0] + nx, a[1] + ny)], close=True, sw=0.8, dash='4 3')
    s.text((a[0] + b[0]) / 2, ty + 2.88 * u / 2 + 6, '2.88', size=20, font=SERIF, style='italic', anchor='middle')
    s.text((a[0] + b[0]) / 2, ty + 2.88 * u / 2 + 30, '8.2944', size=15, font=SERIF, anchor='middle', c=PENCIL)
    s.text(b[0] + 2.16 * u / 2, ty - 2.16 * u / 2 + 2, '2.16', size=20, font=SERIF, style='italic', anchor='middle')
    s.text(b[0] + 2.16 * u / 2, ty - 2.16 * u / 2 + 26, '4.6656', size=15, font=SERIF, anchor='middle', c=PENCIL)
    s.text(tx + 30, ty - 190, '3.60', size=24, font=SERIF, style='italic', anchor='middle', c=OX)
    s.text(tx + 30, ty - 164, '12.96', size=15, font=SERIF, anchor='middle', c=PENCIL)
    s.text(170, 640, 'Run of 8 Feb.  agrees.     Run of 11 Feb.  agrees.', size=20, font=SERIF, style='italic')
    s.text(170, 674, 'Error falls inward, toward the pin.  Needle will not settle near Mon. 3.', size=20, font=SERIF, style='italic')
    s.text(170, 708, 'Fifth signature:', size=20, font=SERIF, style='italic')
    s.line(320, 712, 640, 712, sw=0.9)
    s.save('p11-fieldbook.svg')


# ------------------------------------------------------------------ XII. the beam
def beam():
    s = S(bg=PAPER)
    frame(s, 'STORES BEAM SCALE  --  CLASS: FOUR POUNDS AND UNDER')
    cx, py = W / 2, 430
    s.poly([(cx - 70, 1000), (cx - 18, py + 20), (cx + 18, py + 20), (cx + 70, 1000)], close=True, sw=1.6)
    s.rect(cx - 150, 1000, 300, 26, sw=1.6)
    s.line(cx - 330, py, cx + 330, py, sw=5)
    s.poly([(cx - 12, py + 20), (cx, py - 6), (cx + 12, py + 20)], close=True, sw=1.4, fill=INK)
    for i in range(0, 34):
        xx = cx + 20 + i * 9
        s.line(xx, py - 3, xx, py - (15 if i % 4 == 0 else 9), sw=0.8)
    s.rect(cx + 312, py - 18, 20, 36, sw=1.4, fill=OX, c=OX)
    s.text(cx + 322, py - 30, 'both poises, at the stop', size=14, font=SERIF, style='italic', anchor='end', c=OX)
    for side, xx in ((-1, cx - 300), (1, cx + 240)):
        s.line(xx, py, xx - 70, py + 250, sw=0.9); s.line(xx, py, xx + 70, py + 250, sw=0.9)
        s.path(f'M{xx - 84},{py + 250} q84,40 168,0', sw=1.8)
    lx = cx - 300
    s.path(f'M{lx - 62},{py + 246} q60,-14 124,-2', c=INK, sw=1.2)
    s.text(lx, py + 316, 'one leaf', size=18, font=SERIF, style='italic', anchor='middle')
    s.text(lx, py + 340, '1953-B', size=13, anchor='middle', c=OX)
    rx = cx + 240
    yb = py + 262
    for i, (w, h) in enumerate([(54, 30)] * 2):
        s.rect(rx - 60 + i * 64, yb - h - 14, w, h, sw=1.3)
        s.text(rx - 33 + i * 64, yb - 24, '1 LB', size=11, anchor='middle')
    s.text(rx, py + 316, 'tares, brass', size=18, font=SERIF, style='italic', anchor='middle')
    wts = [60, 41, 38, 36, 43, 40, 28, 29, 25, 25, 28, 63, 13, 14, 15, 14]
    x0, y0, sc = 110, 1180, 1.0
    x = x0
    for i, w in enumerate(wts):
        s.rect(x, y0 - 34, w * sc, 34, sw=0.9); s.text(x + w * sc / 2, y0 - 12, str(i + 1), size=9, anchor='middle', ls=0)
        x += w * sc
    s.rect(x, y0 - 34, 152 * sc, 34, c=OX, sw=1.1, dash='4 3'); s.text(x + 76, y0 - 12, '17', size=10, anchor='middle', c=OX)
    s.text(x0, y0 + 20, 'SIXTEEN RECORDS: 32 LB 0 OZ', size=10.5); s.text(x + 152, y0 + 20, 'AS BOUND: 41 LB 8 OZ', size=10.5, anchor='end', c=OX)
    s.save('p12-beam.svg')


# ------------------------------------------------------------------ XIV. doors
def doors():
    rnd = random.Random(44)
    s = S(bg=PAPER)
    frame(s, 'UNCLAIMED DOORS  --  ELEVATIONS, TO ONE SCALE')
    cw, ch = 190, 265
    x0, y0 = (W - 4 * cw) / 2, 100
    names = ['ALABASTER', 'CHALK', 'FORTY-FOUR', '', 'IRON PIN', 'PAVILION', 'FORTY-ONE', 'WAITING', '14-C', '409', 'EXIT 47', 'SUITE 400', 'TANK 2', 'GALLERY 9', 'COUNTER 2', '1953-B']
    for i in range(16):
        r, c = divmod(i, 4)
        x, y = x0 + c * cw + 38, y0 + r * ch + 34
        w, h = 114, 190
        if i == 3:                                 # the entry omitted
            s.rect(x, y, w, h, c=PENCIL, sw=0.8, dash='2 5')
            continue
        kind = rnd.choice(['panel', 'arch', 'plank', 'steel']) if i != 2 else 'steel'
        if kind == 'arch':
            s.path(f'M{x},{y + h} L{x},{y + 50} A{w / 2},{50} 0 0 1 {x + w},{y + 50} L{x + w},{y + h} Z', sw=1.5)
            s.path(f'M{x + 12},{y + h} L{x + 12},{y + 56} A{w / 2 - 12},{40} 0 0 1 {x + w - 12},{y + 56} L{x + w - 12},{y + h}', sw=0.8)
        else:
            s.rect(x, y, w, h, sw=1.5)
        if kind == 'panel':
            rows, cols = rnd.choice([(2, 2), (3, 2), (2, 1), (4, 2)]), 0
            pr, pc = rows
            for a in range(pr):
                for b in range(pc):
                    s.rect(x + 12 + b * (w - 24) / pc + 3, y + 12 + a * (h - 24) / pr + 3, (w - 24) / pc - 6, (h - 24) / pr - 6, sw=0.8)
        elif kind == 'plank':
            for a in range(1, 6):
                s.line(x + a * w / 6, y, x + a * w / 6, y + h, sw=0.7)
            s.line(x, y + 40, x + w, y + 60, sw=1); s.line(x, y + h - 60, x + w, y + h - 40, sw=1)
        elif kind == 'steel':
            for a in range(9):
                s.dot(x + 8, y + 12 + a * 21, 1.4); s.dot(x + w - 8, y + 12 + a * 21, 1.4)
            s.rect(x + 14, y + 20, w - 28, 54, sw=0.8)
        hs = rnd.choice([1, 0])
        s.circ(x + (w - 16 if hs else 16), y + h * 0.56, 4.5, sw=1.1)
        if i == 2:
            s.rect(x + 6, y - 28, w - 12, 20, c=LAKE, sw=1.2, fill='#cfe3d6')
            s.text(x + w / 2, y - 14, 'NOT AN EXIT', size=9, anchor='middle', c=LAKE, ls=1)
        s.line(x - 14, y + h, x + w + 14, y + h, sw=1.1)
        s.text(x + w / 2, y + h + 20, names[i], size=10, anchor='middle', c=PENCIL, ls=1.5)
    s.save('p14-doors.svg')


# ------------------------------------------------------------------ XVI. boring logs
def borings():
    rg = np.random.default_rng(1872)
    s = S(bg=PAPER)
    frame(s, 'W. HARRIS, FOR THE WORKS, 1872  --  BORINGS WEST OF THE WORKS')
    y0, depth, ft = 190, 52, 16.0
    cols = [('1', 6, 0, 3), ('2', 14, 0, 2), ('3', 23, 0, 4), ('4', 37, 0, 3), ('5', 52, 0, 2), ('SEC. 15', None, 20, 5), ('SEC. 9', None, 22, 4)]
    x = 120
    for name, ch, drift, clay in cols:
        w = 62
        if name == 'SEC. 15':
            x += 46
            s.line(x - 23, y0 - 60, x - 23, y0 + depth * ft + 20, sw=0.8, dash='3 5')
        s.rect(x, y0, w, depth * ft, sw=1.4)
        yy = y0
        if drift:
            hgt = drift * ft
            for _ in range(int(hgt * 0.9)):
                s.circ(x + rg.uniform(5, w - 5), yy + rg.uniform(4, hgt - 4), rg.uniform(1.2, 4.2), sw=0.6)
            yy += hgt; s.line(x, yy, x + w, yy, sw=1)
        hgt = clay * ft
        for j in range(int(hgt / 6)):
            for k in range(5):
                s.line(x + 5 + k * 11 + (j % 2) * 5, yy + 4 + j * 6, x + 11 + k * 11 + (j % 2) * 5, yy + 4 + j * 6, c=OX, sw=0.8)
        yy += hgt; s.line(x, yy, x + w, yy, sw=1)
        j = 0
        while yy + j * 13 < y0 + depth * ft:
            ly = yy + j * 13
            s.line(x, ly, x + w, ly, sw=0.5)
            for k in range(4):
                bx = x + k * 21 + (10 if j % 2 else 0)
                if x < bx < x + w and ly + 13 <= y0 + depth * ft:
                    s.line(bx, ly, bx, ly + 13, sw=0.5)
            j += 1
        if not drift:
            for _ in range(rg.integers(3, 8)):
                gx, gyy = x + rg.uniform(6, w - 10), rg.uniform(yy + 30, y0 + depth * ft - 12)
                s.rect(gx, gyy, 5, 5, fill=INK, sw=0)
        s.text(x + w / 2, y0 - 34, f'No. {name}' if ch else name, size=12, anchor='middle')
        if ch:
            s.text(x + w / 2, y0 - 16, f'{ch} ch W', size=10, anchor='middle', c=PENCIL)
        s.text(x + w / 2, y0 + depth * ft + 22, 'DRIFT: NIL' if not drift else f'DRIFT {drift} FT', size=9.5, anchor='middle', c=OX if not drift else INK, ls=0.3)
        x += w + 32
    for d in range(0, depth + 1, 10):
        s.line(96, y0 + d * ft, 112, y0 + d * ft, sw=0.8); s.text(90, y0 + d * ft + 4, f'{d}', size=10, anchor='end')
    s.text(84, y0 - 16, 'FT', size=10, anchor='end')
    ly = y0 + depth * ft + 74
    s.circ(130, ly, 4, sw=0.6); s.text(144, ly + 4, 'drift: gravel, cobble', size=14, font=SERIF, style='italic')
    s.line(330, ly, 346, ly, c=OX, sw=1); s.text(356, ly + 4, 'red clay', size=14, font=SERIF, style='italic')
    s.rect(450, ly - 6, 16, 12, sw=0.6); s.text(476, ly + 4, 'dolomite', size=14, font=SERIF, style='italic')
    s.rect(580, ly - 3, 5, 5, fill=INK, sw=0); s.text(596, ly + 4, 'a little lead ore', size=14, font=SERIF, style='italic')
    s.text(120, ly + 50, 'Low banks west of No. 5 entered by the county as wash.  We do not cut there.', size=17, font=SERIF, style='italic')
    s.save('p16-borings.svg')


# ------------------------------------------------------------------ stemma
def stemma():
    s = S(w=900, h=980, bg=PAPER)
    N = {'O': (450, 70, 'Ω'), 'a': (300, 190, 'α'), 'b': (600, 190, 'β'), 'g': (190, 330, 'γ'), 'd': (410, 330, 'δ'), 'e': (640, 330, 'ε'),
         'z': (760, 330, 'ζ')}
    lab = {'O': 'an evening, not dated', 'a': 'the pamphlet of 1898', 'b': 'county and ironworks paper', 'g': 'the notebook, 2004',
           'd': 'hearsay', 'e': 'the cabinets, 1953', 'z': 'the octavo, 1931'}
    def edge(p, q, dash=None, c=INK):
        s.line(N[p][0], N[p][1] + 16, N[q][0], N[q][1] - 22, c=c, sw=1.1, dash=dash)
    for p, q in [('O', 'a'), ('O', 'b'), ('a', 'g'), ('a', 'd'), ('b', 'e'), ('b', 'z')]:
        edge(p, q)
    recs = {'g': [1], 'd': [3, 4, 5, 6], 'e': [7, 8, 9, 10, 11], 'z': [12, 13, 14, 15, 16]}
    pos = {}
    xs = np.linspace(70, 830, 16)
    order = [1, 3, 4, 5, 6, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    for i, r in enumerate(order):
        pos[r] = (xs[i], 520)
    for k, rs in recs.items():
        for r in rs:
            s.line(N[k][0], N[k][1] + 16, pos[r][0], pos[r][1] - 20, sw=0.8)
    s.line(N['b'][0], N['b'][1] + 16, pos[2][0], pos[2][1] - 20, sw=0.8)
    for r, (x, y) in pos.items():
        s.circ(x, y, 15, sw=1.1, fill=PAPER); s.text(x, y + 5, str(r), size=13, anchor='middle', ls=0)
    for k, (x, y, g) in N.items():
        s.circ(x, y, 19, sw=1.4, fill=PAPER); s.text(x, y + 8, g, size=24, font=SERIF, anchor='middle')
        s.text(x + 28, y + 5, lab[k], size=15, font=SERIF, style='italic')
    for r in range(1, 17):                       # the two impressions
        s.line(pos[r][0], pos[r][1] + 15, 330, 660, sw=0.5, op=0.7)
    s.rect(250, 660, 160, 44, sw=1.4, fill=PAPER); s.text(330, 688, 'FIRST IMPRESSION', size=11.5, anchor='middle')
    s.line(330, 704, 450, 780, sw=1.2)
    s.rect(350, 780, 200, 44, sw=1.8, fill=PAPER); s.text(450, 808, 'PRESENT IMPRESSION', size=11.5, anchor='middle')
    s.circ(690, 660, 15, c=OX, sw=1.2, fill=PAPER); s.text(690, 665, '17', size=13, anchor='middle', c=OX, ls=0)
    s.line(676, 668, 550, 790, c=OX, sw=1.1, dash='5 4')
    s.text(712, 665, 'no exemplar', size=15, font=SERIF, style='italic', c=OX)
    # the loop: the present volume as the source of its own source
    s.path('M350,802 C40,820 20,300 276,196', c=OX, sw=1.2, dash='5 4')
    s.poly([(262, 190), (278, 196), (268, 210)], c=OX, sw=1.2)
    s.text(56, 600, 'sewn in', size=15, font=SERIF, style='italic', c=OX, rot=-78)
    s.text(450, 900, 'Solid lines: copied from.   Broken lines: not sustained.', size=16, font=SERIF, style='italic', anchor='middle', c=PENCIL)
    s.save('stemma.svg')


# ------------------------------------------------------------------ the plan that no plan could hold
def plan():
    rnd = random.Random(16)
    s = S(w=900, h=980, bg=PAPER)
    rooms = []
    grid = [(c, r) for r in range(5) for c in range(4)]
    for (c, r) in grid:
        if rnd.random() < 0.18:
            continue
        w, h = rnd.choice([150, 170, 190]), rnd.choice([120, 140, 150])
        x, y = 70 + c * 200 + rnd.uniform(-8, 8), 70 + r * 172 + rnd.uniform(-6, 6)
        rooms.append((x, y, w, h))
        s.rect(x, y, w, h, sw=1.8)
        if rnd.random() < 0.5:
            for k in range(1, 6):
                s.line(x + k * w / 6, y + h - 16, x + k * w / 6, y + h, sw=0.6)
    for i, (x, y, w, h) in enumerate(rooms):
        s.text(x + 8, y + 18, f'{i + 1:02d}', size=11, c=PENCIL)
    pairs = set()
    n = 0
    while n < 16:
        a, b = rnd.sample(range(len(rooms)), 2)
        if (a, b) in pairs or (b, a) in pairs:
            continue
        xa, ya, wa, ha = rooms[a]; xb, yb, wb, hb = rooms[b]
        if abs(xa - xb) + abs(ya - yb) < 260:
            continue
        pairs.add((a, b)); n += 1
        p = (xa + wa * rnd.uniform(0.3, 0.7), ya + ha * rnd.uniform(0.3, 0.7))
        q = (xb + wb * rnd.uniform(0.3, 0.7), yb + hb * rnd.uniform(0.3, 0.7))
        mx, my = (p[0] + q[0]) / 2 + rnd.uniform(-90, 90), (p[1] + q[1]) / 2 + rnd.uniform(-90, 90)
        s.path(f'M{p[0]:.0f},{p[1]:.0f} Q{mx:.0f},{my:.0f} {q[0]:.0f},{q[1]:.0f}', c=OX, sw=1.1, dash='6 4')
        s.dot(p[0], p[1], 3.2, OX); s.dot(q[0], q[1], 3.2, OX)
        s.circ(mx * 0.5 + (p[0] + q[0]) * 0.25, my * 0.5 + (p[1] + q[1]) * 0.25, 9, c=OX, sw=0.8, fill=PAPER)
        s.text(mx * 0.5 + (p[0] + q[0]) * 0.25, my * 0.5 + (p[1] + q[1]) * 0.25 + 3.5, str(n), size=9, anchor='middle', c=OX, ls=0)
    s.save('plan.svg')


# ------------------------------------------------------------------ XVII. the plate withheld
def withheld():
    s = S(bg=PAPER)
    frame(s)
    for y in range(60, H - 40, 9):
        s.line(40, y, W - 40, y, c='#d9ccb0', sw=0.4)
    rg = np.random.default_rng(17)
    for _ in range(2200):
        x = rg.uniform(50, W - 50); d = abs(rg.normal(0, 13))
        s.dot(x, H - 50 - d - 10 * math.sin(x / 70) ** 2, rg.uniform(0.5, 1.6), c=rg.choice(['#b8860b', '#c99a1e', '#9a7412']), op=rg.uniform(0.3, 0.9))
    cx, cy = W / 2, H / 2 - 40
    s.rect(cx - 190, cy - 250, 380, 500, sw=1.6, fill='#e9e2d3')
    s.line(cx - 190, cy, cx + 190, cy, c=PENCIL, sw=5, op=0.55); s.line(cx, cy - 250, cx, cy + 250, c=PENCIL, sw=5, op=0.55)
    s.path(f'M{cx},{cy} q-26,-22 -44,-6 q-10,16 44,6 q26,-22 44,-6 q10,16 -44,6', c=PENCIL, sw=3, op=0.7)
    s.rect(cx - 150, cy - 210, 150, 52, sw=0.9)
    s.save('p17-withheld.svg')


def pin():
    s = S(w=300, h=300)
    k = 3.0
    p = [(30, 30)]
    for dx, dy in [(80, 0), (0, 80), (-77.12 + 2.88 * -2, 0), (0, -77.84 + 2.16 * 2)]:
        p.append((p[-1][0] + dx * k, p[-1][1] + dy * k))
    s.poly(p, c=INK, sw=2.2)
    s.line(p[-1][0], p[-1][1], p[0][0], p[0][1], c=OX, sw=2, dash='5 5')
    for q in p[:4]:
        s.rect(q[0] - 7, q[1] - 7, 14, 14, sw=2, fill=PAPER)
    s.circ(150, 150, 9, c=OX, sw=2.4); s.dot(150, 150, 3, OX)
    s.save('pin.svg')


if __name__ == '__main__':
    import traceback
    for f in (leaf, plat, hotel, tape, stacks, tank, tally, score, caller, fieldbook, beam, doors, borings, stemma, plan, withheld, pin):
        try:
            f()
        except Exception:
            print('FAILED', f.__name__); traceback.print_exc(limit=-1)
