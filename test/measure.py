import asyncio, json
from playwright.async_api import async_playwright
B=__import__('sppath').APP
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        r=await pg.evaluate("""()=>{
          const card=document.querySelector('#interCard .ad');
          const art=document.querySelector('#interCard .ad-art');
          const out={card:null, art:null, imgs:[]};
          const R=e=>{const b=e.getBoundingClientRect(); return {t:Math.round(b.top),b:Math.round(b.bottom),l:Math.round(b.left),r:Math.round(b.right)}};
          if(card) out.card=R(card);
          if(art) out.art=R(art);
          document.querySelectorAll('#interCard .ad-p').forEach(i=>out.imgs.push(Object.assign({cls:i.className},R(i))));
          const ov=document.querySelector('#interCard .interad');
          out.overflowCard = card? getComputedStyle(card).overflow : null;
          out.overflowInterad = ov? getComputedStyle(ov).overflow : null;
          return out }""")
        print(json.dumps(r, indent=1))
        await br.close()
asyncio.run(m())
