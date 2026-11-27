"""Three logo ideas for the French channel (NeLazurka), same style as the others."""
import make
from make import rect, palm, BLACK, build
W = '#fff'
def poly(pts, fill=BLACK): return '<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="{fill}"/>'

def haussmann(x, w, h):
    """Paris apartment block: stone facade, balcony lines, slate mansard roof with dormers and chimneys."""
    e = [rect(x, -h, w, h)]
    rows = int((h - 30) // 30); cols = max(2, int(w // 16))
    for r in range(rows):
        y = -h + 14 + r * 30
        for c in range(cols): e.append(rect(x + 6 + c * (w - 12) / cols + 2, y, (w - 12) / cols - 6, 16, W))
        if r in (1, rows - 1): e.append(rect(x + 2, y + 18, w - 4, 2.4, W))
    e.append(poly([(x - 3, -h), (x + w + 3, -h), (x + w - 8, -h - 30), (x + 8, -h - 30)]))   # mansard
    for c in range(max(1, int(w // 26))): e.append(rect(x + 12 + c * 26, -h - 22, 8, 12, W))
    e.append(rect(x + w * .25, -h - 42, 7, 14)); e.append(rect(x + w * .7, -h - 40, 7, 12))
    return e

def arc(x):
    e = [rect(x, -150, 110, 150)]
    e.append(f'<path d="M{x+33},0 V-70 A22,22 0 0 1 {x+77},-70 V0z" fill="{W}"/>')
    e.append(rect(x - 4, -116, 118, 6)); e.append(rect(x - 6, -164, 122, 14)); e.append(rect(x + 10, -142, 90, 3, W))
    for k in (12, 88): e.append(rect(x + k, -104, 10, 30, W))
    return e

def sacrecoeur(x):
    e = [rect(x, -90, 120, 90)]
    for k in (14, 50, 86): e.append(f'<path d="M{x+k},0 V-40 A10,10 0 0 1 {x+k+20},-40 V0z" fill="{W}"/>')
    e.append(rect(x + 30, -130, 60, 40)); e.append(f'<path d="M{x+28},-130 C{x+28},-176 {x+60},-196 {x+60},-200 C{x+60},-196 {x+92},-176 {x+92},-130z" fill="{BLACK}"/>')
    e.append(rect(x + 57, -222, 6, 24)); e.append(f'<circle cx="{x+60}" cy="-226" r="5" fill="{BLACK}"/>')
    for k in (4, 96):
        e.append(f'<path d="M{x+k},-90 A10,14 0 0 1 {x+k+20},-90z" fill="{BLACK}"/>'); e.append(rect(x + k + 9, -110, 2, 8))
    return e

def eiffel():
    e = [rect(-350, -14, 700, 14)]
    e += haussmann(-350, 52, 130) + haussmann(-296, 46, 160)
    e += arc(-246)
    e += haussmann(-132, 34, 120)
    e += haussmann(102, 36, 115) + sacrecoeur(142) + haussmann(266, 44, 150) + haussmann(312, 40, 120)
    half = [(-140, 0), (-108, -70), (-88, -150), (-70, -240), (-52, -330), (-34, -440), (-18, -536)]
    out = half + [(-x, y) for x, y in reversed(half)]
    tower = 'M' + ' L'.join(f'{x},{y}' for x, y in out) + 'z'
    e.append(f'<clipPath id="tw"><path d="{tower}"/></clipPath>')
    e.append(f'<path d="{tower}" fill="{BLACK}"/>')
    lat = [f'M{i*22-300},-150 L{i*22+300},-750 M{i*22+300},-150 L{i*22-300},-750' for i in range(-40, 40)]
    e.append(f'<g clip-path="url(#tw)"><path d="{" ".join(lat)}" stroke="{W}" stroke-width="1.8" fill="none"/></g>')
    e.append(f'<path d="M-80,0 Q-74,-84 0,-92 Q74,-84 80,0z" fill="{W}"/>')                       # great arch between the legs
    e.append(rect(-104, -166, 208, 16)); e.append(rect(-96, -150, 192, 4))
    for k in range(-92, 94, 12): e.append(rect(k, -162, 6, 8, W))
    e.append(rect(-64, -340, 128, 12)); e.append(rect(-58, -328, 116, 3))
    for k in range(-54, 56, 10): e.append(rect(k, -337, 5, 6, W))
    e.append(rect(-24, -560, 48, 22)); e.append(rect(-28, -566, 56, 6)); e.append(rect(-18, -552, 36, 4, W))
    e.append(rect(-11, -592, 22, 26)); e.append(rect(-3, -660, 6, 70)); e.append(rect(-8, -620, 16, 3))
    return '\n'.join(e)

def sacre_and_eiffel():   # not used
    return eiffel()

def carlton():
    """Cannes seafront: Hotel Carlton with its two black cupolas, palms on the Croisette."""
    e = [rect(-340, -14, 680, 14)]
    e.append(rect(-160, -190, 320, 190))
    for r in range(6):
        for c in range(13): e.append(rect(-151 + c * 23.6, -178 + r * 28, 12, 15, W))
        e.append(rect(-156, -160 + r * 28, 312, 2, W))
    e.append(rect(-172, -202, 344, 12)); e.append(rect(-40, -240, 80, 38))
    for c in range(3): e.append(rect(-30 + c * 24, -232, 12, 20, W))
    e.append(poly([(-52, -240), (52, -240), (0, -262)]))
    for s in (-1, 1):
        x = s * 136
        e.append(rect(x - 30, -250, 60, 50))
        for c in range(2): e.append(rect(x - 20 + c * 26, -242, 14, 30, W))
        e.append(f'<path d="M{x-36},-250 C{x-36},-298 {x-12},-322 {x},-334 C{x+12},-322 {x+36},-298 {x+36},-250z" fill="{BLACK}"/>')
        e.append(rect(x - 3, -358, 6, 26)); e.append(f'<circle cx="{x}" cy="-362" r="6" fill="{BLACK}"/>')
    for x, h, l, sc in [(-310, 200, -6, .62), (-226, 245, 10, .74), (226, 240, -10, .74), (310, 195, 6, .62)]: e.append(palm(x, h, l, sc))
    return '\n'.join(e)

if __name__ == '__main__':
    build('fr_paris', 'NeLazurka', 'fr', eiffel, 'k', 0.7, False)
    build('fr_nice', 'NeLazurka', 'fr', make.riviera, 'k', 1.0, False)
    build('fr_cannes', 'NeLazurka', 'fr', carlton, 'k', 0.9, False)
    print('ok')
