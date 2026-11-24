#!/usr/bin/env python3
"""Tonal plates for the second impression: the deposit, the cover board, the
neon, the contact sheet and the sand figures. Fixed seeds. Output: art/*.png"""
import math, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

A = pathlib.Path(__file__).resolve().parent
F = '/usr/share/fonts/truetype/'
MONO = F + 'ibm-plex/IBMPlexMono-Regular.ttf'
COND = F + 'ibm-plex/IBMPlexSansCondensed-Bold.ttf'
PAPER = (244, 237, 223)
INK = (28, 26, 23)
OX = (139, 42, 32)


def font(p, s): return ImageFont.truetype(p, s)


# ------------------------------------------------------------------ the deposit
def dust():
    w, h = 1100, 1700
    for k in range(1, 6):
        rg = np.random.default_rng(100 + k)
        im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        n = 500 * k * k
        xs = rg.uniform(0, w * 2, n)
        ridge = 10 + 9 * k + 16 * np.sin(xs / 190.0 + k) ** 2 + 10 * np.sin(xs / 57.0) ** 2
        ys = h * 2 - 60 - np.abs(rg.normal(0, 1, n)) * ridge
        for x, y in zip(xs, ys):
            r = rg.uniform(0.8, 2.6)
            c = [(184, 134, 11), (201, 154, 30), (154, 116, 18), (214, 172, 60)][rg.integers(0, 4)]
            d.ellipse([x - r, y - r, x + r, y + r], fill=c + (int(rg.uniform(70, 215)),))
        im.resize((w * 2 // 3, h * 2 // 3), Image.LANCZOS).save(A / f'dust-{k}.png')
    print('dust')


# ------------------------------------------------------------------ the board
def field(n=260, seed=16):
    rg = np.random.default_rng(seed)
    y, x = np.mgrid[0:1:n * 1j, 0:1:n * 1j]
    z = np.zeros_like(x)
    for k in range(1, 7):
        for _ in range(3):
            fx, fy = rg.normal(0, k * 1.5, 2)
            z += np.sin(2 * math.pi * (fx * x + fy * y) + rg.uniform(0, 6.28)) / (k ** 1.35)
    return x, y, z


def cover():
    import contourpy
    w, h, ss = 1100, 1700, 2
    im = Image.new('RGB', (w * ss, h * ss), (22, 21, 19))
    d = ImageDraw.Draw(im)
    x, y, z = field(seed=53)
    cx, cy = 0.5, 0.67
    z = z + 2.6 * np.exp(-(((x - cx) ** 2 + ((y - cy) * 1.55) ** 2) / 0.03))
    cg = contourpy.contour_generator(x, y, z)
    for i, lv in enumerate(np.linspace(z.min(), z.max(), 34)[1:-1]):
        for ln in cg.lines(lv):
            pts = [(px * w * ss, py * h * ss) for px, py in ln]
            d.line(pts, fill=(58, 52, 42) if i % 5 else (84, 72, 52), width=2 if i % 5 else 3)
    # the traverse that will not close, run until there is no section left
    L = 640.0 * ss
    a, b = 2.88 / 80 * L * 1.25, 2.16 / 80 * L * 1.25
    px, py = (w * ss - L) / 2 + 14 * ss, cy * h * ss - L / 2 - 20 * ss
    pts = [(px, py)]
    legs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    i = 0
    while True:
        k = i // 2
        ln = L - (a if i % 2 == 0 else b) * k
        if ln <= 6:
            break
        dx, dy = legs[i % 4]
        px, py = px + dx * ln, py + dy * ln
        pts.append((px, py)); i += 1
    for j in range(len(pts) - 1):
        t = j / (len(pts) - 1)
        col = (int(196 - 70 * t), int(150 - 62 * t), int(70 - 30 * t))
        d.line([pts[j], pts[j + 1]], fill=col, width=3)
    for q in pts[:4]:
        d.rectangle([q[0] - 9, q[1] - 9, q[0] + 9, q[1] + 9], outline=(232, 222, 200), fill=(22, 21, 19), width=3)
    im = im.resize((w, h), Image.LANCZOS)
    glow = Image.new('RGB', (w, h), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    ex, ey = pts[-1][0] / ss, pts[-1][1] / ss
    g.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], fill=(255, 196, 96))
    glow = glow.filter(ImageFilter.GaussianBlur(46))
    im = ImageChops.add(im, glow)
    d = ImageDraw.Draw(im)
    d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(255, 232, 170))
    im.save(A / 'cover.jpg', quality=90)
    print('cover')


