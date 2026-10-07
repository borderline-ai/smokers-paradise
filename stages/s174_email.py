#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 174 — email becomes the channel, and the app stops saying it texts.
#
# WHY EMAIL AND NOT SMS.
#
# US carrier rules on application-to-person messaging filter on content, under
# the heading SHAFT: Sex, Hate, Alcohol, Firearms, Tobacco. A smoke shop is the
# T. Registration for a vape retailer is uncertain, and even an approved
# campaign has its promotional messages dropped when the body names a product —
# which is the worst failure available, because nobody is told. Every deal,
# every reward, every birthday note would be a fight over phrasing that the
# shop loses silently.
#
# Email has no such fight. The legal regime is CAN-SPAM rather than TCPA:
# accurate sender, a physical address in the message, and an unsubscribe that
# is honoured. The shop's address is already in STORE.
#
# WHAT WAS FALSE BEFORE THIS STAGE, AND IS NOT NOW.
#
# Four claims, and the last one is the bad one.
#
#   "Mark ready, text them"            no text is sent
#   "Ready · customer notified"        nobody was notified
#   "we'll text you when the bag       no
#    is ready"
#   "You are on the list. One text     THERE WAS NO LIST. The front page box
#    when a real deal lands."          took a phone number, wrote it to that
#                                      browser's localStorage, and said this.
#
# The last one is worse than the others because it is worse than doing nothing.
# A form that silently discards what it is given makes a customer believe they
# have done something and stop looking for the real way in. It has a table
# behind it now, and an unsubscribe.
#
# WHAT IS ACTUALLY TRUE about an order, and is what the words say now: the
# customer's own order screen follows the counter within about five seconds
# while the app is open, and it already raises a toast when the bag is ready.
# That toast is real. The Order alerts switch now gates it, so the switch does
# something for the first time — it used to flip a flag nothing read.
#
# Web push is the next stage and will extend that to a closed app without
# needing any carrier's permission. Nothing here promises it yet.
#
# THE CONSENT SENTENCE TRAVELS WITH THE CONSENT. MB_TERMS is one constant, put
# on the form and sent with the join, so the shop's record says what the person
# agreed to rather than only that they agreed. "They opted in" is not an answer
# to a complaint.
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'app', 'index.html')
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---------------------------------------------------------------------------
# 1. THE JOIN FORM ASKS FOR AN ADDRESS.
#
# One more field, which costs some conversion. Worth it: email is now the only
# channel the shop has, so a member without an address is a member nobody can
# ever reach — the birthday promise on the card would be empty for them.
#
# The mobile number stays, and is NOT the channel. It is the identity: the
# member code is derived from it, and the counter can find somebody by number
# when they have lost their code.
# ---------------------------------------------------------------------------
rep("""const MB = {first: '', phone: '', bmon: '', bday: '', sms: true, msg: '', done: false};""",
"""/* The sentence, in one place, because it goes on the form AND into the shop's
   record of what this person agreed to. */
const MB_TERMS = 'Email me when something I actually want lands, and on my birthday. Unsubscribe any time.';
const MB = {first: '', phone: '', email: '', bmon: '', bday: '', sms: true, msg: '', done: false};""")

rep("""      <label class="ckfield"><span>Mobile number</span>
        <input id="mbPhone" value="${esc(MB.phone)}" placeholder="(520) 555-0134"
          inputmode="tel" autocomplete="tel" enterkeyhint="next"></label>
      <div class="mb-bday">""",
"""      <label class="ckfield"><span>Mobile number</span>
        <input id="mbPhone" value="${esc(MB.phone)}" placeholder="(520) 555-0134"
          inputmode="tel" autocomplete="tel" enterkeyhint="next"></label>
      <label class="ckfield"><span>Email</span>
        <input id="mbEmail" value="${esc(MB.email)}" placeholder="you@example.com"
          type="email" inputmode="email" autocomplete="email"
          autocapitalize="off" spellcheck="false" enterkeyhint="next"></label>
      <p class="ckfine">Your number is how the counter finds you. Your email is
        how the shop reaches you &mdash; that is the only thing it is used for.</p>
      <div class="mb-bday">""")

