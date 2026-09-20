import asyncio, os
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
OUT='/tmp/sp9'; os.makedirs(OUT, exist_ok=True)
async def shots(pg, name, sel='#main', step=740, cap=8):
    H=await pg.evaluate("s=>{const e=document.querySelector(s); return e?e.scrollHeight:0}", sel)
    n=0;y=0
    while y<max(H,1) and n<cap:
        await pg.evaluate("([s,y])=>{const e=document.querySelector(s); if(e)e.scrollTop=y}", [sel,y])
        await pg.wait_for_timeout(400)
        await pg.screenshot(path='%s/%s_%02d.png'%(OUT,name,n)); n+=1; y+=step
    return n
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+B); await pg.wait_for_timeout(1800)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1600)
        await pg.evaluate("hideInter()")
        # a product page with options, one glass piece, one puffco
        for pid,label in [('rx063','pdp_offstamp'),('rx096','pdp_grav'),('rx002','pdp_peak'),('rx140','pdp_lookah')]:
            await pg.evaluate("(id)=>openPDP(id)", pid); await pg.wait_for_timeout(1500)
            n=await shots(pg,label,'.sheet',700,6); print(label,n)
            await pg.evaluate("()=>{const b=document.querySelector('[data-close]'); if(b)b.click()}")
            await pg.wait_for_timeout(700)
        # the menu
        await pg.evaluate("()=>{const b=document.querySelector('[data-menu],#menuBtn,.burger'); if(b)b.click()}")
        await pg.wait_for_timeout(900); await pg.screenshot(path=OUT+'/menu.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(600)
        # search
        await pg.evaluate("()=>{const b=document.querySelector('[data-search],#searchBtn'); if(b)b.click()}")
        await pg.wait_for_timeout(900); await pg.screenshot(path=OUT+'/search.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(600)
        # the fit tool
        await pg.evaluate("()=>{const b=document.querySelector('[data-ffopen]'); if(b)b.click()}")
        await pg.wait_for_timeout(1200); await pg.screenshot(path=OUT+'/fit.png')
        print('errors:',errs[:5])
        await br.close()
asyncio.run(m())
