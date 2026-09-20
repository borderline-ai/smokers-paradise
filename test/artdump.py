import asyncio, base64, io, os
from playwright.async_api import async_playwright
from PIL import Image
B='/root/work/smokers-paradise-demo/build/index.html'
os.makedirs('/tmp/spart', exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page()
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1500)
        for b,mm,tag in [('Off-Stamp','X Cube 25K','xcube'),('Lost Mary','MT35000 Turbo','lm'),
                         ('Geek Bar','Pulse X 25K','gb'),('Off-Stamp','SW9000','sw9000'),
                         ('Lost Mary','MO20000 Pro','lm2'),('Geek Bar','Pulse 15K','gb2')]:
            u=await pg.evaluate("([b,m])=>{const f=(typeof heroCut==='function')?heroCut(b,m):''; return f||''}", [b,mm])
            if not u: print(tag,'NONE'); continue
            open('/tmp/spart/%s.webp'%tag,'wb').write(base64.b64decode(u.split(',',1)[1]))
            print(tag, Image.open('/tmp/spart/%s.webp'%tag).size)
        await br.close()
asyncio.run(m())