rep("""      <label class="mb-agree"><input type="checkbox" id="mbSms" ${MB.sms ? 'checked' : ''}>
        <span>Text me when something I actually want lands, and on my birthday.
          Reply STOP any time.</span></label>""",
"""      <label class="mb-agree"><input type="checkbox" id="mbSms" ${MB.sms ? 'checked' : ''}>
        <span>${esc(MB_TERMS)}</span></label>""")

rep("""  perk: 'A birthday text with something on us, every year.',""",
"""  perk: 'A birthday email with something on us, every year.',""")


# ---------------------------------------------------------------------------
# 2. THE FORM REFUSES A JOIN IT CANNOT USE.
#
# Same shape as the refusals already there: say which field, in the words a
# person would use. An address that cannot be sent to is a member who never
# hears from the shop again, so it is checked here rather than discovered
# months later when a birthday email bounces.
# ---------------------------------------------------------------------------
rep("""  const read = () => {
    MB.first = (g('mbFirst') || {}).value || '';
    MB.phone = (g('mbPhone') || {}).value || '';
    MB.bmon  = (g('mbMon')   || {}).value || '';
    MB.bday  = (g('mbDay')   || {}).value || '';
    MB.sms   = !!((g('mbSms') || {}).checked);
  };""",
"""  const read = () => {
    MB.first = (g('mbFirst') || {}).value || '';
    MB.phone = (g('mbPhone') || {}).value || '';
    MB.email = ((g('mbEmail') || {}).value || '').trim();
    MB.bmon  = (g('mbMon')   || {}).value || '';
    MB.bday  = (g('mbDay')   || {}).value || '';
    MB.sms   = !!((g('mbSms') || {}).checked);
  };
  /* Deliberately loose. The only way to truly check an address is to send to
     it, and a clever pattern rejects real addresses people actually have.
     This catches the typo and the empty box and gets out of the way. */
  const emailOK = v => /^[^\\s@,;]+@[^\\s@,;.]+(\\.[^\\s@,;.]+)+$/.test(String(v || '').trim());""")

rep("""    if(digits.length !== 10){ MB.msg = 'That does not look like a 10 digit mobile number.'; renderRewards(); return }
    if(!MB.sms){ MB.msg = 'Tick the box so we are allowed to text you. It is the whole point.'; renderRewards(); return }""",
"""    if(digits.length !== 10){ MB.msg = 'That does not look like a 10 digit mobile number.'; renderRewards(); return }
    if(!emailOK(MB.email)){ MB.msg = 'We need an email address. It is how the shop sends your birthday reward.'; renderRewards(); return }
    if(!MB.sms){ MB.msg = 'Tick the box so we are allowed to email you. It is the whole point.'; renderRewards(); return }""")

rep("""    Member.join(MB.first, digits, bday, MB.sms);
    if(typeof toast === 'function') toast('You are in. Show your code at the counter.');""",
"""    Member.join(MB.first, digits, bday, MB.sms, MB.email);
    if(typeof toast === 'function') toast('You are in. Show your code at the counter.');""")

rep("""    Member.forget();
    MB.first = ''; MB.phone = ''; MB.bmon = ''; MB.bday = ''; MB.msg = '';""",
"""    Member.forget();
    MB.first = ''; MB.phone = ''; MB.email = ''; MB.bmon = ''; MB.bday = ''; MB.msg = '';""")


