import asyncio, os
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
os.makedirs('/tmp/spfin',exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1300)
        await pg.screenshot(path='/tmp/spfin/1-home.png')
        await pg.evaluate("document.querySelector('[data-focussearch]').click()"); await pg.wait_for_timeout(900)
        await pg.screenshot(path='/tmp/spfin/2-search-open.png')
        await pg.evaluate("closeSearchRow(); go('store'); "); await pg.wait_for_timeout(1400)
        await pg.evaluate("()=>{const e=document.querySelector('.hlrow'); if(e) e.scrollIntoView({block:'center'})}")
        await pg.wait_for_timeout(1100); await pg.screenshot(path='/tmp/spfin/3-pills.png')
        await pg.evaluate("go('home')"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{const e=document.querySelector('.give'); if(e) e.scrollIntoView({block:'start'})}")
        await pg.wait_for_timeout(1100); await pg.screenshot(path='/tmp/spfin/4-events.png')
        await pg.evaluate("()=>{const e=document.querySelector('.gr-acts'); if(e) e.scrollIntoView({block:'center'})}")
        await pg.wait_for_timeout(1100); await pg.screenshot(path='/tmp/spfin/5-reviews.png')
        await pg.evaluate("setLang('es'); go('store')"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='/tmp/spfin/6-store-es.png')
        await br.close()
asyncio.run(m())
