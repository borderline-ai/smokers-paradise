import asyncio, json
from playwright.async_api import async_playwright
B=__import__('sppath').APP
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1500)
        await pg.evaluate("""async ()=>{
          const m=document.querySelector('#main');
          for(let y=0; y<m.scrollHeight; y+=420){ m.scrollTop=y; await new Promise(r=>setTimeout(r,200)) }
          // every horizontal rail, all the way across and back
          for(const r of document.querySelectorAll('.rail, .spotrow, .feedrow, .brandgrid, .cattiles, .gr-strip')){
            const w=r.scrollWidth;
            for(let x=0; x<w; x+=260){ r.scrollLeft=x; await new Promise(t=>setTimeout(t,110)) }
            r.scrollLeft=0;
          }
          // and force any straggler to load now
          document.querySelectorAll('img[loading="lazy"]').forEach(i=>i.loading='eager');
          await new Promise(r=>setTimeout(r,400)); }""")
        await pg.wait_for_timeout(5000)
        r=await pg.evaluate("""()=>{
          const bad=[];
          document.querySelectorAll('.view.on img').forEach(im=>{
            if(im.naturalWidth>2) return;
            const src=im.getAttribute('src')||'';
            bad.push({cls:im.className, host: src.slice(0,5)==='data:'?'DATA':(src.split('/')[2]||''),
                      alt:(im.alt||'').slice(0,40)});
          });
          return {imgs:document.querySelectorAll('.view.on img').length, broken:bad.length, bad,
                  plates:document.querySelectorAll('.view.on .nophoto').length} }""")
        print(json.dumps(r, indent=1)[:1200])
        await br.close()
asyncio.run(m())