# ---------------------------------------------------------------------------
# 3. THE JOIN CARRIES THE ADDRESS AND WHAT WAS AGREED TO.
#
# The queue item keeps the flat shape a GoHighLevel inbound webhook was set up
# for; the new keys are added beside the old ones rather than replacing them,
# so a shop that already built an automation against it keeps working.
#
# `sms` is written as false. The shop is not doing SMS, and a CRM that receives
# sms:true will eventually act on it — which is a text this person never agreed
# to receive.
# ---------------------------------------------------------------------------
rep("""    join(first, phone, bday, sms){
      m = {
        first: String(first || '').trim(),
        phone: digits(phone),
        bday: bday || '',
        sms: !!sms,
        code: codeFor(phone),
        joined: new Date().toISOString(),
        visits: [],
        redeemed: []
      };
      store();
      let q = [];
      try{ q = JSON.parse(localStorage.getItem(KEY + '_q') || '[]') }catch(e){ q = [] }
      q.push({first: m.first, phone: m.phone, birthday: m.bday, sms: m.sms,
              code: m.code, joined: m.joined, shop: (typeof STORE !== 'undefined' ? STORE.name : '')});""",
"""    join(first, phone, bday, consent, email){
      m = {
        first: String(first || '').trim(),
        phone: digits(phone),
        email: String(email || '').trim().toLowerCase(),
        bday: bday || '',
        /* The box on the form is consent to EMAIL. It is not consent to be
           texted, and must never be recorded as if it were. */
        emailOk: !!consent,
        sms: false,
        code: codeFor(phone),
        joined: new Date().toISOString(),
        visits: [],
        redeemed: []
      };
      store();
      let q = [];
      try{ q = JSON.parse(localStorage.getItem(KEY + '_q') || '[]') }catch(e){ q = [] }
      q.push({first: m.first, phone: m.phone, email: m.email, birthday: m.bday,
              emailOk: m.emailOk, sms: false,
              terms: (typeof MB_TERMS !== 'undefined' ? MB_TERMS : ''),
              code: m.code, joined: m.joined, shop: (typeof STORE !== 'undefined' ? STORE.name : '')});""")


# ---------------------------------------------------------------------------
# 4. THE COUNTER STOPS CLAIMING IT SENT A TEXT.
#
# What the button does is set the ticket to ready. What that causes is the
# customer's own order screen following it within about five seconds while the
# app is open. Both of those are true, so both of those are what it says.
# ---------------------------------------------------------------------------
rep("""          <span class="tkstate">Ready &middot; customer notified</span>`""",
"""          <span class="tkstate">Ready &middot; showing on their order screen</span>`""")

rep("""        :`<button class="p" data-tk="${esc(o.code)}">Mark ready, text them</button>""",
"""        :`<button class="p" data-tk="${esc(o.code)}">Mark ready</button>""")


# ---------------------------------------------------------------------------
# 5. CHECKOUT STOPS PROMISING A TEXT.
#
# The number is worth asking for and the reason is real — a shop with a
# question about an order picks up the phone, and a person ringing a customer
# is not application-to-person messaging and needs nobody's permission.
# ---------------------------------------------------------------------------
rep("""      <p class="ckfine">Staff call this name out at the counter. Add a number and we&rsquo;ll
        text you when the bag is ready, or leave it blank and watch this screen.</p>""",
"""      <p class="ckfine">Staff call this name out at the counter. Add a number if you
        want the shop to be able to ring you about this order. Either way, this
        screen updates the moment the counter marks your bag ready.</p>""")

rep("""  <p style="font-size:11.5px;color:var(--muted);margin:16px 0 4px;line-height:1.55">Adding your number means Smokers Paradise can text you about orders and deals. Reply STOP any time. Message rates apply.</p>""",
"""  <p style="font-size:11.5px;color:var(--muted);margin:16px 0 4px;line-height:1.55">Your number is so the shop can ring you about an order, and so the counter can find you in the rewards programme. It is not used for marketing.</p>""")


# ---------------------------------------------------------------------------
# 6. THE TWO SWITCHES DO SOMETHING.
#
# Both of them flipped a flag in localStorage that nothing ever read. The first
# one now gates a notification that genuinely exists: the toast raised when the
# status poll sees the counter mark a bag ready. The second is the email
# preference, which is a real fact about a real list.
# ---------------------------------------------------------------------------
rep("""      <div class="t"><b>Order alerts</b><small>Text me when it’s bagged</small></div>
      <button class="sw ${S.notif?'on':''}" data-tog="notif" type="button"
        role="switch" aria-checked="${S.notif?'true':'false'}"
        aria-label="Order alerts"></button></div>""",
"""      <div class="t"><b>Order alerts</b><small>Tell me the moment my bag is ready</small></div>
      <button class="sw ${S.notif?'on':''}" data-tog="notif" type="button"
        role="switch" aria-checked="${S.notif?'true':'false'}"
        aria-label="Order alerts"></button></div>""")

