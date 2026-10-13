import asyncio, time, json
from playwright.async_api import async_playwright
URL='http://localhost:8765/?mock'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        A=await ctx.new_page(); B=await ctx.new_page(); errs=[]
        for pg in (A,B): pg.on('pageerror',lambda e: errs.append(str(e)))
        await A.goto(URL); await A.wait_for_timeout(400); await A.click('[data-act=tour-close]'); await A.click('[data-act=mode][data-m=online]'); await A.fill('#on-name','Rob'); await A.click('[data-act=create]')
        await A.wait_for_selector('.code-letters'); code=(await A.get_attribute('.code-letters','aria-label')).replace('Code ','').replace(' ','')
        await A.click('[data-act=add-ai]'); await A.wait_for_timeout(300)
        await B.goto(URL+'#'+code); await B.fill('#on-name','Sanne'); await B.click('[data-act=join]'); await B.wait_for_selector('.code-letters')
        await A.click('[data-act=start-online]'); await A.wait_for_timeout(800)
        # Rob trekt, dan is de computer aan de beurt; Rob sluit meteen de app
        await A.click('.dock [data-act=draw]'); await A.wait_for_timeout(300)
        rd=lambda: B.evaluate("JSON.parse(JSON.parse(localStorage.getItem('wb-mock:"+code+"')).d)")
        st=await rd(); print('na trekken: aan de beurt',st['S']['players'][st['S']['cur']]['name'],'fase',st['S']['phase'])
        await A.close(); t0=time.time()
        seq0=st['S']['seq']
        while time.time()-t0<25:
            await B.wait_for_timeout(1000); st=await rd()
            if st['S']['seq']>seq0+1: break
        S=st['S']; print(f'na {time.time()-t0:.0f}s: zetten {seq0} -> {S["seq"]}, aan de beurt {S["players"][S["cur"]]["name"]}, fase {S["phase"]}')
        print('laatste log:',[ (l['k'],l.get('a')) for l in S['log'][-4:]])
        print('fouten:',errs)
        await b.close()
asyncio.run(main())
