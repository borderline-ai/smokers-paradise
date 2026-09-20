#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 168 — the banners adapt once and then stop.
#
# Marco: "the banners do not adjust to the ipad size."
#
# He is right, and the cause is a single number. The campaign system is built
# on container queries, which was the correct decision, but it has exactly ONE
# breakpoint in it: 560px. Below that the banner is a phone banner. Above it
# the banner becomes the two-column composition and then nothing else ever
# happens, however wide the screen gets.
#
# Measured, with a touch pointer so the app runs full bleed the way it does on
# the installed iPad and not inside the desktop phone frame:
#
#     PHONE 390          lead banner   356 x 442    aspect 0.81   headline 33px
#     IPAD  834          lead banner   800 x 371    aspect 2.16   headline 40px
#     IPAD  1112 land    lead banner  1078 x 371    aspect 2.90   headline 40px
#
# The box more than doubles in width and gets SHORTER, from 442 to 371. The
# headline grows by seven pixels. So a composition designed as a portrait card
# is served on the iPad as a letterbox strip with phone-sized type stranded at
# one end of it, and the flattest one of the set is worse:
#
#     editor banner      358 x 232 on the phone   ->   802 x 232 on the iPad
#
# Identical height. Three and a half times wider than it is tall.
#
# ======================================================================
# THE FIX IS TWO MORE BREAKPOINTS, NOT A NEW LAYOUT
# ======================================================================
# Nothing is wrong with the compositions. They are simply never asked to grow.
# So the same container gets two more sizes above the one it has, and every
# measurement that should scale with the box does:
#
#     container 560   the composition it has today, unchanged on every phone
#     container 760   taller box, bigger headline, bigger offer, wider gutters
#     container 1000  taller again, for the iPad turned sideways
#
# What that does to the number that was wrong:
#
#     IPAD  834        aspect 2.16  ->  1.77      headline 40px  ->  52px
#     IPAD  1112 land  aspect 2.90  ->  2.07      headline 40px  ->  62px
#     editor banner    232px tall   ->  310px tall
#
# The product photographs are positioned in percentages of the box, so they
# grow with it on their own and no packshot is touched by this stage.
#
# NOT DONE HERE, DELIBERATELY. The two-up pair under the carousel is still one
# column on the iPad, because `.bpair` carries `container-type` itself and then
# tries to query itself, which can never match. Fixing that means the banners
# inside it start measuring the pair rather than their own width, and every
# composition rule in the campaign system reads that number. That is a real
# piece of work and it is not something to do in the hour before a demo.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


ANCHOR = """@container (min-width:560px){
  .ad.l-split,.ad.l-reverse{grid-template-rows:1fr;
    grid-template-columns:minmax(0,54%) 1fr;align-items:stretch;min-height:300px}
  .ad.l-split .ad-copy{grid-row:1;grid-column:1;padding:30px 12px 30px 30px}
  .ad.l-split .ad-art{grid-row:1;grid-column:2}
  .ad.l-reverse .ad-copy{grid-row:1;grid-column:2;padding:30px 30px 30px 12px}
  .ad.l-reverse .ad-art{grid-row:1;grid-column:1}
  .ad .ad-title{font-size:32px}
  .ad-offer b{font-size:54px}
}"""

