import asyncio, json
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file:///root/work/smokers-paradise-demo/build/index.html'); await pg.wait_for_timeout(1700)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter(); go('home'); heroTo(2); clearInterval(heroT)"); await pg.wait_for_timeout(1400)
        r=await pg.evaluate("""()=>{
          const im=document.querySelectorAll('#heroVp .slide')[2].querySelector('.camp-lead');
          const cs=getComputedStyle(im);
          const shot=im.closest('.camp-shot'); const ss=getComputedStyle(shot);
          return {cls:im.className, pos:cs.position, right:cs.right, bottom:cs.bottom,
                  height:cs.height, maxH:cs.maxHeight, objf:cs.objectFit,
                  shotOverflow:ss.overflow, shotH:ss.height} }""")
        print(json.dumps(r, indent=1))
        await br.close()
asyncio.run(m())
