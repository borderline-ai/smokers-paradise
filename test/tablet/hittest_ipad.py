#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Can a FINGER reach every control, or only element.click()?

This is the test that should have existed before the 546-control walk, and the
reason that walk was green while real buttons were dead on Marco's iPad.

    el.click()          dispatches the event straight at the element and
                        skips hit-testing entirely. It "works" on a control
                        buried under an overlay, behind pointer-events:none,
                        or off the bottom of the screen.

    a real tap          goes to whatever document.elementFromPoint() returns
                        at that coordinate, and nothing else.

So for every visible control on every screen, this asks elementFromPoint what
is actually at its centre. If the answer is not that control or something
inside it, a customer cannot press it, however green the click walk was.

It also counts anything that LOOKS like a control but is not a button or a
link, because the click walk never enumerated those either.
"""
import asyncio
import json
from playwright.async_api import async_playwright

B = __import__('sppath').APP

PROBE = """() => {
  const SEL = 'button, a[href], [role=button], [data-go], [data-cat], [data-p],'
            + '[data-brand], [data-deal], [data-dealgo], [data-tog], [data-pill],'
            + '[data-scrollto], [data-back], [data-sort], [data-oi], [data-q],'
            + '[data-herogo], [data-hero], [data-pair], [data-fav], [data-scr]';
  /* A control behind an OPEN overlay is supposed to be unreachable. Only judge
     what the customer can actually see: if something is covering the screen on
     purpose, judge the things inside it instead. */
  const veils = [...document.querySelectorAll(
    '#gate, #inter, .sheet, #menu, .modal, #pin, #ff, .pop')]
    .filter(v => {
      const c = getComputedStyle(v);
      /* the dismissed age gate keeps its element and its id: what makes an
         overlay an overlay is that it is actually painted over the screen */
      if(c.display === 'none' || c.visibility === 'hidden' || +c.opacity === 0) return false;
      const r = v.getBoundingClientRect();
      return r.width > innerWidth*0.5 && r.height > innerHeight*0.4;
    });
  /* WHICH OVERLAY IS ON TOP is a z-index question, not a document order one.
     With the menu open over a product sheet, the sheet comes later in the DOM
     and was being picked as the scope, so the test then judged the sheet's
     buttons — which the menu is deliberately covering — and called them dead.
     Highest z-index wins, document order breaks the tie. */
  const veil = veils.sort((a, b) => {
    const za = +getComputedStyle(a).zIndex || 0, zb = +getComputedStyle(b).zIndex || 0;
    return za - zb;
  })[veils.length-1] || null;
  const scope = veil || document;
  /* the fixed furniture: everything above it and below it is chrome */
  let SAFE_TOP = 0, SAFE_BOTTOM = innerHeight;
  if(!veil){
    /* THE CHROME IS A STACK, NOT ONE BAR. The header sits at the top, the
       store bar sits UNDER it, the announcement bar under that, and a shelf
       adds a filter bar under that again. Only the first of those has top <= 1,
       so this counted one bar, put SAFE_TOP at its bottom, and then judged
       every card sitting behind the other three as unreachable: 140 findings,
       of which two were real. A control tucked under sticky chrome is not
       broken, it is scrolled — the customer moves the page a centimetre and
       taps it — and a test that cries wolf 138 times is how the two real ones
       get missed.

       So: anything fixed or sticky ANCHORED NEAR THE TOP pushes SAFE_TOP down,
       and anything anchored near the bottom pulls SAFE_BOTTOM up, whatever it
       is called. */
    document.querySelectorAll('*').forEach(f => {
      const c = getComputedStyle(f);
      if(c.position !== 'fixed' && c.position !== 'sticky') return;
      if(c.display === 'none' || c.visibility === 'hidden' || +c.opacity === 0) return;
      const q = f.getBoundingClientRect();
      if(q.height < 4 || q.width < innerWidth * 0.5) return;
      if(q.top <= innerHeight * 0.35) SAFE_TOP = Math.max(SAFE_TOP, q.bottom);
      else if(q.bottom >= innerHeight * 0.65) SAFE_BOTTOM = Math.min(SAFE_BOTTOM, q.top);
    });
  }
  const out = [];
  scope.querySelectorAll(SEL).forEach(el => {
    if(el.disabled) return;
    const cs = getComputedStyle(el);
    if(cs.visibility === 'hidden' || cs.display === 'none') return;
    if(el.offsetParent === null && cs.position !== 'fixed') return;
    const r = el.getBoundingClientRect();
    if(r.width < 4 || r.height < 4) return;
    /* Only judge what is in the clear. A control tucked under the sticky
       header or behind the bottom bar is not broken, it is scrolled: the
       customer moves the page a centimetre and taps it. Judge the band
       between the fixed chrome. */
    if(r.top < SAFE_TOP || r.bottom > SAFE_BOTTOM) return;
    if(r.right < 1 || r.left > innerWidth-1) return;
    const cx = Math.round(r.left + r.width/2);
    const cy = Math.round(r.top + r.height/2);
    /* CLAMPING THE PROBE POINT INVENTED FAULTS. A chip row is a horizontal
       rail: the fourth brand filter and the last sort sit off to the right
       until you push the rail sideways, which is what a rail is for. Their
       centres are past the edge of the screen, and clamping the probe to the
       screen edge asked elementFromPoint about a coordinate that is not on the
       control at all — so the rail's own background answered, and every shelf
       in the app reported two dead buttons that a finger reaches by sliding
       the row. Same for a control whose centre is outside the scroller it
       lives in. Neither is broken; both are scrolled. */
    if(cx < 1 || cx > innerWidth-2 || cy < 1 || cy > innerHeight-2) return;
    let sc = el.parentElement, clipped = false;
    while(sc && sc !== document.body){
      const c = getComputedStyle(sc);
      if(/(auto|scroll|hidden)/.test(c.overflowX + ' ' + c.overflowY + ' ' + c.overflow)){
        const q = sc.getBoundingClientRect();
        if(cx < q.left || cx > q.right || cy < q.top || cy > q.bottom){ clipped = true; break }
      }
      sc = sc.parentElement;
    }
    if(clipped) return;
    const hit = document.elementFromPoint(cx, cy);
    if(!hit) { out.push({el, cause:'nothing at its own centre'}); return }
    /* Reached only if the point lands ON it or on something INSIDE it.
       "the hit element contains this one" is NOT reachable: an ancestor
       answering for its own child is the exact signature of the child being
       transparent to touch, which is what pointer-events:none does. */
    if(hit === el || el.contains(hit)) return;
    let near = null;
    try { near = hit.closest(SEL) } catch(e) {}
    if(near === el) return;
    let blocker = hit.tagName.toLowerCase()
                + (hit.id ? '#'+hit.id : '')
                + (hit.className ? '.'+String(hit.className).split(' ')[0] : '');
    let cause = 'covered by ' + blocker;
    let p = el, chain = [];
    while(p && p !== document.body){
      if(getComputedStyle(p).pointerEvents === 'none'){
        chain.push(p.tagName.toLowerCase()
                  + (p.id ? '#'+p.id : '')
                  + (p.className ? '.'+String(p.className).split(' ')[0] : ''));
      }
      p = p.parentElement;
    }
    if(chain.length) cause = 'pointer-events:none on ' + chain.join(' < ');
    out.push({el, cause});
  });
  /* dressed as a control, but not one: the click walk never even saw these */
  const fake = [];
  scope.querySelectorAll('span, div, li, figure').forEach(el => {
    if(el.children.length) return;
    if(el.closest(SEL)) return;
    if(getComputedStyle(el).cursor !== 'pointer') return;
    if(el.offsetParent === null) return;
    const t = (el.textContent||'').replace(/\\s+/g,' ').trim();
    if(t) fake.push(t.slice(0,34));
  });
  return {
    dead: out.map(o => ({
      label: (o.el.getAttribute('aria-label') || o.el.textContent || '')
             .replace(/\\s+/g,' ').trim().slice(0,38),
      tag: o.el.tagName.toLowerCase(),
      data: JSON.stringify(o.el.dataset || {}).slice(0,44),
      cause: o.cause })),
    fake: [...new Set(fake)],
    veil: veil ? (veil.id || veil.className) : null
  };
}"""


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 820, 'height': 1180}, is_mobile=True, has_touch=True)
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1700)

        found = []

        async def sweep(name):
            r = await pg.evaluate(PROBE)
            for d in r['dead']:
                d['screen'] = name
                found.append(d)
            if r['fake']:
                print('  %-22s LOOKS CLICKABLE BUT IS NOT A CONTROL: %s'
                      % (name, json.dumps(r['fake'][:4], ensure_ascii=False)))

        await sweep('age gate')
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1800)
        await sweep('entrance offer')
        await pg.evaluate("hideInter()")

        cats = await pg.evaluate("CATS.map(c=>c[0])")
        screens = ([('home', "go('home')"), ('deals', "go('deals')"),
                    ('store', "go('store')"), ('all', "go('all')"),
                    ('bag empty', "go('orders')"), ('account', "go('account')")]
                   + [('shelf:' + c, "go('cat','%s')" % c) for c in cats])

        for name, setup in screens:
            await pg.evaluate(setup)
            await pg.wait_for_timeout(750)
            # every control the screen has, not just the ones above the fold
            n = await pg.evaluate("document.querySelector('#main').scrollHeight")
            y = 0
            while y < n:
                await pg.evaluate("(y)=>document.querySelector('#main').scrollTo(0,y)", y)
                await pg.wait_for_timeout(230)
                await sweep(name)
                y += 700
            await pg.evaluate("document.querySelector('#main').scrollTo(0,0)")

        # the overlays
        await pg.evaluate("go('all')")
        await pg.wait_for_timeout(700)
        await pg.evaluate("""()=>{const c=document.querySelector('.view.on .card'); if(c) c.click()}""")
        await pg.wait_for_timeout(1200)
        await sweep('product page')
        await pg.evaluate("openSearchRow && openSearchRow()")
        await pg.wait_for_timeout(600)
        await sweep('search open')
        await pg.evaluate("""()=>{const m=document.querySelector('#menu'); if(m) m.classList.add('on')}""")
        await pg.wait_for_timeout(600)
        await sweep('menu open')

        seen, uniq = set(), []
        for f in found:
            k = (f['screen'], f['label'], f['cause'])
            if k in seen:
                continue
            seen.add(k)
            uniq.append(f)

        print('\n%d controls a finger cannot reach:' % len(uniq))
        for f in uniq:
            print('  %-14s %-38s %-8s %s'
                  % (f['screen'], f['label'][:38], f['tag'], f['cause'][:70]))
        await br.close()
    raise SystemExit(1 if uniq else 0)


asyncio.run(main())
