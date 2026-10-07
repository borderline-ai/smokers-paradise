import asyncio, json
from playwright.async_api import async_playwright
B=__import__('sppath').APP
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1200)
        print('btn:', await pg.evaluate("(document.querySelector('#langBtn')||{}).textContent"))
        await pg.screenshot(path='/tmp/spfix/L-en.png')
        await pg.evaluate("document.querySelector('#langBtn').click()"); await pg.wait_for_timeout(1600)
        await pg.screenshot(path='/tmp/spfix/L-es.png')
        r=await pg.evaluate("""()=>({btn:(document.querySelector('#langBtn')||{}).textContent,
            lang:LANG, htmlLang:document.documentElement.lang,
            tabs:[...document.querySelectorAll('.tabbar b, .tab b, nav b, .tabbar span')].map(e=>e.textContent.trim()).slice(0,8),
            body: document.querySelector('#v-home').textContent.replace(/\\s+/g,' ').slice(0,300)})""")
        print(json.dumps(r, ensure_ascii=False, indent=1))
        await pg.evaluate("go('store')"); await pg.wait_for_timeout(1400)
        await pg.screenshot(path='/tmp/spfix/L-es-store.png')
        await pg.evaluate("document.querySelector('#langBtn').click()"); await pg.wait_for_timeout(1500)
        back=await pg.evaluate("document.querySelector('#v-store').textContent.replace(/\\s+/g,' ').slice(0,220)")
        print('back to EN:', back)
        print('errors', errs[:3])
        await br.close()
asyncio.run(m())
