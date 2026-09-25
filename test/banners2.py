import asyncio, os
from playwright.async_api import async_playwright
os.makedirs('/tmp/spban2',exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + __import__('sppath').APP); await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1500)
        await pg.evaluate("clearInterval(heroT)")   # stop the auto advance so a shot is the slide asked for
        n=await pg.evaluate("PROMOS.length")
        for i in range(n):
            await pg.evaluate("(i)=>{heroTo(i); clearInterval(heroT)}", i)
            await pg.wait_for_timeout(1400)
            cur=await pg.evaluate("PROMOS[HERO].id")
            await pg.locator('#hero').screenshot(path='/tmp/spban2/%d-%s.png'%(i,cur))
            print(i, cur)
        await br.close()
asyncio.run(m())
