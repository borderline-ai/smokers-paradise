import asyncio, json, re
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter()")
        seen={}
        for setup in ["go('home')","go('deals')","go('store')","go('all')","go('cat','disp')",
                      "go('orders')","go('account')"]:
            await pg.evaluate(setup); await pg.wait_for_timeout(1100)
            r=await pg.evaluate("""()=>{
              const out=[]; const skip=new Set(['SCRIPT','STYLE','svg','path','circle','rect']);
              const w=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
              let n; while(n=w.nextNode()){
                const p=n.parentElement; if(!p) continue;
                if(skip.has(p.tagName)) continue;
                if(p.closest('.card, .spot, #catGrid, .rail, .feedrow')) continue;
                const t=n.nodeValue.replace(/\\s+/g,' ').trim();
                if(t.length>1 && t.length<170 && /[A-Za-z]/.test(t)) out.push(t);
              } return out }""")
            for t in r: seen[t]=seen.get(t,0)+1
        keys=sorted(seen.keys())
        json.dump(keys, open('/tmp/strings.json','w'), indent=1)
        print(len(keys),'unique strings')
        await br.close()
asyncio.run(m())
