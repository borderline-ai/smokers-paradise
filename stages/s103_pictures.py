#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 103 — the picture pass. All 259, measured and then looked at.
#
# Marco: "Theres a lot of them that are missing a tiny bit of quality... You
# should zoom into these products and look at them, the shadows, the way you cut
# them out, The way you display the pictures. Centered, correctly displayed...
# When you click throughout the flavors and products there is no consistency
# with backgrounds and cuts."
#
# He pointed at the Lookah Seahorse Queen. Enlarged, its cut-out is:
#
#     a 154x279 frame, with the device in the LOWER RIGHT QUARTER,
#     a white blade-shaped spike across the bottom left where the shadow
#     was keyed off, and a speck at the very top.
#
# Both artifacts sat at the edges of the frame, so the frame was trimmed to
# THEM rather than to the product. The app then centred that frame, which put
# the device low and right with a third of the picture empty, and shrank it,
# because a frame padded with invisible artifacts is mostly invisible artifact.
# That is the whole of "not centered, missing quality" in one image, and it was
# never a layout bug.
#
# MEASURED ACROSS THE CATALOGUE: 162 of the 259 embedded photographs carry
# either a transparent margin they do not use or detached keying specks. Fixed
# by trimming each one to what is actually drawn, after dropping blobs that sit
# entirely outside the product's own silhouette.
#
# WHY COLUMN BANDS AND NOT CONNECTED COMPONENTS. The first attempt split each
# image into connected components and kept the biggest. That works on an opaque
# device and destroys clear glass: a bong's walls are drawn by thin highlights
# that never touch, so "the biggest component" is one wall of one chamber, and
# cropping to it threw the base away. Rendered side by side, it had beheaded the
# GRAV Mini Round Base and reduced the Session Goods Glow Lime to a green disc.
#
# So the unit is a COLUMN BAND. Project the alpha onto the x axis; a run of
# near-empty columns is the gap between two products standing side by side, and
# everything between two gaps is one product however many disconnected
# highlights it is drawn with. Three or more comparable bands is a wholesaler's
# range shot, and a product card shows one unit.
#
# THREE DONE BY HAND, because a rule that caught them would have caught things
# it should not:
#
#   rx142  the white blade on the Seahorse touches the device's base, so no
#          "detached blob" rule reaches it. Removed by colour and position:
#          pale, unsaturated, in the bottom-left corner, away from the black body.
#   r052   the Vaporesso XROS 5 was a ten-up colour grid, two rows of five.
#          Cropped to one device.
#   rx067  the two Fifty Bars are wholesaler slides like the Tyson ones were:
#   rx068  the device, a vertical WARNING sidebar the packaging already carries,
#          and FIFTYBARVAPES.COM across the bottom. That is the second
#          competitor's web address found on a card in this app. Cropped to the
#          product; the nicotine warning stays where it belongs, printed on the
#          device in the picture.
import io
import json
import base64
import os

P = '/root/work/smokers-paradise-demo/build/index.html'
TIDY = '/tmp/spnight/tidy2'

s = io.open(P, encoding='utf-8').read()
n0 = len(s)

k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cur = json.loads(s[i + len(k):j])

k2 = 'const SCENE_PHOTOS = '
i2 = s.index(k2)
j2 = s.index('};\n', i2) + 1
scene = json.loads(s[i2 + len(k2):j2])

done = miss = 0
before = after = 0
for f in sorted(os.listdir(TIDY)):
    pid = f[:-4]
    with open(os.path.join(TIDY, f), 'rb') as fh:
        from PIL import Image
        im = Image.open(fh).convert('RGBA')
    tmp = '/tmp/spnight/_e.webp'
    # q82, not q92. These render at 132px on a card and about 320px on a
    # product page; at q92 the retrim made the file 567KB HEAVIER for detail
    # that cannot be seen at either size. Compared side by side at 3x first.
    im.save(tmp, 'WEBP', quality=82, method=6)
    with open(tmp, 'rb') as fh:
        d = 'data:image/webp;base64,' + base64.b64encode(fh.read()).decode()
    if pid in cur:
        before += len(cur[pid]); cur[pid] = d; after += len(d); done += 1
    elif pid in scene:
        before += len(scene[pid]); scene[pid] = d; after += len(d); done += 1
    else:
        miss += 1

s = s[:i2] + k2 + json.dumps(scene, separators=(',', ':')) + s[j2:]
# CUT_PHOTOS moved if it sat after SCENE_PHOTOS, so find it again
i = s.index(k)
j = s.index('};\n', i) + 1
s = s[:i] + k + json.dumps(cur, separators=(',', ':')) + s[j:]

print('  ok: %d photographs retrimmed, %d not in either table' % (done, miss))
print('  ok: %d KB of image data -> %d KB' % (before // 1024, after // 1024))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
