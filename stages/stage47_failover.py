#!/usr/bin/env python3
# Stage 47 — a photograph that fails to load falls back to the one in the file.
#
# This is the last hole, and it is the one that produced most of the blank
# cards. When a remote flavour photograph failed — hotlink refused, file moved,
# no network — hcImgFail retired it and replaced the frame with "Photo coming
# soon". It never looked at the embedded photograph of that same product, which
# was sitting right there in the file.
#
# Now the order is: the exact flavour's photograph while the network can serve
# it, and the embedded photograph of that exact model the moment it cannot.
# The honest empty frame is still there, but only for a product this build has
# no photograph of at all — and after stage 45 there are none of those on the
# shelf.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

OLD = """    const url = el.getAttribute('src');
    if(typeof retireImage==='function' && retireImage(url)){
      if(typeof rebuildCatalog==='function') rebuildCatalog();
      if(typeof repaintAfterMedia==='function'){ repaintAfterMedia(); return; }
    }
    el.outerHTML = imageUnavailable();"""
NEW = """    const url = el.getAttribute('src');
    /* Before anything else: this product's own photograph is in this file.
       A remote file being unreachable is not a reason to show a customer an
       empty frame when the picture is already here. */
    if(p && typeof LOCAL_PHOTOS!=='undefined' && LOCAL_PHOTOS[p.id]){
      if(typeof retireImage==='function') retireImage(url);
      const alt = (p.brand+' '+p.name).replace(/"/g,'');
      el.outerHTML = '<img src="'+LOCAL_PHOTOS[p.id]+'" alt="'+alt+'">';
      return;
    }
    if(typeof retireImage==='function' && retireImage(url)){
      if(typeof rebuildCatalog==='function') rebuildCatalog();
      if(typeof repaintAfterMedia==='function'){ repaintAfterMedia(); return; }
    }
    el.outerHTML = imageUnavailable();"""
assert s.count(OLD)==1
s=s.replace(OLD,NEW)
io.open(P,'w',encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
