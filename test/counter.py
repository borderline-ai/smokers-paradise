#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The counter's half of the rewards programme.

A customer joins on the phone, shows a code, and the counter adds the visit.
Then the parts that keep it honest: a wrong code finds nobody, the count the
counter sees is the count the customer sees, a reward comes off once, and the
rule the owner types is the rule the customer's screen states.
"""
import asyncio, os, sys
from playwright.async_api import async_playwright

B = '/root/work/smokers-paradise-demo/build/index.html'
os.makedirs('/tmp/spc', exist_ok=True)
fails, passes = [], []


def check(name, ok, detail=''):
    (passes if ok else fails).append(name)
    print(('  ok   ' if ok else '  FAIL ') + name + (('  :: ' + str(detail)) if detail and not ok else ''))


OPEN_STAFF = ("const st = document.querySelector('#staff');"
              "if(!st.classList.contains('on')) st.classList.add('on');"
              "STAB = 'rw'; renderStaff();"
              "await new Promise(r=>setTimeout(r,400));")


def staff(body, *a):
    """Open the counter screen on the Rewards tab, then run body."""
    return 'async () => {' + OPEN_STAFF + (body % a if a else body) + '}'


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 834, 'height': 1112}, device_scale_factor=2)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1600)
        await pg.evaluate("""() => {localStorage.removeItem('sp_member_v1');
            localStorage.removeItem('sp_rewards_cfg_v1');
            document.querySelector('#gateYes').click()}""")
        await pg.wait_for_timeout(700)

        # ---- the tab exists and the rule is editable -------------------------
        r = await pg.evaluate(staff("""
            return {tab: !!document.getElementById('srwCode'),
                    tabs: [...document.querySelectorAll('[data-stab]')].map(b=>b.dataset.stab),
                    fields: ['srwName','srwN','srwGift','srwPerk','srwEnd'].filter(i=>document.getElementById(i)),
                    txt: document.querySelector('#staffBody').innerText} """))
        check('the counter screen has a Rewards tab', 'rw' in r['tabs'], r['tabs'])
        check('with a box for the code the customer shows', r['tab'], r)
        check('the rule is on the same screen, and editable', len(r['fields']) == 5, r['fields'])
        check('the demo says what it can and cannot look up',
              'no server' in r['txt'], r['txt'][:300])
        await pg.screenshot(path='/tmp/spc/tab.png', full_page=True)

        # ---- a code with no member behind it finds nobody --------------------
        r = await pg.evaluate("""async () => {
            document.getElementById('srwCode').value = 'SP00000';
            document.getElementById('srwFind').click();
            await new Promise(r=>setTimeout(r,350));
            return {warn: (document.querySelector('#staffBody .ckwarn')||{}).innerText||'',
                    hit: !!document.querySelector('.srw-hit'),
                    add: !!document.getElementById('srwAdd')} }""")
        check('a code with no member behind it finds nobody',
              not r['hit'] and not r['add'] and len(r['warn']) > 8, r)

        # ---- a customer joins on the phone -----------------------------------
        r = await pg.evaluate("""async () => {
            document.querySelector('#staff').classList.remove('on');
            go('rewards'); await new Promise(r=>setTimeout(r,600));
            mbFirst.value='Marco'; mbPhone.value='5205550134'; mbMon.value='4'; mbDay.value='14';
            mbGo.click(); await new Promise(r=>setTimeout(r,500));
            return {code: Member.data.code} }""")
        code = r['code']
        check('the customer has a code to show', code.startswith('SP'), code)

        # ---- the counter finds them and adds a visit -------------------------
        r = await pg.evaluate(staff("""
            document.getElementById('srwCode').value = %r.toLowerCase();
            document.getElementById('srwFind').click();
            await new Promise(r=>setTimeout(r,350));
            const found = !!document.getElementById('srwAdd');
            const txt = (document.querySelector('.srw-hit')||{}).innerText||'';
            document.getElementById('srwAdd').click();
            await new Promise(r=>setTimeout(r,350));
            return {found, txt, after: (document.querySelector('.srw-hit')||{}).innerText||'',
                    total: Member.progress().total} """, code))
        check('the code is found however it is typed', r['found'], r)
        check('and it names the member, not a number', 'Marco' in r['txt'], r['txt'][:160])
        check('Add a visit writes exactly one visit', r['total'] == 1, r)
        check('the counter screen updates to say so', '1 of 10' in r['after'], r['after'][:160])

        # ---- the two screens never disagree ----------------------------------
        r = await pg.evaluate("""async () => {
            document.querySelector('#staff').classList.remove('on');
            go('rewards'); await new Promise(r=>setTimeout(r,600));
            return {lit: document.querySelectorAll('.mb-dots i.on').length,
                    txt: document.querySelector('#v-rewards').innerText} }""")
        check('the customer card shows the visit the counter added', r['lit'] == 1, r)

        # ---- ten visits, one reward, and it comes off once -------------------
        r = await pg.evaluate(staff("""
            for(let i=0;i<9;i++) Member.addVisit();
            document.getElementById('srwCode').value = %r;
            document.getElementById('srwFind').click();
            await new Promise(r=>setTimeout(r,350));
            const ready = (document.querySelector('.srw-ready')||{}).innerText||'';
            const has = !!document.getElementById('srwUse');
            document.getElementById('srwUse').click();
            await new Promise(r=>setTimeout(r,350));
            return {ready, has, after: Member.progress(),
                    still: !!document.getElementById('srwUse')} """, code))
        check('ten visits puts a reward on the counter screen', r['has'] and '$10 off' in r['ready'], r)
        check('taking the reward off clears it, once', r['after']['ready'] == 0 and not r['still'], r)
        check('and the card starts again from zero', r['after']['visits'] == 0, r['after'])
        await pg.screenshot(path='/tmp/spc/used.png', full_page=True)

        # ---- the owner changes the rule, and the customer screen says it ----
        r = await pg.evaluate(staff("""
            document.getElementById('srwN').value = '6';
            document.getElementById('srwGift').value = '$5 off';
            document.getElementById('srwName').value = 'Paradise Club';
            document.getElementById('srwSave').click();
            await new Promise(r=>setTimeout(r,400));
            document.querySelector('#staff').classList.remove('on');
            go('rewards'); await new Promise(r=>setTimeout(r,600));
            return {dots: document.querySelectorAll('.mb-dots i').length,
                    lit: document.querySelectorAll('.mb-dots i.on').length,
                    txt: document.querySelector('#v-rewards').innerText,
                    saved: JSON.parse(localStorage.getItem('sp_rewards_cfg_v1')||'null')} """))
        check('a new visit count reaches the customer card', r['dots'] == 6, r['dots'])
        # the programme name is drawn through a text-transform, so the
        # comparison is on the words, not on their case
        low = r['txt'].lower()
        check('a new reward and name reach the words on it',
              '$5 off' in low and 'paradise club' in low, r['txt'][:260])
        check('and the rule survives a reload', (r['saved'] or {}).get('visitsFor') == 6, r['saved'])
        # a reward already given away is not re-priced under the new rule, so
        # changing it must not hand the customer visits they never made
        check('changing the rule invents no visits', r['lit'] == 0, r)

        # ---- switching it off gives the honest screen back -------------------
        r = await pg.evaluate(staff("""
            document.getElementById('srwOff').click();
            await new Promise(r=>setTimeout(r,400));
            document.querySelector('#staff').classList.remove('on');
            go('rewards'); await new Promise(r=>setTimeout(r,600));
            return {form: !!document.getElementById('mbGo'),
                    card: !!document.querySelector('.mb-code'),
                    txt: document.querySelector('#v-rewards').innerText} """))
        check('switching the programme off takes it off the customer screen',
              not r['form'] and not r['card'], r)
        check('and leaves an honest screen, not an empty one', len(r['txt']) > 120, r['txt'][:200])

        # ---- the member list marks the real one as real ----------------------
        r = await pg.evaluate("""async () => {
            SHOP_REWARDS.on = true; saveRewardsCfg();
            const st = document.querySelector('#staff'); st.classList.add('on');
            STAB = 'cust'; renderStaff(); await new Promise(r=>setTimeout(r,400));
            const rows = [...document.querySelectorAll('#staffBody .strow')];
            return {first: rows[0] ? rows[0].innerText : '', n: rows.length,
                    note: document.querySelector('#staffBody .stnote').innerText} }""")
        check('a real member sits above the sample list', 'Marco' in r['first'], r['first'][:120])
        check('and the sample is still called a sample',
              'sample' in r['note'].lower(), r['note'][:200])

        check('no page errors anywhere in the flow', not errs, errs[:3])
        await br.close()

    print('\n%d ok, %d failed' % (len(passes), len(fails)))
    for f in fails:
        print('  FAIL ' + f)
    sys.exit(1 if fails else 0)


asyncio.run(main())
