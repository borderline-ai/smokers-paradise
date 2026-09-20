#!/usr/bin/env python3
# Stage 50 — the campaigns use the embedded photographs too.
#
# heroShot() still handed the campaigns a remote URL, so with the network
# blocked the hero and the pair went to empty frames while every product card
# behind them was fine. The campaigns are the first thing anyone sees; they get
# the same guarantee.
#
# The embedded photograph is the same official file, already downloaded, so
# this costs nothing visually and removes the last thing in the app that
# depends on somebody else's CDN.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

OLD = """  const pool = cands.length ? cands : list.filter(p => p.brand === brand);
  for(const p of pool){
    if(flavor){"""
NEW = """  const pool = cands.length ? cands : list.filter(p => p.brand === brand);
  /* the embedded photograph first: it is the same official file, it is in this
     document, and a campaign must never be the thing that shows an empty frame */
  if(typeof LOCAL_PHOTOS !== 'undefined')
    for(const p of pool) if(LOCAL_PHOTOS[p.id]) return LOCAL_PHOTOS[p.id];
  for(const p of pool){
    if(flavor){"""
assert s.count(OLD)==1
s=s.replace(OLD,NEW)
io.open(P,'w',encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
