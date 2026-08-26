"""Animated pixel-art banner. Everything snaps to a 4px grid; the title uses 8px blocks."""
import random
from PIL import Image, ImageDraw, ImageFont

FONT = "fonts/PressStart2P.ttf"
W, H = 1200, 340
P = 4                      # scene pixel
TP = 8                     # title pixel

SKY = ["#0A0E24", "#141A3C", "#22214F", "#3A2A5E", "#5C3363"]
GLOW = ["#8E3A64", "#C25473", "#E8825F"]
CITY_FAR = "#272C60"
CITY_NEAR = "#0A0B1E"
WIN = ["#FFD166", "#FFB347", "#6FE3D4", "#FF7FA8"]
STAR = ["#FFFFFF", "#CFE0FF", "#FFE9A8"]
TITLE = "#FFFFFF"
TITLE_SHADOW = "#C2426F"
SUB = "#8DA2DE"

rnd = random.Random(7)
out = []


def r(x, y, w, h, fill, cls="", style="", extra=""):
    c = f' class="{cls}"' if cls else ""
    s = f' style="{style}"' if style else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{c}{s}{extra}/>')


def bitmap(text, size=8):
    """Return set of on-pixels for text rendered at its native pixel size."""
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
    """Merge horizontal runs so we emit far fewer rects."""
    byrow = {}
    for x, y in on:
        byrow.setdefault(y, []).append(x)
    for y in sorted(byrow):
        xs = sorted(byrow[y])
        s = xs[0]
        prev = xs[0]
        for x in xs[1:]:
            if x != prev + 1:
                yield s, y, prev - s + 1
                s = x
            prev = x
        yield s, y, prev - s + 1


# ---------------------------------------------------------------- sky
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
           f'height="{H}" shape-rendering="crispEdges" role="img" '
           f'aria-label="Muhammad Junaid, senior forward deployed engineer">')
out.append('''<style>
.tw{animation:tw 3.4s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}
.wn{animation:wn 8s steps(1,end) infinite}
@keyframes wn{0%,42%{opacity:1}43%,52%{opacity:.12}53%,100%{opacity:1}}
.ch{opacity:0;animation:pop .34s cubic-bezier(.2,1.6,.4,1) forwards}
@keyframes pop{0%{opacity:0;transform:translateY(-14px)}100%{opacity:1;transform:translateY(0)}}
.sb{opacity:0;animation:fin .5s ease-out 1.5s forwards}
@keyframes fin{to{opacity:1}}
.cr{opacity:0;animation:cr 1.05s steps(1,end) 1.9s infinite}
@keyframes cr{0%,50%{opacity:1}51%,100%{opacity:0}}
.cl{animation-name:cl;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes cl{0%{transform:translateX(-460px)}100%{transform:translateX(1260px)}}
.sh{animation:sh 9s linear infinite}
@keyframes sh{0%{transform:translate(0,0);opacity:0}4%{opacity:1}16%{transform:translate(-360px,180px);opacity:0}100%{transform:translate(-360px,180px);opacity:0}}
@media (prefers-reduced-motion:reduce){.tw,.wn,.ch,.sb,.cr,.sh,.cl{animation:none;opacity:1}}
</style>''')
out.append(f'<clipPath id="c"><rect width="{W}" height="{H}" rx="10"/></clipPath><g clip-path="url(#c)">')

bands = [(0, 24), (24, 40), (40, 50), (50, 56), (56, 60)]
for (a, b), col in zip(bands, SKY):
    r(0, a * P, W, (b - a) * P, col)
