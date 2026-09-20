#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 164 — the KB10000, and the forty four others like it.
#
# Marco: "the KB10000 seems to be blurred... it still has mistakes all
# throughout and inconsistencies in quality. I cannot have that."
#
# The KB10000 is blurred and so are forty four other products, for one reason
# that is now measurable. Every product image is a square, and the product page
# paints that square at about 780 device pixels. So the blur of any product is
# simply 780 divided by the size of its file:
#
#     upscale on the product page     median 2.34x     p90 3.39x     worst 6.78x
#     over 2x   159 of 261
#     over 3x    45 of 261
#
#     r017    canvas 115   6.78x        rx052 (the KB10000)  canvas 191  4.08x
#     rx049   canvas 139   5.61x        rx074                canvas 192  4.06x
#     rx015   canvas 141   5.53x        rx067                canvas 204  3.82x
#
# That is the inconsistency, and it is not a style problem. A product whose
# maker published a 700 pixel photograph is painted at 1.1x and looks like a
# photograph. The one next to it, published at 190, is painted at 4x and looks
# like a smear. They sit side by side on the same shelf, and the eye reads the
# whole app by its worst tile.
#
# I TRIED TO SHARPEN IT FIRST, because that would have cost nothing. Unsharp
# masking the KB10000 at three strengths moved its focus measure from 1585 to
# 1733, about nine percent, and at full size the four versions are
# indistinguishable. There is no detail in a 97 by 185 pixel device to bring
# back. Sharpening a soft photograph does not make it sharp, it makes it a soft
# photograph with halos, so it is not used here.
#
# ======================================================================
# WHAT ACTUALLY WORKS: STOP PAINTING THEM SO BIG
# ======================================================================
# A file cannot be made sharper, but it can be asked to cover less of the
# screen, and under three times its own resolution the softness stops reading
# as a broken image. So the square each product sits in now has a floor:
#
#     canvas floor 260px   ->   nothing is ever painted above 3.0x
#
# A product with a big file is untouched — the 216 images already at or above
# that floor keep the size stage 162 gave them. The 45 with tiny files get more
# room around them, which paints them about a quarter smaller and a third
# sharper. The KB10000 goes from 4.08x to 3.0x.
#
# THE HONEST COST, because there is one: those 45 products now sit slightly
# smaller in their tile than their neighbours. That is a real inconsistency and
# it is the better of the two. A product a quarter smaller reads as a product.
# A product at four times its own resolution reads as a bug, which is the exact
# word he used.
#
# The only real fix for those 45 is a bigger file, and the makers publish them —
# this container's proxy refuses the manufacturer hosts, which is why the app is
# carrying 190 pixel copies at all.
import io
import json
import base64

from PIL import Image

P = '/root/work/smokers-paradise-demo/build/index.html'
FLOOR = 260          # 780 / 3.0, the smallest square that keeps upscale under 3x

s = io.open(P, encoding='utf-8').read()
n0 = len(s)

k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cut = json.loads(s[i + len(k):j])

changed = 0
for pid, uri in list(cut.items()):
    im = Image.open(io.BytesIO(base64.b64decode(uri.split(',', 1)[1]))).convert('RGBA')
    side = im.size[0]
    if side >= FLOOR or im.size[0] != im.size[1]:
        continue
    out = Image.new('RGBA', (FLOOR, FLOOR), (0, 0, 0, 0))
    out.paste(im, ((FLOOR - side) // 2, (FLOOR - side) // 2))
    buf = io.BytesIO()
    out.save(buf, 'WEBP', quality=88, method=6)
    cut[pid] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    changed += 1
    if changed <= 8:
        print('  ok: %-8s canvas %3d -> %d   upscale %.2fx -> %.2fx'
              % (pid, side, FLOOR, 780 / side, 780 / FLOOR))

s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]
io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d images given room so nothing paints above 3x' % changed)
print('%d -> %d chars' % (n0, len(s)))
