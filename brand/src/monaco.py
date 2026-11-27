"""NeLazurka (Monaco): Casino de Monte-Carlo in the centre, superyachts and high-rises on the left,
Hôtel de Paris on the right, supercars and palms in front. Hangs from the bar like Big Ben in NeMyfair."""
import math
from make import rect, palm, BLACK, build
W = '#fff'
def poly(pts, fill=BLACK): return '<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="{fill}"/>'
def arch(x, w, top, bottom, fill=W):   # arched opening: x left, width w, from bottom up to top of the arch
    r = w / 2
    return f'<path d="M{x},{bottom} V{top+r} A{r},{r} 0 0 1 {x+w},{top+r} V{bottom}z" fill="{fill}"/>'
def balustrade(x, w, y, h=10):
    e = [rect(x, y - h, w, h), rect(x - 2, y - h - 3, w + 4, 3)]
    for k in range(int(w // 5)): e.append(f'<ellipse cx="{x+3+k*5}" cy="{y-h/2}" rx="1.4" ry="{h*.32}" fill="{W}"/>')
    return e
def urn(x, y): return f'<path d="M{x-4},{y} L{x+4},{y} L{x+3},{y-4} Q{x+6},{y-9} {x},{y-13} Q{x-6},{y-9} {x-3},{y-4}z" fill="{BLACK}"/>'

def palm2(x, h, lean, s=1.0):
    """Palm with fronds radiating all round (reads as a palm both upright and hanging)."""
    tx, ty = x + lean, -h
    e = [f'<path d="M{x-7*s},0 Q{x+lean*.4-4*s},{-h*.55} {tx-3*s},{ty} L{tx+3*s},{ty} Q{x+lean*.4+4*s},{-h*.55} {x+7*s},0z" fill="{BLACK}"/>']
    for k in range(int(h / 14)):
        y = -6 - k * 14; px = x + lean * (k * 14 / h) ** 1.4 * .9
        e.append(f'<path d="M{px-6*s},{y} L{px+6*s},{y}" stroke="{W}" stroke-width="1.2"/>')
    for a, L in ((-30, 62), (5, 76), (38, 70), (72, 56), (108, 56), (142, 70), (175, 76), (210, 62)):
        r = math.radians(a); L *= s
        ex, ey = tx + L * math.cos(r), ty - L * math.sin(r) + L * .32
        mx, my = tx + L * .55 * math.cos(r), ty - L * .55 * math.sin(r) - 6 * s
        nx, ny = -math.sin(r) * 7 * s, -math.cos(r) * 7 * s
        e.append(f'<path d="M{tx},{ty} Q{mx+nx:.1f},{my+ny:.1f} {ex:.1f},{ey:.1f} Q{mx-nx:.1f},{my-ny:.1f} {tx},{ty}z" fill="{BLACK}"/>')
    for dx, dy in ((-5, 6), (4, 7), (0, 10)): e.append(f'<circle cx="{tx+dx*s}" cy="{ty+dy*s}" r="{4*s}" fill="{BLACK}"/>')
    return ''.join(e)

# ---------- Casino de Monte-Carlo (Place du Casino facade, Garnier 1879) ----------
def casino_tower(cx):
    e = [rect(cx - 28, -212, 56, 212)]
    for dx in (-24, 20): e.append(rect(cx + dx, -206, 4, 200, W)); e.append(rect(cx + dx + 1.2, -204, 1.6, 196))   # pilasters
    e.append(arch(cx - 9, 18, -150, -104, W)); e.append(rect(cx - 9, -118, 18, 2))                           # tall arched windows
    e.append(arch(cx - 9, 18, -92, -50, W)); e.append(rect(cx - .8, -84, 1.6, 34))
    e.append(arch(cx - 8, 16, -36, -4, W))
    for y in (-160, -98): e.append(rect(cx - 30, y, 60, 4))
    e.append(rect(cx - 32, -218, 64, 6)); [e.append(rect(cx - 30 + k * 6, -214, 3, 2, W)) for k in range(10)]   # cornice + dentils
    e.append(rect(cx - 26, -252, 52, 34))                                                                       # belvedere loggia
    for k in range(3): e.append(arch(cx - 21 + k * 15, 12, -248, -222, W))
    e.append(rect(cx - 30, -258, 60, 6))
    for dx in (-26, 26):                                                                                        # corner obelisks
        e.append(rect(cx + dx - 3, -264, 6, 6)); e.append(poly([(cx + dx - 2.5, -264), (cx + dx + 2.5, -264), (cx + dx, -282)]))
    e.append(f'<path d="M{cx-22},-258 Q{cx-23},-276 {cx-12},-282 Q{cx-4},-288 {cx-4},-302 L{cx+4},-302 Q{cx+4},-288 {cx+12},-282 Q{cx+23},-276 {cx+22},-258z" fill="{BLACK}"/>')  # bell roof
    for k in (-12, 0, 12): e.append(f'<path d="M{cx+k},-260 Q{cx+k*.7},-276 {cx+k*.25},-298" fill="none" stroke="{W}" stroke-width="1.1"/>')
    e.append(rect(cx - 6, -318, 12, 16)); e.append(rect(cx - 3.6, -315, 2.4, 9, W)); e.append(rect(cx + 1.2, -315, 2.4, 9, W))
    e.append(f'<path d="M{cx-7},-318 Q{cx},-330 {cx+7},-318z" fill="{BLACK}"/>'); e.append(rect(cx - 1.1, -360, 2.2, 34))
    e.append(f'<circle cx="{cx}" cy="-342" r="3" fill="{BLACK}"/>')
    return e

def torch_bearer(x, s):
    """Bronze sprite carrying a torch (added 1906), standing beside the shell pediment; s=-1 left, 1 right."""
    e = [f'<path d="M{x-6},-206 L{x+6},-206 L{x+4*s+3},-232 Q{x+2*s},-240 {x-2*s},-234 L{x-6},-206z" fill="{BLACK}"/>']
    e.append(f'<circle cx="{x+1*s}" cy="-243" r="5" fill="{BLACK}"/>')
    e.append(f'<path d="M{x+3*s},-234 L{x+16*s},-254" stroke="{BLACK}" stroke-width="3.2" stroke-linecap="round"/>')   # raised arm
    e.append(f'<path d="M{x+14*s},-252 L{x+20*s},-262" stroke="{BLACK}" stroke-width="2.4"/>')
    e.append(f'<path d="M{x+20*s},-262 Q{x+14*s},-270 {x+22*s},-282 Q{x+27*s},-270 {x+20*s},-262z" fill="{BLACK}"/>')  # flame
    e.append(f'<path d="M{x-4*s},-224 Q{x-14*s},-232 {x-18*s},-226 Q{x-12*s},-220 {x-4*s},-218z" fill="{BLACK}"/>')    # wing
    return e

def casino():
    e = []
    for s in (-1, 1):                                                         # recessed bays between centre and towers
        x = 62 if s > 0 else -90
        e.append(rect(x, -182, 28, 182))
        for y0, y1 in ((-170, -128), (-112, -66)): e.append(arch(x + 7, 14, y0, y1, W))
        e += balustrade(x, 28, -182, 8); e.append(urn(x + 14, -193))
    e.append(rect(-62, -206, 124, 206))                                       # central pavilion
    for k in range(3): e.append(arch(-35 + k * 25, 20, -156, -66, W))         # three tall arched windows
    for x in (-54, -46, 40, 48): e.append(rect(x, -166, 6, 112, W)); e.append(rect(x + 2, -162, 2, 104))   # paired columns
    e.append(rect(-66, -172, 132, 8)); e.append(rect(-62, -168, 124, 2, W))
    e += balustrade(-60, 120, -172, 8)
    e.append(rect(-50, -206, 100, 26))
    # seashell pediment with the clock
    e.append(f'<path d="M-40,-206 A40,40 0 0 1 40,-206z" fill="{BLACK}"/>')
    for k in range(9):
        a = math.radians(15 + k * 18.75)
        e.append(f'<path d="M0,-206 L{38*math.cos(a):.1f},{-206-38*math.sin(a):.1f}" stroke="{W}" stroke-width="1.3"/>')
    e.append(f'<path d="M-42,-206 A42,42 0 0 1 42,-206" fill="none" stroke="{BLACK}" stroke-width="4"/>')
    e.append(f'<circle cx="0" cy="-200" r="15" fill="{BLACK}"/><circle cx="0" cy="-200" r="12" fill="{W}"/>')
    e.append(f'<path d="M0,-200 L0,-209 M0,-200 L6,-197" stroke="{BLACK}" stroke-width="2" stroke-linecap="round"/>')
    for k in range(12):
        a = math.radians(k * 30); e.append(f'<circle cx="{10*math.cos(a):.1f}" cy="{-200-10*math.sin(a):.1f}" r=".9" fill="{BLACK}"/>')
    e += torch_bearer(-50, -1) + torch_bearer(50, 1)
    # glass and iron marquee over the entrance, three doors below
    e.append(rect(-74, -48, 148, 6))
    for k in range(12): e.append(rect(-70 + k * 12, -47, 8, 4, W))
    e.append(f'<path d="{" ".join(f"M{x},-42 a6,5 0 0 0 12,0" for x in range(-74, 74, 12))}" fill="{BLACK}"/>')
    for x in (-74, 72): e.append(rect(x, -42, 2.4, 42))
    for k in range(3): e.append(arch(-40 + k * 30, 20, -36, -2, W))
    e += casino_tower(-118) + casino_tower(118)
    return e

# ---------- cars: Ferrari 488 Pista and Rolls-Royce Phantom VIII (see cars.py) ----------
import cars
def car(x, kind, d=1, k=1.0):
    L = 160 if kind == 'rolls' else 153
    t = f'translate({x},0) scale({k},{k})' if d > 0 else f'translate({x+L*k},0) scale({-k},{k})'
    return [f'<g transform="{t}">'] + (cars.phantom() if kind == 'rolls' else cars.pista()) + ['</g>']

# ---------- left: harbour with superyachts in front of Monaco high-rises ----------
def highrise(x, w, h):
    e = [rect(x, -h, w, h)]
    for y in range(-h + 8, -16, 12): e.append(rect(x + 3, y, w - 6, 3.2, W))     # balcony bands
    e.append(rect(x + w * .4, -h - 10, w * .2, 10))
    return e

def superyacht(x, L, k=1.0):
    """Motor superyacht, bow to the left; white outlines so it reads against the buildings."""
    def P(pts): return ' '.join(f'{x+px*k:.1f},{py*k:.1f}' for px, py in pts)
    e = [f'<polygon points="{P([(0,-14),(L,-14),(L+8,-34),(-30,-36),(-14,-22)])}" fill="{BLACK}" stroke="{W}" stroke-width="2.4" stroke-linejoin="round"/>']
    e.append(rect(x, -24 * k, L * .9 * k, 2.2 * k, W))
    decks = [(6, L - 2, -36, -50), (16, L - 14, -50, -63), (30, L - 30, -63, -74)]
    for a, b, y0, y1 in decks:
        e.append(f'<polygon points="{P([(a,y0),(b,y0),(b-6,y1),(a+12,y1)])}" fill="{BLACK}" stroke="{W}" stroke-width="2" stroke-linejoin="round"/>')
        e.append(f'<polygon points="{P([(a+10,(y0+y1)/2+2),(b-6,(y0+y1)/2+2),(b-8,(y0+y1)/2-3),(a+14,(y0+y1)/2-3)])}" fill="{W}"/>')
    mx = x + L * .55 * k                                                    # radar arch with two radomes
    e.append(f'<path d="M{mx-10*k},{-78*k} L{mx-4*k},{-92*k} L{mx+8*k},{-92*k} L{mx+12*k},{-78*k}z" fill="{BLACK}"/>')
    for dx in (-3, 7): e.append(f'<circle cx="{mx+dx*k}" cy="{-96*k}" r="{4.5*k}" fill="{BLACK}"/>')
    return e

def sailyacht(x, h):
    e = [poly([(x - 34, -16), (x + 40, -16), (x + 30, -28), (x - 44, -28)])]
    e.append(rect(x - 1.5, -h, 3, h - 28))
    e.append(f'<path d="M{x},{-h+6} L{x-38},-32 M{x},{-h+6} L{x+34},-32" stroke="{BLACK}" stroke-width="1.2"/>')
    for y in range(-h + 40, -40, 34): e.append(rect(x - 10, y, 20, 1.6))
    return e

def harbour():
    e = []
    for x, w, h in [(-561, 31, 214), (-530, 26, 264), (-504, 30, 188), (-474, 28, 236)]:
        e += highrise(x, w, h)
    # water of the port with small white waves; boats float on it
    e.append(rect(-476, -18, 178, 18))
    e.append(f'<path d="{" ".join(f"M{x},-9 q5,-5 10,0" for x in range(-472, -302, 12))}" fill="none" stroke="{W}" stroke-width="1.6"/>')
    e += superyacht(-440, 120, 1.0)
    return e

# ---------- right: Hôtel de Paris ----------
def hotel_de_paris():
    e = []
    x0, x1 = 304, 518
    e.append(rect(x0, -150, x1 - x0, 150))
    for r in range(3):                                   # three upper floors of tall windows with a small cornice above each
        y = -138 + r * 32
        for c in range(6):
            wx = x0 + 54 + c * 19
            e.append(rect(wx, y, 9, 20, W)); e.append(rect(wx - 2, y - 4, 13, 2.4))
        e.append(rect(x0 + 46, y + 24, x1 - x0 - 92, 2))
    for k in range(5): e.append(arch(x0 + 56 + k * 21, 13, -38, -4, W))          # ground-floor arcade
    e += balustrade(x0, x1 - x0, -150, 10)
    for cx in (x0 + 22, x1 - 22):                       # corner rotundas with domes, inside the facade
        e.append(rect(cx - 22, -184, 44, 184))
        for y in (-148, -108, -68): e.append(rect(cx - 5, y - 20, 10, 20, W))
        e.append(arch(cx - 6, 12, -36, -4, W))
        e.append(rect(cx - 25, -190, 50, 6))
        e.append(f'<path d="M{cx-22},-190 C{cx-22},-222 {cx-8},-234 {cx},-236 C{cx+8},-234 {cx+22},-222 {cx+22},-190z" fill="{BLACK}"/>')
        for k in (-10, 0, 10): e.append(f'<path d="M{cx+k},-192 Q{cx+k*.5},-222 {cx},-234" fill="none" stroke="{W}" stroke-width="1.2"/>')
        e.append(rect(cx - 3, -252, 6, 16)); e.append(f'<circle cx="{cx}" cy="-256" r="4" fill="{BLACK}"/>')
    e.append(rect(x0 + 84, -178, 46, 28)); e.append(f'<circle cx="{x0+107}" cy="-164" r="8" fill="{W}"/>')
    e.append(poly([(x0 + 78, -178), (x0 + 136, -178), (x0 + 107, -196)]))
    e += highrise(528, 32.5, 236)                       # one residential tower, flush with the end of the bar
    return e

def monaco():
    e = [rect(-561, -10, 1122, 10)]
    e += harbour()
    e += hotel_de_paris()
    e += casino()
    # the casino square: paved road strips with the cars on them
    for x0, x1 in ((-298, -146), (146, 298)):
        e.append(rect(x0, -14, x1 - x0, 14)); e.append(f'<path d="{" ".join(f"M{x},-7 h8" for x in range(x0 + 4, x1 - 6, 16))}" stroke="{W}" stroke-width="1.6"/>')
    e += ['<g transform="translate(0,-14)">'] + car(-296, 'rolls', 1, .92) + car(150, 'ferrari', -1, .95) + ['</g>']
    return '\n'.join(e)

if __name__ == '__main__':
    build('ne_lazurka', 'NeLazurka', 'mc', monaco, 'a', 0.66, False)
    print('ok')
