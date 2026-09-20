#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 95 — the product page paints before it asks the internet for anything.
#
# Stage 93 stopped grid cards fetching a remote photograph of a flavour nobody
# had chosen. The product page still does it, and for the same reason: the page
# opens on the DEFAULT selection, option index 0 for every group, so on the
# first paint "the flavour" is just the first one in the list. Nobody picked it.
#
#     PICK = {id, sel:{}, q:1, editKey:null};
#     (p.opts||[]).forEach(g => PICK.sel[g.k] = 0);
#
# and the page then asks art() for it STRICTLY, which means: go to the network,
# and do not accept the photograph in this file as a substitute.
#
# That is the most-demoed screen in the app after the shelf. On a phone with one
# bar it opens to an empty frame and stays there until the request gives up, at
# which point hcImgFail puts in the embedded photograph that was available the
# whole time. Measured on the full button walk: 964 failed requests remain after
# stage 93, and they are almost all this.
#
# THE FIX IS THE DISTINCTION THE CODE WAS MISSING. `strict` should mean "the
# customer chose this variant", not "a variant is selected" — something is
# always selected. PICK gains a `touched` flag, set the moment somebody presses
# an option, and the four places that render the product's image ask strictly
# only when it is set.
#
# So: the page opens instantly on the photograph in the file, and the moment a
# customer taps Blue Razz the app goes and gets the Blue Razz photograph, which
# is the only moment that fetch was ever worth waiting for.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- 1. the flag -----------------------------------------------------------
rep("""  PICK={id, sel:{}, q:1, editKey:null};
  (p.opts||[]).forEach(g=>PICK.sel[g.k]=0);""",
"""  /* `touched` is the difference between "a variant is selected", which is
     always true because the page opens on option 0 of every group, and "the
     customer chose this variant", which is what justifies waiting on a remote
     photograph instead of showing the one in this file. */
  PICK={id, sel:{}, q:1, editKey:null, touched:false};
  (p.opts||[]).forEach(g=>PICK.sel[g.k]=0);""")

rep("""        const btn=e.target.closest('[data-oi]'); if(!btn)return;
        PICK.sel[grp.dataset.og]=+btn.dataset.oi; refresh();""",
"""        const btn=e.target.closest('[data-oi]'); if(!btn)return;
        PICK.sel[grp.dataset.og]=+btn.dataset.oi; PICK.touched=true; refresh();""")

# a bag row opens on a selection the customer made earlier: that IS their choice
rep("""    PICK.q=Math.max(1,Math.min(MAXQ,preset.q||1));
    PICK.editKey=preset.editKey||null;""",
"""    PICK.q=Math.max(1,Math.min(MAXQ,preset.q||1));
    PICK.editKey=preset.editKey||null;
    /* they chose this one already, in the bag */
    PICK.touched=true;""")

# ---- 2. the four render sites ----------------------------------------------
n = s.count("art(p, selKey(p,PICK.sel), true)")
assert n == 4, 'expected 4 render sites, found %d' % n
s = s.replace("art(p, selKey(p,PICK.sel), true)",
              "art(p, selKey(p,PICK.sel), !!PICK.touched)")
print('  ok: %d product-image render sites now ask strictly only once a '
      'customer has chosen' % n)

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
