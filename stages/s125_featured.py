#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 125 — the two carton shots that cannot be separated, and where they sit.
#
# Stage 124 took the retail carton out of fifteen photographs. Three would not
# come apart, because in those three the device stands IN FRONT OF the carton
# and the two overlap: there is no seam to open. I tried an erosion split, a
# straight vertical cut and two rounds of grabcut, and every result either left
# a grey tab of cardboard hanging off the device or tore a piece out of it.
#
#   rx076  Foger Switch Pro 30K   device in front of the carton
#   rx086  Geek Bar Pulse 15K     carton in front of the device
#   rx073  Tyson MIA 50K          the maker published the carton alone
#
# So: they keep the maker's photograph, because it is the maker's photograph
# and an invented one is not an option. What changes is where they stand. Both
# of the separable ones were marked featured, which is why the Geek Bar Pulse —
# the card Marco has now pointed at three times — was the second thing on the
# Disposable Vapes shelf, next to a Foger that is also a carton shot. Two
# cardboard boxes, side by side, first screen.
#
# Featured is a position, not a fact about the product. These three are still
# on the shelf, still searchable, still complete; they are simply no longer the
# first thing a customer is shown, because the picture we have of them is not
# our best picture. The moment Smokers Paradise photographs their own Pulse on
# the counter, it goes back.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

for pid, why in [('rx076', 'Foger Switch Pro 30K'), ('rx086', 'Geek Bar Pulse 15K')]:
    i = s.index('{"id":"%s"' % pid)
    j = s.index('},{', i) + 1
    rec = s[i:j]
    assert rec.count('"featured":true') == 1, pid
    s = s[:i] + rec.replace('"featured":true', '"featured":false') + s[j:]
    print('  ok: %s no longer leads the shelf (%s)' % (pid, why))

# and say so where the catalogue explains itself, so it is not quietly undone
k = 'const REAL_PRODUCTS='
i = s.index(k)
head = s.rindex('/* ====', 0, i)
note = """
   NOT FEATURED, AND WHY: rx073, rx076 and rx086. The maker's photograph for
   each of those three is a wholesaler's slide with the retail carton in it,
   and in those three the carton and the device overlap, so the carton cannot
   be separated out the way it was for the other fifteen. They stay on the
   shelf with the picture their maker published. They do not lead it.
"""
s = s[:i] + '/*' + note + '*/\n' + s[i:]
print('  ok: the reason is written where the catalogue is defined')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
