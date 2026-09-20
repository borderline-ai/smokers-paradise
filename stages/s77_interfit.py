#!/usr/bin/env python3
# Stage 77 — the product stands inside the dialog instead of being sliced by it.
#
# A deal card is drawn so the lead product overhangs the bottom of its own
# artwork row by 6% and stands 126% of its height: on the home screen that
# overhang falls into the card's own rounded base and reads as a product set
# down on the card rather than pasted into it.
#
# The dialog reuses that card, and there the card's bottom edge IS the dialog's
# bottom edge. The overhang has nothing to overhang into, so both devices were
# cut straight through, half a centimetre from the bottom of the poster, which
# is the first thing anybody sees when they open this app.
#
# Scoped to the dialog, so the home card keeps its overhang.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


rep(".interad .ad{min-height:300px;border-radius:var(--r-card)}",
    ".interad .ad{min-height:330px;border-radius:var(--r-card)}\n"
    "/* The deal card lets its lead product hang below the artwork row, because\n"
    "   on the home screen it falls into the card's own base. In the dialog that\n"
    "   edge is the dialog's edge and the overhang is simply amputated, so here\n"
    "   the products stand on the floor instead of over it. */\n"
    "/* Written against the id, because every layout sets its own bottom and\n"
    "   max-height on .ad.l-<layout> .ad-p and a class selector here only ties\n"
    "   with them: the tie goes to whichever is written later, which was them. */\n"
    "#inter .ad .ad-p.lead{bottom:6%;max-height:100%;max-width:46%}\n"
    "#inter .ad .ad-p.back{bottom:10%;max-height:84%;max-width:36%}\n"
    "#inter .ad .ad-art{min-height:158px}")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
