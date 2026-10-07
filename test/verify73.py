#!/usr/bin/env python3
"""Every claim in this pass, checked by pressing the thing a customer presses."""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

B = __import__('sppath').APP
os.makedirs('/tmp/spfix', exist_ok=True)
fails, passes = [], []


def check(name, ok, detail=''):
    (passes if ok else fails).append(name)
    print(('  ok   ' if ok else '  FAIL ') + name + (('  :: ' + str(detail)) if detail and not ok else ''))


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1400)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1700)

        # ---- 1. the entrance, exactly as a customer meets it ----------------
        await pg.screenshot(path='/tmp/spfix/01-entrance.png')
        r = await pg.evaluate("""async () => {
            const b = [...document.querySelectorAll('#interCard button')]
                        .find(x => /Shop Off-Stamp/i.test(x.textContent));
            if(!b) return {none:true};
            b.click(); await new Promise(r=>setTimeout(r,1300));
            const cards = [...document.querySelectorAll('#catGrid .card')];
            return { closed: !document.querySelector('#inter').classList.contains('on'),
                     view: VIEW, cat: CATSTATE.c, brand: (CATSTATE.b||[]).join('+'),
                     n: cards.length,
                     allOffStamp: cards.length > 0 && cards.every(c=>/Off-Stamp/i.test(c.textContent)) } }""")
        check('the entrance offer closes when its button is pressed', r.get('closed'), r)
        check('"Shop Off-Stamp" lands on the disposables shelf', r.get('cat') == 'disp', r)
        check('and it is filtered to Off-Stamp', r.get('brand') == 'Off-Stamp', r)
        check('so every card on it is an Off-Stamp', r.get('allOffStamp'), r)
        await pg.screenshot(path='/tmp/spfix/02-offstamp-shelf.png')

        # ---- 2. every promo and deal that names a brand --------------------
        cases = [
            ('Browse pods',      'disp', 'Off-Stamp'),
            ('See the flavors',  'disp', 'Lost Mary'),
            ('Browse new vapes', 'disp', 'Geek Bar'),
            ('Shop Off-Stamp',   'disp', 'Off-Stamp'),
            ('Shop Puffco',      'dab',  'Puffco'),
        ]
        for label, cat, brand in cases:
            got = await pg.evaluate("""async (args) => {
                const [label, ] = args;
                go('home'); await new Promise(r=>setTimeout(r,500));
                const all = [...PROMOS, ...DEALCARDS];
                const d = all.find(x => (x.cta || x.ctaLabel) === label);
                if(!d) return {missing:true};
                goTarget(d.target || d.ctaTarget);
                await new Promise(r=>setTimeout(r,900));
                const cards = [...document.querySelectorAll('#catGrid .card')];
                return { cat: CATSTATE.c, brand: (CATSTATE.b||[]).join('+'),
                         n: cards.length,
                         pure: cards.length>0 && cards.every(c=>c.textContent.indexOf(args[2])>=0) } }""",
                [label, cat, brand])
            # The shelf drops a brand filter when the shelf holds only that one
            # brand, because narrowing 20 Puffcos to Puffco is not a narrowing.
            # What the button promised is that everything on the screen is the
            # brand it named, and that is what is checked.
            check('"%s" -> %s, and every card is a %s' % (label, cat, brand),
                  got.get('cat') == cat and got.get('pure')
                  and (got.get('brand') == brand or got.get('brand') == ''), got)

        # ---- 3. the two shelf-wide buttons must NOT be filtered -------------
        got = await pg.evaluate("""async () => {
            go('home'); await new Promise(r=>setTimeout(r,400));
            const d = DEALCARDS.find(x => x.ctaLabel === 'Shop glass');
            goTarget(d.ctaTarget); await new Promise(r=>setTimeout(r,900));
            return {cat: CATSTATE.c, brand: (CATSTATE.b||[]).join('+'),
                    n: document.querySelectorAll('#catGrid .card').length} }""")
        check('"Shop glass" still opens the whole glass shelf',
              got.get('cat') == 'water' and not got.get('brand') and got.get('n') > 10, got)

        # ---- 4. Shop by category actually scrolls --------------------------
        got = await pg.evaluate("""async () => {
            go('home'); await new Promise(r=>setTimeout(r,900));
            const main = document.querySelector('#main');
            main.scrollTop = 0; await new Promise(r=>setTimeout(r,200));
            const b = document.querySelector('[data-scrollto]'); if(!b) return {missing:true};
            b.click(); await new Promise(r=>setTimeout(r,1500));
            const rail = document.getElementById('catRail');
            return { top: Math.round(main.scrollTop),
                     railOnScreen: rail ? Math.round(rail.getBoundingClientRect().top) : null } }""")
        check('"Shop by category" scrolls the page to the rail',
              got.get('top', 0) > 400 and 0 < (got.get('railOnScreen') or -1) < 500, got)
        await pg.screenshot(path='/tmp/spfix/03-catrail.png')

        # ---- 5. no poster leads with a warning label -----------------------
        got = await pg.evaluate("""() => PROMOS.filter(p=>p.shot).map(p => ({
              id: p.id,
              hero: p.shot.hero ? p.shot.hero().slice(0,40) : '',
              device: !!(typeof HERO_DEVICE!=='undefined' && p.shot.hero
                         && p.shot.hero().indexOf('data:image/webp') === 0) }))""")
        check('the three carton photographs are replaced by the device',
              sum(1 for g in got if g['device']) >= 3, got)

        # ---- 6. nothing else moved -----------------------------------------
        got = await pg.evaluate("""async () => {
            const bad = [];
            for(const c of CATS.map(x=>x[0])){
              go('cat', c); await new Promise(r=>setTimeout(r,260));
              const want = PRODUCTS.filter(p=>p.cat===c).length;
              const n = document.querySelectorAll('#catGrid .card').length;
              if(n !== want && want > 0) bad.push(c + ' ' + n + '/' + want);
            }
            return bad }""")
        check('every shelf still paints in full', not got, got)
        check('no page errors', not errs, errs[:3])

        await br.close()
    print('\n%d passed, %d failed' % (len(passes), len(fails)))
    sys.exit(1 if fails else 0)


asyncio.run(main())
