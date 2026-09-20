#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 166 — the counter's half of the programme.
#
# Stage 165 gave the customer a way to join and a card with a code on it. That
# card is worthless until somebody at the counter can do something with the
# code, and by design nothing the customer presses may ever add a visit. So
# this stage builds the only thing that can: a Rewards tab on the counter
# screen, behind the PIN.
#
#     type the code the customer shows  ->  it names them and their count
#     Add a visit                       ->  one visit, written by the counter
#     Reward used                       ->  the ten come off, the card resets
#
# That is the whole loop, and it is the loop the shop is being sold. Everything
# else in this stage exists so the shop can run it without me.
#
# ======================================================================
# THE RULE IS THE SHOP'S, NOT MINE
# ======================================================================
# Marco: "we would need to go through the settings and input our name and phone
# number." Same idea one level up — nothing about this programme should be a
# number I chose and buried in a file. So the tab carries the rule itself:
#
#     the programme on or off      how many visits            what they get
#     the birthday line            where a new member is sent (the CRM webhook)
#
# Saved on the device, read by the customer's screens the moment it changes, and
# it survives a reload. Ten visits for ten dollars is a starting position, not a
# decision I made for him.
#
# ======================================================================
# WHAT THIS DEMO FILE CAN AND CANNOT DO, SAID ON THE SCREEN
# ======================================================================
# This is the offline walkthrough: one file, no server, so the member list is
# the phone in front of you. Typing a code that belongs to somebody else's
# phone finds nothing, and the tab says exactly that rather than pretending to
# search a list that does not exist here. With the endpoint set, joins leave for
# the shop's CRM and the list becomes real. The demo is still complete, because
# the demo is one phone joining and one counter adding a visit to it, which is
# the entire motion the owner needs to see.
#
# The Customers tab keeps its sample list and keeps saying it is a sample. A
# real member, once one joins on the device, is shown above it as real.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. the rule is loaded from wherever the shop last saved it -------------
rep("""  terms: 'One membership per phone number. Visits are added at the counter when you pay. 21+ only. The register is the final word on any discount.'
};""",
"""  terms: 'One membership per phone number. Visits are added at the counter when you pay. 21+ only. The register is the final word on any discount.'
};

/* THE SHOP OWNS THE RULE. Whatever the counter last saved wins over the
   defaults above, so nothing about this programme is a number I chose and
   left in a file. */
(function(){
  try{
    const saved = JSON.parse(localStorage.getItem('sp_rewards_cfg_v1') || 'null');
    if(saved) Object.assign(SHOP_REWARDS, saved);
  }catch(e){}
})();
function saveRewardsCfg(){
  try{
    localStorage.setItem('sp_rewards_cfg_v1', JSON.stringify({
      on: SHOP_REWARDS.on, name: SHOP_REWARDS.name, visitsFor: SHOP_REWARDS.visitsFor,
      reward: SHOP_REWARDS.reward, perk: SHOP_REWARDS.perk, endpoint: SHOP_REWARDS.endpoint
    }));
  }catch(e){}
}""")

# ---- 2. redeeming is a counter action too, and it is recorded ---------------
rep("""    /* ONLY THE COUNTER CALLS THIS. */
    addVisit(){
      if(!load()) return null;
      m.visits.push({at: new Date().toISOString()});
      store();
      return m;
    },""",
"""    /* ONLY THE COUNTER CALLS THIS. */
    addVisit(){
      if(!load()) return null;
      m.visits.push({at: new Date().toISOString()});
      store();
      return m;
    },
    /* And this. A reward coming off is a fact about the till, so it is
       recorded the same way a visit is, and the card recomputes from it. */
    redeem(){
      if(!load()) return null;
      m.redeemed = m.redeemed || [];
      m.redeemed.push({at: new Date().toISOString(), reward: SHOP_REWARDS.reward});
      store();
      return m;
    },""")

# ---- 3. the tab itself -------------------------------------------------------
rep("""const tabs=[['orders','Orders'],['menu','Menu'],['media','Media check'],['cust','Customers'],['feeds','Connected'],['calls','AI phone'],['blast','Text blast'],['stock','Low stock']];""",
"""const tabs=[['orders','Orders'],['menu','Menu'],['rw','Rewards'],['media','Media check'],['cust','Customers'],['feeds','Connected'],['calls','AI phone'],['blast','Text blast'],['stock','Low stock']];""")

