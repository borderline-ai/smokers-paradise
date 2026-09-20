import asyncio, json
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1400)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelectorAll('.on').forEach(e=>{if(e.id==='inter')e.classList.remove('on')})")
        await pg.evaluate("go('home')"); await pg.wait_for_timeout(1200)
        r=await pg.evaluate("""()=>{
          const el=document.getElementById('catRail');
          const main=document.querySelector('#main');
          return {exists: !!el,
                  offsetTop: el?el.offsetTop:null,
                  offsetParent: el&&el.offsetParent?(el.offsetParent.id||el.offsetParent.className).slice(0,30):null,
                  rectTop: el?Math.round(el.getBoundingClientRect().top):null,
                  mainScroll: main.scrollTop, mainH: main.scrollHeight,
                  target: el?Math.max(0, el.offsetTop-150):null } }""")
        print(json.dumps(r, indent=1))
        await pg.evaluate("const b=document.querySelector('[data-scrollto]'); if(b)b.click()")
        await pg.wait_for_timeout(1400)
        r2=await pg.evaluate("""()=>({ after: document.querySelector('#main').scrollTop,
            railTop: Math.round((document.getElementById('catRail')||{getBoundingClientRect:()=>({top:0})}).getBoundingClientRect().top) })""")
        print('after click ->', json.dumps(r2))
        await br.close()
asyncio.run(m())
