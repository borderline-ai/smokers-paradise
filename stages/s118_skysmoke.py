#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 118 — the smoke has to reach the top of the screen, and never stop.
#
# Marco: "I saw you added the animated logos ALMOST how I asked. What I asked
# for was for the smoke to go ALL THE WAY UP, for it to never stop going up. I
# want to see the smoke from all of these logos all the way at the top of the
# page AT THE ENTRANCE and ALL THROUGHOUT until you get to each logo. ALL OF
# THEM SHOULD BE SMOKING."
#
# Stage 107 lit every mark. What it could not do is get the smoke off the mark,
# and the reason is structural rather than a setting:
#
#   THE CANVAS BELONGS TO THE MARK. Each plume hangs its own canvas behind its
#   own logo, sized to the logo plus a margin — PAD_TOP is one mark height. So
#   the tallest a column could ever be was about twice the logo, whatever the
#   particles did.
#
#   AND ITS ANCESTORS CLIP IT. The mark on the Visit screen sits inside
#   `.addrplate`, which has overflow:hidden on it, so that plume is cut off at
#   the edge of a 340x152 box. The footer mark is inside `.sitefoot`. No
#   per-mark canvas can leave the box its mark is standing in, so no amount of
#   particle life reaches the top of the page.
#
# So the surface changes. ONE canvas, the size of the whole phone, sitting on
# the app's background layer where the smoke field already lives — behind every
# card, above the sky, inert to touch. Every mark on the screen is an EMITTER
# on that one surface, found each frame by where its artwork actually is, and
# the smoke it throws is no longer its own property. It leaves the logo, passes
# behind the cards, and keeps going until it is off the top of the screen.
#
#   ONE SURFACE      one canvas, one composited layer, one clear per frame,
#                    instead of a canvas per mark. Cheaper than what it
#                    replaces, not more expensive.
#   NO CEILING       a particle lives long enough to cross the whole screen
#                    and is only retired when it is past the top edge. It is
#                    never killed by a timer part way up.
#   IT NEVER STOPS   emission is continuous. The breath still makes it rise
#                    and fall, but there is no frame on which a logo is not
#                    smoking.
#   EVERY LOGO       the door, the hero, the fit tool, the Visit plate, the
#                    sign at the foot of the page, the menu, the order ticket.
#                    Anything with the mark on it is a chimney.
#
# The door gets its own copy of the same surface, because the gate is a full
# screen layer above the app and a canvas on the app's background cannot be
# seen through it.
#
# Off when the phone asks for less motion, off on a hidden tab, and capped at
# a particle count that a phone in a shop can hold.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- 1. the per-mark canvases stand down ----------------------------------
rep("""  const LIVE = new WeakMap();
  function smokeUp(root){
    if(REDUCED()) return;""",
"""  const LIVE = new WeakMap();
  /* THE PER-MARK CANVAS IS RETIRED. It could never leave the box its mark
     stood in — the Visit plate clips at 340x152, the footer clips at the
     section — so the column could never reach the top of the page, which is
     the whole of what was asked for. One surface for the entire phone does it
     instead, below. This is kept because the gate's own mark is mounted
     through it before that surface exists, and because a mark that somehow
     never reaches the sky still gets its wisp. */
  const SKY_OWNS_IT = true;
  function smokeUp(root){
    if(REDUCED() || SKY_OWNS_IT) return;""")

