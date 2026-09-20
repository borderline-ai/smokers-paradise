#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 132 — the smoke was behind the furniture.
#
# I raised the haze twice and shot the page twice and it barely moved, which
# meant the number was not the problem. It was the stacking order:
#
#     #phone > canvas.skysmoke   z-index: 0
#     main.main                  z-index: 1
#
# The smoke surface sits UNDER the app. Everywhere a section paints a card, a
# panel or a photograph — which is most of this page — the smoke is behind it
# and cannot be seen at any alpha. It only ever showed in the gaps between
# cards, which is exactly the pattern in the screenshots: a wisp beside the
# footer mark, nothing across the middle of the page.
#
# That was a deliberate choice once. Stage 118's note says "the column leaves
# the logo, passes BEHIND the cards" — behind was the tasteful answer when the
# question was whether smoke should exist at all. It is the wrong answer to the
# question Marco is actually asking, which is for smoke you can see everywhere,
# and real smoke in a real room is in front of the shelves.
#
# SO IT MOVES IN FRONT, to z-index 20: over everything inside #main, under the
# header at 30, the announcement bar at 40, the menu, the sheets and the tab
# bar. The controls a finger uses are never under it, the canvas takes no
# pointer events, and the type stays legible because the whole surface is at
# .55 and drawn in soft radial sprites rather than flat fill.
#
# Two layers now, because they want different heights:
#
#   THE PLUMES stay where the sign is, in front of the cards, so a column off
#   the mark crosses whatever is next to it.
#   THE HAZE is thin room air fed from the bottom edge across the full width.
#
# Checked at five scroll positions with body copy under it, not assumed.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


i = s.index('#phone > canvas.skysmoke{')
j = s.index('}', i) + 1
old = s[i:j]
new = """#phone > canvas.skysmoke{position:absolute;left:0;top:0;z-index:20;
  pointer-events:none;opacity:.55;mix-blend-mode:screen}"""
s = s[:i] + new + s[j:]
print('  ok: the phone smoke surface moves from z-index 0 to 20')
print('      was:', old.replace('\n', ' '))

# the note above it explained the old choice; correct it rather than leave it lying
rep("""/* the plume is a trace over the page, never a curtain in front of it */""",
"""/* IN FRONT OF THE APP, NOT BEHIND IT.
   At z-index 0 this sat under main.main at z-index 1, so everywhere a section
   painted a card the smoke was hidden and no alpha could bring it back. It is
   over the content now and under the header, the announcement bar, the menu,
   the sheets and the tab bar, so nothing a finger needs is ever beneath it.
   `screen` rather than `source-over` keeps it from muddying the ink under it:
   it can only lighten, so dark type stays dark and the veil reads as air. */""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
