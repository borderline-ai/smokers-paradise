#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 179 — the Account screen was still on the old programme.
#
# Found on a phone in the shop, mid-demo, which is the worst place to find
# anything. Two strings on one screen:
#
#   "Paradise Rewards / Every 10 visits is $10 off"
#       The rewards row never learned about points. Stage 177 rewrote the card
#       and the join sheet and missed this, because the row builds its own
#       sentence from SHOP_REWARDS.visitsFor rather than asking the card.
#
#   "Name and phone / Used for pickup and your ready text"
#       A fourth survivor of the SMS sweep. Stages 174 and 175 took out the
#       counter button, the ticket state, the checkout copy, the join prompt,
#       the switches, the front-page box and the Spanish — and left this one,
#       for the same reason as the others: it is prose on a settings row, and
#       the suites assert on controls.
#
# The pattern is now unmistakable. Every miss has been a sentence a person
# reads rather than a control a test can press. Worth remembering the next
# time something is "swept".
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


# The rewards row: a balance and the nearest rung where there is one.
rep("""      <div class="t"><b>${esc(SHOP_REWARDS.name)}</b><small>${Member.joined
        ? esc(Member.data.code) + ' &middot; ' + Member.progress().visits + ' of ' + SHOP_REWARDS.visitsFor + ' visits'
        : 'Every ' + SHOP_REWARDS.visitsFor + ' visits is ' + esc(SHOP_REWARDS.reward)}</small></div>""",
"""      <div class="t"><b>${esc(SHOP_REWARDS.name)}</b><small>${(function(){
        /* The points programme, where the shop runs one. Asks Member rather
           than building its own sentence out of visitsFor, which is how this
           row got left behind when the card was rewritten. */
        const P = (typeof Member !== 'undefined') ? Member.points : null;
        if(P){
          return Member.joined
            ? esc(Member.data.code) + ' &middot; ' + P.balance.toLocaleString() + ' points' +
              (P.next ? ' &middot; ' + P.next.short.toLocaleString() + ' to ' + esc(P.next.label) : '')
            : 'Every $1 earns ' + SP_POINTS_PER_DOLLAR + ' points';
        }
        if(SP_TIERS.length && !Member.joined){
          return 'Every $1 earns ' + SP_POINTS_PER_DOLLAR + ' points';
        }
        return Member.joined
          ? esc(Member.data.code) + ' &middot; ' + Member.progress().visits + ' of ' + SHOP_REWARDS.visitsFor + ' visits'
          : 'Every ' + SHOP_REWARDS.visitsFor + ' visits is ' + esc(SHOP_REWARDS.reward);
      })()}</small></div>""")

# The last "text" claim on a customer surface.
rep("""<div class="t"><b>Name and phone</b><small>Used for pickup and your ready text</small></div>""",
    """<div class="t"><b>Name and phone</b><small>So staff can call your name, and ring you about an order</small></div>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
