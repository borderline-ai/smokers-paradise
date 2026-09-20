#!/usr/bin/env python3
# Stage 35 — page titles carry the weight of a page title.
#
# "DEALS" sat above "OFF-STAMP PODS, 2 FOR $10" in a lighter face at a smaller
# weight, so on a dark ground the title read as grey and the card headline under
# it read as white. The hierarchy was upside down, which is most of why the
# heading looked dark-on-purple in the first place.
#
# Same display face, same weight, same near-white as every other heading.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

CLOSE = """
/* One heading system, page titles included. A page title is the strongest
   thing on its screen or it is not a page title. */
.backbar h2,.shelfhead h2,#v-deals .backbar h2{
  font-family:var(--disp);font-weight:800;letter-spacing:-.03em;
  color:#FFF;text-shadow:none;-webkit-font-smoothing:antialiased}
"""
i = s.rindex('</style>')
s = s[:i] + CLOSE + s[i:]
io.open(P, 'w', encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
