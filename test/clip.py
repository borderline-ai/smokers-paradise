import asyncio, json
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + __import__('sppath').APP); await pg.wait_for_timeout(1700)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1400)
        for i in range(4):
            r=await pg.evaluate("""async (i)=>{
              heroTo(i); clearInterval(heroT); await new Promise(r=>setTimeout(r,900));
              const slide=document.querySelectorAll('#heroVp .slide')[i];
              const camp=slide.querySelector('.camp'); if(!camp) return {i, none:true};
              const cb=camp.getBoundingClientRect();
              const out=[];
              slide.querySelectorAll('.camp-shot img').forEach(im=>{
                const b=im.getBoundingClientRect();
                out.push({cls:im.className||'-',
                  overRight: Math.round(b.right-cb.right), overBottom: Math.round(b.bottom-cb.bottom),
                  overLeft: Math.round(cb.left-b.left), overTop: Math.round(cb.top-b.top)});
              });
              return {i, id:PROMOS[i].id, imgs:out, overflow:getComputedStyle(camp).overflow} }""", i)
            print(json.dumps(r))
        await br.close()
asyncio.run(m())
