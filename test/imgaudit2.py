import asyncio, json, collections
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter()")
        tot=collections.Counter()
        for v,setup in [('home',"go('home')"),('deals',"go('deals')"),('store',"go('store')"),
                        ('all',"go('all')"),('disp',"go('cat','disp')"),('water',"go('cat','water')"),
                        ('dab',"go('cat','dab')"),('nic',"go('cat','nic')"),('eliq',"go('cat','eliq')"),
                        ('hard',"go('cat','hard')"),('rig',"go('cat','rig')"),('hand',"go('cat','hand')"),
                        ('parts',"go('cat','parts')"),('roll',"go('cat','roll')"),('cig',"go('cat','cig')"),
                        ('hook',"go('cat','hook')"),('gear',"go('cat','gear')"),('snack',"go('cat','snack')"),
                        ('exotic',"go('cat','exotic')")]:
            await pg.evaluate(setup); await pg.wait_for_timeout(2600)
            r=await pg.evaluate("""()=>{
              const bad=[];
              document.querySelectorAll('.view.on img').forEach(im=>{
                if(im.offsetParent===null) return;
                if(im.naturalWidth>2) return;
                const src=im.getAttribute('src')||'';
                bad.push({where:(im.closest('[class]')||{className:'?'}).className.split(' ')[0],
                          src: src.slice(0,4)==='data'?'DATA':src.split('/')[2]||src.slice(0,40),
                          alt:(im.alt||'').slice(0,40)});
              });
              const all=[...document.querySelectorAll('.view.on img')].filter(i=>i.offsetParent!==null).length;
              return {all, bad} }""")
            tot[v]=(r['all'], len(r['bad']))
            if r['bad']:
                print('%-7s %3d imgs, %3d broken' % (v, r['all'], len(r['bad'])))
                c=collections.Counter((b['where'],b['src']) for b in r['bad'])
                for k,n in c.most_common(6): print('        %-16s %-28s x%d' % (k[0],k[1],n))
            else:
                print('%-7s %3d imgs, all good' % (v, r['all']))
        await br.close()
asyncio.run(m())
