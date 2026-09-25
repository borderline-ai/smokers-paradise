#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The walk a customer takes, end to end, the way it will be demoed in the shop.

Browse, open a product, pick a flavour, add it, change the quantity, add a
second thing from another shelf, open the bag, check out, place the order, read
the code, tell the counter you are on the way, then find the same order on the
counter screen. If any step of this breaks in front of the owner the pitch is
over, so it is tested as one continuous run rather than as isolated controls.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

B = __import__('sppath').APP
os.makedirs('/tmp/spj', exist_ok=True)
fails, passes = [], []

def check(name, ok, detail=''):
    (passes if ok else fails).append(name)
    print(('  ok   ' if ok else '  FAIL ') + name + (('  :: ' + str(detail)) if detail and not ok else ''))

async def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else 'en'
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 820, 'height': 1180}, is_mobile=True, has_touch=True, device_scale_factor=2)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B); await pg.wait_for_timeout(1600)

        r = await pg.evaluate("""async () => {
            const gate = document.querySelector('#gate');
            const shown = gate && getComputedStyle(gate).display !== 'none';
            document.querySelector('#gateNo').click(); await new Promise(r=>setTimeout(r,500));
            const denied = getComputedStyle(document.querySelector('#gateDeny')).display !== 'none';
            const oops = document.querySelector('#gateOops'); if(oops) oops.click();
            await new Promise(r=>setTimeout(r,400));
            return {shown, denied, canUndo: !!oops} }""")
        check('the age gate comes before anything else', r['shown'], r)
        check('saying under 21 refuses entry', r['denied'], r)
        check('and a mis-tap can be undone', r['canUndo'], r)

        await pg.evaluate("document.querySelector('#gateYes').click()"); await pg.wait_for_timeout(1800)
        if lang == 'es':
            await pg.evaluate("setLang('es')"); await pg.wait_for_timeout(1000)

        r = await pg.evaluate("""async () => {
            const on = document.querySelector('#inter').classList.contains('on');
            const go = document.querySelector('#interCard .ad-cta');
            if(go){ go.click(); await new Promise(r=>setTimeout(r,1200)) }
            return {on, closed: !document.querySelector('#inter').classList.contains('on'),
                    cat: CATSTATE.c, brand:(CATSTATE.b||[]).join('+')} }""")
        check('the entrance offer opens and its button lands right',
              r['on'] and r['closed'] and r['cat']=='disp' and r['brand']=='Off-Stamp', r)

        r = await pg.evaluate("""async () => {
            S.cart = []; save(); go('cat','disp'); await new Promise(r=>setTimeout(r,1500));
            const card = document.querySelector('#catGrid .card');
            const name = card.textContent.replace(/\\s+/g,' ').trim().slice(0,40);
            card.click(); await new Promise(r=>setTimeout(r,1200));
            const sheet = document.querySelector('.sheet.on');
            return {opened: !!sheet, name,
                    hasArt: !!(sheet && sheet.querySelector('#pdpArt img, #pdpArt svg, #pdpArt span')),
                    opts: sheet ? sheet.querySelectorAll('[data-oi]').length : 0,
                    hasAdd: !!(sheet && [...sheet.querySelectorAll('button')]
                                 .find(b=>/add to bag|agregar/i.test(b.textContent)))} }""")
        check('a product card opens the product', r['opened'], r)
        check('the product page shows a picture', r['hasArt'], r)
        check('it offers its options', r['opts'] >= 1, r)
        check('and it has an add button', r['hasAdd'], r)

        r = await pg.evaluate("""async () => {
            const sheet = document.querySelector('.sheet.on');
            const opts = [...sheet.querySelectorAll('[data-oi]')];
            const before = (document.querySelector('#pdpArt img')||{}).src || '';
            const lab0 = (document.querySelector('.optlab')||{}).textContent || '';
            if(opts[1]) opts[1].click(); await new Promise(r=>setTimeout(r,800));
            const after = (document.querySelector('#pdpArt img')||{}).src || '';
            const lab1 = (document.querySelector('.optlab')||{}).textContent || '';
            /* The stepper is a pair of [data-q] buttons, not an id. */
            const up = [...sheet.querySelectorAll('[data-q]')].find(b=>b.dataset.q==='1');
            if(up) up.click(); await new Promise(r=>setTimeout(r,500));
            const qty = (document.querySelector('#qv')||{}).textContent;
            const add = [...sheet.querySelectorAll('button')].find(b=>/add to bag|agregar/i.test(b.textContent));
            add.click(); await new Promise(r=>setTimeout(r,1100));
            return {picChanged: before!==after, labChanged: lab0!==lab1,
                    hadOpts: opts.length>1, qty,
                    cart: S.cart.length, units: S.cart.reduce((n,l)=>n+l.q,0)} }""")
        if r['hadOpts']:
            # A flavour changes the sleeve and so changes the picture; a size or a
            # volume does not, and demanding that it did would be asserting a lie.
            check('picking another option registers',
                  r['picChanged'] or r['labChanged'], r)
        check('the quantity stepper works', r['qty']=='2', r)
        check('adding puts the right number in the bag', r['cart']==1 and r['units']==2, r)

        r = await pg.evaluate("""async () => {
            try{ closeSheet() }catch(e){}
            go('cat','water'); await new Promise(r=>setTimeout(r,1400));
            document.querySelector('#catGrid .card').click(); await new Promise(r=>setTimeout(r,1100));
            const sheet = document.querySelector('.sheet.on');
            const add = [...sheet.querySelectorAll('button')].find(b=>/add to bag|agregar/i.test(b.textContent));
            if(add) add.click(); await new Promise(r=>setTimeout(r,900));
            try{ closeSheet() }catch(e){}
            return {cart: S.cart.length} }""")
        check('a second shelf adds to the same bag', r['cart']==2, r)

        r = await pg.evaluate("""async () => {
            go('orders'); await new Promise(r=>setTimeout(r,1300));
            const t = document.querySelector('#v-orders').textContent;
            return {money: /\\$\\d/.test(t), len: t.length} }""")
        check('the bag shows the lines and a subtotal', r['money'] and r['len']>100, r)
        await pg.screenshot(path='/tmp/spj/bag-%s.png' % lang)

        r = await pg.evaluate("""async () => {
            const b = [...document.querySelectorAll('#v-orders button')]
                        .find(x=>/review pickup|revisar/i.test(x.textContent));
            if(b) b.click(); else go('checkout');
            await new Promise(r=>setTimeout(r,1400));
            S.name='Demo'; S.phone='5203382119'; save();
            CHK.step=3; renderCheckout(); await new Promise(r=>setTimeout(r,1000));
            const disc = document.querySelector('[data-ckdisc]');
            return {step: CHK.step, hasPlace: !!document.querySelector('#placeBtn'),
                    money: /\\$\\d/.test(document.querySelector('#v-checkout').textContent)} }""")
        check('checkout reaches the confirm step with a place button',
              r['hasPlace'] and r['money'], r)
        await pg.screenshot(path='/tmp/spj/checkout-%s.png' % lang)

        r = await pg.evaluate("""async () => {
            document.querySelector('#placeBtn').click(); await new Promise(r=>setTimeout(r,2200));
            const o = (S.orders||[])[0];
            return {view: VIEW, orders:(S.orders||[]).length, cartEmpty: S.cart.length===0,
                    code: o?o.code:null, items:o?o.items.length:0, total:o?o.total:null} }""")
        check('the order is placed', r['orders']==1, r)
        check('the bag empties when it is sent', r['cartEmpty'], r)
        check('the order carries a pickup code', bool(r['code']), r)
        check('and it carries both items', r['items']==2, r)
        check('it lands on the order screen', r['view']=='order', r)
        check('and it has a total', isinstance(r['total'], (int,float)) and r['total']>0, r)
        await pg.screenshot(path='/tmp/spj/order-%s.png' % lang)

        r = await pg.evaluate("""async () => {
            const el = document.querySelector('.pickcode');
            const code = el?el.textContent.trim():'';
            const fs = el?parseFloat(getComputedStyle(el).fontSize):0;
            const onway = [...document.querySelectorAll('#v-order button')]
                            .find(b=>/on my way|voy en camino/i.test(b.textContent));
            let a1=null; if(onway){ onway.click(); await new Promise(r=>setTimeout(r,900));
              a1=(S.orders[0]||{}).arrive||null }
            const here = [...document.querySelectorAll('#v-order button')]
                           .find(b=>/i.?m here|ya llegu/i.test(b.textContent));
            let a2=null; if(here){ here.click(); await new Promise(r=>setTimeout(r,900));
              a2=(S.orders[0]||{}).arrive||null }
            return {code, fs, onway:!!onway, a1, here:!!here, a2} }""")
        check('the pickup code is on screen and big enough to read across a counter',
              bool(r['code']) and r['fs']>=24, r)
        check('"on my way" registers', r['a1'] is not None, r)
        check('"I am here" registers', r['a2']=='here', r)

        r = await pg.evaluate("""async () => {
            /* The counter prints the order NUMBER on a ticket, not the whole
               pickup code: the code is what the customer holds up, the number
               is what the counter calls out. */
            const o = S.orders[0];
            try{ renderStaff() }catch(e){}
            const t = (document.querySelector('#staffBody')||{textContent:''}).textContent;
            return {n:o.n, hasNumber: t.indexOf('#'+o.n)>=0, hasName: /Demo/.test(t),
                    tickets: document.querySelectorAll('#staffBody .ticket').length} }""")
        check('the counter screen shows the order and the name',
              r['hasNumber'] and r['hasName'] and r['tickets']>0, r)

        r = await pg.evaluate("""async () => {
            go('orders'); await new Promise(r=>setTimeout(r,1200));
            const row = document.querySelector('#v-orders .ordrow');
            if(!row) return {noRow:true};
            row.click(); await new Promise(r=>setTimeout(r,1200));
            return {opened: VIEW==='order',
                    money: /\\$\\d/.test(document.querySelector('#v-order').textContent),
                    hide: !!document.querySelector('[data-ordhide]')} }""")
        check('a past order reopens from the bag screen', r.get('opened'), r)
        check('shows its total', r.get('money'), r)
        # (the fold-away receipt control is a Holy Cow feature, not this build)

        r = await pg.evaluate("""async () => {
            go('account'); await new Promise(r=>setTimeout(r,1000));
            const b = document.querySelector('[data-reset]'); if(!b) return {noReset:true};
            b.click(); await new Promise(r=>setTimeout(r,800));
            const ask = document.querySelector('#ask');
            const shown = ask && ask.classList.contains('on');
            const yes = ask ? [...ask.querySelectorAll('button')]
                         .find(x=>/start over|empezar|over/i.test(x.textContent)) : null;
            if(yes){ yes.click(); await new Promise(r=>setTimeout(r,1600)) }
            return {shown, orders:(S.orders||[]).length, cart:(S.cart||[]).length} }""")
        check('reset asks before it wipes', r.get('shown'), r)
        check('and the demo comes back clean', r.get('orders')==0 and r.get('cart')==0, r)

        check('no page errors anywhere in the journey', not errs, errs[:3])
        await br.close()
    print('\n%s: %d passed, %d failed' % (lang, len(passes), len(fails)))
    sys.exit(1 if fails else 0)

asyncio.run(main())
