import asyncio, re
from playwright.async_api import async_playwright
FIX=re.search(r"FIX='''(.*?)'''",open('test/ui2.py').read(),re.S).group(1)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/')
        await pg.evaluate(FIX,[3,[['taco','skip','defuse','nope'],['attack','beard'],['melon','melon','skip']],['taco','beard','potato','ek','beard','ek','taco','melon'],{'S':{'cur':1}}])
        await pg.reload(); await pg.wait_for_timeout(300)
        await pg.evaluate('''()=>{ window.__imgs=0; window.__nodes=0; window.__renders=0;
          new MutationObserver(ms=>{ for(const m of ms) for(const n of m.addedNodes){ if(n.nodeType===1){ window.__nodes++; window.__imgs+=(n.tagName==='IMG'?1:0)+n.querySelectorAll('img').length; } } })
            .observe(document.body,{childList:true,subtree:true}); }''')
        await pg.wait_for_timeout(9000)
        r=await pg.evaluate('({nodes:window.__nodes,imgs:window.__imgs})')
        print('in 9 s toegevoegde elementen:',r['nodes'],'| opnieuw geplaatste afbeeldingen:',r['imgs'],'| fouten',errs)
        await b.close()
asyncio.run(main())