# light dither on the seams so the bands read as a gradient, not stripes
for (a, b), col in list(zip(bands, SKY))[1:]:
    for x in range(0, W // P, 4):
        r((x + (a % 3)) * P, (a - 1) * P, P, P, col)
for i, col in enumerate(GLOW):
    r(0, (54 + i * 2) * P, W, 2 * P, col)

# drifting clouds, stepped silhouettes so they read as clouds not bars
def cloud(x, y, L, tone):
    r(x * P, (y + 2) * P, L * P, P, tone)
    r((x + 2) * P, (y + 1) * P, (L - 4) * P, P, tone)
    for bx, bw in ((3, 5), (10, 7), (19, 4)):
        if bx + bw < L:
            r((x + bx) * P, y * P, bw * P, P, tone)

for cy, dur, delay, tone in ((9, 58, 0, "#1B2149"), (23, 82, -34, "#232A57")):
    out.append(f'<g class="cl" style="animation-duration:{dur}s;animation-delay:{delay}s">')
    cloud(0, cy, 26, tone)
    cloud(46, cy + 2, 18, tone)
    out.append('</g>')

# ---------------------------------------------------------------- stars
for _ in range(64):
    x = rnd.randrange(0, W // P)
    y = rnd.randrange(0, 44)
    s = 1 if rnd.random() < 0.78 else 2
    r(x * P, y * P, s * P, s * P, rnd.choice(STAR), cls="tw",
      style=f"animation-delay:{rnd.uniform(0,3.4):.2f}s")

# ---------------------------------------------------------------- moon
mx, my, rad = 252, 13, 7
for dy in range(-rad, rad + 1):
    for dx in range(-rad, rad + 1):
        if dx * dx + dy * dy <= rad * rad:
            shade = "#FFE9A8" if (dx + 2) ** 2 + (dy - 1) ** 2 > 9 else "#E8CE86"
            r((mx + dx) * P, (my + dy) * P, P, P, shade)

# shooting star
out.append('<g class="sh">')
for i in range(6):
    r((240 + i * 2) * P, (6 - i) * P, P * 2, P, "#FFFFFF" if i < 2 else "#9FB6FF")
out.append('</g>')

# ---------------------------------------------------------------- city
def skyline(base_row, top_min, top_max, colour, win_chance, seed):
    g = random.Random(seed)
    x = -2
    while x < W // P + 4:
        bw = g.choice([6, 8, 8, 10, 12, 14])
        top = g.randrange(top_min, top_max)
        r(x * P, top * P, bw * P, (base_row - top) * P, colour)
        # antenna
        if bw >= 12 and g.random() < 0.4:
            r((x + bw // 2) * P, (top - 4) * P, P, 4 * P, colour)
            r((x + bw // 2) * P, (top - 5) * P, P, P, "#FF7FA8", cls="tw",
              style=f"animation-delay:{g.uniform(0,3):.2f}s")
        for wy in range(top + 2, base_row - 1, 4):
            for wx in range(x + 2, x + bw - 2, 4):
                if g.random() < win_chance:
                    r(wx * P, wy * P, 2 * P, 2 * P, g.choice(WIN), cls="wn",
                      style=f"animation-delay:{g.uniform(0,8):.2f}s")
        x += bw + g.choice([1, 2])

skyline(77, 57, 65, CITY_FAR, 0.24, 12)
skyline(85, 67, 76, CITY_NEAR, 0.44, 99)

# ---------------------------------------------------------------- title
name = "MUHAMMAD JUNAID"
cw = 8  # Press Start 2P advance at size 8
total = len(name) * cw * TP
ox = (W - total) // 2
oy = 84

for i, ch in enumerate(name):
    if ch == " ":
        continue
    on, gw, gh = bitmap(ch, 8)
    out.append(f'<g class="ch" style="animation-delay:{0.05 + i * 0.045:.2f}s">')
    for sx, sy, ln in runs(on):
        r(ox + (i * cw + sx) * TP + TP, oy + sy * TP + TP, ln * TP, TP, TITLE_SHADOW)
    for sx, sy, ln in runs(on):
        r(ox + (i * cw + sx) * TP, oy + sy * TP, ln * TP, TP, TITLE)
    out.append('</g>')

# ---------------------------------------------------------------- subtitle
sub = "SENIOR FORWARD DEPLOYED ENGINEER"
on, gw, gh = bitmap(sub, 8)
sx0 = (W - gw * P) // 2
sy0 = 172
out.append('<g class="sb">')
for sx, sy, ln in runs(on):
    r(sx0 + sx * P, sy0 + sy * P, ln * P, P, SUB)
out.append('</g>')
r(sx0 + gw * P + P * 3, sy0, P * 6, gh * P, "#6FE3D4", cls="cr")

out.append('</g></svg>')
open("out/assets/banner.svg", "w").write("\n".join(out))
print("rects:", sum(1 for l in out if l.startswith("<rect")))
