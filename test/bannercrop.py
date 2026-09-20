#!/usr/bin/env python3
"""Every product picture on a banner that is being CUT by the card it sits in.

Marco: "the banner of the geek bars has a bug in it, the geek bars are slightly
cropped."

The campaign cards position their product art absolutely with a deliberate
bleed (bottom:-6%, height:112%) so the product looks like it is standing out of
the frame. The card clips. Where the bleed is bigger than the art's own empty
margin, the PRODUCT gets cut instead of the empty space, and a cut product on
an advert reads as a broken image."""
import asyncio
from playwright.async_api import async_playwright
B='/root/work/smokers-paradise-demo/build/index.html'

PROBE = """() => {
  const out=[];
  document.querySelectorAll('.camp, .ad, .promo').forEach(card=>{
    const cs=getComputedStyle(card);
    if(!/hidden|clip/.test(cs.overflow)) return;
    const cr=card.getBoundingClientRect();
    card.querySelectorAll('img').forEach(im=>{
      const r=im.getBoundingClientRect();
      if(r.width<20) return;
      const cut={
        top:   Math.max(0, cr.top   - r.top),
        bottom:Math.max(0, r.bottom - cr.bottom),
        left:  Math.max(0, cr.left  - r.left),
        right: Math.max(0, r.right  - cr.right)
      };
      const worst=Math.max(cut.top,cut.bottom,cut.left,cut.right);
      if(worst>1) out.push({alt:(im.alt||'').slice(0,40), cls:(im.className||'')+'',
        cut, worst:Math.round(worst),
        pct:Math.round(100*worst/Math.max(r.width,r.height))});
    });
  });
  return out;
}"""

async def main():
    async with async_playwright() as pw:
        br=await pw.chromium.launch()
        pg=await br.new_page(viewport={'width':430,'height':932})
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(2000)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1600)
        try: await pg.evaluate("hideInter()")
        except Exception: pass
        seen={}
        for view in ["go('home')","go('deals')","go('store')","go('all')"]:
            await pg.evaluate(view); await pg.wait_for_timeout(700)
            n=await pg.evaluate("document.querySelector('#main').scrollHeight")
            y=0
            while y<n:
                await pg.evaluate("(y)=>document.querySelector('#main').scrollTo(0,y)",y)
                await pg.wait_for_timeout(220)
                for d in await pg.evaluate(PROBE):
                    seen[(d['alt'],d['cls'])]=d
                y+=700
        rows=sorted(seen.values(), key=lambda d:-d['worst'])
        print('\n%d banner pictures are being cut by their card:'%len(rows))
        for d in rows[:30]:
            c=d['cut']
            sides=' '.join('%s%d'%(k[0].upper(),round(v)) for k,v in c.items() if v>1)
            print('  %-42s %-12s cut %3dpx (%d%%)  %s'%(d['alt'],d['cls'],d['worst'],d['pct'],sides))
        await br.close()
asyncio.run(main())
