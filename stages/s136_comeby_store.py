#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 136 — the OTHER Come By.
#
# Marco asked for two sections and I rebuilt three, because there are two
# things in this app called Come By and I had only found one of them:
#
#   the FOOTER block headed COME BY, on every screen         (stage 135)
#   the SECTION headed Come By on the Our Store screen       (this one)
#   the SECTION headed Visit the Shop on the home screen     (stage 134)
#
# The last two are the same card, `.storeb`, rendered from two different
# places, and stage 134 only touched the home one — because the text I matched
# on included the orphaned map pin, and the pin was only in the home copy. So
# the Store screen still had the old shape: the plate, a two-row hours table, a
# bulleted list of four facts and three buttons, with no photograph of the shop
# on the screen whose entire subject is the shop.
#
# Same treatment, same reasons, and now they are the same card again. Two
# copies of one component drifting apart is how an app starts looking like two
# people built it.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""    ${secHead('Come By','', st.label)}
    <div class="storeb">
      <div class="map">${mapArt()}</div>""",
"""    ${secHead('Come By','', st.label)}
    <div class="storeb">
      ${/* the same storefront that leads the card on the home screen; these
             are one component rendered from two places and they had drifted */''}
      <div class="stfront">
        <img src="${IG_SIGN}" alt="Smokers Paradise on North Grand Avenue, under the red awning"
          loading="lazy" decoding="async"
          onerror="this.closest('.stfront').classList.add('nopic')">
        <span class="stf-scrim" aria-hidden="true"></span>
        <span class="stf-state ${st.open?'on':''}"><i></i>${esc(st.label)}</span>
        <span class="stf-cap">North Grand Avenue, under the red awning</span>
      </div>
      <div class="map">${mapArt()}</div>""")

rep("""        ${/* The four things a person asks before driving over. Every one of
             them is stated elsewhere in this app and none of them were on the
             screen about visiting the shop. */''}
        <ul class="sfacts">
          <li><svg viewBox="0 0 24 24"><path d="M4 7h11v9H4zM15 10h3l3 3v3h-6z"/><circle cx="7.5" cy="18" r="1.6"/><circle cx="17.5" cy="18" r="1.6"/></svg>
            Pickup at the counter. Nothing ships and nothing gets delivered.</li>
          <li><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2.5"/><circle cx="9" cy="11" r="2"/><path d="M5.5 16.5c.9-1.6 2-2.4 3.5-2.4s2.6.8 3.5 2.4M15 10h4M15 13.5h4"/></svg>
            21+ with valid ID, every visit, no exceptions.</li>
          <li><svg viewBox="0 0 24 24"><path d="M4 6h9M8.5 6v1.5c0 3-2 5.5-4.5 6.5M6.5 10.5c1 2.2 2.8 3.6 5 4.2"/><path d="M13 19l3.5-8 3.5 8M14.6 16.4h4.8"/></svg>
            Se habla espa&ntilde;ol. Ask for anything at the counter.</li>
          <li><svg viewBox="0 0 24 24"><path d="M12 21s7-5.5 7-11a7 7 0 10-14 0c0 5.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>
            North Grand Avenue, Suite B. Plus code 83XC+9G.</li>
        </ul>""",
"""        ${/* the same five plates as the home card, for the same reason: a
               bulleted list of conditions is read as a paragraph, and a
               paragraph on this screen is not read at all */''}
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
        </div>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
