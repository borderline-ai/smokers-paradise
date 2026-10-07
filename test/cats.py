import asyncio, json
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page()
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + __import__('sppath').APP); await pg.wait_for_timeout(1600)
        r=await pg.evaluate("""()=>{
          const out={cats:[], subs:{}};
          CATS.forEach(c=>out.cats.push([c[0],c[1],PRODUCTS.filter(p=>p.cat===c[0]).length]));
          PRODUCTS.forEach(p=>{const s=(typeof subOf==='function')?subOf(p):null; if(s){out.subs[p.cat+'/'+s]=(out.subs[p.cat+'/'+s]||0)+1}});
          return out }""")
        print(json.dumps(r['cats'], indent=0))
        print(json.dumps(r['subs'], indent=1))
        # what words DO hit
        for q in ['torch','tray','kratom','cbd','scale','incense','wrap','paper','juice','pod','vaporizer','grinder']:
            n=await pg.evaluate("""(q)=>PRODUCTS.filter(p=>{
                const hay=[p.name,p.brand,(p.vars||[]).join(' '),p.cat].join(' ').toLowerCase();
                return hay.indexOf(q)>=0}).length""", q)
            print('  %-12s %d' % (q, n))
        await br.close()
asyncio.run(m())
