#!/usr/bin/env python3
"""Draw the news-image-20261119-r2 front page: one image summing up
Thursday 19 November 2026 as a one-page newspaper.

Deterministic: no randomness, no clock, no network, fixed strings.
Output: entry.png next to this script (1024x1024, PNG, stdlib-free
of Pillow at grading time -- this script itself uses Pillow only
to *produce* the image here; main.py ships it with stdlib only).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
M = 36                      # side margin
CW = W - 2 * M              # 952 content width
PAPER = (247, 242, 231)     # #F7F2E7
INK = (17, 17, 17)          # #111111
RED = (166, 30, 30)         # #A61E1E
NAVY = (31, 58, 95)         # #1F3A5F
GREY = (90, 84, 72)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Greedy word wrap by pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, fnt, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def fit_size(text, path, start, max_w, minimum=10):
    """Largest size <= start whose text fits max_w (single line)."""
    size = start
    while size > minimum and font(path, size).getlength(text) > max_w:
        size -= 1
    return size


def star_points(cx, cy, r_outer, r_inner, rotation=-90):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(rotation + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_star(d, cx, cy, r, fill):
    d.polygon(star_points(cx, cy, r, r * 0.42), fill=fill)


def draw_courthouse(d, x0, y0, x1, y1):
    """Simple columned courthouse facade inside box (x0,y0)-(x1,y1)."""
    cx = (x0 + x1) // 2
    w = x1 - x0
    h = y1 - y0
    # steps at the bottom
    step_h = 7
    for i in range(3):
        sw = w - i * 26
        d.rectangle([cx - sw // 2, y1 - (3 - i) * step_h,
                     cx + sw // 2, y1 - (2 - i) * step_h], fill=NAVY)
    base_y = y1 - 3 * step_h
    # columns
    col_w, col_h = 14, int(h * 0.44)
    col_top = base_y - col_h
    n = 5
    span = w - 90
    for i in range(n):
        cx_i = x0 + 45 + i * span // (n - 1)
        d.rectangle([cx_i - col_w // 2, col_top, cx_i + col_w // 2, base_y],
                    fill=NAVY)
    # entablature
    ent_h = 12
    d.rectangle([x0 + 40, col_top - ent_h, x1 - 40, col_top], fill=NAVY)
    # pediment (triangle, narrower than the facade) + medallion
    apex_y = y0 + 12
    d.polygon([(x0 + 40, col_top - ent_h), (x1 - 40, col_top - ent_h),
               (cx, apex_y)], fill=NAVY)
    d.ellipse([cx - 7, apex_y + 12, cx + 7, apex_y + 26], fill=PAPER)
    # door
    d.rectangle([cx - 16, base_y - 26, cx + 16, base_y], fill=PAPER)


def draw_scales(d, cx, top, height):
    """Scales of justice centred at cx, from y=top, total height."""
    beam_y = top + 14
    half = 62
    pole_w = 5
    # pole + base
    d.rectangle([cx - pole_w // 2, top, cx + pole_w // 2, top + height - 8],
                fill=INK)
    d.rectangle([cx - 26, top + height - 8, cx + 26, top + height - 2],
                fill=INK)
    # finial
    d.ellipse([cx - 5, top - 6, cx + 5, top + 4], fill=RED)
    # beam
    d.rectangle([cx - half, beam_y - 3, cx + half, beam_y + 3], fill=INK)
    for sx in (cx - half, cx + half):
        # hanger lines
        d.line([(sx, beam_y), (sx - 20, beam_y + 34)], fill=INK, width=2)
        d.line([(sx, beam_y), (sx + 20, beam_y + 34)], fill=INK, width=2)
        d.line([(sx, beam_y), (sx, beam_y + 34)], fill=INK, width=2)
        # pan (half-disc)
        d.pieslice([sx - 22, beam_y + 30, sx + 22, beam_y + 74],
                   start=0, end=180, fill=RED)


def draw_flag_us(d, x, y, w, h):
    stripe = h / 7
    for i in range(7):
        if i % 2 == 0:
            d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                        fill=(178, 34, 52))
    canton_w, canton_h = w * 0.42, stripe * 4
    d.rectangle([x, y, x + canton_w, y + canton_h], fill=NAVY)
    for r in range(3):
        for c in range(4):
            px = x + 6 + c * (canton_w - 10) / 3
            py = y + 6 + r * (canton_h - 10) / 2
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=PAPER)


def draw_flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw_star(d, x + w * 0.22, y + h * 0.30, 9, (255, 222, 0))
    for sx, sy in ((0.52, 0.16), (0.64, 0.30), (0.60, 0.52), (0.46, 0.62)):
        draw_star(d, x + w * sx, y + h * sy, 3.5, (255, 222, 0))


def draw_flag_ru(d, x, y, w, h):
    for i, col in enumerate(((255, 255, 255), (0, 57, 166), (213, 0, 50))):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=col)
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def draw_flags(d, x0, y0, x1, y1):
    """Three small flags on poles: US, China, Russia."""
    n = 3
    slot = (x1 - x0) // n
    fw, fh = 84, 50
    pole_top = y0 + 6
    pole_bot = y1 - 4
    painters = (draw_flag_us, draw_flag_cn, draw_flag_ru)
    labels = ("USA", "CHINA", "RUSSIA")
    for i, paint in enumerate(painters):
        fx = x0 + i * slot + (slot - fw) // 2
        fy = pole_top + 4
        d.line([(fx, pole_top), (fx, pole_bot)], fill=INK, width=3)
        d.ellipse([fx - 3, pole_top - 4, fx + 3, pole_top + 2], fill=RED)
        paint(d, fx + 3, fy, fw, fh)
        d.rectangle([fx + 3, fy, fx + 3 + fw, fy + fh], outline=INK, width=1)
        lf = font(SANS_B, 11)
        lab = labels[i]
        d.text((fx + 3 + fw / 2 - lf.getlength(lab) / 2, fy + fh + 8),
               lab, font=lf, fill=GREY)


def draw_chart(d, x0, y0, x1, y1):
    """Rising line chart with axes and a $83 label."""
    d.rectangle([x0, y0, x1, y1], outline=GREY, width=1)
    # horizontal gridlines
    for i in range(1, 4):
        gy = y0 + i * (y1 - y0) // 4
        d.line([(x0, gy), (x1, gy)], fill=(210, 203, 186), width=1)
    # axes
    d.line([(x0, y1 - 1), (x1, y1 - 1)], fill=INK, width=2)
    d.line([(x0, y0), (x0, y1)], fill=INK, width=2)
    pts = [(0.00, 0.78), (0.12, 0.72), (0.24, 0.74), (0.36, 0.60),
           (0.48, 0.62), (0.60, 0.44), (0.72, 0.46), (0.84, 0.26),
           (0.94, 0.16), (1.00, 0.08)]
    xy = [(x0 + 8 + p[0] * (x1 - x0 - 16), y0 + 8 + p[1] * (y1 - y0 - 16))
          for p in pts]
    d.line(xy, fill=NAVY, width=4, joint="curve")
    ex, ey = xy[-1]
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=RED)
    lf = font(SANS_B, 20)
    d.text((ex - 58, ey - 10), "$83", font=lf, fill=RED)
    sf = font(SANS, 12)
    d.text((x0 + 4, y1 - 16), "IPO DAY", font=sf, fill=GREY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle([14, 14, W - 15, H - 15], outline=INK, width=2)

    # ---- masthead ----
    title_f = font(SERIF_B, 62)
    d.text((W // 2, 26), "THE WORLD IN ONE DAY", font=title_f,
           fill=INK, anchor="ma")
    d.line([(M, 104), (W - M, 104)], fill=INK, width=3)
    d.line([(M, 110), (W - M, 110)], fill=INK, width=1)

    # ---- date line ----
    dl_f = font(SANS_B, 19)
    d.text((M, 120), "THURSDAY, 19 NOVEMBER 2026", font=dl_f, fill=INK)
    dr_f = font(SANS, 15)
    d.text((W - M, 123), "ONE PAGE · THE DAY'S WORLD NEWS",
           font=dr_f, fill=INK, anchor="ra")
    d.line([(M, 148), (W - M, 148)], fill=INK, width=1)

    T = 160  # content top
    # vertical divider between main story and right column
    d.line([(660, T), (660, 540)], fill=(200, 192, 172), width=1)

    # ---- main story (left) ----
    kick_f = font(SANS_B, 17)
    d.text((M, T), "THE HAGUE · WORLD COURT", font=kick_f, fill=RED)
    head_f = font(SERIF_B, 40)
    head_lines = wrap("MYANMAR COMMITTED GENOCIDE, WORLD COURT RULES",
                      head_f, 612)
    y = draw_lines(d, M, T + 26, head_lines, head_f, INK, 48)
    deck_f = font(SANS, 20)
    deck_lines = wrap("The International Court of Justice finds Myanmar "
                      "responsible for genocide against the Rohingya in "
                      "2017 and orders restitution.", deck_f, 612)
    y = draw_lines(d, M, y + 8, deck_lines, deck_f, INK, 26)
    # illustration: courthouse left, scales right (placed below the deck,
    # never overlapping it)
    iy0 = y + 10
    draw_courthouse(d, M, iy0, M + 380, 540)
    draw_scales(d, M + 500, iy0 + 6, 540 - iy0 - 6)

    # ---- right column: summit ----
    RX, RW = 676, 312
    d.text((RX, T), "SHENZHEN · SUMMIT", font=kick_f, fill=RED)
    rhead_f = font(SERIF_B, 29)
    rhead_lines = wrap("Trump, Xi and Putin meet in Shenzhen", rhead_f, RW)
    y = draw_lines(d, RX, T + 26, rhead_lines, rhead_f, INK, 35)
    rdeck_f = font(SANS, 17)
    rdeck_lines = wrap("First three-way summit issues a 'Declaration "
                       "toward Peace' and pledges nuclear-risk talks — "
                       "but no major deal.", rdeck_f, RW)
    y = draw_lines(d, RX, y + 6, rdeck_lines, rdeck_f, INK, 22)
    draw_flags(d, RX, 396, RX + RW, 540)

    # ---- middle band: Anthropic IPO ----
    d.line([(M, 552), (W - M, 552)], fill=INK, width=2)
    BY = 564
    d.text((M, BY), "MARKETS · ARTIFICIAL INTELLIGENCE", font=kick_f,
           fill=RED)
    bhead_f = font(SERIF_B, 29)
    bhead_lines = wrap("Anthropic's $83 debut values AI firm at "
                       "$1.5 trillion", bhead_f, 620)
    y = draw_lines(d, M, BY + 26, bhead_lines, bhead_f, INK, 35)
    bdeck_f = font(SANS, 18)
    bdeck_lines = wrap("Record offering of 980 million shares; Nasdaq "
                       "trading begins Thursday.", bdeck_f, 620)
    draw_lines(d, M, y + 6, bdeck_lines, bdeck_f, INK, 23)
    draw_chart(d, 700, BY + 8, W - M, 700)

    # ---- grid: 2 rows x 3 cols ----
    d.line([(M, 712), (W - M, 712)], fill=INK, width=2)
    items = [
        ("BANGLADESH", "Violence spreads to 28 districts",
         "Yunus's ancestral home set on fire."),
        ("COP31 · ANTALYA", "Ministers race to unblock climate talks",
         "Negotiators push for a final text."),
        ("GAZA", "Aid groups score peace plan 4 of 26",
         "New evacuation orders in Gaza."),
        ("HAITI", "Police operation kills 34 gang suspects",
         "Major sweep in Port-au-Prince."),
        ("VAN GOGH", "Van Gogh sells for $190.4m",
         "A record price for the artist."),
        ("GREENLAND", "Denmark ratifies US security pact",
         "109 lawmakers vote yes."),
    ]
    col_w, gap = 304, 20
    gkick_f = font(SANS_B, 14)
    ghead_f = font(SANS_B, 19)
    gdeck_f = font(SANS, 16)
    for idx, (kick, head, deck) in enumerate(items):
        row, col = divmod(idx, 3)
        gx = M + col * (col_w + gap)
        gy = 724 + row * 100
        d.text((gx, gy), kick, font=gkick_f, fill=RED)
        hlines = wrap(head, ghead_f, col_w)
        yy = draw_lines(d, gx, gy + 20, hlines[:2], ghead_f, INK, 22)
        # deck: single line, shrink font if needed to fit
        dsize = 16
        while (dsize > 13 and
               font(SANS, dsize).getlength(deck) > col_w):
            dsize -= 1
        d.text((gx, yy + 3), deck, font=font(SANS, dsize), fill=INK)
        if col < 2:
            vx = gx + col_w + gap // 2
            d.line([(vx, gy), (vx, gy + 88)], fill=(200, 192, 172), width=1)
    d.line([(M, 932), (W - M, 932)], fill=INK, width=1)

    # ---- markets strip ----
    strip = ("MARKETS 19 NOV — S&P 500 7,323.63 -0.23% · Nasdaq 24,429.88 "
             "+0.42% · Nikkei 59,444.21 +0.71% · Brent $89.59 -2.57% · "
             "Gold $3,739.60 -0.06%")
    ssize = fit_size(strip, SANS_B, 16, CW)
    sf = font(SANS_B, ssize)
    d.text((W // 2, 942), strip, font=sf, fill=NAVY, anchor="ma")

    # ---- footer ----
    ff = font(SANS, 14)
    d.text((W // 2, 972), "The world in one page — Thursday 19 November 2026",
           font=ff, fill=GREY, anchor="ma")

    img.save(OUT, format="PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
