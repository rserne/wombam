import asyncio, re
from playwright.async_api import async_playwright
FIX=re.search(r"FIX='''(.*?)'''",open('test/ui2.py').read(),re.S).group(1)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True,color_scheme='dark')
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/')
        await pg.evaluate(FIX,[2,[['taco','skip','defuse'],['beard']],['melon','potato','taco','ek'],{'S':{'cur':1}}])
        await pg.reload()
        seq=[]
        for t,name in [(900,'90-bolle-denkt'),(2300,'91-bolle-trekt'),(3300,'92-nog-bolle'),(5000,'93-jouw-knop')]:
            await pg.wait_for_timeout(t-(seq[-1] if seq else 0)); seq.append(t)
            await pg.screenshot(path=f'test/schermen/{name}.png')
            print(name,'| kaartje:',await pg.locator('.dock .ev').count(),'| trekknop:',await pg.locator('.dock [data-act=draw]').count())
        print('fouten',errs)
        await b.close()
asyncio.run(main())
