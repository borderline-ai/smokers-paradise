#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 167 — a reward already given away does not get re-priced.
#
# Found by the counter test, not by reading the code. The sequence:
#
#     ten visits  ->  reward taken off  ->  card correctly back to 0 of 10
#     owner then changes the rule to six visits
#     card jumps to 4 OF 6
#
# Four visits appear out of nothing, on a card whose whole claim is that it can
# never be ahead of the shop. The cause is that progress() priced every past
# redemption at TODAY'S rule:
#
#     used = redeemed.length * SHOP_REWARDS.visitsFor
#
# so the ten visits that were spent on a ten-visit reward were retroactively
# re-billed at six, and the change of rule handed the customer four free ones.
# Tilt it the other way — six to twelve — and the same line silently takes
# visits away from someone who earned them.
#
# A redemption is a thing that happened at the till on a particular day under
# the rule that was running that day, so it now carries its own price and
# progress() spends what was actually spent. Rules set before this stage have
# no price recorded; those fall back to the current one, which is the only
# guess available and is noted here rather than hidden.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


rep("""      m.redeemed.push({at: new Date().toISOString(), reward: SHOP_REWARDS.reward});""",
    """      /* the price is stamped on the redemption, because the rule can change
         tomorrow and this one was already paid for */
      m.redeemed.push({at: new Date().toISOString(), reward: SHOP_REWARDS.reward,
                       cost: SHOP_REWARDS.visitsFor});""")

rep("""      const used = (d.redeemed || []).length * SHOP_REWARDS.visitsFor;""",
    """      /* spend what was actually spent. A redemption from before the price
         was stamped has nothing to go on, so it takes today's rule. */
      const used = (d.redeemed || []).reduce(
        (a, r) => a + (r && r.cost ? r.cost : SHOP_REWARDS.visitsFor), 0);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
