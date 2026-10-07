#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 171 — the app talks to the shop.
#
# Everything this stage touches was already written correctly against a server
# that did not exist. `OrderStore` has spoken to an order service since it was
# written; `Member` has not spoken to anything. That asymmetry is the whole bug:
#
#     customer joins on her phone      -> SP26699 in HER localStorage
#     staff type SP26699 on the iPad   -> "No member with that code on this device."
#
# server/ is now that shop. This stage connects five things to it and changes
# nothing else:
#
#   1. the rewards rule, so the owner changing it on the iPad reaches phones
#   2. the member's card, so it reads the shop's count and not its own
#   3. the counter's lookup, add-a-visit and take-a-reward-off
#   4. the catalogue edits, so a price change reaches a customer
#   5. the join queue, which now drains to the shop as well as to a CRM
#
# THE SHAPE OF THE CHANGE, AND WHY IT IS THIS SHAPE.
#
# Every one of these is guarded on SP_API. With no API base — the file opened
# off a disk, which is what the 60 test suites drive and what gets emailed
# around — not one line of new code runs and the behaviour is byte for byte
# what stage 170 left. That is deliberate and it is testable: the offline
# walkthrough is a product, not a fallback.
#
# Where a screen reads a number synchronously, it goes on reading a number
# synchronously. `Member.progress()` is called from inside render functions and
# making it async would mean rewriting six screens. Instead the server's answer
# is cached on the member record and `progress()` prefers the cache when there
# is one. An async refresh fills it and re-renders. The card is never ahead of
# the shop, because the cache is only ever written by an answer from the shop.
#
# WHAT THIS STAGE DOES NOT DO. It does not let the customer's device write a
# visit, by any path, ever. `Member.addVisit` and `Member.redeem` stay exactly
# where they were — reachable only from the counter screen — and when the
# service is live the counter calls the server instead, which checks for a
# staff session before it writes. The local versions remain the offline
# walkthrough's, which is the one context where there is no shop to ask.
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'app', 'index.html')
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---------------------------------------------------------------------------
# 1. THE CLIENT FOR THE SHOP'S SERVICE.
#
# A second door beside `call()`. It exists because `call()` throws the server's
# sentence away — `if(!r.ok) return {ok:false, status:r.status}` — and the
# counter needs that sentence. "A visit was already added for Ana a moment ago"
# is the difference between a staff member understanding what happened and a
# staff member pressing the button again.
# ---------------------------------------------------------------------------
rep("""/* THE MEMBER ON THIS PHONE.
   Visits are never written here by anything the customer can press — only the
   counter adds one, from Staff view, against the code the customer shows. */
const Member = (function(){""",
"""/* ======================================================================
   THE SHOP'S OWN SERVICE.

   `call()` above is the order client and it deliberately drops the server's
   words: it answers {ok:false, status} and nothing more, because an order
   either reached the register or it did not and there is nothing to read out.
   The rewards counter is the opposite. Every refusal it can get is a sentence
   somebody has to say to a customer standing in front of them:

     "A visit was already added for Ana a moment ago."
     "Ana is 9 visits short of a reward."
     "No member with that code. Check the code on their screen."

   So this keeps the body. Same JSON-or-nothing rule as `call()`, for the same
   reason: a static host answers an unknown path with HTML and a 200, and
   reading that as an answer would tell the counter things that are not true.
   ====================================================================== */
const Shop = (function(){
  let ready = false;         /* config has been read at least once          */

  async function req(path, opts){
    if(!SP_API) return null;
    try{
      const r = await fetch(SP_API + path, Object.assign({
        credentials: 'same-origin',
        headers: {'content-type': 'application/json'}
      }, opts || {}));
      const ct = (r.headers.get('content-type') || '').toLowerCase();
      if(ct.indexOf('json') < 0) return null;
      const body = await r.json().catch(()=>null);
      if(!body) return null;
      return {ok: r.ok && body.ok !== false, status: r.status, body: body};
    }catch(e){ return null }
  }

  /* The sentence to show a person, whatever went wrong. `fallback` is used
     when there was no service at all, because "could not reach the shop" and
     "the shop said no" are different facts and a counter needs to tell them
     apart. */
  function why(r, fallback){
    if(!r) return fallback || 'Could not reach the shop. Check the connection.';
    return (r.body && (r.body.detail || r.body.reason)) || fallback || 'That did not work.';
  }

  return {
    get live(){ return !!SP_API },
    get ready(){ return ready },
    req, why,

    /* THE RULE, FROM THE SHOP. Before this the owner could set "6 visits" on
       the iPad and every customer's phone went on saying 10 forever. */
    async pullConfig(){
      const r = await req('/config');
      if(!r || !r.ok) return false;
      const rw = r.body.rewards || {};
      /* `endpoint` is not in the public config on purpose and must not be
         invented here: an empty string would switch the CRM forward off. */
      ['on','name','visitsFor','reward','perk','terms'].forEach(k=>{
        if(k in rw) SHOP_REWARDS[k] = rw[k];
      });
      ready = true;
      return true;
    },

    /* THE SHELF, FROM THE SHOP. A price edited at the counter lands here and
       the customer's menu changes with it. Verified broken before this stage:
       edited 30 -> 999.99 on the shop device, the customer device still 30. */
    async pullCatalog(){
      const r = await req('/catalog/overrides');
      if(!r || !r.ok) return false;
      const edits = r.body.edits || {}, custom = r.body.custom || [];
      /* The shop's copy wins over anything cached on this device, but a photo
         held locally is kept: the service does not store photographs and
         dropping one would blank a picture the shop already added. */
      S.edits = S.edits || {};
      Object.keys(edits).forEach(id=>{
        const had = S.edits[id] || {};
        S.edits[id] = Object.assign({}, edits[id], had.photo ? {photo: had.photo} : {});
      });
      if(custom.length){
        const mine = (S.custom || []);
        S.custom = custom.map(c=>{
          const had = mine.find(x=>x.id === c.id) || {};
          return Object.assign({}, had, c, had.photo ? {photo: had.photo} : {});
        }).concat(mine.filter(x=>!custom.some(c=>c.id === x.id)));
      }
      try{ localStorage.setItem('sp_demo_v1', JSON.stringify(S)) }catch(e){}
      if(typeof rebuildCatalog === 'function') rebuildCatalog();
      if(typeof buildNav === 'function') buildNav();
      return true;
    },

    /* THE SHELF, TO THE SHOP. Photographs are stripped rather than sent: the
       service refuses them with a 413 and it is right to, a database row is
       not a photo store. They stay on the device that added them. */
    async pushCatalog(){
      if(!SP_API) return false;
      const edits = {};
      Object.keys(S.edits || {}).forEach(id=>{
        const e = Object.assign({}, S.edits[id]); delete e.photo;
        if(Object.keys(e).length) edits[id] = e;
      });
      const custom = (S.custom || []).map(c=>{
        const x = Object.assign({}, c); delete x.photo; return x;
      });
      const r = await req('/staff/catalog/overrides',
        {method:'POST', body: JSON.stringify({edits: edits, custom: custom})});
      return !!(r && r.ok);
    },

    /* Everything the counter does to a member. Each one answers the same
       shape — {ok, progress, member} or a sentence — so the three buttons
       that call them can all be wired the same way. */
    lookupMember(code){ return req('/staff/members?code=' + encodeURIComponent(code)) },
    addVisit(code, force){
      return req('/staff/members/' + encodeURIComponent(code) + '/visit',
        {method:'POST', body: JSON.stringify({force: !!force})});
    },
    redeem(code){
      return req('/staff/members/' + encodeURIComponent(code) + '/redeem',
        {method:'POST', body: JSON.stringify({})});
    },
    saveRule(rule){
      return req('/staff/config', {method:'POST', body: JSON.stringify({rewards: rule})});
    }
  };
})();

/* THE MEMBER ON THIS PHONE.
   Visits are never written here by anything the customer can press — only the
   counter adds one, from Staff view, against the code the customer shows.

   Since stage 171 the shop's own service is the authority whenever there is
   one. What is kept here is a cache and an outbox, not a ledger: the count on
   this screen is the count the shop last told this phone. */
const Member = (function(){""")


