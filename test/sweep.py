import asyncio, os, sys
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
OUT='/tmp/sp6b'
os.makedirs(OUT, exist_ok=True)

async def strip(pg, name, scroller='#main', step=740, cap=40):
    H = await pg.evaluate("s=>document.querySelector(s).scrollHeight", scroller)
    n=0; y=0
    while y < H and n < cap:
        await pg.evaluate("([s,y])=>{document.querySelector(s).scrollTop=y}", [scroller,y])
        await pg.wait_for_timeout(420)
        await pg.screenshot(path='%s/%s_%02d.png'%(OUT,name,n))
        n+=1; y+=step
    await pg.evaluate("s=>{document.querySelector(s).scrollTop=0}", scroller)
    return n,H

async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch()
        pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+B); await pg.wait_for_timeout(2200)
        await pg.screenshot(path=OUT+'/00gate.png')
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.screenshot(path=OUT+'/01inter.png')
        await pg.evaluate("hideInter()"); await pg.wait_for_timeout(600)
        for v,setup in [('home',"go('home')"),('deals',"go('deals')"),('store',"go('store')"),
                        ('all',"go('all')"),('account',"go('account')"),('orders',"go('orders')")]:
            await pg.evaluate(setup); await pg.wait_for_timeout(1400)
            n,H = await strip(pg, v)
            print('%-8s %2d shots  %5dpx' % (v,n,H))
        print('errors:', errs[:6])
        await br.close()
asyncio.run(m())
