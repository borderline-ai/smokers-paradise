#!/usr/bin/env python3
# Stage 60 — three corrections from looking at the six finished ads.
#
# TRE HOUSE went to a photographic ground, and the photograph's own top third
# is pale, so the kicker vanished into it. Its cut-out keyed cleanly, so it
# goes back to standing on the cacao gradient — which is the richer answer
# anyway, because then the chocolate colour is ours and not the photo's.
#
# PUFFCO's two devices sat on the bottom edge and were cropped by it. They
# stand higher now, with room under them for the shadow.
#
# THE CAMPAIGNS still used the full packshot with its studio sweep, held
# together by a light field. They use the cut-outs now, so the product carries
# a real shadow instead of melting into a white corner.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:120])
    s = s.replace(a, b); print('  ok:', a[:56].replace('\n',' '))

rep("  { id:'d-tre', concept:'tre', layout:'photo',",
    "  { id:'d-tre', concept:'tre', layout:'stack',")

# the campaigns take the cut-out
rep("""const heroShot = (brand, modelLike, flavor) => {""",
"""/* The campaigns want the cut-out: a product with its ground removed can be
   lit and can cast a shadow, where a packshot can only sit in its own box. */
const heroCut = (brand, modelLike) => {
  const id = (typeof pidFor==='function') ? pidFor(brand, modelLike) : '';
  return id ? cutout(id) : '';
};

const heroShot = (brand, modelLike, flavor) => {""")

for a, b in [
    ("hero:()=>heroShot('Off-Stamp','X Cube 25K')", "hero:()=>heroCut('Off-Stamp','X Cube 25K')||heroShot('Off-Stamp','X Cube 25K')"),
    ("back:()=>heroShot('Off-Stamp','SW9000')", "back:()=>heroCut('Off-Stamp','SW9000')||heroShot('Off-Stamp','SW9000')"),
    ("hero:()=>heroShot('Lost Mary','MT35000 Turbo')", "hero:()=>heroCut('Lost Mary','MT35000 Turbo')||heroShot('Lost Mary','MT35000 Turbo')"),
    ("back:()=>heroShot('Lost Mary','MO20000 Pro')", "back:()=>heroCut('Lost Mary','MO20000 Pro')||heroShot('Lost Mary','MO20000 Pro')"),
    ("hero:()=>heroShot('Geek Bar','Pulse X 25K')", "hero:()=>heroCut('Geek Bar','Pulse X 25K')||heroShot('Geek Bar','Pulse X 25K')"),
    ("back:()=>heroShot('Geek Bar','Pulse X2 50K')", "back:()=>heroCut('Geek Bar','Pulse X2 50K')||heroShot('Geek Bar','Pulse X2 50K')"),
    ("hero:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter')",
     "hero:()=>heroCut('TRE House','Mushroom Chocolate, Peanut Butter')||heroShot('TRE House','Mushroom Chocolate, Peanut Butter')"),
    ("back:()=>heroShot('TRE House','Mushroom Chocolate, Fruity Cereal')",
     "back:()=>heroCut('TRE House','Mushroom Chocolate, Fruity Cereal')||heroShot('TRE House','Mushroom Chocolate, Fruity Cereal')"),
]:
    rep(a, b)

CSS = r'''
/* a cut-out on the campaign's field: no studio sweep to hide, so the product
   gets a real shadow and the white plate under the product cell comes off */
.camp.light .camp-shot{background:none;overflow:visible}
.camp .camp-lead,.camp .camp-back{
  filter:drop-shadow(0 16px 18px rgba(24,10,34,.30)) drop-shadow(0 2px 3px rgba(24,10,34,.22))}
.camp.lead .camp-field,.camp.tall .camp-field{
  background:linear-gradient(163deg, var(--f2) 0%, var(--f1) 34%, var(--f0) 82%, var(--f0) 100%)}

/* Puffco stands clear of the bottom edge instead of being cropped by it */
.ad.c-puffco .ad-p.lead{bottom:6%;max-height:104%}
.ad.c-puffco .ad-p.back{bottom:12%;max-height:74%}
.ad.l-reverse .ad-floor{bottom:12%}
'''
i = s.rindex('</style>'); s = s[:i] + CSS + s[i:]
print('  polish appended')
io.open(P,'w',encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
