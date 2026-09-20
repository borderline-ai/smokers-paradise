import asyncio, os
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
os.makedirs('/tmp/spfix',exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.screenshot(path='/tmp/spfix/A-entrance.png')
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{const d=document.querySelector('.ad'); if(d) d.scrollIntoView({block:'center'})}")
        await pg.wait_for_timeout(1100); await pg.screenshot(path='/tmp/spfix/B-home-ad.png')
        await pg.evaluate("go('deals')"); await pg.wait_for_timeout(1300)
        await pg.screenshot(path='/tmp/spfix/C-deals.png')
        await br.close()
asyncio.run(m())
