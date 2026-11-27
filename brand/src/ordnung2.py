"""NE ORDNUNG with the corners filled: Berlin TV tower + old Berlin houses on the left, the Reichstag on the right."""
import math
from make import rect, BLACK, build, gate
W = '#fff'
def poly(pts, fill=BLACK): return '<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="{fill}"/>'

EDGE = 529   # bar half-width in emblem units (402 px / 0.76)

def altbau(x, w, h):
    e = [rect(x, -h, w, h)]
    for r in range(int((h - 30) // 26)):
        for c in range(max(2, int(w // 16))):
            cw = (w - 8) / max(2, int(w // 16))
            e.append(rect(x + 4 + c * cw + cw * .22, -h + 12 + r * 26, cw * .56, 15, W))
    e.append(rect(x - 2, -h - 4, w + 4, 4))
    e.append(poly([(x, -h - 4), (x + w, -h - 4), (x + w - 6, -h - 22), (x + 6, -h - 22)]))
    return e

def fernsehturm(cx):
    e = [poly([(cx - 9, 0), (cx + 9, 0), (cx + 5, -250), (cx - 5, -250)])]
    for y in (-60, -130, -200): e.append(rect(cx - 6, y, 12, 2, W))
    e.append(f'<circle cx="{cx}" cy="-276" r="30" fill="{BLACK}"/>')
    e.append(f'<path d="M{cx-29},-282 A30,30 0 0 1 {cx+29},-282 L{cx+29},-276 A30,30 0 0 0 {cx-29},-276z" fill="{W}"/>')   # window band
    for k in range(-4, 5): e.append(rect(cx + k * 6.4 - .6, -284, 1.2, 9))
    e.append(rect(cx - 4, -330, 8, 26)); e.append(rect(cx - 2.2, -380, 4.4, 52))
    for y in (-344, -356, -368): e.append(rect(cx - 3.2, y, 6.4, 1.6, W))
    e.append(rect(cx - 1, -398, 2, 20))
    return e

def reichstag(x0, x1):
    w = x1 - x0; cx = (x0 + x1) / 2
    e = [rect(x0, -112, w, 112)]
    for t in (x0, x1 - 26):                                   # four corner towers (seen as two)
        e.append(rect(t, -150, 26, 150))
        for y in (-140, -100, -60): e.append(rect(t + 8, y, 10, 22, W))
        e.append(rect(t - 2, -154, 30, 4))
        for k in range(4): e.append(rect(t + 2 + k * 6.5, -160, 3.5, 6))
    for k in range(int((w - 70) // 12)):                     # side windows
        for y in (-96, -56): e.append(rect(x0 + 32 + k * 12, y, 6, 18, W))
    e.append(rect(cx - 30, -126, 60, 126))                   # portico with six columns and pediment
    for k in range(6): e.append(rect(cx - 25 + k * 9.6, -112, 4, 76, W))
    e.append(rect(cx - 34, -36, 68, 4)); e.append(rect(cx - 30, -24, 60, 2, W))
    e.append(poly([(cx - 36, -126), (cx + 36, -126), (cx, -146)]))
    e.append(poly([(cx - 24, -129), (cx + 24, -129), (cx, -141)], W))
    e.append(rect(x0 - 2, -116, w + 4, 4))
    # Foster's glass dome
    e.append(f'<path d="M{cx-34},-146 A34,34 0 0 1 {cx+34},-146z" fill="{BLACK}"/>')
    for k in range(-3, 4): e.append(f'<path d="M{cx+k*9.5:.1f},-146 Q{cx+k*6:.1f},-170 {cx},-180" fill="none" stroke="{W}" stroke-width="1.1"/>')
    for r in (12, 22): e.append(f'<path d="M{cx-math.sqrt(34**2-r**2):.1f},{-146-r} H{cx+math.sqrt(34**2-r**2):.1f}" stroke="{W}" stroke-width="1"/>')
    e.append(rect(cx - 6, -186, 12, 6))
    return e

def berliner_dom(x0, x1):
    """Berlin Cathedral: arched facade, big central dome with lantern and cross, two corner towers with small domes."""
    w = x1 - x0; cx = (x0 + x1) / 2
    e = [rect(x0, -104, w, 104), rect(x0 - 2, -108, w + 4, 4)]
    for k in range(3): e.append(f'<path d="M{cx-30+k*20},0 V-30 A8,9 0 0 1 {cx-14+k*20},-30 V0z" fill="{W}"/>')       # portal arches
    e.append(f'<path d="M{cx-18},-50 V-74 A18,18 0 0 1 {cx+18},-74 V-50z" fill="{W}"/>'); e.append(rect(cx - 1, -90, 2, 40))  # big window
    for t in (x0, x1 - 30):                                                     # corner towers
        e.append(rect(t, -150, 30, 150)); e.append(f'<path d="M{t+9},-70 V-108 A6,6 0 0 1 {t+21},-108 V-70z" fill="{W}"/>')
        e.append(rect(t - 2, -154, 34, 4))
        e.append(f'<path d="M{t+3},-154 C{t+3},-176 {t+12},-184 {t+15},-186 C{t+18},-184 {t+27},-176 {t+27},-154z" fill="{BLACK}"/>')
        e.append(rect(t + 13, -198, 4, 12)); e.append(f'<circle cx="{t+15}" cy="-201" r="3" fill="{BLACK}"/>')
    e.append(rect(cx - 34, -128, 68, 22)); e.append(rect(cx - 37, -131, 74, 3))  # drum
    for k in range(6): e.append(f'<path d="M{cx-27+k*10},-110 V-120 A3,3 0 0 1 {cx-21+k*10},-120 V-110z" fill="{W}"/>')
    e.append(f'<path d="M{cx-34},-131 C{cx-34},-176 {cx-14},-192 {cx},-194 C{cx+14},-192 {cx+34},-176 {cx+34},-131z" fill="{BLACK}"/>')
    for k in (-20, -8, 8, 20): e.append(f'<path d="M{cx+k},-134 Q{cx+k*.6},-170 {cx},-192" fill="none" stroke="{W}" stroke-width="1.2"/>')
    e.append(rect(cx - 6, -212, 12, 20)); e.append(rect(cx - 2.5, -208, 5, 10, W))
    e.append(f'<path d="M{cx-8},-212 Q{cx},-224 {cx+8},-212z" fill="{BLACK}"/>')
    e.append(rect(cx - 1.5, -244, 3, 22)); e.append(rect(cx - 6, -238, 12, 3))
    return e

def ordnung_full():
    e = [gate()]
    e += altbau(-EDGE, 40, 140) + fernsehturm(-462) + altbau(-438, 46, 116)
    e += berliner_dom(392, EDGE)
    return '\n'.join(e)

if __name__ == '__main__':
    build('ordnung', 'NE ORDNUNG', 'de', ordnung_full, 'O', 0.7, True)
    print('ok')
