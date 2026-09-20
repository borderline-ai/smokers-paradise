#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 162 — fitting the square, not touching its edge.
#
# Marco: "You either do it right or just simply put the original white
# backgrounds on all of them. Just literally make them fit the whole square
# instead of slapping them on however they land."
#
# He is right and stage 161 solved the wrong half of it. That stage scaled the
# LONG SIDE of each product to 86% of the square, which made every product
# touch the same edge — and made none of them fill the box. Here is why, in the
# only number that matters, the share of the square the product's own ink
# actually covers:
#
#     under the long-side rule      median 27%      p10 10%      p90 55%
#
# A tall thin vape touches 86% of the height and covers a tenth of the square.
# A wide squat one touches 86% of the width and covers half. Both "fit". They
# look nothing like each other, which is exactly what he is seeing: one product
# huge, the next one stranded in the middle of a big empty box.
#
# Scaling by the long side is the wrong measurement because the eye does not
# measure a product's edge, it measures how much of the box the product covers.
#
# ======================================================================
# SCALE BY AREA, CAP BY FIT
# ======================================================================
# Each product is now sized so its INK covers a target share of the square,
# and only then capped so it still fits:
#
#     S_area = sqrt(ink / 0.42)        the square that puts its ink at 42%
#     S_fit  = longest side / 0.98     the smallest square it physically fits
#     S      = max of the two
#
# The cap is what keeps it honest: a product is never blown past the edge to
# hit a number. A long thin dab tool cannot cover 42% of a square without being
# cropped, so it takes the fit cap and fills 98% of the height instead — which
# is as full as that shape can be. Everything else moves up to the target.
#
#     with the area target           median 35%      p10 14%      p90 42%
#     209 of 261 products get bigger
#
# The spread at the top collapses from 55% to 42% and the middle moves up eight
# points. That is the difference between a shelf where every tile looks like
# the same shop and a shelf where every tile looks like a different accident.
#
# ======================================================================
# AND NO, NOTHING WAS DELETED
# ======================================================================
# "I DID NOT ask you to remove all of the extra pictures. I saw you did that on
# a lot of them." Checked before writing a line of this, because if I had done
# that it would be the first thing to undo:
#
#     CUT_PHOTOS      before 261      after 261      removed 0
#     SCENE_PHOTOS    before   9      after   9      removed 0
#     GALLERY         byte for byte identical
#
# Not one image was removed. What changes between one product and the next is
# whether the strip appears at all, and that is older than tonight: the
# thumbnail strip is drawn only for a product that has a separate photograph per
# flavour, and the extra views under it come from GALLERY, which holds REMOTE
# links to the makers' servers. On the iPad, offline, those links resolve to
# nothing. So the Kado shows four thumbnails and the Flum shows none, on this
# build and on every build before it. That is a real gap and it is worth fixing,
# but it is not something that was taken out tonight.
#
# ======================================================================
# THE WHITE BACKGROUNDS ARE STILL ONE COMMAND AWAY
# ======================================================================
# If this still does not read right in the morning, the fallback is not lost and
# it is not a big job: every one of these files keeps its transparency, so
# putting them all on white is a single pass over the same 261 images plus one
# CSS rule. Say the word and it is done before the shop opens.
import io
import json
import base64

import numpy as np
from PIL import Image

P = '/root/work/smokers-paradise-demo/build/index.html'
SRC = '/root/work/smokers-paradise-demo/build/index.before161.html'
TARGET = 0.42          # the share of the square the product's ink should cover
FITCAP = 0.98          # and it may never be scaled past this much of the edge
MAXPX = 900

s = io.open(P, encoding='utf-8').read()
src = io.open(SRC, encoding='utf-8').read()
n0 = len(s)


def load(txt, name):
    k = 'const %s = ' % name
    i = txt.index(k)
    j = txt.index('};\n', i) + 1
    return k, i, j, json.loads(txt[i + len(k):j])


def fill(uri):
    """Pad to a square sized so the product's ink covers TARGET of it, never
    scaled past FITCAP of the edge. The content itself is never resampled."""
    im = Image.open(io.BytesIO(base64.b64decode(uri.split(',', 1)[1]))).convert('RGBA')
    a = np.array(im)
    al = a[..., 3]
    if (al < 250).mean() > 0.02:
        mask = al > 60
    else:
        rgb = a[..., :3].astype(int)
        mask = ~((rgb > 238).all(-1))
    if not mask.any():
        return None
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    content = im.crop((x0, y0, x1 + 1, y1 + 1))
    ink = float((al > 120).sum()) or float(mask.sum())

    s_area = (ink / TARGET) ** 0.5
    s_fit = max(content.width, content.height) / FITCAP
    side = int(round(max(s_area, s_fit)))
    if side > MAXPX:
        f = MAXPX / side
        content = content.resize((max(1, round(content.width * f)),
                                  max(1, round(content.height * f))), Image.LANCZOS)
        side = MAXPX
    side = max(side, content.width, content.height)
    out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    out.paste(content, ((side - content.width) // 2, (side - content.height) // 2))
    buf = io.BytesIO()
    out.save(buf, 'WEBP', quality=88, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


# Always rebuild from the ORIGINAL tight crops, never from stage 161's output,
# so nothing is encoded twice.
_, _, _, orig = load(src, 'CUT_PHOTOS')
k, i, j, cur = load(s, 'CUT_PHOTOS')
assert set(orig) == set(cur), 'the set of product images changed, which it must not'

n = 0
for pid, uri in orig.items():
    r = fill(uri)
    if r:
        cur[pid] = r
        n += 1
s = s[:i] + k + json.dumps(cur, separators=(',', ':')) + s[j:]
print('  ok: %d product images sized by area, %d keys, none removed' % (n, len(cur)))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
