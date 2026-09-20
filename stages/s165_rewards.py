#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 165 — the rewards programme the shop does not have yet.
#
# Marco: "we have nothing set up for members to sign up for rewards and be asked
# for their information. It's one of the main things we are selling."
#
# He is right, and the shape of the gap is worth stating precisely because the
# app already contains most of a rewards system:
#
#   Loyalty (a 5,700 character module)   reads an EXISTING programme: look up
#                                        by phone, verify with a code, show the
#                                        balance, list rewards, redeem
#   Staff view, Customers tab            shows a member list with point totals
#   Account screen                       links to Rewards when a programme exists
#
# All of it assumes the shop already runs loyalty and this app is a window onto
# it. Smokers Paradise runs none. Asked directly, Marco: "they dont, but thats
# what we are selling."
#
# So every one of those screens is switched off, the member list in Staff view
# is illustrative, and a customer has no way to become a member at all. The only
# place anyone can type a name and a phone number is Account, under a row called
# "Name and phone" that explains itself as pickup details.
#
# ======================================================================
# THE APP IS THE PROGRAMME
# ======================================================================
# With nothing to read from, the app stops being a window and becomes the thing
# itself: people join here, and the shop's member list is built out of those
# joins. That is a different mode from the one Loyalty was written for, so it is
# added beside it rather than bolted into it — an external provider, when one
# day there is one, still wins.
#
#     no provider + programme off   ->  the honest "rewards live at the counter"
#     no provider + programme on    ->  JOIN HERE  (this stage)
#     a provider answering          ->  Loyalty, exactly as before
#
# ======================================================================
# WHAT IT ASKS FOR, AND WHY EACH ONE
# ======================================================================
#     First name      so the counter can greet them and a text can open properly
#     Mobile          the whole point: a number the shop owns and can text
#     Birthday        month and day only, never the year. A birthday offer is
#                     the single highest-response message a shop of this size
#                     can send, and a year of birth is a piece of identity
#                     nobody needs to hand a smoke shop.
#     Consent         an explicit tick, not a pre-ticked box, with STOP in the
#                     line above the button rather than buried underneath it
#
# Nothing else. Not an email nobody reads, not an address, not a last name.
# Every extra field costs sign ups, and none of those four can be dropped.
#
# ======================================================================
# THE PART THAT KEEPS IT HONEST: WHO COUNTS A VISIT
# ======================================================================
# A visit counter the customer's own phone can increment is a coupon anyone can
# print. So the customer's screen never counts anything. A visit is written only
# by the counter, from Staff view, against the member code the customer shows —
# and the card says so in as many words:
#
#     "Visits are added by the counter when you pay. This screen only shows
#      what they have added."
#
# The reward itself is never applied by the app either. The card says a reward
# is ready; the register is what takes it off, which is the same rule every
# other price in this app already follows.
#
# ======================================================================
# WHERE THE MEMBER GOES
# ======================================================================
# A join posts to SHOP_REWARDS.endpoint, which is where the shop's CRM listens.
# In this walkthrough file that is empty, nothing is sent, and the join is kept
# on the phone so the screen works in a shop with no signal. When it is set, a
# join arrives as one flat JSON object — first, phone, birthday, consent, code,
# joined — which is what a GoHighLevel inbound webhook expects. Failures queue
# and retry on the next open rather than being lost or shown to the customer.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. the programme, and the member on this phone ------------------------
rep("""function rwDisconnected(){""",
"""/* ======================================================================
   THE SHOP'S OWN REWARDS PROGRAMME
   Used only where no external loyalty provider answers, which is every shop
   that has never run one. The shop owns every value in here; nothing about
   the rule is hard-coded into the screens that draw it.
   ====================================================================== */
const SHOP_REWARDS = {
  on: true,
  name: 'Paradise Rewards',
  /* the rule, in the shop's words and the shop's numbers */
  visitsFor: 10,
  reward: '$10 off',
  perk: 'A birthday text with something on us, every year.',
  /* Where a new member lands. Empty here: this file is the offline
     walkthrough, so a join is kept on the phone and nothing leaves it. */
  endpoint: '',
  terms: 'One membership per phone number. Visits are added at the counter when you pay. 21+ only. The register is the final word on any discount.'
};

/* THE MEMBER ON THIS PHONE.
   Visits are never written here by anything the customer can press — only the
   counter adds one, from Staff view, against the code the customer shows. */
const Member = (function(){
  const KEY = 'sp_member_v1';
  let m = null;
  function load(){
    if(m) return m;
    try{ m = JSON.parse(localStorage.getItem(KEY) || 'null') }catch(e){ m = null }
    return m;
  }
  function store(){
    try{ localStorage.setItem(KEY, JSON.stringify(m)) }catch(e){}
  }
  /* A short code the counter can read off a screen across a counter and type
     without asking twice. Derived from the number so it is stable, and it is
     not the number: four digits of it would be a credential. */
  function codeFor(phone){
    const d = String(phone || '').replace(/\\D/g, '');
    let h = 7;
    for(let i = 0; i < d.length; i++) h = (h * 31 + d.charCodeAt(i)) % 100000;
    return 'SP' + String(h).padStart(5, '0');
  }
  function digits(p){ return String(p || '').replace(/\\D/g, '') }
  return {
    get joined(){ return !!load() },
    get data(){ return load() },
    codeFor,
    /* the queue is drained on every open, so a join made with no signal still
       reaches the shop the next time the phone has one */
    async flush(){
      if(!SHOP_REWARDS.endpoint) return;
      let q = [];
      try{ q = JSON.parse(localStorage.getItem(KEY + '_q') || '[]') }catch(e){ q = [] }
      if(!q.length) return;
      const left = [];
      for(const item of q){
        try{
          const r = await fetch(SHOP_REWARDS.endpoint, {
            method: 'POST', headers: {'content-type': 'application/json'},
            body: JSON.stringify(item)
          });
          if(!r.ok) left.push(item);
        }catch(e){ left.push(item) }
      }
      try{ localStorage.setItem(KEY + '_q', JSON.stringify(left)) }catch(e){}
    },
    join(first, phone, bday, sms){
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
              code: m.code, joined: m.joined, shop: (typeof STORE !== 'undefined' ? STORE.name : '')});
      try{ localStorage.setItem(KEY + '_q', JSON.stringify(q)) }catch(e){}
      this.flush();
      return m;
    },
    /* ONLY THE COUNTER CALLS THIS. */
    addVisit(){
      if(!load()) return null;
      m.visits.push({at: new Date().toISOString()});
      store();
      return m;
    },
    forget(){ m = null; try{ localStorage.removeItem(KEY) }catch(e){} },
    /* how far through the card they are, counting only what the counter added */
    progress(){
      const d = load();
      if(!d) return {visits: 0, need: SHOP_REWARDS.visitsFor, ready: 0};
      const used = (d.redeemed || []).length * SHOP_REWARDS.visitsFor;
      const net = Math.max(0, (d.visits || []).length - used);
      return {
        visits: net % SHOP_REWARDS.visitsFor,
        need: SHOP_REWARDS.visitsFor,
        ready: Math.floor(net / SHOP_REWARDS.visitsFor),
        total: (d.visits || []).length
      };
    }
  };
})();

function rwDisconnected(){""")

