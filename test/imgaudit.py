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
        r=await pg.evaluate("""()=>{
          const out={haveLocal:0, haveCut:0, remoteOnly:0, nothing:0, remoteOnlyIds:[]};
          PRODUCTS.forEach(p=>{
            const local = (typeof LOCAL_PHOTOS!=='undefined' && LOCAL_PHOTOS[p.id]) ? 1:0;
            const cut   = (typeof CUT_PHOTOS!=='undefined' && CUT_PHOTOS[p.id]) ? 1:0;
            const rem   = (typeof remoteFor==='function' && remoteFor(p,null)) ? 1:0;
            if(local) out.haveLocal++;
            else if(cut) out.haveCut++;
            else if(rem){ out.remoteOnly++; if(out.remoteOnlyIds.length<400) out.remoteOnlyIds.push(p.cat+'/'+p.id+' '+p.brand+' '+p.name) }
            else out.nothing++;
          });
          return out }""")
        print(json.dumps({k:v for k,v in r.items() if k!='remoteOnlyIds'}, indent=1))
        print('\nremote-only products by shelf:')
        import collections
        c=collections.Counter(x.split('/')[0] for x in r['remoteOnlyIds'])
        print(dict(c))
        print('\nfirst 12:'); [print('  ',x) for x in r['remoteOnlyIds'][:12]]
        # what does a broken card look like right now
        r2=await pg.evaluate("""async ()=>{
          go('cat','water'); await new Promise(r=>setTimeout(r,2500));
          const bad=[...document.querySelectorAll('#catGrid .card')].filter(c=>{
            const im=c.querySelector('img'); return im && im.naturalWidth<=2 });
          if(!bad.length) return 'none broken here';
          const c=bad[0], im=c.querySelector('img');
          return {n:bad.length, alt:im.alt, onerror:im.getAttribute('onerror'),
                  vis:getComputedStyle(im).visibility, display:getComputedStyle(im).display,
                  thumbHTML:c.querySelector('.thumb').innerHTML.slice(0,220)} }""")
        print('\nbroken card now ->', json.dumps(r2, indent=1)[:900])
        await br.close()
asyncio.run(m())
