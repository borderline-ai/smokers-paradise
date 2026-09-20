#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 117 — nothing gets cut off. One bug, most of his list.
#
# Marco, for the fourth time: "There should not be any cropped pictures like
# those where you can only see the tip of the disposable vapes, the tip of the
# vape hardware... and the e-liquid category has a picture of THE TOP OF A
# E-LIQUID BOTTLE INSTEAD OF AN ACTUAL E-LIQUID BOTTLE."
#
# Last time I told him a tile with object-fit:contain could not crop. I was
# wrong, and I should have measured instead of explaining. Measured now:
#
#     .ctile .ph img{width:78%;height:78%;object-fit:contain}
#
#     the tile             104 x 104
#     the picture drawn     57 x 234      171px hanging out of the bottom
#     of the picture shown         27%
#
# A PERCENTAGE HEIGHT NEEDS A PARENT WITH A DEFINITE HEIGHT. `.ph` is a grid
# box that takes its height from its content, so `height:78%` resolves to
# `auto`, the image's own aspect ratio takes over, and a 103 x 432 vape renders
# 234px tall inside a 104px box with overflow:hidden on it. object-fit never
# got a chance: the BOX was already the wrong size before object-fit was asked
# anything.
#
# THE SAME THREE WORDS APPEAR IN FOUR MORE PLACES, and they explain almost
# every picture complaint in his message:
#
#   .spotitem .sp img    the Puffco band. He said "the puffcos sizes just look
#                        a bit disproportionate". They are not disproportionate.
#                        The Hot Knife is showing 9% of itself, the Peak Pro
#                        46%, the Peak 54%, the Proxy 59% — each sliced by a
#                        different amount, which is exactly what "the sizes look
#                        wrong" looks like.
#   .ctile .ph img       the department tiles: the tip of a vape, the tip of a
#                        pod, the top of a bottle.
#   .ffimg img           the Find Your Fit rows, at 24%, 39% and 83%.
#   .feedrow img         the Instagram strip, at 32%.
#
# And separately, THE BANNERS. `.ad-p.lead{bottom:-6%; max-height:126%}` — the
# artwork is deliberately hung off the edge of the card, and `.ad` clips. As a
# composition idea that is a real one; as a result it slices a vape down the
# left side, which is what Marco has pointed at twice: "the full left side of
# the vape is just cropped". A product sliced by a card edge does not read as
# style, it reads as a mistake, and he is the one looking at it. Every piece of
# banner artwork now sits fully inside its own card. The vapes and the
# promotions are untouched — he asked for that specifically — only the frame
# they sit in has changed.
#
# There is now a test for this, test/cropcheck.py, which asks every picture on
# every screen how much of itself it is actually showing. It should have
# existed before I told him it could not happen.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- 1. the department tiles ----------------------------------------------
# There are TWO rules for this image, 2900 lines apart, and the later one wins:
#   1638  .ctile .ph img{width:78%;height:78%}
#   4583  .ctile .ph img{width:auto;height:auto;max-width:74%;max-height:74%}
# Both carry the same fault. max-height:74% of a grid box with no height of its
# own resolves to none, so the picture takes its intrinsic size capped only by
# its width. Fixing the first one changed nothing at all, which is its own
# lesson: fix the rule that wins, and then make sure it keeps winning.
rep(""".ctile .ph img{width:78%;height:78%;object-fit:contain;transition:transform .32s var(--spring)}""",
""".ctile .ph img{object-fit:contain;transition:transform .32s var(--spring)}""")
rep(""".ctile .ph img{position:relative;z-index:2;width:auto;height:auto;
  max-width:74%;max-height:74%;object-fit:contain;""",
"""/* ABSOLUTE, SO THE BOX HAS A DEFINITE SIZE BEFORE object-fit IS ASKED.
   max-height:74% against a grid box with no height of its own resolves to
   none, the picture takes its intrinsic ratio, and a 103x432 vape draws 234px
   tall inside a 104px tile: 27% of it shown, which is the tip of a vape. */
.ctile .ph img{position:absolute;z-index:2;inset:12%;width:76%;height:76%;
  max-width:none;max-height:none;object-fit:contain;object-position:center;""")

# ---- 2. the Puffco band: not disproportionate, sliced ----------------------
rep(""".spotitem .sp img{max-height:84%;max-width:78%;object-fit:contain;filter:drop-shadow(0 8px 14px rgba(0,0,0,.5))}""",
"""/* "The puffcos sizes just look a bit disproportionate." They were not:
   the Hot Knife was showing 9% of itself and the Peak 54%, each cut off at
   the bottom of the tile by a different amount. Same definite-box fix, and
   now every device in the row is measured against the same frame. */
.spotitem .sp img{position:absolute;inset:8%;width:84%;height:84%;
  max-height:none;max-width:none;object-fit:contain;object-position:center;
  filter:drop-shadow(0 8px 14px rgba(0,0,0,.5))}""")

# ---- 3. the fit tool rows --------------------------------------------------
rep(""".ffimg img{width:86%;height:86%;object-fit:contain}""",
""".ffimg img{position:absolute;inset:7%;width:86%;height:86%;
  object-fit:contain;object-position:center}""")
rep(""".ffimg{width:44px;height:44px;border-radius:9px;background:var(--card2);display:grid;place-items:center;flex:none;overflow:hidden}""",
""".ffimg{position:relative;width:44px;height:44px;border-radius:9px;background:var(--card2);display:grid;place-items:center;flex:none;overflow:hidden}""")