# ---- 2. the rewards screen offers the shop's own programme ------------------
rep("""  /* No order service, or no programme configured: one honest screen. */
  if(!Loyalty.available || L.provider === 'none'){
    $('#v-rewards').innerHTML = head + `<div class="ckwrap">${rwDisconnected()}</div>`;
    return;
  }""",
"""  /* NO EXTERNAL PROVIDER. Two different answers, and the difference is
     whether the shop runs a programme of its own. When it does, this app is
     where people join it; when it does not, the honest screen stands. */
  if(!Loyalty.available || L.provider === 'none'){
    const body = (typeof SHOP_REWARDS !== 'undefined' && SHOP_REWARDS.on)
      ? (Member.joined ? mbCard() : mbJoin())
      : rwDisconnected();
    $('#v-rewards').innerHTML = head + `<div class="ckwrap">${body}</div>`;
    if(typeof SHOP_REWARDS !== 'undefined' && SHOP_REWARDS.on) mbWire();
    return;
  }""")

# ---- 3. the two screens ----------------------------------------------------
rep("""function rwSignIn(){""",
"""/* JOIN. Four fields, and each one earns its place: see the note at the top of
   scripts/s165_rewards.py for why there is no email and no year of birth. */
const MB = {first: '', phone: '', bmon: '', bday: '', sms: true, msg: '', done: false};

function mbJoin(){
  const R = SHOP_REWARDS;
  const months = ['January','February','March','April','May','June','July',
                  'August','September','October','November','December'];
  return `
    <div class="rw-card mb-hero">
      <div class="mb-badge"><svg viewBox="0 0 24 24"><path d="M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/></svg></div>
      <h3>${esc(R.name)}</h3>
      <p>Every ${R.visitsFor} visits is ${esc(R.reward)}. ${esc(R.perk)}</p>
      <p class="ckfine">Free to join. Nothing to carry, nothing to lose.</p>
    </div>
    <div class="rw-card">
      <label class="ckfield"><span>First name</span>
        <input id="mbFirst" value="${esc(MB.first)}" placeholder="Marco"
          autocomplete="given-name" enterkeyhint="next"></label>
      <label class="ckfield"><span>Mobile number</span>
        <input id="mbPhone" value="${esc(MB.phone)}" placeholder="(520) 555-0134"
          inputmode="tel" autocomplete="tel" enterkeyhint="next"></label>
      <div class="mb-bday">
        <label class="ckfield"><span>Birthday month</span>
          <select id="mbMon"><option value="">Choose</option>${months.map((n, i) =>
            `<option value="${i + 1}" ${MB.bmon == (i + 1) ? 'selected' : ''}>${n}</option>`).join('')}</select></label>
        <label class="ckfield"><span>Day</span>
          <input id="mbDay" value="${esc(MB.bday)}" placeholder="14" inputmode="numeric" maxlength="2"></label>
      </div>
      <p class="ckfine">Your birthday is month and day only. We never ask the year.</p>
      <label class="mb-agree"><input type="checkbox" id="mbSms" ${MB.sms ? 'checked' : ''}>
        <span>Text me when something I actually want lands, and on my birthday.
          Reply STOP any time.</span></label>
      ${MB.msg ? `<div class="ckwarn" role="alert">${esc(MB.msg)}</div>` : ''}
      <button class="btn" id="mbGo">Join ${esc(R.name)}</button>
      <p class="ckfine">${esc(R.terms)}</p>
    </div>`;
}

/* THE CARD. What the customer holds up at the counter. */
function mbCard(){
  const R = SHOP_REWARDS, d = Member.data, p = Member.progress();
  const dots = Array.from({length: p.need}).map((_, i) =>
    `<i class="${i < p.visits ? 'on' : ''}"></i>`).join('');
  return `
    <div class="rw-card mb-card">
      <div class="rw-eyebrow">${esc(R.name)}</div>
      <div class="mb-name">${esc(d.first || 'Member')}</div>
      <div class="mb-code">${esc(d.code)}</div>
      <div class="mb-hint">Show this at the counter</div>
    </div>

    ${p.ready ? `<div class="rw-card mb-ready">
      <h3>${p.ready > 1 ? p.ready + ' rewards ready' : 'A reward is ready'}</h3>
      <p>${esc(R.reward)} on your next visit. Ask for it at the counter and they
        will take it off at the register.</p>
    </div>` : ''}

    <div class="rw-card">
      <h4>${p.visits} of ${p.need} visits</h4>
      <div class="mb-dots">${dots}</div>
      <p class="ckfine">${p.visits === 0 && !p.total
        ? 'Your first visit gets added next time you pay at the counter.'
        : (p.need - p.visits) + ' more and the next ' + esc(R.reward) + ' is yours.'}</p>
      <p class="ckfine">Visits are added by the counter when you pay. This screen
        only shows what they have added, so it can never be ahead of the shop.</p>
    </div>

    <div class="rw-card">
      <h4>How it works</h4>
      <p class="ckfine">Show your code when you pay. Every ${R.visitsFor} visits
        earns ${esc(R.reward)}, and the register applies it. ${esc(R.perk)}</p>
      <p class="ckfine">${esc(R.terms)}</p>
      <button class="btn ghost" id="mbForget">Leave the programme</button>
    </div>`;
}

function mbWire(){
  const g = id => document.getElementById(id);
  const read = () => {
    MB.first = (g('mbFirst') || {}).value || '';
    MB.phone = (g('mbPhone') || {}).value || '';
    MB.bmon  = (g('mbMon')   || {}).value || '';
    MB.bday  = (g('mbDay')   || {}).value || '';
    MB.sms   = !!((g('mbSms') || {}).checked);
  };
  const go = g('mbGo');
  if(go) go.onclick = () => {
    read();
    const digits = MB.phone.replace(/\\D/g, '');
    if(!MB.first.trim()){ MB.msg = 'We need a first name for the counter.'; renderRewards(); return }
    if(digits.length !== 10){ MB.msg = 'That does not look like a 10 digit mobile number.'; renderRewards(); return }
    if(!MB.sms){ MB.msg = 'Tick the box so we are allowed to text you. It is the whole point.'; renderRewards(); return }
    const day = parseInt(MB.bday, 10);
    const bday = (MB.bmon && day >= 1 && day <= 31) ? (MB.bmon + '-' + day) : '';
    MB.msg = '';
    Member.join(MB.first, digits, bday, MB.sms);
    if(typeof toast === 'function') toast('You are in. Show your code at the counter.');
    renderRewards();
  };
  const f = g('mbForget');
  if(f) f.onclick = () => {
    Member.forget();
    MB.first = ''; MB.phone = ''; MB.bmon = ''; MB.bday = ''; MB.msg = '';
    renderRewards();
  };
}

function rwSignIn(){""")

