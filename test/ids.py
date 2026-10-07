import asyncio, json
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page()
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + __import__('sppath').APP); await pg.wait_for_timeout(1500)
        r=await pg.evaluate("""()=>['Off-Stamp|X Cube 25K','Lost Mary|MT35000 Turbo','Geek Bar|Pulse X 25K']
            .map(k=>{const [b,m]=k.split('|'); const id=pidFor(b,m);
              return {k, id, inCUTOUTS: !!(typeof CUTOUTS!=='undefined' && CUTOUTS[id]),
                      inLOCAL: !!(typeof LOCAL_PHOTOS!=='undefined' && LOCAL_PHOTOS[id])}})""")
        print(json.dumps(r, indent=1))
        await br.close()
asyncio.run(m())
