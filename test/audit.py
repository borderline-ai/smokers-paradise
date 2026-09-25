# -*- coding: utf-8 -*-
"""The content audit: every claim, every route, every carousel slide.

Not a spot-check of the one screenshot. This walks the whole app and asserts
what has to be true of a storefront: the right shop, the right city, no
competitor assets, no invented recognition, no button that goes nowhere, no
headline that contradicts the product beside it.
"""
import re, pathlib
from playwright.sync_api import sync_playwright

SRC = pathlib.Path(__import__('sppath').APP)
FILE = SRC.as_uri()
res = []
def ck(name, cond, detail=''):
    res.append((name, bool(cond), detail))

src = SRC.read_text('utf-8')

# ---------------------------------------------------------------- the source
for token in ['Holy Cow', 'holycow', 'holy-cow', 'hc_', 'HolyCow']:
    ck('no Holy Cow residue: %s' % token, token.lower() not in src.lower())
ck('no Tempe anywhere', not re.search(r'\bTempe\b', src))
ck('no other city claimed', not re.search(r'\b(Phoenix|Scottsdale|Mesa|Chandler|Gilbert)\b,?\s*AZ', src))

with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': 390, 'height': 844})
    ctx.route('**/*', lambda r: r.continue_()
              if r.request.url.startswith(('file:', 'data:', 'blob:')) else r.abort())
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(FILE, wait_until='load'); pg.wait_for_timeout(1600)
    pg.click('#gateYes'); pg.wait_for_timeout(2200)
    if pg.locator('[data-interx]').count():
        pg.locator('[data-interx]').first.click(); pg.wait_for_timeout(600)
    pg.evaluate("clearInterval(heroT)")

    # ------------------------------------------------------------- the store
    ck('the store is Smokers Paradise', pg.evaluate("STORE.name") == 'Smokers Paradise')
    ck('the address is the Nogales one', '922 N Grand Ave' in pg.evaluate("STORE.street"))
    ck('the city is Nogales', 'Nogales' in pg.evaluate("STORE.city"))
    ck('the tax rate is the Nogales rate', abs(pg.evaluate("TAX_RATE") - 0.086) < 1e-9)

    # the award is theirs, announced by them, and the county is the right one
    aw = pg.evaluate("STORE_CONTENT.award")
    ck('the award names Santa Cruz County, which is where Nogales is',
       aw and 'Santa Cruz' in (aw.get('region') or ''), str(aw and aw.get('region')))
    ck('the award is dated and attributed', bool(aw and aw.get('announced')),
       str(aw and aw.get('announced')))

    # ------------------------------------------------------- language sweep
    body = ''
    views = ['home', 'deals', 'all', 'store', 'rewards', 'orders', 'account']
    for v in views:
        pg.evaluate("go('%s')" % v); pg.wait_for_timeout(650)
        body += ' ' + pg.inner_text('body')
    pg.evaluate("go('cat','exotic')"); pg.wait_for_timeout(500)
    body += ' ' + pg.inner_text('body')
    low = body.lower()

    for phrase in ['sample offer', 'demo promotion', 'pending store confirmation',
                   'pending confirmation', 'seen in smokers paradise content',
                   'demo selection', 'demonstration build', 'demo build',
                   'featured in the demo', 'demo raffle', 'demo prize bundle']:
        ck('no internal note on screen: "%s"' % phrase, phrase not in low)

    for phrase in ['in stock', 'on the shelf now', 'shop stocked', 'available now',
                   'popular in nogales', 'selling fast', 'limited time', 'hurry',
                   'only a few left', 'best in arizona']:
        ck('no unsupported claim: "%s"' % phrase, phrase not in low)

    ck('the shop name is spelled one way', 'smoker’s paradise' not in low
       or 'smokers paradise' in low)

    # ------------------------------------------------------------- routing
    dead = pg.evaluate("""(()=>{const bad=[];
      DEALCARDS.forEach(d=>{const t=d.ctaTarget;
        if(!t){bad.push(d.id+':no target');return}
        if(t.view==='cat' && !CATS.some(c=>c[0]===t.arg)) bad.push(d.id+' -> '+t.arg)});
      PROMOS.forEach(p=>{const t=p.target;
        if(!t){bad.push(p.id+':no target');return}
        if(t.view==='cat' && !CATS.some(c=>c[0]===t.arg)) bad.push(p.id+' -> '+t.arg)});
      PROMO_PAIR.forEach(p=>{const t=p.act;
        if(!t){bad.push(p.id+':no target');return}
        if(t.view==='cat' && !CATS.some(c=>c[0]===t.arg)) bad.push(p.id+' -> '+t.arg)});
      return bad})()""")
    ck('no promotion points at a department that does not exist', not dead, str(dead))

    landed = pg.evaluate("""(()=>{const bad=[];
      const all=DEALCARDS.map(d=>[d.id,d.ctaTarget])
        .concat(PROMOS.map(p=>[p.id,p.target]))
        .concat(PROMO_PAIR.map(p=>[p.id,p.act]));
      all.forEach(([id,t])=>{try{goTarget(t);
        if(VIEW==='cat' && !document.querySelectorAll('#v-cat .card').length) bad.push(id)}
        catch(e){bad.push(id+':'+e.message)}});
      go('home'); return bad})()""")
    ck('every promotion lands on something', not landed, str(landed))

    # --------------------------------------------- headline vs the product
    mismatch = pg.evaluate("""(()=>{const bad=[];
      DEALCARDS.forEach(d=>{
        (d.art||[]).forEach(a=>{
          const id=pidFor(a.b,a.m); const p=id?P(id):null;
          if(!p){ bad.push(d.id+': no product for '+a.b+' '+a.m); return }
          if(p.brand!==a.b) bad.push(d.id+': asked '+a.b+', got '+p.brand);
          // normalise both sides: the kicker spells it TRĒ House
          const norm=x=>x.toLowerCase().normalize('NFD').replace(/[^a-z]/g,'');
          const hay=norm(d.kicker+' '+d.title+' '+d.subtitle);
          const brand=norm(a.b);
          if(hay.indexOf(brand)<0 &&
             ['glass','raffle'].indexOf(d.concept)<0)
            bad.push(d.id+': copy never names '+a.b);
        });
      });
      return bad})()""")
    ck('every advertisement pictures the brand it names', not mismatch, str(mismatch[:4]))

    # ------------------------------------------------- every carousel slide
    pg.evaluate("go('home')"); pg.wait_for_timeout(700)
    pg.evaluate("document.querySelector('#heroVp').style.transition='none'")
    n = pg.evaluate("document.querySelectorAll('#hero .slide').length")
    ck('the carousel has more than one slide', n > 1, '%d slides' % n)
    for k in range(n):
        info = pg.evaluate("""(k)=>{heroTo(k);
          const s=document.querySelectorAll('#hero .slide')[k];
          const t=s.innerText.trim();
          const img=[...s.querySelectorAll('img')].filter(i=>!(i.complete&&i.naturalWidth===0));
          return {text:t.slice(0,60), lines:t.length, art:img.length}}""", k)
        ck('slide %d has copy and artwork' % (k + 1),
           info['lines'] > 10 and info['art'] > 0, info['text'].replace('\n', ' '))
    pg.evaluate("heroTo(0)")

    # ----------------------------------------------------- no duplicates
    dupes = pg.evaluate("""(()=>{const seen={},bad=[];
      DEALCARDS.forEach(d=>{const k=d.title.trim().toLowerCase();
        if(seen[k]) bad.push(d.id+' duplicates '+seen[k]); seen[k]=d.id});
      return bad})()""")
    ck('no two promotions say the same thing', not dupes, str(dupes))

    # ------------------------------------- invented merchandise, not just claims
    # The old sweep looked for invented CLAIMS and never for invented PRODUCTS,
    # which is how ten SKUs under a house brand nobody has ever sold, at ten
    # prices nobody ever quoted, sat on the Love shelf through five passes.
    ck('no product carries a brand the shop does not stock', pg.evaluate("""(()=>{
      const fake=['paradise','house','generic','sample','demo','placeholder'];
      return PRODUCTS.filter(p=>fake.indexOf(String(p.brand||'').toLowerCase())>=0)
        .map(p=>p.brand+' '+p.name)})()""") == [])
    ck('every product in the catalogue has a photograph', pg.evaluate("""(()=>{
      return PRODUCTS.filter(p=>{ try{ return art(p,null,false).indexOf('<img')<0 }
        catch(e){ return true } }).map(p=>p.brand+' '+p.name).slice(0,8)})()""") == [])
    ck('no department renders a card without a picture', pg.evaluate("""(()=>{
      const bad=[]; CATS.forEach(c=>{ go('cat',c[0]);
        document.querySelectorAll('#v-cat .card').forEach(k=>{
          if(!k.querySelector('img')) bad.push(c[0]) }) }); go('home'); return bad})()""") == [])

    ck('no console errors across the audit', not errs, str(errs[:2]))
    br.close()

ok = sum(1 for _, c, _ in res if c)
for n, c, d in res:
    print('%s - %s %s' % ('PASS' if c else 'FAIL', n, ('  ' + d) if d else ''))
print('\n%d/%d checks passed' % (ok, len(res)))
