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
        # 1. Back from a shelf you arrived at from home
        r=await pg.evaluate("""async ()=>{
            go('home'); await new Promise(r=>setTimeout(r,700));
            go('cat','disp'); await new Promise(r=>setTimeout(r,700));
            const b=document.querySelector('#v-cat [data-back]'); if(!b) return 'no back';
            b.click(); await new Promise(r=>setTimeout(r,800));
            return {view:VIEW} }""")
        print('back from shelf reached via home ->', json.dumps(r))
        # 2. account toggles
        r=await pg.evaluate("""async ()=>{
            go('account'); await new Promise(r=>setTimeout(r,900));
            const out={};
            for(const k of ['notif','sms']){
              const b=document.querySelector('[data-tog="'+k+'"]');
              if(!b){ out[k]='missing'; continue }
              const before=S[k], cls0=b.className, aria=b.getAttribute('aria-label'), role=b.getAttribute('role');
              b.click(); await new Promise(r=>setTimeout(r,500));
              out[k]={before, after:S[k], changed:S[k]!==before, cls0, cls1:b.className,
                      aria, role, text:b.textContent.trim()};
              b.click(); await new Promise(r=>setTimeout(r,400));
            }
            return out }""")
        print('account toggles ->', json.dumps(r, indent=1))
        # 3. image inventory
        r=await pg.evaluate("""()=>{
            let embedded=0, remote=0, hosts={};
            const scan=o=>{ for(const k in o){ const v=o[k];
              if(typeof v==='string'){
                if(v.slice(0,5)==='data:') embedded++;
                else if(/^https?:/.test(v)){ remote++; const h=v.split('/')[2]; hosts[h]=(hosts[h]||0)+1 } } } };
            if(typeof REMOTE!=='undefined') Object.values(REMOTE).forEach(r=>{ if(r&&r.remoteImageUrl){ remote++; const h=String(r.remoteImageUrl).split('/')[2]; hosts[h]=(hosts[h]||0)+1 } });
            if(typeof CUT_PHOTOS!=='undefined') scan(CUT_PHOTOS);
            if(typeof LOCAL_PHOTOS!=='undefined') scan(LOCAL_PHOTOS);
            const prods = PRODUCTS.length;
            return {embedded, remote, prods, topHosts:Object.entries(hosts).sort((a,b)=>b[1]-a[1]).slice(0,8)} }""")
        print('images ->', json.dumps(r, indent=1))
        # 4. how many cards actually render a picture with the network dead
        r=await pg.evaluate("""async ()=>{
            go('all'); await new Promise(r=>setTimeout(r,2500));
            const cards=[...document.querySelectorAll('.card')];
            let withImg=0, broken=0, none=0;
            cards.forEach(c=>{ const im=c.querySelector('img');
              if(!im) { none++; return }
              if(im.naturalWidth>2) withImg++; else broken++; });
            return {cards:cards.length, withImg, broken, none} }""")
        print('offline picture check ->', json.dumps(r))
        await br.close()
asyncio.run(m())