rep("""  } else if(STAB==='cust'){""",
"""  } else if(STAB==='rw'){
    body=staffRewards();
  } else if(STAB==='cust'){""")

# ---- 4. and what it draws ----------------------------------------------------
rep("""function normTok(""",
"""/* ======================================================================
   THE COUNTER SCREEN FOR THE REWARDS PROGRAMME
   Two things live here and they are deliberately not mixed: the action the
   counter takes fifty times a day, and the rule the owner sets once.
   ====================================================================== */
let SRW = {code:'', msg:'', found:null};

function staffRewards(){
  const R = SHOP_REWARDS;
  if(!R.on){
    return `<div class="stempty"><b>The rewards programme is switched off</b>
      <p>Customers see the honest "rewards live at the counter" screen instead.</p></div>
      ${srwSetup()}`;
  }
  const m = SRW.found;
  const p = m ? Member.progress() : null;
  return `
    <div class="srw">
      <div class="srw-do">
        <div class="eyebrow">Add a visit</div>
        <p class="srw-lead">Type the code on the customer's screen, then add the
          visit when you take their money.</p>
        <div class="srw-row">
          <input id="srwCode" value="${esc(SRW.code)}" placeholder="SP00000"
            autocomplete="off" autocapitalize="characters" spellcheck="false" maxlength="7">
          <button class="btn" id="srwFind">Look up</button>
        </div>
        ${SRW.msg ? `<div class="ckwarn" role="alert">${esc(SRW.msg)}</div>` : ''}
        ${m ? `<div class="srw-hit">
          <div class="t"><b>${esc(m.first || 'Member')}</b>
            <small>${esc(m.code)} &middot; ${p.visits} of ${p.need} visits
              &middot; ${p.total} all time</small></div>
          ${p.ready ? `<div class="srw-ready">${p.ready > 1 ? p.ready + ' rewards' : 'A reward'}
            ready &middot; ${esc(R.reward)}</div>` : ''}
          <div class="srw-acts">
            <button class="btn" id="srwAdd">Add a visit</button>
            ${p.ready ? `<button class="btn ghost" id="srwUse">Reward used, take it off</button>` : ''}
          </div></div>` : ''}
        <div class="stnote" style="margin-left:0;margin-right:0">This walkthrough
          file has no server, so the only member it can find is the one who
          joined on this device. With the shop's list connected below, every
          member's code works from any counter.</div>
      </div>
      ${srwSetup()}
    </div>`;
}

function srwSetup(){
  const R = SHOP_REWARDS;
  return `
    <div class="srw-set">
      <div class="eyebrow">The rule</div>
      <p class="srw-lead">Change any of this and the customer's screen changes
        with it. Nothing here is fixed.</p>
      <label class="ckfield"><span>Programme name</span>
        <input id="srwName" value="${esc(R.name)}"></label>
      <div class="srw-two">
        <label class="ckfield"><span>Visits to earn a reward</span>
          <input id="srwN" value="${R.visitsFor}" inputmode="numeric" maxlength="3"></label>
        <label class="ckfield"><span>What they get</span>
          <input id="srwGift" value="${esc(R.reward)}"></label>
      </div>
      <label class="ckfield"><span>Birthday line</span>
        <input id="srwPerk" value="${esc(R.perk)}"></label>
      <label class="ckfield"><span>Where new members are sent</span>
        <input id="srwEnd" value="${esc(R.endpoint)}" placeholder="Paste the CRM webhook URL"
          autocomplete="off" spellcheck="false" inputmode="url"></label>
      <p class="ckfine">Empty means a join stays on the customer's phone and
        nothing leaves this device. Paste the shop's webhook and every join
        arrives as a contact with their name, number and birthday.</p>
      <div class="srw-acts">
        <button class="btn" id="srwSave">Save the rule</button>
        <button class="btn ghost" id="srwOff">${R.on ? 'Switch the programme off' : 'Switch the programme on'}</button>
      </div>
    </div>`;
}

function wireStaffRewards(){
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
  };
  const sv = g('srwSave');
  if(sv) sv.onclick = () => {
    const n = parseInt((g('srwN') || {}).value, 10);
    SHOP_REWARDS.name = ((g('srwName') || {}).value || '').trim() || SHOP_REWARDS.name;
    if(n >= 1 && n <= 100) SHOP_REWARDS.visitsFor = n;
    SHOP_REWARDS.reward = ((g('srwGift') || {}).value || '').trim() || SHOP_REWARDS.reward;
    SHOP_REWARDS.perk = ((g('srwPerk') || {}).value || '').trim();
    SHOP_REWARDS.endpoint = ((g('srwEnd') || {}).value || '').trim();
    saveRewardsCfg();
    renderStaff();
    toast('Saved. The customer screen already says it.');
  };
  const off = g('srwOff');
  if(off) off.onclick = () => {
    SHOP_REWARDS.on = !SHOP_REWARDS.on;
    saveRewardsCfg();
    renderStaff();
    toast(SHOP_REWARDS.on ? 'Programme switched on' : 'Programme switched off');
  };
}

function normTok(""")

