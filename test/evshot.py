import asyncio, os
from playwright.async_api import async_playwright
B=__import__('sppath').APP
os.makedirs('/tmp/sp4',exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch()
        pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+B); await pg.wait_for_timeout(1400)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1500)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1400)
        # events section
        r=await pg.evaluate("""()=>{
          const o={};
          const now=document.querySelector('.ev-now'), rail=document.querySelector('.ev-rail');
          o.evnow = !!now; o.evrail = !!rail;
          o.cards = document.querySelectorAll('.ev-card').length;
          o.years = document.querySelectorAll('.ev-year').length;
          o.pics  = document.querySelectorAll('.ev-pic img').length;
          const sec = now? now.closest('section')||now.parentElement : null;
          if(sec){ const b=sec.getBoundingClientRect(); o.secH=Math.round(sec.scrollHeight); }
          o.pageH = Math.round(document.querySelector('#scr')?document.querySelector('#scr').scrollHeight:document.body.scrollHeight);
          return o; }""")
        print('events:', r)
        el = await pg.query_selector('.ev-now')
        if el:
            await pg.evaluate("()=>{const e=document.querySelector('.ev-lab')||document.querySelector('.ev-now'); e.scrollIntoView({block:'start'})}")
            await pg.wait_for_timeout(700)
            await pg.evaluate("()=>{const s=document.querySelector('#scr')||document.scrollingElement; s.scrollTop-=210}")
            await pg.wait_for_timeout(500)
            await pg.screenshot(path='/tmp/sp4/events1.png')
            await pg.evaluate("()=>{const s=document.querySelector('#scr')||document.scrollingElement; s.scrollTop+=760}")
            await pg.wait_for_timeout(500)
            await pg.screenshot(path='/tmp/sp4/events2.png')
        # the footer under reviews
        await pg.evaluate("()=>{const f=document.querySelector('.sitefoot'); if(f) f.scrollIntoView({block:'start'})}")
        await pg.wait_for_timeout(700); await pg.screenshot(path='/tmp/sp4/foot1.png')
        await pg.evaluate("()=>{const s=document.querySelector('#scr')||document.scrollingElement; s.scrollTop+=700}")
        await pg.wait_for_timeout(500); await pg.screenshot(path='/tmp/sp4/foot2.png')
        # the wheel banner
        w = await pg.query_selector('.ad-wheel')
        if w:
            await pg.evaluate("()=>{document.querySelector('.ad-wheel').closest('.ad').scrollIntoView({block:'center'})}")
            await pg.wait_for_timeout(700); await pg.screenshot(path='/tmp/sp4/wheel.png')
        print('errs:', errs[:4])
        await br.close()
asyncio.run(m())
