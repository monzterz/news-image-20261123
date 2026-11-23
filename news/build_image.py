#!/usr/bin/env python3
"""Draw "23 November 2026, in one image": a one-page world news summary.

The image is judged by a vision model against other entries, on one day's news, breadth across
regions, whether a viewer can read what happened, faithfulness and craft. So the drawing is a
front page, not an illustration: the date is the largest thing on it, the lead story carries a
picture and a sentence, and four more stories run down the page with a pictogram each and a label
short enough to read when the whole image is 300 px across.

Every fact here was reported on 23 November 2026 (Reuters, AP, Guardian, Democracy Now, Anadolu,
Euronews); the copy stays with what those reports said.

    python3 news/build_image.py --out entry.png
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (245, 240, 230)
INK = (20, 17, 15)
BODY = (58, 52, 47)
MUTED = (110, 103, 94)
RULE = (214, 206, 192)
RED = (200, 16, 46)
STEEL = (54, 74, 94)
LIGHTSTEEL = (78, 100, 122)
SEA = (36, 58, 78)
WINDOW = (255, 206, 128)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf"
SANS_B = str(Path.home() / "makefun-work/fonts/Inter-Bold.ttf")
SANS = str(Path.home() / "makefun-work/fonts/Inter-Regular.ttf")
MONO_B = str(Path.home() / "makefun-work/fonts/JetBrainsMono-Bold.ttf")

MARGIN = 46
COL_TEXT = 640


def f(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def tracked(d, xy, text, font, fill, tracking=3):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x - tracking


def wrap(text: str, font, width: float) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if font.getlength(candidate) <= width or not line:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def star(d, cx, cy, r, fill, points=9, inner=0.42, rot=-math.pi / 2):
    pts = []
    for i in range(points * 2):
        ang = rot + i * math.pi / points
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def icon_warship(d, x, y, s=1.0):
    """A corvette at a quay under drone attack: sea, hull, burst, and the drone boat coming in."""
    def P(px, py):
        return (x + px * s, y + py * s)

    d.rectangle([*P(0, 196), *P(330, 278)], fill=SEA)
    for i, wy in enumerate((216, 240, 262)):
        d.line([P(14 + 14 * i, wy), P(316 - 12 * i, wy)], fill=(60, 92, 118), width=3)
    # the corvette: hull, deck, funnel, mast
    d.polygon([P(40, 138), P(262, 138), P(228, 186), P(66, 186)], fill=STEEL)
    d.rectangle([*P(88, 106), *P(208, 138)], fill=LIGHTSTEEL)
    d.rectangle([*P(142, 78), *P(170, 106)], fill=STEEL)
    d.line([P(156, 78), P(156, 44)], fill=STEEL, width=4)
    d.line([P(156, 48), P(190, 58)], fill=STEEL, width=3)
    d.rectangle([*P(66, 186), *P(228, 194)], fill=(31, 44, 58))
    # the drone boat, small and fast, running in
    d.polygon([P(266, 196), P(300, 208), P(266, 220)], fill=RED)
    d.line([P(292, 208), P(330, 204)], fill=(250, 250, 250), width=3)
    # the round that lands
    star(d, *P(196, 116), 32 * s, RED, points=11, inner=0.36)
    star(d, *P(196, 116), 14 * s, WINDOW, points=8, inner=0.45)


def icon_thermometer(d, x, y, s=1.0):
    """Climate: a warming globe beside a thermometer past the mark."""
    def P(px, py):
        return (x + px * s, y + py * s)

    d.ellipse([*P(16, 34), *P(146, 164)], outline=STEEL, width=5)
    for lat in (62, 82, 100, 118, 136):
        d.line([P(22, lat), P(140, lat)], fill=RULE, width=2)
    d.arc([*P(16, 34), *P(146, 164)], 200, 340, fill=RULE, width=2)
    d.rounded_rectangle([*P(178, 12), *P(206, 126)], radius=14, fill=PAPER, outline=INK, width=4)
    d.rounded_rectangle([*P(184, 54), *P(200, 120)], radius=8, fill=RED)
    d.ellipse([*P(168, 112), *P(216, 160)], fill=RED, outline=INK, width=4)
    d.line([P(220, 34), P(244, 34)], fill=RED, width=4)
    d.line([P(220, 50), P(240, 50)], fill=RED, width=3)


def icon_hormuz(d, x, y, s=1.0):
    """A tanker struck: hull, deck tanks, a missile trail into it."""
    def P(px, py):
        return (x + px * s, y + py * s)

    d.rectangle([*P(0, 148), *P(250, 178)], fill=SEA)
    d.polygon([P(18, 92), P(200, 92), P(180, 146), P(36, 146)], fill=STEEL)
    for tx in (48, 90, 132):
        d.rectangle([*P(tx, 62), *P(tx + 30, 92)], fill=LIGHTSTEEL)
    d.polygon([P(176, 92), P(212, 92), P(206, 116), P(176, 116)], fill=LIGHTSTEEL)
    d.line([P(18, 146), P(200, 146)], fill=(31, 44, 58), width=4)
    d.line([P(236, 2), P(190, 78)], fill=RED, width=5)
    d.line([P(226, 8), P(204, 52)], fill=(255, 170, 120), width=2)
    star(d, *P(182, 82), 24 * s, RED, points=10, inner=0.38)


def icon_fire(d, x, y, s=1.0):
    """A factory blaze: roof line, windows lit, flames above."""
    def P(px, py):
        return (x + px * s, y + py * s)

    d.rectangle([*P(14, 96), *P(214, 168)], fill=STEEL)
    d.polygon([P(14, 96), P(74, 66), P(74, 96)], fill=STEEL)
    d.rectangle([*P(130, 50), *P(166, 96)], fill=LIGHTSTEEL)
    for wx in (32, 64, 96, 128, 160, 186):
        d.rectangle([*P(wx, 114), *P(wx + 16, 136)], fill=WINDOW)
    for fx, fh, fw, colour in ((58, 62, 44, RED), (108, 84, 50, (232, 88, 40)), (164, 56, 40, RED)):
        top = 96 - fh
        d.polygon(
            [P(fx - fw / 2, 96), P(fx - fw / 3, top + fh * 0.42), P(fx, top),
             P(fx + fw / 3, top + fh * 0.45), P(fx + fw / 2, 96)],
            fill=colour,
        )
    d.rectangle([*P(12, 168), *P(216, 176)], fill=INK)


def icon_capitol(d, x, y, s=1.0):
    """US politics: the Capitol's dome and columns, a flag on top."""
    def P(px, py):
        return (x + px * s, y + py * s)

    d.ellipse([*P(74, 8), *P(138, 70)], fill=STEEL)
    d.rectangle([*P(74, 54), *P(138, 78)], fill=STEEL)
    d.polygon([P(90, 90), P(122, 90), P(126, 76), P(86, 76)], fill=STEEL)
    d.rectangle([*P(18, 90), *P(194, 102)], fill=STEEL)
    d.rectangle([*P(12, 102), *P(200, 114)], fill=LIGHTSTEEL)
    for cx in range(24, 192, 22):
        d.rectangle([*P(cx, 114), *P(cx + 10, 160)], fill=STEEL)
    d.rectangle([*P(6, 160), *P(206, 176)], fill=(31, 44, 58))
    d.line([P(106, 8), P(106, 0)], fill=INK, width=4)
    d.polygon([P(106, 0), P(128, 6), P(106, 12)], fill=RED)


