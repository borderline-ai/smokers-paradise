#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 139 — the smoke did not scroll with the page.
#
# The haze is gone and the plumes are thin again, and one white blob is still
# sitting in the bottom left of the footer screenshot with nothing above it.
# Marco has been pointing at this all along, in the sentence I read as being
# only about reach:
#
#     "I dont want it to glitch at all."
#
# HERE IS THE GLITCH, and it is a coordinate system mistake, not a tuning one.
# The canvas is pinned to the phone. A particle's position is stored in SCREEN
# coordinates, and it is never touched when the page scrolls. So the emitter
# moves — sources() re-measures every mark from its bounding box every frame,
# correctly — and everything it has already thrown stays exactly where it was
# on the glass. Scroll the page a screen and a half and the column detaches
# from the logo and hangs in the middle of the screen with no source under it,
# growing and fading on its own. That is the stranded blob, and the faster you
# scroll the worse it looks.
#
# SMOKE BELONGS TO THE PAGE, NOT TO THE SCREEN. Every particle now moves by
# the scroll delta each frame, so the column stays attached to the mark that
# threw it, all the way up, however fast the page is moving. Scroll away and
# the whole column travels off the top of the screen with its logo, which is
# both correct and exactly what he asked for: no logo, no smoke.
#
# And anything that ends up a long way below the bottom edge is dropped rather
# than simulated forever.
#
# The gate and the hero do not need this: their canvases are children of the
# thing that scrolls, so they move with it already. Only the phone-wide surface
# is pinned to the glass, and only it has to be corrected.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""    const srcs = this.sources();
    /* WHICH MARKS ARE ACTUALLY ON THE SCREEN RIGHT NOW.""",
"""    /* THE SMOKE MOVES WITH THE PAGE.
       A particle is stored in screen coordinates and this canvas is pinned to
       the phone, so until now the emitter moved with the page and everything
       it had already thrown stayed on the glass: scroll a screen and the
       column detached from the logo and hung there with no source under it.
       Shift every particle by the scroll delta and the column stays attached
       to the mark all the way up, however fast the page moves — and when the
       logo leaves the screen the whole column leaves with it. */
    const sc = this.scroller || (this.scroller = (this.scope ? null
                : document.getElementById('main')));
    if(sc){
      const st = sc.scrollTop;
      if(this.lastScroll == null) this.lastScroll = st;
      const dy = st - this.lastScroll;
      this.lastScroll = st;
      if(dy) for(const p of this.ps) p.y -= dy;
    }

    const srcs = this.sources();
    /* WHICH MARKS ARE ACTUALLY ON THE SCREEN RIGHT NOW.""")

rep("""      if(p.y + rad < -20 || a <= 0.0025 || p.age > 26) continue;""",
"""      /* off the top, faded out, timed out, or carried a long way below the
         bottom edge by a scroll: none of those are worth another frame */
      if(p.y + rad < -20 || a <= 0.0025 || p.age > 26) continue;
      if(p.y - rad > this.h + 420) continue;""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
