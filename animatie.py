"""Maakt van de twee losse wombat-tekeningen (SVG) een bewegende versie.

De tekening zelf blijft zoals hij is; er komt alleen iets omheen.

Blij (je wint):
- springt: eerst door de knieën, dan omhoog met de armen de lucht in, en weer landen (inveren);
- een schaduw op de grond die kleiner wordt als hij hoog is;
- knippert af en toe met zijn ogen;
- confetti dwarrelt naar beneden, deels achter en deels voor hem.

Sip (je verliest):
- zucht diep en snikt af en toe even;
- knippert langzaam;
- tranen wellen op, lopen over zijn wangen (met een nat spoortje) en druppen eraf;
- een grijs wolkje boven zijn hoofd laat het op hem regenen.

De armen van de blije wombat worden 'uitgeknipt': de tekening staat er drie keer in, één keer
zonder armen en twee keer alleen een arm, die rond de schouder draait. Alles is SVG met
CSS-animaties, zodat het ook werkt als gewone <img> en offline.

Wordt gebruikt door build.py.
"""
import random
import re

# Coördinaten in de tekening (die loopt van 0 tot 2048). De ruimte erboven is voor de sprong en het wolkje.
VIEWBOX = '-120 -420 2288 2430'
GROND = 1935          # waar de voeten staan

BLIJ = {
    'armen': [
        # (naam, omtrek van het uitknipstuk, draaipunt)
        ('l', [(495, 840), (440, 760), (380, 700), (300, 680), (40, 700), (20, 1070), (240, 1180),
               (470, 1310), (600, 1255)], (548, 1048)),
        ('r', [(1590, 960), (1650, 880), (1700, 820), (2020, 860), (2030, 1200), (1820, 1280),
               (1600, 1370), (1500, 1335)], (1545, 1148)),
    ],
    # ogen: middelpunt, straal x/y, kleur van de vacht eromheen
    'ogen': [((838, 500), 132, 128, '#F78E24'), ((1322, 592), 124, 146, '#F78E24')],
    'tranen': [],
}
SIP = {
    'armen': [],
    'ogen': [((842, 618), 138, 140, '#F4841D'), ((1276, 686), 118, 142, '#F4841D')],
    # traan: begin (ooghoek) en het spoor over de wang
    'tranen': [((1232, 806), 'M1232 806 C1240 880 1252 960 1262 1040'),
               ((888, 746), 'M888 746 C880 820 868 900 856 985')],
}

INKT = '#1E120B'


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


def _oogleden(ogen):
    h = ''
    for (cx, cy), rx, ry, kleur in ogen:
        lijn = (f'M{cx - rx * 0.78:.0f} {cy + ry * 0.05:.0f} '
                f'Q{cx} {cy + ry * 0.5:.0f} {cx + rx * 0.78:.0f} {cy + ry * 0.05:.0f}')
        h += (f'<g class="lid" style="transform-origin:{cx}px {cy - ry}px">'
              f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{kleur}"/>'
              f'<path d="{lijn}" fill="none" stroke="{INKT}" stroke-width="22" stroke-linecap="round"/></g>')
    return h


def _schaduw(cls=''):
    return f'<ellipse class="schaduw {cls}" cx="1010" cy="{GROND}" rx="470" ry="58" fill="#000" opacity=".16"/>'