TABLET = """

/* ==========================================================================
   THE TABLET SIZES OF THE SAME COMPOSITIONS

   Every block above stops at 560. On an iPad the campaign column is 802px
   and in landscape it is 1080px, so a banner written for 560 gets served at
   twice that width with the same height and the same type: a 2.16 letterbox
   with a phone headline in it. These two blocks are that composition at the
   sizes the column actually reaches.

   THE OFFERS PAGE HAD NO CONTAINER AT ALL. Every @container rule written for
   .ad was dead code, because nothing above an .ad was ever declared a
   container: on the Offers page the ad went from 358px wide on a phone to
   746px on an iPad with the same height and the same 26px title. The two
   holders are named below, and they are named separately on purpose. The
   Offers page stacks its ads full width, so its holder is the tablet width
   and the ad grows. The home page runs them along a rail as 340px cards, so
   its holder stays under every breakpoint here and those cards do not change
   at all.

   Only measurements change. The grid, the fields, the blocks and the product
   positions are all inherited, and every packshot is placed in percentages of
   the box, so the photographs scale with it and none of them is touched.
   ========================================================================== */
/* the two holders the offers and home ads sit in, so an .ad can finally
   measure something */
.adstack,.adwrap{container-type:inline-size}

@container (min-width:700px){
  /* the lead: the box gets its height back, and the type follows the box */
  .camp.lead{min-height:452px}
  .camp.lead .camp-copy{padding:40px 14px 40px 44px}
  .camp.lead .camp-head{font-size:52px}
  .camp.lead .camp-offer b{font-size:58px}
  /* a line of copy stops being readable long before 400px of it */
  .camp-sub{font-size:14.5px;max-width:32ch}
  .camp-kick{font-size:10.5px}
  .camp-cta{font-size:13px;padding:12px 20px}

  /* THE TALL ONE GOES BACK SIDE BY SIDE. Standing the product along the
     bottom of an 800px box leaves two small packs floating in a white field
     the size of the card. Every value below is the composition this banner
     already uses on a phone, restated at the width that suits it. */
  .camp.tall{grid-template-columns:minmax(0,1fr) 46%;grid-template-rows:1fr;
    min-height:330px;align-items:stretch}
  .camp.tall .camp-copy{grid-row:1;grid-column:1;padding:34px 10px 34px 34px}
  .camp.tall .camp-head{font-size:34px}
  .camp.tall .camp-shot{grid-row:1;grid-column:2;align-self:stretch}
  /* pulled in from the phone's 2%: at 800px the frame was cutting the
     packshot mid-spoon, which reads as a mistake rather than as a crop */
  .camp.tall .camp-lead{left:auto;right:5%;transform:none;bottom:9%;
    height:auto;max-height:86%;max-width:88%}
  .camp.tall .camp-back{left:auto;right:56%;transform:none;bottom:11%;
    height:auto;max-height:62%;max-width:54%}
  .camp.tall .camp-ground{left:auto;right:3%;transform:none;
    bottom:5%;width:76%;height:13px}
  .camp.tall .camp-block{width:200%;height:150%;left:-70%;top:-28%}

  /* the editorial one is the flattest of the set: same height on a phone and
     on an iPad until now */
  .camp.dark{min-height:310px}
  #hero .camp.dark{min-height:452px}
  .camp.dark .camp-head{font-size:34px}
  #hero .camp.dark .camp-head{font-size:52px}
  #hero .camp.dark .camp-copy{padding:0 44px 40px}

  .camp.award .aw-head{font-size:40px}
  .camp.award .aw-sub{font-size:15.5px;max-width:34ch}
  .camp.award .aw-rule{width:72px;margin:22px 0 20px}

  .ad.l-split,.ad.l-reverse{min-height:380px}
  .ad.l-split .ad-copy{padding:38px 14px 38px 38px}
  .ad.l-reverse .ad-copy{padding:38px 38px 38px 14px}
  /* THE STACK LAYOUT. It stands its packs along the bottom, which at 746px
     wide leaves a field the size of the card with two small bars in it. It
     goes side by side like the split. The .c-tre selector is named alongside
     it because that campaign restates every one of these values at a higher
     specificity further up the file, and a rule that loses is worse than no
     rule: it looks done and is not. */
  .ad.l-stack,.ad.c-tre.l-stack{grid-template-rows:1fr;
    grid-template-columns:minmax(0,52%) 1fr;align-items:stretch;min-height:390px}
  .ad.l-stack .ad-copy,.ad.c-tre.l-stack .ad-copy{grid-row:1;grid-column:1;
    align-self:center;padding:38px 14px 38px 38px}
  .ad.l-stack .ad-art,.ad.c-tre.l-stack .ad-art{grid-row:1;grid-column:2;
    position:relative;height:auto;align-self:stretch;overflow:visible}
  .ad.l-stack .ad-p.lead,.ad.c-tre.l-stack .ad-p.lead{left:auto;right:4%;
    bottom:12%;transform:rotate(-3deg);max-height:66%;max-width:86%}
  .ad.l-stack .ad-p.back,.ad.c-tre.l-stack .ad-p.back{left:auto;right:46%;
    bottom:18%;transform:rotate(6deg);max-height:48%;max-width:52%}
  .ad.c-tre.l-stack .ad-glow{left:70%;top:auto;bottom:4%;width:96%}
  .ad.l-stack .ad-floor{left:auto;right:6%;width:62%;bottom:8%}
  /* the art cell is pinned to 196px further up the file, which in a side by
     side layout leaves the packs floating at the top of the column */
  .ad.l-split .ad-art,.ad.l-reverse .ad-art{height:auto;align-self:stretch}
  .ad .ad-title{font-size:40px}
  .ad-offer b{font-size:66px}
  .ad-sub{font-size:14.5px;max-width:32ch}
}

@container (min-width:980px){
  /* the iPad turned sideways. The cap on height is deliberate: the banner may
     take most of a landscape screen, never all of it, or nothing below it
     exists as far as the customer is concerned. */
  .camp.lead{min-height:520px}
  .camp.lead .camp-copy{padding:48px 16px 48px 54px}
  .camp.lead .camp-head{font-size:62px}
  .camp.lead .camp-offer b{font-size:70px}
  .camp-sub{font-size:15.5px;max-width:34ch}

  .camp.tall{min-height:380px}
  .camp.tall .camp-copy{padding:42px 12px 42px 44px}
  .camp.tall .camp-head{font-size:40px}

  .camp.dark{min-height:352px}
  #hero .camp.dark{min-height:520px}
  .camp.dark .camp-head{font-size:38px}
  #hero .camp.dark .camp-head{font-size:62px}
  #hero .camp.dark .camp-copy{padding:0 54px 48px}

  .camp.award .aw-head{font-size:48px}
  .camp.award .aw-sub{font-size:16.5px}

  .ad.l-split,.ad.l-reverse{min-height:430px}
  .ad.l-stack,.ad.c-tre.l-stack{min-height:440px}
  .ad .ad-title{font-size:48px}
  .ad-offer b{font-size:78px}
}"""

# The campaign CSS is written in several passes down the file, and some of the
# later passes restate the same selectors, so a block placed beside the 560
# one loses to them. It goes at the end of the last stylesheet instead, where
# nothing restates anything.
TAIL = """.feedrow img{max-width:100%!important;max-height:100%!important}
"""
assert s.count(ANCHOR) == 1, 'the 560 block this extends is not where it was'
rep(TAIL, TAIL + TABLET)

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
