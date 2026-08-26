"""Pixel horizon divider. Same palette and 4px grid as the banner, no font needed."""
import random

W, H, P = 1200, 44, 4
ROWS = H // P
SKY = ["#0A0E24", "#141A3C", "#22214F", "#3A2A5E"]
GLOW = ["#8E3A64", "#C25473", "#E8825F"]
STAR = ["#FFFFFF", "#CFE0FF", "#FFE9A8"]
CITY = "#0A0B1E"
WIN = ["#FFD166", "#FFB347", "#6FE3D4", "#FF7FA8"]

rnd = random.Random(7)
out = []


def r(x, y, w, h, fill, cls="", style=""):
    c = f' class="{cls}"' if cls else ""
    s = f' style="{style}"' if style else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{c}{s}/>')


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
           f'height="{H}" shape-rendering="crispEdges" role="presentation" aria-hidden="true">')
out.append('''<style>
.tw{animation:tw 3.4s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}
.wn{animation:wn 8s steps(1,end) infinite}
@keyframes wn{0%,42%{opacity:1}43%,52%{opacity:.12}53%,100%{opacity:1}}
@media (prefers-reduced-motion:reduce){.tw,.wn{animation:none;opacity:1}}
</style>''')
out.append(f'<clipPath id="c"><rect width="{W}" height="{H}" rx="6"/></clipPath><g clip-path="url(#c)">')

# sky bands, then the sunset glow along the bottom edge
bands = [(0, 4, SKY[0]), (4, 6, SKY[1]), (6, 7, SKY[2]), (7, 8, SKY[3]),
         (8, 9, GLOW[0]), (9, 10, GLOW[1]), (10, 11, GLOW[2])]
for a, b, col in bands:
    r(0, a * P, W, (b - a) * P, col)
# dither the seams so the strip reads as a gradient
for a, b, col in bands[1:]:
    for x in range(0, W // P, 4):
        r((x + (a % 3)) * P, (a - 1) * P, P, P, col)

# stars in the dark rows
for _ in range(38):
    x = rnd.randrange(0, W // P)
    y = rnd.randrange(0, 5)
    r(x * P, y * P, P, P, rnd.choice(STAR), cls="tw",
      style=f"animation-delay:{rnd.uniform(0, 3.4):.2f}s")

# low skyline silhouette sitting on the glow
x = -2
while x < W // P + 4:
    bw = rnd.choice([5, 6, 8, 8, 10, 12])
    top = rnd.randrange(4, 8)
    r(x * P, top * P, bw * P, (ROWS - top) * P, CITY)
    for wx in range(x + 1, x + bw - 1, 3):
        if rnd.random() < 0.35:
            r(wx * P, (top + 2) * P, P, P, rnd.choice(WIN), cls="wn",
              style=f"animation-delay:{rnd.uniform(0, 8):.2f}s")
    x += bw + rnd.choice([2, 3, 4])

out.append('</g></svg>')
open("assets/divider.svg", "w").write("\n".join(out))
print("rects:", sum(1 for l in out if l.startswith("<rect")))
