import asyncio, re
from playwright.async_api import async_playwright
FIX=re.search(r"FIX='''(.*?)'''",open('test/ui2.py').read(),re.S).group(1)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/')
        # Bolle (computer) is aan de beurt en heeft Aanval; Snuffel heeft een paar
        await pg.evaluate(FIX,[3,[['taco','skip','defuse'],['attack','attack'],['melon','melon']],['taco','beard','potato','ek','beard','ek'],{'S':{'cur':1}}])
        await pg.reload()
        shots=[(600,'80-denkt-na'),(1900,'81-spot-aanval'),(4200,'82-na-aanval')]
        t=0
        for at,name in shots:
            await pg.wait_for_timeout(at-t); t=at
            await pg.screenshot(path=f'test/schermen/{name}.png')
        print('fouten',errs)
        await b.close()
asyncio.run(main())
