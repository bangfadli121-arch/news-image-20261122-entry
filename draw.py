#!/usr/bin/env python3
"""Draw the front page for Sunday 22 November 2026 (1024x1024, PNG).

Every story in the picture happened, or was first reported, on Sunday
22 November 2026. Stories from earlier in the week (the Shenzhen summit,
the World Court's Myanmar ruling, Anthropic's debut, the Peru quake,
Estonia's border decision, the Kerch Bridge strikes) are named in the
red DATE CHECK box instead of being shown as Sunday news.

Deterministic: no clock, no network, no unseeded randomness. All art is
drawn from scratch with Pillow: layered gradients, glows, shading and
hand-set polygons, so two runs produce byte-identical output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (232, 220, 188)
INK = (18, 18, 18)
SOFT = (60, 60, 60)
RED = (176, 32, 32)
RED_BG = (248, 226, 208)
SEA = (148, 188, 214)
LAND = (222, 190, 134)
LAND_LINE = (70, 58, 32)
GRID = (168, 184, 196)

F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Split text into lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, f, max_w, lh, fill=INK):
    """Draw wrapped text, return the y below the last line."""
    for line in wrap(d, text, f, max_w):
        d.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def centre(d, cx, y, text, f, fill=INK):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def fit(d, text, f_path, size, max_w):
    """Largest font size at or below `size` that fits max_w."""
    while size > 10:
        f = F(f_path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return F(f_path, 10)


def rule(d, x, y, w, weight=2, fill=INK):
    d.rectangle([x, y, x + w - 1, y + weight - 1], fill=fill)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_bands(d, x, y, w, h, top, bottom, bands=0):
    """Smooth vertical gradient, one row per step (deterministic)."""
    if h <= 1:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=top)
        return
    for i in range(h):
        c = lerp(top, bottom, i / (h - 1))
        d.line([(x, y + i), (x + w - 1, y + i)], fill=c)


def speckle(d, x, y, w, h, seed=12345, n=140, col=(120, 110, 90)):
    """Deterministic paper speckle from a tiny fixed-seed generator."""
    s = seed
    for _ in range(n):
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        px = x + s % w
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        py = y + s % h
        d.point((px, py), fill=col)


def paper_texture(d, seed=20261122):
    """Aged-newsprint texture: deterministic fibres + speckle over paper."""
    s = seed
    for _ in range(2600):
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        px = s % W
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        py = s % H
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        ln = 2 + s % 4
        col = (205, 190, 155) if s % 3 else (244, 236, 205)
        if s % 2 == 0:
            d.line([(px, py), (px + ln, py)], fill=col, width=1)
        else:
            d.line([(px, py), (px, py + ln)], fill=col, width=1)
    speckle(d, 0, 0, W, H, seed=777, n=500, col=(150, 135, 105))
    speckle(d, 0, 0, W, H, seed=31337, n=500, col=(210, 195, 160))


def hatch(d, x, y, w, h, step=7, col=(0, 0, 0)):
    """Diagonal hatch lines clipped to a rectangle."""
    for i in range(-h, w + h, step):
        d.line([(x + i, y + h), (x + i + h, y)], fill=col, width=1)


def starburst(d, cx, cy, r1, r2, points, fill):
    """Spiky explosion shape with alternating radii."""
    import math
    pts = []
    for i in range(points * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def glow(d, cx, cy, r, core, halo, steps=6):
    """Radial glow: concentric discs fading from core to halo colour."""
    for i in range(steps, 0, -1):
        t = (i - 1) / (steps - 1)
        c = lerp(core, halo, t)
        rr = r * i // steps
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)


def puff(d, cx, cy, rx, ry, base, sky, layers=4):
    """Soft cloud/smoke puff: layered ellipses fading into the sky."""
    for i in range(layers, 0, -1):
        t = (i - 1) / (layers - 1)
        c = lerp(base, sky, t)
        k = i / layers
        d.ellipse([cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k],
                  fill=c)


def stars(d, x, y, w, h, seed=987, n=26):
    """Deterministic stars in the upper part of a sky box."""
    s = seed
    for _ in range(n):
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        px = x + s % w
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        py = y + s % max(1, h * 3 // 5)
        r = 1 + s % 2
        d.ellipse([px - r, py - r, px + r, py + r], fill=(235, 238, 245))


# ---------------------------------------------------------------- art: heroes
def art_gulf(d, x, y, w, h):
    """Dusk over the Gulf: glowing sun, layered clouds, lit base, blast."""
    sky_bands(d, x, y, w, h, (240, 150, 68), (102, 50, 48))
    sx, sy = x + w - 56, y + 28
    glow(d, sx, sy, 36, (255, 232, 160), (208, 128, 64))
    d.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(255, 240, 190))
    for cx, cy, rx in [(x + 58, y + 22, 46), (x + 152, y + 13, 40),
                       (x + 250, y + 46, 50), (x + 92, y + 48, 34)]:
        puff(d, cx, cy, rx, 8, (246, 188, 142), (228, 134, 64), layers=3)
        puff(d, cx - rx // 2, cy + 3, rx // 2, 6, (246, 188, 142),
             (228, 134, 64), layers=3)
        puff(d, cx + rx // 2, cy + 3, rx // 2, 6, (246, 188, 142),
             (228, 134, 64), layers=3)
    stars(d, x, y, w, 26, seed=4242, n=10)
    sea_y = y + h - 26
    sky_bands(d, x, sea_y, w, y + h - sea_y, (66, 98, 114), (36, 58, 74))
    for i in range(6):
        wx = x + 10 + i * 52
        d.arc([wx, sea_y + 3, wx + 40, sea_y + 15], 200, 340,
              fill=(150, 185, 198))
    for gy in range(sea_y + 4, y + h - 4, 6):
        gw = 30 - (gy - sea_y) // 2
        d.line([(sx - gw // 2, gy), (sx + gw // 2, gy)],
               fill=(250, 214, 130), width=1)
    # base silhouette: shaded faces, lit windows, radar dome
    base, dark = (36, 33, 38), (18, 16, 20)
    d.rectangle([x + 18, sea_y - 26, x + 78, sea_y], fill=base)
    d.rectangle([x + 72, sea_y - 26, x + 78, sea_y], fill=dark)
    d.rectangle([x + 88, sea_y - 16, x + 128, sea_y], fill=base)
    d.rectangle([x + 122, sea_y - 16, x + 128, sea_y], fill=dark)
    d.rectangle([x + 138, sea_y - 32, x + 150, sea_y], fill=base)
    d.ellipse([x + 139, sea_y - 44, x + 153, sea_y - 30], fill=base)
    d.arc([x + 141, sea_y - 42, x + 151, sea_y - 32], 200, 340,
          fill=(200, 200, 195))
    d.rectangle([x + 210, sea_y - 20, x + 300, sea_y], fill=base)
    d.rectangle([x + 292, sea_y - 20, x + 300, sea_y], fill=dark)
    d.polygon([(x + 236, sea_y - 20), (x + 246, sea_y - 44),
               (x + 256, sea_y - 20)], fill=base)
    d.ellipse([x + 243, sea_y - 48, x + 249, sea_y - 42], fill=(255, 90, 70))
    for wx in range(x + 24, x + 74, 10):
        for wy in range(sea_y - 22, sea_y - 4, 8):
            if (wx + wy) % 3 == 0:
                d.rectangle([wx, wy, wx + 2, wy + 2], fill=(255, 200, 90))
    for wx in range(x + 216, x + 296, 12):
        if wx % 24 == 0:
            d.rectangle([wx, sea_y - 14, wx + 2, sea_y - 12],
                        fill=(255, 200, 90))
    # blast with halo, core and rising smoke
    bx, by = x + 190, y + 52
    glow(d, bx, by, 28, (255, 214, 110), (182, 108, 60))
    starburst(d, bx, by, 26, 11, 9, (250, 196, 66))
    starburst(d, bx, by, 15, 7, 9, (238, 90, 40))
    d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(255, 244, 200))
    puff(d, bx - 14, by - 26, 16, 9, (96, 86, 84), (206, 126, 62))
    puff(d, bx + 8, by - 34, 12, 7, (116, 104, 100), (214, 132, 64))
    # missile arcs with faint smoke trails
    for sx0, sy0, ex, ey in [(x + 40, y + 96, x + 120, y + 40),
                             (x + 280, y + 100, x + 220, y + 44),
                             (x + 90, y + 104, x + 168, y + 62)]:
        d.line([(sx0 + 3, sy0 + 2), (ex + 3, ey + 2)], fill=(200, 186, 170),
               width=1)
        d.line([(sx0, sy0), (ex, ey)], fill=(255, 244, 214), width=2)
        d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 244, 214))


def art_mexico(d, x, y, w, h):
    """Night raid in the desert: moon glow, layered ridges, helicopter."""
    sky_bands(d, x, y, w, h, (16, 26, 52), (66, 84, 116))
    stars(d, x, y, w, h, seed=777, n=30)
    mx, my = x + w - 48, y + 26
    glow(d, mx, my, 30, (250, 244, 210), (22, 32, 58))
    d.ellipse([mx - 15, my - 15, mx + 15, my + 15], fill=(242, 236, 204))
    for cx, cy, r in [(mx - 5, my - 3, 3), (mx + 6, my + 5, 2),
                      (mx + 2, my - 8, 2)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 206, 170))
    d.polygon([(x, y + h), (x + 40, y + 58), (x + 110, y + 70),
               (x + 180, y + 50), (x + 250, y + 66), (x + w, y + 58),
               (x + w, y + h)], fill=(40, 52, 80))
    d.line([(x, y + 74), (x + 40, y + 58), (x + 110, y + 70),
            (x + 180, y + 50), (x + 250, y + 66), (x + w, y + 58)],
           fill=(96, 110, 146), width=1)
    d.polygon([(x, y + h), (x + 60, y + 78), (x + 150, y + 66),
               (x + 230, y + 82), (x + w, y + 72), (x + w, y + h)],
              fill=(18, 24, 44))
    d.line([(x, y + 92), (x + 60, y + 78), (x + 150, y + 66),
            (x + 230, y + 82), (x + w, y + 72)], fill=(56, 68, 100), width=1)
    # desert floor with cacti and scattered lights
    sky_bands(d, x, y + h - 16, w, 16, (56, 46, 34), (30, 22, 18))
    for lx in range(x + 14, x + w - 10, 34):
        d.ellipse([lx, y + h - 12, lx + 3, y + h - 9], fill=(250, 210, 110))
    for cx in (x + 34, x + 288):
        d.rectangle([cx, y + h - 30, cx + 4, y + h - 16], fill=(22, 32, 24))
        d.rectangle([cx - 5, y + h - 26, cx - 1, y + h - 20],
                    fill=(22, 32, 24))
        d.rectangle([cx + 5, y + h - 28, cx + 9, y + h - 22],
                    fill=(22, 32, 24))
    # helicopter with layered searchlight cone and ground pool
    hx, hy = x + 128, y + 30
    d.ellipse([hx - 46, hy - 14, hx + 46, hy - 10], outline=(170, 170, 165))
    d.line([(hx - 52, hy - 12), (hx + 52, hy - 12)], fill=(210, 210, 200),
           width=3)
    d.ellipse([hx - 30, hy - 8, hx + 26, hy + 10], fill=(30, 30, 34))
    d.rectangle([hx - 28, hy - 7, hx + 24, hy - 3], fill=(70, 70, 76))
    d.rectangle([hx + 26, hy - 2, hx + 52, hy + 4], fill=(30, 30, 34))
    d.polygon([(hx + 52, hy - 2), (hx + 62, hy - 10), (hx + 62, hy + 4)],
              fill=(30, 30, 34))
    d.line([(hx - 4, hy + 10), (hx - 4, hy + 22)], fill=(200, 200, 190),
           width=2)
    d.polygon([(hx - 16, hy + 12), (hx + 8, hy + 12), (hx + 46, y + h - 16),
               (hx - 36, y + h - 16)], fill=(214, 198, 122))
    d.polygon([(hx - 10, hy + 12), (hx + 2, hy + 12), (hx + 34, y + h - 16),
               (hx - 24, y + h - 16)], fill=(238, 220, 138))
    d.polygon([(hx - 4, hy + 12), (hx - 2, hy + 12), (hx + 22, y + h - 16),
               (hx - 12, y + h - 16)], fill=(250, 232, 150))
    d.ellipse([hx - 12, y + h - 24, hx + 28, y + h - 8], fill=(250, 210, 110))
    d.ellipse([hx - 4, y + h - 20, hx + 20, y + h - 12], fill=(255, 232, 150))


def art_cop(d, x, y, w, h):
    """Climate deadlock: shaded globe, glass thermometer, waving flags."""
    sky_bands(d, x, y, w, h, (146, 196, 190), (56, 100, 116))
    glow(d, x + 34, y + 20, 26, (255, 244, 200), (146, 196, 190))
    for cx, cy, rx, ry in [(x + 78, y + 14, 34, 7), (x + 216, y + 12, 40, 8),
                           (x + 284, y + 36, 28, 6)]:
        puff(d, cx, cy, rx, ry, (242, 250, 248), (150, 198, 192))
    # globe: ocean, two-tone land, shaded limb, bright highlight
    cx, cy, r = x + 118, y + 58, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(96, 158, 205))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 60, 90), width=2)
    for lx, ly, rx, ry in [(cx - 30, cy - 26, 28, 20), (cx + 4, cy - 2, 26, 24),
                           (cx - 18, cy + 18, 24, 16)]:
        d.ellipse([lx, ly, lx + rx, ly + ry], fill=(74, 134, 94))
        d.ellipse([lx + 3, ly + 3, lx + rx - 3, ly + ry - 3],
                  fill=(112, 176, 122))
    for gx in range(cx - r + 8, cx + r - 4, 16):
        d.arc([gx, cy - r, gx + 16, cy + r], 270, 90, fill=(60, 110, 150))
    d.line([(cx - r, cy), (cx + r, cy)], fill=(60, 110, 150), width=1)
    d.arc([cx - r, cy - r, cx + r, cy + r], -55, 55, fill=(58, 108, 158),
          width=6)
    d.arc([cx - r, cy - r, cx + r, cy + r], 140, 230, fill=(196, 228, 242),
          width=4)
    # smoke puffs, upper right (behind the thermometer)
    for sx, sy, sr in [(x + 250, y + 18, 9), (x + 268, y + 28, 12),
                       (x + 288, y + 16, 8)]:
        puff(d, sx, sy, sr, sr * 3 // 4, (205, 205, 200), (150, 198, 192))
    # thermometer: glass tube, red gradient column, bulb glow, ticks
    tx = x + w - 46
    d.rectangle([tx, y + 12, tx + 14, y + h - 34], fill=(240, 240, 235),
                outline=(30, 30, 30))
    sky_bands(d, tx + 3, y + 20, 8, h - 56, (232, 82, 62), (192, 32, 32))
    d.rectangle([tx, y + 12, tx + 14, y + h - 34], outline=(30, 30, 30))
    d.line([(tx + 2, y + 16), (tx + 2, y + h - 40)], fill=(255, 255, 255),
           width=2)
    glow(d, tx + 7, y + h - 28, 14, (230, 60, 50), (80, 118, 130))
    d.ellipse([tx - 3, y + h - 38, tx + 17, y + h - 18], fill=(210, 40, 40))
    d.ellipse([tx + 1, y + h - 34, tx + 9, y + h - 26], fill=(238, 90, 70))
    for i, mark in enumerate([0, 1, 2]):
        my = y + 22 + mark * 18
        d.line([(tx + 14, my), (tx + 20, my)], fill=(30, 30, 30), width=1)
    # flags: shaded two-tone cloth on poles
    flags = [(196, 60, 60), (60, 110, 190), (240, 200, 60), (70, 150, 90),
             (150, 90, 160), (220, 120, 60)]
    for i, c in enumerate(flags):
        fx = x + 14 + i * 46
        dark = tuple(int(v * 0.62) for v in c)
        d.line([(fx, y + h - 30), (fx, y + h - 8)], fill=(40, 40, 40),
               width=2)
        d.polygon([(fx, y + h - 30), (fx + 34, y + h - 30),
                   (fx + 34, y + h - 18), (fx, y + h - 18)], fill=c)
        d.polygon([(fx, y + h - 24), (fx + 34, y + h - 24),
                   (fx + 34, y + h - 18), (fx, y + h - 18)], fill=dark)
        d.line([(fx, y + h - 30), (fx + 34, y + h - 30)],
               fill=(255, 255, 255), width=1)


# ---------------------------------------------------------------- art: minis
def art_mini(d, x, y, w, h, kind):
    """Small square scene for a small card. kind picks the emblem."""
    tops = {"db": ((40, 44, 66), (84, 96, 124)),
            "fire": ((120, 40, 30), (220, 110, 50)),
            "bottle": ((60, 90, 60), (140, 170, 120)),
            "flood": ((70, 110, 150), (150, 190, 215)),
            "ship": ((60, 90, 120), (130, 170, 200)),
            "raid": ((30, 36, 58), (70, 88, 120)),
            "factory": ((90, 80, 70), (170, 150, 120)),
            "capitol": ((50, 70, 110), (120, 150, 190)),
            "rugby": ((40, 110, 60), (110, 180, 110)),
            "trophy": ((120, 90, 30), (220, 180, 80))}
    top, bot = tops[kind]
    sky_bands(d, x, y, w, h, top, bot, bands=4)
    if kind == "db":
        # server racks with rows of status LEDs and a warning triangle
        for i in range(3):
            rx = x + 8 + i * 15
            d.rectangle([rx, y + 10, rx + 11, y + h - 8], fill=(22, 26, 34))
            d.rectangle([rx, y + 10, rx + 11, y + 12], fill=(70, 78, 92))
            d.rectangle([rx + 9, y + 10, rx + 11, y + h - 8],
                        fill=(10, 12, 16))
            for j in range(4):
                led = [(90, 220, 120), (250, 200, 80), (90, 220, 120),
                       (235, 70, 60)][(i + j) % 4]
                d.ellipse([rx + 2, y + 14 + j * 5, rx + 5, y + 17 + j * 5],
                          fill=led)
        d.line([(x + 8, y + h - 8), (x + w - 8, y + h - 8)],
               fill=(120, 130, 145), width=1)
        glow(d, x + w - 9, y + 16, 10, (255, 90, 70), (58, 66, 90))
        d.polygon([(x + w - 16, y + 8), (x + w - 2, y + 8), (x + w - 9, y + 24)],
                  fill=(230, 40, 40))
        d.text((x + w - 12, y + 11), "!", font=F(F_SANS_B, 10), fill=(255, 255, 255))
    elif kind == "fire":
        # layered flames over dark ground, smoke and sparks above
        d.rectangle([x, y + h - 8, x + w - 1, y + h - 1], fill=(48, 26, 20))
        for fx, fy, fs, c in [(x + 10, y + 20, 18, (226, 84, 28)),
                              (x + 24, y + 12, 22, (240, 120, 40)),
                              (x + 16, y + 26, 14, (252, 190, 70)),
                              (x + 26, y + 22, 10, (255, 240, 180))]:
            d.polygon([(fx, fy + fs), (fx + fs // 2, fy), (fx + fs, fy + fs)],
                      fill=c)
        for sx, sy, sr in [(x + 16, y + 8, 5), (x + 28, y + 4, 6)]:
            puff(d, sx, sy, sr, sr // 2 + 2, (150, 140, 135), (150, 70, 45))
        for sx, sy in [(x + 12, y + 10), (x + 36, y + 8), (x + 44, y + 16)]:
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 220, 120))
    elif kind == "bottle":
        # poison bottle: glass highlight, label, skull mark, bubbles
        d.ellipse([x + 8, y + h - 8, x + w - 8, y + h - 2], fill=(30, 55, 35))
        d.rectangle([x + 20, y + 12, x + 32, y + h - 8], fill=(36, 100, 46))
        d.rectangle([x + 29, y + 12, x + 32, y + h - 8], fill=(22, 66, 30))
        d.rectangle([x + 24, y + 6, x + 28, y + 12], fill=(30, 84, 40))
        d.rectangle([x + 22, y + 22, x + 30, y + 30], fill=(242, 238, 220))
        d.ellipse([x + 24, y + 23, x + 28, y + 27], fill=(30, 30, 30))
        d.line([(x + 22, y + 26), (x + 30, y + 26)], fill=(30, 30, 30),
               width=1)
        d.line([(x + 22, y + 14), (x + 22, y + h - 10)], fill=(190, 230, 190),
               width=1)
        for bx, by in [(x + 26, y + 32), (x + 29, y + 35), (x + 24, y + 36)]:
            d.ellipse([bx, by, bx + 1, by + 1], fill=(170, 220, 170))
        d.ellipse([x + 36, y + 12, x + 46, y + 22], fill=(240, 240, 230))
        d.ellipse([x + 38, y + 14, x + 40, y + 16], fill=(30, 30, 30))
        d.ellipse([x + 42, y + 14, x + 44, y + 16], fill=(30, 30, 30))
        d.arc([x + 38, y + 16, x + 44, y + 21], 0, 180, fill=(30, 30, 30))
    elif kind == "flood":
        # driving rain, capped waves and a rooftop breaking the water
        for i in range(5):
            rx = x + 6 + i * 10
            d.line([(rx, y + 4), (rx - 3, y + 12)], fill=(220, 232, 240),
                   width=1)
        sky_bands(d, x, y + h - 16, w, 16, (70, 110, 140), (52, 88, 120))
        for i in range(3):
            wy = y + 12 + i * 9
            d.arc([x + 4, wy, x + w - 4, wy + 12], 180, 360,
                  fill=(240, 245, 250), width=2)
            d.line([(x + 8 + i * 14, wy + 2), (x + 16 + i * 14, wy + 2)],
                   fill=(255, 255, 255), width=1)
        d.polygon([(x + 10, y + h - 8), (x + 26, y + h - 26),
                   (x + 42, y + h - 8)], fill=(120, 70, 50))
        d.polygon([(x + 10, y + h - 8), (x + 26, y + h - 26),
                   (x + 42, y + h - 8)], outline=(70, 40, 30))
        d.rectangle([x + 22, y + h - 18, x + 30, y + h - 10],
                    fill=(255, 210, 110))
        d.rectangle([x + 20, y + h - 26, x + 32, y + h - 24],
                    fill=(70, 40, 30))
    elif kind == "ship":
        # container ship: shaded hull, stacked boxes, funnel smoke, gulls
        for gx, gy in [(x + 12, y + 8), (x + 24, y + 6), (x + 38, y + 10)]:
            d.line([(gx, gy), (gx + 3, gy + 2)], fill=(240, 240, 230), width=1)
            d.line([(gx + 3, gy + 2), (gx + 6, gy)], fill=(240, 240, 230),
                   width=1)
        sky_bands(d, x, y + h - 16, w, 16, (52, 96, 128), (36, 72, 100))
        for i in range(2):
            wy = y + h - 12 + i * 5
            d.arc([x + 4, wy, x + w - 4, wy + 8], 180, 360,
                  fill=(200, 220, 230), width=1)
        d.polygon([(x + 8, y + h - 16), (x + 14, y + h - 30),
                   (x + 42, y + h - 30), (x + 46, y + h - 16)],
                  fill=(28, 28, 32))
        d.polygon([(x + 8, y + h - 16), (x + 14, y + h - 30),
                   (x + 42, y + h - 30), (x + 46, y + h - 16)],
                  outline=(90, 90, 95))
        d.rectangle([x + 8, y + h - 18, x + 46, y + h - 16],
                    fill=(150, 60, 50))
        for px in range(x + 12, x + 44, 8):
            d.ellipse([px, y + h - 24, px + 2, y + h - 22],
                      fill=(255, 210, 110))
        d.rectangle([x + 16, y + h - 38, x + 30, y + h - 30],
                    fill=(170, 70, 50))
        d.rectangle([x + 31, y + h - 38, x + 42, y + h - 30],
                    fill=(60, 130, 140))
        d.rectangle([x + 16, y + h - 38, x + 42, y + h - 36],
                    fill=(255, 255, 255))
        d.rectangle([x + 44, y + 2, x + 48, y + h - 30], fill=(28, 28, 32))
        puff(d, x + 46, y + 4, 5, 3, (200, 200, 195), (110, 160, 195))
        d.line([(x + 14, y + h - 30), (x + 14, y + h - 36)],
               fill=(28, 28, 32), width=1)
        d.ellipse([x + 13, y + h - 38, x + 15, y + h - 36],
                  fill=(255, 240, 180))
    elif kind == "raid":
        # night ridge, moon glow and a helicopter with a searchlight
        stars(d, x, y, w, h, seed=31, n=8)
        glow(d, x + w - 11, y + 11, 9, (240, 236, 210), (40, 48, 72))
        d.ellipse([x + w - 16, y + 6, x + w - 6, y + 16], fill=(238, 232, 200))
        d.polygon([(x, y + h), (x + 16, y + 18), (x + 34, y + h)],
                  fill=(14, 20, 36))
        d.polygon([(x + 24, y + h), (x + 40, y + 24), (x + w, y + h)],
                  fill=(20, 28, 48))
        d.line([(x + 4, y + 26), (x + 16, y + 18), (x + 30, y + 26)],
               fill=(60, 72, 104), width=1)
        d.ellipse([x + 14, y + 12, x + 30, y + 18], fill=(60, 60, 64))
        d.line([(x + 10, y + 10), (x + 34, y + 10)], fill=(200, 200, 190),
               width=2)
        d.polygon([(x + 18, y + 14), (x + 26, y + 14), (x + 32, y + h - 8),
                   (x + 14, y + h - 8)], fill=(250, 226, 140))
        d.ellipse([x + 18, y + h - 12, x + 28, y + h - 4],
                  fill=(250, 210, 110))
    elif kind == "factory":
        # factory blocks with lit windows, sawtooth roof, chimney smoke
        d.rectangle([x + 6, y + 22, x + 24, y + h - 6], fill=(50, 48, 46))
        d.rectangle([x + 26, y + 28, x + 46, y + h - 6], fill=(70, 66, 62))
        d.polygon([(x + 6, y + 22), (x + 15, y + 12), (x + 24, y + 22)],
                  fill=(62, 60, 58))
        d.polygon([(x + 26, y + 28), (x + 32, y + 20), (x + 38, y + 28)],
                  fill=(84, 80, 76))
        d.polygon([(x + 38, y + 28), (x + 44, y + 20), (x + 46, y + 28)],
                  fill=(84, 80, 76))
        for wx in range(x + 9, x + 22, 5):
            for wy in range(y + 26, y + h - 8, 6):
                if (wx + wy) % 2 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 2], fill=(255, 200, 90))
        d.rectangle([x + 30, y + 8, x + 34, y + 28], fill=(50, 48, 46))
        d.rectangle([x + 30, y + 8, x + 32, y + 28], fill=(70, 68, 66))
        puff(d, x + 32, y + 4, 7, 4, (160, 155, 150), (130, 120, 105))
        puff(d, x + 38, y + 3, 5, 3, (170, 165, 160), (130, 120, 105))
        d.rectangle([x + 12, y + h - 12, x + 18, y + h - 6],
                    fill=(30, 28, 26))
        d.rectangle([x, y + h - 6, x + w - 1, y + h - 1], fill=(40, 36, 32))
    elif kind == "capitol":
        # domed capitol: shaded dome, columns, steps and a flag
        d.rectangle([x + 8, y + h - 14, x + w - 8, y + h - 6],
                    fill=(40, 44, 60))
        d.rectangle([x + 4, y + h - 8, x + w - 4, y + h - 6],
                    fill=(56, 60, 78))
        d.rectangle([x + 18, y + h - 26, x + w - 18, y + h - 14],
                    fill=(50, 56, 76))
        for cx in range(x + 22, x + w - 20, 8):
            d.line([(cx, y + h - 26), (cx, y + h - 14)],
                   fill=(200, 205, 220), width=1)
        d.pieslice([x + 14, y + 10, x + w - 14, y + 34], 180, 360,
                   fill=(50, 56, 76))
        d.arc([x + 16, y + 12, x + w - 16, y + 34], 200, 340,
              fill=(150, 160, 190))
        d.rectangle([x + w // 2 - 1, y + 4, x + w // 2 + 1, y + 12],
                    fill=(50, 56, 76))
        d.polygon([(x + w // 2 + 1, y + 4), (x + w // 2 + 12, y + 4),
                   (x + w // 2 + 12, y + 9), (x + w // 2 + 1, y + 9)],
                  fill=(196, 60, 60))
        for sx, sy in [(x + 10, y + 10), (x + w - 12, y + 8), (x + 14, y + 24)]:
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(250, 240, 180))
    elif kind == "rugby":
        # striped pitch, goal posts and a shaded ball
        for i in range(6):
            sx = x + i * (w // 6)
            col = (46, 110, 60) if i % 2 == 0 else (56, 128, 70)
            d.rectangle([sx, y + h - 16, sx + w // 6, y + h - 1], fill=col)
        d.line([(x + 10, y + h - 26), (x + 10, y + h - 12)],
               fill=(240, 240, 230), width=2)
        d.line([(x + w - 10, y + h - 26), (x + w - 10, y + h - 12)],
               fill=(240, 240, 230), width=2)
        d.line([(x + 10, y + h - 26), (x + w - 10, y + h - 26)],
               fill=(240, 240, 230), width=2)
        d.line([(x, y + h - 16), (x + w - 1, y + h - 16)],
               fill=(240, 240, 230), width=1)
        d.ellipse([x + 12, y + h - 6, x + w - 12, y + h - 2],
                  fill=(30, 70, 40))
        d.ellipse([x + 14, y + 12, x + w - 14, y + 34], fill=(200, 120, 50))
        d.ellipse([x + 18, y + 14, x + w - 18, y + 30], fill=(220, 145, 70))
        d.line([(x + 16, y + 22), (x + w - 16, y + 22)], fill=(120, 60, 20),
               width=2)
        d.line([(x + w // 2 - 8, y + 19), (x + w // 2 + 8, y + 25)],
               fill=(240, 230, 210), width=1)
    else:  # trophy
        # golden cup: sheened bowl, handles, stepped base, sparkles
        d.ellipse([x + w // 2 - 9, y + 10, x + w // 2 + 9, y + 30],
                  fill=(214, 164, 52))
        d.ellipse([x + w // 2 - 7, y + 12, x + w // 2 + 1, y + 26],
                  fill=(240, 198, 96))
        d.arc([x + w // 2 - 8, y + 11, x + w // 2 + 8, y + 29], 180, 300,
              fill=(255, 232, 160), width=2)
        d.rectangle([x + w // 2 - 3, y + 30, x + w // 2 + 3, y + 38],
                    fill=(200, 150, 40))
        d.rectangle([x + w // 2 - 3, y + 30, x + w // 2 + 3, y + 33],
                    fill=(232, 184, 70))
        d.rectangle([x + w // 2 - 10, y + 38, x + w // 2 + 10, y + 42],
                    fill=(180, 132, 32))
        d.rectangle([x + w // 2 - 10, y + 38, x + w // 2 + 10, y + 40],
                    fill=(214, 164, 52))
        d.arc([x + 8, y + 12, x + 24, y + 28], 90, 270, fill=(200, 150, 40),
              width=3)
        d.arc([x + w - 24, y + 12, x + w - 8, y + 28], 270, 90,
              fill=(200, 150, 40), width=3)
        for cx, cy in [(x + 10, y + 8), (x + w - 12, y + 14), (x + 16, y + 36)]:
            starburst(d, cx, cy, 4, 2, 4, (255, 240, 170))
        for cx, cy, c in [(x + 26, y + 8, (240, 90, 90)),
                          (x + w - 30, y + 30, (90, 140, 240)),
                          (x + w - 20, y + 6, (90, 200, 120))]:
            d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)


# ---------------------------------------------------------------- map
N_AMERICA = [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73),
             (-105, 70), (-95, 69), (-90, 66), (-85, 66), (-80, 73),
             (-75, 72), (-68, 62), (-60, 55), (-55, 47), (-60, 44),
             (-66, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 32),
             (-81, 26), (-84, 30), (-89, 29), (-93, 29), (-97, 26),
             (-100, 22), (-105, 20), (-102, 17), (-95, 16), (-90, 14),
             (-86, 12), (-82, 9), (-79, 9), (-83, 10), (-86, 13),
             (-90, 14), (-94, 16), (-97, 16), (-101, 18), (-105, 20),
             (-108, 23), (-112, 28), (-117, 33), (-122, 37), (-124, 42),
             (-124, 48), (-130, 55), (-140, 60), (-150, 59), (-158, 58),
             (-165, 60), (-168, 66)]
S_AMERICA = [(-79, 9), (-75, 11), (-71, 12), (-66, 11), (-61, 9), (-56, 6),
             (-52, 5), (-50, 0), (-46, -2), (-42, -3), (-38, -5), (-35, -8),
             (-37, -12), (-39, -17), (-41, -22), (-46, -24), (-48, -27),
             (-52, -32), (-55, -35), (-58, -38), (-62, -41), (-65, -45),
             (-68, -50), (-70, -54), (-73, -50), (-73, -44), (-72, -36),
             (-71, -28), (-70, -20), (-72, -17), (-76, -14), (-79, -8),
             (-81, -4), (-80, 1), (-79, 5), (-79, 9)]
AFRICA = [(-17, 15), (-16, 20), (-14, 24), (-10, 28), (-6, 34), (-2, 35),
          (3, 37), (9, 37), (11, 34), (15, 32), (20, 32), (25, 32),
          (30, 31), (33, 28), (35, 28), (37, 24), (39, 20), (41, 16),
          (43, 12), (46, 11), (51, 11), (50, 6), (46, 2), (42, -2),
          (40, -8), (39, -14), (36, -18), (34, -22), (32, -26), (30, -30),
          (28, -33), (24, -34), (19, -35), (16, -32), (14, -24), (13, -18),
          (12, -10), (11, -4), (9, 3), (6, 4), (2, 6), (-3, 5), (-8, 5),
          (-12, 8), (-15, 11), (-17, 15)]
EURASIA = [(-9, 37), (-9, 43), (-2, 44), (0, 46), (3, 43), (7, 44),
           (10, 44), (12, 42), (15, 40), (18, 40), (20, 42), (23, 37),
           (26, 38), (28, 37), (30, 36), (33, 36), (36, 36), (39, 38),
           (42, 41), (44, 40), (47, 40), (50, 42), (52, 44), (55, 46),
           (58, 48), (60, 50), (63, 53), (66, 55), (68, 58), (70, 62),
           (72, 66), (74, 69), (76, 72), (80, 73), (85, 74), (90, 75),
           (95, 76), (100, 76), (105, 77), (110, 74), (115, 73), (120, 73),
           (125, 72), (130, 72), (135, 71), (140, 72), (145, 71), (150, 70),
           (155, 69), (160, 69), (165, 68), (170, 67), (175, 66), (178, 65),
           (180, 65), (180, 62), (175, 61), (170, 60), (165, 60), (160, 58),
           (158, 53), (155, 51), (150, 50), (147, 46), (143, 44), (140, 40),
           (138, 36), (135, 34), (132, 33), (130, 33), (127, 35), (125, 38),
           (122, 38), (121, 34), (119, 30), (117, 26), (114, 23), (111, 21),
           (109, 19), (107, 12), (105, 9), (103, 6), (101, 7), (100, 9),
           (98, 12), (96, 15), (94, 17), (92, 21), (90, 22), (88, 22),
           (86, 20), (84, 19), (82, 17), (80, 14), (78, 9), (76, 10),
           (74, 14), (73, 19), (71, 20), (69, 22), (67, 24), (65, 25),
           (62, 25), (59, 25), (57, 26), (55, 26), (52, 27), (50, 29),
           (48, 30), (46, 29), (44, 29), (42, 30), (40, 31), (38, 32),
           (36, 33), (34, 31), (32, 31), (30, 31), (28, 32), (26, 34),
           (24, 36), (22, 37), (20, 39), (18, 40), (16, 41), (14, 42),
           (12, 44), (10, 44), (8, 44), (6, 43), (4, 43), (2, 42),
           (0, 40), (-2, 37), (-5, 36), (-8, 37), (-9, 37)]
AUSTRALIA = [(113, -22), (114, -28), (115, -32), (117, -35), (121, -34),
             (124, -33), (127, -32), (130, -32), (132, -32), (134, -33),
             (136, -35), (138, -35), (140, -38), (143, -39), (146, -39),
             (149, -37), (151, -34), (153, -31), (153, -27), (152, -24),
             (150, -22), (147, -19), (145, -17), (143, -14), (142, -11),
             (141, -13), (138, -15), (136, -12), (134, -12), (132, -12),
             (130, -13), (128, -14), (126, -14), (124, -15), (122, -17),
             (120, -19), (117, -20), (114, -21), (113, -22)]
GREENLAND = [(-45, 60), (-40, 64), (-35, 66), (-30, 68), (-25, 70),
             (-20, 70), (-22, 74), (-30, 76), (-40, 76), (-50, 75),
             (-58, 72), (-55, 68), (-52, 64), (-48, 61), (-45, 60)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-3, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37), (140, 39),
         (141, 41), (142, 43), (144, 44), (142, 42), (140, 38), (138, 36),
         (135, 34), (132, 33), (130, 31)]
NZ = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
      (175, -40), (173, -42), (170, -44), (167, -46), (167, -45)]
CONTINENTS = [N_AMERICA, S_AMERICA, AFRICA, EURASIA, AUSTRALIA, GREENLAND,
              UK, JAPAN, NZ]


def chaikin(pts, rounds=1):
    """Smooth a closed polygon by Chaikin corner-cutting (deterministic)."""
    out = list(pts)
    for _ in range(rounds):
        new = []
        n = len(out)
        for i in range(n):
            p0 = out[i]
            p1 = out[(i + 1) % n]
            new.append((p0[0] * 0.75 + p1[0] * 0.25,
                        p0[1] * 0.75 + p1[1] * 0.25))
            new.append((p0[0] * 0.25 + p1[0] * 0.75,
                        p0[1] * 0.25 + p1[1] * 0.75))
        out = new
    return out


def project(lon, lat, x, y, w, h):
    """Equirectangular projection into a box (lon -180..180, lat 75..-58)."""
    px = x + (lon + 180.0) / 360.0 * w
    py = y + (75.0 - lat) / 133.0 * h
    return px, py


def draw_map(d, x, y, w, h, pins):
    """World map with numbered pins. pins: (lon, lat, label, dx, dy)."""
    sky_bands(d, x, y, w, h, (148, 188, 214), (118, 166, 196))
    for lon in range(-165, 181, 15):
        px, _ = project(lon, 0, x, y, w, h)
        d.line([(px, y), (px, y + h - 1)], fill=GRID, width=1)
    for lat in range(-45, 76, 15):
        _, py = project(0, lat, x, y, w, h)
        d.line([(x, py), (x + w - 1, py)], fill=GRID, width=1)
    for poly in CONTINENTS:
        pts = list(poly)
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        pts = chaikin(pts, rounds=3 if len(pts) >= 30 else 2)
        pp = [project(lon, lat, x, y, w, h) for lon, lat in pts]
        d.polygon(pp, fill=LAND)
        d.line(pp + [pp[0]], fill=LAND_LINE, width=2, joint="curve")
    f_num = F(F_SANS_B, 10)
    f_lab = F(F_SANS_B, 13)
    for i, (lon, lat, label, dx, dy) in enumerate(pins, 1):
        px, py = project(lon, lat, x, y, w, h)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        num = str(i)
        d.text((px - d.textlength(num, font=f_num) / 2, py - 7), num,
               font=f_num, fill=(255, 255, 255))
        lx, ly = px + dx, py + dy
        d.text((lx, ly), label, font=f_lab, fill=INK,
               stroke_width=1, stroke_fill=(236, 226, 196))


# ---------------------------------------------------------------- data
HEROES = [
    ("Iran hits US bases as Gulf war widens",
     "Missiles and drones hit US positions in Bahrain; Kuwait on alert.",
     "AP • REPORTED 22 NOV", art_gulf),
    ("Mexico captures 'El Chapo Isidro'; 11 killed",
     "Troops storm a Sinaloa hideout and seize the FBI's most-wanted drug lord.",
     "REUTERS • REPORTED 22 NOV", art_mexico),
    ("COP31 deadlocked as talks run into overtime",
     "Nearly 200 nations split over fossil fuels in Antalya; no deal yet.",
     "AL JAZEERA • REPORTED 22 NOV", art_cop),
]

SMALL = [
    ("FBI probes suspected hack of crime database", "REPORTED • USA", "db"),
    ("Fire at Iraq power station kills 4, injures 35",
     "IRAQI STATE MEDIA", "fire"),
    ("Toxic alcohol kills 11 in Manipur", "INDIA • OFFICIAL", "bottle"),
    ("Florida river breaks 73-year flood record", "USA • CONFIRMED", "flood"),
    ("Russian ship hit by drones; crew evacuated", "AL JAZEERA", "ship"),
    ("15 militants killed in Balochistan raid", "XINHUA", "raid"),
    ("Factory fire in Indonesia: 3 dead, 30 missing", "XINHUA", "factory"),
    ("Trump vows 10% cap on credit-card rates", "USA • REPORTED", "capitol"),
    ("Australia edge Wales in rugby thriller", "SPORT • OCEANIA", "rugby"),
    ("France reach final after beating Argentina", "SPORT • EUROPE", "trophy"),
]

NUMBERS = [
    ("200", "nations deadlocked\nat COP31"),
    ("15", "militants killed\nin Balochistan"),
    ("11", "killed as Mexico\nseizes cartel boss"),
    ("10%", "Trump's cap on\ncredit-card rates"),
    ("5,300", "DRC Ebola death\ntoll passed"),
    ("73", "years: St. Johns\nRiver record broken"),
]

REGIONS = [("Middle East", 7, (179, 64, 46)),
           ("Americas", 8, (46, 109, 180)),
           ("Europe", 7, (46, 125, 91)),
           ("Africa", 6, (201, 138, 27)),
           ("Asia", 4, (122, 74, 158)),
           ("Oceania", 2, (31, 138, 138)),
           ("Global", 1, (85, 85, 85))]

PINS = [
    (56.5, 26.5, "1 Hormuz tankers", 10, -4),
    (28.0, -26.0, "2 S. Africa vote", 10, -4),
    (46.0, 2.0, "3 Somalia ambush", 10, -4),
    (10.0, 60.0, "4 Norway ruling", 12, -4),
    (105.0, 12.5, "5 Cambodia", 10, -4),
    (8.7, 50.1, "6 ECB chief hunt", -122, -4),
    (-77.0, 38.9, "7 Trump orders", 12, 16),
]

ALSO = [
    "Ghana unveils Heritage banknotes honouring Nkrumah",
    "S\u00e3o Tom\u00e9: Am\u00e9rico Ramos reappointed prime minister",
    "Sahel states restart dialogue with West Africa bloc",
    "Nigeria starts building naval ships at home",
    "Storms batter the California coast",
    "Sacramento Republic win the USL Championship",
    "New Senate Democrats promise change as vote looms",
    "Alcaraz to face Zverev in ATP Finals decider",
    "Evanilson scores in a sixth straight league game",
    "Pezeshkian: Iran in 'silent economic war'",
    "Turkish minister: war fallout threatens markets",
    "Group urges Germany to arrest Israeli soldier",
    "Settlers attack Palestinian homes in Hebron",
    "Turkey: Israel blocking container homes for Gaza",
    "Australia bowl first; Smith misses S. Africa decider",
]

DATE_CHECK = (
    "DATE CHECK \u2014 LEFT OUT ON PURPOSE: the Trump\u2013Xi\u2013Putin Shenzhen "
    "summit (19 Nov), the World Court's Myanmar ruling (19 Nov) and "
    "Anthropic's $81.3bn debut (19 Nov) all happened before Sunday. "
    "Also out: Peru's M6.9 quake (20 Nov), Estonia's border decision "
    "(20 Nov) and the third Kerch Bridge strike (19 Nov).")


# ---------------------------------------------------------------- layout
MX, CW = 16, 992
HERO_KICK = ["WAR IN THE GULF", "MEXICO", "CLIMATE"]


def hero_card(d, x, y, w, h, hero, kick):
    head, deck, tag, art = hero
    art(d, x, y, w, 118)
    d.rectangle([x, y, x + w - 1, y + 117], outline=INK, width=1)
    f_kick = F(F_SANS_B, 10)
    d.text((x, y + 126), kick, font=f_kick, fill=RED)
    f_head = F(F_SERIF_B, 20)
    lines = wrap(d, head, f_head, w)
    yy = y + 142
    for line in lines:
        d.text((x, yy), line, font=f_head, fill=INK)
        yy += 24
    f_deck = F(F_SANS, 13)
    yy = para(d, x, yy + 4, deck, f_deck, w, 16, fill=SOFT)
    f_tag = F(F_SANS_B, 10)
    d.text((x, y + h - 16), tag, font=f_tag, fill=INK)


def small_card(d, x, y, w, h, item):
    head, tag, kind = item
    art_mini(d, x, y, w, 42, kind)
    d.rectangle([x, y, x + w - 1, y + 41], outline=INK, width=1)
    size = 14
    while size > 11:
        f_head = F(F_SERIF_B, size)
        if len(wrap(d, head, f_head, w)) <= 2:
            break
        size -= 1
    yy = y + 48
    for line in wrap(d, head, f_head, w):
        d.text((x, yy), line, font=f_head, fill=INK)
        yy += 17
    d.text((x, y + h - 14), tag, font=F(F_SANS_B, 9), fill=RED)


def region_bar(d, y):
    f_lab = F(F_SANS_B, 12)
    d.text((MX, y), "THE DAY BY REGION", font=f_lab, fill=INK)
    rule(d, MX, y + 16, CW, 2)
    total = sum(n for _, n, _ in REGIONS)
    bx, bw, bh = MX, CW, 12
    by = y + 20
    cx = bx
    for _, n, col in REGIONS:
        seg = int(round(n / total * bw))
        d.rectangle([cx, by, cx + seg - 1, by + bh - 1], fill=col)
        cx += seg
    d.rectangle([bx, by, bx + bw - 1, by + bh - 1], outline=INK, width=1)
    parts, widths = [], []
    f_leg = F(F_SANS, 11)
    for name, n, col in REGIONS:
        parts.append((name, n, col))
        widths.append(d.textlength(name + " " + str(n) + "   ", font=f_leg))
    total_w = sum(widths) - d.textlength("   ", font=f_leg)
    lx = MX + (CW - total_w) / 2
    ly = by + bh + 6
    for (name, n, col), wdt in zip(parts, widths):
        d.rectangle([lx, ly + 2, lx + 8, ly + 10], fill=col)
        d.text((lx + 12, ly), name + " ", font=f_leg, fill=INK)
        nx = lx + 12 + d.textlength(name + " ", font=f_leg)
        d.text((nx, ly), str(n), font=F(F_SANS_B, 11), fill=INK)
        lx += wdt


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    paper_texture(d)
    # masthead
    rule(d, MX, 8, CW, 5)
    rule(d, MX, 15, CW, 2)
    centre(d, W // 2, 20, "THE WORLD IN ONE PICTURE  \u2022  SUNDAY EDITION",
           F(F_SANS_B, 15))
    f_date = fit(d, "Sunday 22 November 2026", F_SERIF_B, 62, CW)
    centre(d, W // 2, 42, "Sunday 22 November 2026", f_date)
    centre(d, W // 2, 110,
           "War widens in the Gulf, a cartel kingpin falls in Mexico, "
           "and the climate talks stall.",
           F(F_SERIF_I, 19), fill=SOFT)
    rule(d, MX, 136, CW, 3)
    rule(d, MX, 141, CW, 2)
    # heroes
    for i, hero in enumerate(HEROES):
        x = MX + i * (322 + 13)
        hero_card(d, x, 148, 322, 250, hero, HERO_KICK[i])
    for sx in (MX + 322 + 6, MX + 2 * 322 + 13 + 6):
        d.line([(sx, 148), (sx, 398)], fill=(150, 135, 100), width=2)
    # numbers strip
    f_sec = F(F_SANS_B, 12)
    d.rectangle([MX, 403, MX + CW - 1, 420], fill=INK)
    d.text((MX + 8, 406), "THE DAY IN NUMBERS", font=f_sec, fill=PAPER)
    rule(d, MX, 422, CW, 1, fill=(160, 145, 110))
    cell_w = CW // 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = MX + i * cell_w
        centre(d, cx + cell_w // 2, 426, num, F(F_SERIF_B, 30))
        for j, ln in enumerate(label.split("\n")):
            centre(d, cx + cell_w // 2, 456 + j * 12, ln, F(F_SANS, 10),
                   fill=SOFT)
        if i:
            d.line([(cx, 428), (cx, 472)], fill=(160, 145, 110), width=1)
    # region bar
    region_bar(d, 480)
    # small cards, two rows of five
    for row in range(2):
        for col in range(5):
            item = SMALL[row * 5 + col]
            x = MX + col * (192 + 8)
            y = 536 + row * (99 + 8)
            small_card(d, x, y, 192, 99, item)
    # column rules between the small cards (newspaper gutters)
    for col in range(1, 5):
        sx = MX + col * 200 - 4
        d.line([(sx, 536), (sx, 742)], fill=(160, 145, 110), width=1)
    rule(d, MX, 639, CW, 1, fill=(160, 145, 110))
    # map + also
    d.rectangle([MX, 747, MX + 491, 764], fill=INK)
    d.text((MX + 8, 750), "WHERE IT HAPPENED", font=f_sec, fill=PAPER)
    draw_map(d, MX, 768, 492, 180, PINS)
    d.rectangle([MX, 768, MX + 491, 947], outline=INK, width=2)
    ax = 520
    d.rectangle([ax, 747, MX + CW - 1, 764], fill=INK)
    d.text((ax + 8, 750), "ALSO ON SUNDAY\u2026", font=f_sec, fill=PAPER)
    f_also = F(F_SANS, 11)
    f_num = F(F_SANS_B, 11)
    ay = 770
    for i, item in enumerate(ALSO, 1):
        d.text((ax, ay), str(i) + ".", font=f_num, fill=RED)
        d.text((ax + 22, ay), item, font=f_also, fill=INK)
        ay += 13
    rule(d, MX, 962, CW, 2, fill=(160, 145, 110))
    # date check
    d.rectangle([MX, 970, MX + CW - 1, 1001], fill=RED_BG, outline=RED,
                width=2)
    para(d, MX + 12, 973, DATE_CHECK, F(F_SANS, 11), CW - 24, 13, fill=INK)
    # footer
    centre(d, W // 2, 1007,
           "Every story here happened, or was first reported, on Sunday "
           "22 November 2026  \u2022  All artwork is original drawings",
           F(F_SANS, 11), fill=SOFT)
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    img = build()
    out = os.path.join(here, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
