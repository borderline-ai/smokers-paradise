#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 92 — twelve pictures that were not pictures of the product.
#
# All 259 published images were laid out on contact sheets and read one by one.
# Twelve are carrying something that belongs to the website they came off,
# not to the thing the shop is selling. Every crop below was made, rendered on
# the card's own plum plate beside the original, and looked at before it was
# accepted. Three were rejected on sight and redone.
#
# A. A COMPETITOR'S WEB ADDRESS ON THREE PRODUCT CARDS.
#    rx073 Tyson MIA 50K, rx074 Iron Mike 15K, rx075 Tyson 2.0 Round 2 are not
#    photographs at all. They are a wholesaler's advertising slide: a TYSON
#    logo block across the top, the product, a vertical WARNING sidebar the
#    packaging already carries, and MIKETYSONOFFICIAL.COM printed in red across
#    the bottom. In an app built for Smokers Paradise, three cards were sending
#    customers to somebody else's website.
#    Each is cropped to the product alone: the carton for the MIA, the device
#    for the other two. The nicotine warning stays where it is legally supposed
#    to be, printed on the package in the picture.
#
# B. A RETAILER'S USER INTERFACE, PHOTOGRAPHED.
#    rx092 RAZ DC25000 carries a green rounded pill reading "Sour Watermelon
#    Peach" floating above the product. That is a flavour chip from the web
#    page the image was taken from. Cropped off; the carton beneath says the
#    same flavour in its own type.
#
# C. A WARNING BANNER THAT IS NOT ON THE PACKAGE.
#    hook1 and rx028, both Al Fakher shisha, have a white rectangle floating
#    clear above the tin with a gap of empty pixels between them. It is an
#    overlay the source site stamps on, not part of the product, and on a card
#    it reads as a broken composite. Cropped to the tin. The app's own nicotine
#    notice still sits at the foot of every shelf, in both languages.
#
# D. SPEC DRAWINGS BEING USED AS PACKSHOTS.
#    rx100, rx102, rx103, rx104, rx107 and rx144 are the manufacturer's
#    dimension drawings: a ruler across the top with a measurement, a second
#    one down the side, and on several of them a white smear where the shadow
#    was keyed off. Rulers cropped, and on the five that are coloured glass the
#    detached white blob is removed as well.
#
#    NOT on rx107 and rx144. Both are CLEAR glass, which is pale and neutral
#    exactly like a keying smear, and the first attempt at them deleted most of
#    the product: the Caldera Bowl came back as 129x55 of fragments. They get
#    the crop and nothing else. Clear glass is never passed through a
#    pale-pixel filter.
#
# WHAT WAS DELIBERATELY NOT DONE. The same detached-blob rule, run across the
# whole catalogue, offers to touch 41 more images for a percent or two each.
# Several of those percent-or-two are the white warning panel printed on a
# carton, which must stay, and telling them apart reliably is not something a
# threshold can do. Twelve pictures were changed, each one looked at. The rest
# stand.
import io
import json
import base64

P = '/root/work/smokers-paradise-demo/build/index.html'
IDS = ['rx073', 'rx074', 'rx075', 'rx092', 'hook1', 'rx028',
       'rx100', 'rx102', 'rx103', 'rx104', 'rx107', 'rx144']

s = io.open(P, encoding='utf-8').read()
n0 = len(s)

new = {}
for pid in IDS:
    with open('/tmp/spnight/art/%s-clean.webp' % pid, 'rb') as f:
        new[pid] = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()

k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cur = json.loads(s[i + len(k):j])
missing = [p for p in IDS if p not in cur]
assert not missing, 'not in CUT_PHOTOS: %s' % missing
before = sum(len(cur[p]) for p in IDS)
cur.update(new)
after = sum(len(cur[p]) for p in IDS)
s = s[:i] + k + json.dumps(cur, separators=(',', ':')) + s[j:]
print('  ok: %d photographs recut (%d -> %d bytes of image data)'
      % (len(IDS), before, after))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
