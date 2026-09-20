#!/usr/bin/env python3
# Stage 41 — .tall's two cells were landing in two rows.
#
# The product markup comes before the copy, so auto-placement put the shot in
# row 1 and pushed the copy into a second, implicit row: the product got a
# 29px sliver at the top and the copy got everything else. Both cells are now
# placed explicitly, which is what you do the moment a grid has more than one
# item with a definite column.
#
# And the horizontal .tall gets its own field angle. The 163-degree ground was
# drawn for a layout where the product sits bottom-right; here it sits on the
# right, so the white has to run left-to-right or the packshot lands on the
# colour and shows its own edge again.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

CSS = """
/* both cells placed, because auto-placement was putting the product in a row
   of its own and pushing the copy underneath it */
.camp.tall .camp-copy{grid-row:1;grid-column:1}
.camp.tall .camp-shot{grid-row:1;grid-column:2;height:auto}
/* the field runs left to right in this layout, so the white is where the
   product stands */
.camp.tall .camp-field{background:linear-gradient(96deg,
  var(--f2) 0%, var(--f1) 34%, var(--f0) 68%, var(--f0) 100%)}
.camp.tall .camp-block{width:150%;height:190%;left:-64%;top:-44%}

@container (min-width:560px){
  /* stood up again: one column, product below, so the ground goes back to
     the diagonal */
  .camp.tall .camp-copy{grid-row:1;grid-column:1}
  .camp.tall .camp-shot{grid-row:2;grid-column:1}
  .camp.tall .camp-field{background:linear-gradient(163deg,
    var(--f2) 0%, var(--f1) 26%, var(--f0) 56%, var(--f0) 100%)}
  .camp.tall .camp-block{width:200%;height:80%;left:-52%;top:-34%}
}
"""
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]

# two lines of sub reads better than three under a headline this size
s = s.replace("sub:'Twenty-five thousand puffs a pod, and the flavours mix however you like.',",
              "sub:'Twenty-five thousand puffs a pod. Mix the flavours however you like.',")
io.open(P, 'w', encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
