import asyncio, sys
from playwright.async_api import async_playwright
URL='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True,color_scheme=sys.argv[1] if len(sys.argv)>1 else 'light')
        pg=await ctx.new_page()
        errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(800); await pg.click('[data-act=tour-close]')
        await pg.screenshot(path='test/schermen/01-start.png')
        await pg.click('[data-act=start]'); await pg.wait_for_timeout(900)
        await pg.screenshot(path='test/schermen/02-spel.png')
        await pg.click('.hc >> nth=2'); await pg.wait_for_timeout(400)
        await pg.screenshot(path='test/schermen/03-kaart.png')
        await pg.click('[data-act=close]'); await pg.wait_for_timeout(200)
        # trek een kaart en kijk hoe de computer speelt
        await pg.click('.dock [data-act=draw]'); await pg.wait_for_timeout(500)
        await pg.screenshot(path='test/schermen/04-getrokken.png')
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path='test/schermen/05-computer.png')
        print('fouten:',errs)
        await b.close()
asyncio.run(main())
