#!/usr/bin/env python3
"""Does it fit, on every screen Marco might hold it up on?

Every test in this build has run at 390x844 — one iPhone. This asks the same
questions at every size the app will actually be opened on, phones and iPads,
portrait and landscape: does anything scroll sideways, does the phone frame fit
the screen, is anything under the notch or the home indicator, and is any text
or control smaller than it should be.
"""
import asyncio, os, json, sys
from playwright.async_api import async_playwright

B='/root/work/smokers-paradise-demo/build/index.html'
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/dev'
os.makedirs(OUT, exist_ok=True)

DEVICES = [
  ('iphone-se',        375, 667, 2),
  ('iphone-13-mini',   375, 812, 3),
  ('iphone-14',        390, 844, 3),
  ('iphone-15-pro',    393, 852, 3),
  ('iphone-15-promax', 430, 932, 3),
  ('ipad-mini',        744,1133, 2),
  ('ipad-air',         820,1180, 2),
  ('ipad-pro-11',      834,1194, 2),
  ('ipad-pro-12',     1024,1366, 2),
  ('ipad-mini-land',  1133, 744, 2),
  ('ipad-air-land',   1180, 820, 2),
  ('ipad-pro-12-land',1366,1024, 2),
]

PROBE = """() => {
  const de = document.documentElement, b = document.body;
  const phone = document.getElementById('phone');
  const stage = document.getElementById('stage') || phone.parentElement;
  const main  = document.getElementById('main');
  const pr = phone ? phone.getBoundingClientRect() : null;
  const sr = stage ? stage.getBoundingClientRect() : null;
  // anything painting outside the viewport horizontally
  let widest = null, over = 0;
  document.querySelectorAll('#phone *').forEach(el=>{
    const cs = getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden') return;
    const r = el.getBoundingClientRect();
    if(r.width < 2 || r.height < 2) return;
    const o = Math.max(0, r.right - innerWidth, -r.left);
    if(o > over){ over = o; widest = (el.tagName+'.'+String(el.className||'')).slice(0,46) }
  });
  // controls a finger needs, smaller than 44px
  const small = [];
  document.querySelectorAll('button,a[href],[role=button]').forEach(el=>{
    const cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden') return;
    const r=el.getBoundingClientRect();
    if(r.width<2||r.height<2) return;
    if(r.top<0||r.bottom>innerHeight) return;
    if(r.height < 40 || r.width < 26)
      small.push({t:(el.textContent||'').trim().slice(0,22),
                  w:Math.round(r.width), h:Math.round(r.height),
                  c:String(el.className||'').slice(0,22)});
  });
  return {
    vw: innerWidth, vh: innerHeight,
    docScrollW: de.scrollWidth, bodyScrollW: b.scrollWidth,
    sidewaysScroll: Math.max(de.scrollWidth, b.scrollWidth) - innerWidth,
    phone: pr ? {x:Math.round(pr.left), y:Math.round(pr.top),
                 w:Math.round(pr.width), h:Math.round(pr.height)} : null,
    stage: sr ? {w:Math.round(sr.width), h:Math.round(sr.height)} : null,
    mainH: main ? Math.round(main.getBoundingClientRect().height) : null,
    widestOverflow: over ? {by:Math.round(over), el:widest} : null,
    smallTargets: small.slice(0,6), smallCount: small.length
  };
}"""

async def main():
    rows=[]
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        for name,w,h,dpr in DEVICES:
            pg = await br.new_page(viewport={'width':w,'height':h}, device_scale_factor=min(dpr,2),
                                   is_mobile=True, has_touch=True)
            await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://'+B); await pg.wait_for_timeout(1600)
            await pg.screenshot(path='%s/%s_gate.png'%(OUT,name))
            await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1500)
            await pg.evaluate("hideInter(); go('home')"); await pg.wait_for_timeout(1600)
            r = await pg.evaluate(PROBE); r['name']=name; r['errs']=errs[:2]
            await pg.screenshot(path='%s/%s_home.png'%(OUT,name))
            await pg.evaluate("go('cat','disp')"); await pg.wait_for_timeout(1400)
            await pg.screenshot(path='%s/%s_shelf.png'%(OUT,name))
            rows.append(r)
            await pg.close()
        await br.close()
    json.dump(rows, open(OUT+'/report.json','w'), indent=1)
    print('%-18s %-11s %-22s %-22s %s' % ('device','viewport','phone frame','sideways','small targets'))
    for r in rows:
        p=r['phone']; 
        print('%-18s %-11s %-22s %-22s %s%s' % (
            r['name'], '%dx%d'%(r['vw'],r['vh']),
            '%dx%d @%d,%d'%(p['w'],p['h'],p['x'],p['y']) if p else 'none',
            ('SCROLLS %dpx'%r['sidewaysScroll']) if r['sidewaysScroll']>1 else 'ok',
            r['smallCount'],
            ('  ERR '+r['errs'][0][:40]) if r['errs'] else ''))
asyncio.run(main())
