#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The shop, with a backend, in two real browsers.

Every other suite in here drives the offline file, and it should: that file is
a product. This one is the opposite check. It starts the real service on this
machine, points a real browser at it, and does the thing that was impossible
before server/ existed:

    a customer joins on ONE browser
    the counter, in a DIFFERENT browser with its own cookie jar and its own
    localStorage, types her code and adds a visit
    her card, back in the first browser, says one visit

Two browser contexts are two devices. That is not a convenience of the test,
it is the exact shape of the bug this backend was built to end, quoted from
CLAUDE.md:

    customer joins on her phone      -> code SP26699 written to HER localStorage
    staff type SP26699 on the iPad   -> "No member with that code on this device."

Network is dead except to the local service, for the same reason the other
suites kill it entirely: nothing here may quietly depend on the internet.

    python3 test/live_backend.py
"""
import asyncio, os, socket, subprocess, sys, time
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(os.path.dirname(HERE), 'server')
PIN = '7413'

fails, passes = [], []


def check(name, ok, detail=''):
    (passes if ok else fails).append(name)
    print(('  ok   ' if ok else '  FAIL ') + name + (('  :: ' + str(detail)) if detail and not ok else ''))


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def start_server(port):
    """The same handler that deploys to Workers, behind node:http.

    Built first, because server/public/index.html is a copy of app/index.html
    and a stale copy would mean this suite passed against last week's app.
    """
    subprocess.run(['node', os.path.join(SERVER, 'scripts', 'build.mjs')],
                   cwd=SERVER, check=True, capture_output=True)
    p = subprocess.Popen(['node', os.path.join(SERVER, 'scripts', 'serve.mjs'), str(port)],
                         cwd=SERVER, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         env=dict(os.environ, STAFF_PIN=PIN))
    for _ in range(80):
        try:
            socket.create_connection(('127.0.0.1', port), 0.2).close()
            return p
        except OSError:
            if p.poll() is not None:
                raise SystemExit('the service died on start:\n' +
                                 p.stdout.read().decode('utf8', 'replace'))
            time.sleep(0.15)
    raise SystemExit('the service never came up')


async def main():
    port = free_port()
    proc = start_server(port)
    base = 'http://127.0.0.1:%d' % port
    errs = []

    try:
        async with async_playwright() as pw:
            br = await pw.chromium.launch()

            async def device(w, h):
                """A context is a device: its own cookies, its own storage."""
                ctx = await br.new_context(viewport={'width': w, 'height': h})
                pg = await ctx.new_page()
                pg.on('pageerror', lambda e: errs.append(str(e)))
                # Everything except this machine is off, exactly as the other
                # suites do it. A test that can reach the internet is a test
                # that can pass for the wrong reason.
                await pg.route('**/*', lambda r: r.continue_()
                               if '127.0.0.1' in r.request.url else r.abort())
                return ctx, pg

            # ---- the customer, on her phone ---------------------------------
            cctx, phone = await device(390, 844)
            await phone.goto(base + '/')
            await phone.wait_for_timeout(1600)

            served = await phone.evaluate("() => ({api: window.SP_API, staff: !!window.SP_STAFF})")
            check('the shop address hands the app an API base', served['api'] == '/api', served)
            check('and does not put a staff door on it', not served['staff'], served)

            await phone.evaluate("() => document.querySelector('#gateYes').click()")
            await phone.wait_for_timeout(2200)

            # ---- stage 172: the photographs are files now ---------------------
            # They are written into the document as `img/<hash>.webp`, with no
            # leading slash, so that the same file also works opened off a disk.
            # Served, that has to resolve against the root — which is what the
            # <base href="/"> the Worker injects is for. If it were missing this
            # would still pass on '/' and fail on '/counter', so both are checked.
            # The SIZE of the document is the assertion. Searching it for
            # "data:image" is not, and that is worth recording: the file
            # carries a comment showing the shape of a PHOTOS entry —
            #     /* PHOTOS['disp0::miami-mint'] = 'data:image/webp;base64,...' */
            # — and a substring check reads that comment as a photograph. It
            # went red while the thing it was checking was entirely true.
            # What matters is that 6.8 MB of pictures are no longer inside a
            # document that is re-fetched whenever a price changes.
            r = await phone.evaluate("""async () => {
                const doc = await (await fetch('/', {cache:'no-store'})).blob();
                const im = [...document.querySelectorAll('img')];
                return {bytes: doc.size,
                        raster: im.filter(i => /^data:image\/(webp|png|jpeg)/
                          .test(i.getAttribute('src')||'')).length} }""")
            check('the photographs are out of the document',
                  r['bytes'] < 4 * 1024 * 1024,
                  'the document is %.2f MB' % (r['bytes'] / 1048576.0))
            check('and no img element carries a photograph as base64',
                  r['raster'] == 0, r)

            # Forced eager and given time, the way imgaudit5 does it. Reading
            # naturalWidth off a lazy image nobody has scrolled to measures the
            # loading strategy, not whether the picture is there.
            r = await phone.evaluate("""async () => {
                go('home'); await new Promise(r=>setTimeout(r,900));
                const m = document.querySelector('#main');
                for(let y=0;y<m.scrollHeight;y+=420){ m.scrollTop=y;
                  await new Promise(r=>setTimeout(r,140)) }
                document.querySelectorAll('img[loading="lazy"]').forEach(i=>i.loading='eager');
                m.scrollTop = 0;
                await new Promise(r=>setTimeout(r,2600));
                const im = [...document.querySelectorAll('.view.on img')];
                return {n: im.length,
                        broken: im.filter(i=>i.naturalWidth<=2).length,
                        rel: im.filter(i=>(i.getAttribute('src')||'').startsWith('img/')).length,
                        sample: im.length ? im[0].currentSrc : ''} }""")
            check('and every photograph loads over http',
                  r['n'] > 4 and r['broken'] == 0, r)
            check('the relative paths resolve against the root',
                  r['rel'] > 0 and '/img/' in r['sample'], r['sample'][:120])

            r = await phone.evaluate("""async () => {
                const reg = await navigator.serviceWorker.getRegistration('/');
                return {registered: !!reg,
                        scope: reg ? reg.scope : '',
                        sw: (await fetch('/sw.js')).status} }""")
            check('a service worker is registered, so an outage is survivable',
                  r['registered'] and r['sw'] == 200, r)

            r = await phone.evaluate("""async () => {
                go('rewards'); await new Promise(r=>setTimeout(r,600));
                document.getElementById('mbFirst').value = 'Ana';
                document.getElementById('mbPhone').value = '(520) 555-0134';
                document.getElementById('mbMon').value = '3';
                document.getElementById('mbDay').value = '14';
                document.getElementById('mbSms').checked = true;
                document.getElementById('mbGo').click();
                await new Promise(r=>setTimeout(r,1200));
                return {code: (document.querySelector('.mb-code')||{}).innerText||'',
                        txt: document.querySelector('#v-rewards').innerText} }""")
            code = (r['code'] or '').strip()
            check('she joins and gets a code on a card', code.startswith('SP') and len(code) == 7, r)

            queued = await phone.evaluate(
                "() => JSON.parse(localStorage.getItem('sp_member_v1_q')||'[]').length")
            check('and the join actually reached the shop, so nothing is left queued',
                  queued == 0, 'still queued: %s' % queued)

            # ---- the counter, on the iPad by the till -----------------------
            ictx, ipad = await device(834, 1112)
            await ipad.goto(base + '/counter')
            await ipad.wait_for_timeout(1600)
            staffed = await ipad.evaluate("() => !!window.SP_STAFF")
            check('the counter has its own address', staffed, staffed)

            await ipad.evaluate("() => document.querySelector('#gateYes').click()")
            await ipad.wait_for_timeout(1400)
            up = await ipad.evaluate("() => document.querySelector('#pin').classList.contains('on')")
            check('and it puts a PIN pad up', up, up)

            # The PIN is checked by the server. A wrong one is refused there,
            # not here, which is the whole reason the door is safe to publish.
            for k in '0000':
                await ipad.evaluate("k => document.querySelector('#keys [data-k=\"%s\"]').click()" % k, k)
            await ipad.wait_for_timeout(900)
            r = await ipad.evaluate("""() => ({
                pin: document.querySelector('#pin').classList.contains('on'),
                staff: document.querySelector('#staff').classList.contains('on')})""")
            check('the wrong PIN does not open the counter', r['pin'] and not r['staff'], r)

            for k in PIN:
                await ipad.evaluate("k => document.querySelector('#keys [data-k=\"%s\"]').click()" % k, k)
            await ipad.wait_for_timeout(1000)
            r = await ipad.evaluate("""() => ({
                staff: document.querySelector('#staff').classList.contains('on')})""")
            check('the right one does', r['staff'], r)

            # The counter lives at /counter, one path segment deep, which is the
            # case a root-relative path would have got right by luck and a
            # relative one gets wrong without <base>. This is that check.
            r = await ipad.evaluate("""async () => {
                document.querySelectorAll('img[loading]').forEach(i=>i.loading='eager');
                await new Promise(r=>setTimeout(r,2400));
                const im = [...document.querySelectorAll('img')].filter(
                  i => (i.getAttribute('src')||'').startsWith('img/')
                       && i.getBoundingClientRect().width > 0);
                return {n: im.length,
                        broken: im.filter(i=>i.naturalWidth<=2).length,
                        sample: im.length ? im[0].currentSrc : ''} }""")
            check('photographs load on the counter address too, one path deep',
                  r['n'] > 0 and r['broken'] == 0 and '/img/' in r['sample'], r)

            # ---- THE TEST THIS WHOLE BACKEND EXISTS FOR ---------------------
            r = await ipad.evaluate("""async (code) => {
                STAB = 'rw'; renderStaff();
                await new Promise(r=>setTimeout(r,400));
                document.getElementById('srwCode').value = code;
                document.getElementById('srwFind').click();
                await new Promise(r=>setTimeout(r,900));
                return {hit: !!document.querySelector('.srw-hit'),
                        txt: (document.querySelector('#staffBody')||{}).innerText||'',
                        warn: (document.querySelector('#staffBody .ckwarn')||{}).innerText||''} }""", code)
            check('the counter finds a member who joined on another device',
                  r['hit'] and 'Ana' in r['txt'], r['warn'] or r['txt'][:200])
            check('and no longer says the member is not on this device',
                  'on this device' not in r['txt'], r['txt'][:200])

            r = await ipad.evaluate("""async () => {
                document.getElementById('srwAdd').click();
                await new Promise(r=>setTimeout(r,900));
                return {txt: (document.querySelector('.srw-hit')||{}).innerText||''} }""")
            check('the counter adds a visit', '1 of 10' in r['txt'], r)

            r = await ipad.evaluate("""async () => {
                document.getElementById('srwAdd').click();
                await new Promise(r=>setTimeout(r,900));
                return {txt: (document.querySelector('.srw-hit')||{}).innerText||'',
                        warn: (document.querySelector('#staffBody .ckwarn')||{}).innerText||''} }""")
            check('a double tap is refused and said out loud, not swallowed',
                  '1 of 10' in r['txt'] and len(r['warn']) > 8, r)

            # ---- back on her phone ------------------------------------------
            r = await phone.evaluate("""async () => {
                await Member.refresh();
                go('rewards'); await new Promise(r=>setTimeout(r,500));
                return {txt: document.querySelector('#v-rewards').innerText,
                        p: Member.progress()} }""")
            check('her card shows the visit the counter added, on her own device',
                  r['p']['visits'] == 1 and '1 of 10' in r['txt'], r['p'])

            # ---- rule 1, against a real server -------------------------------
            # mbForget is excluded for the reason member.py excludes it: it is
            # the one control on the card that is SUPPOSED to change something,
            # and against a real server it does — it leaves the programme.
            r = await phone.evaluate("""async () => {
                const before = Member.progress().visits;
                const els = [...document.querySelectorAll(
                  '#v-rewards button, #v-rewards .mb-dots i, #v-rewards .rw-card')]
                  .filter(b => b.id !== 'mbForget');
                for(const el of els){ try{ el.click() }catch(e){}
                  await new Promise(r=>setTimeout(r,80)) }
                await new Promise(r=>setTimeout(r,600));
                await Member.refresh();
                return {before, after: Member.progress().visits, pressed: els.length} }""")
            check('pressing every control on the card still adds no visit',
                  r['after'] == r['before'] == 1, r)

            # A customer device holds no staff session, so the server refuses.
            r = await phone.evaluate("""async (code) => {
                const r = await fetch('/api/staff/members/' + code + '/visit',
                  {method:'POST', credentials:'same-origin',
                   headers:{'content-type':'application/json'}, body:'{}'});
                await Member.refresh();
                return {status: r.status, visits: Member.progress().visits} }""", code)
            check('and the service refuses a visit from a device with no staff session',
                  r['status'] == 401 and r['visits'] == 1, r)

            # ---- the rule reaches the phone ---------------------------------
            r = await ipad.evaluate("""async () => {
                STAB = 'rw'; renderStaff();
                await new Promise(r=>setTimeout(r,300));
                document.getElementById('srwN').value = '6';
                document.getElementById('srwGift').value = 'A free lighter';
                document.getElementById('srwSave').click();
                await new Promise(r=>setTimeout(r,1200));
                return {n: SHOP_REWARDS.visitsFor} }""")
            check('the owner changes the rule at the counter', r['n'] == 6, r)

            await phone.reload()
            await phone.wait_for_timeout(2200)
            r = await phone.evaluate("""async () => {
                go('rewards'); await new Promise(r=>setTimeout(r,600));
                return {n: SHOP_REWARDS.visitsFor, gift: SHOP_REWARDS.reward,
                        txt: document.querySelector('#v-rewards').innerText} }""")
            check('and the customer phone picks it up on its next open',
                  r['n'] == 6 and r['gift'] == 'A free lighter', r)
            check('the card counts against the new rule without inventing a visit',
                  '1 of 6' in r['txt'], r['txt'][:200])

            # ---- an order crosses devices too --------------------------------
            r = await phone.evaluate("""async () => {
                const code = 'ZZ-4242';
                const res = await OrderStore.place({
                  code, n: 4242, who: 'Ana', phone: '5205550134',
                  items: [{id:'x', n:'Geek Bar Pulse', brand:'Geek Bar', v:'Miami Mint', q:1, unit:25}],
                  subtotal: 25, fee: 0, tax: 2.15, total: 27.15,
                  source: 'smokersparadise-mobile', pickup: 'ASAP, ',
                  placedAt: Date.now(), status: 'placed'});
                return {ok: !!res, live: OrderStore.live, total: res && res.total} }""")
            check('an order placed on the phone reaches the shop', r['ok'] and r['live'], r)

            r = await ipad.evaluate("""async () => {
                STAB = 'orders'; renderStaff();
                await new Promise(r=>setTimeout(r,2600));
                renderStaff();
                return {txt: (document.querySelector('#staffBody')||{}).innerText||''} }""")
            check('and the counter board shows it, on the other device',
                  'ZZ-4242' in r['txt'] or 'Geek Bar Pulse' in r['txt'], r['txt'][:300])
            check('and the board says it is reading the shop, not this browser',
                  'not this browser' in r['txt'], r['txt'][:300])

            # ---- the shop owns its list --------------------------------------
            r = await ipad.evaluate("""async () => {
                const r = await fetch('/api/staff/members/export.csv', {credentials:'same-origin'});
                return {status: r.status, body: await r.text()} }""")
            check('the whole member list downloads from the counter',
                  r['status'] == 200 and 'Ana,5205550134' in r['body'], r['body'][:200])

            check('no page errors anywhere in the flow', not errs, errs[:3])

            await cctx.close()
            await ictx.close()
            await br.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    print('\n%d ok, %d failed' % (len(passes), len(fails)))
    if fails:
        print('failed:')
        for f in fails:
            print('  - ' + f)
    sys.exit(1 if fails else 0)


asyncio.run(main())
