#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 142 — three more cartons, and the seam that opens them.
#
# Stage 124 took the retail carton out of fifteen vape photographs by eroding
# until the picture fell into two pieces. Three of the biggest cards on the
# Disposable Vapes shelf were not among them:
#
#     disp2   Geek Bar Pulse X 25K     carton + device
#     disp3   Geek Bar Pulse X2 50K    carton + device
#     rx086   Geek Bar Pulse 15K       carton + device
#
# all three with "WARNING: This product contains nicotine. Nicotine is an
# addictive chemical." printed across the box, on the shelf for the brand
# Smokers Paradise leads with. Stage 125 even names rx086 as one that "cannot
# be separated" — that was true of the method, not of the picture.
#
# WHY EROSION FAILED AND WHAT WORKS. In these three the carton and the device
# touch along a long edge, so eroding to break them apart eats one of them
# first. But they are not overlapping — they are two columns standing side by
# side — and two columns of ink have a DIP between them. Sum the alpha down
# each column, smooth it, and take the lowest point in the middle third: that
# is the seam, and a straight cut there gives the device whole with nothing of
# the box left on it. Two pixels of bias to the right of the dip, because the
# carton's near face is the thing that survives a cut placed exactly on it.
#
# rx073 (Tyson MIA 50K) is still not fixable: the maker published the carton
# ALONE, with no device in the frame at all. It keeps its picture and stays off
# the front of the shelf, which is what stage 125 decided for it.
import io
import json
import base64

import numpy as np
from PIL import Image
from scipy import ndimage as nd

P = '/root/work/smokers-paradise-demo/build/index.html'

# id -> which side of the seam the DEVICE is on
KEEP = {
    'disp2': 'right',   # Geek Bar Pulse X 25K,  Grape Elixir carton on the left
    'disp3': 'right',   # Geek Bar Pulse X2 50K, Blue Razz Bull carton on the left
    'rx086': 'right',   # Geek Bar Pulse 15K,    Meta Moon carton on the left
}
BIAS = 0.012            # of the image width, away from the carton


def seam(a):
    al = a[..., 3]
    col = (al > 70).sum(0).astype(float)
    w = len(col)
    sm = np.convolve(col, np.ones(7) / 7.0, mode='same')
    lo, hi = int(w * 0.30), int(w * 0.70)
    return lo + int(np.argmin(sm[lo:hi]))


s = io.open(P, encoding='utf-8').read()
n0 = len(s)
k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cut = json.loads(s[i + len(k):j])

for pid, side in KEEP.items():
    raw = cut[pid]
    a = np.array(Image.open(io.BytesIO(base64.b64decode(raw.split(',', 1)[1]))).convert('RGBA'))
    x = seam(a)
    pad = int(a.shape[1] * BIAS)
    b = a[:, x + pad:] if side == 'right' else a[:, :max(1, x - pad)]
    ys, xs = np.nonzero(b[..., 3] > 70)
    assert len(ys), pid
    b = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray(b)
    if max(im.size) > 660:
        f = 660 / max(im.size)
        im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    im.save('/tmp/sp8/%s_final.png' % pid)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=86, method=6)
    was = len(raw)
    cut[pid] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    print('  ok: %-6s seam at %d, device %dx%d, %d -> %d bytes'
          % (pid, x, im.width, im.height, was, len(cut[pid])))

s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]
io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
