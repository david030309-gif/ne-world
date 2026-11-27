"""NeKosher (Israel): Western Wall on the left, Tower of David in the centre (hangs longest, like Big Ben),
Tel Aviv skyline (Azrieli towers, Bauhaus White City) on the right, and a kippah hanging on the K."""
import math, os
import make
from make import rect, BLACK, build, text_path, S, OUT
W = '#fff'
def poly(pts, fill=BLACK): return '<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="{fill}"/>'
EDGE = 561

def western_wall(x0, x1, h=150):
    e = [rect(x0, -h, x1 - x0, h)]
    y, row = 0, 0
    courses = [22, 22, 20, 20, 18, 16, 14, 12, 10]           # Herodian blocks at the bottom, smaller stones above
    for ch in courses:
        if -y - ch < -h + 2: break
        e.append(rect(x0, y - ch - 1, x1 - x0, 1.8, W))
        bw = ch * 2.6; off = (row % 2) * bw / 2; x = x0 - off
        while x < x1:
            if x > x0: e.append(rect(x, y - ch, 1.8, ch, W))
            if ch >= 18 and x + bw > x0 + 4 and x < x1 - 6:  # drafted margins on the big Herodian ashlars
                lx, rx = max(x + 4, x0 + 3), min(x + bw - 4, x1 - 3)
                if rx - lx > 8: e.append(f'<rect x="{lx:.1f}" y="{y-ch+4}" width="{rx-lx:.1f}" height="{ch-8}" fill="none" stroke="{W}" stroke-width=".9"/>')
            x += bw
        y -= ch; row += 1
    for px, py in [(x0 + 40, -66), (x0 + 130, -104), (x0 + 210, -58), (x0 + 270, -118)]:   # hyssop / caper plants in the joints
        e.append(f'<path d="M{px},{py} q-10,-4 -14,4 M{px},{py} q2,-10 10,-12 M{px},{py} q10,-2 14,6" stroke="{W}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    # Old City roofs above the wall: small stone domes and a bell tower
    for cx, r in [(x0 + 36, 14), (x0 + 104, 18), (x0 + 196, 12), (x0 + 250, 16)]:
        e.append(rect(cx - r - 4, -h - 10, 2 * r + 8, 10)); e.append(f'<path d="M{cx-r},{-h-10} A{r},{r} 0 0 1 {cx+r},{-h-10}z" fill="{BLACK}"/>')
        e.append(rect(cx - 1, -h - 10 - r - 8, 2, 8))
    bt = x0 + 150
    e.append(rect(bt - 9, -h - 70, 18, 70)); e.append(f'<path d="M{bt-4},{-h-56} V{-h-46} A4,4 0 0 1 {bt+4},{-h-46} V{-h-56}z" fill="{W}"/>')
    e.append(poly([(bt - 11, -h - 70), (bt + 11, -h - 70), (bt, -h - 92)])); e.append(rect(bt - 1, -h - 104, 2, 12))
    return e

def tower_of_david():
    """Jerusalem citadel: crenellated walls with a gate, and the slender tower with two balconies."""
    e = []
    e.append(rect(-150, -112, 300, 112))
    for i, y in enumerate(range(-14, -110, -14)):                                   # stone courses on the citadel wall
        e.append(rect(-150, y, 300, 1.4, W))
        for x in range(-150 + (i % 2) * 18, 150, 36): e.append(rect(x, y, 1.4, 14, W))
    for x in (-60, 60): e.append(f'<path d="M{x-7},-60 V-80 A7,7 0 0 1 {x+7},-80 V-60z" fill="{W}"/>')
    for k in range(-150, 150, 14): e.append(rect(k, -124, 9, 12))                 # crenellations
    e.append(rect(-30, -60, 60, 60)); e.append(f'<path d="M-22,0 V-46 A22,22 0 0 1 22,-46 V0z" fill="{W}"/>')         # gate
    for x in (-110, -70, 70, 110): e.append(rect(x - 2, -90, 4, 18, W))          # arrow slits
    for s in (-1, 1):                                                              # corner bastions
        e.append(rect(s * 150 - (30 if s > 0 else 0), -146, 30, 146))
        for k in range(4): e.append(rect(s * 150 - (30 if s > 0 else 0) + k * 8, -156, 5, 10))
    # the tower (square base, octagonal shaft, two balconies, lantern, finial)
    e.append(rect(-34, -200, 68, 200)); e.append(rect(-38, -204, 76, 6))
    for y in (-180, -140): e.append(f'<path d="M-6,{y+30} V{y+8} A6,6 0 0 1 6,{y+8} V{y+30}z" fill="{W}"/>')
    e.append(poly([(-22, -204), (22, -204), (20, -330), (-20, -330)]))
    for y in (-240, -290): e.append(rect(-18, y, 36, 2, W))
    for y, w in ((-330, 34), (-392, 28)):                                         # balconies with railings
        e.append(rect(-w, y - 6, 2 * w, 6)); e.append(poly([(-w + 2, y), (w - 2, y), (w - 10, y + 10), (-w + 10, y + 10)]))
        for k in range(int(w * 2 / 5)): e.append(rect(-w + 2 + k * 5, y - 14, 1.6, 8))
        e.append(rect(-w, y - 16, 2 * w, 2.4))
    e.append(poly([(-17, -336), (17, -336), (15, -392), (-15, -392)]))
    for x in (-8, 4): e.append(rect(x, -380, 4, 30, W))
    e.append(poly([(-13, -408), (13, -408), (11, -440), (-11, -440)]))
    e.append(f'<path d="M-13,-440 Q-13,-462 0,-470 Q13,-462 13,-440z" fill="{BLACK}"/>')
    e.append(rect(-1.5, -500, 3, 32)); e.append(f'<circle cx="0" cy="-482" r="4" fill="{BLACK}"/>')
    return e

def bauhaus(x, w, h):
    """Tel Aviv White City block: rounded corner, long ribbon balconies, pilotis."""
    e = [f'<path d="M{x},0 V{-h} H{x+w-16} A16,16 0 0 1 {x+w},{-h+16} V0z" fill="{BLACK}"/>']
    for y in range(-h + 14, -20, 20):
        e.append(rect(x + 4, y, w - 10, 3, W)); e.append(rect(x + 6, y + 6, w - 14, 7, W))
    for k in range(int(w // 14)): e.append(rect(x + 6 + k * 14, -14, 6, 14, W))   # pilotis
    return e

def tel_aviv(x0):
    e = []
    e += bauhaus(x0, 48, 96)
    x = x0 + 54
    e.append(rect(x, -300, 48, 300))                                              # Azrieli round tower
    for y in range(-290, -10, 10): e.append(rect(x + 3, y, 42, 2.4, W))
    e.append(rect(x - 2, -312, 52, 12)); e.append(rect(x + 18, -326, 12, 14))
    x += 54
    e.append(poly([(x, 0), (x + 44, 0), (x + 44, -290), (x, -268)]))               # Azrieli triangular tower (slanted top)
    for y in range(-262, -10, 10): e.append(rect(x + 3, y, 38, 2.4, W))
    x += 50
    e.append(rect(x, -262, 42, 262))                                              # Azrieli square tower
    for y in range(-252, -10, 10): e.append(rect(x + 3, y, 36, 2.4, W))
    e.append(rect(x + 19, -296, 4, 34))
    x += 48
    e.append(rect(x, -210, 40, 210))                                              # glass tower with grid
    for y in range(-200, -10, 12):
        for c in range(4): e.append(rect(x + 4 + c * 9, y, 6, 7, W))
    x += 46
    e += bauhaus(x, 48, 120)
    x += 54
    e.append(poly([(x, 0), (EDGE, 0), (EDGE, -228), (x + 8, -244)]))            # modern tower to the edge
    for y in range(-224, -10, 10): e.append(rect(x + 4, y, EDGE - x - 8, 2.4, W))
    return e

def israel():
    e = [rect(-EDGE, -10, 2 * EDGE, 10)]
    e += western_wall(-EDGE, -156)
    e += tel_aviv(156)
    e += tower_of_david()
    return '\n'.join(e)

def kippah(cx, cy, w, ang):
    """Knitted kippah in 3/4 view: a shallow dome with a visible rim, a patterned band that follows the curve, a hair clip."""
    rx, hd, rr = w / 2, w * .36, w * .15
    def ring(v, n=24, zig=None):
        a, bb, y0 = rx * math.sqrt(1 - v * v), rr * math.sqrt(1 - v * v), -hd * v
        pts = []
        for i in range(n + 1):
            t = math.pi * i / n
            vv = v if zig is None else (v if i % 2 == 0 else zig)
            aa, b2, yy = rx * math.sqrt(1 - vv * vv), rr * math.sqrt(1 - vv * vv), -hd * vv
            pts.append((aa * math.cos(t), yy + b2 * math.sin(t)))
        return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    return (f'<g transform="translate({cx},{cy}) rotate({ang})">'
            f'<path d="M{-rx},0 C{-rx},{-hd*1.32:.1f} {rx},{-hd*1.32:.1f} {rx},0 A{rx},{rr:.1f} 0 0 1 {-rx},0z" fill="{BLACK}"/>'
            f'<path d="{ring(0.1)}" fill="none" stroke="{W}" stroke-width="1.6"/>'
            f'<path d="{ring(0.26, 22, 0.44)}" fill="none" stroke="{W}" stroke-width="2.2" stroke-linejoin="round"/>'
            f'<path d="{ring(0.56)}" fill="none" stroke="{W}" stroke-width="1.6"/>'
            f'<ellipse cx="0" cy="{-hd*.78:.1f}" rx="{rx*.1:.1f}" ry="{rr*.28:.1f}" fill="{W}"/>'
            f'</g>')

if __name__ == '__main__':
    word = 'NeKosher'
    svg = build('ne_kosher', word, 'il', israel, 'r', 0.66, False)
    # hang the kippah on the upper arm of the K
    size = 150; d, w, _ = text_path(word, size, 0, 0); k = 760 / w
    _, _, boxes = text_path(word, size * k, (S - 760) / 2, 430)
    b = [bx for bx in boxes if bx[0] == 'K'][0]
    svg = svg.replace('</svg>', kippah(b[3] - 14, b[2] + 10, 88, 26) + '\n</svg>')
    open(os.path.join(OUT, 'ne_kosher.svg'), 'w').write(svg)
    print('ok')
