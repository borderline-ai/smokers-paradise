#!/usr/bin/env python3
# Stage 67 — the second look at the four rebuilt compositions.
#
# Each one was rendered, screenshotted and read before this file was written.
#
#   AWARD    The sub-line wrapped to "Voted Best of Santa Cruz / County." and
#            "Voted" asserts a mechanism nobody has confirmed. The plaque
#            carries both facts, so the kicker takes the county and the sub
#            takes the shop's own words from their post.
#   RAFFLE   "Spend $10+ for a raffle entry" as the headline and "$10 to enter"
#            directly under it said the same thing twice in two type sizes.
#   TRE      The photograph as a full-bleed ground put the copy straight onto
#            the packaging, and the pale top of the shot bleached the card.
#            Two zones instead: copy on cacao, the bar whole underneath it.
#   GLASS    The headline still crossed the base of the left beaker.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:60].replace('\n', ' '))


rep("""    kicker:'Nogales International',
    headline:'Best Smoke Shop 2026',
    sub:'Voted Best of Santa Cruz County.',""",
    """    kicker:'Best of Santa Cruz County',
    headline:'Best Smoke Shop 2026',
    sub:'Thank you, Nogales.',""")

rep("""    kicker:'Raffle',
    title:'Spend $10+\\nfor a raffle entry',
    offer:'$10', offerSub:'to enter',
    subtitle:'One entry per visit. Ask at the counter and we\\u2019ll write your name on the ticket.',""",
    """    kicker:'Raffle',
    title:'Draw at\\nthe counter',
    offer:'$10', offerSub:'to enter',
    subtitle:'Spend $10 or more and we\\u2019ll write your name on a ticket. One entry per visit.',""")

CSS = r'''
/* ---- the award, second pass ------------------------------------------- */
.camp.award .aw-sub{max-width:30ch;color:#E6DCCB}
.camp.award .aw-kick{letter-spacing:.16em}

/* ---- the raffle ticket, second pass ------------------------------------
   The perforation was drawn outside the card and clipped away by its own
   overflow. */
.ad.l-ticket::before{top:0}
.ad.l-ticket::after{bottom:0}

/* ==========================================================================
   TRE HOUSE, SECOND PASS
   Full bleed put the headline on the packaging and the pale top of the
   photograph bleached the card. Two zones: the copy owns a solid cacao
   ground, the bar owns the band underneath it and is never cropped by text.
   ========================================================================== */
.ad.c-tre.l-photo{
  display:grid;
  grid-template-rows:auto 46%;
  min-height:420px;
  background:linear-gradient(168deg,#2A1508 0%,#3E2109 46%,#20100A 100%);
}
.ad.c-tre.l-photo .ad-copy{
  grid-row:1;grid-column:1;
  align-self:start;
  background:none;
  padding:26px 20px 14px;
}
.ad.c-tre.l-photo .ad-art,.ad.c-tre.l-photo .photoart{
  grid-row:2;grid-column:1;
  position:relative;inset:auto;
  overflow:hidden;
}
.ad.c-tre.l-photo .ad-photo{
  position:absolute;inset:0;width:100%;height:100%;
  object-fit:cover;object-position:center 46%;
}
/* the seam between the two zones is a fade, not a cut */
.ad.c-tre.l-photo .ad-art::before{
  content:"";position:absolute;left:0;right:0;top:0;height:38%;z-index:2;
  background:linear-gradient(to bottom, #341B09 0%, rgba(52,27,9,.55) 46%, rgba(52,27,9,0) 100%);
}
.ad.c-tre .ad-sub{color:#EFE1CE}

/* ---- glass, second pass: the bases clear the headline ---------------- */
.ad.c-glass.l-hero .ad-p.lead{top:-1%;max-height:52%}
.ad.c-glass.l-hero .ad-p.back{top:3%;max-height:40%}
.ad.c-glass.l-hero .ad-copy{
  background:linear-gradient(to top,
    rgba(4,10,14,.97) 0%, rgba(4,10,14,.95) 52%,
    rgba(4,10,14,.5) 78%, rgba(4,10,14,0) 100%);
}

/* ---- the secondary action on an advertisement -------------------------
   "SAVE" was a different height, a different radius and the only uppercase
   label left on a control. */
.ad-save,.ad-actions .ad-save{
  min-height:46px;
  padding:0 20px;
  border-radius:99px;
  font-family:var(--body-f);
  font-weight:700;
  font-size:14.5px;
  letter-spacing:.005em;
  text-transform:none;
  background:rgba(255,255,255,.08);
  color:#FFFFFF;
  border:1px solid rgba(255,255,255,.34);
}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  refinements appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