def _confetti(n, seed, voor):
    """Snippers die van boven naar beneden dwarrelen. Elk snipper valt (buitenste groep) en draait (binnenste)."""
    rnd = random.Random(seed)
    kleuren = ['#FFD23F', '#E0441C', '#2E9E3E', '#1E6FD8', '#7B2FBE', '#E0457B', '#FFFFFF']
    h, css = '', ''
    for i in range(n):
        x = rnd.randint(-60, 2110)
        if voor and 560 < x < 1480:        # vóór de wombat niet midden over zijn gezicht
            x = rnd.choice([rnd.randint(-60, 560), rnd.randint(1480, 2110)])
        w, l = rnd.randint(48, 66), rnd.randint(84, 120)
        kl = rnd.choice(kleuren)
        duur = rnd.uniform(2.6, 4.2)
        vertraging = -rnd.uniform(0, duur)
        drift = rnd.choice([-1, 1]) * rnd.randint(60, 200)
        draai = rnd.choice(['flip-a', 'flip-b', 'flip-c'])
        naam = f'c{"v" if voor else "a"}{i}'
        rond = rnd.random() < 0.3
        vorm = (f'<circle r="{w // 2 + 4}" fill="{kl}"/>' if rond else
                f'<rect x="{-w // 2}" y="{-l // 2}" width="{w}" height="{l}" rx="6" fill="{kl}"/>')
        h += (f'<g class="val {naam}" transform="translate({x} -460)"><g class="{draai}" '
              f'style="animation-duration:{rnd.uniform(0.7, 1.4):.2f}s">{vorm}</g></g>')
        css += (f'.{naam}{{animation:{naam} {duur:.2f}s linear {vertraging:.2f}s infinite}}'
                f'@keyframes {naam}{{from{{transform:translate({x}px,-460px)}}'
                f'50%{{transform:translate({x + drift}px,800px)}}'
                f'to{{transform:translate({x - drift // 2}px,2080px)}}}}\n')
    return h, css


def _wolkje():
    """Een grijs regenwolkje boven het hoofd, met druppels die op de wombat vallen."""
    bollen = [(800, -170, 130), (960, -230, 165), (1140, -200, 140), (1270, -150, 105), (690, -130, 95)]
    rand = ''.join(f'<circle cx="{x}" cy="{y}" r="{r + 20}" fill="{INKT}"/>' for x, y, r in bollen)
    rand += f'<rect x="680" y="-150" width="680" height="70" rx="35" fill="{INKT}"/>'
    vul = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9AA3B5"/>' for x, y, r in bollen)
    vul += '<rect x="690" y="-140" width="660" height="50" rx="25" fill="#9AA3B5"/>'
    licht = ''.join(f'<circle cx="{x - r * .25:.0f}" cy="{y - r * .3:.0f}" r="{r * .55:.0f}" fill="#B9C0CE"/>'
                    for x, y, r in bollen[:3])
    druppels = ''
    for i, x in enumerate([760, 880, 1000, 1120, 1240, 940, 1180]):
        druppels += (f'<path class="regen r{i}" d="M{x} -70 c8 32 30 54 30 78 a30 30 0 0 1 -60 0 c0 -24 22 -46 30 -78z" '
                     f'fill="#7FD3FF" stroke="{INKT}" stroke-width="8"/>')
    return f'<g class="regen-lagen">{druppels}</g><g class="wolk">{rand}{vul}{licht}</g>'


