"""Realistic Eiffel Tower emblem (hanging, like Big Ben in NeMyfair) + Paris skyline; three name options."""
import math
import make, make_fr
from make import rect, BLACK, build
from make_fr import poly, haussmann, arc, sacrecoeur
W = '#fff'

def w(y):   # outer half-width of the tower at height y (y negative = up)
    t = min(1, -y / 560)
    return 12 + 150 * (1 - t) ** 2.35

def edge(y0, y1, side=-1, n=14, f=w):
    return [(side * f(y0 + (y1 - y0) * i / n), y0 + (y1 - y0) * i / n) for i in range(n + 1)]

def invalides(x):
    """Les Invalides: wide base with portico, drum with columns, ribbed dome, lantern and spire (80 wide)."""
    e = [rect(x, -70, 80, 70), rect(x - 3, -76, 86, 6)]
    for k in range(5): e.append(rect(x + 8 + k * 14, -60, 6, 52, W))                  # ground-floor arcade
    e.append(poly([(x + 18, -76), (x + 62, -76), (x + 40, -92)]))                       # pediment
    e.append(rect(x + 14, -126, 52, 34)); e.append(rect(x + 10, -130, 60, 5))           # drum
    for k in range(6): e.append(rect(x + 18 + k * 8, -122, 3.4, 26, W))
    e.append(f'<path d="M{x+12},-130 C{x+12},-170 {x+28},-186 {x+40},-188 C{x+52},-186 {x+68},-170 {x+68},-130z" fill="{BLACK}"/>')
    for k in (-14, 0, 14): e.append(f'<path d="M{x+40+k},-132 Q{x+40+k*0.6},-170 {x+40},-186" fill="none" stroke="{W}" stroke-width="1.4"/>')
    e.append(rect(x + 35, -204, 10, 16)); e.append(poly([(x + 34, -204), (x + 46, -204), (x + 40, -232)])); e.append(rect(x + 39, -246, 2, 16))
    return e

def moulin(x):
    """Moulin Rouge: low cabaret building, windmill tower with conical roof and four lattice sails."""
    cx = x + 40
    e = [rect(x, -64, 80, 64), rect(x - 3, -70, 86, 6)]
    for k in range(4): e.append(f'<path d="M{x+8+k*18},-8 V-36 A6,6 0 0 1 {x+20+k*18},-36 V-8z" fill="{W}"/>')
    e.append(rect(x + 4, -54, 72, 8, W)); e.append(rect(x + 6, -52, 68, 4))
    e.append(poly([(cx - 18, -70), (cx + 18, -70), (cx + 14, -128), (cx - 14, -128)]))
    e.append(rect(cx - 5, -108, 10, 14, W))
    e.append(poly([(cx - 20, -128), (cx + 20, -128), (cx, -156)]))
    for a in (45, 135, 225, 315):
        g = [f'<g transform="rotate({a} {cx} -132)">', rect(cx - 1.5, -132 - 70, 3, 70),
             rect(cx + 2, -132 - 70, 12, 56)]
        for k in range(5): g.append(rect(cx + 2, -132 - 66 + k * 11, 12, 2, W))
        g.append(rect(cx + 7, -132 - 68, 1.6, 52, W)); g.append('</g>')
        e += g
    e.append(f'<circle cx="{cx}" cy="-132" r="5" fill="{BLACK}"/>')
    return e

