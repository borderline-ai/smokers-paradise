#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The rewards join, end to end, including the ways it must refuse.

A customer opens Rewards, is offered the programme, fills the form, and comes
back to a card with a code on it. Then the parts that keep it honest: the form
refuses a half-filled join, the card counts only what the counter added, and
nothing the customer can press adds a visit.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

B = __import__('sppath').APP
os.makedirs('/tmp/spm', exist_ok=True)
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
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(700)

        # ---- the programme is offered at all ---------------------------------
        r = await pg.evaluate("""async () => {
            localStorage.removeItem('sp_member_v1');
            go('rewards'); await new Promise(r=>setTimeout(r,700));
            const v = document.querySelector('#v-rewards');
            return {txt: v.innerText,
                    form: !!document.getElementById('mbGo'),
                    fields: ['mbFirst','mbPhone','mbMon','mbDay','mbSms'].filter(i=>document.getElementById(i)),
                    disconnected: /counter/i.test(v.innerText) && !document.getElementById('mbGo')} }""")
        check('Rewards offers a join form instead of a dead end', r['form'], r['txt'][:220])
        check('all four things are asked for', len(r['fields']) == 5, r['fields'])
        check('the rule is stated before the form', 'Paradise Rewards' in r['txt'] and '$10 off' in r['txt'], r['txt'][:220])
        # not a text search: "every year" appears in the perk line. The test is
        # that no control on the form can take a year of birth.
        y = await pg.evaluate("""() => [...document.querySelectorAll('#v-rewards input,#v-rewards select')]
              .map(e => ((e.closest('label')||{}).innerText||'') + ' ' + (e.placeholder||''))
              .filter(t => /year|yyyy|19\\d\\d|birth ?date|date of birth/i.test(t))""")
        check('no control on the form can take a year of birth', not y, y)
        await pg.screenshot(path='/tmp/spm/join.png', full_page=True)

        # ---- it refuses a join it cannot use --------------------------------
        r = await pg.evaluate("""async () => {
            const out = {};
            const fill = async (f, p, tick) => {
                document.getElementById('mbFirst').value = f;
                document.getElementById('mbPhone').value = p;
                document.getElementById('mbSms').checked = tick;
                document.getElementById('mbGo').click();
                await new Promise(r=>setTimeout(r,350));
                return {joined: !!localStorage.getItem('sp_member_v1'),
                        warn: (document.querySelector('#v-rewards .ckwarn')||{}).innerText || ''} };
            out.noname  = await fill('', '5205550134', true);
            out.shortno = await fill('Marco', '520555', true);
            out.noconsent = await fill('Marco', '5205550134', false);
            return out }""")
        for k, label in [('noname', 'a join with no name'),
                         ('shortno', 'a join with half a phone number'),
                         ('noconsent', 'a join with the consent box unticked')]:
            check('%s is refused, and said so' % label,
                  (not r[k]['joined']) and len(r[k]['warn']) > 8, r[k])

        # ---- the join that works ---------------------------------------------
        r = await pg.evaluate("""async () => {
            document.getElementById('mbFirst').value = 'Marco';
            document.getElementById('mbPhone').value = '(520) 555-0134';
            document.getElementById('mbMon').value = '4';
            document.getElementById('mbDay').value = '14';
            document.getElementById('mbSms').checked = true;
            document.getElementById('mbGo').click();
            await new Promise(r=>setTimeout(r,600));
            const d = JSON.parse(localStorage.getItem('sp_member_v1')||'null');
            const q = JSON.parse(localStorage.getItem('sp_member_v1_q')||'[]');
            const v = document.querySelector('#v-rewards');
            const code = (document.querySelector('.mb-code')||{}).innerText || '';
            return {d, q, code, txt: v.innerText,
                    dots: document.querySelectorAll('.mb-dots i').length,
                    lit: document.querySelectorAll('.mb-dots i.on').length,
                    form: !!document.getElementById('mbGo')} }""")
        check('the join is kept and the form is gone', r['d'] and not r['form'], r['d'])
        check('the card shows a code the counter can read', r['code'].startswith('SP') and len(r['code']) == 7, r['code'])
        check('the code on the card is the stored one', r['code'] == (r['d'] or {}).get('code'), r)
        check('the phone number is kept as digits only', (r['d'] or {}).get('phone') == '5205550134', r['d'])
        check('the birthday is month and day, no year', (r['d'] or {}).get('bday') == '4-14', r['d'])
        check('the join is queued for the shop, once', len(r['q']) == 1, r['q'])
        check('a new member starts on zero visits', r['dots'] == 10 and r['lit'] == 0, r)
        check('the card says who adds a visit', 'added by the counter' in r['txt'], r['txt'][:300])
        await pg.screenshot(path='/tmp/spm/card.png', full_page=True)

        # ---- nothing the customer can press adds a visit ----------------------
        r = await pg.evaluate("""async () => {
            const before = Member.progress().total;
            const btns = [...document.querySelectorAll('#v-rewards button')]
              .filter(b => b.id !== 'mbForget');
            for(const b of btns){ b.click(); await new Promise(r=>setTimeout(r,120)) }
            go('rewards'); await new Promise(r=>setTimeout(r,400));
            return {before, after: Member.progress().total, pressed: btns.length} }""")
        check('pressing every control on the card adds no visit',
              r['before'] == r['after'] == 0, r)

        # ---- the counter adds one, and the card follows -----------------------
        r = await pg.evaluate("""async () => {
            for(let i=0;i<10;i++) Member.addVisit();
            go('rewards'); await new Promise(r=>setTimeout(r,500));
            const p = Member.progress();
            return {p, txt: document.querySelector('#v-rewards').innerText,
                    lit: document.querySelectorAll('.mb-dots i.on').length} }""")
        check('ten visits from the counter makes a reward ready', r['p']['ready'] == 1, r['p'])
        check('and the card says so in words', 'reward is ready' in r['txt'].lower(), r['txt'][:300])
        check('the register is named as what applies it', 'register' in r['txt'].lower(), r['txt'][:400])
        await pg.screenshot(path='/tmp/spm/ready.png', full_page=True)

        # ---- the Account row agrees with the card ----------------------------
        r = await pg.evaluate("""async () => {
            go('account'); await new Promise(r=>setTimeout(r,600));
            const row = [...document.querySelectorAll('#v-account .arow')]
              .find(b => b.dataset.go === 'rewards');
            return {found: !!row, txt: row ? row.innerText : '',
                    code: Member.data.code} }""")
        check('Account carries a row for the programme', r['found'], r)
        check('and it shows the member code, not a guess',
              r['found'] and r['code'] in r['txt'], r)

        # ---- leaving is possible, and complete -------------------------------
        r = await pg.evaluate("""async () => {
            go('rewards'); await new Promise(r=>setTimeout(r,500));
            document.getElementById('mbForget').click();
            await new Promise(r=>setTimeout(r,500));
            return {left: !localStorage.getItem('sp_member_v1'),
                    form: !!document.getElementById('mbGo')} }""")
        check('leaving the programme clears it and offers the form again',
              r['left'] and r['form'], r)

        check('no page errors anywhere in the flow', not errs, errs[:3])
        await br.close()

    print('\n%d ok, %d failed' % (len(passes), len(fails)))
    for f in fails:
        print('  FAIL ' + f)
    sys.exit(1 if fails else 0)


asyncio.run(main())
