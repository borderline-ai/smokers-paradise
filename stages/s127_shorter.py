#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 127 — the home page was sixteen and a half screens.
#
# Marco: "We ALSO cant make this page SO dam long, thats why we have a menu on
# the top right."
#
# Measured on a 390 screen: 13,950 pixels over 27 sections. Sixteen and a half
# phone screens of scrolling to reach the bottom of a home page. Here is where
# it was going, largest first:
#
#     2,540  Today's Deals      every offer, full size, stacked
#       449  Shop Our Brands    a rail of products from the big brands
#       449  Paradise Picks     a rail of products picked at the counter
#       441  Disposable Brands  a grid of brand tiles
#       435  Glass Parts        a rail
#       424  Gear & Cleaning    a rail
#       409  Exotic Snacks      a rail
#
# WHAT IS ACTUALLY WRONG, and it is not that any one of those is bad. It is
# that the home page was trying to BE the shelf instead of pointing at it.
# Eleven rails in a row, each one a header and six cards, is not eleven pieces
# of information; it is the same piece of information eleven times, and a
# customer stops reading at about the fourth.
#
#   TODAY'S DEALS. The Deals tab exists, it is in the navigation bar at the
#   bottom of every screen, and it holds every offer at full size. The home
#   page showed all of them too, which is why one section was a fifth of the
#   entire page. Three, and the button that was already there.
#
#   FOUR RAILS COME OFF. Shop Our Brands, Exotic Snacks, Glass Parts and Gear
#   & Cleaning. Every one of those shelves is one tap away in Shop by Category
#   near the top of this same page, and one tap away again in the footer, which
#   now carries all sixteen departments. Nothing has been made unreachable —
#   the page has stopped saying it twice.
#
#   PARADISE PICKS comes off too, because "products we picked" sitting between
#   "products on offer" and "products that just arrived" is a third curation of
#   the same catalogue.
#
# WHAT STAYS, and why. Shop by Category, because it is the map. Disposable
# Vapes, the Puffco wall, the glass and New Arrivals, because those are the
# four shelves this shop is known for. Disposable Brands, because it is the
# only way to shop by brand from the home page. The shop itself — the feed, the
# crew, the events, the reviews, the address — because that is the half of this
# app that is not a catalogue and it is the half that sells the shop.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the deals stack, which was a fifth of the page ---------------------
rep("""    <div class="sec-lead">What we have going on. Save one and show the screen at the register.</div>
    <div class="dealgrid">${DEALCARDS.map(dealCardBig).join('')}</div>""",
"""    <div class="sec-lead">What we have going on. Save one and show the screen at the register.</div>
    ${/* THREE, NOT ALL OF THEM. Every offer at full size, stacked, was 2,540
           pixels — a fifth of the whole home page — and the Deals tab in the
           bar at the bottom of every screen already holds all of them at full
           size. The button beside the heading has always gone there. */''}
    <div class="dealgrid">${DEALCARDS.slice(0,3).map(dealCardBig).join('')}</div>
    ${DEALCARDS.length>3?`<button class="dealmore" data-go="deals"
      >See all ${DEALCARDS.length} offers ${ARROW}</button>`:''}""")

# ---- 2. four rails that Shop by Category already covers --------------------
rep("""  ${famous.length?railSec('Shop Our Brands',
      '<button class="more" data-go="all">Shop All</button>',
      famous.map(card).join(''),
      4,'Across the shelf'):''}

""",
"""  ${/* OFF THE HOME PAGE, NOT OUT OF THE APP.
         Shop Our Brands, Paradise Picks, Exotic Snacks, Glass Parts and Gear
         & Cleaning were five rails of the same shape carrying the same kind of
         thing, and every one of those shelves is one tap away in Shop by
         Category further up this page and again in the footer. `famous`,
         `picks`, `shrooms`, `parts` and `gear` are still built above, because
         the search, the fit tool and the shelf screens all use them. */''}

""")

rep("""  ${picks.length?railSec('Paradise Picks','<button class="more" data-go="all">Shop All</button>',
      picks.map(card).join(''),1.5,'Picked at the counter'):''}

""", "")

rep("""  ${shrooms.length?railSec('Exotic Snacks','<button class="more" data-go="cat-exotic">View All</button>',
      shrooms.map(card).join(''),1.8,'Picked at the counter'):''}

""", "")

rep("""  ${parts.length?railSec('Glass Parts & Accessories','<button class="more" data-go="cat-parts">View All</button>',
      parts.map(card).join(''),6,'Keep it running'):''}

""", "")

rep("""  ${gear.length?railSec('Gear & Cleaning','<button class="more" data-go="cat-gear">View All</button>',
      gear.map(card).join(''),8,'Grinders, trays, torches'):''}

""", "")

# ---- 3. the one new control ------------------------------------------------
rep(""".gr-sum b{font-size:40px;line-height:1}
""",
""".gr-sum b{font-size:40px;line-height:1}

/* the foot of a shortened deals section */
.dealmore{display:flex;align-items:center;justify-content:center;gap:8px;
  width:calc(100% - 30px);margin:12px 15px 0;min-height:46px;padding:0 18px;
  border-radius:99px;border:1px solid var(--hair);background:none;
  font-family:var(--body-f);font-size:13.5px;font-weight:700;color:var(--ink2)}
.dealmore svg{width:14px;height:14px;flex:none}
.dealmore:focus-visible{outline:2.5px solid var(--brand);outline-offset:2px}
""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
