import asyncio, json
from playwright.async_api import async_playwright
B=__import__('sppath').APP
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        r=await pg.evaluate("""()=>{
          const out=[];
          PROMOS.forEach(p=>{
            const h=p.shot&&p.shot.hero?p.shot.hero():'';
            const b=p.shot&&p.shot.back?p.shot.back():'';
            const kind=u=>!u?'NONE':(typeof heroCut==='function'&&false?'':(u.slice(0,30)));
            out.push({id:p.id, hero:kind(h), back:kind(b),
                      heroIsCut: !!(typeof heroCut==='function' && p.shot && heroCut(p.kicker,'')) });
          });
          return out }""")
        for x in r: print(x)
        # which deal art falls back
        r2=await pg.evaluate("""()=>DEALCARDS.map(d=>({id:d.id,
             art:(d.art||[]).map(a=>({b:a.b,m:a.m,
               cut: (typeof heroCut==='function')? (heroCut(a.b,a.m)?'cut':'NO CUT') : '?',
               shot:(typeof heroShot==='function')? (heroShot(a.b,a.m)?'shot':'no shot') : '?'}))}))""")
        print(json.dumps(r2, indent=1)[:1600])
        await br.close()
asyncio.run(m())
