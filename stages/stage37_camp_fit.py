#!/usr/bin/env python3
# Stage 37 — the carousel cell stops dictating the campaign's height.
#
# The old slide was a fixed 344px box (286 under 420px) because it was a card
# with a picture in it. A campaign is a composition and it sizes itself, so the
# cell is now just a track cell and gets out of the way.
#
# And .tall shows less. At half the width the sub-line collided with the
# product; a designer drops the line rather than shrinking everything until it
# fits, so the half-width campaign runs kicker, headline, price and CTA.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

CSS = """
/* the carousel cell is a track cell, nothing more */
#hero .slide{height:auto!important;min-height:0;overflow:visible}
#hero .promoc .vp,.promoc .vp{align-items:stretch}
#hero .slide>.camp{height:100%}

/* .tall shows less, on purpose */
.camp.tall .camp-sub{display:none}
.camp.tall{min-height:334px}
.camp.tall .camp-copy{padding:18px var(--cx) 0}
.camp.tall .camp-shot{height:46%}
"""
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
io.open(P, 'w', encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
