#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every screen, every shelf, every rail, with the network switched off.

The pitch happens three hours from a Wi-Fi network, on a phone that may have
one bar of signal in a shop on North Grand. So the only audit worth running is
the one where nothing can be fetched: the page is loaded from disk and every
other request is aborted.

Lazy images never fire onerror until they scroll into view, so an audit that
does not move the page reports zero broken images on a page full of them. This
one walks every screen down, then drags every horizontal rail across, then
promotes whatever is left to eager and waits.
"""
import asyncio
import json
from playwright.async_api import async_playwright

B = __import__('sppath').APP

SCREENS = [('home', "go('home')"), ('deals', "go('deals')"), ('store', "go('store')"),
           ('all', "go('all')"), ('account', "go('account')"), ('bag', "go('orders')")]

SWEEP = """async ()=>{
  const m = document.querySelector('#main');
  for(let y=0; y<m.scrollHeight; y+=380){ m.scrollTop=y; await new Promise(r=>setTimeout(r,120)) }
  for(const r of document.querySelectorAll(
      '.rail, .rail-cards, .spotrow, .feedrow, .brandgrid, .cattiles, .gr-strip, .dealgrid')){
    const w=r.scrollWidth;
    for(let x=0; x<w; x+=240){ r.scrollLeft=x; await new Promise(t=>setTimeout(t,70)) }
    r.scrollLeft=0;
  }
  document.querySelectorAll('img[loading="lazy"]').forEach(i=>i.loading='eager');
  m.scrollTop=0;
  await new Promise(r=>setTimeout(r,500));
}"""

COUNT = """()=>{
  const bad=[];
  document.querySelectorAll('.view.on img').forEach(im=>{
    if(im.naturalWidth>2) return;
    const src=im.getAttribute('src')||'';
    bad.push({cls:(im.className||'').slice(0,20),
              kind: src.slice(0,5)==='data:' ? 'DATA' : (src.split('/')[2]||src.slice(0,24)),
              alt:(im.alt||'').slice(0,44)});
  });
  return {imgs:document.querySelectorAll('.view.on img').length, bad};
}"""


async def main():
    total = broken = 0
    rows = []
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter()")

        cats = await pg.evaluate("CATS.map(c=>c[0])")
        screens = SCREENS + [('shelf:' + c, "go('cat','%s')" % c) for c in cats]

        for name, setup in screens:
            await pg.evaluate(setup)
            await pg.wait_for_timeout(700)
            await pg.evaluate(SWEEP)
            await pg.wait_for_timeout(1400)
            r = await pg.evaluate(COUNT)
            total += r['imgs']
            broken += len(r['bad'])
            rows.append((name, r['imgs'], r['bad']))
            print('  %-16s %4d images  %d broken%s'
                  % (name, r['imgs'], len(r['bad']),
                     '  ' + json.dumps(r['bad'][:3], ensure_ascii=False) if r['bad'] else ''))

        print('\n%d images across %d screens, %d broken, network dead'
              % (total, len(rows), broken))
        if errs:
            print('PAGE ERRORS:', errs[:4])
        await br.close()
    raise SystemExit(1 if (broken or errs) else 0)


asyncio.run(main())
