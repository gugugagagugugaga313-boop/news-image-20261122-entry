#!/usr/bin/env python3
"""Draw one image summing up the world news of Sunday 22 November 2026.

Stdlib only. Writes a deterministic 1024x1024 PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
Layout: newspaper front page. Masthead names the day, six labelled
story panels cover climate, conflict, security, politics, economy
and sport, and a footer strip carries two briefs.

FINAL stories: researched after 22 Nov 2026 ended everywhere
(23 Nov 19:00 WIB) and cross-checked date by date against
multiple outlets. Every story pictured happened, or was first
reported, on Sunday 22 November 2026.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (247, 241, 227)
NAVY = (22, 40, 63)
NAVY_LIGHT = (38, 62, 92)
GOLD = (201, 162, 39)
INK = (24, 24, 24)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)

# tag, accent colour, icon, headline, one-line detail
# FINAL stories: researched after the day ended everywhere
# (23 Nov 19:00 WIB) and cross-checked date by date. Every story
# below happened, or was first reported, on Sunday 22 Nov 2026.
# Stories that failed the date check were dropped: the Shenzhen
# summit (19 Nov), the US AI sell-off (20 Nov), the Mexico cartel
# capture (20-21 Nov), the EU-Indonesia signing (21 Nov), the
# Bahrain/Hormuz strikes (21 Nov), the Kryvyi Rih strike (20 Nov),
# the ICJ Myanmar ruling (19 Nov), the Thai court ruling (23 Nov)
# and the Nigeria boat toll (announced 21 Nov).
STORIES = [
    ("CLIMATE", (14, 124, 107), "globe",
     "COP31 COLLAPSES WITHOUT DEAL",
     "Antalya climate talks end with no pact as fossil fuel language is rejected."),
    ("CONFLICT", (179, 55, 47), "flame",
     "KYIV FLATS HIT, 14 MISSING",
     "Russian drone collapses a block in Dymer, and rescuers dig for the missing."),
    ("SECURITY", (91, 74, 138), "shield",
     "POLAND: RAPPER TARGETED TWICE",
     "Poland says Moscow tried to kill Kyivstoner in Poland and Denmark."),
    ("POLITICS", (42, 95, 163), "flags",
     "NEPAL PM HEADS TO INDIA",
     "Balen Shah leaves for Delhi for a two-day state visit and talks with Modi."),
    ("ECONOMY", (201, 106, 27), "chart",
     "CHINA EASES MARGIN RULES",
     "Exchanges cut the minimum margin ratio to 80% from 100% on Nov 30."),
    ("SPORT", (62, 122, 52), "ball",
     "ALCARAZ WINS ATP FINALS",
     "Beats Zverev for his first ATP Finals title in Turin."),
]

HEADLINE = "COP31 COLLAPSES AS KYIV IS HIT"
FOOTER_MAIN = "ALL EVENTS REPORTED ON SUNDAY 22 NOVEMBER 2026"
FOOTER_BRIEFS = "BRIEFS: WEST BANK SETTLERS TORCH 12 CARS - CIKANDE FIRE, 24 BODIES FOUND"

# 5x7 bitmap font, '#' = ink. Only the glyphs the layout uses.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def rect(self, x, y, w, h, c, t=2):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d = math.sqrt(dx * dx + dy * dy)
                if r - t <= d <= r:
                    self.set(cx + dx, cy + dy, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, c):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def draw_text_centred(self, cx, y, text, scale, c):
        w = self.text_width(text, scale)
        self.draw_text(cx - w // 2, y, text, scale, c)

    def wrap(self, text, max_w, scale):
        lines = []
        cur = ""
        for word in text.split(" "):
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def draw_icon(cv, kind, x, y, s, c):
    """Simple pictogram inside a square of side s at (x, y)."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "globe":
        cv.ring(cx, cy, s // 2 - 4, c, 4)
        cv.vline(cx, y + 6, s - 12, c, 3)
        cv.hline(x + 6, cy, s - 12, c, 3)
        cv.ring(cx, cy, s // 4, c, 3)
    elif kind == "flame":
        cv.fill_poly([(cx, y + 4), (cx + 26, cy + 18), (cx + 12, cy + 8),
                      (cx + 20, cy + 34), (cx, cy + 44), (cx - 20, cy + 34),
                      (cx - 12, cy + 8), (cx - 26, cy + 18)], c)
        cv.disc(cx, cy + 22, 10, GOLD)
    elif kind == "shield":
        cv.fill_poly([(x + 8, y + 8), (x + s - 8, y + 8), (x + s - 8, y + 46),
                      (cx, y + s - 8), (x + 8, y + 46)], c)
        cv.draw_text_centred(cx, cy - 8, "!", 4, WHITE)
    elif kind == "flags":
        for i, col in enumerate((c, GOLD, NAVY_LIGHT)):
            px = x + 14 + i * 26
            cv.vline(px, y + 10, s - 20, INK, 3)
            cv.fill_rect(px + 3, y + 12, 22, 16, col)
    elif kind == "chart":
        heights = [66, 48, 58, 30]
        for i, hh in enumerate(heights):
            cv.fill_rect(x + 10 + i * 22, y + s - 10 - hh, 16, hh, c)
        cv.hline(x + 6, y + s - 10, s - 12, INK, 3)
    elif kind == "deal":
        cv.ring(cx - 16, cy, 22, c, 5)
        cv.ring(cx + 16, cy, 22, GOLD, 5)
        cv.disc(cx, cy, 8, c)
    elif kind == "ball":
        cv.ring(cx, cy, s // 2 - 6, c, 5)
        cv.hline(x + 8, cy, s - 16, c, 3)
        cv.disc(cx, cy, 8, c)


def draw_panel(cv, x, y, w, h, story):
    tag, accent, icon, title, detail = story
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, NAVY, 2)
    cv.fill_rect(x, y, w, 32, accent)
    cv.draw_text(x + 14, y + 8, tag, 2, WHITE)
    draw_icon(cv, icon, x + 16, y + 48, 84, accent)
    lines = cv.wrap(title, w - 132, 3)
    ty = y + 52
    for ln in lines[:2]:
        cv.draw_text(x + 116, ty, ln, 3, INK)
        ty += 24
    dlines = cv.wrap(detail, w - 32, 2)
    dy = y + 148
    for ln in dlines[:3]:
        cv.draw_text(x + 16, dy, ln, 2, GREY)
        dy += 18


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    cv = Canvas(W, H, CREAM)
    # Masthead.
    cv.fill_rect(0, 0, W, 150, NAVY)
    cv.hline(0, 150, W, GOLD, 4)
    cv.draw_text_centred(W // 2, 22, "THE WORLD IN ONE DAY", 5, WHITE)
    cv.draw_text_centred(W // 2, 82, "SUNDAY, 22 NOVEMBER 2026", 5, GOLD)
    # Headline strip.
    cv.draw_text_centred(W // 2, 166, HEADLINE, 3, INK)
    cv.hline(16, 202, W - 32, NAVY, 2)
    # Six story panels, 2 columns x 3 rows.
    pw, ph, gap = 488, 224, 16
    for i, story in enumerate(STORIES):
        px = 16 + (i % 2) * (pw + gap)
        py = 216 + (i // 2) * (ph + gap)
        draw_panel(cv, px, py, pw, ph, story)
    # Footer.
    fy = 928
    cv.fill_rect(0, fy, W, H - fy, NAVY)
    cv.draw_text_centred(W // 2, fy + 16, FOOTER_MAIN, 3, WHITE)
    cv.draw_text_centred(W // 2, fy + 56, FOOTER_BRIEFS, 2, GOLD)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(cv)
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes %dx%d" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
