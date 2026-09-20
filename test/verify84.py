import asyncio, json, sys
import os
from playwright.async_api import async_playwright
B=__import__('sppath').APP
fails=[];passes=[]
def check(n,ok,d=''):
    (passes if ok else fails).append(n)
    print(('  ok   ' if ok else '  FAIL ')+n+(('  :: '+str(d)) if d and not ok else ''))
async def m():
    async with async_playwright() as pw:
        br=await pw.chromium.launch(); pg=await br.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://'+B); await pg.wait_for_timeout(1600)
        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter()")
        # DERIVED FROM THE SLIDES, NOT HARD-CODED. This used to name five
        # products by hand, which meant it kept asserting that a product still
        # on the list had a banner cut long after that slide had been changed —
        # and in stage 163 it failed for the right reason in the wrong
        # direction: the two Geek Bar banner cuts were DELETED because they
        # were sliced, and the test wanted them back. What matters is not which
        # products are named here, it is that whatever a slide shows resolves
        # to a picture.
        r=await pg.evaluate("""()=>PROMOS.filter(p=>p.shot).flatMap(p=>
             ['hero','back'].filter(k=>p.shot[k]).map(k=>({id:p.id, slot:k,
               alt:p.shot[k+'Alt']||'',
               got:!!(p.shot[k]()||'')}))) """)
        check('every product a slide shows resolves to a picture',
              all(x['got'] for x in r), [x for x in r if not x['got']] or len(r))
        # A slide may lead on a single photograph rather than a lead-and-back
        # pair: the "New mods just landed" slide is one group shot of five
        # devices and has no back product at all. The rule is that every image
        # a slide DOES carry is one the shop ships, not that every slide
        # carries two of them.
        #
        # This used to read "embedded in this file", and until stage 172 that
        # was the same sentence: every photograph was base64 inside the
        # document, so "starts with data:" WAS "we ship it". Stage 172 took
        # 6.8 MB of photographs out into app/img/ and the two came apart — the
        # test went red while the property it cares about was still true.
        #
        # The property it cares about is rule 2 in CLAUDE.md: every product
        # picture is a real photograph the shop holds, never a hotlink to a
        # manufacturer CDN or a temporary Instagram URL that will rot. So that
        # is what is asserted now, and it is checked harder than before —
        # "data: or a local file" AND the file is actually on disk. A path to
        # a photograph that does not exist used to be impossible and is now
        # merely wrong, which is exactly the kind of thing a test is for.
        r=await pg.evaluate("""()=>PROMOS.filter(p=>p.shot).map(p=>({id:p.id,
             hero: p.shot.hero? (p.shot.hero()||'') : null,
             back: p.shot.back? (p.shot.back()||'') : null}))""")
        appdir = os.path.dirname(__import__('sppath').APP)

        def ships(v):
            if v is None or v == '':
                return v is None
            if v.startswith('data:image'):
                return True
            if v.startswith('img/'):
                return os.path.exists(os.path.join(appdir, v))
            return False          # anything remote is a hotlink, and is refused

        bad = [x for x in r if not (ships(x['hero']) and ships(x['back']))]
        check('every image a slide carries is one the shop ships, and it is there',
              not bad and any(x['hero'] for x in r),
              bad or [dict(x, hero=(x['hero'] or '')[:40]) for x in r])
        r=await pg.evaluate("""async ()=>{
          go('account'); await new Promise(r=>setTimeout(r,1000));
          const out=[];
          document.querySelectorAll('[data-tog]').forEach(b=>out.push({
            k:b.dataset.tog, role:b.getAttribute('role'),
            label:b.getAttribute('aria-label'), checked:b.getAttribute('aria-checked')}));
          return out }""")
        check('both switches announce a name, a role and their state',
              len(r)==2 and all(x['role']=='switch' and x['label'] and x['checked'] in ('true','false') for x in r), r)
        r=await pg.evaluate("""async ()=>{
          go('account'); await new Promise(r=>setTimeout(r,800));
          const q=()=>document.querySelector('[data-tog="sms"]');
          const a=q().getAttribute('aria-checked'); q().click();
          await new Promise(r=>setTimeout(r,600));
          const b=q().getAttribute('aria-checked'); q().click();
          await new Promise(r=>setTimeout(r,500));
          return {a,b,back:q().getAttribute('aria-checked')} }""")
        check('and the state they announce follows the switch', r['a']!=r['b'] and r['a']==r['back'], r)
        r=await pg.evaluate("""async ()=>{
          go('cat','exotic'); await new Promise(r=>setTimeout(r,1200));
          const t=document.querySelector('#v-cat').textContent;
          return {macron: t.indexOf('TR\\u0112 House')>=0, plain: /TRE House/.test(t)} }""")
        check('the cards print TRĒ House', r['macron'] and not r['plain'], r)
        r=await pg.evaluate("""()=>({keysIntact: !!REMOTE['TRE House|Mushroom Chocolate, Peanut Butter|*'],
                                     art: DEALCARDS.some(d=>(d.art||[]).some(a=>a.b==='TRE House'))})""")
        check('and the catalogue key is untouched', r['keysIntact'] and r['art'], r)
        # every image, network dead, after a full walk
        bad=[]
        for v,setup in [('home',"go('home')"),('all',"go('all')"),('disp',"go('cat','disp')"),
                        ('deals',"go('deals')"),('store',"go('store')"),('exotic',"go('cat','exotic')")]:
            await pg.evaluate(setup); await pg.wait_for_timeout(900)
            await pg.evaluate("""async ()=>{ const m=document.querySelector('#main');
              for(let y=0;y<m.scrollHeight;y+=420){m.scrollTop=y; await new Promise(r=>setTimeout(r,140))}
              for(const r of document.querySelectorAll('.rail,.spotrow,.feedrow,.brandgrid,.cattiles,.gr-strip')){
                for(let x=0;x<r.scrollWidth;x+=260){ r.scrollLeft=x; await new Promise(t=>setTimeout(t,80)) } r.scrollLeft=0 }
              document.querySelectorAll('img[loading="lazy"]').forEach(i=>i.loading='eager');
              m.scrollTop=0; await new Promise(r=>setTimeout(r,500)) }""")
            await pg.wait_for_timeout(3000)
            n=await pg.evaluate("""()=>{let b=0; document.querySelectorAll('.view.on img').forEach(i=>{if(i.naturalWidth<=2)b++}); return b}""")
            if n: bad.append('%s:%d' % (v,n))
        check('not one broken image anywhere, with the network dead', not bad, bad)
        check('no page errors', not errs, errs[:3])
        await br.close()
    print('\n%d passed, %d failed' % (len(passes), len(fails)))
    sys.exit(1 if fails else 0)
asyncio.run(m())