# ---------------------------------------------------------------------------
# 2. THE QUEUE NOW DRAINS TO THE SHOP.
#
# The queue item shape is untouched. It was chosen for a GoHighLevel inbound
# webhook, the service accepts exactly that object, and a shop that already
# built an automation against it should not have to rebuild anything.
#
# What changes is where it goes. With a service, the phone posts to the shop
# and the shop forwards to the CRM with its own retries — which is the half of
# stage 170's bug a phone cannot fix, because a phone that is never opened
# again never retries anything.
# ---------------------------------------------------------------------------
rep("""    /* the queue is drained on every open, so a join made with no signal still
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
    },""",
"""    /* the queue is drained on every open, so a join made with no signal still
       reaches the shop the next time the phone has one.

       Two destinations, and the first one that exists wins. With the shop's
       service running, a join goes to the shop, which owns the member list and
       forwards to the CRM on its own schedule. With no service — the offline
       file, or a shop that has only ever pasted a webhook — it goes straight
       at the webhook exactly as it did before.

       An item is only dropped from the queue when something answered 2xx.
       That is what makes this a queue rather than a hole. */
    async flush(){
      const toShop = !!SP_API;
      if(!toShop && !SHOP_REWARDS.endpoint) return;
      let q = [];
      try{ q = JSON.parse(localStorage.getItem(KEY + '_q') || '[]') }catch(e){ q = [] }
      if(!q.length) return;
      const left = [];
      for(const item of q){
        if(toShop){
          const r = await Shop.req('/members', {method:'POST', body: JSON.stringify(item)});
          if(r && r.ok){
            /* The shop decides the code. Usually it is the one this phone
               computed and is already showing on a card, but two numbers can
               hash to the same five digits and only the table knows. When the
               shop moved it, the card has to move with it or the counter will
               type what is on the screen and find nobody. */
            const b = r.body || {};
            if(load() && b.member && b.member.code && b.member.code !== m.code){
              m.code = b.member.code; store();
            }
            if(load() && b.token && b.token !== m.token){ m.token = b.token; store(); }
            if(b.progress) this.take(b.progress);
          }else{
            left.push(item);
          }
        }else{
          try{
            const r = await fetch(SHOP_REWARDS.endpoint, {
              method: 'POST', headers: {'content-type': 'application/json'},
              body: JSON.stringify(item)
            });
            if(!r.ok) left.push(item);
          }catch(e){ left.push(item) }
        }
      }
      try{ localStorage.setItem(KEY + '_q', JSON.stringify(left)) }catch(e){}
      if(VIEW === 'rewards' && typeof renderRewards === 'function') renderRewards();
    },

    /* The shop's count, cached so the render functions can stay synchronous.
       Only ever written by an answer from the shop, which is what stops this
       screen from ever being ahead of the till. */
    take(p){
      if(!load() || !p) return;
      m.srv = {visits: p.visits, need: p.need, ready: p.ready, total: p.total};
      store();
    },

    /* Asked on open and after anything that could have changed it. A 404 is
       not a failure: it means the shop does not know this token, so this phone
       is not holding a membership and should stop saying it is. */
    async refresh(){
      if(!SP_API || !load() || !m.token) return false;
      const r = await Shop.req('/members/me?token=' + encodeURIComponent(m.token));
      if(!r) return false;                       /* no signal; keep the cache */
      if(r.status === 404){ this.forget(); return false }
      if(!r.ok) return false;
      const b = r.body || {};
      if(b.member && b.member.code) m.code = b.member.code;
      if(b.member && b.member.first) m.first = b.member.first;
      if(b.progress) this.take(b.progress);
      /* The visit list is the shop's, not this phone's. Nothing local writes
         to it when there is a service. */
      if(Array.isArray(b.visits)) m.visits = b.visits.map(v=>({at: v.at}));
      if(Array.isArray(b.redemptions)) m.redeemed = b.redemptions.slice();
      store();
      return true;
    },""")


