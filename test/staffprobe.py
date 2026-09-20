import asyncio, json
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file:///root/work/smokers-paradise-demo/build/index.html'); await pg.wait_for_timeout(1700)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        r=await pg.evaluate("""async ()=>{
          hideInter(); S.cart=[]; addToBag(PRODUCTS[0],{},1); S.name='Demo'; S.phone='5203382119'; save();
          go('checkout'); await new Promise(r=>setTimeout(r,900));
          CHK.step=3; renderCheckout(); await new Promise(r=>setTimeout(r,800));
          document.querySelector('#placeBtn').click(); await new Promise(r=>setTimeout(r,2100));
          const code=S.orders[0].code;
          const out={code, STAB:(typeof STAB!=='undefined')?STAB:'?'};
          renderStaff(); await new Promise(r=>setTimeout(r,700));
          out.defaultTab=(typeof STAB!=='undefined')?STAB:'?';
          out.bodyHasCode1=(document.querySelector('#staffBody')||{textContent:''}).textContent.indexOf(code)>=0;
          const t=document.querySelector('[data-stab="orders"]');
          out.foundTab=!!t;
          if(t){ t.click(); await new Promise(r=>setTimeout(r,800)) }
          out.afterTab=(typeof STAB!=='undefined')?STAB:'?';
          const b=(document.querySelector('#staffBody')||{textContent:''}).textContent;
          out.bodyHasCode2=b.indexOf(code)>=0;
          out.ticketCount=document.querySelectorAll('#staffBody .ticket').length;
          out.snippet=b.replace(/\\s+/g,' ').slice(0,200);
          return out }""")
        print(json.dumps(r, indent=1))
        await pg.evaluate("$('#staff').classList.add('on')"); await pg.wait_for_timeout(800)
        await pg.screenshot(path='/tmp/spj/staff.png')
        await br.close()
asyncio.run(m())