def eiffel_real():
    e = [rect(-372, -14, 744, 14)]
    e += haussmann(-372, 44, 150) + haussmann(-326, 36, 120)
    e += arc(-288)

    P1, P2, P3 = -118, -238, -540          # platform heights
    shapes = []
    for s in (-1, 1):
        # leg below 1st platform: outer edge follows the curve, inner edge rises toward the arch
        inner = [(s * (108 - 40 * (i / 10) ** 1.4), -i / 10 * (-P1)) for i in range(11)]
        shapes.append(edge(0, P1, s) + list(reversed(inner)))
        # legs between 1st and 2nd platform, open gap in the middle
        inner2 = [(s * (64 - 46 * i / 10), P1 - 14 - i / 10 * (P2 - (P1 - 14)) * -1 * -1) for i in range(11)]
        inner2 = [(s * (64 - 46 * i / 10), (P1 - 14) + (P2 - (P1 - 14)) * i / 10) for i in range(11)]
        shapes.append(edge(P1 - 14, P2, s) + list(reversed(inner2)))
    # shaft above 2nd platform (four legs merge higher up)
    shaft = edge(P2 - 10, P3, -1, 24) + list(reversed(edge(P2 - 10, P3, 1, 24)))
    shapes.append(shaft)
    d = ' '.join('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in sh) + 'z' for sh in shapes)
    e.append(f'<clipPath id="ef"><path d="{d}"/></clipPath>')
    e.append(f'<path d="{d}" fill="{BLACK}"/>')
    # lattice: two families of diagonal braces + horizontal panel ties, cut out in white
    lat = []
    for i in range(-80, 80):
        b = i * 9
        lat.append(f'M{b-400},40 L{b+400},-700 M{b+400},40 L{b-400},-700')
    ties = ' '.join(f'M-200,{y} H200' for y in range(-16, -540, -22))
    e.append(f'<g clip-path="url(#ef)"><path d="{" ".join(lat)}" stroke="{W}" stroke-width="1.15" fill="none"/>'
             f'<path d="{ties}" stroke="{BLACK}" stroke-width="2.2"/></g>')
    # solid corner members (the four edges of each leg) drawn over the lattice
    e.append(f'<path d="{d}" fill="none" stroke="{BLACK}" stroke-width="4" stroke-linejoin="round"/>')
    for s in (-1, 1):   # central spine of each leg
        e.append(f'<path d="M{s*128},0 Q{s*100},-70 {s*84},{P1}" fill="none" stroke="{BLACK}" stroke-width="3"/>')
        e.append(f'<path d="M{s*82},{P1-14} L{s*42},{P2}" fill="none" stroke="{BLACK}" stroke-width="2.6"/>')
    e.append(f'<path d="M0,{P2-12} L0,{P3}" stroke="{BLACK}" stroke-width="2.4"/>')
    # the great decorative arch between the legs, with its round openings
    e.append(f'<path d="M-104,-6 Q-96,-104 0,-108 Q96,-104 104,-6 L92,-6 Q86,-92 0,-96 Q-86,-92 -92,-6z" fill="{BLACK}"/>')
    e.append(f'<path d="M-100,{P1+2} Q0,-80 100,{P1+2}" fill="none" stroke="{BLACK}" stroke-width="2"/>')
    for k in range(-5, 6):
        a = k / 6 * 1.25
        e.append(f'<circle cx="{98*math.sin(a):.1f}" cy="{-6-96*math.cos(a)*0.98:.1f}" r="2.6" fill="{W}"/>')
    # 1st platform: deck, arcade skirt and railing
    x1 = w(P1) + 10
    e.append(rect(-x1, P1 - 4, 2 * x1, 10)); e.append(rect(-x1 + 4, P1 - 16, 2 * x1 - 8, 12))
    for k in range(int(-x1) + 8, int(x1) - 8, 9):
        e.append(f'<path d="M{k},{P1-5} V{P1-11} A3,3 0 0 1 {k+6},{P1-11} V{P1-5}z" fill="{W}"/>')
    e.append(rect(-x1 - 4, P1 - 22, 2 * x1 + 8, 4)); e.append(rect(-x1 + 2, P1 - 28, 2 * x1 - 4, 2))
    for k in range(int(-x1) + 2, int(x1), 6): e.append(rect(k, P1 - 28, 1.2, 6))
    # 2nd platform
    x2 = w(P2) + 8
    e.append(rect(-x2, P2 - 2, 2 * x2, 8)); e.append(rect(-x2 + 3, P2 - 12, 2 * x2 - 6, 10))
    for k in range(int(-x2) + 6, int(x2) - 6, 8): e.append(rect(k, P2 - 10, 4, 6, W))
    e.append(rect(-x2 - 3, P2 - 16, 2 * x2 + 6, 3)); e.append(rect(-x2 + 2, P2 - 21, 2 * x2 - 4, 1.6))
    for k in range(int(-x2) + 2, int(x2), 5): e.append(rect(k, P2 - 21, 1, 5))
    # intermediate platform rings on the shaft
    for y in (-330, -430):
        xx = w(y) + 4; e.append(rect(-xx, y - 3, 2 * xx, 5))
    # top: 3rd floor cabin, lantern, flag mast / antennas
    e.append(rect(-26, P3 - 6, 52, 8)); e.append(rect(-22, P3 - 26, 44, 20))
    for k in range(-18, 19, 7): e.append(rect(k, P3 - 22, 4, 10, W))
    e.append(rect(-28, P3 - 30, 56, 4))
    e.append(poly([(-18, P3 - 30), (18, P3 - 30), (12, P3 - 52), (-12, P3 - 52)]))
    e.append(f'<path d="M-12,{P3-52} Q0,{P3-70} 12,{P3-52}z" fill="{BLACK}"/>')
    e.append(rect(-6, P3 - 84, 12, 22)); e.append(rect(-2.2, P3 - 150, 4.4, 70))
    for y in (P3 - 100, P3 - 118, P3 - 134): e.append(rect(-7, y, 14, 2.2))
    return '\n'.join(e)

if __name__ == '__main__':
    for slug, name in [('fr_komilfo', 'NeKomilfo'), ('fr_shanzelize', 'NeShanzelize'), ('fr_pari', 'NePari')]:
        build(slug, name, 'fr', eiffel_real, name[-1], 0.66, False)
    print('ok')
