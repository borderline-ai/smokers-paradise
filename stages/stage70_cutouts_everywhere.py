#!/usr/bin/env python3
# Stage 70 — the white rectangle, removed from every product in the app.
#
# "Almost every product is sitting inside a plain white rectangle."
#
# It was true, and the earlier pass only fixed it on the promotional surfaces:
# thirty transparent cut-outs were embedded for the campaigns, the deal ads and
# the department tiles, while all 266 product cards, every product page and
# every rail still showed the manufacturer's packshot with its studio sweep on
# a near-white panel (--stage: #F2EFF5).
#
# The cut-out pipeline had already produced 249 of them and they were sitting
# unused on disk. This stage puts every one of them into the file at 340px and
# makes them the product image everywhere, so a product stands on the app's own
# ground with its own light and shadow instead of inside a box.
#
# The seventeen with no cut-out were checked by eye: they are photographed on
# black or in scene, not on white, so there is no sweep to remove. They keep
# their photograph.
#
# Size stays flat, because the cut-outs REPLACE the packshots rather than being
# added alongside them — one copy of the data, exposed under both names so
# nothing downstream has to change.
import base64
import io
import json
import os

P = '/root/work/smokers-paradise-demo/build/index.html'
CUT = '/tmp/cut340'
PHOTO = '/root/work/assets/products'

s = io.open(P, encoding='utf-8').read()
n0 = len(s)

cut_ids = sorted(f[:-5] for f in os.listdir(CUT) if f.endswith('.webp'))
all_ids = sorted(f[:-5] for f in os.listdir(PHOTO) if f.endswith('.webp'))
only_photo = [i for i in all_ids if i not in set(cut_ids)]
print('  %d cut-outs, %d photographs with no sweep to remove'
      % (len(cut_ids), len(only_photo)))


def uri(path):
    return 'data:image/webp;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


cuts = {i: uri(os.path.join(CUT, i + '.webp')) for i in cut_ids}
phots = {i: uri(os.path.join(PHOTO, i + '.webp')) for i in only_photo}
print('  cut-outs %.2f MB, remaining photographs %.2f MB'
      % (sum(len(v) for v in cuts.values()) / 1048576,
         sum(len(v) for v in phots.values()) / 1048576))

# ---- swap the data ---------------------------------------------------------
i = s.index('const LOCAL_PHOTOS = {')
j = s.index('};', i) + 2

BLOCK = (
    'const CUT_PHOTOS = ' + json.dumps(cuts, separators=(',', ':')) + ';\n'
    '/* The seventeen shot on black or in scene: no studio sweep to remove. */\n'
    'const SCENE_PHOTOS = ' + json.dumps(phots, separators=(',', ':')) + ';\n'
    '/* One copy of the data, under both of the names the app already uses. */\n'
    'const CUTOUTS = CUT_PHOTOS;\n'
    'const LOCAL_PHOTOS = Object.assign({}, SCENE_PHOTOS, CUT_PHOTOS);\n'
    '/* which ids are transparent, so a surface can light them differently */\n'
    'const HAS_CUTOUT = id => Object.prototype.hasOwnProperty.call(CUT_PHOTOS, id);'
)
s = s[:i] + BLOCK + s[j:]
print('  photograph table replaced')

# the old thirty-entry CUTOUTS literal is now dead weight
k = s.find('const CUTOUTS = {"')
if k >= 0:
    k2 = s.index('};', k) + 2
    dropped = k2 - k
    s = s[:k] + '/* superseded: CUTOUTS is now the full 249-entry table above. */' + s[k2:]
    print('  dropped the old 30-entry cut-out table (%.0f KB)' % (dropped / 1024))

CSS = r'''
/* ==========================================================================
   THE PRODUCT STAGE
   Every product is a transparent cut-out now, so it no longer needs a white
   panel to hide a white photograph. It stands on the app's own ground with a
   light behind it and a contact shadow under it — the same treatment the
   campaigns and the department tiles already used.
   ========================================================================== */
:root{--stage:#1B1029}

.card .thumb,.pdp-art,.spotitem .sp,.btile .bp,.dcard .dart .dplate,
.bagrow .bimg,.ckline .th,.stage-panel,.rail-cards .thumb{
  background:
    radial-gradient(72% 58% at 50% 40%, rgba(255,123,200,.13) 0%, transparent 68%),
    linear-gradient(158deg,#1E1230 0%,#170D24 62%,#120A1C 100%);
  border-radius:var(--r-card);
  box-shadow:inset 0 0 0 1px rgba(255,120,205,.10);
  position:relative;
  overflow:hidden;
}
.card .thumb img,.pdp-art img,.spotitem .sp img,.btile .bp img,
.bagrow .bimg img,.ckline .th img,.stage-panel img{
  position:relative;z-index:2;
  object-fit:contain;
  filter:drop-shadow(0 8px 12px rgba(0,0,0,.55));
}
/* the contact shadow that makes a cut-out stand rather than float */
.card .thumb::after,.pdp-art::after,.spotitem .sp::after{
  content:"";position:absolute;left:50%;bottom:7%;
  width:56%;height:8px;transform:translateX(-50%);
  border-radius:50%;filter:blur(6px);z-index:1;pointer-events:none;
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(0,0,0,.55) 0%, rgba(0,0,0,.18) 58%, rgba(0,0,0,0) 100%);
}
/* the product page: a bigger stage, same light */
.pdp-art{aspect-ratio:1/1;display:grid;place-items:center;padding:22px}
.pdp-art img{max-width:82%;max-height:82%}
/* the variant thumbnails match the stage rather than punching a white hole */
.vthumb,.pdp-thumbs button{
  background:linear-gradient(158deg,#1E1230,#140C20);
  border:1px solid rgba(255,120,205,.16);
  border-radius:12px;
}
.vthumb.on,.pdp-thumbs button.on{border-color:var(--go)}
.vthumb img,.pdp-thumbs button img{object-fit:contain}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  stage styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes (%.2f MB)' % (n0, len(s), len(s) / 1048576))