# ---------------------------------------------------------------------------
# 3. THE CARD READS THE SHOP'S COUNT.
#
# `progress()` stays synchronous because six render functions call it inline.
# It prefers the shop's answer when there is one and falls back to counting
# what is on the phone when there is not — which, offline, is the only honest
# thing it could do anyway.
# ---------------------------------------------------------------------------
rep("""    /* how far through the card they are, counting only what the counter added */
    progress(){
      const d = load();
      if(!d) return {visits: 0, need: SHOP_REWARDS.visitsFor, ready: 0};""",
"""    /* how far through the card they are, counting only what the counter added */
    progress(){
      const d = load();
      if(!d) return {visits: 0, need: SHOP_REWARDS.visitsFor, ready: 0};
      /* THE SHOP'S ANSWER WINS. It was computed against the shop's own visits
         and the shop's own redemptions, each one priced at what it cost on the
         day — which is a sum this phone cannot do, because it has never seen
         the rule as it stood last March. */
      if(SP_API && d.srv && typeof d.srv.visits === 'number'){
        return {visits: d.srv.visits, need: d.srv.need || SHOP_REWARDS.visitsFor,
                ready: d.srv.ready || 0, total: d.srv.total || 0};
      }""")


# ---------------------------------------------------------------------------
# 4. LEAVING TELLS THE SHOP.
#
# Without this, "Leave the programme" takes the card off one phone and leaves
# the person on the shop's texting list, which is the kind of thing that gets a
# shop a complaint and an app deleted.
# ---------------------------------------------------------------------------
rep("""    forget(){ m = null; try{ localStorage.removeItem(KEY) }catch(e){} },""",
"""    forget(){
      /* Tell the shop first, while the token is still in hand. Fire and
         forget: a customer pressing Leave should not wait on a network, and
         the shop's own copy is the one that matters for the texting list. */
      try{
        if(SP_API && m && m.token){
          Shop.req('/members/me/leave',
            {method:'POST', body: JSON.stringify({token: m.token})});
        }
      }catch(e){}
      m = null; try{ localStorage.removeItem(KEY) }catch(e){}
    },""")


