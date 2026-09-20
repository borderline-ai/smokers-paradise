#!/usr/bin/env python3
# Stage 75 — no advertisement in this shop leads with a government warning.
#
# The first screen a customer sees is the Off-Stamp offer, and the biggest,
# highest-contrast block on it is a white rectangle that reads WARNING: THIS
# PRODUCT CONTAINS NICOTINE. Not because anyone put it there: the cut-out
# registered for the X Cube is a cut-out of the RETAIL CARTON, and the carton
# has the warning printed across its face. The same is true of the Lost Mary
# MT35000 and the Geek Bar Pulse X, so three of the four campaign photographs
# in the app are advertising the warning label.
#
# The warning belongs on the box and on the shelf, and it is on both. It is not
# the picture, and a poster whose loudest element is a legal notice is not a
# poster. The device is already in the same photograph, standing next to the
# carton it came in, so the fix is a crop and nothing else: no redraw, no
# substitute model, no retouching of the device itself.
#
# These go in their own table rather than over the catalogue's cut-outs. A
# product card and a campaign want different pictures of the same thing, and
# the shelf keeps the photograph the manufacturer published.
import io
import json

P = '/root/work/smokers-paradise-demo/build/index.html'
DEV = '/root/work/smokers-paradise-demo/data_hero_devices.json'

s = io.open(P, encoding='utf-8').read()
n0 = len(s)
dev = json.load(open(DEV))


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


rep("""const heroCut = (brand, modelLike) => {
  const id = (typeof pidFor==='function') ? pidFor(brand, modelLike) : '';
  return id ? cutout(id) : '';
};""",
"""/* The device on its own, for the three products whose only published cut-out
   is of the carton they ship in. A carton carries the printed nicotine warning
   across its face, which at poster size is the only thing on the poster anybody
   can read. Each of these is a crop of the manufacturer's own photograph, taken
   from the device standing beside that carton in the same shot. Nothing is
   redrawn, recoloured or stood in for, and the shelf still shows the picture
   the manufacturer published. */
const HERO_DEVICE = """ + json.dumps(dev, separators=(',', ':')) + """;
const heroCut = (brand, modelLike) => {
  const id = (typeof pidFor==='function') ? pidFor(brand, modelLike) : '';
  if(id && HERO_DEVICE[id]) return HERO_DEVICE[id];
  return id ? cutout(id) : '';
};""")

io.open(P, 'w', encoding='utf-8').write(s)
print('  %d devices embedded (%.0f KB)'
      % (len(dev), sum(len(v) for v in dev.values()) / 1024))
print('\n%d -> %d bytes' % (n0, len(s)))
