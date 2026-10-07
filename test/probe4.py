import asyncio, json
from playwright.async_api import async_playwright
B=__import__('sppath').APP
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1000)
        r=await pg.evaluate("""async ()=>{
          const out={};
          const vp=document.querySelector('#heroVp');
          const t0=vp?vp.style.transform:'';
          const d=document.querySelector('[data-herogo="2"]'); if(d) d.click();
          await new Promise(r=>setTimeout(r,700));
          out.heroDot={before:t0, after:vp?vp.style.transform:'', moved: vp && vp.style.transform!==t0};
          const rail=document.querySelector('[data-scr="rl0|1"]');
          if(rail){
            const id=rail.dataset.scr.split('|')[0];
            const el=document.getElementById(id)||document.querySelector('.rail');
            const s0=el?el.scrollLeft:null;
            rail.click(); await new Promise(r=>setTimeout(r,800));
            out.railArrow={id, before:s0, after: el?el.scrollLeft:null, moved: el && el.scrollLeft!==s0};
          }
          return out }""")
        print(json.dumps(r, indent=1))
        await br.close()
asyncio.run(m())
