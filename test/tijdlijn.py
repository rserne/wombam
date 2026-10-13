# Volgt per kwart seconde wat er in beeld staat (groot effect, balk onderin, venster, melding),
# zodat te zien is of alles netjes na elkaar komt bij trekken, ontmantelen en terugleggen.
import asyncio, re, time
from playwright.async_api import async_playwright
FIX=re.search(r"FIX='''(.*?)'''",open('test/ui2.py').read(),re.S).group(1)

STATE='''()=>{
  const t=s=>{ const e=document.querySelector(s); return e&&!e.hidden?e.innerText.replace(/\\s+/g,' ').trim():''; };
  const sh=document.querySelector('#layer .sheet h2');
  return [t('#fx .boom'), t('#dock'), sh?sh.innerText:'', t('#toast')].join(' | ');
}'''

async def volg(pg,naam,ms,klik=None):
    print(f'\n== {naam}')
    t0=time.time(); prev=None; geklikt=False
    while (time.time()-t0)*1000<ms:
        s=await pg.evaluate(STATE)
        if s!=prev: print(f'{(time.time()-t0):5.2f}s  {s}'); prev=s
        if klik and not geklikt and await pg.locator(klik).count():
            await pg.wait_for_timeout(400); await pg.click(klik); geklikt=True; print(f'{(time.time()-t0):5.2f}s  [tik op {klik}]')
        await pg.wait_for_timeout(120)

async def setup(pg,*a):
    await pg.goto('http://localhost:8765/'); await pg.evaluate(FIX,list(a)); await pg.reload(); await pg.wait_for_timeout(300)
    if await pg.locator('[data-act=tour-close]').count(): await pg.click('[data-act=tour-close]')

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        # 1. Bolle trekt een Exploding Wombat en ontmantelt hem
        await setup(pg,2,[['taco','skip'],['defuse']],['ek','melon','potato','beard'],{'S':{'cur':1}})
        await volg(pg,'Bolle trekt een Exploding Wombat',10000)
        # 2. Jij trekt een Exploding Wombat en ontmantelt hem
        await setup(pg,2,[['taco','defuse'],['beard']],['ek','melon','potato','beard'],{'S':{'cur':0}})
        await pg.click('[data-act=draw]')
        await volg(pg,'Jij trekt een Exploding Wombat',9000,klik='#layer [data-act=place]')
        # 3. Jij trekt een gewone kaart
        await setup(pg,2,[['taco','defuse'],['beard']],['melon','potato','beard','ek'],{'S':{'cur':0}})
        await pg.click('[data-act=draw]')
        await volg(pg,'Jij trekt een gewone kaart',4500)
        # 4. Bolle ontploft
        await setup(pg,3,[['taco','defuse'],['beard'],['melon']],['ek','potato','beard','ek'],{'S':{'cur':1}})
        await volg(pg,'Bolle ontploft',7000)
        print('\nfouten',errs)
        await b.close()
asyncio.run(main())
