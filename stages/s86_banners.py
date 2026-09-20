#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 86 — the banners, read the way a customer reads them.
#
# Marco's note was "the banners could also use some work", so the four hero
# slides and the pair beneath them were measured against their own card and
# then looked at, enlarged, one at a time.
#
# 1. A GREY SMEAR AT THE FOOT OF THE LOST MARY DEVICE. The crop that put the
#    device on the banner carried a pale neutral blob beside its base, left
#    over from the reflection under the product in the original photograph.
#    On a near-white field it reads as a dirty mark on the card. The crop is
#    rebuilt: pale neutral pixels that are not part of the device are dropped,
#    the largest remaining body is kept and its holes filled, so the white
#    lettering on the device survives and the smear does not. 100x206 -> 74x202.
#
# 2. TWO OF THE THREE NICOTINE SLIDES CARRIED NO 21+ LINE. Off-Stamp says
#    "21+ only. Valid ID at pickup." Lost Mary and Geek Bar, both disposables,
#    said nothing. In a carousel that a customer swipes through in ten seconds,
#    a legal line that appears on one slide of three looks like an oversight,
#    because it is one.
#
# 3. THE PRODUCTS ENDED FOUR PIXELS ABOVE THE CARD EDGE. Not cropped by the
#    frame, which is a design device this file already uses on purpose, and not
#    standing on anything either: just stopping, with the contact shadow
#    squeezed into the four pixels left under them. Measured on all three
#    slides: 3, 4, 5, 6 and 7 pixels of daylight. They stand now, with one
#    shadow wide enough to hold both products, and the shadow is darkened for
#    the light fields because a 28% shadow on white is not a shadow.
#
# 4. THE CHOCOLATE BOX WAS SLICED. The pair's TRE House tile hung the box 14px
#    below the card and 4px past its right edge, so the front of the box, which
#    is the whole point of the picture, was cut across. Inside the frame now.
#
# 5. THE HEADLINE LIES ACROSS THEIR SIGN, AND IT STAYS THAT WAY. On the
#    storefront tile "Order ahead." sits over the word PARADISE, which looked
#    like a crop that needed fixing. It is not fixable by cropping: the
#    photograph is 600x368 in a 358x232 box, so cover scales it by height and
#    there is no vertical crop left to move — object-position does nothing
#    here, measured. Zooming in instead would cut the ends off the sign, which
#    is worse. Two denser scrims were rendered and compared against the
#    current one and both made the sign BRIGHTER behind the headline, because
#    the gradient runs from the bottom and moving its dark stops up lifts them
#    off the sign. The present scrim is the darkest of the three. Left alone.
#    Recorded here so the next pass does not re-open it.
import io
import json
import base64

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the Lost Mary device loses the smear -------------------------------
with open('/tmp/spnight/dev-lm2b.webp', 'rb') as f:
    clean = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()
i = s.index('const HERO_DEVICE = ')
j = s.index(';\n', i)
cur = json.loads(s[i + len('const HERO_DEVICE = '):j])
assert 'rx088' in cur
cur['rx088'] = clean
s = s[:i] + 'const HERO_DEVICE = ' + json.dumps(cur, separators=(',', ':')) + s[j:]
print('  ok: rx088 device recut, smear removed')

# ---- 2. every nicotine slide says 21+ --------------------------------------
rep("""    cta:'See the flavors', target:{view:'cat', arg:'disp', brand:'Lost Mary'},
    disclaimer:'',""",
"""    cta:'See the flavors', target:{view:'cat', arg:'disp', brand:'Lost Mary'},
    disclaimer:'21+ only. Valid ID at pickup.',""")

rep("""    cta:'Browse new vapes', target:{view:'cat', arg:'disp', brand:'Geek Bar'},
    disclaimer:'',""",
"""    cta:'Browse new vapes', target:{view:'cat', arg:'disp', brand:'Geek Bar'},
    disclaimer:'21+ only. Valid ID at pickup.',""")

# ---- 3 and 4. the products stand, and nothing is sliced --------------------
rep(""".camp.lead .camp-lead{right:1%;bottom:3%;max-height:104%;max-width:58%;height:auto}
.camp.lead .camp-back{right:38%;bottom:2%;max-height:76%;max-width:38%;height:auto}
.camp.tall .camp-lead{right:-3%;bottom:-5%;max-height:94%;max-width:112%;height:auto;
  left:auto;transform:none}
.camp.tall .camp-back{right:58%;bottom:4%;max-height:68%;max-width:62%;height:auto;
  left:auto;transform:none}""",
"""/* Four pixels of daylight under a product is not a bleed and not a floor. The
   lead and the back both sit clear of the card edge with room for the shadow
   the drop-shadow filter is already drawing, and the one contact shadow under
   them is wide enough to reach both. */
.camp.lead .camp-lead{right:3%;bottom:8%;max-height:108%;max-width:56%;height:auto}
.camp.lead .camp-back{right:40%;bottom:7%;max-height:80%;max-width:38%;height:auto}
.camp.tall .camp-lead{right:2%;bottom:7%;max-height:92%;max-width:98%;height:auto;
  left:auto;transform:none}
.camp.tall .camp-back{right:56%;bottom:9%;max-height:66%;max-width:58%;height:auto;
  left:auto;transform:none}""")

rep("""/* the bar sits into the top of its studio instead of leaving it empty */
.camp.tall .camp-lead{bottom:-6%;max-height:106%}""",
"""/* The box used to hang 14px below the card and 4px past its right edge, which
   cut the front of the box across — the one face the picture exists to show. */
.camp.tall .camp-lead{bottom:7%;max-height:92%}""")

rep(""".camp.lead .camp-ground{right:3%;bottom:3%;width:54%;height:16px}""",
    """.camp.lead .camp-ground{right:2%;bottom:5%;width:78%;height:15px}""")

rep(""".camp.tall .camp-ground{right:4%;bottom:5%;width:62%;height:14px}""",
    """.camp.tall .camp-ground{right:3%;bottom:5%;width:76%;height:13px}""")

rep(""".camp-lead{filter:drop-shadow(0 16px 20px rgba(20,8,30,.20))}
.camp-back{filter:drop-shadow(0 12px 16px rgba(20,8,30,.14));opacity:.94}""",
""".camp-lead{filter:drop-shadow(0 14px 18px rgba(20,8,30,.26))
                 drop-shadow(0 2px 3px rgba(20,8,30,.18))}
.camp-back{filter:drop-shadow(0 11px 14px rgba(20,8,30,.18));opacity:.94}
/* A 28% shadow on a white field is not a shadow. The light campaigns get a
   contact shadow that can actually be seen under the product. */
.camp.light .camp-ground{background:radial-gradient(50% 50% at 50% 50%,
  rgba(20,8,30,.38) 0%, rgba(20,8,30,.15) 52%, rgba(20,8,30,0) 100%)}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
