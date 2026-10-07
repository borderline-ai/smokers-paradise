#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 178 — the card shows what the shop currently says.
#
# Two bugs, one cause: Member.refresh() was called from exactly one place —
# 900ms after the app loads — and nowhere else. So the card showed whatever
# was true when the page last loaded, forever.
#
# WHAT THAT BROKE, FIRST. Joining. The join is queued and posted, and the
# answer carries the member's standing, but flush() stored only the visit
# progress. So a brand new member's card had no points object and fell back to
# the punch-card rendering — the ten dots — on a shop running the points
# programme. Caught by opening it, not by a test: every test joins and then
# reloads, and a reload is exactly the thing that hid this.
#
# WHAT THAT BROKE, SECOND, AND WORSE. The counter credits a sale and the
# customer's card does not move. She is standing there. Her phone still says
# what it said before she paid. She has to close the app and open it again,
# and nobody knows to do that — they conclude it does not work.
#
# THREE PLACES NOW ASK, AND EACH ONE IS A MOMENT SOMEBODY LOOKS:
#
#   after a join lands      so the first card is the real one
#   opening the Rewards tab so looking at it is enough
#   returning to the app    so a phone that was in a pocket catches up
#
# All three are guarded on SP_API and on being a member, so the offline
# walkthrough does none of them and behaves exactly as stage 177 left it.
#
# The refresh is deliberately NOT a poll. A card open on a counter for an hour
# should not be asking every five seconds; it should ask when somebody looks.
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
# 1. A JOIN ENDS WITH THE REAL CARD, NOT A PLACEHOLDER.
# ---------------------------------------------------------------------------
rep("""      try{ localStorage.setItem(KEY + '_q', JSON.stringify(left)) }catch(e){}
      if(VIEW === 'rewards' && typeof renderRewards === 'function') renderRewards();
    },""",
"""      try{ localStorage.setItem(KEY + '_q', JSON.stringify(left)) }catch(e){}
      /* The join answer carries the visit progress but not the points
         standing, so a brand new member's card had nothing to render a
         balance from and fell back to the punch card. One read fixes it, and
         it is the same read the card does anywhere else. */
      if(SP_API && load() && m.token) await this.refresh();
      if(VIEW === 'rewards' && typeof renderRewards === 'function') renderRewards();
    },""")


# ---------------------------------------------------------------------------
# 2. LOOKING AT THE CARD IS ENOUGH.
#
# Placed after the screen has drawn from cache, so it appears instantly and
# corrects itself a moment later rather than showing a spinner. The re-render
# only happens if something actually changed, so a card that was already right
# does not flicker.
# ---------------------------------------------------------------------------
rep("""  $('#v-rewards').innerHTML = head + `<div class="ckwrap">${body}</div>`;
    if(typeof SHOP_REWARDS !== 'undefined' && SHOP_REWARDS.on) mbWire();
    return;""",
"""  $('#v-rewards').innerHTML = head + `<div class="ckwrap">${body}</div>`;
    if(typeof SHOP_REWARDS !== 'undefined' && SHOP_REWARDS.on) mbWire();
    mbFreshen();
    return;""")

rep("""function mbWire(){
  const g = id => document.getElementById(id);""",
"""/* ASK THE SHOP, THEN REDRAW IF THE ANSWER MOVED.

   Not a poll. A card left open on a counter for an hour should not be asking
   every five seconds; it should ask when somebody looks at it. Guarded so a
   second look while the first is still in flight does not stack up. */
let MB_FRESHENING = false;
function mbFreshen(){
  if(!SP_API || MB_FRESHENING) return;
  if(typeof Member === 'undefined' || !Member.joined) return;
  MB_FRESHENING = true;
  const was = JSON.stringify([Member.points, Member.progress()]);
  Member.refresh()
    .then(() => {
      const now = JSON.stringify([Member.points, Member.progress()]);
      /* Only redraw when something actually changed, so a card that was
         already right does not flicker under somebody's thumb. */
      if(was !== now && VIEW === 'rewards' && typeof renderRewards === 'function'){
        renderRewards();
      }
    })
    .catch(()=>{})
    .then(()=>{ MB_FRESHENING = false });
}

/* A phone that was in a pocket while the counter rang a sale catches up the
   moment it is looked at again. */
document.addEventListener('visibilitychange', () => {
  if(!document.hidden && VIEW === 'rewards') mbFreshen();
});

function mbWire(){
  const g = id => document.getElementById(id);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
