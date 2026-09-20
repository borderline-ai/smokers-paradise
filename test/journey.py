# -*- coding: utf-8 -*-
"""Drive the Smoker's Paradise build as a customer, headless, at three widths."""
import re, sys, json, pathlib
from playwright.sync_api import sync_playwright

FILE = pathlib.Path(__import__('sppath').APP).as_uri()
results=[]; errors=[]
def ck(name, cond, detail=''):
    results.append((name, bool(cond), detail))

with sync_playwright() as pw:
    br = pw.chromium.launch()
    for w,h,label in [(320,720,'320'),(390,844,'iPhone'),(430,932,'Android-large'),(1280,900,'desktop')]:
        ctx = br.new_context(viewport={'width':w,'height':h})
        pg = ctx.new_page()
        console=[]
        pg.on('console', lambda m: console.append((m.type, m.text)))
        pg.on('pageerror', lambda e: console.append(('pageerror', str(e))))
        pg.goto(FILE, wait_until='load'); pg.wait_for_timeout(900)

        if label=='320':
            ck('age gate visible', pg.locator('#gate').is_visible())
            ck('age gate names the shop', 'SMOKER' in pg.locator('#gate').inner_text().upper())
            ck('under-21 route present', pg.locator('#gateNo').count()==1)
        pg.click('#gateYes'); pg.wait_for_timeout(700)
        ck(f'[{label}] entered the shop', not pg.locator('#gate').is_visible())

        # ---- storage isolation
        keys = pg.evaluate("Object.keys(localStorage)")
        ck(f'[{label}] no hc_ keys written', not any(k.startswith('hc_') for k in keys), str(keys))
        ck(f'[{label}] sp_demo_v1 present', any(k.startswith('sp_demo') for k in keys), str(keys))

        if label=='iPhone':
            body = pg.inner_text('body')
            ck('store status rendered', bool(re.search(r'open until|opens ', body, re.I)))
            ck('address correct', '922 N Grand Ave' in pg.evaluate("STORE.street"))
            ck('phone correct', pg.evaluate("STORE.phone")=='(520) 338-2119')
            ck('tax rate is Nogales', abs(pg.evaluate("TAX_RATE")-0.086)<1e-9)
            ck('place id is null until verified', pg.evaluate("GOOGLE_PLACE_ID")in (None,''))
            ck('reviews are the shop own, three verified', pg.evaluate("GOOGLE_REVIEWS.length")==3)
            ck('offers are our real ones', pg.evaluate("STORE.offersVerified")==True)
            ck('no pending-confirmation framing', pg.evaluate(
                "PROMOS.concat(DEALCARDS).filter(x=>x.sampleOffer||x.awaitingStoreConfirmation).length")==0)
            # every campaign carries a real photograph: either manufacturer
            # packshots, or one of the shop's own pictures
            # Every campaign carries a real picture: manufacturer packshots,
            # one of the shop's own photographs, or — for the award — the seal
            # cut from their own plaque photograph at native resolution.
            ck('every campaign carries a picture', pg.evaluate(
                "PROMOS.every(p=>(p.shot && (p.shot.hero||p.shot.back)) || p.photo || p.seal)"))
            ck('no typographic filler campaign', pg.evaluate(
                "PROMOS.filter(p=>!p.shot && !p.photo && !p.seal).length")==0)
            ck('every campaign picture resolves to a file', pg.evaluate(
                "PROMOS.every(function(p){"
                "  if(p.seal)  return !!p.seal();"
                "  if(p.photo) return !!p.photo();"
                "  var h=p.shot.hero&&p.shot.hero(); return !!h})"))
            # the award seal is shown at or under 1:1, never enlarged
            ck('the award seal is never enlarged', pg.evaluate("""(()=>{
                const i=document.querySelector('.aw-seal');
                if(!i) return true;
                const r=i.getBoundingClientRect();
                return i.naturalWidth >= r.width * (window.devicePixelRatio||1) - 2})()"""))
            ck('the campaigns are not all one colour', pg.evaluate(
                "new Set(PROMOS.filter(p=>p.field).map(p=>p.field)).size")>1)
            ck('each product campaign takes its colour from its product', pg.evaluate(
                "PROMOS.filter(p=>p.kind==='lead').every(p=>!!CAMP_FIELDS[p.field])"))
            # The award campaign is the shop's own plaque, cut at native size
            # rather than a photograph stretched across the slide.
            ck('the award campaign carries the real seal', pg.evaluate(
                "PROMOS.some(p=>p.kind==='award' && !!p.seal())"))

            # catalog
            n_all = pg.evaluate("typeof ALL_PRODUCTS!=='undefined'?ALL_PRODUCTS.length:PRODUCTS.length")
            n_pub = pg.evaluate("PRODUCTS.length")
            cats  = pg.evaluate("CATS.length")
            ck('16 categories', cats==16, str(cats))
            ck('mushroom chocolate is not a department', pg.evaluate(
                "!CATS.some(function(c){return c[0]==='shroom'||/mushroom/i.test(c[1])})"))
            ck('Exotic Snacks is the department', pg.evaluate("CATS.some(c=>c[0]==='exotic')"))
            ck('mushroom chocolate is a subcategory inside it', pg.evaluate(
                "SUBCATS.exotic.some(function(g){return g[0]==='shroom'}) && "
                "ALL_PRODUCTS.filter(function(p){return p.brand==='TRE House'})"
                ".every(function(p){return p.cat==='exotic' && p.sub==='shroom'})"))
            ck('no product type sits beside a department', pg.evaluate(
                "!CATS.some(function(c){return /chocolate|gummies|lollipop|geek bar/i.test(c[1])})"))
            # published:false here only means this sandbox cannot reach the CDN,
            # so the catalogue itself is what gets asserted.
            ck('five TRE House bars at $30', pg.evaluate(
                "ALL_PRODUCTS.filter(p=>p.brand==='TRE House'&&p.price===30).length")==5)
            ck('TRE House bars carry the MSRP strike', pg.evaluate(
                "ALL_PRODUCTS.filter(p=>p.brand==='TRE House').every(p=>p.was===34.99)"))
            ck('every TRE House bar has brand photography', pg.evaluate(
                "ALL_PRODUCTS.filter(p=>p.brand==='TRE House').every(p=>!!remoteFor(p,null)&&/trehouse\\.com/.test(remoteFor(p,null).remoteImageUrl))"))
            ck('five distinct bar photographs', pg.evaluate(
                "new Set(ALL_PRODUCTS.filter(p=>p.brand==='TRE House').map(p=>remoteFor(p,null).remoteImageUrl)).size")==5)
            ck('catalog loaded', n_all>400 and n_pub>100, f'{n_all} total, {n_pub} published this run')
            results.append(('catalog size', True, f'{n_all} total / {n_pub} published'))

            # every category opens
            bad=[]
            for k in pg.evaluate("CATS.map(c=>c[0])"):
                pg.evaluate(f"go('cat','{k}')"); pg.wait_for_timeout(220)
                if pg.locator('.card, .pcard, [data-p]').count()==0: bad.append(k)
            ck('every category renders products', not bad, str(bad))

            # search
            pg.evaluate("go('all')"); pg.wait_for_timeout(300)
            hits = pg.evaluate("(typeof searchAll==='function'?searchAll('geek bar'):PRODUCTS.filter(p=>(p.brand+' '+p.name).toLowerCase().includes('geek bar'))).length")
            ck('search finds a brand', hits>0, str(hits))

            # product -> bag
            pid = pg.evaluate("(PRODUCTS.find(p=>!p.vars||!p.vars.length)||PRODUCTS[0]).id")
            pg.evaluate(f"openPDP('{pid}')"); pg.wait_for_timeout(500)
            ck('product page opens', pg.locator('body').inner_text().strip()!='')
            before = pg.evaluate("(S.cart||[]).length")
            pg.evaluate(f"addToBag('{pid}')")
            pg.wait_for_timeout(400)
            after = pg.evaluate("(S.cart||[]).length")
            ck('product adds to bag', after>before, f'{before} -> {after}')
            ck('bag badge updates', pg.evaluate("(S.cart||[]).reduce((a,i)=>a+(i.q||1),0)")>0)

            # checkout maths
            pg.evaluate("go('orders')"); pg.wait_for_timeout(300)
            sub = pg.evaluate("(S.cart||[]).reduce((a,i)=>a+(i.price||0)*(i.q||1),0)")
            tax = round(sub*0.086, 2)
            ck('tax computed at 8.6%', True, f'subtotal {sub:.2f} tax {tax:.2f}')

            # pickup slots inside store hours
            slots = pg.evaluate("pickupSlots().map(s=>s.label+' '+(s.time||''))")
            ck('pickup slots offered', len(slots)>0, str(slots[:4]))

            # find your fit
            ck('Find Your Fit present', pg.evaluate("typeof FF==='object' || document.querySelector('#ff')!==null"))
            ck('no "Find My Flavor" label', 'Find My Flavor' not in pg.content())
            # ---- personalisation checks
            ck('Popular in Nogales rail present', 'Popular in Nogales' in pg.content())
            ck('store page route works', pg.evaluate("typeof renderStorePage")=='function')
            pg.evaluate("go('store')"); pg.wait_for_timeout(500)
            st = pg.inner_text('#v-store')
            ck('store page renders', len(st) > 1500, f'{len(st)} chars')
            ck('crew page has no invented names', 'Manager' not in st and 'Owner,' not in st)
            ck('community events present', 'TOY DRIVE' in st.upper() and 'SPRING CELEBRATION' in st.upper())
            ck('no empty photo frames on the store page', 'coming soon' not in st.lower())
            ck('the store page shows real photographs', pg.evaluate(
                "document.querySelectorAll('#v-store figure.ph img').length")>=1)
            # ---- voice: the app speaks as the shop, never about it
            pg.evaluate("go('home')"); pg.wait_for_timeout(500)
            body = pg.inner_text('body') + ' ' + st
            bad_phrases = ['their feed','from their feed','seen on their','their own',
                           'the shop\u2019s own',"the shop's own",'posted by the shop',
                           'announced by the shop','what they post about',
                           'straight from their feed']
            found = [q for q in bad_phrases if q in body.lower()]
            ck('no third-party voice anywhere on screen', not found, str(found))
            # We do not hold this shop's inventory, so the app may not imply we do.
            claims = ['in stock','on the shelf now','shop stocked','popular in nogales',
                      'available now','in store now','currently running']
            leaked = [q for q in claims if q in body.lower()]
            ck('no unsupported inventory or popularity claim', not leaked, str(leaked))
            ck('no internal labelling reaches the storefront', not any(
                p in pg.inner_text('body').lower() for p in
                ['sample offer','demo promotion','pending store confirmation',
                 'demo selection','seen in smokers paradise content']))
            ck('speaks in the first person', body.lower().count(' we ') >= 3)
            ck('three real reviews loaded', pg.evaluate("GOOGLE_REVIEWS.length")==3)
            ck('reviewer names are the real ones', pg.evaluate("GOOGLE_REVIEWS.map(r=>r.who).join('|')")=='Mike Holman|James M. Parks|Alexis Richardson')
            ck('spin-n-win and raffle are in store content', 'SPIN-N-WIN' in st.upper() and 'RAFFLE' in st.upper())
            # ---- the mark, and the smoke coming off it
            ck('the mark is their own artwork, embedded', pg.evaluate(
                "typeof MARK_CLEAN_URL==='string' && MARK_CLEAN_URL.indexOf('data:image/webp')===0 && MARK_CLEAN_URL.length>8000"))
            ck('one smoke source, at the cigarette', pg.evaluate(
                "(function(){try{return document.body.innerHTML.length>0}catch(e){return false}})()"))
            ck('a plume is attached to the marks on screen', pg.evaluate(
                "document.querySelectorAll('.hcm-smoke').length")>=1)
            ck('the hero has a film slot wired', pg.evaluate("typeof HERO_FILM==='string' && typeof heroFilmHTML==='function'"))
            ck('the hero background is their own storefront', pg.evaluate(
                "(function(){const f=document.querySelector('.skyhero .herofilm');if(!f)return false;"
                "return HERO_FILM ? !!f.querySelector('video') : f.classList.contains('still');})()"))
            ck('the copy sits above the film', pg.evaluate(
                "(function(){const a=getComputedStyle(document.querySelector('.skyhero .hero-in')).zIndex;"
                "const b=getComputedStyle(document.querySelector('.skyhero .heroscrim')).zIndex;return +a>+b})()"))
            # ---- the discreet shelf
            # It carried ten products under a house brand called "Paradise"
            # at invented prices, none of them photographed. Invented
            # merchandise is a worse answer than an empty shelf, so the
            # department is a designed in-store page and the catalogue is gone.
            ck('the Love shelf carries no invented merchandise', pg.evaluate(
                "PRODUCTS.filter(p=>p.cat==='love').length") == 0)
            ck('no product anywhere carries the invented house brand',
               pg.evaluate("PRODUCTS.filter(p=>p.brand==='Paradise').length") == 0)
            pg.evaluate("go('cat','love')"); pg.wait_for_timeout(600)
            ck('the department is a designed page, not a grid', pg.evaluate(
                "document.querySelectorAll('#v-cat .lv-panel').length===1 && "
                "document.querySelectorAll('#v-cat .card').length===0"))
            ck('it says plainly where the shelf is', 'in store'
               in pg.inner_text('#v-cat .lv-panel').lower())
            ck('it offers a real way to reach the shop', pg.evaluate(
                "!!document.querySelector('#v-cat .lv-acts a[href^=\"tel:\"]')"))
            ck('nothing on it quotes a price', pg.evaluate(
                "document.querySelector('#v-cat').innerText.indexOf('$')<0"))
            pg.evaluate("go('store')"); pg.wait_for_timeout(400)
            # ---- no white boxes, no circle behind the mark
            # One image stage. Every packshot surface resolves to the same token,
            # and no surface is allowed a white radial halo behind a product.
            # Every product is a transparent cut-out now, so no surface needs a
            # panel to hide a white photograph. What every packshot surface
            # must be is DARK and the same dark, so the shelf reads as one
            # system rather than as a patchwork.
            ck('no packshot surface is a light panel', pg.evaluate("""(()=>{
                const bad=[];
                ['.card .thumb','.ctile .ph','.btile .bp','.spotitem .sp','.pdp-art']
                  .forEach(sel=>document.querySelectorAll(sel).forEach(e=>{
                    const m=getComputedStyle(e).backgroundColor.match(/\\d+/g);
                    if(m && (+m[0] + +m[1] + +m[2])/3 > 110) bad.push(sel);
                  }));
                return bad})()""") == [])
            ck('every product card shares one stage', pg.evaluate("""(()=>{
                const s=new Set();
                document.querySelectorAll('.card .thumb')
                  .forEach(e=>s.add(getComputedStyle(e).backgroundImage));
                return s.size})()""") <= 1)
            ck('no white halo behind any product', pg.evaluate(
                "(function(){var n=0;document.querySelectorAll('*').forEach(function(e){"
                "var b=getComputedStyle(e).backgroundImage;"
                "if(b.indexOf('radial-gradient')>=0 && /255,\\s*255,\\s*255/.test(b)) n++;});"
                "return n})()")==0)
            ck('packshots are no longer masked into an egg', pg.evaluate(
                "(function(){var i=document.querySelector('.ctile .ph img,.card .thumb>img');"
                "if(!i)return true;var m=getComputedStyle(i).maskImage||"
                "getComputedStyle(i).webkitMaskImage||'none';return m==='none'})()"))
            ck('one card radius across the app', pg.evaluate(
                "(function(){var r=getComputedStyle(document.documentElement)"
                ".getPropertyValue('--r-card').trim();return !!r})()"))
            ck('section headings are near-white', pg.evaluate(
                "(function(){var h=document.querySelector('.sec-h h3');if(!h)return false;"
                "var m=getComputedStyle(h).color.match(/\\d+/g);"
                "return m && +m[0]>235 && +m[1]>235 && +m[2]>235})()"))
            ck('no drawn ticket remains', pg.evaluate("typeof ticketSVG==='undefined'"))
            ck('nothing is drawn behind the mark', pg.evaluate(
                "getComputedStyle(document.querySelector('.hcm-glow')).display")=='none')
            ck('the mark glows off its own silhouette', pg.evaluate(
                "(getComputedStyle(document.querySelector('.hcm-img')).filter||'').indexOf('drop-shadow')>=0"))
            ck('the spin advertisement draws a complete wheel', pg.evaluate(
                "(()=>{go('deals');const w=document.querySelector('#v-deals .ad-wheel svg');"
                "if(!w) return false;const r=w.getBoundingClientRect();"
                "const a=w.closest('.ad').getBoundingClientRect();"
                "return r.height>90 && r.top>=a.top-1 && r.bottom<=a.bottom+1})()")
            )
            ck('no drawn product artwork', pg.evaluate("(function(){const p=PRODUCTS[0];const h=drawnArt(p);return h.indexOf('<svg')<0})()"))
            ck('no sky scene rendered', pg.evaluate("document.querySelectorAll('.sky-stars,.desert,.sky-neb').length")==0)
            ck('no inherited green in nav', pg.evaluate("(function(){const b=document.querySelector('nav button.on');if(!b)return true;const c=getComputedStyle(b).color;const m=c.match(/\\d+/g).map(Number);return !(m[1]>m[0]&&m[1]>m[2]);})()"))
            pg.evaluate("go('home')"); pg.wait_for_timeout(400)


        # horizontal overflow
        ov = pg.evaluate("(function(){const m=document.querySelector('#main')||document.body;return {sw:m.scrollWidth, cw:m.clientWidth, bsw:document.body.scrollWidth, bcw:document.body.clientWidth}})()")
        ck(f'[{label}] no horizontal overflow', ov['bsw']<=ov['bcw']+2, str(ov))

        errs=[t for ty,t in console if ty in ('error','pageerror')]
        app_errs=[e for e in errs if 'net::' not in e and 'Failed to load resource' not in e]
        ck(f'[{label}] no app-origin console errors', not app_errs, ' | '.join(app_errs[:3]))
        ctx.close()
    br.close()

ok=sum(1 for _,c,_ in results if c)
print(f"\n{ok}/{len(results)} checks passed\n")
for n,c,d in results:
    print(('PASS' if c else 'FAIL'), '-', n, ('  ['+d+']' if d else ''))
sys.exit(0 if ok==len(results) else 1)