def animeer(svg, cfg, soort, pose=None):
    """svg: de opgeschoonde tekening. pose: alleen voor testen (vaste CSS in plaats van de animatie)."""
    tag = re.match(r'<svg[^>]*>', svg)
    open_tag = re.sub(r'viewBox="[^"]*"', f'viewBox="{VIEWBOX}"', tag.group(0))
    binnen = svg[tag.end():svg.rindex('</svg>')]
    defs_in = re.sub(r'</?defs>', '', ''.join(re.findall(r'<defs>.*?</defs>', binnen, re.S)))
    tekening = re.sub(r'<defs>.*?</defs>', '', binnen, flags=re.S)

    clips, lijf = '', ''
    if cfg['armen']:
        gaten = ' '.join(_poly(a[1]) for a in cfg['armen'])
        clips += f'<clipPath id="romp"><path clip-rule="evenodd" d="M-300 -600H2348V2348H-300Z {gaten}"/></clipPath>'
        lijf += '<use href="#w" clip-path="url(#romp)"/>'
        for naam, pts, (px, py) in cfg['armen']:
            clips += f'<clipPath id="arm-{naam}"><path d="{_poly(_overlap(pts))}"/></clipPath>'
            lijf += (f'<g class="arm arm-{naam}" style="transform-origin:{px}px {py}px">'
                     f'<use href="#w" clip-path="url(#arm-{naam})"/></g>')
    else:
        lijf += '<use href="#w"/>'
    lijf += _oogleden(cfg['ogen'])

    if soort == 'blij':
        achter, css_a = _confetti(14, 7, False)
        voor, css_v = _confetti(9, 11, True)
        lagen = (_schaduw() + f'<g class="confetti">{achter}</g>'
                 f'<g class="spring"><g class="rek">{lijf}</g></g>'
                 f'<g class="confetti">{voor}</g>')
        css = """
/* één sprong per 1,3 s: door de knieën, afzetten, hangen, landen en inveren */
.spring{animation:sprong 1.3s infinite}
@keyframes sprong{
 0%,12%{transform:translateY(0);animation-timing-function:cubic-bezier(.2,.6,.35,1)}
 42%{transform:translateY(-230px);animation-timing-function:ease-in-out}
 54%{transform:translateY(-240px);animation-timing-function:cubic-bezier(.6,0,.85,.45)}
 80%,100%{transform:translateY(0)}}
.rek{transform-origin:1010px 1935px;animation:rek 1.3s infinite}
@keyframes rek{
 0%{transform:scale(1,1)}
 10%{transform:scale(1.07,.9)}
 22%{transform:scale(.95,1.07)}
 42%,58%{transform:scale(1,1)}
 74%{transform:scale(.97,1.04)}
 82%{transform:scale(1.09,.88)}
 90%{transform:scale(.98,1.03)}
 100%{transform:scale(1,1)}}
.arm-l{animation:arm-l 1.3s infinite}
.arm-r{animation:arm-r 1.3s infinite}
@keyframes arm-l{0%,100%{transform:rotate(0)}10%{transform:rotate(-8deg)}30%{transform:rotate(15deg)}
 46%{transform:rotate(10deg)}56%{transform:rotate(16deg)}72%{transform:rotate(6deg)}84%{transform:rotate(-6deg)}}
@keyframes arm-r{0%,100%{transform:rotate(0)}10%{transform:rotate(8deg)}30%{transform:rotate(-15deg)}
 46%{transform:rotate(-10deg)}56%{transform:rotate(-16deg)}72%{transform:rotate(-6deg)}84%{transform:rotate(6deg)}}
.schaduw{transform-origin:1010px 1935px;animation:schaduw 1.3s infinite}
@keyframes schaduw{
 0%,12%{transform:scale(1.04);opacity:.18;animation-timing-function:cubic-bezier(.2,.6,.35,1)}
 42%,54%{transform:scale(.62);opacity:.08;animation-timing-function:cubic-bezier(.6,0,.85,.45)}
 80%{transform:scale(1.1);opacity:.2}100%{transform:scale(1.04);opacity:.18}}
.lid{transform:scaleY(0);animation:knipper 3.9s infinite}
@keyframes knipper{0%,88%,100%{transform:scaleY(0)}91%,94%{transform:scaleY(1)}}
.flip-a,.flip-b,.flip-c{animation-iteration-count:infinite;animation-timing-function:linear}
.flip-a{animation-name:flip-a}.flip-b{animation-name:flip-b}.flip-c{animation-name:flip-c}
@keyframes flip-a{from{transform:rotate(0) scaleX(1)}50%{transform:rotate(180deg) scaleX(-.3)}to{transform:rotate(360deg) scaleX(1)}}
@keyframes flip-b{from{transform:rotate(30deg) scaleY(1)}50%{transform:rotate(-150deg) scaleY(.2)}to{transform:rotate(-330deg) scaleY(1)}}
@keyframes flip-c{from{transform:rotate(-20deg) scale(1,1)}50%{transform:rotate(90deg) scale(.4,1)}to{transform:rotate(340deg) scale(1,1)}}
""" + css_a + css_v
    else:
        tranen, css_t = '', ''
        for i, ((x, y), spoor) in enumerate(cfg['tranen']):
            drup = (f'M{x} {y - 50} C{x + 9} {y - 20} {x + 38} {y + 8} {x + 38} {y + 34} '
                    f'A38 38 0 0 1 {x - 38} {y + 34} C{x - 38} {y + 8} {x - 9} {y - 20} {x} {y - 50} Z')
            (_, _, ex, ey) = [float(v) for v in re.findall(r'-?\d+', spoor)[-4:]]
            dx, dy = ex - x, ey - y
            tranen += (f'<path class="spoor s{i}" d="{spoor}" fill="none" stroke="#BDEBFF" stroke-width="26" '
                       f'stroke-linecap="round" pathLength="100"/>'
                       f'<g class="traan t{i}" style="transform-origin:{x}px {y}px">'
                       f'<path d="{drup}" fill="#7FD3FF" stroke="{INKT}" stroke-width="8"/>'
                       f'<ellipse cx="{x - 13}" cy="{y + 26}" rx="10" ry="14" fill="#fff" opacity=".9"/></g>')
            css_t += (f'@keyframes traan{i}{{0%{{opacity:0;transform:translate(0,0) scale(.15)}}'
                      f'18%{{opacity:1;transform:translate(0,0) scale(.75)}}'
                      f'30%{{transform:translate(0,4px) scale(1)}}'
                      f'72%{{opacity:1;transform:translate({dx:.0f}px,{dy:.0f}px) scale(1)}}'
                      f'90%{{opacity:1;transform:translate({dx * 1.15:.0f}px,{dy + 160:.0f}px) scale(.9,1.1)}}'
                      f'100%{{opacity:0;transform:translate({dx * 1.2:.0f}px,{dy + 260:.0f}px) scale(.8,1.15)}}}}\n')
        lagen = (_schaduw('stil') + f'<g class="spring"><g class="rek">{lijf}{tranen}</g></g>' + _wolkje())
        css = """
/* zuchten (langzaam) en twee keer kort snikken */
.rek{transform-origin:1010px 1935px;animation:zucht 4.8s infinite ease-in-out}
@keyframes zucht{
 0%{transform:scale(1,1)}
 30%{transform:scale(1.015,1.035)}
 52%{transform:scale(1.02,.955)}
 62%{transform:scale(1,1)}
 66%{transform:scale(1,1.02) translateY(-10px)}
 69%{transform:scale(1,.99)}
 73%{transform:scale(1,1.02) translateY(-10px)}
 77%,100%{transform:scale(1,1)}}
.lid{transform:scaleY(0);animation:knipper 4.8s infinite}
@keyframes knipper{0%,40%,100%{transform:scaleY(0)}45%,58%{transform:scaleY(1)}63%{transform:scaleY(0)}}
.traan{opacity:0;animation:3.2s ease-in infinite}
.t0{animation-name:traan0}
.t1{animation-name:traan1;animation-delay:-1.6s}
.spoor{stroke-dasharray:100;stroke-dashoffset:100;opacity:0;animation:spoor 3.2s ease-in infinite}
.s1{animation-delay:-1.6s}
@keyframes spoor{0%,25%{stroke-dashoffset:100;opacity:0}30%{opacity:.75}72%{stroke-dashoffset:0;opacity:.75}100%{stroke-dashoffset:0;opacity:0}}
.wolk{animation:wolk 3.6s ease-in-out infinite}
@keyframes wolk{0%,100%{transform:translate(-14px,0)}50%{transform:translate(14px,-12px)}}
.regen{opacity:0;animation:regen 1.1s linear infinite}
@keyframes regen{0%{opacity:0;transform:translateY(0)}12%{opacity:1}80%{opacity:1}100%{opacity:0;transform:translateY(300px)}}
.r1{animation-delay:-.35s}.r2{animation-delay:-.75s}.r3{animation-delay:-.2s}
.r4{animation-delay:-.6s}.r5{animation-delay:-.95s}.r6{animation-delay:-.5s}
""" + css_t
    css += ('.lid,.traan,.spring,.rek,.schaduw,.val,.wolk,.regen{transform-box:view-box}\n'
            '.flip-a,.flip-b,.flip-c{transform-box:fill-box;transform-origin:center}\n'
            '@media (prefers-reduced-motion:reduce){*{animation:none!important}.confetti,.regen-lagen,.traan,.spoor{display:none}}\n')
    if pose:
        css = pose

    return (f'{open_tag}<style>{css}</style><defs>{defs_in}<g id="w">{tekening}</g>{clips}</defs>'
            f'{lagen}</svg>\n')
