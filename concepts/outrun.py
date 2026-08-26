"""Outrun horizon concept: striped sun, mountain silhouettes, racing perspective grid.
Pixel title uses the same bitmap pipeline as pixel.py."""
import random
from PIL import Image, ImageDraw, ImageFont

FONT = "../fonts/PressStart2P.ttf"
W, H = 1200, 340
HORIZON = 212
TP = 8

SKY = [(0, 58, "#14062E"), (58, 108, "#2A0C4E"), (108, 148, "#4A1160"),
       (148, 184, "#7A1E5C"), (184, HORIZON, "#B23268")]
FLOOR = "#12041F"
GRID = "#FF7FA8"
MOUNT_FAR = "#1A0A2E"
MOUNT_NEAR = "#0D0518"
STAR = ["#FFFFFF", "#CFE0FF", "#FFD9F0"]

rnd = random.Random(11)
out = []


def r(x, y, w, h, fill, cls="", style="", extra=""):
    c = f' class="{cls}"' if cls else ""
    s = f' style="{style}"' if style else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{c}{s}{extra}/>')


def bitmap(text, size=8):
    f = ImageFont.truetype(FONT, size)
    w = max(1, int(f.getlength(text))) + 2
    im = Image.new("L", (w, size * 2), 0)
    ImageDraw.Draw(im).text((0, 0), text, font=f, fill=255)
    px = im.load()
    on = {(x, y) for y in range(im.height) for x in range(im.width) if px[x, y] > 110}
    if not on:
        return set(), 0, 0
    miny = min(y for _, y in on)
    minx = min(x for x, _ in on)
    on = {(x - minx, y - miny) for x, y in on}
    return on, max(x for x, _ in on) + 1, max(y for _, y in on) + 1


def runs(on):
    byrow = {}
    for x, y in on:
        byrow.setdefault(y, []).append(x)
    for y in sorted(byrow):
        xs = sorted(byrow[y])
        s = prev = xs[0]
        for x in xs[1:]:
            if x != prev + 1:
                yield s, y, prev - s + 1
                s = x
            prev = x
        yield s, y, prev - s + 1


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
           f'height="{H}" shape-rendering="crispEdges" role="img" '
           f'aria-label="Muhammad Junaid, design build ship">')
out.append('''<style>
.tw{animation:tw 3.4s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}
.gl{animation:gl 2.2s ease-in infinite;opacity:0}
@keyframes gl{0%{transform:translateY(0) scaleY(.2);opacity:0}12%{opacity:1}100%{transform:translateY(128px) scaleY(1);opacity:1}}
.ch{opacity:0;animation:pop .34s cubic-bezier(.2,1.6,.4,1) forwards}
@keyframes pop{0%{opacity:0;transform:translateY(-14px)}100%{opacity:1;transform:translateY(0)}}
.sb{opacity:0;animation:fin .5s ease-out 1.4s forwards}
@keyframes fin{to{opacity:1}}
.sun{animation:sun 5s ease-in-out infinite}
@keyframes sun{0%,100%{opacity:.85}50%{opacity:1}}
@media (prefers-reduced-motion:reduce){.tw,.gl,.ch,.sb,.sun{animation:none;opacity:1;transform:none}}
</style>''')
out.append(f'<clipPath id="c"><rect width="{W}" height="{H}" rx="10"/></clipPath><g clip-path="url(#c)">')

# sky
for a, b, col in SKY:
    r(0, a, W, b - a, col)
# dither seams on a 4px grid
for i, (a, b, col) in enumerate(SKY[1:]):
    for x in range(0, W, 16):
        r(x + (i % 3) * 4, a - 4, 4, 4, col)