# ------------------------------------------------------------------ VI. the sign
def neon():
    w, h = 1350, 1890
    rg = np.random.default_rng(47)
    tube = Image.new('L', (w, h), 0)
    dead = Image.new('L', (w, h), 0)
    lines = [("VARGA'S", 250, 260), ('PALACE OF', 250, 520), ('WONDERS', 250, 780)]
    for txt, size, y in lines:
        f = font(COND, size)
        tw = sum(f.getlength(c) for c in txt) + 14 * (len(txt) - 1)
        x = (w - tw) / 2
        for ch in txt:
            layer = Image.new('L', (w, h), 0)
            ld = ImageDraw.Draw(layer)
            ld.text((x, y), ch, font=f, fill=255, stroke_width=7, stroke_fill=255)
            ld.text((x, y), ch, font=f, fill=0, stroke_width=1, stroke_fill=0)
            if txt == 'WONDERS' and ch == 'W':
                dead = ImageChops.lighter(dead, layer)
            else:
                tube = ImageChops.lighter(tube, layer)
            x += f.getlength(ch) + 14
    t = np.asarray(tube, float) / 255
    g1 = np.asarray(tube.filter(ImageFilter.GaussianBlur(9)), float) / 255
    g2 = np.asarray(tube.filter(ImageFilter.GaussianBlur(46)), float) / 255
    dd = np.asarray(dead, float) / 255
    img = np.zeros((h, w, 3))
    img[:] = (0.07, 0.066, 0.06)
    yy = np.arange(h)[:, None] / h
    xx = np.arange(w)[None, :] / w
    ridge = 0.11 + 0.035 * np.sin(xx * 7.0) + 0.02 * np.sin(xx * 23.0 + 1)
    sky = (yy < ridge)
    img[np.broadcast_to(sky, (h, w))] = (0.10, 0.098, 0.095)
    red = np.array([1.0, 0.23, 0.16])
    img += g2[..., None] * red * 0.85 + g1[..., None] * red * 0.9
    img += t[..., None] * np.array([1.0, 0.86, 0.80])
    img += dd[..., None] * np.array([0.16, 0.15, 0.14])
    # wet blacktop: the sign upside down, rippled, and one reflection that is not of the sign
    horizon = 1130
    src = np.clip(img[250:horizon], 0, 1)[::-1]
    refl = np.zeros((h - horizon, w, 3))
    for r in range(h - horizon):
        sr = min(src.shape[0] - 1, int(r * 1.18))
        shift = int(9 * math.sin(r / 9.0) + 5 * math.sin(r / 3.1) + rg.normal(0, 1.2))
        refl[r] = np.roll(src[sr], shift, axis=0) * (0.5 * math.exp(-r / 520.0))
    wing = Image.new('L', (w, h - horizon), 0)
    wd = ImageDraw.Draw(wing)
    cxw, cyw = 300, 190
    for s_ in (-1, 1):
        wd.line([(cxw + 90, cyw), (cxw + 20, cyw + s_ * 30), (cxw - 60, cyw + s_ * 110), (cxw - 170, cyw + s_ * 150)], fill=255, width=16, joint='curve')
    wd.line([(cxw + 150, cyw), (cxw - 40, cyw)], fill=255, width=20)
    wing = np.asarray(wing.filter(ImageFilter.GaussianBlur(7)), float) / 255
    for r in range(h - horizon):
        wing[r] = np.roll(wing[r], int(7 * math.sin(r / 8.0)))
    refl += wing[..., None] * np.array([0.95, 0.78, 0.25]) * 0.62
    img[horizon:] = refl + np.array([0.035, 0.034, 0.032])
    img[horizon - 3:horizon] = (0.02, 0.02, 0.02)
    for _ in range(2600):                       # sleet
        x0, y0 = rg.uniform(0, w), rg.uniform(0, horizon)
        ln = rg.uniform(10, 34)
        for q in range(int(ln)):
            xi, yi = int(x0 - q * 0.25), int(y0 + q)
            if 0 <= xi < w and 0 <= yi < horizon:
                img[yi, xi] += 0.07
    img += rg.normal(0, 0.012, img.shape)
    Image.fromarray((np.clip(img, 0, 1) * 255).astype('uint8')).save(A / 'p06-neon.jpg', quality=90)
    print('neon')


