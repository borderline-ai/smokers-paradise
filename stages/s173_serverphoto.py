#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 173 — the shop's photograph wins.
#
# A one-line-each fix to two objects, and the reason is a change of meaning
# rather than a mistake in the original.
#
# When stage 171 wrote Shop.pullCatalog, a `photo` was always megabytes of
# base64 and the service refused to hold one. So the merge kept whatever
# photograph was on the device:
#
#     S.edits[id] = Object.assign({}, edits[id], had.photo ? {photo: had.photo} : {});
#
# That was correct then. The server had no photograph to offer, so the local
# one was the only one there was, and letting an absent server value overwrite
# a real local picture would have blanked it.
#
# Stage 172 took the photographs out of the document and made them files, so a
# photograph is now a short path — `img/<hash>.webp` — and the service holds
# one happily. The moment that became true, the line above became a bug: the
# owner imports their real inventory with their real product photography, the
# shop's copy arrives at a customer's phone, and that phone keeps showing the
# picture whoever used it last had lying in localStorage.
#
# The rule is the same one as everywhere else in this codebase: the shop is the
# authority, and a device's copy is a cache. So the shop's photograph wins when
# there is one, and the local one is kept only when there is not — which is
# what still protects a picture somebody added at the counter and never
# uploaded.
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'app', 'index.html')
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


rep("""      /* The shop's copy wins over anything cached on this device, but a photo
         held locally is kept: the service does not store photographs and
         dropping one would blank a picture the shop already added. */
      S.edits = S.edits || {};
      Object.keys(edits).forEach(id=>{
        const had = S.edits[id] || {};
        S.edits[id] = Object.assign({}, edits[id], had.photo ? {photo: had.photo} : {});
      });
      if(custom.length){
        const mine = (S.custom || []);
        S.custom = custom.map(c=>{
          const had = mine.find(x=>x.id === c.id) || {};
          return Object.assign({}, had, c, had.photo ? {photo: had.photo} : {});
        }).concat(mine.filter(x=>!custom.some(c=>c.id === x.id)));
      }""",
"""      /* THE SHOP'S COPY WINS, INCLUDING THE PHOTOGRAPH.

         Since stage 172 a photograph is a path rather than a megabyte of
         base64, so the service holds one and its answer is the authority —
         the owner's own product photography, imported with their inventory,
         has to reach a phone that is holding somebody else's older picture.

         A local photograph is kept only where the shop has none. That is
         still worth doing: a picture taken at the counter and not yet
         uploaded is real, and blanking it would lose it. */
      const keepPhoto = (from, had) => {
        const out = Object.assign({}, had, from);
        if(!out.photo && had && had.photo) out.photo = had.photo;
        return out;
      };
      S.edits = S.edits || {};
      Object.keys(edits).forEach(id=>{
        S.edits[id] = keepPhoto(edits[id], S.edits[id] || {});
      });
      if(custom.length){
        const mine = (S.custom || []);
        S.custom = custom.map(c=>keepPhoto(c, mine.find(x=>x.id === c.id) || {}))
          .concat(mine.filter(x=>!custom.some(c=>c.id === x.id)));
      }""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
