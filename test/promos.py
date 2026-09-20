import asyncio, json
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1600)
        r=await pg.evaluate("""()=>({
            ids: PROMOS.map(p=>p.id),
            slides: document.querySelectorAll('#heroVp .slide').length,
            dots: document.querySelectorAll('#heroDots button').length,
            heroImgs: PROMOS.map(p=>({id:p.id,
               hero: p.shot&&p.shot.hero? (p.shot.hero()? p.shot.hero().slice(0,24):'EMPTY') : 'none',
               back: p.shot&&p.shot.back? (p.shot.back()? p.shot.back().slice(0,24):'EMPTY') : 'none'}))
          })""")
        print(json.dumps(r, indent=1))
        # which back images are NOT in HERO_DEVICE
        r2=await pg.evaluate("""()=>{
            const out=[];
            const want=[['Off-Stamp','X Cube 25K'],['Off-Stamp','SW9000'],
                        ['Lost Mary','MT35000 Turbo'],['Lost Mary','MO20000 Pro'],
                        ['Geek Bar','Pulse X 25K'],['Geek Bar','Pulse X2 50K'],
                        ['TRE House','Mushroom Chocolate, Peanut Butter'],
                        ['TRE House','Mushroom Chocolate, Fruity Cereal']];
            want.forEach(([b,m])=>{ const id=pidFor(b,m);
              out.push({b,m,id, device: !!(typeof HERO_DEVICE!=='undefined' && HERO_DEVICE[id])}) });
            return out }""")
        print(json.dumps(r2, indent=1))
        await br.close()
asyncio.run(m())
