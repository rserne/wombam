import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/'); await pg.wait_for_timeout(700)
        for i in range(10):
            await pg.screenshot(path=f'test/schermen/60-uitleg-{i+1:02d}.png')
            if i<9: await pg.click('[data-act=tour-next]'); await pg.wait_for_timeout(450)
        await pg.click('[data-act=rules-all]'); await pg.wait_for_timeout(300); await pg.screenshot(path='test/schermen/61-alle-regels.png')
        await pg.click('.sheet [data-act=close]'); await pg.wait_for_timeout(300); await pg.screenshot(path='test/schermen/62-start-met-knop.png')
        await pg.reload(); await pg.wait_for_timeout(600)
        print('na herladen nog open:', await pg.locator('.tour').count(), '| fouten', errs)
        await b.close()
asyncio.run(main())
