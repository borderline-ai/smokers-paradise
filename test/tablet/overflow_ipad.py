#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spanish is longer than English. Find anything it breaks.

A button sized to "Shop the shelf" has to hold "Ver el estante"; one sized to
"Find Your Fit" has to hold "Encuentra lo tuyo". Rather than eyeball it, every
visible element is measured in both languages and anything whose text spills
past its own box, or that grew enough to push the page sideways, is reported.
"""
import asyncio
import json
import sys
from playwright.async_api import async_playwright

B = '/root/work/smokers-paradise-demo/build/index.html'

MEASURE = """() => {
  const bad = [];
  document.querySelectorAll('.view.on button, .view.on a, .view.on h1, .view.on h2, '
    + '.view.on h3, .view.on h4, .view.on b, .view.on .chip, .view.on .hl, '
    + '#nav *, header button').forEach(el => {
    if(el.offsetParent === null) return;
    if(!el.textContent || !el.textContent.trim()) return;
    if(el.children.length > 2) return;
    const cs = getComputedStyle(el);
    const clipsX = cs.overflowX === 'hidden' || cs.overflow === 'hidden';
    const over = el.scrollWidth - el.clientWidth;
    const overY = el.scrollHeight - el.clientHeight;
    /* a horizontal rail is meant to scroll; a button is not */
    const scroller = /rail|row|strip|grid|track|vp/.test(el.className || '');
    if(!scroller && over > 2 && (clipsX || cs.textOverflow === 'ellipsis')){
      bad.push({what: el.textContent.replace(/\\s+/g,' ').trim().slice(0,42),
                cls: (el.className||'').slice(0,26), over, kind:'clipped across'});
    }
    if(!scroller && overY > 2 && (cs.overflowY === 'hidden' || cs.overflow === 'hidden')){
      bad.push({what: el.textContent.replace(/\\s+/g,' ').trim().slice(0,42),
                cls: (el.className||'').slice(0,26), over: overY, kind:'clipped down'});
    }
  });
  const doc = document.documentElement;
  return {bad, sideways: Math.max(0, doc.scrollWidth - doc.clientWidth)};
}"""

SCREENS = [('home', "go('home')"), ('deals', "go('deals')"), ('store', "go('store')"),
           ('all', "go('all')"), ('shelf', "go('cat','disp')"),
           ('bag', "go('orders')"), ('account', "go('account')")]


async def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 390
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': width, 'height': 1180}, is_mobile=True, has_touch=True)
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1700)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter()")

        found = {}
        for lang in ['en', 'es']:
            await pg.evaluate("(l)=>setLang(l)", lang)
            await pg.wait_for_timeout(1300)
            for name, setup in SCREENS:
                await pg.evaluate(setup)
                await pg.wait_for_timeout(900)
                r = await pg.evaluate(MEASURE)
                if r['sideways'] > 2:
                    found.setdefault(lang, []).append(
                        {'screen': name, 'what': 'THE PAGE SCROLLS SIDEWAYS',
                         'over': r['sideways'], 'kind': 'page'})
                for b in r['bad']:
                    b['screen'] = name
                    found.setdefault(lang, []).append(b)

        print('viewport %dpx' % width)
        for lang in ['en', 'es']:
            rows = found.get(lang, [])
            seen, uniq = set(), []
            for r in rows:
                k = (r['screen'], r['what'], r['kind'])
                if k in seen:
                    continue
                seen.add(k)
                uniq.append(r)
            print('  %s: %d problems' % (lang, len(uniq)))
            for r in uniq[:20]:
                print('     %-8s %-16s %-42s by %dpx'
                      % (r['screen'], r['kind'], r['what'], r['over']))
        await br.close()


asyncio.run(main())
