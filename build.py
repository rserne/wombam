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
    bron/kaarten/<soort>.jpg  -> img/<soort>.webp (kaarttekening)
                                 img/face-<soort>.webp (portret voor de spelers)
    bron/achterkant.svg       -> img/back.svg
    bron/ster.svg             -> img/star.svg
    bron/wombat-blij.svg      -> img/blij.svg (uitslag als je wint; achtergrond doorzichtig)
    bron/wombat-sip.svg       -> img/sip.svg  (uitslag als je verliest)
"""
import re, shutil, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
BRON, IMG = ROOT / 'bron', ROOT / 'img'
SOORTEN = ['ek', 'defuse', 'attack', 'skip', 'shuffle', 'future', 'favor', 'nope',
           'beard', 'melon', 'potato', 'rainbow', 'taco']
# Uitsnede van het wombatkopje per tekening (in pixels van een tekening van 1536 x 1024)
GEZICHTEN = {
    'skip': (680, 30, 1080, 430), 'future': (640, 90, 1040, 490), 'beard': (620, 60, 1100, 540),
    'melon': (620, 40, 1080, 500), 'nope': (555, 115, 985, 545), 'taco': (640, 20, 1040, 420),
}


def kaarten():
    IMG.mkdir(exist_ok=True)
    for s in SOORTEN:
        im = Image.open(BRON / 'kaarten' / f'{s}.jpg').convert('RGB')
        im.resize((720, 480), Image.LANCZOS).save(IMG / f'{s}.webp', quality=80, method=6)
        if s in GEZICHTEN:
            sx, sy = im.width / 1536, im.height / 1024
            x0, y0, x1, y1 = GEZICHTEN[s]
            face = im.crop((int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy)))
            face.resize((192, 192), Image.LANCZOS).save(IMG / f'face-{s}.webp', quality=84, method=6)
    shutil.copy(BRON / 'achterkant.svg', IMG / 'back.svg')
    shutil.copy(BRON / 'ster.svg', IMG / 'star.svg')


def wombats():
    """De twee losse wombats: achtergrond weg en getallen afronden, zodat het bestand een stuk kleiner wordt."""
    for bron, doel in (('wombat-blij.svg', 'blij.svg'), ('wombat-sip.svg', 'sip.svg')):
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
        (IMG / doel).write_text(s, encoding='utf-8')


def iconen():
    im = Image.open(BRON / 'icoon.png').convert('RGB')
    w, h = im.size
    # het kopje vult zo het grootste deel van het icoon
    m = round(min(w, h) * 0.13)
    sq = im.crop((m, round(m * 0.6), w - m, round(m * 0.6) + (w - 2 * m)))
    sq.resize((512, 512), Image.LANCZOS).save(ROOT / 'icon-512.png', optimize=True)
    sq.resize((192, 192), Image.LANCZOS).save(ROOT / 'icon-192.png', optimize=True)
    sq.resize((180, 180), Image.LANCZOS).save(ROOT / 'apple-touch-icon.png', optimize=True)
    sq.resize((32, 32), Image.LANCZOS).save(ROOT / 'favicon-32.png', optimize=True)
    sq.resize((48, 48), Image.LANCZOS).save(ROOT / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    # maskable: kopje kleiner op de achtergrondkleur, zodat Android het rond mag afsnijden
    bg = im.getpixel((8, 8))
    mk = Image.new('RGB', (512, 512), bg)
    mk.paste(sq.resize((400, 400), Image.LANCZOS), (56, 56))
    mk.save(ROOT / 'icon-maskable-512.png', optimize=True)


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
    for k in ('img/back.svg', 'img/star.svg'):
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
