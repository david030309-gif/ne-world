"""Side profiles (facing right, wheels on y=0) of a Ferrari 488 Pista and a Rolls-Royce Phantom VIII,
drawn from their real proportions. Black silhouettes with white glass and details."""
import math
B, W = '#0d0d0d', '#fff'
def r(x, y, w, h, f=B): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{f}"/>'

def wheel(cx, R, spokes, style):
    g = [f'<circle cx="{cx}" cy="{-R}" r="{R}" fill="{B}"/>', f'<circle cx="{cx}" cy="{-R}" r="{R*.7:.2f}" fill="{W}"/>']
    if style == 'pista':      # thin 5 double-spoke forged rim
        for i in range(spokes):
            a = math.radians(90 + i * 360 / spokes)
            for da in (-.12, .12):
                g.append(f'<path d="M{cx},{-R} L{cx+R*.68*math.cos(a+da):.2f},{-R-R*.68*math.sin(a+da):.2f}" stroke="{B}" stroke-width="{R*.09:.2f}"/>')
        g.append(f'<circle cx="{cx}" cy="{-R}" r="{R*.5:.2f}" fill="none" stroke="{B}" stroke-width="{R*.05:.2f}"/>')
    else:                      # Phantom: many fine spokes and a big centre disc
        for i in range(spokes):
            a = math.radians(90 + i * 360 / spokes)
            g.append(f'<path d="M{cx+R*.25*math.cos(a):.2f},{-R-R*.25*math.sin(a):.2f} L{cx+R*.68*math.cos(a):.2f},{-R-R*.68*math.sin(a):.2f}" stroke="{B}" stroke-width="{R*.07:.2f}"/>')
        g.append(f'<circle cx="{cx}" cy="{-R}" r="{R*.26:.2f}" fill="{B}"/><circle cx="{cx}" cy="{-R}" r="{R*.12:.2f}" fill="{W}"/>')
    g.append(f'<circle cx="{cx}" cy="{-R}" r="{R*.08:.2f}" fill="{B}"/>')
    return g

def pista():
    """Ferrari 488 Pista: 153 x 40 units (4605 x 1206 mm / 30), wheelbase 88."""
    fx, rx, R = 120, 32, 11.6
    body = (f"M2,-9 L0,-21 L1,-29 L3,-33 L12,-33 Q30,-34 44,-37 Q58,-41 70,-41.5 Q82,-41.5 90,-38 "
            f"Q100,-33 110,-28 Q124,-25 132,-24 Q144,-22 150,-19 L153,-15 L153,-11 L150,-6 L140,-5 "
            f"L{fx+R+3},-5 A{R+2.4},{R+2.4} 0 0 0 {fx-R-3},-5 L{rx+R+3},-5 A{R+2.4},{R+2.4} 0 0 0 {rx-R-3},-5 L6,-6 z")
    g = [f'<path d="{body}" fill="{B}"/>']
    g.append(f'<path d="M97,-32.8 Q89,-37.2 78,-37.8 L68.5,-37.2 L67.5,-32.4 Q84,-31.4 97,-32.8z" fill="{W}"/>')       # side glass
    g.append(f'<path d="M63.5,-36.6 L52,-35.2 L58.5,-33 L63,-32.6z" fill="{W}"/>')                            # engine-cover glass
    g.append(f'<path d="M132,-23 Q141,-21.5 148,-19 L146,-17.5 Q139,-19.5 131,-21.5z" fill="{W}"/>')    # headlight
    g.append(r(1, -30, 3, 3, W)); g.append(r(1, -25, 3, 2, W))                                          # tail lights
    g.append(f'<path d="M98,-31 L104,-33 L106,-31 L101,-30z" fill="{B}"/>' f'<path d="M100,-31 L99,-29" stroke="{B}" stroke-width="1"/>')  # mirror
    g += wheel(rx, R, 5, 'pista') + wheel(fx, R, 5, 'pista')
    return g

def phantom():
    """Rolls-Royce Phantom VIII: 160 x 46 units (5762 x 1646 mm / 36), wheelbase 99, coach doors."""
    fx, rx, R = 134, 35, 12
    body = (f"M1,-11 L0,-27 Q0,-34 6,-35 L28,-36 Q36,-37 42,-44 Q46,-47 56,-47 L94,-47 Q100,-47 104,-43 "
            f"L112,-37 L150,-36 Q158,-36 159,-34 L160,-13 L157,-9 L{fx+R+3},-9 A{R+2.6},{R+2.6} 0 0 0 {fx-R-3},-9 "
            f"L{rx+R+3},-9 A{R+2.6},{R+2.6} 0 0 0 {rx-R-3},-9 L4,-9 z")
    g = [f'<path d="{body}" fill="{B}"/>']
    g.append(f'<path d="M45,-37 L49,-42 Q52,-44.5 58,-44.5 L74,-44.5 L74,-37z" fill="{W}"/>')            # rear door glass
    g.append(f'<path d="M77,-37 L77,-44.5 L94,-44.5 Q99,-44 102,-41 L107,-37z" fill="{W}"/>')           # front door glass
    g.append(f'<path d="M44,-36 L50,-44 Q53,-46 58,-46 L94,-46 Q100,-45.5 104,-41 L109,-36z" fill="none" stroke="{W}" stroke-width=".8"/>')  # chrome surround
    g.append(f'<path d="M6,-31 L152,-33" stroke="{W}" stroke-width=".8"/>')                             # waist line
    g.append(f'<path d="M6,-14 Q80,-17 157,-12" stroke="{W}" stroke-width=".8" fill="none"/>')           # rising waft line
    g.append(f'<path d="M75.5,-36 L75.5,-12" stroke="{W}" stroke-width=".7"/><path d="M110,-35 L110,-15" stroke="{W}" stroke-width=".7"/>')
    g.append(r(155.5, -34.5, 4.5, 21, W)); [g.append(r(156.2 + k * 1.3, -33.5, .55, 19)) for k in range(3)]   # Pantheon grille
    g.append(f'<path d="M157,-36 L158.2,-41 L159.6,-36.5z" fill="{B}"/>')                                # Spirit of Ecstasy
    g.append(r(150, -33, 5, 3, W)); g.append(r(150, -28.5, 5, 1.2, W))                                  # headlights
    g.append(r(0.5, -31, 3, 6, W))                                                                     # tail light
    g.append(f'<path d="M108,-37 L114,-40 L116,-37z" fill="{B}"/>')
    g.append(r(50, -24, 6, 1, W)); g.append(r(86, -24, 6, 1, W))                                        # door handles
    g += wheel(rx, R, 16, 'phantom') + wheel(fx, R, 16, 'phantom')
    return g

if __name__ == '__main__':
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -60 340 70" width="1360" height="280"><rect x="-5" y="-60" width="340" height="70" fill="#fff"/>',
           *pista(), '<g transform="translate(170,0)">', *phantom(), '</g></svg>']
    open('/tmp/cars.svg', 'w').write('\n'.join(svg))
