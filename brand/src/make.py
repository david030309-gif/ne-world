"""Ne World channel logos in the style of Ne Alpy / NeMyfair:
bold wordmark sitting on a black bar, a national landmark hanging upside-down below it,
and a small flag on a pole rising from the word."""
import math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT = TTFont(__import__('os').path.join(__import__('os').path.dirname(__file__), 'montserrat-latin-800-normal.woff'))
GS, CMAP, HMTX, UPM = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['hmtx'], FONT['head'].unitsPerEm
OUT = os.path.dirname(os.path.abspath(__file__))
S = 1000          # canvas
BLACK = '#0b0b0b'

def text_path(txt, size, x0, baseline, track=-0.01):
    """Return (svg path d, width, letter boxes) for txt set at size with its baseline at y=baseline."""
    k = size / UPM
    pen = SVGPathPen(GS)
    x = 0.0; boxes = []
    for ch in txt:
        if ch == ' ':
            x += HMTX[CMAP[32]][0] * 0.55; continue
        g = CMAP[ord(ch)]
        tp = TransformPen(pen, (k, 0, 0, -k, x0 + x * k, baseline))
        GS[g].draw(tp)
        bp = BoundsPen(GS); GS[g].draw(bp)
        if bp.bounds:
            b = bp.bounds; boxes.append((ch, x0 + (x + b[0]) * k, baseline - b[3] * k, x0 + (x + b[2]) * k, baseline - b[1] * k))
        x += HMTX[g][0] + track * UPM
    return pen.getCommands(), x * k, boxes

def flag(kind, x, y, w=80, h=54):
    """Flat flag like NeMyfair: thin straight pole with a ball on top, rectangle flying right from the top."""
    top = y - 128
    p = [f'<rect x="{x-1.6}" y="{top}" width="3.2" height="{y-top}" fill="{BLACK}"/>',
         f'<circle cx="{x}" cy="{top-3}" r="4.2" fill="{BLACK}"/>']
    fx, fy = x + 1.6, top + 2
    g = []
    if kind == 'de':
        for i, c in enumerate(['#000000', '#DD0000', '#FFCE00']): g.append(f'<rect x="{fx}" y="{fy+i*h/3:.2f}" width="{w}" height="{h/3+.4:.2f}" fill="{c}"/>')
    elif kind == 'fr':
        for i, c in enumerate(['#0055A4', '#FFFFFF', '#EF4135']): g.append(f'<rect x="{fx+i*w/3:.2f}" y="{fy}" width="{w/3+.4:.2f}" height="{h}" fill="{c}"/>')
    elif kind == 'pl':
        g.append(f'<rect x="{fx}" y="{fy}" width="{w}" height="{h/2}" fill="#FFFFFF"/><rect x="{fx}" y="{fy+h/2}" width="{w}" height="{h/2}" fill="#DC143C"/>')
    elif kind == 'mc':
        g.append(f'<rect x="{fx}" y="{fy}" width="{w}" height="{h/2}" fill="#CE1126"/><rect x="{fx}" y="{fy+h/2}" width="{w}" height="{h/2}" fill="#FFFFFF"/>')
    elif kind == 'il':
        g.append(f'<rect x="{fx}" y="{fy}" width="{w}" height="{h}" fill="#FFFFFF"/>')
        g.append(f'<rect x="{fx}" y="{fy+h*.1:.2f}" width="{w}" height="{h*.15:.2f}" fill="#0038B8"/><rect x="{fx}" y="{fy+h*.75:.2f}" width="{w}" height="{h*.15:.2f}" fill="#0038B8"/>')
        cx, cy, r = fx + w/2, fy + h/2, h*.2
        for a0 in (-90, 90):
            pts = ' '.join(f'{cx+r*math.cos(math.radians(a0+i*120)):.1f},{cy+r*math.sin(math.radians(a0+i*120)):.1f}' for i in range(3))
            g.append(f'<polygon points="{pts}" fill="none" stroke="#0038B8" stroke-width="2.6"/>')
    p += g
    if kind in ('pl', 'il', 'fr', 'mc'):  # light flags need a hairline edge on white
        p.append(f'<rect x="{fx}" y="{fy}" width="{w}" height="{h}" fill="none" stroke="#d4d4d4" stroke-width="1"/>')
    return '\n'.join(p)

# ---------- hanging emblems (drawn upright with ground at y=0, then flipped to hang from the bar) ----------
def rect(x, y, w, h, fill=BLACK): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>'

