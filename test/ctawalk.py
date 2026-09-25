#!/usr/bin/env python3
"""Press every control in the app and write down where it actually landed.

The only question it asks is the one a customer asks: the button said X, did X
happen. A button naming a brand that lands on a whole department, a button that
promises eligible items and lands on a shelf where nothing is eligible, and a
button that does nothing at all are the same failure, and none of the three
shows up in a page-error log.
"""
import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

BUILD = sys.argv[1] if len(sys.argv) > 1 else __import__('sppath').APP
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/spcta'
os.makedirs(OUT, exist_ok=True)

STATE = """() => {
  const v = (typeof VIEW!=='undefined') ? VIEW : '?';
  const cs = (typeof CATSTATE!=='undefined' && CATSTATE) ? CATSTATE : {};
  const sheet = document.querySelector('.sheet.on, .modal.on, #inter.on, .pop.on');
  const grid = document.querySelector('#catGrid, #allGrid');
  const head = (document.querySelector('.view.on .shelfhead h2, .view.on h2') || {}).textContent || '';
  return {
    view: v,
    cat: cs.c || null,
    brand: Array.isArray(cs.b) ? cs.b.join('+') : (cs.b || null),
    sub: cs.sub || null,
    cards: grid ? grid.querySelectorAll('.card').length : 0,
    head: head.replace(/\\s+/g,' ').trim().slice(0,38),
    sheet: sheet ? (sheet.id || String(sheet.className)).slice(0,24) : null,
    scroll: Math.round((document.querySelector('#main')||{scrollTop:0}).scrollTop)
  };
}"""

CLOSE = """() => { document.querySelectorAll('.sheet.on,.modal.on,#inter.on,.pop.on')
            .forEach(e=>e.classList.remove('on')); }"""


async def settle(pg, ms=700):
    await pg.wait_for_timeout(ms)


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + BUILD)
        await settle(pg, 1400)
        await pg.evaluate("const b=document.querySelector('#gateYes'); if(b) b.click()")
        await settle(pg, 1600)

        # ---------------------------------------------------- the entrance
        entrance = await pg.evaluate("""() => {
            const el = document.querySelector('#inter');
            if(!el || !el.classList.contains('on')) return null;
            const c = el.querySelector('#interCard') || el;
            const go = c.querySelector('.go');
            return { text: c.textContent.replace(/\\s+/g,' ').trim().slice(0,220),
                     go: go ? go.textContent.trim() : null,
                     id: go ? go.dataset.intergo : null } }""")
        await pg.screenshot(path=OUT + '/00-entrance.png')

        rows = []
        if entrance and entrance.get('go'):
            await pg.evaluate("document.querySelector('#interCard .go').click()")
            await settle(pg, 1400)
            land = await pg.evaluate(STATE)
            rows.append({'where': 'entrance', 'label': entrance['go'], 'land': land})
            await pg.screenshot(path=OUT + '/01-entrance-landing.png')
        await pg.evaluate(CLOSE)

        # -------------------------------------------------- walk every screen
        async def walk(where, setup):
            await pg.evaluate(CLOSE)
            await pg.evaluate(setup)
            await settle(pg, 1100)
            labels = await pg.evaluate("""() => {
              const out = [], seen = new Set();
              document.querySelectorAll(
                '.view.on button, .view.on a[href], .view.on [role=button]'
              ).forEach(el => {
                if(el.offsetParent === null) return;
                const label = (el.getAttribute('aria-label') || el.textContent || '')
                                .replace(/\\s+/g,' ').trim().slice(0,44);
                if(!label || seen.has(label)) return;
                seen.add(label); out.push(label);
              });
              return out }""")
            for label in labels:
                await pg.evaluate(CLOSE)
                await pg.evaluate(setup)
                await settle(pg, 500)
                before = await pg.evaluate(STATE)
                hit = await pg.evaluate("""(label) => {
                  const el = [...document.querySelectorAll(
                    '.view.on button, .view.on a[href], .view.on [role=button]')]
                    .filter(e => e.offsetParent !== null)
                    .find(e => ((e.getAttribute('aria-label')||e.textContent||'')
                        .replace(/\\s+/g,' ').trim().slice(0,44)) === label);
                  if(!el) return null;
                  const d = Object.assign({}, el.dataset);
                  const href = el.getAttribute('href') || null;
                  el.click();
                  return {data: d, href} }""", label)
                if hit is None:
                    continue
                await settle(pg, 750)
                after = await pg.evaluate(STATE)
                rows.append({'where': where, 'label': label,
                             'data': hit['data'], 'href': hit['href'],
                             'before': before, 'land': after})

        await walk('home', "go('home')")
        await walk('deals', "go('deals')")
        await walk('shelf:disp', "go('cat','disp')")
        await walk('all', "go('all')")

        json.dump({'entrance': entrance, 'rows': rows, 'errs': errs[:8]},
                  open(OUT + '/walk.json', 'w'), indent=1)
        print('entrance:', json.dumps(entrance))
        print('%d controls pressed, %d page errors' % (len(rows), len(errs)))
        await br.close()


asyncio.run(main())
