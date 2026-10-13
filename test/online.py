import asyncio, re, time
from playwright.async_api import async_playwright
URL='http://localhost:8765/?mock'
async def step(pg,tag,log):
    """Doe wat deze speler nu moet doen. Geeft True terug als er iets gedaan is."""
    if await pg.locator('.prow').count(): return 'over'
    if await pg.locator('[data-act=place]').count():
        await pg.click('[data-act=pos][data-p=rnd]'); await pg.click('[data-act=place]'); log.append(tag+' legt terug'); return True
    if await pg.locator('.sheet [data-act=close]').count() and await pg.locator('.three').count():
        await pg.click('.sheet [data-act=close]'); log.append(tag+' heeft in de toekomst gekeken'); return True
    if await pg.locator('.hand.giving').count():
        await pg.locator('.hand .hc').first.evaluate('e=>e.click()'); await pg.click('[data-act=give]'); log.append(tag+' geeft een kaart'); return True
    nope=pg.locator('.dock [data-act=nope]')
    if await nope.count() and time.time()%3<1:
        await nope.first.click(); log.append(tag+' zegt Nope'); return True
    d=pg.locator('.dock [data-act=draw]')
    if await d.count():
        # soms eerst een losse actiekaart spelen
        for t in ['Toekomst','Schud','Sla Over','Aanval']:
            c=pg.locator(f'.hc[aria-label^="{ {"Toekomst":"Voorspel","Schud":"Schud","Sla Over":"Sla Over","Aanval":"Aanval"}[t] }"]')
            if await c.count() and time.time()%4<1:
                await c.first.evaluate('e=>e.click()'); await pg.wait_for_timeout(150)
                b=pg.locator('[data-act=play-one]')
                if await b.count(): await b.click(); log.append(tag+' speelt '+t); return True
                await pg.click('.sheet [data-act=close]')
        await d.click(); log.append(tag+' trekt'); return True
    return False
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
        A=await ctx.new_page(); B=await ctx.new_page(); errs=[]
        for pg,t in ((A,'A'),(B,'B')): pg.on('pageerror',lambda e,t=t: errs.append(t+': '+str(e)))
        await A.goto(URL); await A.wait_for_timeout(400); await A.click('[data-act=tour-close]'); await A.wait_for_timeout(500)
        await A.click('[data-act=mode][data-m=online]'); await A.fill('#on-name','Rob'); await A.click('[data-act=create]')
        await A.wait_for_selector('.code-letters'); code=(await A.get_attribute('.code-letters','aria-label')).replace('Code ','').replace(' ','')
        await A.click('[data-act=add-ai]'); await A.wait_for_timeout(300)
        await B.goto(URL.replace('?mock','?mock#'+code)); await B.wait_for_timeout(500)
        await B.fill('#on-name','Sanne'); await B.screenshot(path='test/schermen/30-uitgenodigd.png')
        await B.click('[data-act=join]'); await B.wait_for_selector('.code-letters')
        await A.wait_for_timeout(400); await A.screenshot(path='test/schermen/31-wachtkamer.png'); await B.screenshot(path='test/schermen/32-wachtkamer-b.png')
        await A.click('[data-act=start-online]'); await A.wait_for_timeout(900)
        await A.screenshot(path='test/schermen/33-online-a.png'); await B.screenshot(path='test/schermen/34-online-b.png')
        print('titels:',await A.title(),'|',await B.title())
        # geheime informatie: B mag de kaarten van A niet zien
        ha=await A.locator('.hand .hc').evaluate_all('els=>els.map(e=>e.dataset.c)')
        hb_html=await B.locator('#app').inner_html()
        leak=[c for c in ha if f'data-c="{c}"' in hb_html]
        print('hand A:',len(ha),'kaarten; zichtbaar bij B:',leak)
        log=[]; t0=time.time(); shot=False
        while time.time()-t0<240:
            ra=await step(A,'A',log); rb=await step(B,'B',log)
            if ra=='over' and rb=='over': break
            if not shot and len(log)>8:
                await A.screenshot(path='test/schermen/35-online-midden-a.png'); await B.screenshot(path='test/schermen/36-online-midden-b.png'); shot=True
            await A.wait_for_timeout(250)
        await A.wait_for_timeout(600)
        await A.screenshot(path='test/schermen/37-online-uitslag-a.png'); await B.screenshot(path='test/schermen/38-online-uitslag-b.png')
        st=await A.evaluate("JSON.parse(JSON.parse(localStorage.getItem('wb-mock:"+code+"')).d)")
        S=st['S']; cards=S['deck']+S['discard']+S['box']+sum([p['hand'] for p in S['players']],[])+([S['limbo']] if S['limbo'] else [])
        print('afgelopen:',S['phase'],'winnaar:',S['players'][S['winner']]['name'] if S.get('winner') is not None else None,'| kaarten:',len(cards),len(set(cards)),'| zetten:',S['seq'],'| omvang d:',len(JSON:=__import__('json').dumps(st)))
        print('handelingen:',len(log),log[:14])
        print('fouten:',errs)
        await b.close()
asyncio.run(main())
