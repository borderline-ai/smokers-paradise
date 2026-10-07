#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does the app recommend things that actually fit?

Marco found a butane lighter recommended on a $125 ELECTRIC nectar collector.
This asserts the domain rules that a person behind the counter knows and a
keyword list does not, across every product in the catalogue.

Each forbidden pair below is a physical fact, not a preference:
an e-rig is heated by its own battery, so fire is not an accessory to it;
a banger replaces the bowl, so it never needs one; a nectar collector has no
joint at all; a disposable is finished and thrown away.
"""
import asyncio
import json
from playwright.async_api import async_playwright

B = __import__('sppath').APP

FORBIDDEN = [
    ('erig', 'torch', 'an e-rig is heated by its battery, not by a flame'),
    ('erig', 'lighter', 'an e-rig is heated by its battery, not by a flame'),
    ('erig', 'bowl', 'an e-rig has no joint for a bowl'),
    ('erig', 'downstem', 'an e-rig has no joint for a downstem'),
    ('erig', 'banger', 'an e-rig heats its own chamber'),
    ('erig', 'carbcap', 'an e-rig caps its own chamber, not a quartz banger'),
    ('straw', 'torch', 'an electric straw needs no flame'),
    ('straw', 'bowl', 'a nectar collector has no joint'),
    ('straw', 'downstem', 'a nectar collector has no joint'),
    ('straw', 'ashcatcher', 'a nectar collector has no joint'),
    ('straw', 'carbcap', 'a nectar collector has no banger to cap'),
    ('onehitter', 'torch', 'a taster is lit with a lighter, not a torch'),
    ('onehitter', 'bowl', 'a one-hitter has no joint'),
    ('onehitter', 'banger', 'a one-hitter is not a dab rig'),
    ('bong', 'coil', 'a bong has no coil'),
    ('bong', 'chamber', 'a bong has no atomizer'),
    ('bong', 'eliquid', 'a bong does not take e-liquid'),
    ('bong', 'hookahbowl', 'a hookah bowl does not fit a water pipe'),
    ('bong', 'charcoal', 'a bong is not a hookah'),
    ('banger', 'bowl', 'a banger IS what replaces the bowl'),
    ('banger', 'downstem', 'a banger is not a stem'),
    ('papers', 'banger', 'papers are not dabbed'),
    ('papers', 'bowl', 'papers have no joint'),
    ('papers', 'airfilter', 'a sploof is not a rolling accessory'),
    ('hookah', 'bowl', 'a hookah takes a hookah bowl'),
    ('poddevice', 'torch', 'a pod device is not heated by a flame'),
    ('poddevice', 'banger', 'a pod device is not a dab rig'),
]

SILENT = ['disposable', 'pouch', 'snack', 'exotic']

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
        await pg.wait_for_timeout(1700)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1700)

        rows = await pg.evaluate("""()=>PRODUCTS.map(p=>{
            const c = companions(p);
            return {t: p.brand+' '+p.name, k: productKind(p), lab: c?c.label:null,
                    it: c ? c.items.map(x=>({t:x.brand+' '+x.name, k:productKind(x),
                                             b:x.brand})) : [],
                    brand: p.brand};
        })""")
        print('  %d products audited\n' % len(rows))

        for a, b, why in FORBIDDEN:
            bad = [(r['t'], i['t']) for r in rows if r['k'] == a
                   for i in r['it'] if i['k'] == b]
            chk(not bad, '%s never gets a %s: %s%s'
                % (a, b, why, '' if not bad else '  <-- ' + json.dumps(bad[:2])))

        for k in SILENT:
            bad = [r['t'] for r in rows
                   if r['k'] == k and r['lab'] and r['lab'] != 'More like this']
            chk(not bad, 'a %s is offered no accessories, only more like it%s'
                % (k, '' if not bad else '  <-- ' + json.dumps(bad[:2])))

        # fitted parts stay inside their own maker
        locked = await pg.evaluate("BRAND_LOCKED")
        bad = [(r['t'], i['t']) for r in rows for i in r['it']
               if i['k'] in locked and i['b'] != r['brand']]
        chk(not bad, 'a chamber, coil, charger or moulded case is only offered '
            'for its own maker%s' % ('' if not bad else '  <-- ' + json.dumps(bad[:2])))

        # and inside their own device line
        bad = await pg.evaluate("""()=>{
          const out=[];
          PRODUCTS.forEach(p=>{
            const c=companions(p); if(!c) return;
            const lp=deviceLine(p); if(!lp) return;
            c.items.forEach(x=>{
              if(BRAND_LOCKED.indexOf(productKind(x))<0) return;
              const lx=deviceLine(x);
              if(lx && lx!==lp) out.push([p.name, x.name]);
            });
          });
          return out}""")
        chk(not bad, 'a Peak Pro is never offered a Proxy part%s'
            % ('' if not bad else '  <-- ' + json.dumps(bad[:2])))

        # the joint size on the label is respected
        bad = await pg.evaluate("""()=>{
          const out=[];
          PRODUCTS.forEach(p=>{
            const c=companions(p); if(!c) return;
            const jp=jointSize(p); if(!jp) return;
            c.items.forEach(x=>{
              if(JOINT_FITTED.indexOf(productKind(x))<0) return;
              const jx=jointSize(x);
              if(jx && jx!==jp) out.push([p.name, x.name]);
            });
          });
          return out}""")
        chk(not bad, 'a 14mm fitting is never offered an 18mm part%s'
            % ('' if not bad else '  <-- ' + json.dumps(bad[:2])))

        # the specific one Marco found
        r = await pg.evaluate("""()=>{
          const p=PRODUCTS.find(x=>/Seahorse Queen/i.test(x.name));
          const c=p?companions(p):null;
          return {kind:p?productKind(p):null, cat:p?p.cat:null,
                  it:c?c.items.map(x=>x.brand+' '+x.name):[]}}""")
        chk(r['kind'] == 'straw' and r['cat'] == 'dab',
            'the electric nectar collector is a dab device, not a glass part')
        chk(not any('lighter' in i.lower() or 'torch' in i.lower() for i in r['it']),
            'and it is offered no flame: %s' % json.dumps(r['it'][:3]))

        chk(not errs, 'no page errors (%s)' % (errs[:2] if errs else 'none'))
        await br.close()

    print('\n%d passed, %d failed' % (ok, fail))
    raise SystemExit(1 if fail else 0)


asyncio.run(main())
