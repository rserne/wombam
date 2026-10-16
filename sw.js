// Wombam! service worker. Verhoog CACHE bij elke nieuwe versie (build.py doet dat vanzelf).
const CACHE='wombam-v32';
const EXT='wombam-extern';   // lettertypen en Firebase-software: blijven bewaard bij een nieuwe versie
const ASSETS=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png','icon-maskable-512.png','apple-touch-icon.png','favicon.ico','favicon-32.png','img/attack-kaart.webp','img/attack.webp','img/back.webp','img/beard-kaart.webp','img/beard.webp','img/blij.svg','img/defuse-kaart.webp','img/defuse.webp','img/ek-kaart.webp','img/ek.webp','img/face-beard.webp','img/face-future.webp','img/face-melon.webp','img/face-nope.webp','img/face-skip.webp','img/face-taco.webp','img/favor-kaart.webp','img/favor.webp','img/future-kaart.webp','img/future.webp','img/melon-kaart.webp','img/melon.webp','img/nope-kaart.webp','img/nope.webp','img/potato-kaart.webp','img/potato.webp','img/rainbow-kaart.webp','img/rainbow.webp','img/shuffle-kaart.webp','img/shuffle.webp','img/sip.svg','img/skip-kaart.webp','img/skip.webp','img/star.svg','img/taco-kaart.webp','img/taco.webp'];

// Nieuwe versie downloaden, maar wachten tot de speler op 'Vernieuwen' tikt.
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS.map(u=>new Request(u,{cache:'reload'})))));
});
self.addEventListener('message',e=>{ if(e.data&&e.data.type==='SKIP_WAITING') self.skipWaiting(); });
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE&&k!==EXT).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});

self.addEventListener('fetch',e=>{
  const req=e.request; if(req.method!=='GET') return;
  const url=new URL(req.url);
  const font=url.host==='fonts.googleapis.com'||url.host==='fonts.gstatic.com';
  const sdk=url.host==='www.gstatic.com'&&url.pathname.startsWith('/firebasejs/');
  if(font||sdk){
    // lettertypen en de Firebase-software: uit de cache, op de achtergrond bijwerken
    e.respondWith(caches.open(EXT).then(c=>c.match(req).then(hit=>{
      const net=fetch(req).then(res=>{ if(res&&(res.ok||res.type==='opaque')) c.put(req,res.clone()); return res; }).catch(()=>hit);
      return hit||net;
    })));
    return;
  }
  if(url.origin!==location.origin) return;
  // eigen bestanden: altijd uit de cache van deze versie
  e.respondWith(caches.open(CACHE).then(c=>
    (req.mode==='navigate'?c.match('index.html'):c.match(req,{ignoreSearch:true}))
      .then(hit=>hit||fetch(req))
  ));
});
