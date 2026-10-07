#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Everything claimed in this pass, checked by using it."""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

B = __import__('sppath').APP
os.makedirs('/tmp/spv', exist_ok=True)
fails, passes = [], []


def check(name, ok, detail=''):
    (passes if ok else fails).append(name)
    print(('  ok   ' if ok else '  FAIL ') + name + (('  :: ' + str(detail)) if detail and not ok else ''))


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
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

        # ---- the search row hides until asked for ---------------------------
        r = await pg.evaluate("""async () => {
            const row = document.querySelector('.srow');
            const shut = !row.classList.contains('on');
            const h0 = Math.round(row.getBoundingClientRect().height);
            document.querySelector('[data-focussearch]').click();
            await new Promise(r=>setTimeout(r,600));
            const open = row.classList.contains('on');
            const focused = document.activeElement === document.getElementById('q');
            document.querySelector('[data-focussearch]').click();
            await new Promise(r=>setTimeout(r,600));
            return {shut, h0, open, focused, shutAgain: !row.classList.contains('on')} }""")
        check('the search row starts closed', r['shut'] and r['h0'] < 6, r)
        check('the magnifier opens it and puts the cursor in it', r['open'] and r['focused'], r)
        check('and closes it again', r['shutAgain'], r)

        # ---- the shelf pills ------------------------------------------------
        pills = await pg.evaluate("STORE_CONTENT.highlights")
        bad = []
        for p in pills:
            got = await pg.evaluate("""async (label) => {
                go('store'); await new Promise(r=>setTimeout(r,650));
                const b = [...document.querySelectorAll('[data-pill]')]
                            .find(x => x.dataset.pill === label);
                if(!b) return {missing:true};
                b.click(); await new Promise(r=>setTimeout(r,800));
                const cards = document.querySelectorAll('#catGrid .card, #v-search .card').length;
                /* The Love shelf has no grid on purpose: it is an in-store page,
                   so landing on it is a landing even with no cards. */
                const page = !!document.querySelector('#v-cat .lovepage');
                const toast = document.querySelector('#toast');
                return { view: VIEW, cards, page,
                         toast: (toast && toast.classList.contains('on'))
                                ? toast.textContent.replace(/\\s+/g,' ').trim().slice(0,70) : null } }""", p)
            landed = (got.get('cards', 0) > 0) or bool(got.get('toast')) or got.get('page')
            if not landed:
                bad.append(p + ' -> ' + str(got))
        check('every one of the %d shelf pills lands somewhere' % len(pills), not bad, bad)

        # ---- the language switch --------------------------------------------
        r = await pg.evaluate("""async () => {
            go('home'); await new Promise(r=>setTimeout(r,700));
            const en = document.querySelector('#v-home').textContent;
            document.querySelector('#langBtn').click();
            await new Promise(r=>setTimeout(r,1000));
            const es = document.querySelector('#v-home').textContent;
            const tabs = (document.querySelector('#nav')||{}).textContent || '';
            document.querySelector('#langBtn').click();
            await new Promise(r=>setTimeout(r,1000));
            const back = document.querySelector('#v-home').textContent;
            return {changed: en !== es, exact: en === back, tabs,
                    btn: document.querySelector('#langBtn').textContent.trim(),
                    lang: document.documentElement.lang} }""")
        check('pressing ES turns the app Spanish', r['changed'], r)
        check('pressing EN turns it back, exactly', r['exact'], r)
        check('the tab bar translates', 'Tienda' in r['tabs'] and 'Bolsa' in r['tabs'], r['tabs'])

        # a product name must survive both languages untouched
        r = await pg.evaluate("""async () => {
            go('cat','disp'); await new Promise(r=>setTimeout(r,800));
            const name = () => (document.querySelector('#catGrid .card')||{}).textContent||'';
            const en = name();
            setLang('es'); await new Promise(r=>setTimeout(r,1000));
            const es = name();
            setLang('en'); await new Promise(r=>setTimeout(r,900));
            return {en: en.slice(0,60), es: es.slice(0,60)} }""")
        check('a product card reads the same in both languages',
              r['en'] == r['es'], r)

        # ---- the wheel says its days ----------------------------------------
        r = await pg.evaluate("""() => {
            const all = [...DEALCARDS, ...STORE_CONTENT.community]
              .map(x => (x.subtitle || x.d || '')).join(' || ');
            const wheel = all.split('||').filter(t => /spin/i.test(t));
            return {wheel, allSayDays: wheel.length>0 && wheel.every(t=>/monday to wednesday/i.test(t))} }""")
        check('every line about the wheel names Monday to Wednesday',
              r['allSayDays'], r)

        # ---- the events read as five different things -----------------------
        r = await pg.evaluate("""async () => {
            go('home'); await new Promise(r=>setTimeout(r,900));
            /* Stages 120 and 121 rebuilt this section. Five identical text
               blocks (.gitem) became two weekly cards (.ev-card) and the
               annual ones (.ev-flyer, .ev-year), and the single follow link
               lost its .give wrapper and now carries the app's own button
               classes. The check is unchanged in substance: one follow link
               for the whole section, and every event saying something
               different about what it asks of you. */
            const items = [...document.querySelectorAll('.gitem, .ev-card, .ev-flyer, .ev-year')];
            const asks = items.map(i => (i.querySelector('.gask, .ev-when, .ev-ask')||{}).textContent||'');
            const btns = document.querySelectorAll('.give .gbtn, .ev-cta').length;
            return {n: items.length, asks, btns, uniqueAsks: new Set(asks.filter(Boolean)).size} }""")
        check('the events list has one follow link, not one per event',
              r['btns'] == 1, r)
        check('and every event says what it asks of you, differently',
              r['n'] > 0 and r['uniqueAsks'] == r['n'], r)

        # ---- the stock phrases are gone -------------------------------------
        r = await pg.evaluate("""async () => {
            const bad = [];
            for(const v of ['home','deals','store','all']){
              go(v); await new Promise(r=>setTimeout(r,700));
              const t = document.body.textContent;
              ['New-Generation Favorites','Explore the collection'].forEach(p => {
                if(t.indexOf(p) >= 0) bad.push(v + ': ' + p) });
            }
            return bad }""")
        check('no stock ecommerce phrases left on the screens', not r, r)

        # ---- the reviews ask ------------------------------------------------
        r = await pg.evaluate("""async () => {
            go('home'); await new Promise(r=>setTimeout(r,800));
            const acts = document.querySelector('.gr-acts');
            if(!acts) return {missing:true};
            const first = acts.querySelector('a');
            return { first: first.textContent.replace(/\\s+/g,' ').trim(),
                     firstIsButton: first.classList.contains('btn'),
                     hasAsk: !!document.querySelector('.gr-ask') } }""")
        check('"Write a review" is the button, not the afterthought',
              'Write a review' in r.get('first', '') and r.get('firstIsButton'), r)
        check('and it says why', r.get('hasAsk'), r)

        # ---- nothing else moved ---------------------------------------------
        r = await pg.evaluate("""async () => {
            const bad = [];
            for(const c of CATS.map(x=>x[0])){
              go('cat', c); await new Promise(r=>setTimeout(r,240));
              const want = PRODUCTS.filter(p=>p.cat===c).length;
              const n = document.querySelectorAll('#catGrid .card').length;
              if(want > 0 && n !== want) bad.push(c+' '+n+'/'+want);
            }
            return bad }""")
        check('every shelf still paints in full', not r, r)
        check('no page errors', not errs, errs[:3])

        await br.close()
    print('\n%d passed, %d failed' % (len(passes), len(fails)))
    sys.exit(1 if fails else 0)


asyncio.run(main())