def poly(pts, fill=BLACK):
    return '<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="{fill}"/>'

def horse(x0, y0, d=1, k=1.0):
    """Rearing horse, front half (body hidden by the next one), facing right (d=1) or left (d=-1)."""
    P = [(-18,0),(-16,-26),(-10,-38),(-4,-50),(2,-62),(6,-72),(12,-74),(22,-68),(26,-61),(22,-57),(15,-58),
         (11,-52),(12,-44),(18,-42),(26,-38),(30,-30),(27,-26),(21,-31),(14,-34),(14,-26),(20,-20),(19,-14),
         (11,-19),(6,-24),(4,0)]
    ear = [(7,-72),(6,-82),(11,-74)]
    mane = [(-10,-38),(-12,-48),(-6,-58),(0,-68),(4,-74),(2,-62),(-4,-50)]
    f = lambda pts: [(x0 + d*px*k, y0 + py*k) for px, py in pts]
    return poly(f(P)) + poly(f(ear)) + poly(f(mane)) + \
        f'<circle cx="{x0 + d*15*k:.1f}" cy="{y0 - 66*k:.1f}" r="{1.6*k:.1f}" fill="#fff"/>'

def gate():  # Brandenburg Gate, upright: ground y=0, up = negative
    e = []
    W = '#fff'
    # three-step stylobate
    e.append(rect(-306, -10, 612, 10)); e.append(rect(-296, -20, 592, 10)); e.append(rect(-286, -30, 572, 10))
    e.append(rect(-296, -11, 592, 1.4, W)); e.append(rect(-286, -21, 572, 1.4, W))
    cols = [-252, -160, -68, 68, 160, 252]
    for c in cols:
        e.append(rect(c-19, -38, 38, 8)); e.append(rect(c-16, -44, 32, 6))                       # plinth + torus
        e.append(poly([(c-14, -44), (c+14, -44), (c+12, -196), (c-12, -196)]))                  # tapered shaft
        for fx in (-7, 0, 7): e.append(poly([(c+fx-.8, -48), (c+fx+.8, -48), (c+fx*.86+.8, -192), (c+fx*.86-.8, -192)], W))  # flutes
        e.append(rect(c-14, -200, 28, 4)); e.append(poly([(c-13, -200), (c+13, -200), (c+19, -210), (c-19, -210)]))  # echinus
        e.append(rect(c-21, -218, 42, 8))                                                          # abacus
    # architrave with fascia lines
    e.append(rect(-290, -240, 580, 22)); e.append(rect(-290, -229, 580, 1.6, W))
    e.append(rect(-294, -244, 588, 4))
    # frieze: triglyphs and metopes with small reliefs
    e.append(rect(-294, -274, 588, 30))
    i = -294
    while i + 30 <= 294:
        e.append(rect(i+3, -270, 1.8, 22, W)); e.append(rect(i+7, -270, 1.8, 22, W))         # triglyph grooves
        e.append(rect(i+13, -270, 16, 22, W)); e.append(f'<circle cx="{i+21}" cy="-259" r="5" fill="{BLACK}"/>')  # metope + relief
        i += 30
    # cornice with dentils
    e.append(rect(-304, -284, 608, 10))
    for x in range(-300, 300, 10): e.append(rect(x, -276, 5, 3, W))
    e.append(rect(-314, -292, 628, 8))
    # attic: stepped base, body with relief panel of a procession, end blocks
    e.append(rect(-226, -302, 452, 10))
    e.append(rect(-212, -362, 424, 60))
    e.append(rect(-196, -354, 50, 44, W)); e.append(rect(146, -354, 50, 44, W))
    e.append(rect(-186, -346, 30, 28)); e.append(rect(156, -346, 30, 28))
    e.append(rect(-136, -356, 272, 48, W))
    mk = []                                                                                 # Greek-key meander
    for x in range(-128, 120, 20):
        mk.append(f'M{x},-314 H{x+20} M{x+4},-314 V-350 H{x+18} V-326 H{x+10} V-338')
    e.append(f'<path d="{" ".join(mk)}" fill="none" stroke="{BLACK}" stroke-width="3.4"/>')
    e.append(rect(-224, -372, 448, 10)); e.append(rect(-216, -366, 432, 1.6, W))
    # stepped top (pyramid) under the quadriga
    e.append(rect(-170, -384, 340, 12)); e.append(rect(-130, -396, 260, 12)); e.append(rect(-120, -385, 240, 1.4, W))
    # side gate houses (Torhäuser): portico with two columns and a pediment
    for sd in (-1, 1):
        x0 = 300 if sd > 0 else -380
        e.append(rect(x0, -150, 80, 150))
        e.append(rect(x0+10, -126, 22, 96, W)); e.append(rect(x0+48, -126, 22, 96, W))
        e.append(rect(x0+16, -122, 10, 92)); e.append(rect(x0+54, -122, 10, 92))
        e.append(rect(x0-6, -164, 92, 14)); e.append(rect(x0-6, -157, 92, 1.6, W))
        e.append(poly([(x0-10, -164), (x0+90, -164), (x0+40, -196)]))
        e.append(poly([(x0+12, -168), (x0+68, -168), (x0+40, -186)], W))
        e.append(f'<circle cx="{x0+40}" cy="-176" r="4" fill="{BLACK}"/>')
    # quadriga
    e.append(rect(-104, -410, 208, 14)); e.append(rect(-96, -404, 192, 1.6, W))
    e.append(f'<path d="M-36,-410 L-36,-446 Q-36,-456 -26,-456 L26,-456 Q36,-456 36,-446 L36,-410z" fill="{BLACK}"/>')  # chariot
    e.append(f'<circle cx="0" cy="-432" r="12" fill="none" stroke="#fff" stroke-width="2.4"/>')
    e.append(horse(-84, -410, -1, 1.2)); e.append(horse(-40, -410, -1, 1.3))
    e.append(horse(40, -410, 1, 1.3)); e.append(horse(84, -410, 1, 1.2))
    # Victoria: robe, wings, head, raised staff with wreath, iron cross and eagle
    e.append(poly([(-14, -456), (14, -456), (8, -500), (-8, -500)]))
    e.append(poly([(-8, -496), (-34, -520), (-44, -548), (-26, -530), (-6, -506)]))
    e.append(poly([(8, -496), (30, -514), (36, -540), (20, -524), (6, -506)]))
    e.append(f'<circle cx="0" cy="-508" r="7" fill="{BLACK}"/>')
    e.append(poly([(6, -494), (16, -502), (18, -500), (8, -490)]))
    e.append(rect(16, -590, 4, 108))
    e.append(f'<circle cx="18" cy="-600" r="14" fill="none" stroke="{BLACK}" stroke-width="4"/>')
    e.append(f'<path d="M18,-610 L18,-590 M8,-600 L28,-600" stroke="{BLACK}" stroke-width="5"/>')
    e.append(poly([(18, -614), (6, -620), (-4, -634), (10, -628), (18, -640), (26, -628), (40, -634), (30, -620)]))
    return '\n'.join(e)

