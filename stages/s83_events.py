#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 83 — the event list stops saying everything twice, and leads with what
# is actually on today.
#
# Two things were still wrong after the buttons came off.
#
# 1. The one-line ask repeated the description. "Free entry, and a free raffle
#    ticket at the door." followed by "Free entry. A raffle ticket at the
#    door." is the same duplication as five identical buttons, just quieter.
#    A description says WHAT IT IS. The ask says WHAT YOU DO. Neither says
#    both.
#
# 2. Opened in September, the list led with a festival held on April 19 and
#    ran on to a toy drive in December and a car meet in January. Three of the
#    five are dated and none of them is soon; two of them run at the counter
#    every week the shop is open. Those two go first, because they are the ones
#    a customer can act on today, and the dated ones follow in calendar order
#    so the list reads like a year rather than a pile.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


# ---- 1. the description describes ------------------------------------------
for old, new in [
    ("d:'Local vendors, live music, free tacos, a mechanical bull and 420 deals in "
     "our lot on Grand. Free entry, and a free raffle ticket at the door.'",
     "d:'Local vendors, live music, free tacos, a mechanical bull and 420 deals "
     "in our lot on Grand.'"),
    ("d:'Spend $10 or more to get one raffle entry. Prizes come off our own shelf.'",
     "d:'Prizes come off our own shelf, and we draw them at the counter.'"),
    ("d:'Monday to Wednesday. Spend $15 or more and spin the prize wheel at '\n"
     "       + 'the counter.'",
     "d:'The prize wheel lives on the counter and the prizes come off our shelf.'"),
    ("d:'Bring a toy for a child in need and take a free keychain with any purchase.'",
     "d:'We collect toys for kids in Nogales who would not get one otherwise.'"),
    ("d:'First meet of the year in our lot. New members welcome, come through.'",
     "d:'The first meet of the year, in our lot on Grand.'"),
]:
    if s.count(old) == 1:
        s = s.replace(old, new)
        print('  ok:', old[:52].replace('\n', ' '))
    else:
        print('  !! %d matches:' % s.count(old), old[:52].replace('\n', ' '))

# ---- 2. what runs every week comes first -----------------------------------
rep("""const GIVEAWAYS = STORE_CONTENT.community.map((c,i)=>({""",
"""/* What a customer can do TODAY comes first. Two of these run at the counter
   every week the shop is open; the other three are dated, and in September the
   list was opening on a festival held in April. The counter ones lead, the
   dated ones follow in calendar order. */
const EVENT_ORDER = ['Raffles', 'Spin-N-Win', 'Spring Celebration Fest',
                     'Toy Drive', 'Car meet'];
const GIVEAWAYS = STORE_CONTENT.community
  .slice()
  .sort((a, b) => {
    const ia = EVENT_ORDER.indexOf(a.t), ib = EVENT_ORDER.indexOf(b.t);
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
  })
  .map((c,i)=>({""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
