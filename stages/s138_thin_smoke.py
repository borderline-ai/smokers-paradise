#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 138 — it was a light, not smoke. Taking the whole thing back.
#
# Marco, and every sentence of this is a correct fault report:
#
#   "Every few seconds you have like a big white light move all the way up the
#    screen. I think you tried to make thicker smoke and just half assed it
#    with some light."
#   "There should be much more smoke in the backround. Its so incosistent. I
#    see it as soon as I go in but dont see it again for another 10 seconds."
#   "At the bottom under the reviews you have this white light instead of the
#    thin smoke."
#   "Go back to the smoke you had at the very beginning and animate that smoke
#    to CONSTANTLY be going up FROM BOTH LOGOS."
#   "When I scroll down and don't see the logo I should not see the smoke
#    coming from that logo no more."
#
# HE IS DESCRIBING THE AMBIENT HAZE AND HE IS RIGHT ABOUT ALL OF IT. I built it
# in stage 131 to fill the four thousand pixels of this page that have no logo
# on them. A haze puff is born a quarter of the screen wide, carries alpha up
# to .21, and takes twenty seconds to cross. Three point six of those a second
# is not a haze — at that size it is one object at a time, and one big soft
# bright object crossing a dark screen every few seconds is not smoke, it is a
# LIGHT. "Inconsistent" is exactly right too: the gap between two of them IS
# about ten seconds. I built a lava lamp and called it atmosphere.
#
# And the last sentence overturns the premise of stage 130. I gave every mark
# 1,400 pixels of reach so its plume would arrive before the sign did, and a
# head start so it was mid-column when it got there. He does not want that. He
# wants smoke off a logo he can see, and nothing off a logo he cannot.
#
# SO THE HAZE IS GONE, ENTIRELY — the emitter, the branch in the physics, the
# branch in the alpha, the option. Not turned down: removed. Turning it down
# is how it comes back.
#
# WHAT REPLACES IT IS WHAT HE ASKED FOR: the thin smoke, going constantly, off
# the logos, and only off the logos that are on the screen.
#
#     born        .052-.105 of the mark wide   ->  .022-.044
#     rate        9.5 a second per mark        ->  22
#     reach       1,400px below the fold       ->  90
#     head start  46 puffs, aged 8 seconds     ->  none
#     haze        3.6 a second, a quarter wide ->  none
#
# Five times as many puffs, each a quarter of the area, off a mark that has to
# be in front of you. A column made of many small things is a stream; a column
# made of few big things is a lamp. That is the whole difference between the
# two builds and it is the thing I got wrong.
#
# AND THE LAST SENTENCE IS ENFORCED, not just implied by the reach. Every puff
# remembers which mark threw it. When that mark leaves the screen its smoke
# fades out in about half a second rather than carrying on up a screen that no
# longer has a source on it.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- the engine, rewritten ------------------------------------------------
i = s.index('  SkySmoke.prototype.haze = function(){')
j = s.index('  SkySmoke.prototype.start = function(){')
old = s[i:j]
assert 'haze' in old and 'p.slow' in old, 'engine block not found'

