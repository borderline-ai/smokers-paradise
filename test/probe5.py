import asyncio, json
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1200)
        r=await pg.evaluate("""()=>{
          const out=[];
          document.querySelectorAll('[data-scr]').forEach(b=>{
            const [id,dir]=b.dataset.scr.split('|');
            const el=document.getElementById(id);
            out.push({scr:b.dataset.scr, found: !!el,
                      clientW: el?el.clientWidth:null,
                      scrollW: el?el.scrollWidth:null,
                      overflows: el? el.scrollWidth>el.clientWidth+4 : null,
                      overflowX: el? getComputedStyle(el).overflowX : null});
          });
          return out }""")
        print(json.dumps(r, indent=1))
        await br.close()
asyncio.run(m())
