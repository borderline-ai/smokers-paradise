import asyncio, base64, io, os
from playwright.async_api import async_playwright
from PIL import Image
os.makedirs('/tmp/spback',exist_ok=True)
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page()
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file:///root/work/smokers-paradise-demo/build/index.html'); await pg.wait_for_timeout(1600)
        for b,mm,tag in [('Lost Mary','MO20000 Pro','lm2'),('Geek Bar','Pulse X2 50K','gb2'),
                         ('Off-Stamp','SW9000','sw'),('TRE House','Mushroom Chocolate, Peanut Butter','tre1'),
                         ('TRE House','Mushroom Chocolate, Fruity Cereal','tre2')]:
            u=await pg.evaluate("([b,m])=>{const id=pidFor(b,m); return (typeof CUT_PHOTOS!=='undefined'&&CUT_PHOTOS[id])||(typeof LOCAL_PHOTOS!=='undefined'&&LOCAL_PHOTOS[id])||''}", [b,mm])
            if not u or not u.startswith('data:'): print(tag,'NONE'); continue
            open('/tmp/spback/%s.webp'%tag,'wb').write(base64.b64decode(u.split(',',1)[1]))
            im=Image.open('/tmp/spback/%s.webp'%tag); print(tag, im.size, im.mode)
        await br.close()
asyncio.run(m())
