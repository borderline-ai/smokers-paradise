#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 90 — the sixteen category tiles, looked at one at a time.
#
# The tiles are the first product artwork on the home screen and the thing an
# owner's eye lands on. All sixteen were pulled out of the file and rendered
# side by side at four times their real size. Two are wrong.
#
# 1. DISPOSABLE VAPES IS A CARTON, AND THE CARTON'S BIGGEST FEATURE IS A WHITE
#    BOX READING "WARNING: THIS PRODUCT CONTAINS NICOTINE". It is the first
#    tile, top left, above the fold. Stage 84 took exactly this panel off the
#    hero banners by cropping the device out of the carton, and the crop it
#    made for the Geek Bar Pulse X is already in this file. The tile just never
#    asked for it. It does now, through the same adCut() the banners use, so
#    any tile whose product has a device crop gets the device and every other
#    tile is unchanged.
#
#    The warning stays where it belongs: on the product's own card and its own
#    page, where a customer is looking at the thing they are buying.
#
# 2. HAND PIPES IS A SPEC DIAGRAM. The GRAV Classic Spoon photograph is the
#    manufacturer's dimension drawing: a ruler line across the top labelled
#    1.5", a second one down the left, and a white smear under the pipe where
#    the shadow was keyed off. Of the seventeen hand pipes in the catalogue,
#    the Sandblasted Spoon is cut cleanly, has no measurement marks, and is
#    the shop's own pink.
#
# NOT CHANGED, AND WRITTEN DOWN SO THE NEXT PASS DOES NOT RE-OPEN IT:
#    Backwoods Cigars 8 Packs of 5 (rx040) and Singles Cigars Pack of 24
#    (rx041) both carry a wholesaler's dollar-sign watermark stamped across the
#    box. There is no clean copy of either in this file and no way to fetch one
#    from here. They are two cards deep in the Wraps & Cigars shelf rather than
#    on the home screen, so they stay, and they need a replacement photograph
#    from the distributor before this app is anything other than a demo.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. a tile shows the device when there is one --------------------------
rep("""      const pid = tilePid(c);
      const src = pid ? cutout(pid) : (typeof c.img==='function' ? c.img() : '');""",
"""      const pid = tilePid(c);
      /* adCut hands back the device crop when this file holds one and the full
         cut-out when it does not. The banners have used it since stage 84;
         the tiles were still asking for the carton, nicotine warning and all. */
      const src = pid ? (typeof adCut === 'function' ? adCut(pid) : cutout(pid))
                      : (typeof c.img==='function' ? c.img() : '');""")

# ---- 2. hand pipes stops being a ruler -------------------------------------
rep("""  {k:'hand',  n:'Hand Pipes',              img:()=>img('GRAV','Classic Spoon')||catFallbackImage('hand')},""",
"""  /* The GRAV Classic Spoon photograph is a dimension drawing: two ruler lines
     and a keying smear. The Sandblasted Spoon is cut clean and is the right
     colour for this app. */
  {k:'hand',  n:'Hand Pipes',              img:()=>img('GRAV','Sandblasted Spoon')
                                              ||img('GRAV','Pebble Spoon')
                                              ||catFallbackImage('hand')},""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
