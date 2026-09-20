#!/usr/bin/env python3
# Stage 57 — the last of the internal language, and the stray collage goes.
#
# The standalone prize section on the home page is the "large miscellaneous
# collage": a table of products with no offer attached to it, sitting under the
# shelves for no reason. The raffle is now a proper advertisement on the deals
# page and in the deals rail, so the loose collage comes out rather than being
# rebuilt into a third version of the same thing.
#
# One line of provenance stays, in the account footer, because a demo that
# does not say it is a demo anywhere is worse than one that says it once.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:52].replace('\n',' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:120])
    s = s.replace(a, b); print('  ok:', a[:56].replace('\n',' '))

# the loose collage comes off the home page
rep("""  ${prizeSection()}

""", "")

# and the phrases that were only ever notes to ourselves
for a, b in [
    ("<span class=\"pz-eye\">Demo raffle</span>", "<span class=\"pz-eye\">Raffle</span>"),
    ("${secHead('Raffles','<button class=\"more\" data-go=\"deals\">See the deals</button>','Demo prize bundle')}",
     "${secHead('Raffles','<button class=\"more\" data-go=\"deals\">See the deals</button>','At the counter')}"),
    ("Demo prize bundle. The pictured items are examples, not\n            confirmed prizes, and the raffle is pending store confirmation. 21+ only.",
     "Pictured items are examples of what goes on the raffle table, not a\n            promised prize. 21+ only."),
    ("Demo build. Selection and prices are confirmed with the store.",
     "Selection and prices are confirmed with the store."),
    ("Demonstration build. Product selection, prices and availability are demo data and are con",
     "Product selection, prices and availability are confirmed with the store during onboarding. con"),
]:
    rep(a, b, must=False)

io.open(P,'w',encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
