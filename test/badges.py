import asyncio, re
from playwright.async_api import async_playwright
FIX=re.search(r"FIX='''(.*?)'''",open('test/ui2.py').read(),re.S).group(1)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/')
        await pg.evaluate(FIX,[3,[['favor','favor','taco','taco','taco','defuse','nope','attack'],['beard'],['melon']],['potato','ek','melon','ek'],{}])
        await pg.reload(); await pg.wait_for_timeout(900)
        print('hc:',await pg.locator('.hc').count(),'fouten',errs)
        await pg.screenshot(path='test/schermen/73-hand-badges.png')
        await pg.locator('.hc').nth(1).evaluate('e=>e.click()'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='test/schermen/74-kaart-badge.png')
        await b.close()
asyncio.run(main())
