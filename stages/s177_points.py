#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 177 — the card becomes a points balance and a ladder.
#
# Ten dots was a punch card, and a punch card cannot express "you are 350
# points from three dollars off". The programme is spend-based now: a dollar
# earns ten points, and points come off a sale as money.
#
#      400 -> $1 off  (baskets over $15)   $40 spend   2.5% back
#      750 -> $3 off                       $75         4.0%
#    2,500 -> $10 off                     $250         4.0%
#    3,000 -> $12 off                     $300         4.0%
#    5,000 -> $25 off                     $500         5.0%
#   15,000 -> $75 off                   $1,500         5.0%
#
# THE CARD SAYS DOLLARS, NEVER PRODUCTS. Every rung is "$25 off". The tier's
# internal name — Papers, Disposable, Glass — is the owner's, for her reports,
# and never reaches a customer's screen. That is the legal structure and it is
# also the better product: the customer spends it on whatever they want.
#
# WHY THE UNAFFORDABLE RUNGS STILL SHOW. A ladder where you can only see the
# rung you are standing on is not a ladder. The whole mechanism is somebody
# knowing there is a bigger thing further up, so every tier renders, greyed,
# with how far away it is.
#
# TWO SENTENCES THE CUSTOMER MUST READ HERE, NOT AT THE TILL. A reward comes
# off a purchase, and ID is checked when it does. Somebody learning either of
# those at the counter blames the shop, and the employee should never be the
# one delivering it.
#
# IT DEGRADES. A shop still on the visit programme sends no `points` object,
# and the card falls back to the dots exactly as before. That is what lets
# this deploy before every shop has migrated.
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
# 1. THE SHOP'S ANSWER CARRIES A BALANCE AND A LADDER.
# ---------------------------------------------------------------------------
rep("""      if(b.progress) this.take(b.progress);
      /* The visit list is the shop's, not this phone's. Nothing local writes
         to it when there is a service. */""",
"""      if(b.progress) this.take(b.progress);
      /* The points standing, when the shop runs the spend programme. Cached
         the same way the visit progress is, so the card renders instantly and
         the render functions stay synchronous. */
      if(b.points){ m.points = b.points; store(); }""")

rep("""    take(p){
      if(!load() || !p) return;
      m.srv = {visits: p.visits, need: p.need, ready: p.ready, total: p.total};
      store();
    },""",
"""    take(p){
      if(!load() || !p) return;
      m.srv = {visits: p.visits, need: p.need, ready: p.ready, total: p.total};
      store();
    },
    /* The points standing, or null on a shop still counting visits. Every
       screen asks this rather than reading the cache directly, so there is
       one place that decides which programme is running. */
    get points(){ const d = load(); return (d && d.points) || null },""")


# ---------------------------------------------------------------------------
# 2. THE CARD.
# ---------------------------------------------------------------------------
rep("""function mbCard(){
  const R = SHOP_REWARDS, d = Member.data, p = Member.progress();
  const dots = Array.from({length: p.need}).map((_, i) =>
    `<i class="${i < p.visits ? 'on' : ''}"></i>`).join('');
  return `""",
"""function mbCard(){
  const R = SHOP_REWARDS, d = Member.data, p = Member.progress();
  /* Spend programme if the shop sent a balance; punch card if it did not. */
  if(Member.points) return mbPointsCard();
  const dots = Array.from({length: p.need}).map((_, i) =>
    `<i class="${i < p.visits ? 'on' : ''}"></i>`).join('');
  return `""")

rep("""function mbWire(){
  const g = id => document.getElementById(id);""",
"""/* THE SPEND PROGRAMME'S CARD.

   A balance, the nearest rung with a bar to it, and then every rung — the
   ones they can take now, and the ones they cannot, greyed with the distance.
   A ladder you can only see one step of is not a ladder. */
function mbPointsCard(){
  const R = SHOP_REWARDS, d = Member.data, P = Member.points;
  const money0 = c => '$' + (c/100).toFixed(2).replace(/\\.00$/, '');
  const next = P.next;
  const pct = next ? Math.max(3, Math.round(100 * P.balance / next.points)) : 100;
  const can = P.tiers.filter(t => t.affordable);

  return `
    <div class="rw-card mb-card">
      <div class="rw-eyebrow">${esc(R.name)}</div>
      <div class="mb-name">${esc(d.first || 'Member')}</div>
      <div class="mb-code">${esc(d.code)}</div>
      <div class="mb-hint">Show this at the counter</div>
    </div>

    <div class="rw-card">
      <div class="pt-bal">${P.balance.toLocaleString()}<span>points</span></div>
      ${next
        ? `<div class="pt-bar"><i style="width:${pct}%"></i></div>
           <p class="ckfine">${(next.short).toLocaleString()} more points and
             ${esc(next.label)} is yours.</p>`
        : `<p class="ckfine">You have reached every reward on the card.</p>`}
      <p class="ckfine">Every $1 you spend earns
        ${(SP_POINTS_PER_DOLLAR||10)} points. Points are added at the counter
        when you pay.</p>
    </div>

    ${can.length ? `<div class="rw-card mb-ready">
      <h3>${can.length > 1 ? can.length + ' rewards ready' : 'A reward is ready'}</h3>
      <p>Ask for ${esc(can[can.length-1].label)} at the counter and they will
        take it off at the register.</p>
    </div>` : ''}

    <div class="rw-card">
      <h4>Your rewards</h4>
      <div class="pt-tiers">
        ${P.tiers.map(t => `<div class="pt-tier ${t.affordable ? 'on' : ''}">
          <b>${esc(t.label)}</b>
          <small>${t.affordable
            ? 'Ready to use' + (t.minSubtotalCents
                ? ' on a purchase over ' + money0(t.minSubtotalCents) : '')
            : t.short.toLocaleString() + ' points to go'}</small>
          <span>${t.points.toLocaleString()}</span>
        </div>`).join('')}
      </div>
      ${/* The two sentences that must not be learned at the till. */''}
      <p class="ckfine">A reward comes off a purchase, it is not a free item,
        and the register is the final word. Your ID is checked at the counter
        when you use one.</p>
    </div>

    <div class="rw-card">
      <h4>How it works</h4>
      <p class="ckfine">Show your code when you pay. Every dollar earns points,
        and points come off a future purchase. ${esc(R.perk)}</p>
      <p class="ckfine">${esc(R.terms)}</p>
      <button class="btn ghost" id="mbForget">Leave the programme</button>
    </div>`;
}

function mbWire(){
  const g = id => document.getElementById(id);""")


