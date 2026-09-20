#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 115 — five cards were showing the whole rack.
#
# On the Water Pipes shelf, "Beaker Water Pipe" showed three beakers and
# "Clear Mansion Water Pipe" showed five bongs. A card is one product at one
# price with one Add to bag, so a card showing the rack is a card that is
# lying about what the button does.
#
# Stage 112 split the range shots in the photographs it re-took. These five are
# in photographs it did NOT re-take, because their makers — Diamond Glass,
# Lookah — are behind the browser approval Marco has not given yet. The picture
# is the one we already had; it is just no longer three of them.
#
# WHY THE TEST IS NARROW, and stays narrow. Widening the gap until a picture
# comes apart shatters a single bong into nine pieces: measured, a Diamond
# Glass pipe went to eight bands at the same threshold that split the rack.
# So a split is only made when the result looks like what a range shot
# actually is — three or more objects of NEARLY THE SAME WIDTH, each at least
# a seventh of the frame, carrying comparable amounts of ink. Anything that
# does not answer that description is left exactly as it is, and the one that
# would not come apart cleanly (five overlapping Mansion bongs) is still there,
# waiting on a better photograph.
#
# Every split was rendered before and after and looked at before this ran.
import io
import json
import base64
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, '/tmp/sp2')
import proc2 as P   # the shared band code, so there is one implementation

P_HTML = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P_HTML, encoding='utf-8').read()
n0 = len(s)


def rangeshot(al):
    W = al.shape[1]
    for gf in (0.03, 0.045, 0.06, 0.08, 0.10):
        bs = P.bands(al, gap_frac=gf, min_w=max(8, int(W * 0.12)))
        if len(bs) < 3: continue
        w = [x1 - x0 for x0, x1 in bs]
        if min(w) < W * 0.14: continue
        if max(w) / max(1, min(w)) > 1.35: continue
        ink = [(al[:, x0:x1] > 70).sum() for x0, x1 in bs]
        if min(ink) < max(ink) * 0.45: continue
        return bs, ink
    return None


k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cut = json.loads(s[i + len(k):j])

fixed = []
for pid, d in list(cut.items()):
    raw = base64.b64decode(d.split(',', 1)[1])
    a = np.array(Image.open(io.BytesIO(raw)).convert('RGBA'))
    r = rangeshot(a[..., 3])
    if not r: continue
    bs, ink = r
    pick = int(np.argmax(ink))
    x0, x1 = bs[pick]
    b = a[:, x0:x1]
    ys, xs = np.nonzero(b[..., 3] > 8)
    if not len(ys): continue
    b = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    buf = io.BytesIO()
    Image.fromarray(b, 'RGBA').save(buf, 'WEBP', quality=86, method=6)
    cut[pid] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    fixed.append('%s  %d units -> 1  (%dx%d)' % (pid, len(bs), b.shape[1], b.shape[0]))

for f in fixed:
    print('  ok:', f)

s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]
io.open(P_HTML, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
