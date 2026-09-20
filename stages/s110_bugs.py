#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 110 — three faults found by looking, not by a score.
#
# ONE. THE PHOTOGRAPH WAS EATING THE TAP.
#
# Stage 105 gave the eight lifestyle photographs `position:absolute; inset:0`
# so they fill the frame. On the product page that frame IS a button — tapping
# the picture opens the full size view — and an absolutely positioned child
# with no pointer rule takes the tap instead. Reported by the hit test as
# "Main product image, covered by img.scenephoto", which is the hit test doing
# exactly the job it was written for the night before. A picture is not a
# control; it never takes a tap.
#
# TWO. THE SPANISH LINE AT THE DOOR WAS PRINTED IN ENGLISH.
#
# The gate reads, in English, then in pink underneath:
#
#     Find everything for your smoke necessities, at the best prices.
#     Everything for your smoke necessities, at the best prices.
#
# The second line is supposed to be "Encuentra todo para tus necesidades de
# humo, a los mejores precios." It is written that way in the markup. The
# language walk translated it: it walks every text node on the screen and, in
# English mode, looks each one up in the Spanish-to-English table — and the
# `.es` spans ARE Spanish, so they matched and were turned into English. The
# first screen of the app, the one a shop owner in Nogales sees before anything
# else, was showing the same sentence twice in the same language.
#
# The `.es` spans are the one part of this app that is bilingual ON PURPOSE:
# the door greets everybody in both languages, whichever way the toggle is set.
# So the walk now steps over them. And when the whole app is switched to
# Spanish, the courtesy line stops being a courtesy and becomes a duplicate, so
# it is hidden — one line of CSS, no second code path.
#
# THREE. FLAVOURS FLICKERED THROUGH A DEAD NETWORK.
#
# Marco: "When you click throughout the flavors and products there is no
# consistency with backgrounds and cuts."
#
# Part of that was the cut-outs, which stages 103 to 105 dealt with. The rest
# is this: when a customer PICKS a flavour, the app prefers that flavour's own
# photograph, which lives on the manufacturer's server. In the shop there is no
# wifi. So the picture request hangs, fails, and the failure handler quietly
# puts the embedded photograph back. Every flavour tap was: right picture,
# blank, right picture. It reads as the app breaking and reassembling itself.
#
# Nothing detected that the network was gone. Each URL was retired one at a
# time, on its own failure, so the same flicker happened on every new flavour
# of every product for the whole session. Three failures is now enough to
# conclude the obvious, and from that point the app stops asking the network
# for pictures at all and goes straight to the ones it is carrying. One repaint
# when it flips, so the screen already on the glass settles too.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. a picture is not a control ----------------------------------------
rep(""".scenephoto{position:absolute!important;inset:0!important;""",
"""/* An absolutely positioned child of a frame that IS a button takes the tap
   that belongs to the button. The product page's picture opens the full size
   view; the photograph is scenery. */
.scenephoto{pointer-events:none;position:absolute!important;inset:0!important;""")

# ---- 2. the door is bilingual on purpose -----------------------------------
rep("""    const raw = n.nodeValue;
    const key = raw.replace(/\\s+/g,' ').trim();""",
"""    /* THE .es SPANS ARE NOT COPY TO BE TRANSLATED, THEY ARE THE TRANSLATION.
       The door, the pickup note and the under-21 button carry a Spanish line
       under the English one, always, whichever way the toggle is set. They are
       written in Spanish in the markup, so in English mode this walk found them
       in the Spanish-to-English table and turned them into English — and the
       first screen of the app showed the same sentence twice in one language.
       Step over them. */
    if(p.closest && p.closest('.es')) continue;
    const raw = n.nodeValue;
    const key = raw.replace(/\\s+/g,' ').trim();""")

rep(""".es{display:inline-block;color:var(--go-ink);opacity:.92;font-style:normal}""",
"""/* The courtesy line under the English. When the whole app is in Spanish it is
   no longer a courtesy, it is the same sentence twice, so it goes. */
.es{display:inline-block;color:var(--go-ink);opacity:.92;font-style:normal}
html[lang="es"] .es{display:none}""")

# ---- 3. stop asking a network that is not there ----------------------------
rep("""function remoteFor(p, flavorName){
  const k = p.brand+'|'+p.name+'|'+(flavorName||'*');
  return (typeof REMOTE!=='undefined' && REMOTE[k]) ? REMOTE[k] : null;
}""",
"""/* ---- THE NETWORK IS NOT THERE ----
   This app is shown in a shop in Nogales with no wifi. Every photograph it
   needs is carried inside the file; the remote records are a preference, not a
   dependency — a flavour's own photograph on the manufacturer's server is more
   exact than the embedded photograph of the model.

   With no network that preference costs a customer a flicker on every single
   flavour tap: the exact picture is requested, the request dies, the failure
   handler puts the embedded picture back. Right picture, blank, right picture,
   every time, all session, because each URL was only retired on its own
   failure and the next flavour had a URL of its own.

   Three failures is enough to conclude the obvious. After that this returns
   nothing and every picture in the app comes from the file. */
let NET_FAILS = 0, NET_DOWN = false;
function netFailed(){
  if(NET_DOWN) return;
  if(++NET_FAILS < 3) return;
  NET_DOWN = true;
  /* the screen already on the glass settles too, once */
  try{ if(typeof repaintAfterMedia === 'function') repaintAfterMedia();
       else if(typeof paint === 'function') paint(); }catch(e){}
}
function remoteFor(p, flavorName){
  if(NET_DOWN) return null;
  const k = p.brand+'|'+p.name+'|'+(flavorName||'*');
  return (typeof REMOTE!=='undefined' && REMOTE[k]) ? REMOTE[k] : null;
}""")

rep("""function hcImgFail(el, id, vk){
  try{""",
"""function hcImgFail(el, id, vk){
  try{
    netFailed();""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
