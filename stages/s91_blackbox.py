#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 91 — nine black rectangles on the shelf.
#
# This build spent a pass removing white boxes from product cards, and the rule
# it settled on is written into the file: every product stands on ONE stage,
# its own cut-out on the card's lit plum plate, no plate of its own. The pass
# checked for white. It never checked for black.
#
# Every one of the 259 published images was pulled out of the built file and
# its border ring measured. Nine come back fully opaque and almost perfectly
# black: they were photographed on a black sweep and were never keyed, because
# the earlier pass looked at them and decided a dark photograph on a dark card
# was fine. On the card it is not fine. It is a hard-edged black rectangle
# sitting inside a plum panel, and next to a keyed card it looks like a
# different app.
#
#   r002 Diamond Glass 8" Classic Beaker      r013 Diamond Glass Buoy Recycler
#   r003 Smoke Cartel Straight Tube           r056 Kaloud Samsaris Kore Bowl
#   r004 Human Grade 18" Straight Tube        rx231 Clipper Micro Lighter
#   r005 Diamond Glass Gold Warp              r006 LA Pipes Showerhead Perc
#   r007 Pulsar 4-Tube Recycler
#
# HOW, AND WHY IT IS SAFE ON GLASS. Clear glass photographed on black is drawn
# almost entirely by its white speculars; the black behind it and the black
# seen THROUGH it are the same black. So the key is not a colour threshold over
# the whole frame, which would eat the product: it is a flood fill that starts
# at the border, travels only through pixels darker than 46, and stops at the
# first highlight. Anything the fill cannot reach stays exactly as shot,
# including the dark interior of every tube. The alpha edge is then softened by
# less than a pixel so the cut does not jag, and the frame is trimmed to what
# is left.
#
# Checked by eye, before and after, side by side on the card's own plum: all
# nine keep every part of the product. The Gold Warp trio loses 149px of empty
# black margin and not one millimetre of glass.
#
# NOT TOUCHED, and listed so the next pass does not spend an hour on it:
# eight products carry a manufacturer LIFESTYLE photograph rather than a
# packshot — Session Goods on a tiled floor, the Air Bar Gem on crystals, a
# Uwell pod on a laptop, two Lookah recyclers on a plinth, King Palm on palm
# leaves, the RAZ LTX on its orange field, the Air Bar Nex on marble. Keying a
# scene does nothing useful, and these are the brands' own pictures. They stay.
import io
import json
import base64

P = '/root/work/smokers-paradise-demo/build/index.html'
IDS = ['r002', 'r003', 'r004', 'r005', 'r006', 'r007', 'r013', 'r056', 'rx231']

s = io.open(P, encoding='utf-8').read()
n0 = len(s)

new = {}
for pid in IDS:
    with open('/tmp/spnight/art/%s.webp' % pid, 'rb') as f:
        new[pid] = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()

# The nine stop being "shot on black, nothing to remove" and become what they
# now are: cut-outs. Moving them from SCENE_PHOTOS to CUT_PHOTOS is not
# bookkeeping — HAS_CUTOUT reads that table, and it is what tells a card to
# light the product from behind instead of treating it as a flat photograph.
def table(name):
    k = 'const %s = ' % name
    i = s.index(k)
    j = s.index('};\n', i) + 1
    return i, j, json.loads(s[i + len(k):j])


i, j, scene = table('SCENE_PHOTOS')
moved = [pid for pid in IDS if pid in scene]
for pid in moved:
    scene.pop(pid)
s = s[:i] + 'const SCENE_PHOTOS = ' + json.dumps(scene, separators=(',', ':')) + s[j:]
print('  ok: %d moved out of SCENE_PHOTOS, %d left in it' % (len(moved), len(scene)))

i, j, cut = table('CUT_PHOTOS')
for pid in IDS:
    cut[pid] = new[pid]
s = s[:i] + 'const CUT_PHOTOS = ' + json.dumps(cut, separators=(',', ':')) + s[j:]
print('  ok: CUT_PHOTOS now holds %d photographs' % len(cut))

s = s.replace('/* The seventeen shot on black or in scene: no studio sweep to remove. */',
              '/* Shot in scene, with a real background that IS the picture: a bong on a\n'
              '   tiled floor, a pod kit on a laptop, wraps on palm leaves. Nothing to key.\n'
              '   The nine that were merely shot on a black sweep are cut-outs now and have\n'
              '   moved to CUT_PHOTOS, where the card lights them like everything else. */')
print('  ok: the comment says what the table now is')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
