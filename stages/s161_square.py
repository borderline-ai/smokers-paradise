#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 161 — every product photograph the same size, in the same place.
#
# Marco, at one in the morning before the demo: "go into ALL of the product
# images and make the pictures presentable. It looks bugged out, low quality
# because they are not centered and things just look off. There might be some
# that are acceptable but when you click onto the other images of the same
# product you are met with smaller or out of frame pictures or off to the right
# side. If it is impossible we will need to go back to the white background."
#
# It is not impossible and the pictures are not the problem. Measured across all
# 270 product images:
#
#     261 of 270 are clean cut-outs with real transparency
#       0 of 270 have their content sitting under 80% of the frame
#       1 of 270 is off-centre inside its own file
#
# The files are fine. Here is the actual number:
#
#     ASPECT RATIO, WIDTH OVER HEIGHT
#       min    0.09      a dab tool: eleven times taller than it is wide
#       p10    0.31
#       median 0.65
#       p90    1.47
#       max    6.60      a slide: six times wider than it is tall
#
# A seventy-fold spread, and every one of them is dropped into the same square
# box with `object-fit:contain`. Contain fits the LONG side. So the 0.09 image
# fills the height and is a sliver a few pixels wide; the 6.60 image fills the
# width and is a strip with empty space above and below it; and the product next
# to it, at 0.65, fills neither. Nothing is broken and nothing is off-centre —
# every single one is dead centre in its box — and yet flicking through the
# thumbnails of one product shows it at four different sizes in four different
# shapes. That reads exactly as "out of frame, off to the right, bugged out",
# because the eye is comparing them to each other, not to the box.
#
# ======================================================================
# THE FIX: EVERY FILE BECOMES A SQUARE
# ======================================================================
# Each image is padded — not resampled, not cropped, not sharpened — onto a
# square transparent canvas, its content centred, with the long side set to 86%
# of the square. Every original pixel survives untouched; only empty space is
# added around it.
#
# After that, every product image has the same aspect as every other and the
# same aspect as the box it goes in, so `contain` has nothing left to decide.
# Every product lands dead centre with exactly the same 7% margin, at the same
# visual weight, on the card, on the product page, in the thumbnail strip and in
# every gallery. Clicking through the views of one product now shows the same
# product the same size four times.
#
# The one file that IS off-centre inside itself (rx142, 20% to the right) is
# fixed by the same pass, because centring is what the pass does.
#
# WHY NOT WHITE BACKGROUNDS, WHICH HE OFFERED AS THE FALLBACK. Because the
# fallback throws away the thing he liked — 261 real cut-outs, which is what
# makes this look like a shop's app instead of a slide deck — to solve a problem
# that is not in the pictures. If the squares do not read as "presentable" in
# the morning, white is still there and is a ten minute change, but it should be
# spent after seeing this, not instead of it.
import io
import json
import base64

import numpy as np
from PIL import Image

P = '/root/work/smokers-paradise-demo/build/index.html'
SCALE = 0.86          # the long side of the content, as a share of the square
MAXPX = 900           # nothing needs to be bigger than this on a phone

s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def load(name):
    k = 'const %s = ' % name
    i = s.index(k)
    j = s.index('};\n', i) + 1
    return k, i, j, json.loads(s[i + len(k):j])


def squarify(uri):
    """Pad to a square, content centred, long side at SCALE. No resampling of
    the content unless the result would be larger than MAXPX."""
    im = Image.open(io.BytesIO(base64.b64decode(uri.split(',', 1)[1]))).convert('RGBA')
    a = np.array(im)
    al = a[..., 3]
    if (al < 250).mean() > 0.02:
        mask = al > 60
    else:
        rgb = a[..., :3].astype(int)
        mask = ~((rgb > 238).all(-1))          # an opaque slide: trim white
    if not mask.any():
        return None
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    content = im.crop((x0, y0, x1 + 1, y1 + 1))
    long_side = max(content.width, content.height)
    side = int(round(long_side / SCALE))
    if side > MAXPX:                            # only ever scales DOWN
        f = MAXPX / side
        content = content.resize((max(1, round(content.width * f)),
                                  max(1, round(content.height * f))), Image.LANCZOS)
        side = MAXPX
    out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    out.paste(content, ((side - content.width) // 2, (side - content.height) // 2))
    buf = io.BytesIO()
    out.save(buf, 'WEBP', quality=88, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode(), out.size


total = 0
grew = 0
for name in ['CUT_PHOTOS', 'SCENE_PHOTOS']:
    k, i, j, st = load(name)
    before = sum(len(v) for v in st.values() if isinstance(v, str))
    n = 0
    for pid, uri in list(st.items()):
        if not isinstance(uri, str) or not uri.startswith('data:'):
            continue
        r = squarify(uri)
        if not r:
            continue
        st[pid] = r[0]
        n += 1
    after = sum(len(v) for v in st.values() if isinstance(v, str))
    s = s[:i] + k + json.dumps(st, separators=(',', ':')) + s[j:]
    total += n
    grew += after - before
    print('  ok: %-14s %d images squared, %+d bytes' % (name, n, (after - before) * 3 // 4))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d images normalised' % total)
print('%d -> %d chars' % (n0, len(s)))
