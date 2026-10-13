import asyncio, re
from playwright.async_api import async_playwright
FIX=re.search(r"FIX='''(.*?)'''",open('test/ui2.py').read(),re.S).group(1)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for scheme in ['light','dark']:
            ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True,color_scheme=scheme)
            pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:8765/')
            # Bolle (computer) speelt Aanval; ik heb een Nope
            await pg.evaluate(FIX,[3,[['taco','nope','defuse'],['attack','attack'],['melon','melon']],['taco','beard','potato','ek','beard','ek'],{'S':{'cur':1}}])
            await pg.reload()
            pre='d-' if scheme=='dark' else ''
            await pg.wait_for_timeout(700); await pg.screenshot(path=f'test/schermen/{pre}80-denkt-na.png')
            await pg.wait_for_timeout(1400); await pg.screenshot(path=f'test/schermen/{pre}81-aanval-nope.png')
            await pg.wait_for_timeout(5500); await pg.screenshot(path=f'test/schermen/{pre}82-snuffel.png')
            await pg.wait_for_timeout(4000); await pg.screenshot(path=f'test/schermen/{pre}83-later.png')
            print(scheme,'fouten',errs)
        await b.close()
asyncio.run(main())