def palm(x, h, lean, scale=1.0):
    """Upright palm at ground x, height h, lean (+right); fronds droop like a real palm."""
    s = scale
    tx, ty = x + lean, -h
    trunk = f'<path d="M{x-8*s},0 Q{x+lean*.4-5*s},{-h*.55} {tx-3.5*s},{ty} L{tx+3.5*s},{ty} Q{x+lean*.4+5*s},{-h*.55} {x+8*s},0z" fill="{BLACK}"/>'
    fr = []
    for side in (-1, 1):
        for L, lift, drop in ((92, 30, 58), (80, 44, 20), (58, 52, -16)):
            L *= s; lift *= s; drop *= s
            ex, ey = tx + side*L, ty + drop
            c1x, c1y = tx + side*L*.45, ty - lift
            fr.append(f'<path d="M{tx},{ty-2*s} Q{c1x:.1f},{c1y:.1f} {ex:.1f},{ey:.1f} Q{c1x:.1f},{c1y+30*s:.1f} {tx},{ty+8*s}z" fill="{BLACK}"/>')
    fr.append(f'<circle cx="{tx}" cy="{ty}" r="{11*s}" fill="{BLACK}"/>')
    return trunk + ''.join(fr)

def riviera():
    e = [rect(-330, -16, 660, 16)]
    e += skyline([(-330, 40, 78, 'box'), (-288, 34, 112, 'step'), (-250, 46, 92, 'gable'), (-200, 38, 128, 'box'),
                  (100, 36, 120, 'box'), (140, 44, 90, 'dome'), (188, 34, 140, 'step'),
                  (272, 30, 76, 'gable'), (304, 26, 110, 'box')])
    # Hotel Negresco: wide facade, rows of windows, the famous pink dome with a lantern (centre, like Big Ben)
    n = []
    n.append(rect(-112, -120, 224, 120))
    for r in range(4):
        for c in range(9):
            n.append(rect(-100 + c*24, -108 + r*26, 10, 14, '#fff'))
    n.append(rect(-120, -132, 240, 12))
    n.append(rect(-44, -170, 88, 40))
    n.append(f'<path d="M-50,-170 C-50,-232 -14,-262 0,-270 C14,-262 50,-232 50,-170z" fill="{BLACK}"/>')
    for k in (-30, -10, 10, 30): n.append(rect(k-2, -228 + abs(k)*1.1, 4, 50 - abs(k)*1.1, '#fff'))
    n.append(rect(-8, -296, 16, 28)); n.append(f'<path d="M-10,-296 L0,-316 L10,-296z" fill="{BLACK}"/>'); n.append(rect(-1.5, -350, 3, 36))
    e += n
    e.append(palm(-150, 215, 14, .75)); e.append(palm(250, 190, -10, .7))
    # yacht mast and sail on the right
    e.append(rect(170, -200, 3, 200)); e.append(f'<path d="M168,-196 L168,-60 L118,-60z" fill="{BLACK}"/>')
    return '\n'.join(e)

