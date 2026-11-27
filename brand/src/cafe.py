"""NeProvence: Eiffel Tower + Paris, with cafés, a Morris column and street lamps filling the outer corners."""
import eiffel, make
from make import rect, BLACK, build, text_path
from make_fr import poly, haussmann
W = '#fff'

def sign(txt, cx, base, size):
    d, w, _ = text_path(txt, size, 0, 0)
    d, w, _ = text_path(txt, size, cx - w / 2, base)
    return f'<path d="{d}" fill="{W}"/>'   # hangs upside down with the rest of the skyline

def cafe(x, w, h, name):
    e = haussmann(x, w, h)
    e.append(rect(x, -96, w, 96))                                   # shop floor
    e.append(rect(x + 4, -118, w - 8, 18)); e.append(sign(name, x + w / 2, -103, 14))   # sign band
    n = 3; gw = (w - 16) / n
    for i in range(n): e.append(rect(x + 6 + i * (gw + 2), -64, gw - 2, 58, W))         # big café windows
    # striped awning with scalloped edge
    e.append(poly([(x - 4, -98), (x + w + 4, -98), (x + w + 16, -70), (x - 16, -70)]))
    k = 0; xs = x - 16
    while xs < x + w + 16:
        if k % 2: e.append(poly([(xs, -70), (xs + 8, -70), (xs + 8 - (xs + 4 - x - w / 2) * .04, -97), (xs - (xs + 4 - x - w / 2) * .04, -97)], W))
        e.append(f'<path d="M{xs},-70 A4,5 0 0 0 {xs+8},-70z" fill="{BLACK}"/>'); xs += 8; k += 1
    # bistro tables and chairs in front of the windows
    for tx in range(int(x + 16), int(x + w - 10), 34):
        e.append(f'<ellipse cx="{tx}" cy="-26" rx="10" ry="2.6" fill="{BLACK}"/>'); e.append(rect(tx - 1.2, -26, 2.4, 22)); e.append(rect(tx - 6, -5, 12, 2.4))
        for s in (-1, 1):
            cx = tx + s * 15
            e.append(rect(cx - 4, -18, 8, 2.2)); e.append(rect(cx + s * 3 - 1, -34, 2, 34)); e.append(rect(cx - s * 4 - 1, -18, 2, 18))
            e.append(f'<path d="M{cx+s*4},-34 Q{cx+s*9},-30 {cx+s*4},-24" fill="none" stroke="{BLACK}" stroke-width="2"/>')
    return e

def lamp(x, h=150):
    e = [rect(x - 5, -10, 10, 10), rect(x - 3, -h + 20, 6, h - 20), rect(x - 6, -60, 12, 5)]
    e.append(poly([(x - 9, -h + 20), (x + 9, -h + 20), (x + 12, -h + 2), (x - 12, -h + 2)]))
    e.append(rect(x - 6, -h + 17, 12, 13, W))
    e.append(poly([(x - 14, -h + 2), (x + 14, -h + 2), (x, -h - 12)])); e.append(f'<circle cx="{x}" cy="{-h-15}" r="3" fill="{BLACK}"/>')
    return e

def morris(x):
    e = [rect(x - 18, -8, 36, 8), rect(x - 15, -118, 30, 112)]
    for y in (-30, -60, -90): e.append(rect(x - 15, y, 30, 2, W))
    e.append(rect(x - 19, -124, 38, 6)); e.append(f'<path d="M{x-17},-124 Q{x},-152 {x+17},-124z" fill="{BLACK}"/>')
    e.append(rect(x - 1.5, -162, 3, 12)); e.append(f'<circle cx="{x}" cy="-164" r="3.5" fill="{BLACK}"/>')
    return e