new = r"""  SkySmoke.prototype.emit = function(src){
    if(this.ps.length >= this.cap) return;
    const mw = src.w;
    /* Straight up, narrowly. A cigarette end throws a thin column before it
       spreads; the wander comes later, out of the turbulence bands below. */
    const ang = (-95 + Math.random() * 16) * Math.PI / 180;
    const speed = mw * (0.090 + Math.random() * 0.060);
    this.ps.push({
      src: src.key,
      x: src.x + (Math.random() - 0.5) * mw * 0.035,
      y: src.y + (Math.random() - 0.5) * mw * 0.02,
      vx: Math.cos(ang) * speed,
      vy: Math.sin(ang) * speed,
      /* SMALL, AND THERE ARE FIVE TIMES AS MANY.
         A column made of many small puffs is a stream. A column made of few
         big ones is a lamp, which is what the last build looked like and what
         Marco called "a big white light". A quarter of the area, at five
         times the rate, for the same amount of smoke and none of the blobs. */
      r: mw * (0.022 + Math.random() * 0.022),
      grow: 2.6 + Math.random() * 1.8,
      rot: Math.random() * 6.2832,
      spin: (Math.random() - 0.5) * 0.5,
      age: 0,
      off: 0,
      seed: Math.random() * 100,
      /* Scaled by the size of the mark it comes off: every dimension of a puff
         is a fraction of the mark's width, so the 300px sign at the door would
         otherwise throw puffs of nine times the area of the footer's at the
         same weight, and `lighter` compositing would take the door to white. */
      alpha: (0.070 + Math.random() * 0.055) * Math.min(1, 150 / Math.max(40, mw))
    });
  };
  SkySmoke.prototype.frame = function(now){
    if(!this.running) return;
    const dt = Math.min((now - this.last) / 1000, 0.05);
    this.last = now; this.t += dt;
    if(Math.abs(this.host.getBoundingClientRect().width - this.w) > 2) this.measure();

    const srcs = this.sources();
    /* WHICH MARKS ARE ACTUALLY ON THE SCREEN RIGHT NOW.
       "When I scroll down and don't see the logo I should not see the smoke
       coming from that logo no more." The reach in sources() stops a mark
       that has left from emitting anything new; this stops what it already
       threw from carrying on up a screen with no source on it. */
    const live = Object.create(null);
    for(const sc of srcs) if(sc.key) live[sc.key] = 1;

    const br = (typeof window.__hcBreath === 'function' && typeof window.__hcClock === 'function')
      ? window.__hcBreath(window.__hcClock()) : {rate:1};
    /* Per mark, per second. High, because each puff is now small: the column
       has to be continuous, which is a question of spacing, not of size. */
    const per = 22 * (br.rate || 1) * dt;
    this.acc = (this.acc || 0) + per;
    while(this.acc >= 1){
      this.acc -= 1;
      for(const s of srcs) this.emit(s);
    }

    const g = this.ctx, sp = sprite();
    g.clearRect(0, 0, this.w, this.h);
    g.globalCompositeOperation = 'lighter';
    const keep = [];
    for(const p of this.ps){
      p.age += dt;
      /* buoyancy that eases as the puff cools, drag, and two turbulence bands
         whose amplitude grows with age, so a young puff is tight and an old
         one wanders */
      const cool = 1 / (1 + p.age * 0.32);
      p.vy -= 30 * cool * dt;
      p.vx *= (1 - 0.42 * dt);
      p.vy *= (1 - 0.18 * dt);
      const amp = Math.min(1, p.age * 0.35);
      const wob = Math.sin(this.t * 0.9 + p.seed) * 11 * amp
                + Math.sin(this.t * 2.3 + p.seed * 1.7) * 4 * amp;
      p.x += (p.vx + wob * 0.3) * dt;
      p.y += p.vy * dt;
      p.rot += p.spin * dt;
      const rad = p.r * (1 + p.grow * Math.min(p.age * 0.5, 2.4));
      /* the mark that threw this has left the screen: take it with it, over
         about half a second, rather than cutting it off mid-air */
      if(p.src && !live[p.src]) p.off += dt;
      const gone = p.off ? Math.max(0, 1 - p.off * 2.1) : 1;
      /* THINS WITH HEIGHT, NOT WITH A TIMER.
         Nothing is killed part way up. A puff fades as it climbs and as it
         spreads, and it is only dropped once it is genuinely off the top. */
      const a = p.alpha * gone
                * Math.max(0, 1 - p.age * 0.055)
                * Math.min(1, p.age * 3.2)
                * Math.max(0, Math.min(1, (p.y + rad) / Math.max(1, this.h * 0.14)));
      if(p.y + rad < -20 || a <= 0.0025 || p.age > 26) continue;
      keep.push(p);
      /* stepped but not drawn: off any edge, or too faint to register */
      if(p.y - rad > this.h + 30 || p.y + rad < -30) continue;
      if(p.x - rad > this.w + 30 || p.x + rad < -30) continue;
      if(a < 0.0035) continue;
      g.save();
      g.translate(p.x, p.y);
      g.rotate(p.rot);
      g.globalAlpha = a;
      g.drawImage(sp, -rad, -rad, rad * 2, rad * 2);
      g.restore();
    }
    this.ps = keep;
    g.globalCompositeOperation = 'source-over';
    this.raf = requestAnimationFrame(t => this.frame(t));
  };
"""
s = s[:i] + new + s[j:]
print('  ok: engine rewritten, %d -> %d chars in the block' % (len(old), len(new)))

# ---- the reach comes back to the screen ------------------------------------
rep("""      /* THE REACH, AND THE WHOLE POINT OF IT.
         This used to be `y > this.h + 60`, so a mark started smoking at the
         same moment it appeared. The effect is supposed to be the other way
         round: you scroll into a haze that has no visible cause, and then the
         sign rises into frame and you understand where it was coming from.
         A mark feeds this canvas from nearly two screens below the bottom of
         it. Particles born down there are stepped but not drawn until they
         climb into view, which costs a few multiplications and nothing else. */
      const below = this.reach || 1400;
      if(y < -220 || y > this.h + below || x < -160 || x > this.w + 160) return;""",
"""      /* ONLY OFF A LOGO YOU CAN SEE.
         Stage 130 gave every mark 1,400 pixels of reach so its plume would
         arrive before the sign did. Marco: "When I scroll down and don't see
         the logo I should not see the smoke coming from that logo no more."
         So: on the screen, or just under the bottom edge so a mark rising into
         view is already alight rather than switching on. */
      const below = this.reach || 90;
      if(y < -220 || y > this.h + below || x < -160 || x > this.w + 160) return;""")

rep("""    this.reach = (opts && opts.reach) || 1400;
    this.ambient = (opts && opts.ambient) || 0;   /* haze puffs per second */""",
"""    this.reach = (opts && opts.reach) || 90;""")

# ---- the mounts ------------------------------------------------------------
rep("""      window.__skySmoke = new SkySmoke(phone, {cap:300, reach:1400, ambient:3.6});""",
"""      window.__skySmoke = new SkySmoke(phone, {cap:340, reach:90});""")
rep("""      window.__gateSmoke = new SkySmoke(gate, {cap:190, scope:gate, reach:260, ambient:1.9});""",
"""      window.__gateSmoke = new SkySmoke(gate, {cap:200, scope:gate, reach:60});""")
rep("""      window.__heroSmoke = new SkySmoke(hero, {cap:150, scope:hero, reach:120});""",
"""      window.__heroSmoke = new SkySmoke(hero, {cap:200, scope:hero, reach:60});""")
rep("""          window.__heroSmoke = new SkySmoke(h, {cap:150, scope:h, reach:120});""",
"""          window.__heroSmoke = new SkySmoke(h, {cap:200, scope:h, reach:60});""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