def skyline(spec):
    """Generic hanging skyline: list of (x, w, h, kind)."""
    e = []
    for x, w, h, kind in spec:
        if kind == 'box': e.append(rect(x, -h, w, h))
        elif kind == 'step':
            e.append(rect(x, -h, w, h)); e.append(rect(x+w*.2, -h-14, w*.6, 14))
        elif kind == 'gable':
            e.append(rect(x, -h, w, h)); e.append(f'<path d="M{x},{-h} L{x+w/2},{-h-w*.45} L{x+w},{-h}z" fill="{BLACK}"/>')
            for r in range(2): e.append(rect(x+w*.3, -h+18+r*26, w*.4, 10, '#fff'))
        elif kind == 'round':
            e.append(f'<path d="M{x},0 V{-h+w/2} A{w/2},{w/2} 0 0 1 {x+w},{-h+w/2} V0z" fill="{BLACK}"/>')
            for r in range(5): e.append(rect(x+5, -h+w/2+10+r*22, w-10, 3, '#fff'))
        elif kind == 'tri':
            e.append(f'<path d="M{x},0 V{-h+30} L{x+w/2},{-h} L{x+w},{-h+30} V0z" fill="{BLACK}"/>')
            for r in range(5): e.append(rect(x+5, -h+44+r*22, w-10, 3, '#fff'))
        elif kind == 'sq':
            e.append(rect(x, -h, w, h))
            for r in range(5): e.append(rect(x+5, -h+14+r*22, w-10, 3, '#fff'))
        elif kind == 'dome':
            e.append(rect(x, -h, w, h)); e.append(f'<path d="M{x+4},{-h} A{w/2-4},{w/2} 0 0 1 {x+w-4},{-h}z" fill="{BLACK}"/>')
        elif kind == 'palm':
            e.append(palm(x, h, w, .55))
    return e

def telaviv():
    e = [rect(-330, -16, 660, 16)]
    e += skyline([(-330, 40, 70, 'box'), (-292, 34, 110, 'step'), (-254, 26, 0, 'palm') if False else (-262, 0, 0, 'box'),
                  (-250, 46, 190, 'round'), (-198, 46, 175, 'tri'), (-146, 46, 160, 'sq'),
                  (-96, 30, 90, 'box'), (70, 36, 120, 'box'), (110, 30, 150, 'step'), (146, 44, 100, 'box'),
                  (196, 34, 135, 'box'), (288, 42, 105, 'step')])
    e.append(palm(262, 180, -10, .62))
    # Jaffa clock tower (centre, long, like Big Ben in NeMyfair)
    t = []
    t.append(rect(-46, -70, 92, 70)); t.append(rect(-54, -82, 108, 14))
    t.append(rect(-38, -180, 76, 100)); t.append(rect(-46, -192, 92, 14))
    t.append(f'<circle cx="0" cy="-135" r="24" fill="#fff"/><circle cx="0" cy="-135" r="19" fill="{BLACK}"/><circle cx="0" cy="-135" r="15" fill="#fff"/>')
    t.append(f'<path d="M0,-135 l0,-11 M0,-135 l8,4" stroke="{BLACK}" stroke-width="3" stroke-linecap="round"/>')
    t.append(rect(-30, -280, 60, 90)); t.append(rect(-18, -262, 12, 46, '#fff')); t.append(rect(6, -262, 12, 46, '#fff'))
    t.append(rect(-38, -292, 76, 14)); t.append(rect(-22, -340, 44, 48))
    t.append(f'<path d="M-22,-340 A22,26 0 0 1 22,-340z" fill="{BLACK}"/>'); t.append(rect(-2.5, -392, 5, 30))
    for x in (-30, -14, 2, 18): t.append(rect(x, -40, 12, 30, '#fff'))
    e += t
    return '\n'.join(e)

