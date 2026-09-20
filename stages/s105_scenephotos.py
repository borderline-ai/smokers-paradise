#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 105 — eight photographs that are not cut-outs, and were pretending to be.
#
# Marco: "When you click throughout the flavors and products there is no
# consistency with backgrounds and cuts and a lot of different things cropped
# with bad inconsistent backgrounds that make it look unprofessional."
#
# 251 of the 259 photographs are cut-outs: the product, keyed off its studio
# sweep, floating on the app's plum stage with a contact shadow under it.
# EIGHT are not. They are the maker's own lifestyle photography — the Uwell on
# a laptop, King Palm on palm leaves, the Air Bar on concrete, the Gem on
# crystals, RAZ on its orange field, two Lookah rigs lit on plinths, Session
# Goods glowing on a tiled floor — and they were being rendered through the
# cut-out rules: floated at 90% of the tile with a drop shadow and a contact
# shadow, as if the rectangle of concrete were the shape of the product.
#
# That is the inconsistency. A keyed product floats; a photograph is a
# rectangle. Floating a rectangle looks like a cut-out that failed.
#
# WHAT WAS TRIED FIRST, AND WHY IT WAS THROWN AWAY. Keying all eight, so every
# card in the app carries the same treatment. A saturation and luminance mask,
# largest component, fill, dilate, trim. Measured on the results: one worked
# (the Air Bar, and even that kept a grey fringe of concrete), five were
# untouched because the subject filled the frame, and the two Lookah rigs —
# clear glass on a lit grey backdrop — came apart into white blobs. Clear glass
# has no silhouette to find. Keying it destroys it, which is the same lesson
# stage 103 learned about connected components, arriving by a different road.
#
# So the eight stay photographs, and are made to LOOK like photographs on
# purpose: edge to edge in the tile, filling it, with the tile's own corner
# radius, no drop shadow and no contact shadow, because a photograph does not
# stand on the stage, it IS the stage. Beside a floating cut-out it now reads
# as a second deliberate treatment rather than as a broken first one.
#
# Six of the eight are square and fill a square tile exactly. The two Lookah
# rigs are 255x340, so filling a square tile would crop a quarter of their
# height and cut the mouthpiece off. Both are extended to square on a backdrop
# built out of their own photograph — scaled up, blurred hard, pulled toward
# the app's plum — so the frame grows and nothing in the picture is invented,
# moved or cropped. The product sits exactly where the photographer put it.
import io
import json
import base64

import numpy as np
from PIL import Image, ImageFilter

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. square the two tall ones on a backdrop made of themselves ----------
k = 'const SCENE_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
scene = json.loads(s[i + len(k):j])

for pid in ('rx140', 'rx141'):
    im = Image.open(io.BytesIO(base64.b64decode(scene[pid].split(',', 1)[1]))).convert('RGB')
    if im.width == im.height:
        continue
    S = max(im.size)
    k2 = S / min(im.size) * 1.25
    bd = im.resize((int(im.width * k2), int(im.height * k2)), Image.LANCZOS)
    bx, by = (bd.width - S) // 2, (bd.height - S) // 2
    bd = bd.crop((bx, by, bx + S, by + S)).filter(ImageFilter.GaussianBlur(26))
    bd = Image.blend(bd, Image.new('RGB', (S, S), (24, 14, 34)), 0.22)
    bd.paste(im, ((S - im.width) // 2, (S - im.height) // 2))
    tmp = '/tmp/spnight/_sq.webp'
    bd.save(tmp, 'WEBP', quality=84, method=6)
    with open(tmp, 'rb') as fh:
        scene[pid] = 'data:image/webp;base64,' + base64.b64encode(fh.read()).decode()
    print('  ok: %s %dx%d -> %dx%d on its own backdrop' % (pid, im.width, im.height, S, S))

s = s[:i] + k + json.dumps(scene, separators=(',', ':')) + s[j:]

# ---- 2. the app knows which ids are photographs ----------------------------
rep("""const LOCAL_PHOTOS = Object.assign({}, SCENE_PHOTOS, CUT_PHOTOS);""",
"""const LOCAL_PHOTOS = Object.assign({}, SCENE_PHOTOS, CUT_PHOTOS);
/* The eight that are photographs rather than cut-outs. A cut-out floats on the
   stage with a shadow under it; a photograph fills the frame. Rendering the
   second through the first is what made a rectangle of concrete look like a
   failed key. */
const SCENE_IDS = new Set(Object.keys(SCENE_PHOTOS));""")

# ---- 3. tag the image when it is one of those eight ------------------------
rep("""/* the drawn object: step 4 of the chain, and the landing place whenever a
   remote host refuses to serve us */""",
"""/* A photograph, not a cut-out: it fills its frame instead of floating in it.
   Wrapped rather than threaded through art()'s eight return points, because
   the question is about the file that came out, not about which branch found
   it. Only the model-level embedded photograph is a scene photograph; a
   flavour the customer picked resolves to its own file and keeps the cut-out
   treatment. */
(function(){
  const inner = art;
  art = function(p, vkey, strict){
    const h = inner(p, vkey, strict);
    if(p && SCENE_IDS.has(p.id) && h.slice(0,10) === '<img src="'
       && !(vkey && PHOTOS[p.id+'::'+vkey]))
      return '<img class="scenephoto" ' + h.slice(5);
    return h;
  };
})();

/* the drawn object: step 4 of the chain, and the landing place whenever a
   remote host refuses to serve us */""")

# ---- 4. and the stylesheet renders it as one -------------------------------
rep("""/* the product page: a bigger stage, same light */
.pdp-art{aspect-ratio:1/1;display:grid;place-items:center;padding:22px}""",
"""/* ---- THE EIGHT THAT ARE PHOTOGRAPHS ----
   The maker's own lifestyle shot, not a keyed product. It fills the frame
   edge to edge and takes the frame's corner radius: no inset, no padding, no
   drop shadow, no contact shadow. A cut-out stands on the stage. A photograph
   is the stage. Declared here and again after the framing rules, because the
   cut-out rules that follow are more specific than they look. */
.scenephoto{position:absolute!important;inset:0!important;
  width:100%!important;height:100%!important;padding:0!important;
  max-width:none!important;max-height:none!important;
  object-fit:cover!important;object-position:center!important;
  filter:none!important;border-radius:inherit}
.card .thumb:has(.scenephoto)::after,.pdp-art:has(.scenephoto)::after,
.spotitem .sp:has(.scenephoto)::after{display:none}

/* the product page: a bigger stage, same light */
.pdp-art{aspect-ratio:1/1;display:grid;place-items:center;padding:22px}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
