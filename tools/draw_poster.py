#!/usr/bin/env python3
"""Draws entry.png: one-image summary of world news, Wednesday 25 November 2026.

Build-time tool only (needs Pillow and the Liberation fonts). The contest
program is main.ts, which copies the committed entry.png to the output dir.
Everything is drawn from primitives here: no photos, no logos, no downloads.

Run:  python3 tools/draw_poster.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersampling factor
W = H = 1024
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = "/usr/share/fonts/truetype/liberation/"

PAPER = (245, 240, 228)
INK = (22, 22, 30)
RED = (200, 32, 38)
GOLD = (255, 204, 77)
WHITE = (255, 255, 255)
MUTED = (92, 88, 84)

_fonts = {}


def font(name, size):
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_DIR + name + ".ttf", int(round(size * S)))
    return _fonts[key]


def sans(size):
    return font("LiberationSans-Regular", size)


def bold(size):
    return font("LiberationSans-Bold", size)


def serif(size):
    return font("LiberationSerif-Bold", size)


def P(*v):
    """Scale 1024-space numbers to the supersampled canvas."""
    return tuple(int(round(x * S)) for x in v)


def text_w(d, s, f):
    return d.textlength(s, font=f) / S


def fit(d, s, maker, size, max_w):
    """Largest font size <= size at which s fits in max_w."""
    while size > 8 and text_w(d, s, maker(size)) > max_w:
        size -= 1
    return maker(size)


def put(d, x, y, s, f, fill, anchor="la"):
    d.text(P(x, y), s, font=f, fill=fill, anchor=anchor)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(img, x0, y0, x1, y1, stops):
    """Vertical gradient through (position, colour) stops."""
    d = ImageDraw.Draw(img)
    X0, Y0, X1, Y1 = P(x0, y0, x1, y1)
    for y in range(Y0, Y1):
        t = (y - Y0) / max(1, Y1 - Y0 - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                d.line([(X0, y), (X1 - 1, y)], fill=lerp(c0, c1, (t - p0) / (p1 - p0)))
                break


# ---------------------------------------------------------------- masthead
def masthead(img, d):
    d.rectangle(P(0, 0, W, 76), fill=PAPER)
    put(d, W / 2, 40, "THE WORLD TODAY", serif(62), INK, "mm")
    for x0, x1 in ((24, 196), (828, 1000)):
        d.rectangle(P(x0, 30, x1, 33), fill=INK)
        d.rectangle(P(x0, 45, x1, 47), fill=INK)
    d.rectangle(P(0, 76, W, 120), fill=RED)
    put(d, W / 2, 98, "WEDNESDAY  25 NOVEMBER 2026", bold(31), WHITE, "mm")


# ------------------------------------------------------------- lead: space
def flag_china(d, x, y, w, h):
    d.rectangle(P(x, y, x + w, y + h), fill=(222, 41, 16))
    star(d, x + w * 0.18, y + h * 0.28, h * 0.19, (255, 222, 0))
    for dx, dy in ((0.36, 0.12), (0.43, 0.25), (0.43, 0.42), (0.36, 0.55)):
        star(d, x + w * dx, y + h * dy, h * 0.065, (255, 222, 0))


def flag_pakistan(d, x, y, w, h):
    d.rectangle(P(x, y, x + w, y + h), fill=(1, 65, 28))
    d.rectangle(P(x, y, x + w * 0.25, y + h), fill=WHITE)
    cx, cy, r = x + w * 0.62, y + h * 0.5, h * 0.3
    d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=WHITE)
    r2 = r * 0.86
    ox, oy = cx + r * 0.22, cy - r * 0.2
    d.ellipse(P(ox - r2, oy - r2, ox + r2, oy + r2), fill=(1, 65, 28))
    star(d, cx + r * 0.42, cy - r * 0.38, h * 0.11, WHITE)


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.4
        pts.append(P(cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def rocket(d, cx, top):
    """Long March-style crewed rocket, nose at (cx, top)."""
    body = (236, 238, 242)
    shade = (176, 182, 196)
    # escape tower
    d.rectangle(P(cx - 1.5, top, cx + 1.5, top + 30), fill=shade)
    d.polygon([P(cx, top - 6), P(cx - 4, top + 6), P(cx + 4, top + 6)], fill=body)
    # fairing
    d.polygon([P(cx, top + 24), P(cx - 15, top + 62), P(cx + 15, top + 62)], fill=body)
    d.rectangle(P(cx - 15, top + 62, cx + 15, top + 100), fill=body)
    # taper + core stage
    d.polygon([P(cx - 15, top + 100), P(cx + 15, top + 100), P(cx + 12, top + 112), P(cx - 12, top + 112)], fill=shade)
    d.rectangle(P(cx - 12, top + 112, cx + 12, top + 232), fill=body)
    d.rectangle(P(cx + 4, top + 62, cx + 15, top + 100), fill=shade)
    d.rectangle(P(cx + 5, top + 112, cx + 12, top + 232), fill=shade)
    d.rectangle(P(cx - 12, top + 150, cx + 12, top + 158), fill=RED)
    d.rectangle(P(cx - 12, top + 196, cx + 12, top + 201), fill=(40, 44, 60))
    # boosters
    for sx in (-1, 1):
        bx = cx + sx * 19
        d.polygon([P(bx, top + 158), P(bx - 7, top + 176), P(bx + 7, top + 176)], fill=body)
        d.rectangle(P(bx - 7, top + 176, bx + 7, top + 236), fill=body if sx < 0 else shade)
        d.polygon([P(bx - 7, top + 236), P(bx + 7, top + 236), P(bx + 10, top + 246), P(bx - 10, top + 246)], fill=(60, 64, 80))
    d.polygon([P(cx - 12, top + 232), P(cx + 12, top + 232), P(cx + 14, top + 244), P(cx - 14, top + 244)], fill=(60, 64, 80))
    return top + 244


def flame(d, cx, y0, y1):
    for wdt, col in ((34, (255, 120, 20)), (24, (255, 176, 40)), (14, (255, 232, 130)), (7, (255, 255, 235))):
        d.polygon([P(cx - wdt, y0), P(cx + wdt, y0), P(cx + wdt * 0.5, y0 + (y1 - y0) * 0.55), P(cx, y1),
                   P(cx - wdt * 0.5, y0 + (y1 - y0) * 0.55)], fill=col)


def smoke(d, cx, base):
    puffs = [(-150, 6, 46), (-112, -8, 50), (-70, -20, 56), (-30, -30, 58), (10, -34, 60), (52, -26, 56),
             (96, -14, 52), (134, 0, 46), (-90, 18, 54), (-40, 14, 60), (14, 10, 64), (70, 16, 58), (118, 22, 48)]
    for dx, dy, r in puffs:
        d.ellipse(P(cx + dx - r, base + dy - r, cx + dx + r, base + dy + r), fill=(214, 186, 170))
    for dx, dy, r in puffs:
        r2 = r * 0.72
        d.ellipse(P(cx + dx - r2 - 6, base + dy - r2 - 8, cx + dx + r2 - 6, base + dy + r2 - 8), fill=(246, 226, 204))
    # warm glow where the exhaust meets the pad, widest at the bottom
    for i, col in enumerate(((255, 214, 150), (255, 190, 104), (255, 236, 190))):
        rx, ry = 62 - i * 18, 30 - i * 8
        d.ellipse(P(cx - rx, base - 12 - ry, cx + rx, base - 12 + ry), fill=col)


def station(d, cx, cy, k):
    """Small T-shaped space station silhouette with solar wings."""
    hull = (232, 234, 240)
    wing = (86, 140, 220)
    d.rounded_rectangle(P(cx - 30 * k, cy - 5 * k, cx + 30 * k, cy + 5 * k), radius=int(4 * k * S), fill=hull)
    d.rounded_rectangle(P(cx - 5 * k, cy - 5 * k, cx + 5 * k, cy + 26 * k), radius=int(4 * k * S), fill=hull)
    for sx in (-1, 1):
        x0 = cx + sx * 34 * k
        x1 = cx + sx * 66 * k
        d.rectangle(P(min(x0, x1), cy - 9 * k, max(x0, x1), cy + 9 * k), fill=wing)
        for j in range(1, 4):
            xx = x0 + (x1 - x0) * j / 4
            d.line([P(xx, cy - 9 * k), P(xx, cy + 9 * k)], fill=(30, 60, 120), width=S)
        d.rectangle(P(min(cx + sx * 30 * k, x0), cy - 1.5 * k, max(cx + sx * 30 * k, x0), cy + 1.5 * k), fill=hull)


def lead(img, d):
    y0, y1 = 120, 604
    horizon = 548
    vgrad(img, 0, y0, W, horizon, [(0.0, (8, 10, 40)), (0.5, (30, 28, 96)), (0.8, (96, 48, 120)),
                                    (0.93, (226, 110, 60)), (1.0, (255, 200, 110))])
    # stars: fixed lattice with a small deterministic jitter
    seed = 12345
    for i in range(110):
        seed = (seed * 1103515245 + 12345) % 2147483648
        sx = seed % 1024
        seed = (seed * 1103515245 + 12345) % 2147483648
        sy = y0 + 6 + seed % 250
        seed = (seed * 1103515245 + 12345) % 2147483648
        r = 0.8 + (seed % 10) / 10.0
        d.ellipse(P(sx - r, sy - r, sx + r, sy + r), fill=(235, 235, 255))
    # desert floor and distant dunes
    d.rectangle(P(0, horizon, W, y1), fill=(34, 24, 36))
    d.polygon([P(0, horizon), P(120, horizon - 14), P(300, horizon), P(520, horizon - 10), P(760, horizon),
               P(900, horizon - 16), P(W, horizon - 4), P(W, horizon + 6), P(0, horizon + 6)], fill=(58, 34, 52))
    # launch tower
    tx = 74
    d.rectangle(P(tx - 13, 356, tx + 13, horizon + 6), fill=(24, 20, 34))
    for yy in range(366, horizon, 26):
        d.line([P(tx - 13, yy), P(tx + 13, yy + 26)], fill=(120, 80, 90), width=2 * S)
        d.line([P(tx + 13, yy), P(tx - 13, yy + 26)], fill=(120, 80, 90), width=2 * S)
    d.rectangle(P(tx + 13, 400, tx + 46, 406), fill=(24, 20, 34))
    d.rectangle(P(tx + 13, 460, tx + 40, 466), fill=(24, 20, 34))
    # rocket, exhaust, smoke
    cx = 186
    tail = rocket(d, cx, 168)
    smoke(d, cx, horizon + 8)
    flame(d, cx, tail, horizon + 2)
    for sx in (-19, 19):
        flame_small(d, cx + sx, tail + 2, tail + 70)
    # trajectory to the station
    pts = []
    for i in range(0, 41):
        t = i / 40
        x = 200 + (884 - 200) * t
        y = 164 - 24 * math.sin(math.pi * t) - (164 - 158) * t
        pts.append((x, y))
    for i in range(1, 40, 2):
        x, y = pts[i]
        d.ellipse(P(x - 3, y - 3, x + 3, y + 3), fill=GOLD)
    station(d, 946, 158, 0.72)
    put(d, 946, 190, "TIANGONG", bold(13), (214, 220, 240), "mt")
    # words
    tx0, maxw = 330, 668
    put(d, tx0, 186, "SPACE  \u00b7  JIUQUAN, CHINA  \u00b7  08:18", bold(22), GOLD)
    f = fit(d, "FIRST PAKISTANI", bold, 90, maxw)
    put(d, tx0 - 3, 216, "FIRST PAKISTANI", f, WHITE)
    put(d, tx0 - 3, 216 + f.size / S * 1.02, "IN ORBIT", f, WHITE)
    by = 216 + f.size / S * 2.1 + 10
    for i, line in enumerate(("Shenzhou-24 lifts off with Zeeshan Ali,",
                              "first foreign astronaut bound for",
                              "China\u2019s Tiangong space station")):
        put(d, tx0, by + i * 37, line, sans(31), WHITE)
    # crew line sits on the dark desert floor, clear of the bright horizon and the smoke
    cx0, fy = 392, 559
    flag_china(d, cx0, fy, 54, 36)
    flag_pakistan(d, cx0 + 64, fy, 54, 36)
    put(d, cx0 + 134, fy + 18, "Crew: Tang Hongbo \u00b7 Wu Yi \u00b7 Zeeshan Ali", bold(23), (255, 240, 214), "lm")


def flame_small(d, cx, y0, y1):
    for wdt, col in ((9, (255, 140, 30)), (5, (255, 226, 130))):
        d.polygon([P(cx - wdt, y0), P(cx + wdt, y0), P(cx, y1)], fill=col)


# ------------------------------------------------------------------- cards
def pic_markets(d, x, y, w, h):
    d.rectangle(P(x, y, x + w, y + h), fill=(16, 24, 44))
    for i in range(1, 4):
        yy = y + h * i / 4
        d.line([P(x, yy), P(x + w, yy)], fill=(44, 56, 86), width=S)
    vals = [0.2, 0.16, 0.26, 0.22, 0.36, 0.33, 0.5, 0.46, 0.66, 0.62, 0.84]
    pts = [(x + 12 + (w * 0.5) * i / (len(vals) - 1), y + 8 + (h - 30) * v) for i, v in enumerate(vals)]
    d.polygon([P(*p) for p in pts] + [P(pts[-1][0], y + h), P(pts[0][0], y + h)], fill=(96, 22, 34))
    d.line([P(*p) for p in pts], fill=(255, 70, 70), width=4 * S, joint="curve")
    ex, ey = pts[-1]
    d.polygon([P(ex + 12, ey + 10), P(ex - 6, ey + 6), P(ex + 8, ey - 8)], fill=(255, 70, 70))
    put(d, x + w - 12, y + 12, "SEOUL", bold(17), (200, 208, 228), "ra")
    put(d, x + w - 12, y + 32, "\u22125.3%", bold(40), (255, 86, 86), "ra")
    put(d, x + w - 12, y + 82, "TAIPEI \u22125.1%", bold(17), (255, 150, 150), "ra")


def pic_pacific(d, x, y, w, h):
    d.rectangle(P(x, y, x + w, y + h), fill=(18, 96, 150))
    for j in range(5):
        yy = y + 16 + j * 24
        for i in range(0, 8):
            xx = x + 6 + i * 40 + (j % 2) * 16
            if xx + 22 > x + w - 4:
                continue  # keep every wave inside the picture frame
            d.arc(P(xx, yy, xx + 22, yy + 10), 180, 360, fill=(70, 150, 200), width=2 * S)
    # island chain
    for cx, cy, rx, ry in ((40, 34, 24, 9), (88, 52, 30, 11), (140, 76, 26, 10), (62, 88, 18, 7)):
        d.ellipse(P(x + cx - rx, y + cy - ry, x + cx + rx, y + cy + ry), fill=(226, 204, 140))
        d.ellipse(P(x + cx - rx + 4, y + cy - ry + 2, x + cx + rx - 4, y + cy + ry - 3), fill=(64, 150, 84))
    # shield with tick
    sx, sy = x + w - 74, y + 14
    d.polygon([P(sx, sy), P(sx + 56, sy), P(sx + 56, sy + 50), P(sx + 28, sy + 92), P(sx, sy + 50)], fill=WHITE)
    d.polygon([P(sx + 6, sy + 6), P(sx + 50, sy + 6), P(sx + 50, sy + 48), P(sx + 28, sy + 82), P(sx + 6, sy + 48)],
              fill=(22, 60, 120))
    d.line([P(sx + 15, sy + 38), P(sx + 25, sy + 50), P(sx + 42, sy + 22)], fill=GOLD, width=6 * S, joint="curve")


def pic_cyber(d, x, y, w, h):
    d.rectangle(P(x, y, x + w, y + h), fill=(26, 20, 34))
    seed = 777
    for row in range(6):
        for col in range(20):
            seed = (seed * 1103515245 + 12345) % 2147483648
            if seed % 3 == 0:
                continue
            bit = "1" if seed % 2 else "0"
            put(d, x + 10 + col * 15.4, y + 6 + row * 18, bit, bold(13), (56, 110, 86))
    # monitor
    mx, my, mw, mh = x + w / 2 - 74, y + 12, 148, 82
    d.rounded_rectangle(P(mx, my, mx + mw, my + mh), radius=6 * S, fill=(210, 214, 224))
    d.rectangle(P(mx + 7, my + 7, mx + mw - 7, my + mh - 7), fill=(120, 16, 24))
    d.rectangle(P(x + w / 2 - 10, my + mh, x + w / 2 + 10, my + mh + 10), fill=(210, 214, 224))
    d.rectangle(P(x + w / 2 - 34, my + mh + 10, x + w / 2 + 34, my + mh + 15), fill=(210, 214, 224))
    # open padlock
    px, py = x + w / 2 - 42, my + 36
    d.arc(P(px + 4, py - 24, px + 32, py + 8), 180, 380, fill=WHITE, width=5 * S)
    d.rectangle(P(px + 27.5, py - 10, px + 32, py - 2), fill=(120, 16, 24))
    d.rounded_rectangle(P(px - 2, py, px + 30, py + 26), radius=3 * S, fill=WHITE)
    d.ellipse(P(px + 10, py + 8, px + 18, py + 16), fill=(120, 16, 24))
    # warning triangle
    wx, wy = x + w / 2 + 34, my + 22
    d.polygon([P(wx, wy), P(wx + 26, wy + 44), P(wx - 26, wy + 44)], fill=GOLD)
    put(d, wx, wy + 27, "!", bold(30), (60, 20, 20), "mm")


def card(d, x, y, w, pic, tag, tag_col, head, lines):
    pic(d, x, y, w, 118)
    d.rectangle(P(x, y + 118, x + w, y + 123), fill=tag_col)
    put(d, x, y + 134, tag, bold(17), tag_col)
    f = fit(d, head, bold, 32, w)   # one size for all three so the row reads evenly
    put(d, x, y + 159, head, f, INK)
    for i, line in enumerate(lines):
        put(d, x, y + 203 + i * 27, line, fit(d, line, sans, 22, w), (46, 44, 48))


def cards(img, d):
    y = 620
    w, gap = 314, 17
    x = 24
    card(d, x, y, w, pic_markets, "MARKETS \u00b7 ASIA", (190, 30, 40), "ASIA STOCKS SLIDE",
         ("US tariff threat hits chip-heavy", "markets: Seoul and Taipei down", "over 5% at the lows, Tokyo 2.9%"))
    x += w + gap
    card(d, x, y, w, pic_pacific, "PACIFIC \u00b7 SECURITY", (14, 100, 160), "PACIFIC PACT SIGNED",
         ("Australia becomes Solomon", "Islands\u2019 main security partner,", "a setback for China"))
    x += w + gap
    card(d, x, y, w, pic_cyber, "UNITED STATES \u00b7 CYBER", (120, 40, 130), "CIA HIT BY HACK",
         ("Unclassified system breached,", "sources say; officials report", "no classified data affected"))
    d.rectangle(P(24 + w + 8, y, 24 + w + 9, y + 290), fill=(198, 190, 174))
    d.rectangle(P(24 + 2 * w + gap + 8, y, 24 + 2 * w + gap + 9, y + 290), fill=(198, 190, 174))


# ------------------------------------------------------------------ briefs
def briefs(img, d):
    d.rectangle(P(0, 922, W, 1000), fill=(24, 24, 34))
    d.rectangle(P(24, 936, 150, 986), fill=GOLD)
    put(d, 87, 951, "ALSO", bold(19), INK, "mm")
    put(d, 87, 972, "TODAY", bold(19), INK, "mm")
    put(d, 166, 950, "AUSTRALIA formally apologises to LGBTQ veterans for decades of military bans",
        fit(d, "AUSTRALIA formally apologises to LGBTQ veterans for decades of military bans", sans, 21, 834), WHITE, "lm")
    put(d, 166, 975, "DR CONGO: Ebola team evacuated after three days trapped in Ituri hospital, WHO says",
        fit(d, "DR CONGO: Ebola team evacuated after three days trapped in Ituri hospital, WHO says", sans, 21, 834), WHITE, "lm")
    d.rectangle(P(0, 1000, W, H), fill=PAPER)
    put(d, W / 2, 1012, "ONE DAY\u2019S WORLD NEWS  \u00b7  WEDNESDAY 25 NOVEMBER 2026  \u00b7  AS REPORTED BY REUTERS, XINHUA, CNN, WHO",
        bold(13), MUTED, "mm")


def main():
    img = Image.new("RGB", P(W, H), PAPER)
    d = ImageDraw.Draw(img)
    lead(img, d)
    masthead(img, d)
    d.rectangle(P(0, 604, W, 922), fill=PAPER)
    cards(img, d)
    briefs(img, d)
    out = img.resize((W, H), Image.LANCZOS)
    path = os.path.join(ROOT, "entry.png")
    out.save(path, "PNG", optimize=True)
    print(path, os.path.getsize(path), out.size)


if __name__ == "__main__":
    main()
