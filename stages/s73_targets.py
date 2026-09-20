#!/usr/bin/env python3
# Stage 73 — a button that names a brand lands on that brand.
#
# Five advertisements in this app name a product or a brand in their headline
# and in their own button, and all five put the customer on the same
# undifferentiated shelf:
#
#   "Browse pods"      Off-Stamp Crystal Cube  -> 50 vapes, 19 brands
#   "See the flavors"  Lost Mary new flavors   -> the same 50
#   "Browse new vapes" Geek Bar Pulse X        -> the same 50
#   "Shop Off-Stamp"   the 2 for $10 offer     -> the same 50
#   "Shop Puffco"      the Puffco offer        -> all 20 dab items
#
# So the ad does its job, the customer presses the button, and then has to go
# find the thing themselves. That is worse than no button: the app raised an
# expectation and dropped it one tap later.
#
# The shelf already knows how to open pre-filtered. BRANDQ exists for exactly
# this and renderCat reads it on the way in; nothing but goTarget had ever set
# it. Two lines there, and a `brand` on the five targets that name one.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


# ---- 1. the router can carry a brand ---------------------------------------
rep("""function goTarget(t){
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
}""",
"""function goTarget(t){
  if(!t){go('home');return}
  if(t.view==='cat'){
    /* A target may name a group inside the shelf, so "Shop the bars" lands on
       the bars rather than on the whole department they live in. */
    if(typeof CATSTATE==='object' && CATSTATE) CATSTATE.sub = t.sub || '';
    /* And it may name a brand. An advertisement that says Off-Stamp on it, and
       whose button says Shop Off-Stamp, cannot open fifty vapes from nineteen
       brands and leave the customer to go and find the two it was about. The
       shelf already opens pre-filtered: BRANDQ is what renderCat reads on the
       way in, and until now nothing ever set it from a button. */
    if(typeof BRANDQ !== 'undefined') BRANDQ = t.brand || '';
    go('cat', t.arg);
    if(t.sub && typeof CATSTATE==='object'){ CATSTATE.sub = t.sub; renderCat() }
    return;
  }
  go(t.view||'home');
}""")

# ---- 2. the five that name a brand -----------------------------------------
for label, old, new in [
    ('p-offstamp  Browse pods',
     "cta:'Browse pods', target:{view:'cat', arg:'disp'}",
     "cta:'Browse pods', target:{view:'cat', arg:'disp', brand:'Off-Stamp'}"),
    ('p-lostmary  See the flavors',
     "cta:'See the flavors', target:{view:'cat', arg:'disp'}",
     "cta:'See the flavors', target:{view:'cat', arg:'disp', brand:'Lost Mary'}"),
    ('p-geek      Browse new vapes',
     "cta:'Browse new vapes', target:{view:'cat', arg:'disp'}",
     "cta:'Browse new vapes', target:{view:'cat', arg:'disp', brand:'Geek Bar'}"),
    ('d-offstamp  Shop Off-Stamp',
     "ctaLabel:'Shop Off-Stamp', ctaTarget:{view:'cat',arg:'disp'}",
     "ctaLabel:'Shop Off-Stamp', ctaTarget:{view:'cat',arg:'disp',brand:'Off-Stamp'}"),
    ('d-puffco    Shop Puffco',
     "ctaLabel:'Shop Puffco', ctaTarget:{view:'cat',arg:'dab'},",
     "ctaLabel:'Shop Puffco', ctaTarget:{view:'cat',arg:'dab',brand:'Puffco'},"),
]:
    if s.count(old) == 1:
        s = s.replace(old, new)
        print('  ok: %s' % label)
    else:
        print('  !! %s  (%d matches, left alone)' % (label, s.count(old)))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
