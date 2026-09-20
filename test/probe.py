#!/usr/bin/env python3
import asyncio
import json
from playwright.async_api import async_playwright

B = '/root/work/smokers-paradise-demo/build/index.html'


async def m():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1400)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1600)

        r = await pg.evaluate("""async () => {
            const b = [...document.querySelectorAll('#interCard button')]
                        .find(x => /Shop Off-Stamp/i.test(x.textContent));
            if(!b) return 'no cta';
            b.click(); await new Promise(r=>setTimeout(r,1300));
            const cards = [...document.querySelectorAll('#catGrid .card')];
            return { interStillOpen: document.querySelector('#inter').classList.contains('on'),
                     view: VIEW, cat: CATSTATE.c, brand: JSON.stringify(CATSTATE.b),
                     cards: cards.length,
                     firstFive: cards.slice(0,5).map(c=>c.textContent.replace(/\\s+/g,' ').trim().slice(0,26)),
                     offStampAt: cards.findIndex(c=>/Off-Stamp/i.test(c.textContent)) } }""")
        print('ENTRANCE CTA ->', json.dumps(r, indent=1))
        await pg.screenshot(path='/tmp/spcta/02-offstamp-landing.png')

        probes = [
            ('Find Your Fit', "const b=document.querySelector('[data-ffopen]'); if(b)b.click()"),
            ('Join / signup', "const b=document.querySelector('[data-signup]'); if(b)b.click()"),
            ('Read all reviews', "const b=[...document.querySelectorAll('button')].find(x=>/Read all .*reviews/i.test(x.textContent)); if(b)b.click()"),
            ('Write a review', "const b=[...document.querySelectorAll('button')].find(x=>/Write a review/i.test(x.textContent)); if(b)b.click()"),
            ('Shop by category', "const b=document.querySelector('[data-scrollto]'); if(b)b.click()"),
        ]
        for name, js in probes:
            await pg.evaluate("go('home')")
            await pg.wait_for_timeout(800)
            top0 = await pg.evaluate("(document.querySelector('#main')||{scrollTop:0}).scrollTop")
            await pg.evaluate(js)
            await pg.wait_for_timeout(1000)
            st = await pg.evaluate("""() => ({
                view: VIEW,
                opened: [...document.querySelectorAll('.on')]
                          .map(e => e.id || String(e.className))
                          .filter(x => /sheet|modal|pop|ff|sign|rev|ask|inter|drawer/i.test(x))
                          .slice(0,4),
                top: (document.querySelector('#main')||{scrollTop:0}).scrollTop })""")
            st['movedFrom'] = top0
            print('%-18s -> %s' % (name, json.dumps(st)))

        await pg.evaluate("go('all')")
        await pg.wait_for_timeout(1100)
        st = await pg.evaluate("""async () => {
            const c = document.querySelector('#allGrid .card, .grid .card');
            if(!c) return 'no card';
            const name = c.textContent.replace(/\\s+/g,' ').trim().slice(0,30);
            c.click(); await new Promise(r=>setTimeout(r,1000));
            return { clicked: name, view: VIEW,
                     opened: [...document.querySelectorAll('.on')].map(e=>e.id||String(e.className)).slice(0,6) } }""")
        print('product card ->', json.dumps(st))
        print('errors:', errs[:4])
        await br.close()


asyncio.run(m())
