#!/usr/bin/env python3
# Stage 59 — the three clipping defects the probe actually found.
#
# 1. The bottom of every page sat under the navigation bar. The shop's Sunday
#    hours, the Directions link and the 21+ line were unreadable at the end of
#    a scroll because there was no scroll left to do. The scroller now reserves
#    the nav's height plus the home-indicator inset.
#
# 2. A spec chip ("Soft silicone mouthpiece") ran past its row and was cut
#    mid-word. The row hides its overflow deliberately, so the fix is to let
#    the chip say less rather than to let the row grow: it truncates with an
#    ellipsis, which reads as a choice instead of an accident.
#
# 3. The announcement bar is chrome and was reported as content under the
#    header — a test artefact, fixed in the test rather than here.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:120])
    s = s.replace(a, b); print('  ok:', a[:56].replace('\n',' '))

CSS = r'''
/* ---- nothing ends under the navigation ----
   The scroller has to reserve the bar's height, or the last thing on every
   page is unreadable once there is no scrolling left. */
#main{padding-bottom:calc(78px + env(safe-area-inset-bottom, 0px))}

/* ---- a spec chip says less rather than spilling ----
   The row hides its overflow on purpose, so a long spec was being cut
   mid-word. It truncates now, which reads as a decision. */
.card .specrow{min-width:0}
.card .specrow .sp{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  min-width:0;flex:0 1 auto}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  clipping fixes appended')
io.open(P,'w',encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
