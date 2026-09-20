import asyncio, base64, io
from playwright.async_api import async_playwright
from PIL import Image
B='/root/work/smokers-paradise-demo/build/index.html'
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        for b,mm,tag in [('Off-Stamp','X Cube 25K','xcube'),('Off-Stamp','SW9000','sw9000'),
                         ('Lost Mary','MT35000 Turbo','lm'),('Geek Bar','Pulse X 25K','gb')]:
            u=await pg.evaluate("([b,m])=>{const f=(typeof heroCut==='function')?heroCut(b,m):''; return f||''}", [b,mm])
            if not u: print(tag,'NONE'); continue
            d=base64.b64decode(u.split(',',1)[1])
            im=Image.open(io.BytesIO(d)).convert('RGBA')
            bg=Image.new('RGBA',im.size,(30,10,30,255)); bg.alpha_composite(im)
            bg.convert('RGB').save('/tmp/spcta/art-%s.png'%tag); print(tag, im.size)
        await br.close()
asyncio.run(m())
