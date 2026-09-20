import asyncio, json
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file:///root/work/smokers-paradise-demo/build/index.html'); await pg.wait_for_timeout(1700)
        r=await pg.evaluate("""async ()=>{
          document.querySelector('#gateNo').click(); await new Promise(r=>setTimeout(r,700));
          const yes=document.querySelector('#gateYes');
          const st=getComputedStyle(yes);
          return {denyShown: getComputedStyle(document.querySelector('#gateDeny')).display!=='none',
                  yesVisible: yes.offsetParent!==null, yesDisabled: yes.disabled,
                  yesOpacity: st.opacity, yesPointer: st.pointerEvents} }""")
        print('after tapping under-21:', json.dumps(r))
        await pg.screenshot(path='/tmp/spj/gate-denied.png')
        r2=await pg.evaluate("""async ()=>{
          document.querySelector('#gateYes').click(); await new Promise(r=>setTimeout(r,1200));
          return {entered: getComputedStyle(document.querySelector('#gate')).display==='none', view:VIEW} }""")
        print('can still enter:', json.dumps(r2))
        # staff Orders tab
        r3=await pg.evaluate("""async ()=>{
          hideInter(); S.cart=[]; addToBag(PRODUCTS[0],{},1); S.name='Demo'; S.phone='5203382119'; save();
          go('checkout'); await new Promise(r=>setTimeout(r,900));
          CHK.step=3; renderCheckout(); await new Promise(r=>setTimeout(r,800));
          document.querySelector('#placeBtn').click(); await new Promise(r=>setTimeout(r,2000));
          const code=S.orders[0].code;
          renderStaff(); await new Promise(r=>setTimeout(r,600));
          const tabs=[...document.querySelectorAll('#staff [data-stab], #staff .stab')].map(b=>b.textContent.trim());
          const ord=[...document.querySelectorAll('#staff button, #staff [role=tab]')].find(b=>/^orders$/i.test(b.textContent.trim()));
          if(ord){ ord.click(); await new Promise(r=>setTimeout(r,800)) }
          const t=(document.querySelector('#staffBody')||{textContent:''}).textContent;
          return {code, tabs, clickedOrders:!!ord, hasCode:t.indexOf(code)>=0,
                  snippet:t.replace(/\\s+/g,' ').slice(0,200)} }""")
        print('staff orders tab:', json.dumps(r3, indent=1))
        await br.close()
asyncio.run(m())
