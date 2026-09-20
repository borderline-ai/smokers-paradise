#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 163 — the sliced Geek Bars were still in the banner.
#
# Marco: "the banner of the geek bars has a bug in it, the geek bars are
# slightly cropped."
#
# He is right, and this one is mine twice over. Stage 142 cut three Geek Bar
# photographs at a "seam" that does not exist and sliced the left edge off each
# device. Stage 147 reverted that — in CUT_PHOTOS. It never looked at
# HERO_DEVICE, a second five-entry store that the CAMPAIGN BANNERS read from,
# and two of its five entries are the damaged cuts:
#
#     HERO_DEVICE disp2   Pulse X 25K     118x240   left edge sliced
#     HERO_DEVICE disp3   Pulse X2 50K     75x178   left edge sliced
#
# Blown up, the black Pulse X has a flat vertical cut down its left side with
# the G of GEEK BAR chopped off, and the blue X2 is cut the same way. On the
# front page of the app, four times the size it is on a card. Reverting one
# store and not the other is exactly the kind of half-fix that keeps a defect
# alive, and it lived for six days.
#
# ======================================================================
# WHY THE FIX IS DIFFERENT PRODUCTS, NOT A BETTER CUT
# ======================================================================
# Because those two devices cannot be cut out, and I checked it three ways
# before giving up on them. The maker photographs the Pulse X, the X2 and the
# 15K standing against their own carton. The column ink profile never falls to
# zero between box and device:
#
#     disp2   lowest ink anywhere in the middle half   183 px of 296
#     disp3                                            142 px of 220
#     rx086                                            168 px of 261
#
# and the gap is not unkeyed white either — of 12,437 opaque pixels in the band
# between the box and the device on the Pulse X, SIX are near-white. They
# overlap. There is nothing to separate.
#
# The shop stocks five Geek Bars. Three are that carton photograph. Two are
# clean single-device cut-outs:
#
#     rx087   WATT 23000   $16.99   10 flavors
#     rx2go   2GO 50K      $24.99   13 flavors
#
# So the banner shows those two, and the headline now says what is in the
# picture instead of naming a product that is not. Both figures in the new
# sentence come from the catalogue.
#
# THE THIRD DEVICE HE ASKED FOR. "I also think it has the exact space to add
# one more geek bar, maybe another color." There is space and he is right that
# it wants a third. There is no third clean Geek Bar device in this catalogue,
# and inventing one by re-cutting a carton photograph is what caused this
# defect in the first place, so the banner stands at two. ONE PHOTOGRAPH of the
# Pulse X on their own counter is the whole fix, and it would also put the best
# selling Geek Bar back on the front page where it belongs.
#
# And the two damaged files are deleted outright, so there is no third store
# somewhere holding a sliced Geek Bar waiting to surface on another screen.
import io
import json

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- 1. the damaged cuts are deleted, not left lying around ----------------
k = 'const HERO_DEVICE = '
i = s.index(k)
j = s.index('};\n', i) + 1
hd = json.loads(s[i + len(k):j])
gone = [pid for pid in ('disp2', 'disp3') if pid in hd]
for pid in gone:
    del hd[pid]
s = s[:i] + k + json.dumps(hd, separators=(',', ':')) + s[j:]
print('  ok: removed the sliced banner cuts %s, %d left' % (gone, len(hd)))

# ---- 2. the banner shows the two Geek Bars that are whole -------------------
rep("""  { id:'p-geek', kind:'lead', field:'violet',
    kicker:'New in',
    headline:'Pulse X.\\nTwenty-five thousand.',
    sub:'Dual mesh, a screen, and a charge that outlasts the weekend.',
    offer:'', offer2:'',
    cta:'Browse new vapes', target:{view:'cat', arg:'disp', brand:'Geek Bar'},
    disclaimer:'21+ only. Valid ID at pickup.',
    mark:false,
    shot:{ hero:()=>heroCut('Geek Bar','Pulse X 25K')||heroShot('Geek Bar','Pulse X 25K'), heroAlt:'Geek Bar Pulse X 25K',
           back:()=>heroCut('Geek Bar','Pulse X2 50K')||heroShot('Geek Bar','Pulse X2 50K'), backAlt:'Geek Bar Pulse X2 50K' },
    active:true, startDate:null, endDate:null },""",
"""  /* THE TWO GEEK BARS THAT ARE WHOLE.
     This slide used to lead with the Pulse X and the X2, whose banner cuts
     were sliced down the left edge by stage 142 and never reverted in
     HERO_DEVICE. Neither of those devices can be cut out of the maker's
     photograph at all — it stands them against their carton with no gap — so
     the slide leads with the two Geek Bars the shop has as clean single
     device photographs, and the headline names what is actually pictured.
     Both numbers below are the catalogue's. */
  { id:'p-geek', kind:'lead', field:'violet',
    kicker:'New in',
    headline:'Geek Bar,\\ntwo new ones.',
    sub:'The WATT 23K in ten flavors, the 2GO 50K in thirteen.',
    offer:'', offer2:'',
    cta:'Browse new vapes', target:{view:'cat', arg:'disp', brand:'Geek Bar'},
    disclaimer:'21+ only. Valid ID at pickup.',
    mark:false,
    shot:{ hero:()=>heroCut('Geek Bar','2GO 50K')||heroShot('Geek Bar','2GO 50K'), heroAlt:'Geek Bar 2GO 50K',
           back:()=>heroCut('Geek Bar','WATT 23000')||heroShot('Geek Bar','WATT 23000'), backAlt:'Geek Bar WATT 23000' },
    active:true, startDate:null, endDate:null },""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
