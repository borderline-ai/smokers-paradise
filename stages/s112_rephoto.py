#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 112 — the pictures were never big enough, and that was the whole thing.
#
# Marco: "Center these pictures. ALL of the Product pictures should be good
# quality. I CAN ASSURE YOU THAT ON THE PUFFCO SITE THEY DONT HAVE CROPPED
# PICTURES OF THEIR PRODUCTS OR ALL OF THE BRANDS FOR THAT MATTER. WE CANT HAVE
# THAT... some of these product pictures are just awful for example the Small
# Bowl Water Pipe Replacement - 2 pack... its the way you display these
# products they look low quality... Same thing with the off-stamps, it seems
# you are making these pictures low quality and cutting them out wrong leaving
# things in the picture that it just looks bugged."
#
# He has said a version of this four times. Here is the measurement that should
# have been taken the first time.
#
#     EVERY ONE of the 239 embedded photographs had a long side under 400px.
#     Not one was over 400. The product page draws at 356 CSS pixels, which on
#     his iPad is 712 device pixels.
#
#     Session Goods Small Bowl 2-pack      77 x 68     drawn at 712
#     Puffco Hot Knife                     24 x 271
#     Puffco Pivot                         42 x 260
#     GRAV Sandblasted Spoon              113 x 100
#     Vaporesso XROS 5                     35 x 148
#
# Every picture in this app was being blown up between two and nine times. No
# amount of trimming, centring or framing fixes that, and the last three stages
# spent their time on trimming, centring and framing. The source files were too
# small. That is all it ever was.
#
# WHAT THIS DOES. Goes back to the makers and the big retailers, reads their
# own product feeds, and takes the photograph at the size THEY publish it.
#
#     GRAV publish at              4042 x 6063
#     Session Goods at             2500 x 2500
#     MJ Arsenal at                3000 x 3000
#     Puffco at                    1800 x 2400
#
# 83 products, re-taken. Median long side out: 660px, which is comfortably past
# what a retina iPad asks for, from a source between five and fifteen times the
# old one.
#
# HOW A MATCH IS ALLOWED. A wrong photograph is worse than a small one, and the
# fuzzy matcher's first pass proved it: it offered an Empire Glassworks
# attachment as the Puffco Peak, a Halloween House Beaker as the Pulsar
# Snatched Beaker, and the same Gold Little Beaker for four different Diamond
# Glass pipes. So a candidate now has to carry every word of our product name,
# name the maker, and add no word that changes what the object is: no kit, set,
# pack, bundle, "A + B", "X x Y", edition, replacement, downstem. 127 candidates
# went in, 80 came out; the rest were picked by hand off the maker's own store
# by exact title, and 8 were thrown away after looking at them:
#
#   rx172  four bongs in one frame and they do not come apart
#   r050   a sixteen-up colourway grid
#   r015   the retail cartons, with no product in the frame
#   rx143  the same
#   r036   a Star Wars licensed edition, not the grinder the shop carries
#   rx145  Session Goods only shot the Cherry bong in somebody's hand
#   rx228  two torches stacked, and the splitter only works sideways
#   r020   the splitter took a fragment rather than the bubbler
#
# Those eight keep the picture they had. A small right picture beats a big
# wrong one.
#
# AND THE THINGS LEFT IN THE FRAME, which is the other half of his note:
#
#   THE CARTON. A device photographed next to its retail box, with the nicotine
#   warning panel printed on it. Told apart from the product by how much of its
#   own bounding box it fills: a carton is a solid rectangle and fills nearly
#   all of it, a pipe is mostly air. The box goes.
#
#   THE RANGE SHOT. Six of the same thing in six colours. The gap that
#   separates them is not one number, so it is widened until the picture comes
#   apart, and one unit survives.
#
#   THE RULER. GRAV publish their glass with the measurements drawn on the
#   photograph: a 6" line across the top, a 12.25" line down the side, and the
#   figures beside them. They keyed out with the product and sat on the card
#   looking like debris. Found by shape, not colour — a rule is one pixel in
#   one direction and a quarter of the picture in the other — and the pale
#   figures beside them go with the rule that nothing faint survives unless it
#   is attached to something solid. 14 rule marks came off one GRAV beaker.
#
# WHAT WAS TRIED AND THROWN AWAY: cropping off GRAV's white plinth, because the
# reflection reads as a pool of white on a dark card. Dropping rows from the
# bottom while they are almost all sweep-coloured removes it, and also removes
# the clear glass foot of every beaker, because a clear foot IS almost all
# sweep-coloured. It cut the base off six bongs to tidy a reflection on four.
# The reflection is the maker's own photograph and it stays.
import io
import json
import base64
import os

from PIL import Image

P = '/root/work/smokers-paradise-demo/build/index.html'
OUT = '/tmp/sp2/out2'
TARGET, QUALITY = 660, 84

s = io.open(P, encoding='utf-8').read()
n0 = len(s)

res = json.load(open('/tmp/sp2/proc2.json'))
meta = {m['id']: m for m in json.load(open('/tmp/sp2/hires_meta.json'))}

def table(name):
    k = 'const %s = ' % name
    i = s.index(k)
    j = s.index('};\n', i) + 1
    return k, i, j, json.loads(s[i + len(k):j])

_, _, _, cut = table('CUT_PHOTOS')
_, _, _, scene = table('SCENE_PHOTOS')

before = {}
for pid in res:
    for t in (cut, scene):
        if pid in t:
            before[pid] = len(t[pid])

grew = shrank = 0
for pid, info in sorted(res.items()):
    im = Image.open(os.path.join(OUT, pid + '.png'))
    if max(im.size) > TARGET:
        k = TARGET / max(im.size)
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))),
                       Image.LANCZOS)
    buf = io.BytesIO()
    if info['kind'] == 'scene':
        im.convert('RGB').save(buf, 'WEBP', quality=QUALITY, method=6)
    else:
        im.convert('RGBA').save(buf, 'WEBP', quality=QUALITY, method=6)
    uri = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    # a photograph and a cut-out are rendered differently, so a product that
    # changes from one to the other has to change table as well
    cut.pop(pid, None); scene.pop(pid, None)
    (scene if info['kind'] == 'scene' else cut)[pid] = uri
    if pid in before:
        if len(uri) > before[pid]: grew += 1
        else: shrank += 1

# write both tables back, re-finding the second one because the first moved it
k, i, j, _ = table('SCENE_PHOTOS')
s = s[:i] + k + json.dumps(scene, separators=(',', ':')) + s[j:]
k, i, j, _ = table('CUT_PHOTOS')
s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]

print('  ok: %d photographs re-taken at source resolution' % len(res))
print('  ok: %d cut-outs, %d photographs'
      % (sum(1 for v in res.values() if v['kind'] != 'scene'),
         sum(1 for v in res.values() if v['kind'] == 'scene')))
print('  ok: %d files bigger than before, %d smaller' % (grew, shrank))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
