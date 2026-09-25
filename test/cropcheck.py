#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is any picture in this app being CUT OFF by the box it sits in?

Marco, four times: "there should not be any cropped pictures like those where
you can only see the tip of the disposable vapes, the tip of the vape
hardware... the e-liquid category has a picture of THE TOP OF A E-LIQUID BOTTLE
INSTEAD OF AN ACTUAL E-LIQUID BOTTLE".

I told him a tile with `object-fit:contain` could not crop. That was wrong, and
this test is the thing that should have answered it instead of me:

    .ctile .ph img{width:78%;height:78%;object-fit:contain}

A PERCENTAGE HEIGHT NEEDS A PARENT WITH A DEFINITE HEIGHT. `.ph` is a grid box
whose height comes from its own content, so `height:78%` resolves to `auto`,
the image's own aspect ratio takes over, and a 103x432 vape inside a 104px tile
renders 57 x 234 — 171px of it hanging out of the bottom of a box with
`overflow:hidden` on it. object-fit never got a chance to do anything, because
the BOX was the wrong size before object-fit was consulted.

So this measures, for every image on every screen: how far does it extend past
the nearest ancestor that clips? Anything over a few pixels is a picture the
customer is only seeing part of.
"""
import asyncio
from playwright.async_api import async_playwright

B = __import__('sppath').APP

PROBE = """() => {
  const out = [];
  const clipper = el => {
    let p = el.parentElement;
    while(p && p !== document.body){
      const c = getComputedStyle(p);
      if(c.overflow !== 'visible' || c.overflowX !== 'visible' || c.overflowY !== 'visible') return p;
      p = p.parentElement;
    }
    return null;
  };
  document.querySelectorAll('img').forEach(im => {
    const c = getComputedStyle(im);
    if(c.display === 'none' || c.visibility === 'hidden' || +c.opacity === 0) return;
    if(im.offsetParent === null && c.position !== 'fixed') return;
    const r = im.getBoundingClientRect();
    if(r.width < 6 || r.height < 6) return;
    /* object-fit:cover is a deliberate crop: a photograph filling a frame. */
    if(c.objectFit === 'cover') return;
    const box = clipper(im);
    if(!box) return;
    /* A SCROLLER IS NOT A CROP. The page scrolls vertically and a rail scrolls
       sideways; a card parked off the end of either is reached by moving the
       thing, which is what it is for. Only judge the axis the box does NOT
       scroll on. */
    const scrollsY = box.scrollHeight > box.clientHeight + 2;
    const scrollsX = box.scrollWidth  > box.clientWidth + 2;
    const b = box.getBoundingClientRect();
    const overY = scrollsY ? 0 : Math.max(0, Math.round(b.top - r.top), Math.round(r.bottom - b.bottom));
    const overX = scrollsX ? 0 : Math.max(0, Math.round(b.left - r.left), Math.round(r.right - b.right));
    const over = Math.max(overY, overX);
    if(over <= 2) return;
    /* how much of the picture is actually being shown */
    const visW = scrollsX ? r.width  : Math.max(0, Math.min(r.right, b.right) - Math.max(r.left, b.left));
    const visH = scrollsY ? r.height : Math.max(0, Math.min(r.bottom, b.bottom) - Math.max(r.top, b.top));
    const shown = (visW * visH) / Math.max(1, r.width * r.height);
    out.push({
      cls: im.className ? '.' + String(im.className).trim().split(/\\s+/)[0] : 'img',
      box: box.tagName.toLowerCase() + (box.className ? '.' + String(box.className).trim().split(/\\s+/)[0] : ''),
      drawn: Math.round(r.width) + 'x' + Math.round(r.height),
      frame: Math.round(b.width) + 'x' + Math.round(b.height),
      over: over,
      shown: Math.round(shown * 100),
      alt: (im.alt || '').slice(0, 28)
    });
  });
  return out;
}"""


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(2000)
        await pg.evaluate("()=>document.getElementById('gateYes').click()")
        await pg.wait_for_timeout(1600)
        await pg.evaluate("()=>{const i=document.getElementById('inter'); if(i) i.style.display='none'}")

        seen, rows = set(), []

        async def sweep(name):
            await pg.evaluate("()=>document.querySelectorAll('.reveal').forEach(n=>n.classList.add('in'))")
            await pg.wait_for_timeout(350)
            for r in await pg.evaluate(PROBE):
                k = (name, r['cls'], r['box'], r['drawn'])
                if k in seen: continue
                seen.add(k)
                r['screen'] = name
                rows.append(r)

        for view, arg, name in [('home', None, 'home'), ('all', None, 'shop all'),
                                ('cat', 'disp', 'shelf:disp'), ('cat', 'water', 'shelf:water'),
                                ('cat', 'eliq', 'shelf:eliq'), ('cat', 'hard', 'shelf:hard'),
                                ('deals', None, 'deals'), ('store', None, 'store'),
                                ('account', None, 'account')]:
            await pg.evaluate("([v,a])=>go(v,a)", [view, arg])
            await pg.wait_for_timeout(900)
            n = await pg.evaluate("()=>document.getElementById('main').scrollHeight")
            y = 0
            while y < n:
                await pg.evaluate("(y)=>document.getElementById('main').scrollTo(0,y)", y)
                await pg.wait_for_timeout(200)
                await sweep(name)
                y += 700

        await pg.evaluate("()=>{const c=document.querySelector('.view.on .card'); if(c) c.click()}")
        await pg.wait_for_timeout(1300)
        await sweep('product page')
        await pg.evaluate("()=>{if(typeof closeSheet==='function') closeSheet()}")
        await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{if(typeof ffOpen==='function') ffOpen(null,'')}")
        await pg.wait_for_timeout(900)
        await sweep('find your fit')

        rows.sort(key=lambda r: r['shown'])
        print('\n%d pictures are being cut off by the box they sit in:' % len(rows))
        for r in rows:
            print('  %-14s %-22s in %-22s drawn %-10s frame %-9s %3d%% shown  %s'
                  % (r['screen'], r['cls'], r['box'], r['drawn'], r['frame'], r['shown'], r['alt']))
        await br.close()
    raise SystemExit(1 if rows else 0)


asyncio.run(main())
