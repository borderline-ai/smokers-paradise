#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 128 — putting back what stage 127 should not have taken.
#
# Stage 127 cut five rails off the home page to shorten it, and the test suite
# caught one of them being wrong within the minute:
#
#     FAIL  the featured-brand rail is on the home screen
#     FAIL  and it shows all 9 brands the shop leads with, not the first four
#
# That check was written in stage 88 for a reason. STORE_CONTENT.featuredBrands
# is the shop's own answer to "what moves off your shelf" — TRE House,
# Off-Stamp, Lost Mary, Geek Bar, RAZ, RAW, GRAV, Puffco, Ooze — and it spans
# the whole shop. The Disposable Brands grid that is still on the page covers
# vapes only, so cutting Shop Our Brands took RAW, GRAV, Puffco, Ooze and TRE
# House off the home page with no way back to them by name.
#
# It does not have to come back as it was. As a rail of twelve product cards it
# cost 449 pixels to say nine words. As a strip of nine brand chips, each with
# one photograph from that brand's own shelf, it costs about 150 and says the
# same thing more directly — the brand IS the thing being tapped, instead of a
# product standing in for it.
#
# The lesson is the test, not the rail. Shortening a page is deleting, and
# deleting is where you lose something you meant to keep. Every cut in 127 went
# past a suite that knows what this app is supposed to contain, and the one cut
# that mattered failed out loud.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- the strip -------------------------------------------------------------
rep("""  ${/* OFF THE HOME PAGE, NOT OUT OF THE APP.""",
"""  ${/* THE NINE BRANDS THE SHOP LEADS WITH, as brands rather than as twelve
         product cards standing in for them. Same list, a third of the height,
         and tapping a brand goes to that brand instead of to one of its
         products. The Disposable Brands grid below covers vapes; this covers
         the shop, which is where RAW, GRAV, Puffco, Ooze and TRE House live. */''}
  ${famous.length?`<div class="sec tight reveal" style="--i:1.2">
    ${secHead('Shop Our Brands','<button class="more" data-go="all">Shop All</button>','Across the shelf')}
    <div class="brandstrip">${(STORE_CONTENT.featuredBrands||[]).map(b=>{
      const ps = PRODUCTS.filter(p=>p.brand===b && p.published!==false).filter(shot).sort(rank);
      if(!ps.length) return '';
      const p  = ps[0];
      const src= (typeof adCut==='function' ? adCut(p.id) : cutout(p.id)) || cutout(p.id);
      if(!src) return '';
      return `<button class="bstrip" data-brand="${esc(b)}">
        <span class="bs-ph"><img src="${src}" alt="" loading="lazy" decoding="async"
          onerror="this.style.visibility='hidden'"></span>
        <b>${esc(b)}</b><small>${ps.length} item${ps.length===1?'':'s'}</small></button>`;
    }).join('')}</div>
  </div>`:''}

  ${/* OFF THE HOME PAGE, NOT OUT OF THE APP.""")

# ---- the look --------------------------------------------------------------
rep("""/* the foot of a shortened deals section */""",
"""/* nine brands in one row, scrolled across rather than nine rows down */
.brandstrip{display:flex;gap:10px;overflow-x:auto;padding:2px 15px 8px;
  scrollbar-width:none;scroll-snap-type:x proximity}
.brandstrip::-webkit-scrollbar{display:none}
.bstrip{flex:none;width:96px;scroll-snap-align:start;display:flex;flex-direction:column;
  align-items:center;gap:2px;padding:10px 8px 11px;border-radius:14px;
  border:1px solid var(--hair);background:var(--card)}
.bs-ph{position:relative;width:100%;height:56px;display:block}
.bs-ph img{position:absolute;inset:4%;width:92%;height:92%;
  object-fit:contain;object-position:center}
.bstrip b{font-family:var(--body-f);font-size:12px;font-weight:700;color:var(--ink);
  line-height:1.2;text-align:center;margin-top:6px}
.bstrip small{font-family:var(--mono);font-size:9px;letter-spacing:.6px;color:var(--faint)}
.bstrip:focus-visible{outline:2.5px solid var(--brand);outline-offset:2px}

/* the foot of a shortened deals section */""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
