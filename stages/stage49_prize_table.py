#!/usr/bin/env python3
# Stage 49 — the prize table is lit, not dark.
#
# Standing seven white-ground packshots on a plum field produced a collage of
# white rectangles: every product brought its own paper with it. The same
# answer as the campaigns — put the photographs on white and let the colour
# arrive at the edges — turns the same seven files into one table of prizes.
#
# The card is now two pieces: the photograph on a lit table, and the copy on
# the shop's plum underneath it. Scale is set so the glass reads as glass and
# the disposables read as small, which is the whole point of a prize picture.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


# ---- placement: the glass reads big, the disposables read small ----------
rep("""const PRIZE_ITEMS = [
  /* id, what it is, where it sits, how big, how far back */
  {id:'rx119', label:'Pulsar Snatched Beaker Bong',   x:'50%', y:'2%',  h:'92%', z:2, s:1.00},
  {id:'rx097', label:'GRAV Medium Beaker Base',       x:'14%', y:'16%', h:'70%', z:1, s:1.00},
  {id:'r039',  label:'Blazer Big Shot torch',         x:'88%', y:'30%', h:'52%', z:1, s:1.00},
  {id:'disp2', label:'Geek Bar Pulse X 25K',          x:'22%', y:'54%', h:'44%', z:4, s:1.00},
  {id:'rx089', label:'Lost Mary MT35000 Turbo',       x:'42%', y:'58%', h:'42%', z:5, s:1.00},
  {id:'rx065', label:'Off-Stamp X Cube 25K',          x:'61%', y:'56%', h:'40%', z:4, s:1.00},
  {id:'rx092', label:'RAZ DC25000',                   x:'79%', y:'59%', h:'38%', z:3, s:1.00}
];""",
"""const PRIZE_ITEMS = [
  /* id, what it is, where it stands on the table, how tall, how far back.
     The glass is tall and behind; the disposables are small and in front and
     overlap each other, which is what makes it read as one table rather than
     seven cut-outs in a row. */
  {id:'rx119', label:'Pulsar Snatched Beaker Bong',   x:'52%', y:'-2%', h:'86%', z:2},
  {id:'rx097', label:'GRAV Medium Beaker Base',       x:'19%', y:'12%', h:'64%', z:1},
  {id:'r039',  label:'Blazer Big Shot torch',         x:'85%', y:'26%', h:'50%', z:1},
  {id:'disp2', label:'Geek Bar Pulse X 25K',          x:'20%', y:'58%', h:'40%', z:4},
  {id:'rx089', label:'Lost Mary MT35000 Turbo',       x:'41%', y:'62%', h:'37%', z:6},
  {id:'rx065', label:'Off-Stamp X Cube 25K',          x:'61%', y:'60%', h:'38%', z:5},
  {id:'rx092', label:'RAZ DC25000',                   x:'80%', y:'63%', h:'35%', z:3}
];""")

CSS = r'''
/* ---- the prize table, lit ----
   Seven packshots printed on white, stood on a white table: no paper edges,
   no collage. The colour arrives at the corners, the copy sits on plum
   underneath, and each piece has its own contact shadow so the table has a
   floor. */
.prize .pz-stage{
  background:
    linear-gradient(196deg, #F4EFF7 0%, #FFFFFF 26%, #FFFFFF 74%, #F1EAF5 100%)}
.prize{aspect-ratio:4/3;border-radius:var(--r-card) var(--r-card) 0 0;
  overflow:hidden}
.prize.sm{aspect-ratio:1/1;border-radius:var(--r-card)}
.prize .pz-i img{filter:none}
.prize .pz-sh{bottom:-2%;height:11px;width:78%;
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(24,10,34,.34) 0%, rgba(24,10,34,.14) 54%, rgba(24,10,34,0) 100%)}
/* the mark signs the table in ink, because the neon version needs a dark
   ground and this one is lit */
.prize .pz-mark{display:none}
.prizecard .pz-sig{position:absolute;left:14px;top:12px;z-index:9;
  font-family:var(--mono);font-size:8.5px;letter-spacing:.24em;
  text-transform:uppercase;color:#2B1330;opacity:.42;pointer-events:none}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]

rep("""    ${compact?'':`<span class="pz-mark">${markImg('pzmark')}</span>`}""",
    """    ${compact?'':`<span class="pz-sig" aria-hidden="true">Smokers Paradise</span>`}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
