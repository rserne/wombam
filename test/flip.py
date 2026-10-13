import asyncio, re
from playwright.async_api import async_playwright
FIX=re.search(r"FIX='''(.*?)'''",open('test/ui2.py').read(),re.S).group(1)
SWIPE='''(dx)=>{
  const el=document.querySelector('.sheet[data-flip]'); const r=el.getBoundingClientRect();
  const x=r.left+r.width/2, y=r.top+150;
  const mk=(type,cx)=>{ const t=new Touch({identifier:1,target:el,clientX:cx,clientY:y}); return new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true}); };
  el.dispatchEvent(mk('touchstart',x)); el.dispatchEvent(mk('touchend',x+dx));
}'''
async def title(pg): return await pg.locator('.sheet .card .ban span').inner_text()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/')
        await pg.evaluate(FIX,[3,[['defuse','attack','skip','taco','taco','nope'],['taco'],['melon']],['taco','ek','melon','ek'],{}])
        await pg.reload(); await pg.wait_for_timeout(700)
        await pg.locator('.hc').nth(1).evaluate('e=>e.click()'); await pg.wait_for_timeout(300)
        seq=[await title(pg)]
        await pg.evaluate(SWIPE,-120); await pg.wait_for_timeout(350); seq.append(await title(pg))
        await pg.evaluate(SWIPE,-120); await pg.wait_for_timeout(350); seq.append(await title(pg))
        await pg.screenshot(path='test/schermen/70-bladeren.png')
        await pg.evaluate(SWIPE,120); await pg.wait_for_timeout(350); seq.append(await title(pg))
        await pg.click('[data-act=flip][data-d="1"]'); await pg.wait_for_timeout(350); seq.append(await title(pg))
        await pg.click('[data-act=flip][data-d="1"]'); await pg.wait_for_timeout(350); seq.append(await title(pg))
        print('volgorde:',seq,'| nog open:',await pg.locator('.sheet[data-flip]').count(),'| volgende uit bij laatste:',await pg.locator('[data-act=flip][data-d="1"][disabled]').count(),'| fouten',errs)
        await b.close()
asyncio.run(main())