# ---------------------------------------------------------------------------
# 3. THE EARN RATE AND THE LADDER COME FROM THE SHOP.
# ---------------------------------------------------------------------------
rep("""    /* THE RULE, FROM THE SHOP. Before this the owner could set "6 visits" on
       the iPad and every customer's phone went on saying 10 forever. */
    async pullConfig(){
      const r = await req('/config');
      if(!r || !r.ok) return false;
      const rw = r.body.rewards || {};""",
"""    /* THE RULE, FROM THE SHOP. Before this the owner could set "6 visits" on
       the iPad and every customer's phone went on saying 10 forever. */
    async pullConfig(){
      const r = await req('/config');
      if(!r || !r.ok) return false;
      /* The earn rate, so the card can say what a dollar is worth without
         guessing. A shop that has not moved to points sends neither. */
      if(r.body.points && r.body.points.perDollar){
        SP_POINTS_PER_DOLLAR = r.body.points.perDollar;
      }
      const rw = r.body.rewards || {};""")

rep("""const SHOP_REWARDS = {
  on: true,""",
"""/* Points per dollar, replaced by whatever the shop's own config says. Ten is
   the default the ladder was priced against, not a number to rely on. */
let SP_POINTS_PER_DOLLAR = 10;

const SHOP_REWARDS = {
  on: true,""")


# ---------------------------------------------------------------------------
# 4. THE OFFER SHEET AND THE JOIN SCREEN SPEAK IN POINTS WHERE THERE ARE ANY.
# ---------------------------------------------------------------------------
rep("""    <h3>Every ${R.visitsFor} visits is ${esc(R.reward)}.</h3>""",
"""    <h3>${SP_TIERS.length
      ? 'Every dollar earns ' + SP_POINTS_PER_DOLLAR + ' points.'
      : 'Every ' + R.visitsFor + ' visits is ' + esc(R.reward) + '.'}</h3>""")

rep("""      <p>Every ${R.visitsFor} visits is ${esc(R.reward)}. ${esc(R.perk)}</p>""",
"""      <p>${SP_TIERS.length
        ? 'Every dollar you spend earns ' + SP_POINTS_PER_DOLLAR +
          ' points, and points come off a future purchase. ' + esc(R.perk)
        : 'Every ' + R.visitsFor + ' visits is ' + esc(R.reward) + '. ' + esc(R.perk)}</p>""")

rep("""let SP_POINTS_PER_DOLLAR = 10;""",
"""let SP_POINTS_PER_DOLLAR = 10;
/* The ladder, as the shop published it. Empty on a shop still counting
   visits, which is what every screen tests to decide what to say. */
let SP_TIERS = [];""")

rep("""      if(r.body.points && r.body.points.perDollar){
        SP_POINTS_PER_DOLLAR = r.body.points.perDollar;
      }""",
"""      if(r.body.points && r.body.points.perDollar){
        SP_POINTS_PER_DOLLAR = r.body.points.perDollar;
      }
      if(Array.isArray(r.body.tiers)) SP_TIERS = r.body.tiers;""")


# ---------------------------------------------------------------------------
# 5. THE STYLES.
# ---------------------------------------------------------------------------
rep(""".mb-dots{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 8px}""",
"""/* ---- the points card (stage 177) ---- */
.pt-bal{font-size:44px;font-weight:800;letter-spacing:-.04em;line-height:1;
  font-variant-numeric:tabular-nums;margin:2px 0 10px}
.pt-bal span{font-size:14px;font-weight:700;letter-spacing:0;color:var(--muted);
  margin-left:8px;vertical-align:middle}
.pt-bar{height:8px;border-radius:99px;background:rgba(255,255,255,.1);overflow:hidden;
  margin:0 0 9px}
.pt-bar i{display:block;height:100%;border-radius:99px;
  background:linear-gradient(90deg,#FF2E88,#FF7AB8)}
.pt-tiers{display:flex;flex-direction:column;gap:7px;margin:10px 0 12px}
.pt-tier{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:11px;
  background:rgba(255,255,255,.04);border:1px solid var(--hair);opacity:.5}
.pt-tier.on{opacity:1;border-color:rgba(255,46,136,.5);background:rgba(255,46,136,.1)}
.pt-tier b{font-size:15px;min-width:64px}
.pt-tier small{flex:1;color:var(--muted);font-size:12px}
.pt-tier span{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.mb-dots{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 8px}
""", 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
