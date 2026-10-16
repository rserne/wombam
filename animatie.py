"""Maakt van de twee losse wombat-tekeningen (SVG) een bewegende versie.

De tekening blijft zoals hij is; er komt alleen iets omheen:
- de juichende wombat (blij) springt op en neer, wiebelt mee en laat de juichstreepjes naast zijn handen flitsen;
- de sippe wombat (sip) zucht, knippert langzaam en laat tranen over zijn wangen lopen.

De armen worden 'uitgeknipt': de tekening staat er drie keer in, één keer zonder armen
en twee keer alleen een arm, die rond de schouder draait. Alles in SVG met CSS-animaties,
zodat het ook werkt als gewone <img>.

Wordt gebruikt door build.py.
"""
import re

# Coördinaten in de tekening (viewBox 0 0 1536 2048).
BLIJ = {
    'voet': (768, 1880),          # rond dit punt veert hij in bij het springen
    'armen': [],                  # de armen zitten vast aan het lijf; hij juicht met zijn hele lijf
    'glans': (253, 211, 3),       # de gele juichstreepjes naast zijn handen: die flitsen
    'ogen': [],                   # zijn ogen zijn dichtgeknepen van plezier: niets te knipperen
    'tranen': [],
}
SIP = {
    'voet': (768, 1860),
    'armen': [],
    # ogen: middelpunt, straal x/y, kleur van de vacht eromheen
    'ogen': [((676, 745), 78, 72, '#AB7C5C'), ((1106, 818), 64, 62, '#AB7C5C')],
    'tranen': [(642, 875), (1120, 965)],
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

    glans = ''
    if cfg.get('glans'):
        kleur = 'rgb(%d,%d,%d)' % cfg['glans']
        paden = re.findall(r'<path[^>]*/>', tekening)
        links, rechts = [], []
        for i, pad in enumerate(paden):
            if f'fill="{kleur}"' in pad:
                stuk = [pad]
                if i and 'fill="rgb(0,0,0)"' in paden[i - 1]:
                    stuk.insert(0, paden[i - 1])      # de zwarte omlijning hoort erbij
                x = float(re.search(r'd="M ([\d.]+)', pad).group(1))
                (links if x < 768 else rechts).extend(stuk)
        for pad in links + rechts:
            tekening = tekening.replace(pad, '')
        glans = (f'<g class="glans gl" style="transform-origin:330px 470px">{"".join(links)}</g>'
                 f'<g class="glans gr" style="transform-origin:1240px 480px">{"".join(rechts)}</g>')

    armen = cfg['armen']
    clips, lagen = '', ''
    if armen:
        gaten = ' '.join(_poly(a[1]) for a in armen)
        clips += f'<clipPath id="romp"><path clip-rule="evenodd" d="M-300 -300H2400V2400H-300Z {gaten}"/></clipPath>'
        lagen += '<use href="#w" clip-path="url(#romp)"/>'
        for naam, pts, (px, py), _, _ in armen:
            clips += f'<clipPath id="arm-{naam}"><path d="{_poly(_overlap(pts))}"/></clipPath>'
            lagen += f'<g class="arm arm-{naam}" style="transform-origin:{px}px {py}px"><use href="#w" clip-path="url(#arm-{naam})"/></g>'
    else:
        lagen += '<use href="#w"/>'

    lagen += glans

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
.spring{transform-origin:VXpx VYpx;animation:hop 1s ease-in-out infinite}
@keyframes hop{0%,100%{transform:translateY(0) scale(1.03,.97)}45%{transform:translateY(-70px) scale(.98,1.02)}55%{transform:translateY(-70px) scale(.98,1.02)}}
.rek{transform-origin:VXpx VYpx;animation:wiebel 2s ease-in-out infinite}
@keyframes wiebel{0%,100%{transform:rotate(-2.5deg)}50%{transform:rotate(2.5deg)}}
.glans{animation:flits 1s ease-out infinite}
@keyframes flits{0%,30%{transform:scale(.7);opacity:.3}50%{transform:scale(1.15);opacity:1}100%{transform:scale(.9);opacity:.6}}
"""
    else:
        css = """
.spring{transform-origin:VXpx VYpx;animation:zucht 3.6s ease-in-out infinite}
@keyframes zucht{0%,100%{transform:scale(1,1)}40%{transform:scale(1.012,.975) translateY(10px)}}
.lid{transform:scaleY(0);animation:knipper 5s infinite}
@keyframes knipper{0%,84%,100%{transform:scaleY(0)}88%,93%{transform:scaleY(1)}}
.traan{opacity:0;animation:traan 2.6s ease-in infinite}
.t1{animation-delay:-1.3s}
@keyframes traan{0%{opacity:0;transform:translateY(-10px) scale(.4)}15%{opacity:1;transform:translateY(0) scale(1)}80%{opacity:1}100%{opacity:0;transform:translateY(230px) scale(.9)}}
"""
    css = css.replace('VX', str(cfg['voet'][0])).replace('VY', str(cfg['voet'][1]))
    css += '.lid,.traan,.glans,.rek{transform-box:view-box}\n@media (prefers-reduced-motion:reduce){*{animation:none!important}}\n'
    if pose:
        css = pose

    return (f'{open_tag}<style>{css}</style><defs>{defs_in}<g id="w">{tekening}</g>{clips}</defs>'
            f'<g class="spring"><g class="rek">{lagen}</g></g></svg>\n')
