#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 111 — six pixels is not a button.
#
# Marco, on the iPad: "I've already told you MOST of this stuff and not even
# the bag works. None of the following buttons work: SHOP THE SHELF /
# Disposable Vapes50 Vape Hardware13 E-Liquid11 Nicotine Pouches17 Exotic
# Snacks5 Puffco & Dab20"
#
# Those seven were a real fault — `.hcstate` carried `pointer-events:none`,
# which turned off every action button in every empty state — and stage 98
# fixed them. Verified with a real tap: all seven work.
#
# But "buttons don't work" on a touch screen has a second cause that no hit
# test finds, because the control IS reachable: it is simply too small for a
# finger. A mouse pointer is one pixel and a fingertip is about forty five, and
# every platform's guidance says the same number: 44 points, minimum, for
# anything a person taps.
#
# MEASURED ACROSS EVERY SCREEN. Forty eight distinct controls are under 40px on
# their short side. Most are chips at 31 to 32px high, which is what a chip is
# everywhere, in a row where a miss lands on another chip and costs nothing.
# These seven are not that:
#
#     6 x 6     the hero carousel dots, five of them, on the FIRST screen
#    26 x 26    the save heart, on all 259 cards
#    27 x 27    the rail scroll arrows
#    28 x 30    the announcement bar arrows
#    30 x 30    Back
#    44 x 18    Privacy
#    37 x 18    Terms
#
# Six by six. On the first screen of the app. A fingertip covers that dot and
# the four next to it and about eight millimetres of the picture behind them.
# There is no way to hit it on purpose and no way to know which one you hit.
#
# THE FIX DOES NOT CHANGE HOW ANY OF IT LOOKS. Each of these already draws at
# the size it should: a 6px dot is a 6px dot. What is added is an invisible
# target around it, in a pseudo-element, so the drawing stays exactly as it is
# and the area a finger has to land in becomes 44px.
#
# The dots are the one place that needs a compromise: they sit 7px apart, so
# giving each a 44px wide target would put five overlapping targets on top of
# each other and the wrong offer would win. They get the full 44 in height and
# half the gap on each side, which is the most a row of five can carry without
# stealing from its neighbours — and the arrows either side of them, now 44px
# themselves, are the reliable way through the carousel.
#
# This was found by measuring, not by a report, and it is the likeliest reason
# a control Marco pressed did nothing even after it was reachable.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""#hero .dots button{width:6px;height:6px;border-radius:99px;padding:0;border:0;
  background:rgba(255,123,200,.30);box-shadow:none;
  transition:width .2s,background .2s}""",
"""#hero .dots button{position:relative;width:6px;height:6px;border-radius:99px;padding:0;border:0;
  background:rgba(255,123,200,.30);box-shadow:none;
  transition:width .2s,background .2s}
/* THE DOT YOU SEE IS 6px. THE DOT YOU CAN HIT IS 44 TALL.
   A fingertip is about 45px across and these sit 7px apart, so five of them
   fit inside one fingerprint. The drawing does not change: the target is an
   invisible box around it. Full height, and half the gap on each side, which
   is all a row of five can take without stealing from its neighbours — which
   is why the arrows either side are the reliable way through the carousel. */
#hero .dots button::after{content:'';position:absolute;left:50%;top:50%;
  width:calc(100% + 7px);height:44px;transform:translate(-50%,-50%)}
#hero .dots{padding-bottom:2px}""")

# ---- the save heart, on 259 cards ------------------------------------------
rep(""".card .fav{position:absolute;top:7px;right:7px;width:26px;height:26px;""",
"""/* 26px of white circle, 44px of target around it. The heart is in the corner
   of a 161px tile, so the bigger target cannot reach anything else. */
.card .fav::after{content:'';position:absolute;left:50%;top:50%;
  width:44px;height:44px;transform:translate(-50%,-50%)}
.card .fav{position:absolute;top:7px;right:7px;width:26px;height:26px;""")

# ---- the rail arrows, the announcement arrows, Back ------------------------
rep("""/* deal cards */""",
"""/* ---- WHAT A FINGER HAS TO LAND IN ----
   Every one of these draws at the size it should; what was missing was the
   area around the drawing. 44px is the number every platform's guidance gives
   and the number a fingertip actually is. Invisible, so nothing on any screen
   moves. */
.arw,.nb,.bk{position:relative}
.arw::after,.nb::after,.bk::after{content:'';position:absolute;left:50%;top:50%;
  width:44px;height:44px;transform:translate(-50%,-50%)}
/* the footer's legal links: 18px tall type in a row with room under it */
.foot .fl button,.sf-legal button{position:relative}
.foot .fl button::after,.sf-legal button::after{content:'';position:absolute;
  left:0;right:0;top:50%;height:44px;transform:translateY(-50%)}

/* deal cards */""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
