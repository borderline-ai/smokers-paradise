#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 98 — two controls that a finger cannot press, and why 546 green checks
# never saw either of them.
#
# Marco, on an iPad, in under a minute: "not even the bag works. None of the
# following buttons work: SHOP THE SHELF, Disposable Vapes 50, Vape Hardware 13,
# E-Liquid 11, Nicotine Pouches 17, Exotic Snacks 5, Puffco & Dab 20."
#
# THE TEST WAS LYING, AND HERE IS EXACTLY HOW.
#
#     el.click()     dispatches the event straight AT the element. It does not
#                    hit-test. It "works" on a control that is underneath an
#                    overlay, behind pointer-events:none, or off the screen.
#
#     a real tap     goes to whatever document.elementFromPoint() returns at
#                    that coordinate. Nothing else ever receives it.
#
# test/allbuttons.py drives the app with el.click(). So it pressed all seven of
# those buttons, watched the app respond, and reported them working, because in
# its world they do. A test that cannot fail the way the product fails is not a
# test. test/hittest.py is new and asks elementFromPoint what is actually at
# each control's centre.
#
# 1. EVERY BUTTON IN AN EMPTY STATE IS TRANSPARENT TO TOUCH.
#
#        .hcm,.hcstate,.hcskel::after{pointer-events:none}
#
#    The intent is in the comment above it: "none of it ever sits above a
#    control" — it was written to stop the decorative animated mark eating taps
#    aimed at what is behind it. `.hcm` is that mark. `.hcstate` is the whole
#    state block, INCLUDING its buttons. So the rule aimed at the decoration
#    switched off the one control on the screen.
#
#    That is not just the bag. hcState() is the app's single shape for loading,
#    empty, offline, error, out of stock and expired hold. Every action button
#    on every one of those screens was dead. The bag is simply the one a
#    customer reaches first, because it is where the app opens with nothing in
#    it.
#
# 2. THE SAVE HEART IS DEAD ON EVERY PRODUCT CARD IN THE APP.
#
#    `.card .fav` is z-index 2. The product photograph in the same thumb is
#    also z-index 2, and it comes LATER in the DOM, so it wins the tie and
#    covers the heart. Measured: the heart's own centre hit-tests to IMG.
#    Tapping it does not save the product and does not open it either. It does
#    nothing at all, on all 259 cards.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the empty states accept a tap again --------------------------------
rep(""".hcm,.hcstate,.hcskel::after{pointer-events:none}""",
"""/* The MARK is decoration and must never eat a tap. The STATE BLOCK is not
   decoration: it holds the one button on the screen. Listing .hcstate here
   turned off every action button in every empty, offline, error and
   out-of-stock state in the app, including "Shop the shelf" and the six
   category buttons on an empty bag, which is the first screen a customer
   reaches with nothing in it. */
.hcm,.hcskel::after{pointer-events:none}
.hcstate .hcm{pointer-events:none}""")

# ---- 2. the heart sits above the photograph it is pinned to ----------------
rep(""".card .fav{position:absolute;top:7px;right:7px;width:26px;height:26px;border-radius:99px;display:grid;place-items:center;""",
"""/* The photograph in the same thumb is z-index 2 as well and comes after this
   in the DOM, so at equal z-index it painted over the heart and took the tap.
   The heart is pinned ON the picture, so it has to sit above it. */
.card .fav{position:absolute;top:7px;right:7px;width:26px;height:26px;border-radius:99px;display:grid;place-items:center;z-index:6;""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