# stars
for _ in range(56):
    x, y = rnd.randrange(0, W // 4) * 4, rnd.randrange(0, 120 // 4) * 4
    s = 4 if rnd.random() < 0.8 else 8
    r(x, y, s, s, rnd.choice(STAR), cls="tw", style=f"animation-delay:{rnd.uniform(0, 3.4):.2f}s")

# sun: pixel half-disc with stripes coloured by the band behind them
def band_at(y):
    for a, b, col in SKY:
        if a <= y < b:
            return col
    return FLOOR

import math
cx = 600                      # grid vanishing point
scx, rad = 884, 116           # sun sits off-centre, outrun style
stripe_top = HORIZON - 72
for y in range(HORIZON - rad, HORIZON, 4):
    dy = HORIZON - y
    half = int(math.sqrt(max(rad * rad - dy * dy, 0)))
    half = (half // 4) * 4
    # stripes: growing gaps toward the bottom of the sun
    if y >= stripe_top and ((y - stripe_top) // 4) % max(2, 6 - (y - stripe_top) // 16) == 0:
        continue
    t = (y - (HORIZON - rad)) / rad
    col = "#FFD166" if t < 0.45 else ("#FF9A5A" if t < 0.75 else "#FF5E7E")
    r(scx - half, y, half * 2, 4, col, cls="sun")

# mountains: stepped pixel silhouettes on the horizon
def range_line(seed, base, peak_min, peak_max, col):
    g = random.Random(seed)
    x, y = -8, base - g.randrange(peak_min, peak_max)
    heights = []
    while x < W + 8:
        heights.append((x, y))
        x += 8
        y += g.choice([-8, -4, 0, 4, 8])
        y = max(base - peak_max, min(base - 4, y))
    for hx, hy in heights:
        r(hx, hy, 8, base - hy, col)

range_line(3, HORIZON, 8, 40, MOUNT_FAR)
range_line(8, HORIZON, 4, 24, MOUNT_NEAR)

# floor + grid
r(0, HORIZON, W, H - HORIZON, FLOOR)
# vertical rays from the vanishing point (drawn as 4px steps, faded near the horizon)
for k in range(-7, 8):
    bx = cx + k * 150
    steps = (H - HORIZON) // 4
    for i in range(3, steps):
        y = HORIZON + i * 4
        t = (i + 1) / steps
        x = int(cx + (bx - cx) * t) // 4 * 4
        r(x, y, 4, 4, GRID, style=f"opacity:{0.2 + 0.5 * t:.2f}")
# horizontal scan lines racing toward the viewer
for i in range(4):
    out.append(f'<g class="gl" style="animation-delay:{i * 0.55:.2f}s;transform-origin:600px {HORIZON}px">')
    r(0, HORIZON + 2, W, 4, GRID)
    out.append('</g>')
# horizon glow
r(0, HORIZON - 2, W, 2, "#FFB9D2")

# title with a pixel chrome gradient: light top rows, hot bottom rows
name = "MUHAMMAD JUNAID"
cw = 8
total = len(name) * cw * TP
ox = (W - total) // 2
oy = 56
CHROME = ["#F4F8FF", "#F4F8FF", "#CFE0FF", "#9FB6FF", "#FF9ECF", "#FF7FA8", "#FF5E7E", "#FF5E7E"]
for i, ch in enumerate(name):
    if ch == " ":
        continue
    on, gw, gh = bitmap(ch, 8)
    out.append(f'<g class="ch" style="animation-delay:{0.05 + i * 0.045:.2f}s">')
    for sx, sy, ln in runs(on):
        r(ox + (i * cw + sx) * TP + TP, oy + sy * TP + TP, ln * TP, TP, "#2A0C4E")
    for sx, sy, ln in runs(on):
        r(ox + (i * cw + sx) * TP, oy + sy * TP, ln * TP, TP, CHROME[min(sy, len(CHROME) - 1)])
    out.append('</g>')

sub = "DESIGN / BUILD / SHIP"
on, gw, gh = bitmap(sub, 8)
sx0 = (W - gw * 4) // 2
out.append('<g class="sb">')
for sx, sy, ln in runs(on):
    r(sx0 + sx * 4 + 4, 144 + sy * 4, ln * 4, 4, "#2A0C4E")
for sx, sy, ln in runs(on):
    r(sx0 + sx * 4, 140 + sy * 4, ln * 4, 4, "#6FE3D4")
out.append('</g>')

out.append('</g></svg>')
open("outrun.svg", "w").write("\n".join(out))
print("rects:", sum(1 for l in out if l.startswith("<rect")))
