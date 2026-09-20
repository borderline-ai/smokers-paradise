#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 114 — the Geek Bar Marco has pointed at more than once.
#
# Marco: "I've also told you SO MANY TIMES about the dam geek bar that you have
# cropped in the shop by category disposable vapes section."
#
# He is describing the Disposable Vapes tile on Shop by Category. Pulled out and
# enlarged, the file behind it is:
#
#     a retail CARTON, cut off at the left edge of the frame,
#     the device beside it,
#     and a white panel with the nicotine warning printed across it.
#
# Three things in a 104px square, one of them sliced. The tile is not cropping
# it — `object-fit:contain` at 78% cannot crop anything — the PICTURE is a
# wholesaler's slide and it arrived already cut.
#
# So the fix is not in the tile, it is in which photograph the tile asks for.
# All three of the tiles that carry a carton and a warning panel now point at a
# product whose photograph is one clean unit on nothing:
#
#     Disposable Vapes   Geek Bar carton + device + warning  ->  North 5000
#     Vape Hardware      Uwell, cropped at the bottom        ->  Caliburn A3
#     E-Liquid           Coastal Clouds bottle + box + panel ->  Juice Head
#
# And they are addressed BY PRODUCT rather than by brand-model-flavour, which
# is what let a flavour-level wholesaler slide answer for a whole department in
# the first place.
#
# Also here: the North 5000 photograph itself, re-taken at 600px from 333px,
# because the tile it now fronts is the first picture of the shelf anybody sees.
import io
import json
import base64
import os

from PIL import Image

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the one disposable worth re-taking from the reachable sources ------
# The rest of the disposable wall could not be improved: the only store that
# answers for those brands publishes marketing banners rather than product
# shots -- five devices on a starburst, or a card with "21+" set across it --
# and the pictures this app already carries came off the makers themselves and
# are better. Those need Marco to let the browser open the brand sites.
k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cut = json.loads(s[i + len(k):j])

im = Image.open('/tmp/sp2/out3/rx057.png')
if max(im.size) > 660:
    r = 660 / max(im.size)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
buf = io.BytesIO()
im.convert('RGBA').save(buf, 'WEBP', quality=84, method=6)
was = len(cut.get('rx057', ''))
cut['rx057'] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]
print('  ok: rx057 North 5000 re-taken, %d -> %d bytes' % (was, len(cut['rx057'])))

# ---- 2. the three tiles that were showing cartons -------------------------
rep("""  {k:'disp',  n:'Disposable Vapes',        img:()=>img('Geek Bar','Pulse X 25K','Miami Mint')||catFallbackImage('disp')},""",
"""  /* WAS: a Geek Bar wholesaler slide — the retail carton cut off at the left
     edge, the device beside it, and the nicotine warning panel. Three things
     in a 104px square, one of them sliced. Addressed by product now, not by
     brand-model-flavour, so a flavour-level slide can never answer for a
     department again. */
  {k:'disp',  n:'Disposable Vapes',        img:()=>LOCAL_PHOTOS['rx057']||catFallbackImage('disp')},""")

rep("""  {k:'hard',  n:'Vape Hardware',           img:()=>img('Uwell','Caliburn G4 Pro Kit','Black')
                                              ||img('Uwell','Caliburn A3 Kit','Black')
                                              ||img('Suorin','Air Pro 18W Pod System')},""",
"""  {k:'hard',  n:'Vape Hardware',           img:()=>LOCAL_PHOTOS['rx185']
                                              ||LOCAL_PHOTOS['rx184']||catFallbackImage('hard')},""")

rep("""  {k:'eliq',  n:'E-Liquid',                img:()=>img('Coastal Clouds','Apple Peach Strawberry 60mL')||catFallbackImage('eliq')},""",
"""  /* WAS: the bottle, its box, and a warning panel. This one is the bottle. */
  {k:'eliq',  n:'E-Liquid',                img:()=>LOCAL_PHOTOS['rx207']||catFallbackImage('eliq')},""")

# ---- 3. the mark on the fit tool was taking half the first screen ---------
rep(""".ffmark{width:112px;margin:0 auto 4px;line-height:0}""",
""".ffmark{width:92px;margin:0 auto 2px;line-height:0}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
