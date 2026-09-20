#!/usr/bin/env python3
# Stage 21 — their real mark, and smoke coming off the cigarette.
import io, base64, os

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))

# ---------------------------------------------------------------- 1. the mark
# Cut from the shop's own Happy Holidays post: the badge and the white page it
# was printed on are flood filled away, so what is left is exactly the ink —
# the script wordmark, the SMOKE SHOP ring, and the magenta neon smoker. Soft
# alpha, so it sits on the plum without a cut edge around it.
raw = open('/tmp/t76.webp', 'rb').read()
uri = 'data:image/webp;base64,' + base64.b64encode(raw).decode('ascii')
i = s.index('const MARK_CLEAN_URL = "')
j = s.index('";', i)
old_len = j - i
s = s[:i] + 'const MARK_CLEAN_URL = "' + uri + s[j:]
print('  mark replaced: %d -> %d chars (%d KB of webp)' % (old_len, len(uri), len(raw)//1024))

# ---------------------------------------------------------------- 2. source
rep("""  const NOSTRIL = [{x:0.3947, y:0.8473, dir:-1}, {x:0.6000, y:0.8442, dir:1}];""",
"""  /* One source, and it is the obvious one: the lit end of the cigarette the
     neon smoker is holding. The mark already draws the first few inches of
     that smoke as a magenta zigzag; this picks it up exactly where the drawn
     line stops, at the top of the curl, so the two read as one plume rather
     than as artwork with an effect stuck next to it.
     Measured off the cut artwork: the topmost magenta run sits at x 0.098,
     y 0.012, and it leans left. */
  const NOSTRIL = [{x:0.098, y:0.012, dir:-1}];""")

rep("""  const CLOUD = [{x:0.2054, y:0.7533, dir:-1}, {x:0.7818, y:0.7525, dir:1}];""",
"""  /* The two drifting clusters belonged to the previous shop's artwork. This
     mark has none, so there is nothing here and the cigarette does all of it. */
  const CLOUD = [];""")

# smoke off a cigarette goes up and keeps going, so it needs sky
rep("""  const PAD_X = 0.42, PAD_TOP = 0.50, PAD_BOTTOM = 0.10;""",
    """  const PAD_X = 0.46, PAD_TOP = 1.00, PAD_BOTTOM = 0.08;""")

# ---------------------------------------------------------------- 3. emission
# A nostril threw a short horizontal blast to clear a muzzle. A cigarette does
# the opposite: it releases slowly, straight up, and the wisp lives long enough
# to spread and thin out on the way.
rep("""      const jitter = this.mw * (nose ? 0.010 : 0.05);
      const life   = nose ? 3.0 + Math.random() * 1.7 : 2.6 + Math.random() * 2.2;
      const speed  = this.mw * (nose ? (0.16 + Math.random() * 0.13)
                                     : (0.018 + Math.random() * 0.028));""",
"""      const jitter = this.mw * (nose ? 0.014 : 0.05);
      const life   = nose ? 3.6 + Math.random() * 2.6 : 2.6 + Math.random() * 2.2;
      const speed  = this.mw * (nose ? (0.055 + Math.random() * 0.070)
                                     : (0.018 + Math.random() * 0.028));""")

rep("""      const ang    = (nose ? (-16 + Math.random() * 26)
                           : (-58 + Math.random() * 64)) * Math.PI / 180;""",
"""      /* Straight up, give or take twenty degrees. Nothing is in the way: the
         cigarette is at the top left corner of the mark and the sky above it
         is empty, which is why the source is there and not at the mouth. */
      const ang    = (nose ? (-110 + Math.random() * 42)
                           : (-58 + Math.random() * 64)) * Math.PI / 180;""")

rep("""        r:  this.mw * (nose ? (0.026 + Math.random() * 0.026)
                            : (0.030 + Math.random() * 0.030)),
        grow: nose ? 1.7 + Math.random() * 1.1 : 1.5 + Math.random() * 1.1,""",
"""        r:  this.mw * (nose ? (0.019 + Math.random() * 0.021)
                            : (0.030 + Math.random() * 0.030)),
        grow: nose ? 2.1 + Math.random() * 1.4 : 1.5 + Math.random() * 1.1,""")

rep("""        alpha: (nose ? 0.17 + Math.random() * 0.10
                     : 0.11 + Math.random() * 0.07) * (src.w == null ? 1 : src.w),""",
"""        alpha: (nose ? 0.125 + Math.random() * 0.085
                     : 0.11 + Math.random() * 0.07) * (src.w == null ? 1 : src.w),""")

# buoyancy from the first frame, and only a light lean instead of a sideways shove
rep("""        const lift = p.nose ? Math.min(1, k / 0.20) : 1;""",
    """        const lift = p.nose ? Math.min(1, k / 0.05) : 1;""")

rep("""        const clear = p.nose ? (1 - Math.min(1, k / 0.45)) : 0;
        p.x += (p.vx + wx * turb * 0.55
                + p.dir * this.mw * (0.030 + 0.085 * clear)) * dt;""",
"""        const clear = p.nose ? (1 - Math.min(1, k / 0.45)) : 0;
        p.x += (p.vx + wx * turb * 0.55
                + p.dir * this.mw * (0.016 + 0.026 * clear)) * dt;""")

# one source instead of four, so it has to work harder to fill the same air
rep("""      this.acc += dt * (13 * wander * b.rate);""",
    """      this.acc += dt * (17 * wander * b.rate);""")

# ---------------------------------------------------------------- 4. restart it
rep("""  function smokeUp(){ /* the drawn smoke plume belonged to the old mark */ }""",
"""  function smokeUp(root){
    if(REDUCED()) return;
    /* Every mark on the screen, with one exception: a mark inside a clipped
       plate. The header badge is a small window with overflow hidden, so a
       plume there would be sliced off at the edge of the box instead of
       drifting out of it. */
    (root || document).querySelectorAll('.hcm').forEach(el => {
      if(LIVE.has(el)) return;
      if(el.closest('.plate')) return;
      const img = el.querySelector('.hcm-img');
      if(!img) return;
      const r = img.getBoundingClientRect();
      if(r.width && r.width < 46) return;      /* too small to read as smoke */
      const go = () => { if(!LIVE.has(el)) LIVE.set(el, new Plume(el)) };
      img.complete && img.naturalWidth ? go() : img.addEventListener('load', go, {once:true});
    });
  }""")

# ---------------------------------------------------------------- 5. the glow
# The mark is neon now, so the halo behind it is the sign's own bloom rather
# than a soft grey shadow.
rep(""".hcm-glow{box-shadow:0 0 34px 6px rgba(255,47,168,.22)}""",
    """.hcm-glow{box-shadow:0 0 44px 10px rgba(255,47,168,.26)}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
