#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 131 — smoke in the room, not only over the sign.
#
# Stage 130 made the plumes bigger and gave every mark nearly two screens of
# reach. I then shot the whole home page and looked at it, and the middle of it
# is empty. Of course it is: there are four marks on this page, at roughly 300,
# 1,500, 8,700 and 10,250 pixels. Between 2,500 and 7,000 there is no mark at
# all, so there is nothing to emit, so there is no smoke. Reach cannot fix a
# four-thousand-pixel gap, and the answer is NOT to scatter logos down the page
# so the engine has something to burn.
#
# Marco asked for two different things in one sentence and I only built one:
#
#     "from the moment I go into the app I should see smoke in the backround"
#     "and when I get to the logo I will realize THAT is where its coming from"
#
# The second is a PLUME — tight, bright, obviously issuing from the cigarette
# in the artwork. The first is a ROOM — a thin haze that is simply always
# there, with no source you can point at. A shop that has been open since eight
# in the morning has both, and they do not look alike.
#
# THE HAZE. Broad, slow, and about a third the weight of a plume particle, fed
# from below the bottom edge across the full width so it is always drifting up
# through whatever is on screen. Wide enough that you never see an individual
# puff: the smallest is a fifth of the screen across, against a plume puff at
# about a twentieth. Slow enough to cross a screen in roughly twenty seconds.
#
# The important part is the RATIO. The haze has to sit far enough under the
# plumes that when the sign finally comes up from the bottom of the screen the
# plume still reads as the source and the haze reads as what it has been doing
# all morning. Haze alpha tops out at .055 where a plume particle starts at
# .080 and there are six times as many of them in a column.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- the haze emitter ------------------------------------------------------
rep("""  SkySmoke.prototype.emit = function(src){""",
"""  /* THE ROOM.
     Not a plume and deliberately not shaped like one. A plume puff is born at
     about a twentieth of the screen across and climbs fast off a fixed point;
     a haze puff is born at a fifth of the screen across, anywhere along the
     bottom edge, and takes about twenty seconds to cross. You are never meant
     to see one of these as an object — only to notice that the air is not
     clean. That is what keeps the sign readable as the source when it finally
     scrolls up into frame. */
  SkySmoke.prototype.haze = function(){
    if(this.ps.length >= this.cap) return;
    const w = this.w, h = this.h;
    this.ps.push({
      x: Math.random() * (w * 1.3) - w * 0.15,
      y: h + 30 + Math.random() * 60,
      vx: (Math.random() - 0.5) * 5,
      vy: -(5 + Math.random() * 7),
      r: w * (0.10 + Math.random() * 0.11),
      grow: 0.55 + Math.random() * 0.5,
      rot: Math.random() * 6.2832,
      spin: (Math.random() - 0.5) * 0.08,
      age: 0,
      seed: Math.random() * 100,
      alpha: 0.026 + Math.random() * 0.029,
      slow: 1                       /* marks it as room air, not a column */
    });
  };
  SkySmoke.prototype.emit = function(src){""")

# ---- the haze rises differently from a plume -------------------------------
rep("""      const cool = 1 / (1 + p.age * 0.32);
      p.vy -= 26 * cool * dt;
      p.vx *= (1 - 0.42 * dt);
      p.vy *= (1 - 0.18 * dt);
      const amp = Math.min(1, p.age * 0.35);
      const wob = Math.sin(this.t * 0.9 + p.seed) * 11 * amp
                + Math.sin(this.t * 2.3 + p.seed * 1.7) * 4 * amp;""",
"""      const cool = 1 / (1 + p.age * 0.32);
      /* room air is not buoyant the way a fresh puff is: it drifts, it does
         not climb, so it gets a twentieth of the lift and twice the wander */
      p.vy -= (p.slow ? 1.3 : 26) * cool * dt;
      p.vx *= (1 - (p.slow ? 0.10 : 0.42) * dt);
      p.vy *= (1 - (p.slow ? 0.05 : 0.18) * dt);
      const amp = Math.min(1, p.age * 0.35);
      const wob = p.slow
        ? (Math.sin(this.t * 0.16 + p.seed) * 26 + Math.sin(this.t * 0.37 + p.seed * 1.3) * 12)
        : (Math.sin(this.t * 0.9 + p.seed) * 11 * amp
          + Math.sin(this.t * 2.3 + p.seed * 1.7) * 4 * amp);""")

# a haze puff must not be aged out the way a plume puff is
rep("""      const a = p.alpha * Math.max(0, 1 - p.age * 0.055)
                        * Math.min(1, p.age * 3.2)
                        * Math.max(0, Math.min(1, (p.y + rad) / Math.max(1, this.h * 0.14)));
      if(p.y + rad < -20 || a <= 0.003 || p.age > 26) continue;""",
"""      const a = p.slow
        ? p.alpha * Math.min(1, p.age * 0.5) * Math.max(0, 1 - p.age * 0.016)
        : p.alpha * Math.max(0, 1 - p.age * 0.055)
                  * Math.min(1, p.age * 3.2)
                  * Math.max(0, Math.min(1, (p.y + rad) / Math.max(1, this.h * 0.14)));
      if(p.y + rad < -20 || a <= 0.0025 || p.age > (p.slow ? 62 : 26)) continue;""")

# ---- and it runs every frame, on the surface that covers the app -----------
rep("""    const per = 13 * (br.rate || 1) * dt;""",
"""    const per = 13 * (br.rate || 1) * dt;
    /* THE ROOM RUNS WHETHER OR NOT A MARK IS ON SCREEN, which is the whole
       reason it exists: between the campaign mark at 1,500 and the address
       plate at 8,700 this page has no emitter at all, and that is most of the
       page. Fed from the bottom edge, so it is always drifting up through
       whatever is in front of you. */
    if(this.ambient){
      this.hacc = (this.hacc || 0) + this.ambient * dt;
      while(this.hacc >= 1){ this.hacc -= 1; this.haze() }
    }""")

rep("""      window.__skySmoke = new SkySmoke(phone, {cap:900, reach:1400});""",
"""      window.__skySmoke = new SkySmoke(phone, {cap:900, reach:1400, ambient:1.5});""")
rep("""      window.__gateSmoke = new SkySmoke(gate, {cap:340, scope:gate, reach:200});""",
"""      window.__gateSmoke = new SkySmoke(gate, {cap:340, scope:gate, reach:200, ambient:1.1});""")

# the constructor reads it
rep("""    this.reach = (opts && opts.reach) || 1400;""",
"""    this.reach = (opts && opts.reach) || 1400;
    this.ambient = (opts && opts.ambient) || 0;   /* haze puffs per second */""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
