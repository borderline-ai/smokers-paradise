#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 160 — the worst photograph in the app had the biggest box.
#
# Marco, pointing at the shelf picture on the store page: "this picture looks
# low quality and old, I'm sure you can find a better picture."
#
# He is right, and the interesting part is WHY, because the picture is not the
# only thing wrong with it. One CSS line decides which photo is big:
#
#     .phgrid .ph:first-child{grid-column:1/-1}
#
# The first photo in the grid runs the full width of the screen. The rest sit
# two to a row at half that. And the photo that happened to be listed first was
# the softest photograph the shop has ever published.
#
# ======================================================================
# MEASURED, NOT EYEBALLED
# ======================================================================
# Focus here is the variance of the Laplacian — the standard way to measure how
# much real detail a photograph holds, and the thing that was never checked
# before a photo was placed. Measured on the four store photos AT THE SIZE THE
# APP ACTUALLY PAINTS THEM, which is the only measurement that matters:
#
#   painted full width, 860 device pixels
#     inside    540x891   upscaled 1.59x     focus  89.6    <- the big slot
#     front     720x960   upscaled 1.19x     focus 248.7
#     display   540x901   upscaled 1.59x     focus 399.9
#     glass     720x960   upscaled 1.19x     focus 617.8    <- seven times more
#
#   painted in a half-width slot, 418 device pixels
#     inside                                 focus 721.6
#     glass                                 focus 2088.6
#     display                               focus 2302.0
#
# Read the two tables together and the mistake is plain. The soft photo was
# being blown up 1.59x into the biggest box on the page, where it holds 89 units
# of detail — while the sharpest photo in the set sat in a small box being shrunk
# to a quarter of the area, where nobody could see how good it was. Every photo
# on that page holds more detail in the SMALL slot than the one in the big slot
# holds. The soft one at half width still measures 721 against the big one's 89.
#
# ======================================================================
# THE FIX IS THE ORDER, NOT THE FILE
# ======================================================================
# So nothing is deleted, nothing is upscaled and nothing is sharpened, because
# sharpening is inventing detail that was never in the lens. The order changes:
#
#     was   inside (big)   glass (small)   display (small)
#     now   glass (big)    display (small) inside (small)
#
# The big picture goes from 89.6 to 617.8 units of detail, a seven-fold
# improvement, out of a file that was already in the app. The soft one keeps its
# place in the section, at a size where it holds up.
#
# ======================================================================
# WHY THERE IS NO BETTER PICTURE OF THAT WALL
# ======================================================================
# Because Marco asked me to find one, and the honest answer is that it does not
# exist yet. Every photograph in this app came out of the shop's own Instagram.
# Twenty one frames were harvested. Exactly two show the paper wall and both are
# frames from the same story pan: t00 at focus 475 and s01 at 495, both 540
# pixels wide, both tilted, both with the @SMOKERS_PARADISE_NOGALES sticker
# burned across the bottom. There is no third frame and Instagram does not serve
# a bigger one — its stories come down at 540, and this container's egress
# refuses instagram.com anyway.
#
# THE REAL FIX IS THIRTY SECONDS WITH A PHONE. A modern phone shoots that wall
# at about 4,000 pixels across. That is roughly eight times the width and sixty
# times the pixels of what the app is working from, and it would be the sharpest
# thing on the page by an order of magnitude. Three photos, held straight,
# with the lights on:
#
#     the paper wall, square on, from about six feet
#     the device wall, the same way
#     somebody behind the counter who is happy to be photographed
#
# The third one also fills "Meet the Crew", which has been standing empty since
# stage 97 because the only crew photo the feed offers is a comedy reel still.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

a = """    <div class="phgrid">
      ${photoSlot(galleryItem('inside'))}
      ${photoSlot(galleryItem('glass'))}
      ${photoSlot(galleryItem('display'))}
    </div>"""
assert s.count(a) == 1, s.count(a)
b = """    ${/* THE FIRST ONE IN HERE RUNS THE FULL WIDTH (.phgrid .ph:first-child),
           so the order of these three lines decides which photograph gets the
           biggest box on the page. It used to be the softest one the shop has:
           blown up 1.59x it held 89 units of detail where the glass shot holds
           618 at the same size. Sharpest first, measured at the size it is
           painted. See scripts/s160_photo_order.py for the numbers. */''}
    <div class="phgrid">
      ${photoSlot(galleryItem('glass'))}
      ${photoSlot(galleryItem('display'))}
      ${photoSlot(galleryItem('inside'))}
    </div>"""
s = s.replace(a, b)
print('  ok: the sharpest photograph leads the grid')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