rep("""      <div class="t"><b>Deals by text</b><small>New arrivals and weekly offers</small></div>
      <button class="sw ${S.sms?'on':''}" data-tog="sms" type="button"
        role="switch" aria-checked="${S.sms?'true':'false'}"
        aria-label="Deal alerts by text"></button></div>""",
"""      <div class="t"><b>Deals by email</b><small>New arrivals and weekly offers</small></div>
      <button class="sw ${S.sms?'on':''}" data-tog="sms" type="button"
        role="switch" aria-checked="${S.sms?'true':'false'}"
        aria-label="Deal alerts by email"></button></div>""")

rep("""    if(o.st!==st){ o.st=st; moved=true;
      if(st==='ready') toast(`Order #${o.n} is bagged and ready`); }""",
"""    if(o.st!==st){ o.st=st; moved=true;
      /* The Order alerts switch, finally wired to something. Until stage 174
         it set a flag nothing read, which made it a decoration on a settings
         screen — the customer turned it off and kept being told. */
      if(st==='ready' && S.notif) toast(`Order #${o.n} is bagged and ready`); }""")


# ---------------------------------------------------------------------------
# 7. THE FRONT PAGE BOX HAS A LIST BEHIND IT.
#
# The one that mattered. It said "You are on the list. One text when a real
# deal lands." and there was no list: the number went to localStorage and
# stopped there. Now it takes an address and posts it to the shop, and says so
# honestly when there is no shop to post it to.
# ---------------------------------------------------------------------------
rep("""      <h4>Deal alerts by text</h4>
      <p>One message when a real deal lands. Not a newsletter.</p>
      <div class="row"><input id="suPhone" type="tel" inputmode="tel" placeholder="(520) 555-0134" aria-label="Phone number">
        <button data-signup="1">Join</button></div>
      <div class="fine">Message and data rates may apply. Reply STOP to quit. 21+ only. We never sell your number.</div>""",
"""      <h4>Deal alerts by email</h4>
      <p>One message when a real deal lands. Not a newsletter.</p>
      <div class="row"><input id="suEmail" type="email" inputmode="email" autocapitalize="off"
          spellcheck="false" autocomplete="email" placeholder="you@example.com" aria-label="Email address">
        <button data-signup="1">Join</button></div>
      <div class="fine">Unsubscribe from any message. 21+ only. We never sell your address.</div>""")

rep("""  const su=t.closest('[data-signup]'); if(su){
    const v=($('#suPhone')||{}).value||'';
    if(v.replace(/\\D/g,'').length<10){toast('Enter a 10 digit number');return}
    S.phone=v; save(); toast('You are on the list. One text when a real deal lands.'); return;
  }""",
"""  const su=t.closest('[data-signup]'); if(su){
    const v=(($('#suEmail')||{}).value||'').trim();
    if(!/^[^\\s@,;]+@[^\\s@,;.]+(\\.[^\\s@,;.]+)+$/.test(v)){toast('Enter an email address');return}
    /* THE WHOLE POINT OF THIS STAGE. This used to write the number to
       localStorage and say "You are on the list." There was no list. */
    if(typeof Shop !== 'undefined' && Shop.live){
      Shop.req('/subscribers', {method:'POST', body: JSON.stringify(
        {email: v, source: 'home', terms: (typeof MB_TERMS !== 'undefined' ? MB_TERMS : '')})})
        .then(r=>{
          toast(r && r.ok ? 'You are on the list. One email when a real deal lands.'
                          : Shop.why(r, 'Could not reach the shop. Try again in a moment.'));
        });
      return;
    }
    /* No shop to post to. Saying so is the only honest answer available: the
       alternative is the sentence this stage exists to delete. */
    toast('This walkthrough has no shop connected, so nothing was sent.');
    return;
  }""")


io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
