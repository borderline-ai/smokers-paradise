#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 129 — the one mark that was not smoking was the first one you see.
#
# Marco: "I want to see the smoke from all of these logos all the way at the
# top of the page AT THE ENTRANCE and ALL THROUGHOUT until you get to each
# logo. ALL OF THEM SHOULD BE SMOKING."
#
# Six marks on the home screen and five of them smoke. The sixth is the big one
# in the hero — the first thing anybody sees after the door, and the one he
# named first. It is emitting; you cannot see it. Why:
#
#     .skyhero{ position:relative; isolation:isolate }
#
# `isolation:isolate` makes the hero its own stacking context, so nothing
# outside it can ever paint between its layers. The one canvas that covers the
# whole phone sits at z-index 0 on #phone, which is outside; the hero's
# photograph and its scrim are at 1 and 2 INSIDE. So the smoke rising off the
# hero mark is drawn behind an opaque photograph of the shop.
#
# The gate had exactly this problem and stage 118 solved it exactly this way:
# a surface that cannot be seen through gets its own canvas inside it. The hero
# gets one at z-index 3 — above the film and the scrim, below .hero-in at 4, so
# the smoke passes in front of the photograph and behind the wordmark, which is
# where smoke off a cigarette in that wordmark would actually be.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""    /* The door is a full screen layer above the app, so a surface on the
       app's background cannot be seen through it. It gets its own. */
    const gate = document.getElementById('gate');
    if(gate && !window.__gateSmoke)
      window.__gateSmoke = new SkySmoke(gate, {cap:200, scope:gate});
  }""",
"""    /* The door is a full screen layer above the app, so a surface on the
       app's background cannot be seen through it. It gets its own. */
    const gate = document.getElementById('gate');
    if(gate && !window.__gateSmoke)
      window.__gateSmoke = new SkySmoke(gate, {cap:200, scope:gate});
    /* AND SO DOES THE HERO, for the same reason and a subtler one.
       .skyhero carries `isolation:isolate`, which makes it a stacking context
       of its own: the phone-wide canvas at z-index 0 on #phone is OUTSIDE it
       and can never paint between the hero's own layers, so smoke off the
       biggest mark in the app was being drawn behind an opaque photograph of
       the shop front. Its own canvas goes in at z-index 3 — over the film and
       the scrim, under .hero-in — so the plume crosses the photograph and
       passes behind the wordmark. */
    const hero = document.querySelector('.skyhero');
    if(hero && !window.__heroSmoke)
      window.__heroSmoke = new SkySmoke(hero, {cap:150, scope:hero});
  }""")

rep("""  window.__skySmoke = null; window.__gateSmoke = null;""",
"""  window.__skySmoke = null; window.__gateSmoke = null; window.__heroSmoke = null;""")

# the hero is rebuilt every time renderHome runs, so the canvas has to be
# re-attached when it is
rep("""    const sweep = () => { queued = false; try{ smokeUp() }catch(e){} };""",
"""    const sweep = () => { queued = false; try{ smokeUp() }catch(e){}
      /* renderHome replaces the hero wholesale, which takes its canvas with
         it. Re-attach rather than assume the one made at boot survived. */
      try{
        const h = document.querySelector('.skyhero');
        if(h && (!window.__heroSmoke || !h.contains(window.__heroSmoke.cv))){
          if(window.__heroSmoke) window.__heroSmoke.stop();
          window.__heroSmoke = new SkySmoke(h, {cap:150, scope:h});
        }
      }catch(e){}
    };""")

rep("""#gate > canvas.skysmoke{position:absolute;left:0;top:0;z-index:1;""",
"""/* over the hero photograph, under the wordmark standing on it */
.skyhero > canvas.skysmoke{position:absolute;left:0;top:0;z-index:3;
  pointer-events:none;opacity:.78}
#gate > canvas.skysmoke{position:absolute;left:0;top:0;z-index:1;""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
