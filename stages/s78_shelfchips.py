#!/usr/bin/env python3
# Stage 78 — fifteen things that look like buttons become buttons.
#
# "What We Carry" is the shop's own list of what is on the shelves, set as
# fifteen pills. They are <span>s. They look exactly like the brand filters on
# a shelf and the criteria in Narrow Your Shelf, which ARE buttons, so every
# customer presses one, and nothing happens.
#
# Wiring them all to the search box is the obvious move and it is wrong: run
# each of the fifteen through the search and eleven of them return nothing.
# "Kratom" returns nothing. "CBD" returns nothing. "Scales" returns nothing.
# That would trade fifteen dead pills for eleven dead ends, which is worse,
# because a dead end is a promise broken twice.
#
# So each pill knows what it is:
#
#   a shelf          Glass, Disposables, Papers & Wraps ... open the shelf
#   on the shelves   Torches, Rolling Trays, Silicone ..... run the search
#   in store only    CBD, Kratom, Scales, Spiritual ....... say so, plainly
#
# The third case is the point. The shop told us they carry these; the app's
# catalogue does not list them yet. A pill that says "we have it, ask at the
# counter" is the truth, and it is the same sentence already printed under the
# list. Silence would have been the lie.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


# ---- 1. where each pill goes ------------------------------------------------
SHELF = {
    'Glass': 'water',
    'E-Juice & Devices': 'eliq',
    'Disposables': 'disp',
    'Mushroom Chocolate': 'exotic',
    'Love': 'love',
    'Papers & Wraps': 'roll',
    'Vaporizers': 'hard',
}
FIND = {
    'Torches': 'torch',
    'Rolling Trays': 'tray',
    'Silicone': 'silicone',
}
# everything else: on the shelf in Nogales, not in this catalogue yet

rep("""function galleryItem(k){ return STORE_CONTENT.gallery.find(g=>g.k===k) }""",
"""function galleryItem(k){ return STORE_CONTENT.gallery.find(g=>g.k===k) }

/* ---- what we carry, and where each one actually goes ----------------------
   A pill that opens a shelf opens it. A pill the catalogue can find by name
   searches for it. A pill for something the shop stocks but the app does not
   list yet says that, because the shop said they carry it and the app saying
   "nothing matched" would call them a liar. */
const SHELF_PILL = """ + __import__('json').dumps(SHELF, separators=(',', ':')) + """;
const FIND_PILL  = """ + __import__('json').dumps(FIND, separators=(',', ':')) + """;
function pillGo(label){
  const cat = SHELF_PILL[label];
  if(cat && CATS.some(c=>c[0]===cat)){ go('cat', cat); return }
  const q = FIND_PILL[label];
  if(q){ openSearchFor(q); return }
  toast('We carry ' + label.toLowerCase() + ' in the shop. It is not on the app '
      + 'shelf yet, so ask for it at the counter.');
}""")

# ---- 2. the markup ---------------------------------------------------------
rep("""    <div class="hlrow">${C.highlights.map(h=>`<span class="hl">${esc(h)}</span>`).join('')}</div>""",
"""    <div class="hlrow">${C.highlights.map(h=>`<button class="hl" type="button"
      data-pill="${esc(h)}">${esc(h)}</button>`).join('')}</div>""")

rep(".hl{font-family:var(--body-f);font-size:12px;color:var(--ink2);background:var(--panel-2);\n  border:1px solid var(--edge);border-radius:var(--rpill);padding:6px 12px}",
    ".hl{font-family:var(--body-f);font-size:12px;color:var(--ink2);background:var(--panel-2);\n"
    "  border:1px solid var(--edge);border-radius:var(--rpill);padding:6px 12px;\n"
    "  cursor:pointer;transition:background .15s,border-color .15s,color .15s}\n"
    "/* It looked like a button before it was one. Now that it is, it says so on\n"
    "   touch and on hover, because a control that gives nothing back when you\n"
    "   press it feels broken even when it worked. */\n"
    ".hl:hover{background:var(--card2);border-color:var(--brand);color:var(--ink)}\n"
    ".hl:active{transform:scale(.96)}\n"
    ".hl:focus-visible{outline:2.5px solid var(--brand);outline-offset:2px}")

# ---- 3. the handler --------------------------------------------------------
rep("""  const sc2=t.closest('[data-scrollto]'); if(sc2){""",
"""  const pl=t.closest('[data-pill]'); if(pl){ pillGo(pl.dataset.pill); return }
  const sc2=t.closest('[data-scrollto]'); if(sc2){""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
