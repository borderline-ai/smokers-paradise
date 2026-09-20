#!/usr/bin/env python3
# Stage 43 — the carousel clip goes back on the frame, not on the track.
#
# The track is what moves: `heroTo` translates #heroVp. Putting `overflow:
# hidden` on the track means the clip translates with it, so after the first
# slide the visible window is empty and every later campaign is clipped away.
# Slide one looked perfect and slides two, three and four were blank plum.
#
# The clip belongs on the frame the track slides behind, which is .promoc.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


rep(""".promoc{border-radius:var(--r-card);overflow:visible;box-shadow:none;
  margin:0 var(--sp-edge);position:relative;padding-bottom:22px}
.promoc .vp{border-radius:var(--r-card);overflow:hidden;align-items:stretch}""",
""".promoc{border-radius:var(--r-card);box-shadow:none;
  margin:0 var(--sp-edge);position:relative;padding-bottom:22px;
  /* the clip lives on the frame, never on the track: the track translates,
     and a clip that translates with it takes the next slide with it */
  overflow:hidden}
.promoc .vp{border-radius:var(--r-card);overflow:visible;align-items:stretch}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
