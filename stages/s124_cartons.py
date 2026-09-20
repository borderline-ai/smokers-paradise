#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 124 — the box next to the vape.
#
# Marco, twice: "Same thing with the off-stamps, it seems you are making these
# pictures low quality and cutting them out wrong leaving things in the picture
# that it just looks bugged." And: "I CAN ASSURE YOU THAT ON THE PUFFCO SITE
# THEY DONT HAVE CROPPED PICTURES OF THEIR PRODUCTS OR ALL OF THE BRANDS FOR
# THAT MATTER."
#
# I fixed the Off-Stamp by hand in stage 119 and moved on, which was treating a
# symptom. Here is the disease. A disposable vape is sold to shops as a case,
# so the picture the maker publishes is a WHOLESALER'S SLIDE: the retail carton
# standing on the left, the device on the right, and a white panel across the
# carton with the nicotine warning printed on it. Twelve of them are in this
# app. Every one of those cards shows a customer a cardboard box and a bar code
# next to the thing they are trying to look at.
#
# That is not what a product card is. A product card shows the product.
#
# HOW THEY COME APART. The carton and the device touch in most of these frames,
# so a gap-scan sees one object — which is why the earlier one_unit() pass,
# which looks for gaps, walked straight past all twelve. The seam opens under
# erosion: erode until the picture falls into two pieces, then grow the pieces
# back with a watershed so the erosion does not eat the edges it was used to
# find. The device is the piece that is kept.
#
# WHAT IS NOT TOUCHED, and why there is a hand-checked list here rather than a
# rule. The same split runs happily on a GRAV bubbler and cuts the downstem off
# it, because a bong is also two pieces that touch. I tried three ways to tell
# a printed carton from a product automatically — how much of its own bounding
# box it fills, how square it is, whether it carries a white warning panel —
# and every one of them fired on clear glass, which is full of white
# reflections and rectangular highlights. So: the split is automatic, the
# decision to apply it is not. Each id below was looked at, before and after,
# on a contact sheet. Nothing splits that was not on the sheet.
import io
import os
import json
import base64
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as nd
from skimage.segmentation import watershed

P = '/root/work/smokers-paradise-demo/build/index.html'

# id -> which piece to keep, left to right (0 is leftmost).
# Checked by eye, one at a time, against /tmp/sp4/two/sheet*.png.
KEEP = {
    # disposables: carton left, device right
    # The carton is usually on the left, but not always: four of these slides
    # stand the device first. The index is which piece to keep counting from
    # the left, and each one was read off a sheet that draws both pieces with
    # their side labelled, not guessed from a habit.
    'rx049': 1,   # Elf Bar BC5000            carton left
    'rx050': 0,   # Elf Bar TE6000            carton RIGHT
    'rx051': 0,   # Vozol Vista 40K           carton RIGHT
    'rx052': 1,   # Kado Bar KB10000          carton left
    'rx055': 0,   # VIHO Supercharge 20000    carton RIGHT
    'rx056': 1,   # North FT12000             carton left
    'rx066': 1,   # Off-Stamp X Cube 25K      carton left
    'rx088': 1,   # Lost Mary MO20000 Pro     carton left
    'rx089': 1,   # Lost Mary MT35000 Turbo   carton left
    'rx090': 0,   # Lost Mary MT15000 Turbo   carton RIGHT
    'rx091': 1,   # Lost Mary Viz 55K         carton left
    'rx092': 1,   # RAZ DC25000               carton left
    # e-liquid: the carton it ships in, and the bottle
    'r045':  1,   # Jam Monster Strawberry 100mL
    'r048':  1,   # Twist Pink Punch No. 1 — a two-pack, so two bottles is right
    # a cleaner photographed in two sizes; this listing is the 12oz
    'r040':  0,
}
# Looked at and deliberately left alone:
#   rx064  the right-hand piece is a blank pod, worse than the pair
#   rx206  one bottle with its own printed label; the split is a fragment
#   rx035/rx036  two jars of cones, which is what a jar of cones looks like
#   every GRAV, Lookah, Diamond Glass and Session Goods piece — the split
#     cuts glass apart, because a bong is two shapes that touch


def parts(a):
    al = a[..., 3]
    op = al > 70
    if op.sum() < 400:
        return None
    for er in range(0, 8):
        m = nd.binary_erosion(op, np.ones((3, 3)), iterations=er) if er else op
        lab, n = nd.label(m)
        if n == 0:
            return None
        sz = np.array(nd.sum(m, lab, range(1, n + 1)))
        keep = [i + 1 for i, s in enumerate(sz) if s >= sz.max() * 0.15]
        if len(keep) >= 2:
            mk = np.zeros_like(lab)
            for j, c in enumerate(keep, 1):
                mk[lab == c] = j
            d = nd.distance_transform_edt(op)
            seg = watershed(-d, mk, mask=op)
            out = [(seg == j) for j in range(1, len(keep) + 1)]
            # left to right, so the index in KEEP means what it reads like
            out.sort(key=lambda m2: np.nonzero(m2)[1].min())
            return out, er
    return None


s = io.open(P, encoding='utf-8').read()
n0 = len(s)
k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cut = json.loads(s[i + len(k):j])

os.makedirs('/tmp/sp4/fixed', exist_ok=True)
done, skipped = 0, []
for pid, want in KEEP.items():
    raw = cut.get(pid)
    if not raw:
        skipped.append((pid, 'not embedded'))
        continue
    a = np.array(Image.open(io.BytesIO(base64.b64decode(raw.split(',', 1)[1]))).convert('RGBA'))
    r = parts(a)
    if not r or len(r[0]) != 2:
        skipped.append((pid, 'did not split in two'))
        continue
    m = r[0][want]
    b = a.copy()
    b[..., 3] = np.where(m, b[..., 3], 0)
    ys, xs = np.nonzero(m)
    b = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray(b)
    if max(im.size) > 660:
        sc = 660 / max(im.size)
        im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.LANCZOS)
    im.save('/tmp/sp4/fixed/%s.png' % pid)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=86, method=6)
    was = len(raw)
    cut[pid] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    print('  ok: %-6s %dx%d  %d -> %d bytes' % (pid, im.width, im.height, was, len(cut[pid])))
    done += 1

s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]
io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d rebuilt, %d skipped %s' % (done, len(skipped), skipped))
print('%d -> %d chars' % (n0, len(s)))
