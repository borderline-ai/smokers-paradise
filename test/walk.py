#!/usr/bin/env python3
"""Every screen, full page, at the size a phone shows it.

Not for a checklist. For reading.
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

B = sys.argv[1] if len(sys.argv) > 1 else __import__('sppath').APP
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/spread'
os.makedirs(OUT, exist_ok=True)


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter()")
        await pg.wait_for_timeout(600)

        async def shot(name, setup, scrolls):
            await pg.evaluate(setup)
            await pg.wait_for_timeout(1300)
            for i, y in enumerate(scrolls):
                await pg.evaluate("(y)=>{document.querySelector('#main').scrollTop=y}", y)
                await pg.wait_for_timeout(900)
                await pg.screenshot(path='%s/%s-%d.png' % (OUT, name, i))

        await shot('home', "go('home')", [0, 780, 1560, 2340, 3120, 3900, 4680, 5460])
        await shot('deals', "go('deals')", [0, 780, 1560, 2340])
        await shot('store', "go('store')", [0, 780, 1560, 2340, 3120, 3900])
        await shot('all', "go('all')", [0, 900])
        await shot('shelf', "go('cat','disp')", [0, 700, 1400])
        await shot('bag', "go('orders')", [0, 700])
        await shot('acct', "go('account')", [0, 700])

        # a product, the bag with something in it, and checkout
        await pg.evaluate("""async () => {
            S.cart = []; go('cat','disp'); await new Promise(r=>setTimeout(r,700));
            const c = document.querySelector('#catGrid .card'); if(c) c.click(); }""")
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path=OUT + '/pdp-0.png')
        await pg.evaluate("""() => { const s=document.querySelector('.sheet.on');
            if(s){ const b=s.querySelector('.sheetbody')||s; b.scrollTop=700 } }""")
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=OUT + '/pdp-1.png')

        print('errors:', errs[:5])
        await br.close()


asyncio.run(main())
