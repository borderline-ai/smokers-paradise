#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 134 — Visit the Shop, and the label sitting on top of the address.
#
# Marco: "You almost got this section right. Its missing work, it needs detail,
# THE WHOLE SECTION THAT SAYS VISIT THE SHOP."
#
# He is being kind. Screenshotted at full size there is a straight collision in
# it, and it is in two of the five pictures he sent:
#
#     .storeb .map .pin{ position:absolute; left:50%; top:44% }
#
# That is a MAP PIN — a red dot and a black "SMOKERS PARADISE" label — from
# when the top of this card was a map. The map was replaced by the address
# plate and the pin was left behind, still absolutely positioned at the middle
# of the band, so it lands on top of the address. The card reads:
#
#     SMOKERS
#     PARADISF          <- clipped by the plate edge
#     922 N Grand Av[SMOKERS PARADISE]
#
# A red dot floating over a wordmark and a black label covering the street
# address. That is the "missing work" he can see and could not name.
#
# WHAT IT SHOULD BE, and the test is simple: this is the screen that asks
# somebody to get in a car. Everything on it should answer a question they
# would ask before doing that.
#
#   WHAT DOES IT LOOK LIKE. Their own photograph of the storefront under the
#   red awning, full bleed at the top of the card — the shop has supplied it
#   and it was being shown nowhere on this screen. You are looking for a red
#   awning on North Grand; here is the red awning on North Grand.
#
#   IS IT OPEN. The live state on the photograph, in the corner, computed from
#   the hours rather than written down.
#
#   WHEN. The hours table with today's row marked, which it already did well.
#
#   WHAT DO I NEED TO KNOW BEFORE I GO. Four facts, as a two-up grid of plates
#   rather than a bulleted list, so they can be taken in at a glance instead of
#   read as a paragraph. Parking is added: it is on the announcement bar, so it
#   is confirmed copy, and "where do I park" is the fifth question anybody asks
#   about a shop on a main road.
#
#   AND THEN THE TWO THINGS THEY WILL ACTUALLY TAP, at equal weight.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the markup ---------------------------------------------------------
rep("""    <div class="storeb">
      <div class="map">${mapArt()}
        <div class="pin"><div class="dot"></div><div class="lb">SMOKERS PARADISE</div></div></div>
      <div class="sinfo">""",
"""    <div class="storeb">
      ${/* THE BUILDING YOU ARE DRIVING TO.
             The shop photographed its own storefront and the picture was being
             used nowhere on the screen that asks somebody to drive to it. The
             orphaned map pin that used to sit here — a red dot and a black
             label, left over from when this band was a map — was landing on
             top of the street address. It is gone. */''}
      <div class="stfront">
        <img src="${IG_SIGN}" alt="Smokers Paradise on North Grand Avenue, under the red awning"
          loading="lazy" decoding="async"
          onerror="this.closest('.stfront').classList.add('nopic')">
        <span class="stf-scrim" aria-hidden="true"></span>
        <span class="stf-state ${(typeof storeStatus==='function'&&storeStatus().open)?'on':''}"
          ><i></i>${esc((typeof storeStatus==='function')?storeStatus().label:'')}</span>
        <span class="stf-cap">North Grand Avenue, under the red awning</span>
      </div>
      <div class="map">${mapArt()}</div>
      <div class="sinfo">""")

rep("""        <ul class="sfacts">
          <li><svg viewBox="0 0 24 24"><path d="M4 7h11v9H4zM15 10h3l3 3v3h-6z"/><circle cx="7.5" cy="18" r="1.6"/><circle cx="17.5" cy="18" r="1.6"/></svg>
            Pickup at the counter. Nothing ships and nothing gets delivered.</li>
          <li><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2.5"/><circle cx="9" cy="11" r="2"/><path d="M5.5 16.5c.9-1.6 2-2.4 3.5-2.4s2.6.8 3.5 2.4M15 10h4M15 13.5h4"/></svg>
            21+ with valid ID, every visit, no exceptions.</li>
          <li><svg viewBox="0 0 24 24"><path d="M4 6h9M8.5 6v1.5c0 3-2 5.5-4.5 6.5M6.5 10.5c1 2.2 2.8 3.6 5 4.2"/><path d="M13 19l3.5-8 3.5 8M14.6 16.4h4.8"/></svg>
            Se habla espa&ntilde;ol. Ask for anything at the counter.</li>
          <li><svg viewBox="0 0 24 24"><path d="M12 21s7-5.5 7-11a7 7 0 10-14 0c0 5.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>
            North Grand Avenue, Suite B. Plus code 83XC+9G.</li>
        </ul>
        <div class="addr" style="margin-top:10px;font-size:11.5px;color:var(--muted)">${STORE.pickup}</div>""",
"""        ${/* BEFORE YOU GET IN THE CAR. A bulleted list is read as a
               paragraph and a paragraph is not read at all. Five plates, taken
               in at a glance. Parking is new and is not invented: it is on the
               shop's own announcement bar, and "where do I park" is the
               question a shop on a main road always gets. */''}
        <div class="sfgrid">
          <div class="sfp"><svg viewBox="0 0 24 24"><path d="M4 7h11v9H4zM15 10h3l3 3v3h-6z"/><circle cx="7.5" cy="18" r="1.6"/><circle cx="17.5" cy="18" r="1.6"/></svg>
            <b>Pickup only</b><span>Nothing ships and nothing gets delivered.</span></div>
          <div class="sfp"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2.5"/><circle cx="9" cy="11" r="2"/><path d="M5.5 16.5c.9-1.6 2-2.4 3.5-2.4s2.6.8 3.5 2.4M15 10h4M15 13.5h4"/></svg>
            <b>21+ with ID</b><span>Checked every visit, no exceptions.</span></div>
          <div class="sfp"><svg viewBox="0 0 24 24"><path d="M4 6h9M8.5 6v1.5c0 3-2 5.5-4.5 6.5M6.5 10.5c1 2.2 2.8 3.6 5 4.2"/><path d="M13 19l3.5-8 3.5 8M14.6 16.4h4.8"/></svg>
            <b>Se habla espa&ntilde;ol</b><span>Ask for anything at the counter.</span></div>
          <div class="sfp"><svg viewBox="0 0 24 24"><path d="M5 11h14l-1.4-4.2A2 2 0 0015.7 5.4H8.3a2 2 0 00-1.9 1.4zM5 11h14v5H5z"/><circle cx="8" cy="18" r="1.4"/><circle cx="16" cy="18" r="1.4"/></svg>
            <b>Free parking</b><span>In our own lot on North Grand.</span></div>
          <div class="sfp wide"><svg viewBox="0 0 24 24"><path d="M12 21s7-5.5 7-11a7 7 0 10-14 0c0 5.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>
            <b>922 N Grand Ave, Suite B</b><span>Plus code 83XC+9G. Nogales, AZ 85621.</span></div>
        </div>
        <div class="addr" style="margin-top:12px;font-size:11.5px;color:var(--muted)">${STORE.pickup}</div>""")