# ---- 5. wire it on every staff render ---------------------------------------
rep("""  if(STAB==='media') wireMediaCheck();""",
"""  if(STAB==='media') wireMediaCheck();
  if(STAB==='rw') wireStaffRewards();""")

# ---- 6. a real member sits above the sample list ----------------------------
rep("""    body=`<div class="stlist">${CUSTOMERS.map(c=>`<div class="strow"><div class="av">${c[0].split(' ').map(x=>x[0]).join('')}</div>
      <div class="t"><b>${c[0]}</b><small>${c[1]} &middot; ${c[2]}</small></div><span class="n">${c[3].toLocaleString()} pts</span></div>`).join('')}</div>
      <div class="stnote">Everyone who scanned the QR to claim a discount is in here with a phone number the shop owns. Right now those numbers go in a notebook and never get used again.</div>`;""",
"""    /* A REAL MEMBER GOES FIRST AND IS MARKED AS REAL. The list below it is
       the sample the walkthrough has always carried, and it still says so. */
    const me = (typeof Member !== 'undefined' && Member.joined) ? Member.data : null;
    const mp = me ? Member.progress() : null;
    body=`${me?`<div class="stlist"><div class="strow">
        <div class="av" style="color:var(--go-ink)">${esc((me.first||'M')[0].toUpperCase())}</div>
        <div class="t"><b>${esc(me.first||'Member')}</b><small>${esc(me.code)}
          &middot; ${esc(String(me.phone||'').replace(/^(\\d{3})(\\d{3})(\\d{4})$/,'$1 ***$3').slice(0,11))}
          &middot; ${mp.total} visit${mp.total===1?'':'s'}</small></div>
        <span class="n" style="color:var(--go-ink);font-size:10px">Joined here</span></div></div>`:''}
      <div class="stlist">${CUSTOMERS.map(c=>`<div class="strow"><div class="av">${c[0].split(' ').map(x=>x[0]).join('')}</div>
      <div class="t"><b>${c[0]}</b><small>${c[1]} &middot; ${c[2]}</small></div><span class="n">${c[3].toLocaleString()} pts</span></div>`).join('')}</div>
      <div class="stnote">${me?'The member at the top joined through the app on this device. The list under it is sample data for the walkthrough. ':''}Everyone who scanned the QR to claim a discount is in here with a phone number the shop owns. Right now those numbers go in a notebook and never get used again.</div>`;""")

# ---- 7. the look of it -------------------------------------------------------
rep(""".mb-hero{text-align:center}""",
""".srw{display:grid;gap:12px}
.srw-do,.srw-set{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px}
.srw-lead{font-size:12.5px;color:var(--body);line-height:1.5;margin:4px 0 10px}
.srw-row{display:flex;gap:8px}
.srw-row input{flex:1;font:inherit;font-family:var(--mono);font-size:19px;letter-spacing:.10em;
  text-transform:uppercase;padding:10px 12px;border-radius:12px;background:rgba(0,0,0,.28);
  color:var(--ink);border:1px solid var(--line);outline:none}
.srw-row input:focus{border-color:var(--brand)}
.srw-row .btn{flex:none;width:auto;padding:10px 16px;font-size:13px}
.srw-hit{margin-top:12px;padding:12px;border-radius:14px;border:1px solid rgba(255,47,168,.3);
  background:rgba(255,47,168,.06)}
.srw-hit .t b{display:block;font-size:15px}
.srw-hit .t small{color:var(--muted);font-size:11.5px}
.srw-ready{margin-top:8px;font-size:12px;font-weight:700;color:var(--reward-ink,#FFC22B)}
.srw-acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.srw-acts .btn{width:auto;flex:1 1 auto;padding:10px 14px;font-size:13px}
.srw-two{display:grid;grid-template-columns:1fr 1.3fr;gap:10px}
.mb-hero{text-align:center}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
