import asyncio, sys, json
from playwright.async_api import async_playwright
URL='http://localhost:8765/'
FIX='''
(args)=>{
  const [n,hands,deck,ex]=args; const extra=ex||{};
  const E=Engine;
  const S=E.newGame(Array.from({length:n},(_,i)=>({name:['Rob','Bolle','Snuffel','Graafje','Pluis'][i],ai:i>0&&!(extra.humans||[]).includes(i),c:i})));
  const pool=[...S.deck,...S.discard,...S.box]; S.players.forEach(p=>pool.push(...p.hand));
  const take=t=>{ const c=pool.find(x=>E.typeOf(x)===t); pool.splice(pool.indexOf(c),1); return c; };
  S.players.forEach((p,i)=>{ p.hand=E.sortHand((hands[i]||[]).map(take)); });
  S.deck=deck.map(take); S.discard=(extra.discard||[]).map(take); S.box=pool; S.seq=1;
  Object.assign(S,extra.S||{});
  if(extra.limbo) S.limbo=take('ek');
  localStorage.setItem('wombam-v1',JSON.stringify({S,seats:[{name:'Rob',type:'mens'},{name:'Bolle',type:'computer'},{name:'Snuffel',type:'computer'},{name:'Graafje',type:'uit'},{name:'Pluis',type:'uit'}],pref:{fast:false,sound:false},viewer:extra.viewer===undefined?0:extra.viewer}));
}
'''
async def setup(pg,*a):
    await pg.goto(URL); await pg.evaluate(FIX,list(a)); await pg.reload(); await pg.wait_for_timeout(700)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        scheme=sys.argv[1] if len(sys.argv)>1 else 'light'
        ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True,color_scheme=scheme)
        pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e: errs.append(str(e)))
        pre='test/schermen/'+('d-' if scheme=='dark' else '')
        # 1. Bolle speelt Kateautje tegen jou -> jij geeft een kaart
        await setup(pg,3,[['taco','skip','defuse'],['favor','beard'],['melon']],['taco','beard','ek','melon','ek'],{'S':{'cur':1}})
        await pg.wait_for_timeout(1600); await pg.screenshot(path=pre+'10-reactie.png')
        await pg.wait_for_timeout(4600); await pg.screenshot(path=pre+'11-geven.png')
        await pg.click('.hc >> nth=0'); await pg.wait_for_timeout(300); await pg.screenshot(path=pre+'12-geefkaart.png')
        await pg.click('[data-act=give]'); await pg.wait_for_timeout(500)
        # 2. Voorspel de toekomst
        await setup(pg,2,[['future','defuse'],['taco']],['melon','ek','taco','beard'])
        await pg.click('.hc >> nth=1'); await pg.wait_for_timeout(250); await pg.click('[data-act=play-one]')
        await pg.wait_for_timeout(1800); await pg.screenshot(path=pre+'13-toekomst.png')
        # 3. Ontmantelen en terugleggen
        await setup(pg,3,[['defuse','taco'],['taco'],['melon']],['ek','taco','beard','melon','taco','ek'])
        await pg.click('.dock [data-act=draw]'); await pg.wait_for_timeout(700); await pg.screenshot(path=pre+'14-pfoe.png')
        await pg.wait_for_timeout(1500); await pg.screenshot(path=pre+'15-terugleggen.png')
        await pg.click('[data-act=pos][data-p="2"]'); await pg.click('[data-act=place]'); await pg.wait_for_timeout(400)
        # 4. Nope van de computer tegen jouw Aanval
        await setup(pg,2,[['attack','taco'],['nope','nope']],['taco','ek','melon'])
        await pg.click('.hc >> nth=0'); await pg.wait_for_timeout(250); await pg.click('[data-act=play-one]')
        await pg.wait_for_timeout(1500); await pg.screenshot(path=pre+'16-nope.png')
        # 5. Paar spelen: kies een tegenstander, drietal: noem een kaart
        await setup(pg,3,[['taco','taco','taco','skip'],['beard','nope'],['melon','defuse']],['taco','ek','melon','ek'])
        await pg.click('.hc >> nth=1'); await pg.wait_for_timeout(250); await pg.screenshot(path=pre+'17-tacokaart.png')
        await pg.click('[data-mode=triple]'); await pg.wait_for_timeout(250); await pg.screenshot(path=pre+'18-kies-speler.png')
        await pg.click('.sheet [data-act=target] >> nth=1'); await pg.wait_for_timeout(250); await pg.screenshot(path=pre+'19-noem-kaart.png')
        await pg.click('[data-act=named][data-t=defuse]'); await pg.wait_for_timeout(5500); await pg.screenshot(path=pre+'20-opgeeist.png')
        # 6. Ontploffen
        await setup(pg,3,[['taco'],['taco'],['melon']],['ek','taco','ek'])
        await pg.click('.dock [data-act=draw]'); await pg.wait_for_timeout(600); await pg.screenshot(path=pre+'21-boem.png')
        await pg.wait_for_timeout(2400); await pg.screenshot(path=pre+'22-uitgeschakeld.png')
        # 7. Doorgeven op één telefoon
        await setup(pg,3,[['taco','skip'],['beard','attack'],['melon']],['taco','ek','melon','ek'],{'humans':[1],'viewer':0})
        await pg.click('.dock [data-act=draw]'); await pg.wait_for_timeout(700); await pg.screenshot(path=pre+'23-doorgeven.png')
        # 8. Uitslag
        await setup(pg,2,[['taco'],['taco']],['ek','taco'],{'S':{'cur':1}})
        await pg.wait_for_timeout(1800); await pg.wait_for_timeout(2800); await pg.screenshot(path=pre+'24-uitslag.png')
        print('fouten:',errs)
        await b.close()
asyncio.run(main())
