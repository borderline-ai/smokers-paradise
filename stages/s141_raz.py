#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 141 — the last advert on a product card.
#
# Stage 124 took the retail carton out of fifteen vape photographs. It worked
# from CUT_PHOTOS, so it never looked at the ten products whose picture lives
# in SCENE_PHOTOS — the ones with a lifestyle shot instead of a keyed cut-out.
# One of those ten is not a lifestyle shot at all:
#
#     rx093  RAZ LTX 25K
#
# It is a full advertisement. The retail carton on the left with the nicotine
# warning panel printed across it, the device on the right, a "Blue Raz Ice"
# chip in the corner, and an orange band across the bottom with the RAZ LTX
# logo in it. Everything stage 124 was written to remove, in one picture, on a
# card sitting between two hundred and fifty clean cut-outs.
#
# The device is alone on white in the upper right of that slide, so it keys
# out: crop to it, drop the white that touches the border (so white ON the
# device survives), keep the largest object only so no fragment of the carton
# rides along, and it becomes an ordinary cut-out. It moves from SCENE_PHOTOS
# to CUT_PHOTOS with it, which is what takes it out of SCENE_IDS and gives it
# the same stage treatment as every other device on the shelf.
#
# The other nine stay. They are what they claim to be — a bong on a table, a
# banger on white, a rolling tray in somebody's hand — and a maker's lifestyle
# photograph of the actual product is not the thing Marco has been objecting
# to. What he objects to is a picture of a box.
import io
import json
import base64

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

# ---- the keyed device, built by scripts/../ the crop recorded in the note ----
blob = open('/tmp/sp8/rx093_cut.png', 'rb').read()
from PIL import Image
im = Image.open(io.BytesIO(blob)).convert('RGBA')
buf = io.BytesIO()
im.save(buf, 'WEBP', quality=86, method=6)
uri = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()

# out of the scene store
k = 'const SCENE_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
scene = json.loads(s[i + len(k):j])
was = len(scene.get('rx093', ''))
assert 'rx093' in scene, 'rx093 is not a scene photo any more'
del scene['rx093']
s = s[:i] + k + json.dumps(scene, separators=(',', ':')) + s[j:]
print('  ok: rx093 out of SCENE_PHOTOS (%d photos left)' % len(scene))

# into the cut-out store
k2 = 'const CUT_PHOTOS = '
i2 = s.index(k2)
j2 = s.index('};\n', i2) + 1
cut = json.loads(s[i2 + len(k2):j2])
cut['rx093'] = uri
s = s[:i2] + k2 + json.dumps(cut, separators=(',', ':')) + s[j2:]
print('  ok: rx093 is a cut-out, %dx%d, %d -> %d bytes' % (im.width, im.height, was, len(uri)))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
