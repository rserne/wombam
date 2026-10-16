#!/usr/bin/env python3
"""Bouwscript voor Wombam!

Maakt uit de bronbestanden in de map bron/ alle afbeeldingen die de app gebruikt,
en werkt de service worker bij (versienummer en lijst met bestanden).

Gebruik:
    pip install pillow
    python3 build.py            # afbeeldingen maken en versienummer ophogen
    python3 build.py --zelfde   # afbeeldingen maken, versienummer laten staan
    python3 build.py --voorbeeld   # ook voorbeeld.html maken: één bestand met alles erin

Wat waar vandaan komt:
    bron/icoon.png            -> icon-192.png, icon-512.png, icon-maskable-512.png,
                                 apple-touch-icon.png, favicon-32.png, favicon.ico
    bron/kaarten/<soort>.png  -> img/<soort>-kaart.webp (de hele kaart met de naam erop, 640 x 1000)
                                 img/<soort>.webp (de tekening zonder naam, voor de kaarten in je hand)
                                 img/face-<soort>.webp (portret voor de spelers)
    bron/achterkant.png       -> img/back.webp
    bron/ster.svg             -> img/star.svg
    bron/wombat-blij.svg      -> img/blij.svg (uitslag als je wint: zwaait, springt en knippert)
    bron/wombat-sip.svg       -> img/sip.svg  (uitslag als je verliest: zucht, knippert en huilt)
                                 De beweging staat in animatie.py.
"""
import re, shutil, sys
from pathlib import Path
from PIL import Image
from animatie import animeer, BLIJ, SIP

ROOT = Path(__file__).resolve().parent
BRON, IMG = ROOT / 'bron', ROOT / 'img'
SOORTEN = ['ek', 'defuse', 'attack', 'skip', 'shuffle', 'future', 'favor', 'nope',
           'beard', 'melon', 'potato', 'rainbow', 'taco']
# Uitsnede van het wombatkopje per kaart, als vierkant (links, boven, maat) in pixels van de brontekening.
GEZICHTEN = {
    'skip': (290, 230, 370), 'future': (205, 255, 370), 'beard': (195, 265, 390),
    'melon': (300, 240, 370), 'nope': (300, 280, 370), 'taco': (385, 395, 345),
}
W, H = 640, 1000          # alle kaarten krijgen deze vorm (staand, ongeveer als een echte speelkaart)


def _kaartvorm(pad):
    """Lees een kaart in, snij hem bij tot de kaart zelf (de rest is doorzichtig) en breng hem op W x H."""
    im = Image.open(pad).convert('RGBA')
    vak = im.split()[3].point(lambda v: 255 if v > 128 else 0).getbbox()
    return im.crop(vak).resize((W, H), Image.LANCZOS)


def kaarten():
    """Per soort: de hele kaart (img/<soort>-kaart.webp), de tekening zonder naam voor je hand (img/<soort>.webp)
    en voor zes soorten een portret (img/face-<soort>.webp). De achterkant wordt img/back.webp."""
    IMG.mkdir(exist_ok=True)
    for s in SOORTEN:
        bron = BRON / 'kaarten' / f'{s}.png'
        im = _kaartvorm(bron)
        im.save(IMG / f'{s}-kaart.webp', quality=86, method=6)
        im.convert('RGB').crop((round(W * .07), round(H * .30), round(W * .93), round(H * .96))).resize((420, 486), Image.LANCZOS).save(IMG / f'{s}.webp', quality=82, method=6)
        if s in GEZICHTEN:
            x, y, m = GEZICHTEN[s]
            Image.open(bron).convert('RGB').crop((x, y, x + m, y + m)).resize((192, 192), Image.LANCZOS).save(IMG / f'face-{s}.webp', quality=86, method=6)
    _kaartvorm(BRON / 'achterkant.png').save(IMG / 'back.webp', quality=86, method=6)
    shutil.copy(BRON / 'ster.svg', IMG / 'star.svg')


def wombats():
    """De twee losse wombats: achtergrond weg en getallen afronden, zodat het bestand een stuk kleiner wordt."""
    for bron, doel, cfg in (('wombat-blij.svg', 'blij', BLIJ), ('wombat-sip.svg', 'sip', SIP)):
        s = (BRON / bron).read_text(encoding='utf-8')
        m = re.search(r'<path[^>]*fill="(rgb\([^)]*\))" d="M 0 0 L 2048 0 L 2048 2048 L 0 2048 L 0 0 z"/>\n?', s)
        if m:
            s = s.replace(m.group(0), '')                            # het vlak achter de wombat
            s = s.replace(f'fill="{m.group(1)}"', 'fill="none"')     # gaatjes in dezelfde kleur
        s = re.sub(r'(\d+\.\d)\d+', r'\1', s)                        # één decimaal is genoeg
        s = s.replace(' transform="translate(0,0)"', '')
        s = re.sub(r' class="stop\d"', '', s)
        s = re.sub(r' (width|height)="1254"', '', s).replace(' style="display: block;"', '').replace(' preserveAspectRatio="none"', '')
        s = re.sub(r'\n\s*', '\n', s)
        (IMG / f'{doel}.svg').write_text(animeer(s, cfg, doel), encoding='utf-8')