# ------------------------------------------------------------------ XIII. the contact sheet
def corridor(n, L, rg, taken=True):
    if not taken:
        fr = rg.normal(0.035, 0.012, (n, n))
        return np.clip(fr, 0, 1)
    f = n * 5.2
    wd, ht, eye = 9.0, 10.0, 5.2
    ys, xs = np.mgrid[0:n, 0:n]
    x = xs - n / 2 + 0.5
    y = ys - n * 0.52 + 0.5
    big = 1e9
    zf = np.where(y > 0, eye * f / np.maximum(y, 1e-6), big)
    zc = np.where(y < 0, (ht - eye) * f / np.maximum(-y, 1e-6), big)
    zr = np.where(x > 0, (wd / 2) * f / np.maximum(x, 1e-6), big)
    zl = np.where(x < 0, (wd / 2) * f / np.maximum(-x, 1e-6), big)
    z = np.minimum(np.minimum(zf, zc), np.minimum(zr, zl))
    surf = np.select([z >= L, z == zf, z == zc, z == zr], [0, 1, 2, 3], default=4)   # end, floor, ceiling, right, left
    z = np.minimum(z, L)
    lamp = 1.0 / (1.0 + ((L - z) / 30.0) ** 2)
    near = 1.0 / (1.0 + (z / 60.0) ** 2)
    img = 0.06 + 0.5 * lamp + 0.30 * near
    wx = x * z / f                                   # lateral position on floor/ceiling
    wy = y * z / f
    floor = surf == 1
    tile = ((np.floor(z / 1.5) + np.floor((wx + 40) / 0.75)) % 2)
    img = np.where(floor, img * (0.72 + 0.2 * tile), img)
    for zs in (L - 108, L - 72):                     # scars where partitions were struck
        img = np.where(floor & (np.abs(z - zs) < 0.7), img + 0.25, img)
    right = surf == 3
    door = right & ((z % 24) < 5) & (wy > -3.2)
    img = np.where(door, img * 0.45, img)
    left = surf == 4
    win = left & (z > L - 62) & (z < L - 48) & (wy > -3.4) & (wy < 2.2)
    img = np.where(win, 0.30 + 0.10 * np.sin(wy * 3) + np.where(wy > 1.7, 0.35, 0), img)       # green to the sill; silt line
    lou = left & (z > L - 42) & (z < L - 30) & (wy > -3.4) & (wy < 2.2)
    img = np.where(lou, np.where(((wy * 2.2) % 1) < 0.55, 0.12, 0.62 - 0.4 * (np.floor((wy + 3.4) * 2.2 / 1) == 2)), img)
    lime = left & (z > L - 24)
    img = np.where(lime, img * (0.6 + 0.5 * rg.random((n, n))), img)
    end = surf == 0
    img = np.where(end, 0.34 + 0.25 * np.exp(-((wx) ** 2 + (wy + 3.6) ** 2) / 3.0), img)
    arch = end & (np.abs(wx) < 2.2) & (wy > -3.0)
    img = np.where(arch, 0.16, img)                  # the arch beyond the bulkhead
    bulb = end & ((wx) ** 2 + (wy + 3.9) ** 2 < 0.22)
    img = np.where(bulb, 1.0, img)
    img = img * (1 - 0.35 * ((x / n) ** 2 + (y / n) ** 2) * 4)
    img += rg.normal(0, 0.035, (n, n))
    return np.clip(img, 0, 1)