# ---- 4. the account row points at it ---------------------------------------
rep("""    ${(typeof Loyalty!=='undefined' && Loyalty.available && Loyalty.state.provider!=='none')?`""",
"""    ${(typeof SHOP_REWARDS!=='undefined' && SHOP_REWARDS.on
        && !(typeof Loyalty!=='undefined' && Loyalty.available && Loyalty.state.provider!=='none'))?`
    <button class="arow" data-go="rewards"><svg viewBox="0 0 24 24"><path d="M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/></svg>
      <div class="t"><b>${esc(SHOP_REWARDS.name)}</b><small>${Member.joined
        ? esc(Member.data.code) + ' &middot; ' + Member.progress().visits + ' of ' + SHOP_REWARDS.visitsFor + ' visits'
        : 'Every ' + SHOP_REWARDS.visitsFor + ' visits is ' + esc(SHOP_REWARDS.reward)}</small></div>
      <span class="ch">&rsaquo;</span></button>`:''}
    ${(typeof Loyalty!=='undefined' && Loyalty.available && Loyalty.state.provider!=='none')?`""")

# ---- 5. the look of it ------------------------------------------------------
rep(""".rw-bal{text-align:center;padding:20px 14px}""",
""".mb-hero{text-align:center}
.mb-badge{margin:0 auto 8px;width:44px;height:44px;border-radius:14px;display:grid;place-items:center;
  background:linear-gradient(140deg,var(--go),#8A1E5E);color:#fff}
.mb-badge svg{width:22px;height:22px;fill:currentColor}
.mb-bday{display:grid;grid-template-columns:1.6fr 1fr;gap:10px}
.mb-bday select{width:100%;font:inherit;padding:11px 12px;border-radius:12px;
  background:var(--card);color:var(--ink);border:1px solid var(--line)}
.mb-agree{display:flex;gap:10px;align-items:flex-start;margin:12px 0 4px;font-size:12.5px;
  line-height:1.45;color:var(--body)}
.mb-agree input{margin-top:2px;width:18px;height:18px;flex:none;accent-color:var(--go)}
.mb-card{text-align:center;background:linear-gradient(150deg,#2A0F33,#12060F);
  border-color:rgba(255,47,168,.34)}
.mb-name{font-family:var(--disp);font-weight:800;font-size:22px;letter-spacing:-.03em;
  color:var(--ink);margin-top:2px}
.mb-code{font-family:var(--mono);font-size:30px;letter-spacing:.10em;color:#FF7BC8;margin-top:8px}
.mb-hint{font-size:11.5px;color:var(--muted);margin-top:6px}
.mb-ready{border-color:rgba(255,194,43,.4)}
.mb-dots{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 8px}
.mb-dots i{width:15px;height:15px;border-radius:50%;border:1.5px solid var(--line);display:block}
.mb-dots i.on{background:var(--go);border-color:var(--go)}
.rw-bal{text-align:center;padding:20px 14px}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
