#!/usr/bin/env python3
"""Every piece of TEXT that is being cut off by the box it sits in.

cropcheck.py asks that question about pictures. Nobody had asked it about
words, and a price reading "3 FOR $" is worse than a cropped photograph.

A text node is clipped when its own scroll extent is bigger than the box that
paints it, and that box is not a scroller. Horizontal rails and real scrollers
are excluded, the same way cropcheck excludes them."""
import asyncio, json
from playwright.async_api import async_playwright
B=__import__('sppath').APP

PROBE = """() => {
  const out=[];
  const walk = document.querySelectorAll('body *');
  walk.forEach(el=>{
    if(el.children.length && ![...el.childNodes].some(n=>n.nodeType===3 && n.textContent.trim())) return;
    const t=(el.textContent||'').trim(); if(!t) return;
    const cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0) return;
    const r=el.getBoundingClientRect(); if(r.width<6||r.height<4) return;
    if(r.bottom<0||r.top>innerHeight*3) return;
    const ox = el.scrollWidth - el.clientWidth;
    const oy = el.scrollHeight - el.clientHeight;
    const scrolls = /(auto|scroll)/.test(cs.overflow+cs.overflowX+cs.overflowY);
    if(scrolls) return;
    const hidden = /hidden|clip/.test(cs.overflow+cs.overflowX+cs.overflowY);
    const ell = cs.textOverflow==='ellipsis';
    if(ox>1 && (hidden||ell)) out.push({t:t.slice(0,48), by:ox, dir:'x',
      cls:(el.className||'').toString().slice(0,26), tag:el.tagName});
    else if(oy>2 && hidden && cs.webkitLineClamp==='none')
      out.push({t:t.slice(0,48), by:oy, dir:'y',
        cls:(el.className||'').toString().slice(0,26), tag:el.tagName});
  });
  return out;
}"""

async def main():
    async with async_playwright() as pw:
        br=await pw.chromium.launch()
        pg=await br.new_page(viewport={'width':390,'height':844})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1700)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1700)
        await pg.evaluate("hideInter()")
        cats = await pg.evaluate("CATS.map(c=>c[0])")
        seen={}
        screens=[('home',"go('home')"),('deals',"go('deals')"),('store',"go('store')"),
                 ('all',"go('all')"),('account',"go('account')"),('orders',"go('orders')")] \
                + [('shelf:'+c, "go('cat','%s')"%c) for c in cats]
        for name,setup in screens:
            await pg.evaluate(setup); await pg.wait_for_timeout(800)
            n = await pg.evaluate("document.querySelector('#main').scrollHeight")
            y=0
            while y < n:
                await pg.evaluate("(y)=>document.querySelector('#main').scrollTo(0,y)", y)
                await pg.wait_for_timeout(180)
                for d in await pg.evaluate(PROBE):
                    k=(d['cls'],d['t'])
                    if k in seen: continue
                    seen[k]={**d,'screen':name}
                y+=760
            await pg.evaluate("document.querySelector('#main').scrollTo(0,0)")
        rows=sorted(seen.values(), key=lambda d:-d['by'])
        print('\n%d pieces of text are being cut off:' % len(rows))
        for d in rows[:60]:
            print('  %-11s %-26s %s%-4d  %r' % (d['screen'], d['cls'], d['dir'], d['by'], d['t']))
        await br.close()
asyncio.run(main())
