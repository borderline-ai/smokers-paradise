import asyncio, os, sys
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/sp5/smoke'
os.makedirs(OUT, exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+B); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=OUT+'/0-gate.png')
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1600)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(4000)
        await pg.screenshot(path=OUT+'/1-hero.png')
        for i,y in enumerate([900, 2000, 3400, 5200, 7400, 8600, 9700, 10400]):
            await pg.evaluate("y=>{document.querySelector('#main').scrollTop=y}", y)
            await pg.wait_for_timeout(2600)
            await pg.screenshot(path=OUT+'/2-y%05d.png'%y)
        print('parts phone', await pg.evaluate("window.__skySmoke? window.__skySmoke.ps.length : -1"),
              'hero', await pg.evaluate("window.__heroSmoke? window.__heroSmoke.ps.length : -1"))
        print('errs', errs[:3])
        await br.close()
asyncio.run(m())
