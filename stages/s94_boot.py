#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 94 — the app stops asking the internet for permission to sell things.
#
# WHAT IT WAS DOING. Two hundred and seventy-one network requests fire before
# the customer has even pressed "Enter the shop": bootMediaCheck probes one
# remote photograph per product, ten at a time, on a nine second budget, to
# find out which third-party hosts are alive. Anything that fails is written
# into DEAD_IMAGES, cached in localStorage FOR SEVEN DAYS, and then fed to the
# publish gate, which drops that flavour from the option list and, if it was
# the last one, unpublishes the product and rebuilds the catalogue.
#
# That was a reasonable design when a dead host meant an empty frame. It is the
# wrong design now, for two reasons.
#
#   1. Every browsing surface in this app draws from the copy embedded in this
#      file. A host being unreachable no longer means there is no picture. It
#      means nothing at all.
#
#   2. Read it as what happens on Saturday. Marco is standing at the counter on
#      North Grand on a phone with one bar. The app opens and spends up to nine
#      seconds pulling at 271 files that are already in the file it just
#      loaded. Some fraction fail. Not enough to trip the "the whole channel is
#      blocked" threshold of 60%, just enough to look like real breakage — so
#      the gate quietly removes those flavours, rebuilds the catalogue and
#      repaints, and the shelf gets shorter while the owner is looking at it.
#      Then the result is cached for a week, so it stays shorter on good Wi-Fi
#      back in Tucson, with nothing on screen to explain why.
#
# A demo that shows a different catalogue depending on the signal in the room
# is not a demo. The menu is the same 259 products on every phone, every time,
# online or off.
#
# WHAT CHANGES: the probe no longer runs on boot. The function stays, and the
# staff media-check screen still runs it on demand, which is where a question
# like "which of our hotlinked photographs have gone stale" actually belongs.
# And a remote file that fails while somebody is browsing is no longer recorded
# as dead when the product's photograph is in this file, because in that case
# the photograph is not dead, only the host is, and the customer already got
# the picture.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""/* Run the check behind the age gate so it is invisible, then repaint once. */
(function bootMediaCheck(){
  const started=Date.now();
  verifyMedia((checked, failed)=>{
    if(failed){
      rebuildCatalog(); reconcileCart(); buildNav();
      if(VIEW==='home') renderHome(); else if(VIEW==='cat') renderCat();
    }
    if(window.console && checked)
      console.info(`Smokers Paradise media check: ${checked} product images checked in `
        +`${Date.now()-started}ms, ${failed} unavailable, ${PRODUCTS.length} products on the menu.`);
  }, 9000);
})();""",
"""/* THE BOOT PROBE IS OFF, DELIBERATELY.
   It used to open the app by pulling at one remote photograph per product,
   271 of them, ten at a time, on a nine second budget, and then hand the
   failures to the publish gate. On a phone with one bar in a shop that meant
   the shelf could lose flavours and whole products while somebody was looking
   at it, and the result was cached for a week, so it stayed lost afterwards on
   good Wi-Fi with nothing to explain it.
   Every surface a customer browses now draws from the photographs embedded in
   this file, so an unreachable host is not a missing picture and must not
   decide what the shop is allowed to sell. The menu is the same on every
   phone, online or off.
   verifyMedia() is unchanged and still available: the staff media-check screen
   runs it on demand, which is where "have any of our hotlinked photographs
   gone stale" is a question worth asking. */""")

rep("""    if(p && typeof LOCAL_PHOTOS!=='undefined' && LOCAL_PHOTOS[p.id]){
      if(typeof retireImage==='function') retireImage(url);
      const alt = (p.brand+' '+p.name).replace(/"/g,'');""",
"""    if(p && typeof LOCAL_PHOTOS!=='undefined' && LOCAL_PHOTOS[p.id]){
      /* The photograph is not dead, the host is, and the customer has just
         been handed the picture anyway. Recording it as dead would put this
         product's flavours in front of the publish gate for seven days over a
         connection problem that lasted a second. */
      const alt = (p.brand+' '+p.name).replace(/"/g,'');""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
