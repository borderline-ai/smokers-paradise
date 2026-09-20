import asyncio, os
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
os.makedirs('/tmp/spban',exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1500)
        n=await pg.evaluate("PROMOS.length")
        for i in range(n):
            await pg.evaluate("(i)=>{heroTo(i)}", i)
            await pg.wait_for_timeout(1100)
            el=pg.locator('#hero')
            await el.screenshot(path='/tmp/spban/promo-%d.png'%i)
        await pg.evaluate("go('deals')"); await pg.wait_for_timeout(1800)
        await pg.evaluate("""async ()=>{ const m=document.querySelector('#main');
          for(let y=0;y<m.scrollHeight;y+=400){m.scrollTop=y; await new Promise(r=>setTimeout(r,160))}
          m.scrollTop=0; document.querySelectorAll('img[loading="lazy"]').forEach(i=>i.loading='eager');
          await new Promise(r=>setTimeout(r,600)) }""")
        await pg.wait_for_timeout(2500)
        ads=await pg.evaluate("document.querySelectorAll('#v-deals .ad').length")
        for i in range(ads):
            el=pg.locator('#v-deals .ad').nth(i)
            try:
                await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(600)
                await el.screenshot(path='/tmp/spban/ad-%d.png'%i)
            except Exception as e: print('ad',i,'skip',str(e)[:60])
        print('promos', n, 'ads', ads)
        await br.close()
asyncio.run(m())