STORIES = [
    ("CLIMATE", "COP31 summit ends with no deal", icon_thermometer),
    ("MIDDLE EAST", "Three more ships struck off Iran", icon_hormuz),
    ("ASIA", "Indonesia fire kills 24; 30 missing", icon_fire),
    ("UNITED STATES", "Democrats win 258 House seats", icon_capitol),
]


def draw(out: Path) -> None:
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # --- masthead -----------------------------------------------------------------
    tracked(d, (MARGIN, 38), "WORLD NEWS IN ONE IMAGE", f(MONO_B, 26), MUTED, tracking=4)
    monday = f(MONO_B, 26)
    mx = W - MARGIN - monday.getlength("MONDAY")
    d.text((mx, 36), "MONDAY", font=monday, fill=RED)
    d.rectangle([mx, 68, W - MARGIN, 71], fill=RED)
    d.text((MARGIN - 5, 66), "23 November 2026", font=f(SERIF_B, 90), fill=INK)
    d.rectangle([MARGIN, 186, W - MARGIN, 191], fill=INK)

    # --- lead ---------------------------------------------------------------------
    tracked(d, (MARGIN, 210), "LEAD  ·  LIBYA  ·  UKRAINE", f(MONO_B, 26), RED, tracking=3)
    head = f(SERIF_B, 58)
    y = 250
    for line in wrap("Ukraine sinks a Russian warship in Libya", head, COL_TEXT):
        d.text((MARGIN - 2, y), line, font=head, fill=INK)
        y += 64
    sub = f(SANS, 30)
    y += 8
    for line in wrap("Seven sea drones hit the corvette Merkury at Benghazi; Libya wants a UN inquiry.",
                     sub, COL_TEXT):
        d.text((MARGIN, y), line, font=sub, fill=BODY)
        y += 38
    icon_warship(d, x=700, y=206, s=0.95)

    # --- the four briefs ----------------------------------------------------------
    top = 528
    for i, (tag, headline, icon) in enumerate(STORIES):
        cy = top + i * 110
        body = f(SANS_B, 40)
        d.text((MARGIN - 2, cy), headline, font=body, fill=INK)
        d.rectangle([MARGIN, cy + 54, MARGIN + 3, cy + 74], fill=RED)
        d.text((MARGIN + 12, cy + 52), tag, font=f(MONO_B, 24), fill=RED)
        icon(d, x=796, y=cy + 4, s=0.56)
        if i < len(STORIES) - 1:
            d.rectangle([MARGIN, cy + 96, W - MARGIN, cy + 97], fill=RULE)

    # --- foot ---------------------------------------------------------------------
    d.rectangle([MARGIN, 968, W - MARGIN, 971], fill=RULE)
    foot = f(MONO_B, 22)
    tracked(d, (MARGIN, 982), "AS REPORTED ON 23 NOVEMBER 2026", foot, MUTED, tracking=2)
    stamp = "FIVE STORIES"
    d.text((W - MARGIN - foot.getlength(stamp), 982), stamp, font=foot, fill=RED)

    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "PNG", optimize=True)
    print(f"{out}: {im.size[0]}x{im.size[1]}, {out.stat().st_size} bytes")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="entry.png")
    a = ap.parse_args()
    draw(Path(a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
