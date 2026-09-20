#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 137 — the smoke cost 24 frames a second.
#
# I got the look right and then measured it, which is the right order but only
# if you actually do the second half:
#
#     before this session   29 fps    99 particles
#     after                  5 fps   328 particles
#
# On this container. On Marco's iPad it would be a slideshow, and he would not
# say "the frame rate is low" — he would say the app is broken, and he would be
# right.
#
# WHERE IT WENT, and it is not the particle count on its own. The canvas is
# sized at device pixels: 390 x 844 at a device ratio of 2 is 780 x 1688, about
# 1.3 million pixels. The haze puffs are a fifth of the screen wide at birth
# and grow, so one of them can cover 400 x 400 device pixels, and every one of
# them is a source-over blend of a radial-gradient bitmap. Three hundred of
# those is tens of millions of blended pixels per frame, every frame. Canvas
# smoke is a FILL RATE problem, not a particle-count problem, and I had been
# tuning the wrong number.
#
# THREE CHANGES, in order of how much they gave back:
#
#   1. THE SURFACE DRAWS AT HALF RESOLUTION and is scaled up by CSS. Smoke is
#      the one thing in this app with no edge and no detail to lose; at 0.55x
#      it is pixel for pixel indistinguishable and costs a third of the fill.
#      Everything else on screen stays at full device resolution — this is one
#      canvas, not the app.
#
#   2. FEWER, WHICH IS ALSO BETTER. Ambient 7.5/sec to 3.6, per source 13 to
#      9.5, cap 900 to 420. Each one carries more alpha to compensate, so the
#      screen looks the same and there is half as much of it to draw. The
#      haze puffs also stop growing as far, which is where the worst of the
#      fill was.
#
#   3. NOTHING IS DRAWN THAT CANNOT BE SEEN. A particle whose alpha has fallen
#      under a thousandth, or that is entirely off any edge, was still being
#      transformed and blitted. It is stepped and skipped now.
#
# Measured after, not assumed: it is the number at the bottom of this file's
# commit note either way.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. half resolution ----------------------------------------------------
rep("""    const dpr = Math.min(devicePixelRatio || 1, 2);""",
"""    /* HALF RESOLUTION, ON PURPOSE.
       This surface draws nothing with an edge. At device resolution the haze
       alone was tens of millions of blended pixels a frame and the app fell
       from 29 fps to 5; at 0.55 it is indistinguishable and costs a third as
       much. Only this canvas is scaled — everything else stays sharp. */
    const dpr = Math.min(devicePixelRatio || 1, 2) * 0.55;""")

# ---- 2. fewer, carrying more ----------------------------------------------
rep("""    const per = 13 * (br.rate || 1) * dt;""",
"""    const per = 9.5 * (br.rate || 1) * dt;""")
rep("""reach:1400, ambient:7.5});""", """reach:1400, ambient:3.6});""")
rep("""reach:260, ambient:3.0});""", """reach:260, ambient:1.9});""")

rep("""      r: w * (0.13 + Math.random() * 0.13),
      grow: 0.7 + Math.random() * 0.6,""",
"""      /* the growth was where the fill went: a puff starting a fifth of the
         screen wide and doubling covers 400x400 device pixels on its own */
      r: w * (0.13 + Math.random() * 0.11),
      grow: 0.34 + Math.random() * 0.3,""")

rep("""      alpha: 0.072 + Math.random() * 0.075,
      slow: 1""",
"""      alpha: 0.105 + Math.random() * 0.105,
      slow: 1""")

rep("""      alpha: (0.080 + Math.random() * 0.070) * Math.min(1, 165 / Math.max(40, mw))""",
"""      alpha: (0.105 + Math.random() * 0.090) * Math.min(1, 165 / Math.max(40, mw))""")

rep("""    if(phone && !window.__skySmoke)
      window.__skySmoke = new SkySmoke(phone, {cap:900,""",
"""    if(phone && !window.__skySmoke)
      window.__skySmoke = new SkySmoke(phone, {cap:420,""")
rep("""      window.__gateSmoke = new SkySmoke(gate, {cap:340,""",
"""      window.__gateSmoke = new SkySmoke(gate, {cap:190,""")
rep("""      window.__heroSmoke = new SkySmoke(hero, {cap:260,""",
"""      window.__heroSmoke = new SkySmoke(hero, {cap:150,""")
rep("""          window.__heroSmoke = new SkySmoke(h, {cap:260,""",
"""          window.__heroSmoke = new SkySmoke(h, {cap:150,""")

# ---- 3. never blit what cannot be seen -------------------------------------
rep("""      keep.push(p);
      if(p.y - rad > this.h + 30) continue;""",
"""      keep.push(p);
      /* stepped but not drawn: below the surface, above it, or off either
         side. A particle two screens down still has to be simulated so its
         column has climbed by the time it is scrolled to, but blitting a
         400 pixel sprite nobody can see is pure fill rate. */
      if(p.y - rad > this.h + 30 || p.y + rad < -30) continue;
      if(p.x - rad > this.w + 30 || p.x + rad < -30) continue;
      if(a < 0.0035) continue;""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