# ---------------------------------------------------------------------------
# 5. OPENING THE APP ASKS THE SHOP.
#
# The old guard was `if(SHOP_REWARDS.endpoint)`, which is empty on a service
# that keeps the webhook to itself — correctly, since a public config that
# leaks the CRM URL lets anybody post fake members into the shop's list. So the
# guard has to widen or the queue would never drain on the hosted app.
# ---------------------------------------------------------------------------
rep("""setTimeout(function(){
  try{ if(SHOP_REWARDS.endpoint) Member.flush() }catch(e){}
}, 2500);""",
"""setTimeout(function(){
  try{ if(SHOP_REWARDS.endpoint || SP_API) Member.flush() }catch(e){}
}, 2500);

/* ASK THE SHOP WHO IT IS, ONCE, ON OPEN.

   Three questions in one breath, deferred past the first paint and guarded so
   that a service which is down can never stop the app from opening:

     the rule    so this phone stops repeating a number the owner changed
     the shelf   so a price edited at the counter is the price on the menu
     the card    so the visit count is the shop's count and not this phone's

   With no SP_API every one of these returns immediately and nothing happens,
   which is the offline walkthrough and is tested. */
setTimeout(function(){
  if(!SP_API) return;
  try{
    Promise.all([
      Shop.pullConfig().catch(()=>false),
      Shop.pullCatalog().catch(()=>false),
      Member.refresh().catch(()=>false)
    ]).then(()=>{
      if(VIEW === 'rewards' && typeof renderRewards === 'function') renderRewards();
      if(typeof renderStaff === 'function' && document.getElementById('staff')
         && document.getElementById('staff').classList.contains('on')) renderStaff();
    }).catch(()=>{});
  }catch(e){}
}, 900);""")


