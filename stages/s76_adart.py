#!/usr/bin/env python3
# Stage 76 — the deal cards take the device too.
#
# Stage 75 gave the carousel campaigns the device instead of the carton, but
# the offer that greets a first visit is not a campaign: it is the deal card,
# rendered into a dialog, and it resolves its artwork through cutout() rather
# than heroCut(). So the entrance still opened on a nicotine warning.
#
# One accessor, used by every advertisement. The shelf keeps cutout() and keeps
# the photograph the manufacturer published.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


rep("""const heroCut = (brand, modelLike) => {
  const id = (typeof pidFor==='function') ? pidFor(brand, modelLike) : '';
  if(id && HERO_DEVICE[id]) return HERO_DEVICE[id];
  return id ? cutout(id) : '';
};""",
"""/* What an ADVERTISEMENT shows for a product: the device where we hold a crop of
   it, and otherwise whatever the shelf shows. The shelf itself always uses
   cutout(), so a product card is still the manufacturer's own published
   photograph of the thing in its box. */
const adCut = id => (id && HERO_DEVICE[id]) || (id ? cutout(id) : '');
const heroCut = (brand, modelLike) => {
  const id = (typeof pidFor==='function') ? pidFor(brand, modelLike) : '';
  return id ? adCut(id) : '';
};""")

rep("""  const shots = (d.art||[]).map(a=>{
    const pid = pidFor(a.b, a.m); if(!pid) return '';
    const src = cutout(pid); if(!src) return '';""",
"""  const shots = (d.art||[]).map(a=>{
    const pid = pidFor(a.b, a.m); if(!pid) return '';
    const src = adCut(pid); if(!src) return '';""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
