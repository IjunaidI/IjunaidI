"""Minified RPG status strip for under the projects table.
Slim cut of concepts/rpg.py: avatar, level line, compact stat bars, quest count."""
import random
from PIL import Image, ImageDraw, ImageFont

FONT = "fonts/PressStart2P.ttf"
W, H = 1200, 160

BG = "#0A0E24"
DITHER = "#141A3C"
FRAME = "#F4F8FF"
FRAME_IN = "#8DA2DE"
TEXT = "#F4F8FF"
DIM = "#8DA2DE"
GOLD = "#FFD166"
TRACK = "#141A3C"

rnd = random.Random(4)
out = []


def r(x, y, w, h, fill, cls="", style=""):
    c = f' class="{cls}"' if cls else ""
    s = f' style="{style}"' if style else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{c}{s}/>')


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


def text(s, x, y, scale, fill, cls="", style=""):
    on, gw, gh = bitmap(s, 8)
    if cls or style:
        c = f' class="{cls}"' if cls else ""
        st = f' style="{style}"' if style else ""
        out.append(f'<g{c}{st}>')
    for sx, sy, ln in runs(on):
        r(x + sx * scale, y + sy * scale, ln * scale, scale, fill)
    if cls or style:
        out.append('</g>')
    return gw * scale


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
           f'height="{H}" shape-rendering="crispEdges" role="img" '
           f'aria-label="Muhammad Junaid, level 8 engineer, side quests cleared: 5">')
out.append('''<style>
.bar{transform-box:fill-box;transform-origin:0 50%;animation:bar 1s steps(12,end) forwards;transform:scaleX(0)}
@keyframes bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.cr{animation:cr 1.05s steps(1,end) infinite}
@keyframes cr{0%,50%{opacity:1}51%,100%{opacity:0}}
.bob{animation:bob 1.6s steps(1,end) infinite}
@keyframes bob{0%,49%{transform:translateY(0)}50%,100%{transform:translateY(4px)}}
.spk{animation:spk 2.8s steps(1,end) infinite;opacity:0}
@keyframes spk{0%,7%{opacity:1}8%,100%{opacity:0}}
.fin{opacity:0;animation:fin .4s steps(1,end) forwards}
@keyframes fin{to{opacity:1}}
@media (prefers-reduced-motion:reduce){.bar{animation:none;transform:scaleX(1)}.cr,.bob,.spk{animation:none}.fin{animation:none;opacity:1}}
</style>''')
out.append(f'<clipPath id="c"><rect width="{W}" height="{H}" rx="8"/></clipPath><g clip-path="url(#c)">')

r(0, 0, W, H, BG)
for _ in range(100):
    x, y = rnd.randrange(0, W // 4) * 4, rnd.randrange(0, H // 4) * 4
    r(x, y, 4, 4, DITHER)


def frame(x, y, w, h, t, col):
    r(x + t, y, w - 2 * t, t, col)
    r(x + t, y + h - t, w - 2 * t, t, col)
    r(x, y + t, t, h - 2 * t, col)
    r(x + w - t, y + t, t, h - 2 * t, col)

frame(6, 6, W - 12, H - 12, 4, FRAME)
frame(14, 14, W - 28, H - 28, 2, FRAME_IN)

SPRITE = [
    "....hhhhhhhh....",
    "...hhhhhhhhhh...",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "..hhsssssssshh..",
    "..hsseesseessh..",
    "..hssssssssssh..",
    "..hssssddssssh..",
    "..hbssssssssbh..",
    "...bbssssssbb...",
    "....ssssssss....",
    "......ssss......",
    "....tttttttt....",
    "..tttttttttttt..",
    ".ttttTTTTTTtttt.",
    ".ttttTTTTTTtttt.",
    ".ttttTTTTTTtttt.",
    ".tttttttttttttt.",
    "..pppppppppppp..",
    "..pppppppppppp..",
]
COLORS = {"h": "#2B1B44", "s": "#E8B08A", "d": "#C98B63", "e": "#0A0E24",
          "b": "#8A6A4F", "t": "#6FE3D4", "T": "#45B5A8", "p": "#141A3C"}
S = 4
ax, ay = 44, 36
out.append('<g class="bob">')
for ry, row in enumerate(SPRITE):
    for rx, ch in enumerate(row):
        if ch != ".":
            r(ax + rx * S, ay + ry * S, S, S, COLORS[ch])
out.append('</g>')
out.append('<g class="spk">')
r(120, 40, 4, 16, GOLD)
r(114, 46, 16, 4, GOLD)
out.append('</g>')

text("MUHAMMAD JUNAID", 148, 30, 3, TEXT)
text("LV.8  ENGINEER  KARACHI", 148, 64, 2, DIM)
text("SIDE QUESTS CLEARED: 5", 148, 106, 2, GOLD, cls="fin", style="animation-delay:1.4s")

STATS = [("FRONTEND", 0.94, "#6FE3D4"),
         ("BACKEND", 0.80, "#FF7FA8"),
         ("PIXELS", 0.88, "#FFD166"),
         ("SHIPPING", 0.97, "#C2426F")]
for i, (label, pct, col) in enumerate(STATS):
    x0 = 560 + i * 156
    text(label, x0, 42, 2, TEXT)
    r(x0, 70, 132, 12, TRACK)
    fill_w = int(132 * pct) // 4 * 4
    r(x0, 70, fill_w, 12, col, cls="bar", style=f"animation-delay:{0.3 + i * 0.2:.2f}s")
    for tx in range(x0 + 16, x0 + 132, 16):
        r(tx, 70, 2, 12, BG)

text("NEW GAME+", 1020, 106, 2, DIM, cls="fin", style="animation-delay:1.7s")
out.append('<g class="cr">')
r(508, 106, 10, 16, GOLD)
out.append('</g>')

out.append('</g></svg>')
open("assets/rpg-mini.svg", "w").write("\n".join(out))
print("rects:", sum(1 for l in out if l.startswith("<rect")))