# ---------------------------------------------------------------------------
# 6. THE COUNTER CAN FIND A REAL CUSTOMER.
#
# This is the function the whole backend was built for. It used to be four
# lines and one of them was a lie by omission:
#
#     else { SRW.msg = 'No member with that code on this device.'; }
#
# True, and useless. There was no device it could have been on except this one.
# ---------------------------------------------------------------------------
rep("""function wireStaffRewards(){
  const g = id => document.getElementById(id);
  const find = () => {
    const c = (g('srwCode') || {}).value || '';
    SRW.code = c.toUpperCase().replace(/[^A-Z0-9]/g, '');
    SRW.found = null;
    if(SRW.code.length < 3){ SRW.msg = 'Type the code from the customer\\'s card.'; }
    else if(Member.joined && Member.data.code === SRW.code){ SRW.msg = ''; SRW.found = Member.data; }
    else { SRW.msg = 'No member with that code on this device.'; }
    renderStaff();
  };
  const f = g('srwFind'); if(f) f.onclick = find;
  const inp = g('srwCode');
  if(inp) inp.onkeydown = e => { if(e.key === 'Enter') find() };
  const a = g('srwAdd');
  if(a) a.onclick = () => {
    Member.addVisit();
    SRW.found = Member.data;
    const p = Member.progress();
    renderStaff();
    toast(p.ready ? 'Visit added. A reward is ready.'
                  : 'Visit added. ' + (p.need - p.visits) + ' to go.');
  };
  const u = g('srwUse');
  if(u) u.onclick = () => {
    Member.redeem();
    SRW.found = Member.data;
    renderStaff();
    toast('Reward taken off. Ring the rest as normal.');
  };""",
"""function wireStaffRewards(){
  const g = id => document.getElementById(id);

  /* With a service, every one of these three goes to the shop and the shop
     decides. The counter is not trusted because it is the counter; it is
     trusted because it holds a session the server issued against a PIN the
     server checked. Without a service they do what they always did, against
     the one member this device happens to be holding, which is the offline
     walkthrough and is exactly as much as it can honestly claim. */
  const find = async () => {
    const c = (g('srwCode') || {}).value || '';
    SRW.code = c.toUpperCase().replace(/[^A-Z0-9]/g, '');
    SRW.found = null; SRW.prog = null;
    if(SRW.code.length < 3){ SRW.msg = 'Type the code from the customer\\'s card.'; renderStaff(); return }

    if(Shop.live){
      SRW.msg = 'Looking up…'; renderStaff();
      const r = await Shop.lookupMember(SRW.code);
      if(r && r.ok){ SRW.msg = ''; SRW.found = r.body.member; SRW.prog = r.body.progress; }
      else { SRW.msg = Shop.why(r, 'No member with that code.'); }
      renderStaff();
      return;
    }
    if(Member.joined && Member.data.code === SRW.code){ SRW.msg = ''; SRW.found = Member.data; }
    else { SRW.msg = 'No member with that code on this device.'; }
    renderStaff();
  };
  const f = g('srwFind'); if(f) f.onclick = find;
  const inp = g('srwCode');
  if(inp) inp.onkeydown = e => { if(e.key === 'Enter') find() };

  const said = p => p.ready ? 'Visit added. A reward is ready.'
                            : 'Visit added. ' + (p.need - p.visits) + ' to go.';

  const a = g('srwAdd');
  if(a) a.onclick = async () => {
    if(Shop.live){
      const code = (SRW.found && SRW.found.code) || SRW.code;
      const r = await Shop.addVisit(code, false);
      if(r && r.ok){
        SRW.found = r.body.member || SRW.found; SRW.prog = r.body.progress;
        SRW.msg = ''; renderStaff(); toast(said(r.body.progress));
        return;
      }
      /* The shop refusing a second visit inside thirty seconds is a thumb on a
         busy iPad, not a fault. It is said out loud rather than swallowed,
         because the alternative is a staff member pressing it again. */
      SRW.msg = Shop.why(r, 'Could not add that visit.');
      renderStaff();
      if(r && r.status === 409) toast(SRW.msg);
      return;
    }
    Member.addVisit();
    SRW.found = Member.data;
    const p = Member.progress();
    renderStaff();
    toast(said(p));
  };

  const u = g('srwUse');
  if(u) u.onclick = async () => {
    if(Shop.live){
      const code = (SRW.found && SRW.found.code) || SRW.code;
      const r = await Shop.redeem(code);
      if(r && r.ok){
        SRW.found = r.body.member || SRW.found; SRW.prog = r.body.progress;
        SRW.msg = ''; renderStaff();
        toast('Reward taken off. Ring the rest as normal.');
        return;
      }
      SRW.msg = Shop.why(r, 'Could not take that reward off.');
      renderStaff();
      return;
    }
    Member.redeem();
    SRW.found = Member.data;
    renderStaff();
    toast('Reward taken off. Ring the rest as normal.');
  };""")


# The counter's own view of a member is the shop's, not this device's copy.
rep("""  const m = SRW.found;
  const p = m ? Member.progress() : null;""",
"""  const m = SRW.found;
  const p = m ? (SRW.prog || Member.progress()) : null;""")

rep("""let SRW = {code:'', msg:'', found:null};""",
"""let SRW = {code:'', msg:'', found:null, prog:null};""")


# ---------------------------------------------------------------------------
# 7. THE NOTE UNDER THE LOOKUP BOX.
#
# It has always told the truth about the walkthrough. On the hosted shop that
# truth becomes a lie, and it is the first thing an owner reads while deciding
# whether to believe any of this. Two notes, and the app knows which one it is.
# Rule 3 in CLAUDE.md — never claim what is not verified — cuts both ways.
# ---------------------------------------------------------------------------
rep("""        <div class="stnote" style="margin-left:0;margin-right:0">This walkthrough
          file has no server, so the only member it can find is the one who
          joined on this device. With the shop's list connected below, every
          member's code works from any counter.</div>""",
"""        <div class="stnote" style="margin-left:0;margin-right:0">${Shop.live
          ? `This counter is reading the shop's member list, not this browser.
             Any member's code works from any screen, and only a counter signed
             in with the PIN can add a visit or take a reward off.
             <a href="${esc(SP_API)}/staff/members/export.csv" download
                style="color:var(--go-ink);font-weight:700">Download the whole
                member list</a> any time — it is the shop's list, not ours.`
          : `This walkthrough file has no server, so the only member it can find
             is the one who joined on this device. Connect the shop's service and
             every member's code works from any counter.`}</div>""")


