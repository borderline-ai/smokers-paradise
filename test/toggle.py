import asyncio, json
from playwright.async_api import async_playwright
B=__import__('sppath').APP
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter(); go('account')"); await pg.wait_for_timeout(1300)
        r=await pg.evaluate("""async ()=>{
          const q=k=>document.querySelector('[data-tog="'+k+'"]');
          const out={};
          for(const k of ['notif','sms']){
            const b0=q(k); if(!b0){ out[k]='missing'; continue }
            const cls0=b0.className, s0=S[k];
            b0.click(); await new Promise(r=>setTimeout(r,600));
            const b1=q(k);
            out[k]={s0, s1:S[k], cls0, cls1:b1?b1.className:'gone',
                    visuallyChanged: b1 && b1.className!==cls0,
                    aria:b1?b1.getAttribute('aria-label'):null,
                    role:b1?b1.getAttribute('role'):null,
                    checked:b1?b1.getAttribute('aria-checked'):null};
            q(k).click(); await new Promise(r=>setTimeout(r,500));
          }
          return out }""")
        print(json.dumps(r, indent=1))
        await pg.evaluate("()=>{const e=document.querySelector('[data-tog]'); if(e) e.closest('.sec,.pad,div').scrollIntoView({block:'center'})}")
        await pg.wait_for_timeout(900); await pg.screenshot(path='/tmp/spv/toggles.png')
        await br.close()
asyncio.run(m())
