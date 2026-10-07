#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The one time the app asks somebody to join, and every time it must not."""
import asyncio, os, sys
from playwright.async_api import async_playwright

B = __import__('sppath').APP
os.makedirs('/tmp/spa', exist_ok=True)
fails, passes = [], []

def check(name, ok, detail=''):
    (passes if ok else fails).append(name)
    print(('  ok   ' if ok else '  FAIL ') + name + (('  :: ' + str(detail)) if detail and not ok else ''))

KILL = """{const i=document.getElementById('inter'); if(i){i.classList.remove('on');i.style.display='none'}
 const s=document.getElementById('scrim'); if(s){s.classList.remove('on')}}"""

async def open_app(pw, clear=True):
    ctx = await pw.chromium.launch()
    return ctx

async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        ctx = await br.new_context(viewport={'width':390,'height':844}, has_touch=True)
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B); await pg.wait_for_timeout(1600)
        await pg.evaluate("""() => {localStorage.removeItem('sp_member_v1');
            localStorage.removeItem('sp_member_ask_v1');
            document.querySelector('#gateYes').click()}"""); await pg.wait_for_timeout(1000)
        await pg.evaluate(KILL)

        r = await pg.evaluate("""async () => {
            const on = () => document.getElementById('mbask').classList.contains('on');
            const seen = [];
            for(const v of ['deals','account','home','cat']){
              go(v === 'cat' ? 'cat' : v, v === 'cat' ? 'disp' : undefined);
              await new Promise(r=>setTimeout(r,1300));
              seen.push({v, on: on()});
            }
            return {seen, txt: document.getElementById('mbaskCard').innerText} }""")
        early = [x for x in r['seen'][:1] if x['on']]
        check('it does not ask on the first screen', not early, r['seen'])
        check('it asks once they have stayed', any(x['on'] for x in r['seen']), r['seen'])
        check('and it states the shop rule, not an invention',
              '10 visits' in r['txt'] and '$10 off' in r['txt'], r['txt'][:200])
        check('no countdown, no scarcity',
              # "21+ only" is the legal line, not scarcity
              not any(w in r['txt'].lower() for w in
                      ['hurry','today only','spots','limited','expires','last chance','act now']),
              r['txt'][:200])
        await pg.screenshot(path='/tmp/spa/ask.png')

        r = await pg.evaluate("""async () => {
            const out = {};
            out.buttons = [...document.querySelectorAll('#mbask button')].map(b=>b.innerText);
            document.getElementById('mbaskNo').click();
            await new Promise(r=>setTimeout(r,400));
            out.closed = !document.getElementById('mbask').classList.contains('on');
            out.remembered = !!localStorage.getItem('sp_member_ask_v1');
            for(const v of ['deals','home','account','deals']){ go(v); await new Promise(r=>setTimeout(r,700)) }
            out.again = document.getElementById('mbask').classList.contains('on');
            return out }""")
        check('"Not now" is a real button, not small print', len(r['buttons']) == 2, r['buttons'])
        check('and it closes the sheet', r['closed'], r)
        check('and it is remembered', r['remembered'], r)
        check('it never asks a second time', not r['again'], r)

        r = await pg.evaluate("""async () => {
            localStorage.removeItem('sp_member_ask_v1');
            go('rewards'); await new Promise(r=>setTimeout(r,700));
            mbFirst.value='Marco'; mbPhone.value='5205550134';
            mbEmail.value='marco@example.com'; mbSms.checked=true;
            mbGo.click(); await new Promise(r=>setTimeout(r,600));
            for(const v of ['home','deals','account','home']){ go(v); await new Promise(r=>setTimeout(r,700)) }
            return {joined: Member.joined,
                    asked: document.getElementById('mbask').classList.contains('on')} }""")
        check('it never asks a member to join again', r['joined'] and not r['asked'], r)

        r = await pg.evaluate("""async () => {
            Member.forget(); localStorage.removeItem('sp_member_ask_v1');
            SHOP_REWARDS.on = false;
            for(const v of ['home','deals','account','home']){ go(v); await new Promise(r=>setTimeout(r,700)) }
            const asked = document.getElementById('mbask').classList.contains('on');
            SHOP_REWARDS.on = true;
            return {asked} }""")
        check('a shop with the programme switched off is never asked for', not r['asked'], r)

        check('no page errors', not errs, errs[:3])
        await ctx.close(); await br.close()
    print('\n%d ok, %d failed' % (len(passes), len(fails)))
    for f in fails: print('  FAIL ' + f)
    sys.exit(1 if fails else 0)

asyncio.run(main())