def warsaw():
    e = [rect(-330, -16, 660, 16)]
    e += skyline([(-330, 34, 95, 'gable'), (-296, 30, 120, 'gable'), (-266, 34, 85, 'gable'), (-232, 30, 110, 'gable'),
                  (-200, 44, 175, 'sq'), (-152, 38, 140, 'box'), (-110, 30, 95, 'step'),
                  (96, 36, 160, 'sq'), (136, 40, 205, 'tri'), (180, 32, 120, 'box'), (216, 44, 150, 'step'),
                  (264, 30, 90, 'gable'), (294, 36, 115, 'gable')])
    # Palace of Culture and Science (centre, tiered, long spire)
    p = []
    tiers = [(170, 60), (130, 60), (100, 50), (76, 46), (58, 40), (44, 34)]
    y = 0
    for w, h in tiers:
        p.append(rect(-w/2, y-h, w, h))
        for i in range(int(w // 14)):
            if w > 60: p.append(rect(-w/2 + 7 + i*14, y-h+10, 4, h-22, '#fff'))
        p.append(rect(-w/2-6, y-h-6, w+12, 6))
        y -= h + 6
    # side towers on the first tier
    for s in (-1, 1): p.append(rect(s*85 - (16 if s < 0 else -0), -98, 16, 40)); p.append(f'<path d="M{s*85-(16 if s<0 else 0)},-98 l8,-18 l8,18z" fill="{BLACK}"/>')
    p.append(f'<circle cx="0" cy="{y+30}" r="13" fill="#fff"/><circle cx="0" cy="{y+30}" r="9" fill="{BLACK}"/>')
    p.append(f'<path d="M-14,{y} L0,{y-70} L14,{y}z" fill="{BLACK}"/>')
    p.append(rect(-2.5, y-170, 5, 105))
    e += p
    return '\n'.join(e)

LOGOS = [
    ('ordnung', 'NE ORDNUNG', 'de', gate, 'O', 0.7, True),
    ('lazurka', 'NeLazurka', 'fr', riviera, 'k', 1.0, False),
    ('shalom', 'NeShalom', 'il', telaviv, 'm', 1.0, False),
    ('zhabka', 'NeZhabka', 'pl', warsaw, 'a', 1.0, False),
]

def build(slug, word, fl, emblem, flag_on, _, caps):
    size = 150
    d, w, boxes = text_path(word, size, 0, 0)
    target = 760
    k = target / w
    x0 = (S - target) / 2
    baseline = 430
    d, w, boxes = text_path(word, size * k, x0, baseline)
    bar_y = baseline + 4
    em_scale = target / 700 * _
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">',
             f'<rect width="{S}" height="{S}" fill="#ffffff"/>',
             f'<path d="{d}" fill="{BLACK}"/>',
             f'<rect x="{x0-22}" y="{bar_y}" width="{target+44}" height="26" fill="{BLACK}"/>',
             f'<g transform="translate({S/2},{bar_y+20}) scale({em_scale},{-em_scale})">{emblem()}</g>']
    # flag on the chosen letter (last occurrence)
    b = [bx for bx in boxes if bx[0] == flag_on][-1]
    fx = b[3] - (b[3]-b[1]) * (0.18 if flag_on in 'Ok' else 0.12)
    parts.append(flag(fl, fx, b[2] + 6))
    parts.append('</svg>')
    svg = '\n'.join(parts)
    open(os.path.join(OUT, f'{slug}.svg'), 'w').write(svg)
    return svg

if __name__ == '__main__':
    for L in LOGOS: build(*L)
    print('ok')
