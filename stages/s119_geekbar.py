#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 119 — the Geek Bar, and the mess on the Off-Stamp.
#
# Marco: "For the geek bars the full left side of the vape is just cropped,
# dont change the vapes or promotions. I asked you multiple times to uncrop the
# purple vape and even on the Disposable Vapes Category I see you literally
# just replaced it with a vape no one knows."
#
# Two separate faults, and only one of them was the frame.
#
# THE FRAME was stage 117: the card was slicing the artwork because the artwork
# was positioned to hang off it. Fixed there.
#
# THE PICTURE IS ALSO CUT, and this is the part I kept missing. Enlarged, the
# Geek Bar Pulse 15K file is a wholesaler's slide: the retail carton on the
# left, a white panel with the nicotine warning across the bottom of it, and
# the purple vape on the right — with the vape's own right edge running off the
# edge of the photograph. The frame was cutting a picture that was already cut.
# No positioning fixes that. Only a different photograph does.
#
# THE TILE. He is right that swapping in the North 5000 was the wrong answer to
# a cropping problem: it fixed the crop by changing the subject, and the subject
# it changed to is a brand nobody walks in asking for. The tile is a Geek Bar
# again — the 2GO 50K, which is the one Geek Bar photograph in this catalogue
# that is a single complete device on nothing, so it is both the brand he asked
# for and a picture that does not need cropping to be shown whole.
#
# THE OFF-STAMP. "The off-stamp just have a tiny bit of a mess up on the bottom
# left corner of the vape." There is: a keying notch in the corner of the
# orange device, left over from a cut-out taken off a busy background. Replaced
# with the maker's own single-device frame — one X-Cube, complete, no carton, no
# warning panel, 258x465 against 312x234 of carton-and-vape.
import io
import json
import base64
import os

from PIL import Image

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- 1. the Off-Stamp, without the carton or the keying notch --------------
k = 'const CUT_PHOTOS = '
i = s.index(k)
j = s.index('};\n', i) + 1
cut = json.loads(s[i + len(k):j])

src = '/tmp/sp3/gb/osk_ablekitf_cut.png'
if os.path.exists(src):
    im = Image.open(src)
    if max(im.size) > 660:
        r = 660 / max(im.size)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    buf = io.BytesIO()
    im.convert('RGBA').save(buf, 'WEBP', quality=84, method=6)
    was = len(cut.get('rx065', ''))
    cut['rx065'] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    s = s[:i] + k + json.dumps(cut, separators=(',', ':')) + s[j:]
    print('  ok: rx065 Off-Stamp X Cube, one device, %d -> %d bytes' % (was, len(cut['rx065'])))
else:
    print('  !! %s missing, Off-Stamp left as it was' % src)

# ---- 2. the tile is a Geek Bar again ---------------------------------------
rep("""  {k:'disp',  n:'Disposable Vapes',        img:()=>LOCAL_PHOTOS['rx057']||catFallbackImage('disp')},""",
"""  /* A GEEK BAR, AND A WHOLE ONE.
     Swapping in a North 5000 fixed the crop by changing the subject, which is
     not a fix. This is the 2GO 50K: the one Geek Bar photograph in this
     catalogue that is a single complete device on nothing, so it is the brand
     the shelf actually leads with AND a picture that survives being shown
     whole. The Pulse 15K file cannot be used here at any size, because the
     vape in it is cut off by the edge of the photograph itself. */
  {k:'disp',  n:'Disposable Vapes',        img:()=>LOCAL_PHOTOS['rx2go']||catFallbackImage('disp')},""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
