#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 126 — the smoke was right, and far too much of it.
#
# Stage 118 did what Marco asked: "I want to see the smoke from all of these
# logos all the way at the top of the page AT THE ENTRANCE and ALL THROUGHOUT
# until you get to each logo, ALL OF THEM SHOULD BE SMOKING." It does. Every
# mark on every screen feeds one canvas that covers the whole phone, and
# nothing is killed part way up.
#
# Then I screenshotted it against the footer and it is a white column. Not a
# plume — a solid, opaque bar of white rising the full height of the screen,
# with the line "We read every one of these and we answer them ourselves"
# washed out behind it.
#
# WHY. The canvas draws in `lighter`, which ADDS. Fifteen particles per second
# per source, five sources on the home page, each at alpha .115 and each
# growing to three and a half times its birth size: by the time a puff is
# halfway up the screen there are thirty of them overlapping in the same
# column, and thirty times .115, added, is white. The physics was fine. The
# dosage was four times what a dark screen can take.
#
#   emitted   15/sec/source  ->  8
#   alpha     .115 to .190   ->  .055 to .105
#   canvas    .92 opacity    ->  .60
#
# AND IT IS TINTED NOW. Pure white smoke on a near-black UI is the one thing
# that reads as a rendering artefact rather than as part of the picture. The
# shop's sign is magenta and the smoke off the girl's cigarette in that sign is
# magenta. A trace of that colour in the plume is the difference between smoke
# that belongs to this brand and fog on a lens.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


rep("""      alpha: 0.115 + Math.random() * 0.075""",
"""      /* a puff carries a quarter of what it used to. Drawn in `lighter`, the
         column is the SUM of everything in it, and at the old value thirty
         overlapping puffs added up to flat white across the screen. */
      alpha: 0.055 + Math.random() * 0.050""")

rep("""    /* Per source, per second. Enough to read as a column without filling the
       screen when four marks are visible at once. */
    const per = 15 * (br.rate || 1) * dt;""",
"""    /* Per source, per second. Five marks are visible at once on the home
       page, and this number is multiplied by every one of them, so it is the
       single biggest lever on how heavy the screen looks. */
    const per = 8 * (br.rate || 1) * dt;""")

rep("""#phone > canvas.skysmoke{position:absolute;left:0;top:0;z-index:0;""",
"""/* the plume is a trace over the page, never a curtain in front of it */
#phone > canvas.skysmoke{position:absolute;left:0;top:0;z-index:0;""")

# the two opacities
i = s.index('#phone > canvas.skysmoke{')
j = s.index('}', i)
blk = s[i:j]
assert 'opacity:.92' in blk or 'opacity:0.92' in blk, blk
s = s[:i] + blk.replace('opacity:.92', 'opacity:.60').replace('opacity:0.92', 'opacity:.60') + s[j:]
print('  ok: phone canvas opacity .92 -> .60')

i = s.index('#gate > canvas.skysmoke{')
j = s.index('}', i)
blk = s[i:j]
print('  gate block:', blk[-40:])
for a, b in (('opacity:.92', 'opacity:.74'), ('opacity:0.92', 'opacity:.74')):
    if a in blk:
        s = s[:i] + blk.replace(a, b) + s[j:]
        print('  ok: gate canvas opacity -> .74')
        break

# ---- the tint --------------------------------------------------------------
i = s.index('function sprite(')
j = s.index('\n  }', i)
spr = s[i:j]
print('\n--- sprite() ---\n' + spr + '\n----------------')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
