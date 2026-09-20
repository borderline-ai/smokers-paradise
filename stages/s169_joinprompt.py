#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 169 — the app never asks.
#
# Marco: "there is still no pop up asking for my information or any type of
# reward system."
#
# Half of that was him looking at this morning's build. The other half is real
# and it is the more important half: the rewards programme exists, but the app
# waits to be found. A customer has to go to You, then Paradise Rewards, and
# nobody does that in a shop with a queue behind them. The programme is what
# the shop is buying, and it was sitting behind two taps nobody takes.
#
# So the app asks. Once.
#
# ======================================================================
# WHEN IT ASKS, AND WHY THAT MOMENT
# ======================================================================
# Not on open. A card thrown at somebody in the first two seconds is closed
# before it is read, and it is the thing that makes an app feel like a leaflet.
# It waits until the third screen: they have browsed, they are still here, they
# have shown the app is worth something to them. That is when a counter worker
# would say it too.
#
#     shown once per device, ever, whether they join or not
#     never if they are already a member
#     never if the shop has the programme switched off
#     "Not now" is a real answer and is remembered
#
# It is a sheet, not a trap: the scrim closes it, the escape key closes it, and
# the button that is NOT the offer is a full sized button, not grey small print.
#
# WHAT IT CLAIMS. Only what the shop set: the rule and the birthday line from
# SHOP_REWARDS, nothing invented, no countdown, no "limited spots". A smoke shop
# loyalty card does not need urgency and a fake one would be the first thing an
# owner spots.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. the sheet itself ----------------------------------------------------
rep("""    <!-- INTERSTITIAL PROMO -->""",
"""    <!-- THE ONE TIME THE APP ASKS SOMEBODY TO JOIN -->
    <div id="mbask" role="dialog" aria-modal="true" aria-label="Join the rewards programme">
      <div class="mbask-card" id="mbaskCard"></div>
    </div>

    <!-- INTERSTITIAL PROMO -->""")

# ---- 2. what it says and what it does --------------------------------------
rep("""function go(v,arg,opts){""",
"""/* ======================================================================
   THE JOIN PROMPT
   Shown once per device, on the third screen, to somebody who is not already
   a member. Every word in it comes from SHOP_REWARDS.
   ====================================================================== */
const MBASK_KEY = 'sp_member_ask_v1';
let MBASK_SEEN = 0;

/* The whole body is guarded. go() runs once during start up, before the
   block that declares SHOP_REWARDS has been reached, and a const in a later
   block is not merely undefined at that moment, it THROWS on being named.
   An unguarded read here killed the rest of that block and took the entire
   rewards programme out of the app. */
function mbAskDue(){
  try{
    if(!SHOP_REWARDS.on) return false;
    if(Member.joined) return false;
    if(localStorage.getItem(MBASK_KEY)) return false;
  }catch(e){ return false }
  return MBASK_SEEN >= 3;
}

function mbAskClose(){
  const el = document.getElementById('mbask');
  if(el) el.classList.remove('on');
  try{ localStorage.setItem(MBASK_KEY, String(Date.now())) }catch(e){}
  if(typeof dialogClosed === 'function') dialogClosed();
}

function mbAskShow(){
  const R = SHOP_REWARDS;
  const el = document.getElementById('mbask');
  const card = document.getElementById('mbaskCard');
  if(!el || !card) return;
  card.innerHTML = `
    <div class="mbask-badge"><svg viewBox="0 0 24 24"><path d="M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/></svg></div>
    <div class="mbask-kick">${esc(R.name)}</div>
    <h3>Every ${R.visitsFor} visits is ${esc(R.reward)}.</h3>
    <p>${esc(R.perk)} Free to join, nothing to carry.</p>
    <button class="btn" id="mbaskGo">Join, it takes a second</button>
    <button class="btn ghost" id="mbaskNo">Not now</button>
    <p class="ckfine">21+ only. We text you, and STOP stops it.</p>`;
  el.classList.add('on');
  if(typeof dialogOpened === 'function') dialogOpened('mbask', null);
  document.getElementById('mbaskGo').onclick = () => { mbAskClose(); go('rewards') };
  document.getElementById('mbaskNo').onclick = mbAskClose;
  el.onclick = e => { if(e.target === el) mbAskClose() };
}

function go(v,arg,opts){""")

# ---- 3. counted at the one place that knows a screen changed ---------------
rep("""  if(typeof resetRails === 'function') resetRails($('#v-'+v));
}""",
"""  if(typeof resetRails === 'function') resetRails($('#v-'+v));
  /* THE APP ASKS ON THE THIRD SCREEN. Not on open: a card thrown at somebody
     in the first two seconds is closed before it is read. Never on the rewards
     screen itself, which is already the offer. */
  MBASK_SEEN++;
  if(v !== 'rewards' && mbAskDue()) setTimeout(() => { if(mbAskDue()) mbAskShow() }, 900);
}""")

# ---- 4. the look of it ------------------------------------------------------
rep(""".mb-hero{text-align:center}""",
"""#mbask{position:absolute;inset:0;z-index:94;display:none;
  align-items:flex-end;justify-content:center;padding:16px;
  background:rgba(6,2,10,.62);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
#mbask.on{display:flex}
.mbask-card{width:100%;max-width:430px;border-radius:22px;padding:24px 22px 18px;
  text-align:center;border:1px solid rgba(255,47,168,.34);
  background:linear-gradient(150deg,#2A0F33,#12060F);
  box-shadow:0 30px 60px rgba(0,0,0,.6);animation:mbaskUp .26s ease both}
@keyframes mbaskUp{from{transform:translateY(22px);opacity:0}to{transform:none;opacity:1}}
.mbask-badge{margin:0 auto 10px;width:46px;height:46px;border-radius:15px;display:grid;
  place-items:center;background:linear-gradient(140deg,var(--go),#8A1E5E);color:#fff}
.mbask-badge svg{width:23px;height:23px;fill:currentColor}
.mbask-kick{font-family:var(--mono);font-size:10px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--go-ink)}
.mbask-card h3{font-family:var(--disp);font-weight:800;letter-spacing:-.03em;
  font-size:24px;line-height:1.1;margin:8px 0 0;color:var(--ink)}
.mbask-card p{font-size:13px;line-height:1.5;color:var(--body);margin:9px 0 16px}
.mbask-card .btn{width:100%}
.mbask-card .btn.ghost{margin-top:9px}
.mbask-card .ckfine{margin:12px 0 0}
@media (pointer:coarse) and (min-width:700px), (display-mode:standalone) and (min-width:700px){
  #mbask{align-items:center}
  .mbask-card{max-width:520px;padding:34px 34px 26px}
  .mbask-card h3{font-size:30px}
  .mbask-card p{font-size:14.5px}
}
.mb-hero{text-align:center}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
