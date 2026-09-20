import asyncio, json
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter(); setLang('es')"); await pg.wait_for_timeout(1400)
        gaps={}
        for setup in ["go('home')","go('deals')","go('store')","go('all')","go('cat','disp')","go('orders')","go('account')"]:
            await pg.evaluate(setup); await pg.wait_for_timeout(1100)
            r=await pg.evaluate("""()=>{
              const out=[]; const w=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
              let n; while(n=w.nextNode()){
                const p=n.parentElement; if(!p||p.tagName==='SCRIPT'||p.tagName==='STYLE') continue;
                if(p.closest('.card, .spot, #catGrid, .rail, .feedrow, .pdp')) continue;
                const t=n.nodeValue.replace(/\\s+/g,' ').trim();
                if(t.length<3 || t.length>150) continue;
                if(T_ES[t]) continue;
                // english-looking: has an english stopword and no spanish accent
                if(/\\b(the|and|your|with|for|from|our|you|we|it|is|are|at|in|on|of|to|by|when|what|how)\\b/i.test(t))
                  out.push(t);
              } return out }""")
            for t in r: gaps[t]=1
        g=sorted(gaps)
        json.dump(g, open('/tmp/gaps.json','w'), ensure_ascii=False, indent=1)
        print(len(g),'untranslated strings still showing in Spanish mode')
        for x in g: print(' |', x)
        await br.close()
asyncio.run(m())
