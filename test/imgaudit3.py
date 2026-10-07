import asyncio, json, collections
from playwright.async_api import async_playwright
B=__import__('sppath').APP
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter()")
        for v,setup in [('disp',"go('cat','disp')"),('all',"go('all')"),('home',"go('home')")]:
            await pg.evaluate(setup); await pg.wait_for_timeout(1500)
            # walk the whole page so every lazy image is asked for
            await pg.evaluate("""async ()=>{
              const m=document.querySelector('#main');
              const h=m.scrollHeight;
              for(let y=0; y<h; y+=500){ m.scrollTop=y; await new Promise(r=>setTimeout(r,180)) }
              m.scrollTop=0; await new Promise(r=>setTimeout(r,400)); }""")
            await pg.wait_for_timeout(3500)
            r=await pg.evaluate("""()=>{
              const bad=[], ok=[];
              document.querySelectorAll('.view.on img').forEach(im=>{
                const src=im.getAttribute('src')||'';
                if(im.naturalWidth>2){ ok.push(1); return }
                bad.push({cls:im.className||'-', host: src.slice(0,5)==='data:'?'DATA':(src.split('/')[2]||src.slice(0,30)),
                          alt:(im.alt||'').slice(0,34)});
              });
              const plates=document.querySelectorAll('.view.on .nophoto').length;
              return {imgs:ok.length+bad.length, broken:bad.length, plates, bad:bad.slice(0,14)} }""")
            print('%-6s imgs=%-4d broken=%-3d comingSoonPlates=%d' % (v, r['imgs'], r['broken'], r['plates']))
            if r['bad']:
                c=collections.Counter((b['cls'],b['host']) for b in r['bad'])
                for k,n in c.most_common(8): print('        %-22s %-26s x%d' % (k[0][:22],k[1],n))
                for b in r['bad'][:5]: print('        alt:', b['alt'])
        await br.close()
asyncio.run(m())
