#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What stages 85 to 88 claim to have fixed, asserted against the built file.

Each check is written so that the old behaviour fails it. A test that passes
against both the bug and the fix is not a test.
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

B = __import__('sppath').APP
ok = fail = 0


def chk(cond, msg):
    global ok, fail
    if cond:
        ok += 1
        print('  ok  ', msg)
    else:
        fail += 1
        print('  FAIL', msg)


async def main():
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
        await pg.evaluate("hideInter(); go('home')")
        await pg.wait_for_timeout(1200)

        # ---- 85: the featured rail is named for what is in it ----------------
        r = await pg.evaluate("""()=>{
          const secs=[...document.querySelectorAll('#v-home .sec')];
          const s=secs.find(x=>{const h=x.querySelector('h3');
            return h && /Shop Our Brands/.test(h.textContent)});
          if(!s) return null;
          /* Stage 128 rebuilt this as a strip of brand chips instead of a rail
             of product cards, because nine product cards cost 449 pixels to
             say nine brand names. The check is unchanged in substance: the
             home page must still name every brand the shop leads with. */
          const br=[...s.querySelectorAll('.card .br, .bstrip b')].map(e=>e.textContent.trim());
          return {n:br.length, brands:[...new Set(br)]}}""")
        chk(r is not None, 'the featured-brand rail is on the home screen')
        want = await pg.evaluate("STORE_CONTENT.featuredBrands.length")
        chk(r and len(r['brands']) == want,
            'and it shows all %d brands the shop leads with, not the first four'
            % want)
        heads = await pg.evaluate("""()=>[...document.querySelectorAll('#v-home .sec h3')]
            .map(h=>h.textContent.trim())""")
        chk(heads.count('Mushroom Chocolate') == 0,
            'the vape rail is no longer titled Mushroom Chocolate')
        chk(len(heads) == len(set(heads)), 'no two sections on home share a heading')

        # ---- 85: no rail is one brand over and over -------------------------
        worst = await pg.evaluate("""()=>{
          let worst={h:'',share:0};
          document.querySelectorAll('#v-home .sec').forEach(s=>{
            const br=[...s.querySelectorAll('.card .br')].map(e=>e.textContent.trim());
            if(br.length<6) return;
            const c={}; br.forEach(b=>c[b]=(c[b]||0)+1);
            const top=Math.max(...Object.values(c))/br.length;
            if(top>worst.share) worst={h:(s.querySelector('h3')||{}).textContent||'', share:top};
          });
          return worst}""")
        chk(worst['share'] <= 0.75,
            'no rail of six or more is mostly one brand (worst: %s at %d%%)'
            % (worst['h'].strip()[:28], round(worst['share'] * 100)))

        # ---- 86: nothing on a banner is sliced by its own card --------------
        clip = await pg.evaluate("""async ()=>{
          clearInterval(heroT);
          const bad=[];
          for(let i=0;i<PROMOS.length;i++){
            heroTo(i); clearInterval(heroT);
            await new Promise(r=>setTimeout(r,700));
          }
          document.querySelectorAll('.camp').forEach(c=>{
            const cr=c.getBoundingClientRect(); if(cr.width<20) return;
            c.querySelectorAll('.camp-shot img').forEach(im=>{
              const r=im.getBoundingClientRect();
              const over=Math.max(cr.left-r.left, r.right-cr.right,
                                  cr.top-r.top, r.bottom-cr.bottom);
              if(over>0.5) bad.push({id:c.dataset.promo||c.dataset.pair,
                                     cls:im.className, over:Math.round(over)});
            });
          });
          return bad}""")
        chk(not clip, 'no product on any banner is cut by the card edge (%s)'
            % (json.dumps(clip)[:90] if clip else 'all clear'))

        # ---- 86: every nicotine slide carries its 21+ line ------------------
        fine = await pg.evaluate("""()=>PROMOS.filter(p=>p.kind==='lead')
            .map(p=>({id:p.id, fine:p.disclaimer||''}))""")
        chk(all(f['fine'] for f in fine),
            'every product slide in the carousel carries a 21+ line (%d of %d)'
            % (sum(1 for f in fine if f['fine']), len(fine)))

        # ---- 88: the language layer translates a sentence that wraps --------
        await pg.evaluate("go('all')")
        await pg.wait_for_timeout(900)
        before = await pg.evaluate("""()=>{
          const w=document.createTreeWalker(document.querySelector('.view.on'),
                  NodeFilter.SHOW_TEXT); const o=[]; let n;
          while(n=w.nextNode()) o.push(n.nodeValue); return o}""")
        await pg.evaluate("setLang('es')")
        await pg.wait_for_timeout(1400)
        nic = await pg.evaluate("""()=>document.body.innerText""")
        chk('sustancia adictiva' in nic,
            'the nicotine notice, written over two lines, now appears in Spanish')
        chk('Nicotine is an addictive chemical' not in nic,
            'and its English is gone from the screen')

        # ---- 88: and the round trip is exact --------------------------------
        await pg.evaluate("setLang('en')")
        await pg.wait_for_timeout(1400)
        after = await pg.evaluate("""()=>{
          const w=document.createTreeWalker(document.querySelector('.view.on'),
                  NodeFilter.SHOW_TEXT); const o=[]; let n;
          while(n=w.nextNode()) o.push(n.nodeValue); return o}""")
        chk(before == after,
            'English -> Spanish -> English puts every text node back exactly')

        # ---- 87 + 88: no em dash in a sentence a customer reads -------------
        prose = await pg.evaluate("""()=>{
          const out=[];
          const w=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          let n;
          while(n=w.nextNode()){
            const p=n.parentElement;
            if(!p || p.tagName==='SCRIPT' || p.tagName==='STYLE') continue;
            const s=(n.nodeValue||'').replace(/\\s+/g,' ').trim();
            /* a lone dash standing in for a missing number is typography,
               not prose; anything with words either side of it is prose */
            if(/\\S\\s*\\u2014\\s*\\S/.test(s)) out.push(s.slice(0,70));
          }
          return out}""")
        chk(not prose, 'no em dash inside a sentence on screen (%s)'
            % (json.dumps(prose, ensure_ascii=False)[:100] if prose else 'clean'))

        # ---- 87: the shop is open on Sunday, everywhere ---------------------
        src = open(B, encoding='utf-8').read()
        closes = await pg.evaluate("""async ()=>{
          const bad=[];
          for(const go_ of [()=>go('home'),()=>go('store'),()=>go('all'),
                            ()=>go('account'),()=>go('deals')]){
            go_(); await new Promise(r=>setTimeout(r,700));
            document.body.innerText.split('\\n').forEach(l=>{
              /* a line that names Saturday as the last day it opens, without
                 naming Sunday in the same breath */
              if(/Monday through Saturday|Mon(day)? to Sat(urday)?\\./.test(l)
                 && !/Sunday|Sundays/.test(l)) bad.push(l.trim().slice(0,70));
            });
          }
          return [...new Set(bad)]}""")
        chk(not closes, 'no screen says the shop closes after Saturday (%s)'
            % (json.dumps(closes)[:90] if closes else 'clean'))

        # ---- 87: the footer does not claim a confirmation nobody gave -------
        chk('Prices and selection are confirmed with the shop' not in src,
            'the account footer no longer claims prices were confirmed')

        chk(not errs, 'no page errors (%s)' % (errs[:2] if errs else 'none'))
        await br.close()

    print('\n%d passed, %d failed' % (ok, fail))
    raise SystemExit(1 if fail else 0)


asyncio.run(main())