# ---------------------------------------------------------------------------
# 8. SAVING THE RULE SAVES IT FOR EVERYONE.
#
# The local save stays: it is what keeps the walkthrough working and it is also
# the right immediate feedback, because the owner should see the screen change
# whether or not a network answers. The difference is that the toast no longer
# overclaims. "The customer screen already says it" was only ever true of the
# customer screen on that same iPad.
# ---------------------------------------------------------------------------
rep("""    saveRewardsCfg();
    renderStaff();
    toast('Saved. The customer screen already says it.');
  };""",
"""    saveRewardsCfg();
    renderStaff();
    if(Shop.live){
      toast('Saving to the shop…');
      Shop.saveRule({
        on: SHOP_REWARDS.on, name: SHOP_REWARDS.name, visitsFor: SHOP_REWARDS.visitsFor,
        reward: SHOP_REWARDS.reward, perk: SHOP_REWARDS.perk, endpoint: SHOP_REWARDS.endpoint
      }).then(r=>{
        if(r && r.ok){ toast('Saved. Every phone picks it up on its next open.') }
        else {
          /* The rule was saved on this iPad and not at the shop, and the owner
             has to know which, because the two now disagree. */
          toast(Shop.why(r, 'Saved here, but the shop did not take it. Try again.'));
        }
      });
      return;
    }
    toast('Saved on this device. It reaches customers once the shop is connected.');
  };""")

rep("""  const off = g('srwOff');
  if(off) off.onclick = () => {
    SHOP_REWARDS.on = !SHOP_REWARDS.on;
    saveRewardsCfg();
    renderStaff();
    toast(SHOP_REWARDS.on ? 'Programme switched on' : 'Programme switched off');
  };""",
"""  const off = g('srwOff');
  if(off) off.onclick = () => {
    SHOP_REWARDS.on = !SHOP_REWARDS.on;
    saveRewardsCfg();
    renderStaff();
    /* Switching the programme off has to reach customers or it has not been
       switched off — they would go on being offered a card that earns nothing. */
    if(Shop.live) Shop.saveRule({on: SHOP_REWARDS.on});
    toast(SHOP_REWARDS.on ? 'Programme switched on' : 'Programme switched off');
  };""")


# ---------------------------------------------------------------------------
# 9. A PRICE EDIT LEAVES THE IPAD.
#
# persist() is the one funnel every menu edit goes through — price, name, new
# product, hide, bulk photo import. Pushing from here rather than from each
# caller means an edit added later is published by default instead of by
# somebody remembering to publish it.
#
# Photographs are stripped on the way out, in Shop.pushCatalog. They stay on
# the device that added them, which is the honest limit of a service that keeps
# prices and names.
# ---------------------------------------------------------------------------
rep("""/* save + rebuild in one move, with a real message if storage is full */
function persist(){
  try{
    localStorage.setItem('sp_demo_v1',JSON.stringify(S));
  }catch(e){
    toast('Out of room on this phone. Remove a picture and try again.');
  }
  rebuildCatalog();
  buildNav();
}""",
"""/* save + rebuild in one move, with a real message if storage is full */
function persist(){
  try{
    localStorage.setItem('sp_demo_v1',JSON.stringify(S));
  }catch(e){
    toast('Out of room on this phone. Remove a picture and try again.');
  }
  rebuildCatalog();
  buildNav();
  /* AND OUT TO THE SHOP. Before this, a price edited at the counter reached
     exactly one device: the one it was typed on. Proven — edited 30 to 999.99
     on the shop device, the customer device still showed 30.

     Debounced because the menu screen calls persist() on every keystroke in a
     bulk import, and a shop on a phone hotspot should not send the whole edit
     set forty times. Failure is silent here on purpose: this runs behind
     screens that have already reported their own result, and a second toast
     saying the same thing twice is noise at a counter. */
  if(typeof Shop !== 'undefined' && Shop.live){
    clearTimeout(persist._t);
    persist._t = setTimeout(()=>{ try{ Shop.pushCatalog() }catch(e){} }, 1200);
  }
}""")


io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
