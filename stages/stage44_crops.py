#!/usr/bin/env python3
# Stage 44 — the packshots are sized by max, not by height.
#
# Setting an explicit height and letting the width follow means a wide file
# (a chocolate bar) grows sideways until the cell clips it, and the clip lands
# in the middle of the product rather than at the panel's edge. Bounding both
# dimensions instead lets each file find its own size inside the space it is
# given: proportions are always preserved, a tall device fills the height, a
# wide bar fills the width, and the only thing that ever crops is the deliberate
# bleed past the frame.
#
# And the storefront tile crops lower. The sign is the brightest thing in that
# photograph and the headline was sitting on top of it.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

CSS = """
/* ---- packshots are bounded, not stretched ----
   Both dimensions capped, neither set: every manufacturer file finds its own
   size inside the space it is given and keeps its proportions, whatever shape
   the file happens to be. */
.camp-shot img{height:auto;width:auto}
.camp.lead .camp-lead{right:1%;bottom:-8%;max-height:118%;max-width:58%;height:auto}
.camp.lead .camp-back{right:38%;bottom:2%;max-height:76%;max-width:38%;height:auto}
.camp.tall .camp-lead{right:-3%;bottom:-5%;max-height:94%;max-width:112%;height:auto;
  left:auto;transform:none}
.camp.tall .camp-back{right:58%;bottom:4%;max-height:68%;max-width:62%;height:auto;
  left:auto;transform:none}
@container (min-width:560px){
  .camp.lead .camp-lead{right:2%;bottom:-6%;max-height:104%;max-width:64%}
  .camp.lead .camp-back{right:44%;bottom:6%;max-height:72%;max-width:42%}
  .camp.tall .camp-lead{left:50%;right:auto;transform:translateX(-46%);
    bottom:-7%;max-height:118%;max-width:76%}
  .camp.tall .camp-back{left:4%;right:auto;transform:none;bottom:2%;
    max-height:78%;max-width:44%}
}

/* the storefront crops below its sign, so the headline sits on the awning
   rather than on the brightest letters in the picture */
.bpair .camp.dark .camp-photo img{object-position:center 62%}
"""
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
io.open(P, 'w', encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
