#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 104 — the product was small inside its own frame.
#
# Marco: "The way you display the pictures. Centered, correctly displayed."
#
# Stage 103 fixed what was IN the picture. This is where it is put.
#
# MEASURED, on the product page, before:
#
#     the stage        356 x 356
#     the image capped at max-width 88% / max-height 88%
#     Seahorse Queen   drew 138 x 250, filling 27% of the stage
#     Pulsar straw     drew  32 x 253, filling  6%
#     Geek Bar         drew 246 x 249, filling 48%
#
# A cap on BOTH axes means a tall product is limited by its width and a wide one
# by its height, so anything that is not roughly square is rendered small and
# then centred in a large empty panel. On a page whose whole job is to show one
# product, the product was a quarter of the frame.
#
# The image now fills the stage and is fitted inside a single even padding, so
# the longest side of every product reaches the same distance from the frame and
# the short side falls where it falls. A tall straw is a tall straw: it can
# never fill a square, but it is now as big as the frame allows rather than as
# big as its narrowest dimension allows.
#
#     Seahorse Queen   27%  ->  45%
#     Pulsar straw      6%  ->  10%
#     Geek Bar         48%  ->  81%
#
# The card thumbnails get the same treatment at a smaller inset: 9% of a 161px
# tile is 15px of nothing on every side of every one of 259 cards.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep(""".card .thumb>svg,.card .thumb>img{position:absolute;inset:9%;width:82%;height:82%;
  object-fit:contain;object-position:center}""",
""".card .thumb>svg,.card .thumb>img{position:absolute;inset:5%;width:90%;height:90%;
  object-fit:contain;object-position:center}""")

# the product page stage: fill it, pad it once, centre it
rep(""".pdp-art{padding:16px}""",
""".pdp-art{padding:16px}
/* THE PRODUCT IS THE PAGE.
   The stage is 356 x 356 and the image was capped at 88% on BOTH axes, which
   means a tall product is limited by its width and a wide one by its height.
   Measured: the Seahorse Queen filled 27% of the stage and the Pulsar nectar
   collector filled 6%, on the one screen whose entire job is to show one
   product. Fill the stage, pad it once, and let the longest side of every
   product reach the same distance from the frame. */
.pdp-art img{width:100%;height:100%;max-width:none;max-height:none;
  object-fit:contain;object-position:center;padding:4%;box-sizing:border-box}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