def contact():
    rg = np.random.default_rng(216)
    w, h = 1350, 1890
    sheet = np.full((h, w), 0.045)
    n, gx, gy = 380, 48, 62
    x0 = (w - 3 * n - 2 * gx) / 2
    y0 = 86
    im = None
    for i in range(12):
        r, c = divmod(i, 3)
        fr = corridor(n, 216 - 6 * i, rg, taken=(i < 11))
        xx, yy = int(x0 + c * (n + gx)), int(y0 + r * (n + gy))
        sheet[yy:yy + n, xx:xx + n] = fr
    sheet += rg.normal(0, 0.008, sheet.shape)
    g = (np.clip(sheet, 0, 1) * 255).astype('uint8')
    rgb = np.stack([np.clip(g * 1.0 + 6, 0, 255), g * 0.97 + 3, g * 0.90], -1).astype('uint8')
    im = Image.fromarray(rgb)
    d = ImageDraw.Draw(im)
    fm = font(MONO, 19)
    for i in range(12):
        r, c = divmod(i, 3)
        xx, yy = int(x0 + c * (n + gx)), int(y0 + r * (n + gy))
        d.text((xx + 4, yy - 30), f'{i + 1}', font=fm, fill=(214, 200, 150))
        d.text((xx + 52, yy - 30), f'{216 - 6 * i} FT' if i < 11 else 'NOT TAKEN', font=fm, fill=(150, 140, 110) if i < 11 else (190, 70, 55))
        d.polygon([(xx + n - 26, yy - 26), (xx + n - 8, yy - 18), (xx + n - 26, yy - 10)], fill=(214, 200, 150))
        d.text((xx + 4, yy + n + 4), 'SAFETY FILM', font=font(MONO, 13), fill=(110, 104, 88))
    d.line([(x0 - 10, y0 + 3 * (n + gy) - 40), (x0 + 3 * n + 2 * gx + 10, y0 + 3 * (n + gy) - 40)], fill=(190, 70, 55), width=2)
    im.save(A / 'p13-contact.jpg', quality=90)
    print('contact')


# ------------------------------------------------------------------ XV. sand figures
def chladni():
    rg = np.random.default_rng(1847)
    w, h, ss = 1350, 1890, 2
    im = Image.new('RGB', (w * ss, h * ss), PAPER)
    d = ImageDraw.Draw(im)
    modes = [(1, 2, 1), (1, 3, -1), (2, 3, 1), (1, 4, 1), (2, 4, -1), (3, 4, 1), (1, 5, -1), (2, 5, 1), (3, 5, -1), (4, 5, 1), (2, 6, 1), (3, 7, -1)]
    cell, gap = 380, 50
    x0 = (w - 3 * cell - 2 * gap) / 2
    y0 = 110
    fm = font(MONO, 15 * ss)
    for i, (n, m, sg) in enumerate(modes):
        r, c = divmod(i, 3)
        ox, oy = (x0 + c * (cell + gap)) * ss, (y0 + r * (cell + gap + 34)) * ss
        S = cell * ss
        d.rectangle([ox, oy, ox + S, oy + S], outline=INK, width=3, fill=(236, 228, 211))
        pts = rg.uniform(-1, 1, (150000, 2))
        u = np.cos(n * math.pi * pts[:, 0] / 2 * 2) * np.cos(m * math.pi * pts[:, 1] / 2 * 2) + sg * np.cos(m * math.pi * pts[:, 0]) * np.cos(n * math.pi * pts[:, 1])
        keep = rg.random(len(pts)) < np.exp(-(u / 0.11) ** 2)
        if i == 7:                                 # report 47/1847: sand where the figure has no line
            extra = rg.normal(0, 0.055, (2600, 2))
            pts = np.vstack([pts[keep], extra]); keep = np.ones(len(pts), bool)
        for px, py in pts[keep][:26000]:
            X, Y = ox + (px + 1) / 2 * S, oy + (py + 1) / 2 * S
            rr = rg.uniform(0.9, 2.0)
            d.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=INK)
        if i == 7:
            d.ellipse([ox + S / 2 - 64, oy + S / 2 - 64, ox + S / 2 + 64, oy + S / 2 + 64], outline=OX, width=5)
        d.text((ox, oy + S + 8 * ss), f'{n} | {m}  {"+" if sg > 0 else "-"}', font=fm, fill=(109, 98, 82))
    d.text((x0 * ss, 48 * ss), 'ACCIDENT-PREVENTION REPORT 47/1847  --  FIGURES ON THE PLATE, SAND', font=font(MONO, 17 * ss), fill=(109, 98, 82))
    im.resize((w, h), Image.LANCZOS).save(A / 'p15-chladni.png')
    print('chladni')


if __name__ == '__main__':
    dust(); cover(); neon(); contact(); chladni()
