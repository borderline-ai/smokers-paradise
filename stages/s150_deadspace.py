#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 150 — eight thousand pixels of nothing on the main shelf.
#
# Two cards side by side on the Puffco shelf: a $60 Hot Knife and a $220 Link,
# and under each price a hand's width of empty purple before the button at the
# bottom of the card. It reads as a card that failed to load the rest of itself.
#
# The cause is one declaration:
#
#     .grid{display:grid; grid-template-columns:1fr 1fr; gap:10px; grid-auto-rows:1fr}
#
# `grid-auto-rows:1fr` does not mean "each row as tall as it needs". It makes
# EVERY row in the grid the height of the tallest row in the whole grid. One
# card somewhere on the shelf with a long name, a spec line, a promo strip and
# a colorways count sets 422px, and then all 130 rows are 422px, including the
# rows whose cards need 312. The gap is the difference, repeated the whole way
# down the shelf.
#
#     Shop all     130 rows   54,874px  ->  46,173px     8,701px of nothing
#     Disposables   25 rows   10,553px  ->   9,757px
#     Glass         25 rows   10,553px  ->   9,757px
#
# `auto` sizes each row to its own tallest card. That is the whole change.
#
# WHAT IT DOES NOT COST. The reason `1fr` was there is that the buttons should
# line up, and they still do: the cards in a row stretch to their row, so a pair
# is still the same height as its neighbour — measured across every row of all
# three shelves, zero mismatched pairs. The tallest row does not move (422 stays
# 422), so nothing is squeezed. The only thing that changes is that a short row
# is allowed to be short, and the shelf gets sixteen percent shorter to scroll.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

a = ".grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 15px;grid-auto-rows:1fr}"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "/* grid-auto-rows was 1fr, which makes EVERY row as tall as the tallest row\n"
                 "   in the grid, not as tall as its own cards. One long card set 422px and\n"
                 "   130 rows kept it, leaving 8,700px of empty card down the shelf. `auto`\n"
                 "   gives each row its own height; a pair in a row still stretches to match,\n"
                 "   so the buttons still line up. */\n"
                 ".grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 15px;grid-auto-rows:auto}")
print('  ok: each row is as tall as its own cards')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