ICOON_ACHTERGROND = (240, 90, 26)     # effen oranje rond de tegel


def _icoon_tegel(sq, schaal, n=1024):
    """Je tekening als afgeronde tegel met een wit randje en een zachte schaduw, midden op effen oranje."""
    from PIL import ImageDraw, ImageFilter

    def afgerond(maat):
        m = Image.new('L', (maat, maat), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, maat - 1, maat - 1), round(maat * 0.2), fill=255)
        return m

    vlak = Image.new('RGB', (n, n), ICOON_ACHTERGROND)
    k, b = round(n * schaal), round(n * 0.035)
    rand = afgerond(k + 2 * b)
    off = (n - k - 2 * b) // 2
    schaduw = Image.new('L', (n, n), 0)
    schaduw.paste(rand, (off, off + n // 70))
    schaduw = schaduw.filter(ImageFilter.GaussianBlur(n / 56)).point(lambda v: int(v * 0.35))
    vlak.paste((0, 0, 0), (0, 0, n, n), schaduw)
    vlak.paste((255, 255, 255), (off, off, off + k + 2 * b, off + k + 2 * b), rand)
    vlak.paste(sq.resize((k, k), Image.LANCZOS), (off + b, off + b), afgerond(k))
    return vlak


def iconen():
    """bron/icoon.png is een afgerond vierkant met doorzichtige hoeken. We knippen net binnen die hoeken een vol
    vierkant uit en zetten dat als tegel op oranje. Voor Android (dat zelf de vorm kiest, soms rond) iets kleiner."""
    im = Image.open(BRON / 'icoon.png').convert('RGBA')
    w = im.width
    m = round(w * 0.0625)                        # net binnen de afgeronde hoeken
    sq = im.crop((m, m, w - m, w - m)).convert('RGB')
    ic = _icoon_tegel(sq, 0.74)
    ic.resize((512, 512), Image.LANCZOS).save(ROOT / 'icon-512.png', optimize=True)
    ic.resize((192, 192), Image.LANCZOS).save(ROOT / 'icon-192.png', optimize=True)
    ic.resize((180, 180), Image.LANCZOS).save(ROOT / 'apple-touch-icon.png', optimize=True)
    ic.resize((32, 32), Image.LANCZOS).save(ROOT / 'favicon-32.png', optimize=True)
    ic.resize((48, 48), Image.LANCZOS).save(ROOT / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    _icoon_tegel(sq, 0.58).resize((512, 512), Image.LANCZOS).save(ROOT / 'icon-maskable-512.png', optimize=True)


def service_worker(ophogen):
    sw = ROOT / 'sw.js'
    tekst = sw.read_text(encoding='utf-8')
    if ophogen:
        tekst = re.sub(r"wombam-v(\d+)", lambda m: f"wombam-v{int(m.group(1)) + 1}", tekst, count=1)
    bestanden = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png',
                 'icon-maskable-512.png', 'apple-touch-icon.png', 'favicon.ico', 'favicon-32.png']
    bestanden += sorted(f'img/{p.name}' for p in IMG.iterdir() if p.is_file())
    lijst = 'const ASSETS=[' + ','.join(f"'{b}'" for b in bestanden) + '];'
    tekst = re.sub(r"const ASSETS=\[.*?\];", lijst, tekst, flags=re.S)
    sw.write_text(tekst, encoding='utf-8')
    versie = re.search(r"wombam-v\d+", tekst).group(0)
    print(f'Service worker: {versie}, {len(bestanden)} bestanden')


def voorbeeld():
    """Eén zelfstandig HTML-bestand, met alle afbeeldingen ingebakken (voor een snelle preview)."""
    import base64, json
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    soort = {'.webp': 'image/webp', '.svg': 'image/svg+xml', '.png': 'image/png'}
    data = {}
    for f in sorted(IMG.iterdir()):
        data[f'img/{f.name}'] = f'data:{soort[f.suffix]};base64,' + base64.b64encode(f.read_bytes()).decode()
    data['icon-192.png'] = 'data:image/png;base64,' + base64.b64encode((ROOT / 'icon-192.png').read_bytes()).decode()
    for k in ('img/star.svg',):
        html = html.replace(f'url({k})', f'url("{data[k]}")')
    html = re.sub(r'<link rel="(?:manifest|icon|apple-touch-icon)"[^>]*>\n', '', html)
    html = html.replace('<script>\n/* ENGINE-START */', '<script>window.WB_IMG=' + json.dumps(data) + ';</script>\n<script>\n/* ENGINE-START */', 1)
    schil = html.index('/* App-schil')
    html = html[:schil] + '/* (geen service worker in het voorbeeld) */})();</script>\n</body>\n</html>\n'
    html = html.replace('<script>\n/* (geen', '<script>(function(){\n/* (geen')
    (ROOT / 'voorbeeld.html').write_text(html, encoding='utf-8')
    print(f'voorbeeld.html: {len(html) // 1024} kB')


if __name__ == '__main__':
    kaarten()
    wombats()
    iconen()
    service_worker('--zelfde' not in sys.argv and '--voorbeeld' not in sys.argv)
    if '--voorbeeld' in sys.argv:
        voorbeeld()
    print('Klaar.')
