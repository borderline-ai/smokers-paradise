# -*- coding: utf-8 -*-
"""Capture every screen so it can be LOOKED AT, not asserted.

Marco's standard for this pass: "Do not report the number of automated checks
as proof that the design is finished. A page can pass hundreds of technical
checks and still look unprofessional."

So this file asserts nothing. It drives the app into each state and writes a
full-page PNG, sliced into readable strips, so every screen gets human eyes.

    python3 test/qa.py                 # 390px, everything
    python3 test/qa.py 320 430 768     # other widths
"""
import os
import pathlib
import sys

from playwright.sync_api import sync_playwright

FILE = pathlib.Path(
    __import__('sppath').APP).as_uri()
OUT = __import__('sppath').SHOTS
WIDTHS = [int(a) for a in sys.argv[1:]] or [390]

# name -> a function body run in the page, plus how long to settle
SCREENS = [
    ('home',          "go('home')", 1200),
    ('all',           "go('all')", 900),
    ('cat-disp',      "go('cat','disp')", 700),
    ('cat-water',     "go('cat','water')", 700),
    ('cat-exotic',    "go('cat','exotic')", 700),
    ('cat-love',      "go('cat','love')", 600),
    ('search',        "go('search'); (function(){const i=document.querySelector('#q');"
                      "if(i){i.value='geek';i.dispatchEvent(new Event('input',{bubbles:true}))}})()", 900),
    ('deals',         "go('deals')", 900),
    ('rewards',       "go('rewards')", 800),
    ('store',         "go('store')", 900),
    ('account',       "go('account')", 800),
    ('menu',          "(function(){go('home');const b=document.querySelector('[data-menu]');if(b)b.click()})()", 700),
]


def shoot(pg, name, w):
    """Frame-by-frame at the REAL viewport.

    The app scrolls #main, not the window, and its header and bottom bar are
    fixed to the viewport — so a tall-viewport "full page" screenshot hides
    exactly the defects worth finding. Every frame here is 390x844 with the
    chrome where a customer actually sees it, stepped down the page until the
    scroller runs out.
    """
    pg.set_viewport_size({'width': w, 'height': 844})
    pg.wait_for_timeout(400)
    pg.evaluate("document.querySelector('#main').scrollTop = 0")
    pg.wait_for_timeout(350)
    out = []
    for i in range(14):
        path = '%s/%d-%s-%02d.png' % (OUT, w, name, i)
        pg.screenshot(path=path)
        out.append(path)
        at_end = pg.evaluate("""(()=>{const m=document.querySelector('#main');
          if(m.scrollTop + m.clientHeight >= m.scrollHeight - 4) return true;
          m.scrollTop += Math.round(m.clientHeight * 0.86); return false})()""")
        pg.wait_for_timeout(420)
        if at_end:
            break
    return '%s  (%d frames)' % (name, len(out))


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for w in WIDTHS:
            ctx = br.new_context(viewport={'width': w, 'height': 844},
                                 device_scale_factor=2)
            ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith(
                ('file:', 'data:', 'blob:')) else r.abort())
            pg = ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(FILE, wait_until='load')
            pg.wait_for_timeout(1600)
            pg.click('#gateYes')
            pg.wait_for_timeout(1600)
            if pg.locator('[data-interx]').count():
                pg.locator('[data-interx]').first.click()
                pg.wait_for_timeout(600)

            for name, js, wait in SCREENS:
                try:
                    pg.evaluate("(()=>{%s})()" % js)
                except Exception as e:
                    print('  !! %s: %s' % (name, e))
                    continue
                pg.wait_for_timeout(wait)
                print(' ', shoot(pg, name, w))
                if name == 'menu':
                    pg.keyboard.press('Escape')
                    pg.wait_for_timeout(300)

            # ---- the product page ------------------------------------------
            pg.evaluate("go('cat','disp')")
            pg.wait_for_timeout(600)
            pg.locator('#v-cat .card').first.click()
            pg.wait_for_timeout(900)
            print(' ', shoot(pg, 'pdp', w))

            # ---- the bag, then every checkout stage ------------------------
            pg.evaluate("""(()=>{
              S.cart=[]; const p=PRODUCTS.filter(x=>x.cat==='disp').slice(0,2);
              addToBag(p[0], {}, 2); addToBag(p[1], {}, 1);
              S.name=''; save(); go('orders')})()""")
            pg.wait_for_timeout(900)
            print(' ', shoot(pg, 'bag', w))

            # Driven the way a customer drives it: the wizard has four
            # steps (Review, Details, Pickup, Confirm) and each one is shot.
            pg.evaluate("go('checkout')")
            pg.wait_for_timeout(900)
            print(' ', shoot(pg, 'ck1-review', w))
            pg.locator('[data-cknext]').first.click()
            pg.wait_for_timeout(800)
            print(' ', shoot(pg, 'ck2-details', w))
            if pg.locator('#ckName').count():
                pg.fill('#ckName', 'santy')
                pg.fill('#ckPhone', '(520) 555-0134')
                pg.wait_for_timeout(300)
                print(' ', shoot(pg, 'ck2-details-filled', w))
            pg.locator('[data-cknext]').first.click()
            pg.wait_for_timeout(800)
            print(' ', shoot(pg, 'ck3-pickup', w))
            slots = pg.locator('[data-cks]')
            if slots.count() > 1:
                slots.nth(1).click()
                pg.wait_for_timeout(400)
                print(' ', shoot(pg, 'ck3-pickup-selected', w))
            pg.locator('[data-cknext]').first.click()
            pg.wait_for_timeout(800)
            print(' ', shoot(pg, 'ck4-confirm', w))
            pg.locator('#placeBtn').click()
            pg.wait_for_timeout(1800)
            print(' ', shoot(pg, 'order', w))

            # ---- empty states ----------------------------------------------
            pg.evaluate("(()=>{S.cart=[];save();go('orders')})()")
            pg.wait_for_timeout(700)
            print(' ', shoot(pg, 'bag-empty', w))
            pg.evaluate("""(()=>{go('search');const i=document.querySelector('#q');
              if(i){i.value='zzzzqq';i.dispatchEvent(new Event('input',{bubbles:true}))}})()""")
            pg.wait_for_timeout(800)
            print(' ', shoot(pg, 'search-empty', w))

            if errs:
                print('  PAGE ERRORS:', errs[:3])
            ctx.close()
        br.close()


if __name__ == '__main__':
    main()