# ---- 2. the plate stops fighting the card ----------------------------------
rep("""  return `<span class="addrplate">
    <span class="ap-txt">
      <b>SMOKERS PARADISE</b>
      <i>922 N Grand Ave Ste B</i><i>Nogales, AZ 85621</i>
      <em>83XC+9G &middot; Nogales</em>
      <span class="ap-now ${st.open?'ap-open':'ap-shut'}"><i></i>${esc(st.word)}
        <b>${esc(st.label)}</b></span>
    </span>""",
"""  /* The address and the plus code moved onto the fact plates below, where
     they are read. What is left here is the sign and the name, which is what
     this band was for. */
  return `<span class="addrplate">
    <span class="ap-txt">
      <b>SMOKERS PARADISE</b>
      <i>Smoke shop &middot; Nogales, Arizona</i>
      <em>Open seven days</em>
      <span class="ap-now ${st.open?'ap-open':'ap-shut'}"><i></i>${esc(st.word)}
        <b>${esc(st.label)}</b></span>
    </span>""")

# ---- 3. the look -----------------------------------------------------------
rep(""".gr-sum b{font-size:40px;line-height:1}
""",
""".gr-sum b{font-size:40px;line-height:1}

/* ---- VISIT THE SHOP ----
   The screen that asks somebody to get in a car. It leads with the building
   they are looking for, in the shop's own photograph, with the live state on
   it; then when it is open; then the five things they would want to know
   before setting off, as plates rather than as a bulleted paragraph. */
.stfront{position:relative;display:block;height:186px;overflow:hidden;
  background:var(--stage);border-bottom:1px solid var(--hair)}
.stfront img{position:absolute;inset:0;width:100%;height:100%;
  object-fit:cover;object-position:50% 58%}
.stfront.nopic{display:none}
.stf-scrim{position:absolute;inset:0;display:block;pointer-events:none;
  background:linear-gradient(180deg, rgba(8,4,12,.46) 0%, rgba(8,4,12,0) 34%,
             rgba(8,4,12,.30) 66%, rgba(8,4,12,.86) 100%)}
.stf-state{position:absolute;top:11px;right:11px;z-index:2;display:inline-flex;
  align-items:center;gap:7px;font-family:var(--mono);font-size:9.5px;
  letter-spacing:1.1px;text-transform:uppercase;color:#F3E6F1;
  background:rgba(10,5,14,.7);border:1px solid rgba(255,255,255,.16);
  border-radius:99px;padding:6px 11px;backdrop-filter:blur(6px)}
.stf-state i{width:6px;height:6px;border-radius:50%;background:#FF7A6B;flex:none}
.stf-state.on i{background:#6BE28A;box-shadow:0 0 0 3px rgba(107,226,138,.2)}
.stf-cap{position:absolute;left:14px;right:14px;bottom:11px;z-index:2;display:block;
  font-family:var(--body-f);font-size:11.5px;line-height:1.35;color:rgba(255,246,252,.82);
  text-shadow:0 1px 10px rgba(0,0,0,.8)}

.sfgrid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:14px}
.sfp{position:relative;border-radius:13px;border:1px solid var(--hair);
  background:var(--card2);padding:11px 11px 12px;display:flex;
  flex-direction:column;gap:2px}
.sfp.wide{grid-column:1 / -1}
.sfp svg{width:17px;height:17px;fill:none;stroke:var(--go-ink);stroke-width:1.6;
  stroke-linecap:round;stroke-linejoin:round;margin-bottom:5px}
.sfp b{font-family:var(--body-f);font-size:12.5px;font-weight:700;color:var(--ink);
  line-height:1.2}
.sfp span{font-size:11px;line-height:1.4;color:var(--muted)}
@media (max-width:344px){ .sfgrid{grid-template-columns:1fr} }
""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
