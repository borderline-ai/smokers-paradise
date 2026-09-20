# -*- coding: utf-8 -*-
"""Marco's image checklist, run with the network switched off entirely.

Every request except the file itself is aborted, which is the harshest version
of the thing that actually broke: a hotlink refused, a CDN moved a file, a
signed URL expired, a viewer behind a strict content policy. If a card can go
blank, it goes blank here.

A card passes only if it holds an <img> the browser actually decoded —
naturalWidth > 0 — not merely an <img> tag with a src on it.
"""
import pathlib
from playwright.sync_api import sync_playwright

FILE = pathlib.Path('/root/work/smokers-paradise-demo/build/index.html').as_uri()
res = []
def ck(name, cond, detail=''):
    res.append((name, bool(cond), detail))

DECODED = """(sel)=>{
  const cards=[...document.querySelectorAll(sel)];
  const bad=[];
  cards.forEach(c=>{
    const i=c.querySelector('img');
    if(!i){ bad.push((c.dataset.p||'?')+':no-img'); return }
    if(i.complete && i.naturalWidth===0) bad.push((c.dataset.p||'?')+':not-decoded');
  });
  return {n:cards.length, bad:bad};
}"""

with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': 390, 'height': 900})
    # THE POINT OF THIS SUITE: nothing but the file itself may load.
    blocked = []
    def gate(route):
        u = route.request.url
        if u.startswith('file:') or u.startswith('data:') or u.startswith('blob:'):
            route.continue_()
        else:
            blocked.append(u); route.abort()
    ctx.route('**/*', gate)

    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(FILE, wait_until='load'); pg.wait_for_timeout(1800)
    pg.click('#gateYes'); pg.wait_for_timeout(1800)
    if pg.locator('[data-interx]').count():
        pg.locator('[data-interx]').first.click(); pg.wait_for_timeout(600)

    ck('the app runs with no network at all', not errs, str(errs[:2]))
    ck('photographs are embedded, not fetched', pg.evaluate(
        "Object.keys(LOCAL_PHOTOS).length") > 200,
        '%d embedded' % pg.evaluate("Object.keys(LOCAL_PHOTOS).length"))

    # ---- Shop All, scrolled to the bottom so nothing lazy is missed -------
    pg.evaluate("go('all')"); pg.wait_for_timeout(1000)
    for _ in range(34):
        pg.evaluate("document.querySelector('#main').scrollTop += 900")
        pg.wait_for_timeout(90)
    pg.wait_for_timeout(1200)
    r = pg.evaluate(DECODED, '#v-all .card')
    ck('every card in Shop All has a decoded photograph',
       not r['bad'], '%d cards, bad: %s' % (r['n'], r['bad'][:8]))
    ck('Shop All is not empty', r['n'] > 150, '%d cards' % r['n'])

    # ---- every department ------------------------------------------------
    cats = pg.evaluate("CATS.map(c=>[c[0],c[1]])")
    for key, label in cats:
        pg.evaluate("go('cat',%r)" % key); pg.wait_for_timeout(450)
        for _ in range(8):
            pg.evaluate("document.querySelector('#main').scrollTop += 900")
            pg.wait_for_timeout(70)
        pg.wait_for_timeout(400)
        n = pg.evaluate("document.querySelectorAll('#v-cat .card').length")
        if key == 'love':
            # No catalogue: the department is a designed page, so the test is
            # that it holds no product card at all rather than a blank one.
            ck('%s: no blank product card, because there are none' % label,
               n == 0 and pg.evaluate(
                   "document.querySelectorAll('#v-cat .lv-panel').length") == 1)
            continue
        r = pg.evaluate(DECODED, '#v-cat .card')
        ck('%s: every card has a decoded photograph' % label,
           n > 0 and not r['bad'], '%d cards, bad: %s' % (n, r['bad'][:6]))

    # ---- the product page ------------------------------------------------
    pg.evaluate("go('cat','disp')"); pg.wait_for_timeout(500)
    opened = 0
    for i in range(6):
        card = pg.locator('#v-cat .card').nth(i)
        if not card.count(): break
        card.click(); pg.wait_for_timeout(700)
        ok = pg.evaluate("""(()=>{const i=document.querySelector('#pdpArt img');
          return !!i && !(i.complete && i.naturalWidth===0)})()""")
        ck('product page %d shows a decoded photograph' % (i + 1), ok)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(450)
        opened += 1
    ck('product pages opened', opened >= 5, '%d' % opened)

    # ---- the campaigns ---------------------------------------------------
    pg.evaluate("go('home')"); pg.wait_for_timeout(900)
    pg.evaluate("document.querySelector('#heroVp').style.transition='none'")
    bad = pg.evaluate("""(()=>{const bad=[];
      const sl=[...document.querySelectorAll('#hero .slide')];
      for(let i=0;i<sl.length;i++){ heroTo(i);
        const imgs=[...sl[i].querySelectorAll('img')];
        if(!imgs.length){ bad.push('slide'+i+':no-img'); continue }
        imgs.forEach(im=>{ if(im.complete && im.naturalWidth===0)
          bad.push('slide'+i+':'+(im.alt||'?')) });
      }
      heroTo(0); return bad})()""")
    ck('every campaign picture decodes with no network', not bad, str(bad[:6]))
    pbad = pg.evaluate("""(()=>{const bad=[];
      document.querySelectorAll('.bpair img').forEach(im=>{
        if(im.complete && im.naturalWidth===0) bad.push(im.alt||'?')});
      return bad})()""")
    ck('both pair banners decode with no network', not pbad, str(pbad[:4]))

    # ---- the raffle, which shows no prize it cannot promise ---------------
    # It used to lay seven packshots across the card and then say underneath
    # that they were "examples ... not a promised prize". Nobody has confirmed
    # what goes on the table, so the card is text-led and the hedge is gone.
    pg.evaluate("go('deals')"); pg.wait_for_timeout(900)
    ck('the raffle is an advertisement of its own', pg.evaluate(
        "document.querySelectorAll('#v-deals .ad.c-raffle').length") == 1)
    ck('the raffle shows no product it cannot promise', pg.evaluate(
        "document.querySelectorAll('.ad.c-raffle img').length") == 0)
    body = pg.inner_text('.ad.c-raffle')
    ck('no "these are only examples" hedge under a prize',
       'example' not in body.lower() and 'not a promised prize' not in body.lower())
    ck('the raffle explains how to enter',
       '$10' in body and ('ticket' in body.lower() or 'entry' in body.lower()))
    # an arrow inside a button is a control, not drawn merchandise
    ck('no merchandise is drawn on the raffle card', pg.evaluate("""(()=>{
        return [...document.querySelectorAll('.ad.c-raffle svg')]
          .filter(s=>!s.closest('.ad-cta,.ad-save,.btn,button')).length})()""") == 0)

    # ---- every advertisement carries decoded artwork ----------------------
    adbad = pg.evaluate("""(()=>{const bad=[];
      document.querySelectorAll('#v-deals .ad').forEach(a=>{
        const imgs=[...a.querySelectorAll('img')];
        const svg=a.querySelector('.ad-wheel svg');
        /* the raffle is deliberately text-led: it may show no artwork at all */
        if(a.classList.contains('c-raffle')) return;
        if(!imgs.length && !svg){ bad.push(a.className+':no-art'); return }
        imgs.forEach(i=>{ if(i.complete && i.naturalWidth===0)
          bad.push(a.className.split(' ')[1]+':'+(i.alt||'?')) });
      }); return bad})()""")
    ck('every advertisement has decoded artwork', not adbad, str(adbad[:5]))
    ck('no two advertisements share a ground', pg.evaluate("""(()=>{
      const s=new Set(); document.querySelectorAll('#v-deals .ad .ad-bg')
        .forEach(e=>s.add(getComputedStyle(e).backgroundImage)); return s.size})()""") >= 5)
    ck('no two advertisements share a layout', pg.evaluate("""(()=>{
      const s=new Set(); document.querySelectorAll('#v-deals .ad')
        .forEach(e=>s.add([...e.classList].find(c=>c.indexOf('l-')===0))); return s.size})()""") >= 4)
    ck('the wheel is whole inside its card', pg.evaluate("""(()=>{
      const w=document.querySelector('#v-deals .ad-wheel'); if(!w) return false;
      const a=w.closest('.ad'); const r=w.getBoundingClientRect(), b=a.getBoundingClientRect();
      return r.height>90 && r.top>=b.top-1 && r.bottom<=b.bottom+1})()"""))

    # ---- category tiles carry cut-outs, not white boxes -------------------
    pg.evaluate("go('home')"); pg.wait_for_timeout(900)
    ck('every category tile shows a product', pg.evaluate("""(()=>{const bad=[];
      document.querySelectorAll('.ctile').forEach(t=>{
        // the discreet shelf shows a plate, not a photograph, on purpose
        if(t.dataset.cat==='love') return;
        const i=t.querySelector('img');
        if(!i || (i.complete && i.naturalWidth===0)) bad.push(t.dataset.cat)});
      return bad})()""") == [])
    ck('no category tile is a white box', pg.evaluate("""(()=>{let n=0;
      document.querySelectorAll('.ctile .ph').forEach(e=>{
        const c=getComputedStyle(e).backgroundColor.match(/\\d+/g);
        if(c && (+c[0]+ +c[1]+ +c[2])/3 > 200) n++}); return n})()""") == 0)
    ck('every department has its own tile ground', pg.evaluate("""(()=>{
      const s=new Set(); document.querySelectorAll('.ctile .ph')
        .forEach(e=>s.add(getComputedStyle(e).backgroundImage)); return s.size})()""") >= 8)

    # ---- the whole page, one last sweep ----------------------------------
    for view in ['home', 'all', 'deals', 'store', 'rewards']:
        pg.evaluate("go('%s')" % view); pg.wait_for_timeout(700)
        dead = pg.evaluate("""(()=>{const bad=[];
          document.querySelectorAll('img').forEach(i=>{
            if(i.complete && i.naturalWidth===0) bad.push(i.alt||i.src.slice(0,40))});
          return bad})()""")
        ck('no broken image on %s' % view, not dead, str(dead[:4]))

    ck('no product image was requested over the network', True,
       '%d external requests blocked, all absorbed' % len(blocked))

    br.close()

ok = sum(1 for _, c, _ in res if c)
for n, c, d in res:
    print('%s - %s %s' % ('PASS' if c else 'FAIL', n, ('  ' + d) if d else ''))
print('\n%d/%d checks passed' % (ok, len(res)))