def metro(x0, x1):
    """Art Nouveau Paris Metro entrance (Guimard): curling iron stems, lamp buds, METROPOLITAIN sign, railing."""
    e = [rect(x0, -34, x1 - x0, 4), rect(x0, -6, x1 - x0, 6)]
    for k in range(int(x0) + 4, int(x1) - 2, 9):
        e.append(rect(k, -30, 2, 24)); e.append(f'<circle cx="{k+1}" cy="-18" r="3" fill="none" stroke="{BLACK}" stroke-width="1.4"/>')
    mid = (x0 + x1) / 2
    for s, x in ((-1, x0 + 8), (1, x1 - 8)):
        e.append(f'<path d="M{x},0 C{x},-70 {x-s*4},-120 {x+s*10},-160 C{x+s*16},-176 {x+s*4},-186 {x-s*6},-180" fill="none" stroke="{BLACK}" stroke-width="5" stroke-linecap="round"/>')
        e.append(f'<ellipse cx="{x-s*8}" cy="-176" rx="5" ry="8" fill="{BLACK}" transform="rotate({-s*30} {x-s*8} -176)"/>')
        e.append(f'<path d="M{x},-40 Q{x+s*14},-48 {x+s*8},-62" fill="none" stroke="{BLACK}" stroke-width="2.4"/>')
    e.append(f'<path d="M{x0+6},-128 Q{mid},-146 {x1-6},-128 L{x1-6},-112 Q{mid},-130 {x0+6},-112z" fill="{BLACK}"/>')
    e.append(sign('METROPOLITAIN', mid, -118, 10.5))
    for k in range(int(x0) + 16, int(x1) - 12, 12):
        e.append(f'<path d="M{k},-112 Q{k+6},-100 {k+12},-112" fill="none" stroke="{BLACK}" stroke-width="1.6"/>')
    return e

def notredame(x):
    """Notre-Dame facade: two square towers, rose window, three portals, spire behind."""
    e = [rect(x, -170, 40, 170), rect(x + 88, -170, 40, 170), rect(x + 40, -132, 48, 132)]
    e.append(poly([(x + 40, -132), (x + 88, -132), (x + 64, -150)]))
    e.append(rect(x + 62, -232, 4, 90)); e.append(poly([(x + 58, -170), (x + 70, -170), (x + 64, -236)]))   # spire
    e.append(f'<circle cx="{x+64}" cy="-100" r="15" fill="{W}"/><circle cx="{x+64}" cy="-100" r="6" fill="{BLACK}"/>')
    for px in (x + 8, x + 52, x + 96):                                                                       # portals
        e.append(f'<path d="M{px},0 V-26 A12,14 0 0 1 {px+24},-26 V0z" fill="{W}"/>')
    for tx in (x, x + 88):
        for k in range(3): e.append(rect(tx + 8 + k * 9, -158, 5, 34, W))                                     # belfry openings
        e.append(rect(tx - 3, -176, 46, 6)); e.append(rect(tx - 3, -92, 46, 4))
    e.append(rect(x + 36, -64, 56, 4))
    return e

