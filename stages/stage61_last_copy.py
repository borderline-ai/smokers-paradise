#!/usr/bin/env python3
# Stage 61 — the last four places internal language reached the storefront.
#
# A footer that says "Demonstration build", a Puffco band eyebrow that says
# "Featured in the demo", and an account note that says "Demo build by
# BorderLine AI". None of it means anything to a customer.
#
# One honest line of provenance stays, in the account panel, because a build
# that never says what it is anywhere is worse than one that says it once. It
# now reads as a sentence rather than a label.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56]); return
    assert n == count, 'count %d for: %s' % (n, a[:110])
    s = s.replace(a, b); print('  ok:', a[:56].replace('\n',' '))

rep("Demonstration build. Product selection, prices and availability are confirmed with the store during onboarding.",
    "Product selection, prices and availability are confirmed with Smoker&rsquo;s Paradise during onboarding.")
rep("<div class=\"eye\">Featured in the demo</div>", "<div class=\"eye\">Puffco at Smokers Paradise</div>")
rep("Demo build by BorderLine AI. Every product shown is a real, listed product with the manufacturer&rsquo;s o",
    "Built for Smokers Paradise by BorderLine AI. Every product shown is a real, listed product with the manufacturer&rsquo;s o", must=False)

io.open(P,'w',encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