# ---- 4. the banner artwork stays inside its own card -----------------------
rep(""".ad.l-split .ad-p.lead{right:6%;bottom:-6%;max-height:126%;max-width:52%}
.ad.l-split .ad-p.back{right:44%;bottom:2%;max-height:92%;max-width:40%}""",
"""/* NOTHING HANGS OFF THE CARD ANY MORE.
   A product bled past the edge is a composition idea; a vape with its left
   side sliced off is a mistake, and the person looking at it has said so
   twice. Same positions, same artwork, sizes that fit. */
.ad.l-split .ad-p.lead{right:5%;bottom:4%;max-height:88%;max-width:48%}
.ad.l-split .ad-p.back{right:42%;bottom:6%;max-height:72%;max-width:36%}""")

rep(""".ad.l-stack .ad-p.lead{left:52%;bottom:-10%;transform:translateX(-50%) rotate(-3deg);
  max-height:132%;max-width:88%}
.ad.l-stack .ad-p.back{left:12%;bottom:12%;transform:rotate(6deg);
  max-height:82%;max-width:52%}""",
""".ad.l-stack .ad-p.lead{left:52%;bottom:5%;transform:translateX(-50%) rotate(-3deg);
  max-height:88%;max-width:72%}
.ad.l-stack .ad-p.back{left:10%;bottom:12%;transform:rotate(6deg);
  max-height:66%;max-width:44%}""")

rep(""".ad.l-hero .ad-p.lead{left:66%;top:-4%;transform:translateX(-50%);
  max-height:82%;max-width:60%}""",
""".ad.l-hero .ad-p.lead{left:66%;top:4%;transform:translateX(-50%);
  max-height:76%;max-width:56%}""")

rep(""".ad.l-reverse .ad-p.lead{left:6%;bottom:-4%;max-height:122%;max-width:52%}
.ad.l-reverse .ad-p.back{left:46%;bottom:6%;max-height:84%;max-width:40%}""",
""".ad.l-reverse .ad-p.lead{left:5%;bottom:4%;max-height:88%;max-width:48%}
.ad.l-reverse .ad-p.back{left:44%;bottom:8%;max-height:68%;max-width:36%}""")

rep(""".ad.c-puffco .ad-p.lead{bottom:6%;max-height:104%}
.ad.c-puffco .ad-p.back{bottom:12%;max-height:74%}""",
""".ad.c-puffco .ad-p.lead{bottom:6%;max-height:86%}
.ad.c-puffco .ad-p.back{bottom:12%;max-height:66%}""")

rep(""".ad.l-hero .ad-p.lead{left:64%;top:3%;transform:translateX(-50%);""",
""".ad.l-hero .ad-p.lead{left:64%;top:5%;transform:translateX(-50%);""")

# the tallest rotated pieces on the TRE stack ran past the bottom too
rep(""".ad.c-tre.l-stack .ad-p.lead{""",
"""/* the rotated pieces reached furthest of all, because a rotation grows the
   box it needs and these were already at 132% */
.ad.c-tre.l-stack .ad-p.lead{max-height:84%;""")

# ---- 5. the Instagram strip -----------------------------------------------
rep(""".feedrow{display:flex;gap:11px;overflow-x:auto;padding:2px 15px 6px;""",
"""/* the strip clips horizontally by design; its pictures must not clip too */
.feedrow img{max-width:100%;max-height:100%;object-fit:contain}
.feedrow{display:flex;gap:11px;overflow-x:auto;padding:2px 15px 6px;""")

# ---- 6. and a last word, so no earlier rule can take it back --------------
# Every one of these boxes has had two or three rules written for it over the
# life of this build, in three stylesheets, and the one that wins is not the
# one you are looking at: fixing .ctile .ph img at line 1638 changed nothing,
# because a second rule for the same selector 2900 lines later was winning.
# This block is last in the last stylesheet, so it wins, and it says the same
# thing four times: the frame has a size of its own, and the picture is fitted
# inside it.
rep(""".gr-sum b{font-size:40px;line-height:1}
</style>""",
""".gr-sum b{font-size:40px;line-height:1}

/* ======================================================================
   NOTHING GETS CUT OFF
   A percentage height needs a parent with a definite height. Every box below
   is a grid or flex cell that takes its height from its content, so every
   percentage height written for the picture inside it silently became `auto`,
   the picture took its own aspect ratio, and the frame — which does clip —
   showed whatever part happened to fit. Measured before this block: the Hot
   Knife was showing 9% of itself, a department tile 27%, a Find Your Fit row
   24%. Absolute inset gives the box a size, and only then does object-fit
   have anything to do.
   ====================================================================== */
.ctile .ph{position:relative}
.ctile .ph img{position:absolute!important;inset:12%!important;
  width:76%!important;height:76%!important;
  max-width:none!important;max-height:none!important;
  object-fit:contain!important;object-position:center!important}
.spotitem .sp{position:relative}
.spotitem .sp img{position:absolute!important;inset:9%!important;
  width:82%!important;height:82%!important;
  max-width:none!important;max-height:none!important;
  object-fit:contain!important;object-position:center!important}
.ffimg{position:relative}
.ffimg img{position:absolute!important;inset:8%!important;
  width:84%!important;height:84%!important;
  max-width:none!important;max-height:none!important;
  object-fit:contain!important;object-position:center!important}
#cmpbar .cth{position:relative}
#cmpbar .cth img{position:absolute!important;inset:8%!important;
  width:84%!important;height:84%!important;object-fit:contain!important}
.feedrow img{max-width:100%!important;max-height:100%!important}
</style>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