def maison(x, w, h, roof, door='arch'):
    """French townhouse: tall windows with mullions, wrought-iron balconies, cornices, roof of the given kind."""
    e = [rect(x, -h, w, h)]
    floors = int((h - 46) // 34); cols = max(2, int(w // 20)); cw = (w - 8) / cols
    for f in range(floors):
        y = -h + 12 + f * 34
        for c in range(cols):
            wx = x + 4 + c * cw + cw * .18; ww = cw * .64
            e.append(rect(wx, y, ww, 22, W)); e.append(rect(wx + ww / 2 - .7, y, 1.4, 22)); e.append(rect(wx, y + 8, ww, 1.2))
            if f in (0, floors - 1) or roof == 'turret':                                   # balcony with iron railing
                e.append(rect(wx - 2, y + 20, ww + 4, 6))
                for k in range(int(ww + 2) // 3): e.append(rect(wx - 1 + k * 3, y + 21.5, 1.4, 3, W))
        if f == 0: e.append(rect(x - 2, y - 6, w + 4, 3))
    # ground floor
    e.append(rect(x - 1, -42, w + 2, 3))
    if door == 'arch':
        e.append(f'<path d="M{x+w/2-8},0 V-20 A8,9 0 0 1 {x+w/2+8},-20 V0z" fill="{W}"/>')
        for s in (-1, 1): e.append(rect(x + w / 2 + s * (w / 4 + 4) - 5, -32, 10, 18, W))
    else:
        for k in range(int(w // 18)): e.append(f'<path d="M{x+5+k*18},-4 V-24 A6,7 0 0 1 {x+17+k*18},-24 V-4z" fill="{W}"/>')
    e.append(rect(x - 3, -h - 4, w + 6, 5))                                                   # cornice
    if roof == 'mansard':
        e.append(poly([(x - 2, -h - 4), (x + w + 2, -h - 4), (x + w - 6, -h - 34), (x + 6, -h - 34)]))
        for k in range(max(1, int(w // 22))):
            dx = x + 10 + k * 22
            e.append(f'<path d="M{dx},{-h-8} V{-h-22} A5,6 0 0 1 {dx+10},{-h-22} V{-h-8}z" fill="{W}"/>')
        e.append(rect(x + w * .7, -h - 48, 8, 16)); e.append(rect(x + w * .7 - 2, -h - 50, 12, 3))
    elif roof == 'gable':
        e.append(poly([(x - 3, -h - 4), (x + w + 3, -h - 4), (x + w / 2, -h - 4 - w * .62)]))
        e.append(f'<circle cx="{x+w/2}" cy="{-h-4-w*.24}" r="{w*.08}" fill="{W}"/>')
        e.append(rect(x + w * .78, -h - 4 - w * .5, 6, w * .3))
    elif roof == 'turret':
        e.append(poly([(x - 4, -h - 4), (x + w + 4, -h - 4), (x + w / 2, -h - 4 - w * 1.05)]))
        e.append(rect(x + w / 2 - 1, -h - 4 - w * 1.05 - 16, 2, 16)); e.append(f'<circle cx="{x+w/2}" cy="{-h-4-w*1.05-17}" r="2.6" fill="{BLACK}"/>')
        e.append(rect(x + w / 2 - 4, -h - 4 - w * .45, 8, 12, W))
    elif roof == 'hip':
        e.append(poly([(x - 2, -h - 4), (x + w + 2, -h - 4), (x + w - 14, -h - 30), (x + 14, -h - 30)]))
        for cx in (x + 16, x + w - 24): e.append(rect(cx, -h - 44, 8, 16)); e.append(rect(cx - 2, -h - 46, 12, 3))
    elif roof == 'balustrade':
        e.append(rect(x - 1, -h - 16, w + 2, 12))
        for k in range(int(w // 6)): e.append(rect(x + 2 + k * 6, -h - 13, 3, 7, W))
        e.append(rect(x - 2, -h - 19, w + 4, 3))
    return e

def right_street():
    e = []
    for x, w, h, roof, door in [(170, 56, 150, 'mansard', 'arch'), (226, 46, 182, 'gable', 'arch'), (272, 62, 140, 'balustrade', 'shop'),
                                (334, 44, 168, 'turret', 'arch'), (378, 58, 132, 'hip', 'shop'), (436, 50, 160, 'mansard', 'arch'),
                                (486, 66, 138, 'gable', 'shop')]:
        e += maison(x, w, h, roof, door)
    return e

def provence_paris():
    base = eiffel.eiffel_real().split('\n')
    e = [rect(-552, -14, 1104, 14)]
    e += cafe(-552, 146, 150, 'CAFÉ') + lamp(-388, 160)
    e += right_street()
    return '\n'.join(e + base)

if __name__ == '__main__':
    build('ne_provence', 'NeProvence', 'fr', provence_paris, 'e', 0.66, False)
    print('ok')
