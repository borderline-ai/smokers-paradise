#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 99 — "someone buying a dab rig is most likely NOT looking for a lighter"
#
# Marco found a Clipper Micro Lighter recommended on the Lookah Seahorse Queen
# ELECTRIC Nectar Collector. The file already had a comment explaining why that
# must never happen: "an electronic dab device is heated by its own battery, so
# a flame is not an accessory to it, it is a contradiction." The rules were
# right. The CATALOGUE was wrong.
#
#   rx142  Lookah Seahorse Queen Electric Nectar Collector  $124.99  cat: parts
#
# A hundred and twenty five dollar electronic device, filed under Glass Parts &
# Accessories. So the rule that fired was the one for bongs and hand pipes,
# which legitimately wants bowls, downstems, ash catchers and a lighter. The
# recommendation engine did exactly what it was told about a product that had
# been told to it wrong.
#
# Auditing all 259 products' recommendations turned up three more of the same
# family, each one a thing that is true of the category but false of the
# product:
#
#   * Pulsar Quartz Nectar Collector -> a carb cap. A nectar collector has no
#     banger to cap. You touch its hot tip to the dish.
#   * GRAV 12mm and 16mm Tasters -> a 14mm funnel bowl. A taster is a
#     one-hitter. There is no joint on it for a bowl to go into.
#   * Session Goods Designer Bong -> a GRAV 14mm funnel bowl, while the Session
#     Goods Small Bowl Water Pipe Replacement, which is the part that actually
#     fits it, sits in the same catalogue unrecommended. That is the one that
#     stings: the app owns the right answer and offers the wrong one.
#
# FOUR CHANGES.
#
# 1. rx142 moves to dab, where an electric dab device belongs. It now reaches
#    the "Keep it running" rule, which wants cleaning supplies and tools, not
#    fire.
#
# 2. A rule for straws. A nectar collector, honey straw or electric dab straw
#    has no joint and no banger: its accessories are what you clean it with and
#    what you rest it on, and nothing that screws into a fitting it does not
#    have.
#
# 3. A rule for one-hitters. A taster, chillum or bat has no joint either.
#
# 4. THE SAME BRAND GOES FIRST. A replacement bowl, a downstem, a chamber, a
#    coil: these fit one maker's fitting and not another's. When the shop
#    stocks the matching part, that part leads. It is also just how somebody
#    behind a counter answers the question.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the device stops being filed as a glass part -----------------------
rep("""const CAT_CORRECTIONS = {""",
"""/* An electric nectar collector is a dab device, not a glass part. Filed under
   parts it inherited the bong rule and recommended a lighter for a thing with
   a battery in it. */
const CAT_CORRECTIONS = {
  rx142: 'dab',""")

# ---- 2 and 3. two rules for things with no joint ---------------------------
rep("""const COMPANION_RULES = [
  { label: 'Keep it running',""",
"""/* A straw is not a rig. A nectar collector, a honey straw, an electric dab
   straw: there is no joint on it and no banger in it, so a bowl, a downstem, an
   ash catcher and a carb cap are all parts for a fitting it does not have. What
   it actually needs is what you clean it with and something to rest the hot end
   on. This has to sit above the glass rules or `parts` and `rig` catch it
   first. */
const STRAW = /nectar collector|honey straw|dab straw|seahorse|\\bnectar\\b/i;
/* Same for a one-hitter. A taster, a chillum, a bat: no joint, no bowl. */
const ONEHIT = /\\btaster\\b|chillum|one.?hitter|\\bbat\\b|dugout/i;

const COMPANION_RULES = [
  { label: 'Keep it running',
    when: p => STRAW.test(p.brand + ' ' + p.name),
    want: /iso\\b|alcohol|swab|wipe|clean\\w*|\\bmats?\\b|dish|silicone jar|storage|\\bcase\\b|dab tools?|dabbers?/i },

  { label: 'Goes with this',
    when: p => ONEHIT.test(p.brand + ' ' + p.name),
    want: /clean\\w*|iso\\b|alcohol|swab|wipe|\\bcase\\b|storage|\\bgrinders?\\b|\\blighters?\\b|\\bscreens?\\b/i },

  { label: 'Keep it running',""")

# ---- 4. the part that actually fits goes first -----------------------------
rep("""    }).sort((a,b) => (b.featured?1:0)-(a.featured?1:0) || a.price-b.price).slice(0, 6);""",
"""    /* A bowl, a downstem, a chamber, a coil: these fit one maker's fitting and
       not another's. When the shop stocks the matching part it leads, which is
       also how the answer sounds from behind a counter. The Session Goods bong
       used to be offered a GRAV funnel bowl while the Session Goods replacement
       bowl sat in the same catalogue, unoffered. */
    }).sort((a,b) => ((b.brand===p.brand)?1:0)-((a.brand===p.brand)?1:0)
                  || (b.featured?1:0)-(a.featured?1:0)
                  || a.price-b.price).slice(0, 6);""")

# "More like this" should lead with the same brand too, then nearest price
rep("""  const near = PRODUCTS.filter(x => x.cat === p.cat && x.id !== p.id)
    .sort((a,b) => Math.abs(a.price - p.price) - Math.abs(b.price - p.price)).slice(0, 6);""",
"""  const near = PRODUCTS.filter(x => x.cat === p.cat && x.id !== p.id && x.published !== false)
    .sort((a,b) => ((b.brand===p.brand)?1:0)-((a.brand===p.brand)?1:0)
                || Math.abs(a.price - p.price) - Math.abs(b.price - p.price)).slice(0, 6);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