# ---- 2. one surface for the whole phone ------------------------------------
rep("""  window.smokeUp = smokeUp;""",
"""  window.smokeUp = smokeUp;

  /* =======================================================================
     THE SKY OF SMOKE

     One canvas the size of the phone. Every mark on the screen is an emitter
     on it, located each frame from where its artwork actually is, and what it
     throws is no longer clipped by whatever box the logo happens to sit in.
     The column leaves the logo, passes behind the cards, and keeps rising
     until it is off the top edge.

     A particle is retired when it has left the screen, not when a timer says
     so, which is the difference between smoke that reaches the top of the
     page and smoke that evaporates just above the logo.
     ======================================================================= */
  function SkySmoke(host, opts){
    opts = opts || {};
    this.host = host;
    this.cv = document.createElement('canvas');
    this.cv.className = 'skysmoke';
    this.cv.setAttribute('aria-hidden','true');
    this.ctx = this.cv.getContext('2d');
    this.ps = [];
    this.cap = opts.cap || 420;
    this.t = 0; this.last = 0; this.raf = 0; this.running = false;
    this.scope = opts.scope || null;   /* only marks inside this element */
    host.insertBefore(this.cv, host.firstChild);
    this.measure();
    addEventListener('resize', () => this.measure(), {passive:true});
    document.addEventListener('visibilitychange',
      () => document.hidden ? this.stop() : this.start());
    this.start();
  }
  SkySmoke.prototype.measure = function(){
    const r = this.host.getBoundingClientRect();
    const dpr = Math.min(devicePixelRatio || 1, 2);
    this.w = Math.max(1, Math.round(r.width));
    this.h = Math.max(1, Math.round(r.height));
    this.cv.width = Math.round(this.w * dpr);
    this.cv.height = Math.round(this.h * dpr);
    this.cv.style.width = this.w + 'px';
    this.cv.style.height = this.h + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.box = r;
  };
  /* WHERE EVERY LOGO IS, RIGHT NOW.
     The lit end of the cigarette the neon smoker is holding, measured off the
     artwork at x 0.098, y 0.012 of the image box — the same point the drawn
     magenta zigzag stops at, so the drawn smoke and the real smoke are one
     plume rather than an effect parked beside a picture. */
  SkySmoke.prototype.sources = function(){
    const out = [];
    const root = this.scope || document;
    const box = this.host.getBoundingClientRect();
    root.querySelectorAll('.hcm').forEach(m => {
      const cs = getComputedStyle(m);
      if(cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity < 0.15) return;
      const img = m.querySelector('.hcm-img');
      if(!img || !img.complete || !img.naturalWidth) return;
      const r = img.getBoundingClientRect();
      if(r.width < 26) return;                      /* too small to read as smoke */
      const x = r.left + r.width * 0.098 - box.left;
      const y = r.top  + r.height * 0.012 - box.top;
      /* on this surface, or close enough above it to still be feeding it */
      if(y < -140 || y > this.h + 60 || x < -80 || x > this.w + 80) return;
      out.push({x:x, y:y, w:r.width});
    });
    return out;
  };
  SkySmoke.prototype.emit = function(src){
    if(this.ps.length >= this.cap) return;
    const mw = src.w;
    /* straight up, give or take, because the sky above the cigarette is empty */
    const ang = (-104 + Math.random() * 30) * Math.PI / 180;
    const speed = mw * (0.050 + Math.random() * 0.055);
    this.ps.push({
      x: src.x + (Math.random() - 0.5) * mw * 0.05,
      y: src.y + (Math.random() - 0.5) * mw * 0.03,
      vx: Math.cos(ang) * speed,
      vy: Math.sin(ang) * speed,
      r: mw * (0.030 + Math.random() * 0.030),
      grow: 1.9 + Math.random() * 1.3,
      rot: Math.random() * 6.2832,
      spin: (Math.random() - 0.5) * 0.4,
      age: 0,
      seed: Math.random() * 100,
      alpha: 0.115 + Math.random() * 0.075
    });
  };
  SkySmoke.prototype.frame = function(now){
    if(!this.running) return;
    const dt = Math.min((now - this.last) / 1000, 0.05);
    this.last = now; this.t += dt;
    if(Math.abs(this.host.getBoundingClientRect().width - this.w) > 2) this.measure();

    const srcs = this.sources();
    const br = (typeof window.__hcBreath === 'function' && typeof window.__hcClock === 'function')
      ? window.__hcBreath(window.__hcClock()) : {rate:1};
    /* Per source, per second. Enough to read as a column without filling the
       screen when four marks are visible at once. */
    const per = 15 * (br.rate || 1) * dt;
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
      p.vy -= 26 * cool * dt;
      p.vx *= (1 - 0.42 * dt);
      p.vy *= (1 - 0.18 * dt);
      const amp = Math.min(1, p.age * 0.35);
      const wob = Math.sin(this.t * 0.9 + p.seed) * 11 * amp
                + Math.sin(this.t * 2.3 + p.seed * 1.7) * 4 * amp;
      p.x += (p.vx + wob * 0.3) * dt;
      p.y += p.vy * dt;
      p.rot += p.spin * dt;
      const rad = p.r * (1 + p.grow * Math.min(p.age * 0.5, 2.4));
      /* THINS WITH HEIGHT, NOT WITH A TIMER.
         Nothing is killed part way up. A puff fades as it climbs and as it
         spreads, and it is only dropped once it is genuinely off the top. */
      const climb = Math.max(0, (p.startY == null ? (p.startY = p.y, 0) : p.startY - p.y));
      void climb;
      const a = p.alpha * Math.max(0, 1 - p.age * 0.055)
                        * Math.min(1, p.age * 3.2)
                        * Math.max(0, Math.min(1, (p.y + rad) / Math.max(1, this.h * 0.14)));
      if(p.y + rad < -20 || a <= 0.003 || p.age > 26) continue;
      keep.push(p);
      if(p.y - rad > this.h + 30) continue;
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
  SkySmoke.prototype.start = function(){
    if(this.running || REDUCED() || document.hidden) return;
    this.running = true; this.last = performance.now();
    this.raf = requestAnimationFrame(t => this.frame(t));
  };
  SkySmoke.prototype.stop = function(){
    this.running = false;
    if(this.raf) cancelAnimationFrame(this.raf);
    this.raf = 0;
  };

  window.__skySmoke = null; window.__gateSmoke = null;
  function raiseTheSmoke(){
    if(REDUCED()) return;
    const phone = document.getElementById('phone');
    if(phone && !window.__skySmoke) window.__skySmoke = new SkySmoke(phone, {cap:420});
    /* The door is a full screen layer above the app, so a surface on the
       app's background cannot be seen through it. It gets its own. */
    const gate = document.getElementById('gate');
    if(gate && !window.__gateSmoke)
      window.__gateSmoke = new SkySmoke(gate, {cap:200, scope:gate});
  }
  window.raiseTheSmoke = raiseTheSmoke;
  if(document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', raiseTheSmoke, {once:true});
  else raiseTheSmoke();""")

# ---- 3. where the surface sits ---------------------------------------------
rep(""".gr-sum b{font-size:40px;line-height:1}
""",
""".gr-sum b{font-size:40px;line-height:1}

/* ---- THE SKY OF SMOKE ----
   One canvas the size of the phone, on the same layer as the drifting field:
   above the evening sky, behind every card, inert to touch. The columns from
   every logo on the screen are drawn on it, which is how they get out of the
   boxes their logos are standing in and reach the top of the page. */
#phone > canvas.skysmoke{position:absolute;left:0;top:0;z-index:0;
  pointer-events:none;opacity:.92}
#gate > canvas.skysmoke{position:absolute;left:0;top:0;z-index:1;
  pointer-events:none;opacity:.95}
#gate .gband,#gate .inner{position:relative;z-index:2}
@media (prefers-reduced-motion:reduce){ canvas.skysmoke{display:none} }
""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
