"""Maakt van de twee losse wombat-tekeningen (SVG) een bewegende versie.

De tekening blijft zoals hij is; er komt alleen iets omheen:
- de juichende wombat (blij) zwaait met zijn armen, springt op en neer en knippert met zijn ogen;
- de sippe wombat (sip) zucht, knippert langzaam en laat tranen over zijn wangen lopen.

De armen worden 'uitgeknipt': de tekening staat er drie keer in, één keer zonder armen
en twee keer alleen een arm, die rond de schouder draait. Alles in SVG met CSS-animaties,
zodat het ook werkt als gewone <img>.

Wordt gebruikt door build.py.
"""
import re

# Coördinaten in de tekening (viewBox 0 0 2048 2048).
BLIJ = {
    'armen': [
        # (naam, omtrek van het uitknipstuk, draaipunt, hoek laag, hoek hoog)
        ('l', [(495, 840), (440, 760), (380, 700), (300, 680), (40, 700), (20, 1070), (240, 1180),
               (470, 1310), (600, 1255)], (548, 1048), -5, 9),
        ('r', [(1590, 960), (1650, 880), (1700, 820), (2020, 860), (2030, 1200), (1820, 1280),
               (1600, 1370), (1500, 1335)], (1545, 1148), 5, -9),
    ],
    # ogen: middelpunt, straal x/y, kleur van de vacht eromheen, bocht van het dichte oog
    'ogen': [((838, 500), 132, 128, '#F78E24'), ((1322, 592), 124, 146, '#F78E24')],
    'tranen': [],
}
SIP = {
    'armen': [],
    'ogen': [((842, 618), 138, 140, '#F4841D'), ((1276, 686), 118, 142, '#F4841D')],
    'tranen': [(1236, 810), (884, 748)],
}


def _overlap(pts, d=40):
    """Het uitknipstuk van een arm loopt iets door in de romp, zodat er bij de schouder geen naadje te zien is."""
    (tx, ty), (bx, by) = pts[0], pts[-1]
    mx, my = sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts)
    nx, ny = -(by - ty), bx - tx
    lengte = (nx * nx + ny * ny) ** 0.5
    nx, ny = nx / lengte, ny / lengte
    if nx * ((tx + bx) / 2 - mx) + ny * ((ty + by) / 2 - my) < 0:   # weg van de arm, de romp in
        nx, ny = -nx, -ny
    return [(round(tx + nx * d), round(ty + ny * d))] + pts + [(round(bx + nx * d), round(by + ny * d))]


def _poly(pts):
    return 'M' + ' L'.join(f'{x} {y}' for x, y in pts) + ' Z'


def animeer(svg, cfg, soort, pose=None):
    """svg: de opgeschoonde tekening. pose: alleen voor testen (vaste stand in plaats van animatie)."""
    open_tag = re.match(r'<svg[^>]*>', svg).group(0)
    binnen = svg[len(open_tag):svg.rindex('</svg>')]
    defs = ''.join(re.findall(r'<defs>.*?</defs>', binnen, re.S))
    defs_in = re.sub(r'</?defs>', '', defs)
    tekening = re.sub(r'<defs>.*?</defs>', '', binnen, flags=re.S)

    armen = cfg['armen']
    clips, lagen = '', ''
    if armen:
        gaten = ' '.join(_poly(a[1]) for a in armen)
        clips += f'<clipPath id="romp"><path clip-rule="evenodd" d="M-300 -300H2348V2348H-300Z {gaten}"/></clipPath>'
        lagen += '<use href="#w" clip-path="url(#romp)"/>'
        for naam, pts, (px, py), _, _ in armen:
            clips += f'<clipPath id="arm-{naam}"><path d="{_poly(_overlap(pts))}"/></clipPath>'
            lagen += f'<g class="arm arm-{naam}" style="transform-origin:{px}px {py}px"><use href="#w" clip-path="url(#arm-{naam})"/></g>'
    else:
        lagen += '<use href="#w"/>'

    # oogleden: een vlak in de kleur van de vacht met een gesloten-ooglijn, dat van boven naar beneden zakt
    for i, ((cx, cy), rx, ry, kleur) in enumerate(cfg['ogen']):
        top = cy - ry
        lijn = f'M{cx - rx * 0.78:.0f} {cy + ry * 0.05:.0f} Q{cx} {cy + ry * 0.5:.0f} {cx + rx * 0.78:.0f} {cy + ry * 0.05:.0f}'
        lagen += (f'<g class="lid" style="transform-origin:{cx}px {top}px">'
                  f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{kleur}"/>'
                  f'<path d="{lijn}" fill="none" stroke="#1E120B" stroke-width="22" stroke-linecap="round"/></g>')

    # tranen
    for i, (x, y) in enumerate(cfg['tranen']):
        drup = (f'M{x} {y - 50} C{x + 9} {y - 20} {x + 38} {y + 8} {x + 38} {y + 34} '
                f'A38 38 0 0 1 {x - 38} {y + 34} C{x - 38} {y + 8} {x - 9} {y - 20} {x} {y - 50} Z')
        lagen += (f'<g class="traan t{i}" style="transform-origin:{x}px {y}px"><path d="{drup}" fill="#7FD3FF" stroke="#1E120B" stroke-width="8"/>'
                  f'<ellipse cx="{x - 13}" cy="{y + 26}" rx="10" ry="14" fill="#fff" opacity=".85"/></g>')

    if soort == 'blij':
        css = """
.spring{transform-origin:1024px 1960px;animation:hop 1s ease-in-out infinite}
@keyframes hop{0%,100%{transform:translateY(0) scale(1.03,.97)}45%{transform:translateY(-70px) scale(.98,1.02)}55%{transform:translateY(-70px) scale(.98,1.02)}}
.arm-l{animation:zwaai-l .5s ease-in-out infinite alternate}
.arm-r{animation:zwaai-r .5s ease-in-out infinite alternate;animation-delay:-.25s}
@keyframes zwaai-l{from{transform:rotate(L0deg)}to{transform:rotate(L1deg)}}
@keyframes zwaai-r{from{transform:rotate(R0deg)}to{transform:rotate(R1deg)}}
.lid{transform:scaleY(0);animation:knipper 3.4s infinite}
@keyframes knipper{0%,90%,100%{transform:scaleY(0)}93%,96%{transform:scaleY(1)}}
""".replace('L0', str(armen[0][3])).replace('L1', str(armen[0][4])).replace('R0', str(armen[1][3])).replace('R1', str(armen[1][4]))
    else:
        css = """
.spring{transform-origin:1024px 1960px;animation:zucht 3.6s ease-in-out infinite}
@keyframes zucht{0%,100%{transform:scale(1,1)}40%{transform:scale(1.012,.975) translateY(10px)}}
.lid{transform:scaleY(0);animation:knipper 5s infinite}
@keyframes knipper{0%,84%,100%{transform:scaleY(0)}88%,93%{transform:scaleY(1)}}
.traan{opacity:0;animation:traan 2.6s ease-in infinite}
.t1{animation-delay:-1.3s}
@keyframes traan{0%{opacity:0;transform:translateY(-10px) scale(.4)}15%{opacity:1;transform:translateY(0) scale(1)}80%{opacity:1}100%{opacity:0;transform:translateY(230px) scale(.9)}}
"""
    css += '.lid,.traan{transform-box:view-box}\n@media (prefers-reduced-motion:reduce){*{animation:none!important}}\n'
    if pose:
        css = pose

    return (f'{open_tag}<style>{css}</style><defs>{defs_in}<g id="w">{tekening}</g>{clips}</defs>'
            f'<g class="spring">{lagen}</g></svg>\n')
