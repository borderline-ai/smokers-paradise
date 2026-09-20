import asyncio, json
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter()")
        chips=await pg.evaluate("STORE_CONTENT.highlights")
        print(json.dumps(chips))
        for c in chips:
            n=await pg.evaluate("""async (q)=>{
                const i=document.querySelector('#q');
                i.focus(); i.value=q; i.dispatchEvent(new Event('input',{bubbles:true}));
                await new Promise(r=>setTimeout(r,420));
                const h=document.querySelector('#v-search h2');
                return h?h.textContent.trim():'?' }""", c)
            print('  %-22s -> %s' % (c, n))
        await br.close()
asyncio.run(m())
