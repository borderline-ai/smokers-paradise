#!/usr/bin/env python3
# Stage 34 — the deals page joins the system, and one dead route is fixed.
#
# Four deal cards, four different background colours (plum, olive, indigo,
# wine) and four different accent colours, stacked one under the other. That is
# the "unrelated card treatments" note at its most visible: the page where the
# money is reads as four unrelated designs.
#
# They now share the ground the banners use and the accent the rest of the app
# uses. The only thing that varies between deal cards is the offer.
#
# And the TRE House card still routed to a department that no longer exists.
# Moving Mushroom Chocolate into Exotic Snacks left "Shop the bars" pointing at
# cat 'shroom', which renders an empty shelf. It now opens Exotic Snacks with
# the Mushroom Chocolates filter already on, which is what the button says.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


# ---- one ground, one accent -----------------------------------------------
for old, new in [
    ("    theme:{bg:'#3A1030', ink:'#FFFFFF', accent:'#FFA51F'},",
     "    theme:{bg:DEAL_GROUND, ink:'#FFFFFF', accent:'#FF7BC8'},"),
    ("    theme:{bg:'#2A1A03', ink:'#FFFFFF', accent:'#FFC46B'},",
     "    theme:{bg:DEAL_GROUND, ink:'#FFFFFF', accent:'#FF7BC8'},"),
    ("    theme:{bg:'#1B1030', ink:'#FFFFFF', accent:'#B487FF'},",
     "    theme:{bg:DEAL_GROUND, ink:'#FFFFFF', accent:'#FF7BC8'},"),
    ("    theme:{bg:'#2A0619', ink:'#FFFFFF', accent:'#FF2FA8'},",
     "    theme:{bg:DEAL_GROUND, ink:'#FFFFFF', accent:'#FF7BC8'},"),
]:
    rep(old, new)

rep("""const DEALCARDS = [""",
"""/* One ground for every deal card, the same one the banners stand on. A deal is
   distinguished by its offer, not by being a different colour from the deal
   above it. */
const DEAL_GROUND = 'linear-gradient(118deg,#1B0A26 0%,#330F33 52%,#4A1038 100%)';

const DEALCARDS = [""")

# ---- the dead route --------------------------------------------------------
rep("""    dealType:'price', discountAmount:'$30', qualifyingCategory:'shroom',
    qualifyingBrandIds:[], ctaLabel:'Shop the bars', ctaTarget:{view:'cat',arg:'shroom'},""",
"""    dealType:'price', discountAmount:'$30', qualifyingCategory:'exotic',
    qualifyingBrandIds:[], ctaLabel:'Shop the bars',
    ctaTarget:{view:'cat', arg:'exotic', sub:'shroom'},""")

rep("""function goTarget(t){
  if(!t){go('home');return}
  if(t.view==='cat') go('cat', t.arg);
  else go(t.view||'home');
}""",
"""function goTarget(t){
  if(!t){go('home');return}
  if(t.view==='cat'){
    /* A target may name a group inside the shelf, so "Shop the bars" lands on
       the bars rather than on the whole department they live in. */
    if(typeof CATSTATE==='object' && CATSTATE) CATSTATE.sub = t.sub || '';
    go('cat', t.arg);
    if(t.sub && typeof CATSTATE==='object'){ CATSTATE.sub = t.sub; renderCat() }
    return;
  }
  go(t.view||'home');
}""")

# the home emphasis list still names the retired department
rep("""  emphasis:['disp','glass','shroom','eliq','hard','roll','gear','dab'],""",
    """  emphasis:['disp','glass','exotic','eliq','hard','roll','gear','dab'],""")

# ---- one secondary colour on the deal page --------------------------------
CLOSE = """
/* The deal page's secondary button took its text colour from each card's own
   accent, so four cards produced an orange, a gold, a violet and a magenta
   outline button. One secondary, like everywhere else. */
.dealrow .drgo,.dcard .dcta,#v-deals .drgo{color:var(--ink)}
.dealrow .drgo svg,.dcard .dcta svg{stroke:var(--go-ink)}
"""
i = s.rindex('</style>')
s = s[:i] + CLOSE + s[i:]
print('  secondary-colour rule appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
