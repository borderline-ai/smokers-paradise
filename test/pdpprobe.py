import asyncio, json
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + __import__('sppath').APP); await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter()")
        r=await pg.evaluate("""async ()=>{
          // a product that definitely has flavours
          const p = PRODUCTS.find(x=>x.cat==='disp' && (x.opts||[]).some(o=>o.k==='v' && o.vals.length>1));
          openPDP(p.id); await new Promise(r=>setTimeout(r,1100));
          const sh=document.querySelector('.sheet.on');
          const attrs={};
          sh.querySelectorAll('button').forEach(b=>{ for(const k in b.dataset) attrs[k]=(attrs[k]||0)+1 });
          const qUp=[...sh.querySelectorAll('[data-q]')].map(b=>b.dataset.q);
          const before=(document.querySelector('#pdpArt img')||{}).src||'';
          const optBtns=[...sh.querySelectorAll('[data-v]')];
          if(optBtns[1]) optBtns[1].click();
          await new Promise(r=>setTimeout(r,800));
          const after=(document.querySelector('#pdpArt img')||{}).src||'';
          const up=[...sh.querySelectorAll('[data-q]')].find(b=>b.dataset.q==='1');
          if(up) up.click(); await new Promise(r=>setTimeout(r,500));
          return {product:p.brand+' '+p.name, datasetKeys:attrs, qVals:qUp,
                  optCount:optBtns.length, picChanged: before!==after,
                  qty:(document.querySelector('#qv')||{}).textContent} }""")
        print(json.dumps(r, indent=1))
        # staff screen
        r2=await pg.evaluate("""async ()=>{
          S.cart=[]; const p=PRODUCTS[0]; addToBag(p,{},1);
          S.name='Demo'; S.phone='5203382119'; save();
          go('checkout'); await new Promise(r=>setTimeout(r,1000));
          CHK.step=3; renderCheckout(); await new Promise(r=>setTimeout(r,900));
          document.querySelector('#placeBtn').click(); await new Promise(r=>setTimeout(r,2200));
          const code=S.orders[0].code;
          renderStaff(); await new Promise(r=>setTimeout(r,700));
          const body=document.querySelector('#staffBody');
          return {code, live: (typeof LIVE!=='undefined')?LIVE.length:null,
                  liveCodes: (typeof LIVE!=='undefined')?LIVE.map(x=>x.code).slice(0,4):null,
                  staffLen: body?body.textContent.length:0,
                  staffHasCode: body? body.textContent.indexOf(code)>=0 : false,
                  staffSnippet: body? body.textContent.replace(/\\s+/g,' ').slice(0,180):''} }""")
        print(json.dumps(r2, indent=1))
        await br.close()
asyncio.run(m())
