#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Press every control in the app and write down what happened.

Exhaustive rather than clever: enumerate every visible clickable thing on every
screen, press it, record the state before and after, put the app back, and move
on. Anything that changes nothing at all gets flagged for a human look, because
a control that does nothing is indistinguishable from a broken one.
"""
import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

B = __import__('sppath').APP
OUT = '/tmp/spall'
os.makedirs(OUT, exist_ok=True)

STATE = """() => {
  const cs = (typeof CATSTATE !== 'undefined' && CATSTATE) ? CATSTATE : {};
  const open = [...document.querySelectorAll('.on')]
      .map(e => e.id || String(e.className))
      .filter(x => /sheet|modal|pop|inter|ff|ask|menu|pin|staff|drawer|toast|srow/i.test(x));
  const grid = document.querySelector('#catGrid, #allGrid');
  return {
    view: (typeof VIEW !== 'undefined') ? VIEW : '?',
    cat: cs.c || null,
    brand: Array.isArray(cs.b) ? cs.b.join('+') : (cs.b || ''),
    sub: cs.sub || '',
    sort: cs.sort || '',
    cards: grid ? grid.querySelectorAll('.card').length : 0,
    cart: (typeof S !== 'undefined' && S.cart) ? S.cart.length : 0,
    favs: (typeof S !== 'undefined' && S.favs) ? S.favs.length : 0,
    orders: (typeof S !== 'undefined' && S.orders) ? S.orders.length : 0,
    open: open.slice(0, 4).join(','),
    scroll: Math.round((document.querySelector('#main') || {scrollTop: 0}).scrollTop),
    sig: document.body.textContent.length
  };
}"""

RESET = """() => {
  document.querySelectorAll('.sheet.on,.modal.on,#inter.on,.pop.on,#menu.on,#ff.on,#ask.on,#pin.on,#staff.on')
    .forEach(e => e.classList.remove('on'));
  const t = document.querySelector('#toast'); if(t) t.classList.remove('on','withacts');
}"""

SCREENS = [
    ('home',        "go('home')"),
    ('deals',       "go('deals')"),
    ('store',       "go('store')"),
    ('all',         "go('all')"),
    ('shelf-disp',  "go('cat','disp')"),
    ('shelf-water', "go('cat','water')"),
    ('shelf-love',  "go('cat','love')"),
    ('bag',         "go('orders')"),
    ('account',     "go('account')"),
]


async def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else 'en'
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console.' + m.type + ': ' + m.text)
              if m.type == 'error' else None)
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter()")
        if lang == 'es':
            await pg.evaluate("setLang('es')")
            await pg.wait_for_timeout(1200)

        rows = []
        for name, setup in SCREENS:
            await pg.evaluate(RESET)
            await pg.evaluate(setup)
            await pg.wait_for_timeout(1000)
            ctrls = await pg.evaluate("""() => {
                const out = [], seen = new Set();
                document.querySelectorAll(
                  '.view.on button, .view.on a[href], .view.on [role=button], '
                  + 'header button, #nav button, #nav a').forEach(el => {
                  if(el.offsetParent === null || el.disabled) return;
                  const label = (el.getAttribute('aria-label') || el.textContent || '')
                                  .replace(/\\s+/g,' ').trim().slice(0,48);
                  const d = JSON.stringify(el.dataset || {});
                  const key = label + '::' + d;
                  if(seen.has(key)) return;
                  seen.add(key);
                  out.push({label, data: d, href: el.getAttribute('href') || null,
                            tag: el.tagName});
                });
                return out }""")
            for c in ctrls:
                await pg.evaluate(RESET)
                await pg.evaluate(setup)
                await pg.wait_for_timeout(420)
                before = await pg.evaluate(STATE)
                hit = await pg.evaluate("""(c) => {
                    const list = [...document.querySelectorAll(
                      '.view.on button, .view.on a[href], .view.on [role=button], '
                      + 'header button, #nav button, #nav a')]
                      .filter(e => e.offsetParent !== null && !e.disabled);
                    const el = list.find(e =>
                      ((e.getAttribute('aria-label') || e.textContent || '')
                        .replace(/\\s+/g,' ').trim().slice(0,48)) === c.label
                      && JSON.stringify(e.dataset || {}) === c.data);
                    if(!el) return false;
                    el.click(); return true }""", c)
                if not hit:
                    continue
                await pg.wait_for_timeout(560)
                after = await pg.evaluate(STATE)
                keys = ('view', 'cat', 'brand', 'sub', 'sort', 'cards',
                        'cart', 'favs', 'orders', 'open', 'sig')
                changed = [k for k in keys if before.get(k) != after.get(k)]
                scrolled = abs((after.get('scroll') or 0) - (before.get('scroll') or 0)) > 30
                rows.append({'screen': name, 'label': c['label'], 'data': c['data'],
                             'href': c['href'], 'changed': changed,
                             'scrolled': scrolled, 'before': before, 'after': after})

        json.dump({'lang': lang, 'rows': rows, 'errs': errs},
                  open('%s/walk-%s.json' % (OUT, lang), 'w'), ensure_ascii=False, indent=1)

        dead = [r for r in rows if not r['changed'] and not r['scrolled'] and not r['href']]
        print('lang=%s   %d controls pressed   %d page errors' % (lang, len(rows), len(errs)))
        print('%d did nothing at all:' % len(dead))
        for r in dead:
            print('   %-12s %-46s %s' % (r['screen'], r['label'][:46], r['data'][:56]))
        if errs:
            print('ERRORS:', errs[:6])
        await br.close()


asyncio.run(main())
