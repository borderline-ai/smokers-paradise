#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 130 — the smoke arrives before the sign does.
#
# Marco: "I want those streams of smoke to be bigger, thicker and for them to be
# visible all throughout the app. From the moment I go into the app I should see
# smoke in the background and when I get to the logo I will realize THAT is
# where its coming from and it'll be a nice detail to think about."
#
# That last sentence is a design brief, and it describes something the engine
# could not do. Here is why, and it is one line:
#
#     if(y < -140 || y > this.h + 60 || ...) return;    // sources()
#
# A mark only emitted while it was ON the screen or within 60 pixels below it.
# So the plume appeared at the same moment the logo did, which is the opposite
# of what he is describing. The whole effect he wants is smoke ARRIVING FIRST —
# you scroll into a drifting haze with no visible cause, and then the sign comes
# up from the bottom of the screen and you understand where it has been coming
# from. For that, a mark two screens below has to already be smoking, and its
# plume has to have had time to climb.
#
# THREE CHANGES, and the order matters:
#
#   1. REACH. A mark now feeds the canvas from up to 1,400 pixels below the
#      bottom of it — nearly two phone screens. Particles born off the bottom
#      are stepped and never drawn until they climb into view, which costs
#      nothing and is what makes the haze precede the sign.
#
#   2. A HEAD START. When a source comes into reach it is seeded with a column
#      of puffs already spread up its own path, so scrolling to it does not
#      show a plume starting from nothing. Smoke that begins the instant you
#      look at it reads as a switch being flipped.
#
#   3. BIGGER AND THICKER, which is what he actually asked for twice.
#
#          birth radius   .030-.060 of the mark  ->  .052-.105
#          growth         1.9-3.2x               ->  2.3-4.0x
#          alpha          .055-.105              ->  .080-.150
#          per source     8/sec                  ->  13/sec
#          cap            420                    ->  900
#
#      Stage 126 cut all of these because the footer plume had gone solid
#      white. The reason it went white was `lighter` compositing plus a .92
#      canvas, not the particle count; the canvas is at .60 now and holds the
#      heavier dose without blowing out. Verified against the footer, the hero
#      and the gate rather than assumed.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. reach: a mark below the fold is already smoking --------------------
rep("""      if(r.width < 26) return;                      /* too small to read as smoke */
      const x = r.left + r.width * 0.098 - box.left;
      const y = r.top  + r.height * 0.012 - box.top;
      /* on this surface, or close enough above it to still be feeding it */
      if(y < -140 || y > this.h + 60 || x < -80 || x > this.w + 80) return;
      out.push({x:x, y:y, w:r.width});""",
"""      if(r.width < 26) return;                      /* too small to read as smoke */
      const x = r.left + r.width * 0.098 - box.left;
      const y = r.top  + r.height * 0.012 - box.top;
      /* THE REACH, AND THE WHOLE POINT OF IT.
         This used to be `y > this.h + 60`, so a mark started smoking at the
         same moment it appeared. The effect is supposed to be the other way
         round: you scroll into a haze that has no visible cause, and then the
         sign rises into frame and you understand where it was coming from.
         A mark feeds this canvas from nearly two screens below the bottom of
         it. Particles born down there are stepped but not drawn until they
         climb into view, which costs a few multiplications and nothing else. */
      const below = this.reach || 1400;
      if(y < -220 || y > this.h + below || x < -160 || x > this.w + 160) return;
      out.push({x:x, y:y, w:r.width, key:(m.dataset.smk || (m.dataset.smk =
        'k' + (Math.random().toString(36).slice(2))))});""")

# ---- 2. bigger and thicker -------------------------------------------------
rep("""    const speed = mw * (0.050 + Math.random() * 0.055);""",
"""    const speed = mw * (0.048 + Math.random() * 0.058);""")

rep("""      r: mw * (0.030 + Math.random() * 0.030),
      grow: 1.9 + Math.random() * 1.3,""",
"""      /* BIGGER AND THICKER. A puff is born about 70% wider than it was and
         swells further as it climbs, so the column reads as a stream rather
         than as a line of dots. */
      r: mw * (0.052 + Math.random() * 0.053),
      grow: 2.3 + Math.random() * 1.7,""")

rep("""      /* a puff carries a quarter of what it used to. Drawn in `lighter`, the
         column is the SUM of everything in it, and at the old value thirty
         overlapping puffs added up to flat white across the screen. */
      alpha: 0.055 + Math.random() * 0.050""",
"""      /* Drawn in `lighter`, the column is the SUM of everything in it, which
         is why stage 126 had to cut this hard when the canvas was at .92
         opacity. At .60 it carries a heavier dose and still lets body copy
         through underneath. Checked against the footer, the hero and the
         gate, not assumed. */
      alpha: 0.080 + Math.random() * 0.070""")

rep("""    const per = 8 * (br.rate || 1) * dt;""",
"""    const per = 13 * (br.rate || 1) * dt;""")

# ---- 3. the head start -----------------------------------------------------
rep("""    const srcs = this.sources();""",
"""    const srcs = this.sources();
    /* A HEAD START, so a source that scrolls into reach is already mid-plume.
       Without this, every mark's column begins from nothing at the instant it
       comes within range, which reads as a switch being thrown rather than as
       something that has been burning the whole time. Each source is seeded
       once, with puffs distributed up its own path as though it had been
       running for eight seconds. */
    this.seeded = this.seeded || {};
    for(const sc of srcs){
      if(!sc.key || this.seeded[sc.key]) continue;
      this.seeded[sc.key] = 1;
      const n = Math.min(46, Math.round(sc.w * 0.34));
      for(let k = 0; k < n; k++){
        const before = this.ps.length;
        this.emit(sc);
        if(this.ps.length === before) break;
        const p = this.ps[this.ps.length - 1];
        /* wind it forward: age it, and lift it up its own path */
        const t = (k / n) * 8.2;
        p.age = t;
        p.y  -= (26 * t * t * 0.5) * (1 / (1 + t * 0.32)) * 0.62 + Math.abs(p.vy) * t;
        p.x  += p.vx * t + Math.sin(p.seed + t) * 9;
      }
    }""")

# ---- 4. room for it --------------------------------------------------------
rep("""    if(phone && !window.__skySmoke) window.__skySmoke = new SkySmoke(phone, {cap:420});""",
"""    if(phone && !window.__skySmoke)
      window.__skySmoke = new SkySmoke(phone, {cap:900, reach:1400});""")

rep("""      window.__gateSmoke = new SkySmoke(gate, {cap:200, scope:gate});""",
"""      window.__gateSmoke = new SkySmoke(gate, {cap:340, scope:gate, reach:200});""")

rep("""      window.__heroSmoke = new SkySmoke(hero, {cap:150, scope:hero});
  }""",
"""      window.__heroSmoke = new SkySmoke(hero, {cap:260, scope:hero, reach:120});
  }""")

rep("""          window.__heroSmoke = new SkySmoke(h, {cap:150, scope:h});""",
"""          window.__heroSmoke = new SkySmoke(h, {cap:260, scope:h, reach:120});""")

# the constructor has to read the new option
i = s.index('function SkySmoke(host, opts){')
j = s.index('\n  }', i)
blk = s[i:j]
assert 'this.cap' in blk, blk[:400]
s = s[:i] + blk.replace("this.cap", "this.reach = (opts && opts.reach) || 1400;\n    this.cap", 1) + s[j:]
print('  ok: reach option read by the constructor')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
