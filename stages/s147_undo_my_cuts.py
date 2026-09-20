#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 147 — undoing three cuts I made yesterday, and the corner I left on.
#
# Marco: "what about the cropped geek bar and the bottom left corner of the
# lost mary. Those tiny mistakes are unnacceptable and are very recent."
#
# He is right on both, and "very recent" is the part that matters: I made both
# of these this week, in stages 142 and 124, and I checked both on a contact
# sheet at about 150 pixels wide and called them clean. At four times size they
# are not clean at all. That is the same mistake I have now made four times —
# looking at the picture too small to see what is wrong with it.
#
# ======================================================================
# THE GEEK BAR, AND WHY MY OWN METHOD WAS WRONG FOR IT
# ======================================================================
# Stage 142 cut three cards at "the seam": sum the alpha down each column,
# smooth it, take the lowest point in the middle third, cut there. That is a
# correct method for two objects STANDING SIDE BY SIDE, and it is the wrong
# method for two objects that OVERLAP. I did not check which of the three I
# had, and here is the profile that would have told me:
#
#     col 149   234 ink        <- the carton
#     col 150   169            <- 65 pixels vanish in one column
#     col 153   170            <- "the seam"
#     col 156   171            <- where I cut
#     col 160   185            <- ink climbing again
#
# The ink never drops toward zero. There is no gap. The carton's right edge
# sits IN FRONT OF the device's left edge and they overlap by about nine
# pixels, so the "lowest point" was not a seam at all — it was the middle of
# the device. I cut nine pixels off its left side, took the G off GEEK BAR
# with it, and left a dead straight vertical edge down the front of a product.
#
# Checked all three of the cards I cut that way, not just the one he caught:
#
#     disp2   Pulse X 25K     78% of the left frame edge is ink   CUT
#     disp3   Pulse X2 50K    81% left, 60% right                 CUT BOTH SIDES
#     rx086   Pulse 15K       the one he spotted                  CUT
#
# All three. I broke three products and shipped them.
#
# THERE IS NO CLEAN PHOTOGRAPH OF ANY OF THEM. Six copies of the Pulse 15K
# source exist on this machine and they are two pictures: a carton-only slide,
# and the carton-with-device slide where the device's left edge is behind the
# box. The container's proxy refuses the manufacturer hosts, so a better file
# cannot be fetched from here.
#
# So all three go back to the maker's whole photograph — box, device and
# warning panel — and off the front of the shelf, which is exactly where stage
# 125 put them and where I should have left them. A complete honest picture
# that happens to include a box beats a product with its side sliced off. One
# photograph of each device on their own counter ends this permanently.
#
# ======================================================================
# THE LOST MARY, WHICH IS ACTUALLY FIXABLE
# ======================================================================
# A pale rectangular tab hanging off the bottom left corner: a piece of the
# retail carton left behind by the stage 124 split, fused to the device's mask
# so no amount of eroding separates it.
#
# It comes off by geometry instead. The device is tilted, so its left edge
# walks smoothly across the frame — fit that line over the rows above the stub
# and it reads x = -0.290*y + 76.1, within a pixel, all the way down. Then the
# rows where the ink starts well left of that line are not the device:
#
#     row 180   ink starts at 24    on the line
#     row 192   starts at 20        on the line
#     row 204   starts at  1        the line says 16   <- the stub
#     row 216   starts at  8        the line says 13   <- the stub
#
# Everything left of the fitted edge, one pixel inside it so the halo goes too,
# is cleared. 224 pixels. The device is untouched.
import io
import json
import base64

import numpy as np
from PIL import Image
from scipy import ndimage as nd

P = '/root/work/smokers-paradise-demo/build/index.html'
PRE = '/root/work/smokers-paradise-demo/build/index.before142.html'

s = io.open(P, encoding='utf-8').read()
n0 = len(s)
k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cut = json.loads(s[i + len(k):j])

# ---- 1. the three seam cuts go back to the maker's whole photograph --------
pre = io.open(PRE, encoding='utf-8').read()
pi = pre.index(k)
pj = pre.index('};\n', pi) + 1
before = json.loads(pre[pi + len(k):pj])
for pid, name in [('disp2', 'Geek Bar Pulse X 25K'),
                  ('disp3', 'Geek Bar Pulse X2 50K'),
                  ('rx086', 'Geek Bar Pulse 15K')]:
    assert pid in before, pid
    was = len(cut[pid])
    cut[pid] = before[pid]
    print('  ok: %-6s back to the uncut photograph  %d -> %d bytes  (%s)'
          % (pid, was, len(cut[pid]), name))

# ---- 2. the Lost Mary loses the carton corner ------------------------------
a = np.array(Image.open(io.BytesIO(base64.b64decode(cut['rx089'].split(',', 1)[1]))).convert('RGBA'))
H, W = a.shape[:2]
op = a[..., 3] > 70
lead = np.array([(np.nonzero(op[y])[0].min() if op[y].any() else -1) for y in range(H)])
rows = np.arange(90, 193)                       # the clean run, above the stub
m, b = np.polyfit(rows, lead[rows], 1)
out = a.copy()
cleared = 0
for y in range(191, H):
    cutx = int(round(m * y + b)) + 1            # one pixel in, so the halo goes too
    if cutx > 0:
        cleared += int((out[y, :cutx, 3] > 70).sum())
        out[y, :cutx, 3] = 0
al = out[..., 3] > 70
lab, nn = nd.label(al)
if nn > 1:
    sz = nd.sum(al, lab, range(1, nn + 1))
    out[..., 3] = np.where(lab == int(np.argmax(sz)) + 1, out[..., 3], 0)
ys, xs = np.nonzero(out[..., 3] > 60)
out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
im = Image.fromarray(out)
buf = io.BytesIO()
im.save(buf, 'WEBP', quality=88, method=6)
was = len(cut['rx089'])
cut['rx089'] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
print('  ok: rx089  carton corner off (%d px), %dx%d, %d -> %d bytes'
      % (cleared, im.width, im.height, was, len(cut['rx089'])))

s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]

# ---- 3. a photograph with a box in it does not lead the shelf --------------
# disp2 and disp3 live in a different array and are already not featured;
# rx086 was promoted back to the front of the shelf in stage 142 on the
# strength of a cut that turns out to have sliced it, so it comes off again.
for pid in ['disp2', 'disp3', 'rx086']:
    tag = '{"id":"%s"' % pid
    if tag not in s:
        print('  -- %s: not a JSON record, featured flag left alone' % pid)
        continue
    a1 = s.index(tag)
    a2 = s.index('},{', a1) + 1
    rec = s[a1:a2]
    if '"featured":true' in rec:
        s = s[:a1] + rec.replace('"featured":true', '"featured":false') + s[a2:]
        print('  ok: %s no longer leads the shelf' % pid)
    else:
        print('  -- %s already off the front of the shelf' % pid)

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
