# Wombam!

Een kaartspel voor twee tot vijf spelers, met de regels van het basisspel van Exploding Kittens, maar dan met wombats. Trek kaarten, speel slim en ontwijk de Exploderende Wombats. Wie er een trekt zonder Ontmantel, ontploft. Wie als laatste overblijft, wint.

Lang niet gespeeld? Op het startscherm en onder het vraagteken staat een uitleg in tien stappen, met de kaarten erbij. Bij de eerste keer openen verschijnt die vanzelf.

Speel tegen de computer, met vrienden op één telefoon (je geeft hem tussen de beurten door) of online, waarbij iedereen op zijn eigen telefoon speelt.

De app is een PWA: je zet hem op het beginscherm van je telefoon, en na het eerste bezoek werkt hij ook offline.

## Inhoud

| Bestand | Functie |
| --- | --- |
| `index.html` | Het spel: opmaak, spelregels, computerspelers en online spelen in één bestand |
| `manifest.webmanifest` | Naam, kleuren en iconen voor het beginscherm |
| `sw.js` | Service worker, voor offline spelen en de melding bij een nieuwe versie |
| `img/` | Kaarttekeningen, spelersportretten, achterkant en ster |
| `icon-*.png`, `apple-touch-icon.png` | App-iconen |
| `favicon.ico`, `favicon-32.png` | Icoontje in browsertabbladen en favorieten |
| `bron/` | De originele tekeningen en het icoon, waaruit `build.py` alles maakt |
| `build.py` | Bouwscript: maakt de afbeeldingen en iconen en werkt `sw.js` bij |
| `animatie.py` | Laat de juichende en de sippe wombat op het uitslagscherm bewegen (gebruikt door `build.py`) |
| `firebase-regels.json` | De regels voor de Realtime Database |
| `test/` | Regeltests, gesimuleerde potjes en schermtests |

## Online spelen

Online spelen loopt via Firebase (project *wombam-d07f9*): anoniem inloggen en een Realtime Database in asia-southeast1 (Singapore). Een spel staat onder `wombam/rooms/CODE` als `{ d, rev, t }`: `d` is de spelstand als JSON-tekst, `rev` een volgnummer dat bij elke zet ophoogt en `t` de tijd. Elke zet is een transactie op de actuele stand, zodat ook spelers die niet aan de beurt zijn veilig Nope kunnen spelen of een kaart kunnen afgeven.

De verbindingsgegevens staan bovenin het tweede script van `index.html` (`FIREBASE_CONFIG`). Die zijn niet geheim.

Testen zonder Firebase kan met een nep-database: open het spel met `?mock` achter het adres in twee vensters van dezelfde browser.

## Een nieuwe versie maken

1. Vervang zo nodig tekeningen in `bron/kaarten/` of het icoon `bron/icoon.png`.
2. Draai `python3 build.py` (eenmalig vooraf: `pip install pillow`). Dat maakt de afbeeldingen en hoogt het versienummer in `sw.js` op.
3. Zet de bestanden op GitHub.

Wie de app open heeft, krijgt dan bovenin de melding *Er is een nieuwe versie van Wombam!* Een tik op **Vernieuwen** laadt de nieuwe versie meteen; een lopend spel blijft bewaard. De app zoekt naar updates bij het openen en elk half uur.

Met `python3 build.py --voorbeeld` maak je ook `voorbeeld.html`: het hele spel in één bestand, met alle afbeeldingen erin.

## Testen

```sh
node test/sim.js        # regeltests en 2000 gesimuleerde potjes
node test/strength.js   # hoe vaak de computerspeler wint van naïeve spelers
python3 -m http.server 8765 &
python3 test/ui2.py     # schermtests (Playwright); schermafbeeldingen in test/schermen/
python3 test/online.py  # een volledig online potje met twee vensters op de nep-database
```

## Lokaal spelen

Dubbelklikken op `index.html` werkt, maar dan doet de offlinefunctie niet mee. Start daarom in de map een kleine webserver:

```sh
python3 -m http.server 8000
```

Open daarna http://localhost:8000 in je browser.

## Op je telefoon zetten

- **iPhone (Safari):** open het adres, tik op de deelknop en kies *Zet op beginscherm*.
- **Android (Chrome):** open het adres, open het menu (drie puntjes) en kies *App installeren*.
