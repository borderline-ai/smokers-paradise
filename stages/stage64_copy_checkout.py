#!/usr/bin/env python3
# Stage 64 — the copy edit, and the checkout screen by screen.
#
# Every string below was read on screen at 390px before it was changed. The
# rule applied throughout: Title Case for page and section headings, sentence
# case for everything a customer reads or fills in, UPPERCASE only for short
# eyebrow labels. American spelling. No sentence that says the same thing the
# sentence above it just said.
import io
import re

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:60].replace('\n', ' '))


# ===================================================================== 1. names
# "santy" was printed on the confirmation screen exactly as it was typed.
rep("""function esc(v){""",
"""/* A name typed into a phone keyboard arrives as "santy" or "SANTY". It is
   printed on the confirm screen, on the ticket the counter reads and in the
   greeting, so it is capitalised at every display site. Only names: nothing
   here touches an email address or any other case-sensitive field. */
function properName(v){
  return String(v == null ? '' : v).trim().toLowerCase()
    .replace(/\\b[\\p{L}][\\p{L}'\\u2019-]*/gu, w => w.charAt(0).toUpperCase() + w.slice(1))
    .replace(/\\bMc([\\p{L}])/gu, (m, a) => 'Mc' + a.toUpperCase())
    .replace(/\\bO\\u2019([\\p{L}])/gu, (m, a) => 'O\\u2019' + a.toUpperCase());
}

function esc(v){""")

rep("""  const who=(S.name||'').trim()||'Online customer';""",
    """  const who=properName(S.name)||'Online customer';""")
rep("""    <h3 style="margin-top:6px">${S.name||'Guest'}</h3>""",
    """    <h3 style="margin-top:6px">${properName(S.name)||'Guest'}</h3>""")
rep("""      <div class="ck-row"><span>${esc(CHK.name.trim()||'No name given')}${""",
    """      <div class="ck-row"><span>${esc(properName(CHK.name)||'No name given')}${""")
rep("""  if(nm) S.name = nm;""", """  if(nm) S.name = properName(nm);""")

# ============================================================== 2. pickup times
# "tomorrow 8:00 AM" on a button, and "Ready at tomorrow 8:00 AM" on the
# summary. The stored value is left alone; only the two display strings change.
rep("""             time: (sameDay ? '' : 'tomorrow ') + fmt(d), at: d}];""",
    """             time: (sameDay ? '' : 'tomorrow ') + fmt(d), at: d, day: sameDay ? '' : 'tomorrow'}];""")

rep("""/* the bag drawer was replaced by the four step checkout screen in p5c */""",
"""/* How a pickup slot reads in the two places a customer sees it. The stored
   value stays as it was so nothing downstream has to change. */
function slotLabel(sl){
  const t = String((sl && sl.time) || '');
  return t.replace(/^tomorrow /, 'Tomorrow, ').replace(/^today /, 'Today, ');
}
function slotPhrase(sl){
  const t = String((sl && sl.time) || '');
  const m = t.match(/^(tomorrow|today) (.+)$/);
  return m ? 'Ready ' + m[1] + ' at ' + m[2] : 'Ready at ' + t;
}

/* the bag drawer was replaced by the four step checkout screen in p5c */""")

rep("""          ${s.label==='ASAP'?'<b>ASAP</b>':''}${s.time}</button>`).join('')}</div>""",
    """          ${s.label==='ASAP'?'<b>ASAP</b>':''}${slotLabel(s)}</button>`).join('')}</div>""")

rep("""      <div class="ck-row"><span>Ready at ${pick.time}</span>""",
    """      <div class="ck-row"><span>${slotPhrase(pick)}</span>""")

# ================================================================= 3. step two
# Two cards, four sentences of help and a long privacy aside for two fields.
rep("""      <label class="ckfield"><span>Mobile number <em>optional</em></span>
        <input id="ckPhone" value="${esc(CHK.phone)}" placeholder="(520) 555-0134"
          inputmode="tel" autocomplete="tel" enterkeyhint="next"></label>
      <div class="ckwarn" id="ckWarn" role="alert"></div>
      <p class="ckfine">The name is what staff call out. The number is only used to text you
        when the bag is ready, and you can leave it blank and watch this screen instead.
        Message and data rates may apply. We never sell your number.</p>
    </div>
    <div class="ckcard">
      <p class="ckfine"><b>No card details.</b> This app does not take payment. You pay for
        your items at the counter when you collect them.</p>
    </div>""",
"""      <label class="ckfield"><span>Mobile number <em>(optional)</em></span>
        <input id="ckPhone" value="${esc(CHK.phone)}" placeholder="(520) 555-0134"
          inputmode="tel" autocomplete="tel" enterkeyhint="next"></label>
      <div class="ckwarn" id="ckWarn" role="alert"></div>
      <p class="ckfine">Staff call this name out at the counter. Add a number and we&rsquo;ll
        text you when the bag is ready &mdash; or leave it blank and watch this screen.</p>
    </div>
    <div class="ckcard">
      <p class="ckfine"><b>No payment here.</b> The app never asks for a card. You pay at the
        counter when you collect.</p>
    </div>""")

# =============================================================== 4. step three
rep("""      <div class="ckhead"><b>Have it ready for</b></div>""",
    """      <div class="ckhead"><b>Have it ready for</b></div>""")

rep("""      <p class="ckfine">${storeOpen()
        ? 'Most pickup orders are bagged in about ten minutes. Anything not collected by close goes back on the shelf.'
        : 'The shop is closed right now, so the first time you can collect is when it opens.'}</p>""",
"""      <p class="ckfine">${storeOpen()
        ? 'Most orders are bagged in about ten minutes. Anything not collected by closing goes back on the shelf.'
        : 'The shop is closed right now, so the first pickup is when it opens.'}</p>""")

# ================================================================ 5. step four
rep("""    <p class="ckfine pad">Your bag is built before you arrive. You still pay at the counter and you
      still show a valid government ID proving you are 21 or older, the same as any other customer.
      Pickup only at ${STORE.street}. Nothing ships and nothing is delivered.</p>""",
"""    <p class="ckfine pad">Pay at the counter and show a valid ID &mdash; 21+ on every pickup.
      Collect at ${STORE.street}. Pickup only; we don&rsquo;t ship or deliver.</p>""")

# ============================================================== 6. the promos
COPY = [
    # spelling: American retail, everywhere
    ('flavour', 'flavor'),
    ('Flavour', 'Flavor'),
    # the raffle and the wheel, written as offers rather than as notes
    ('Spend $10 or more and you are in the drawing. The prizes come off our own shelf.',
     'Spend $10 or more to get one raffle entry. Prizes come off our own shelf.'),
    ('Spend $10, you are in the drawing', 'Spend $10+ for a raffle entry'),
    ('Spend $10,\\nyou are in the drawing', 'Spend $10+\\nfor a raffle entry'),
    ('you are in the drawing', 'for a raffle entry'),
    ('Spend $15 or more and spin the wheel at the counter before you leave.',
     'Spend $15 or more and spin the prize wheel at the counter.'),
    ('Spend $15, spin the wheel at the counter', 'Spend $15+ and spin the prize wheel'),
    ('Spend $15, spin the wheel', 'Spend $15+ and spin the wheel'),
    ('Five flavors\\nof chocolate.', 'Five chocolate\\nflavors.'),
    ('Five flavors,\\nextra strength', 'Five flavors,\\nextra strength'),
    ('$30 a bar', '$30 each'),
    # reviews
    ("'Read the other ' + rest.toLocaleString()",
     "'Read all ' + total.toLocaleString() + ' reviews'"),
    ('<h3>Nogales keeps coming back</h3>', '<h3>Rated 4.9 on Google</h3>'),
    ("""          <span>${GOOGLE_RATING.count} reviews &middot; ${GOOGLE_RATING.checked}</span></div>""",
     """          <span>${GOOGLE_RATING.count} Google reviews</span></div>"""),
    # the duplicated sentence, printed on the storefront
    ("demoDisclaimer:'Product selection, prices and availability are confirmed with the store during onboarding. confirmed with Smokers Paradise during onboarding. Nothing here is a live stock count or a quoted shelf price.'",
     "demoDisclaimer:'Selection and prices can change at the shop, and the register is the final word. Nothing here is a live stock count.'"),
]
for a, b in COPY:
    n = s.count(a)
    if n == 0:
        print('  skip copy:', a[:52]); continue
    s = s.replace(a, b)
    print('  copy x%d:' % n, a[:52].replace('\n', ' '))

# ================================================================= 7. reviews
# The quotes are the reviewers' own words. What changes is only the truncation:
# an extract no longer opens or closes on an ellipsis mid-sentence, and the
# quotation marks are drawn by the stylesheet so the data stays clean.
rep("""       text:'Best place in town too purchase tobacco products or whatever else you\\u2019re looking for, the people are very very nice very attentive and their stock is always kept updated\\u2026'},""",
    """       text:'Best place in town too purchase tobacco products or whatever else you\\u2019re looking for, the people are very very nice very attentive and their stock is always kept updated.'},""")
rep("""       text:'\\u2026great place for all your vaping needs and many many others. The staff is super friendly. The owners super nice, prices are very competitive\\u2026'},""",
    """       text:'Great place for all your vaping needs and many many others. The staff is super friendly. The owners super nice, prices are very competitive.'},""")
rep("""       text:'Irma helped me pick and explained every item and what use and purpose it has! The store is stocked and organized to perfection\\u2026'}""",
    """       text:'Irma helped me pick and explained every item and what use and purpose it has! The store is stocked and organized to perfection.'}""")

# "Add yours" with nowhere to go. Both controls resolve against the same place,
# so neither can point somewhere the other does not.
rep("""const GOOGLE_WRITE_URL   = GOOGLE_PLACE_ID
  ? 'https://search.google.com/local/writereview?placeid=' + GOOGLE_PLACE_ID
  : null;""",
"""const GOOGLE_WRITE_URL   = GOOGLE_PLACE_ID
  ? 'https://search.google.com/local/writereview?placeid=' + GOOGLE_PLACE_ID
  : STORE.mapHref;   /* the listing itself, where the review control lives */""")
rep("""${GOOGLE_WRITE_URL ? `<a class="gr-link" href="${GOOGLE_WRITE_URL}" target="_blank" rel="noopener noreferrer">Add yours</a>` : ''}""",
    """${GOOGLE_WRITE_URL ? `<a class="gr-link" href="${GOOGLE_WRITE_URL}" target="_blank" rel="noopener noreferrer">Write a review</a>` : ''}""")

# ================================================================== 8. footer
rep("""    <div class="sf-note demo"><b>Selection and pricing.</b> ${STORE.demoDisclaimer.replace('','')}
      <span class="es">La seleccion, los precios y la disponibilidad se confirman con la tienda.</span></div>""",
"""    <div class="sf-note"><b>Selection and pricing.</b> ${STORE.demoDisclaimer}</div>""")

rep("""    <div class="sf-note"><b>21+ only.</b> Products on this menu contain nicotine or are intended
      for adults 21 and over. Nicotine is an addictive chemical. A valid government ID is checked
      at the counter on every pickup.</div>""",
"""    <div class="sf-note"><b>21+ only.</b> Products on this menu contain nicotine or are intended for
      adults 21 and over. Nicotine is an addictive chemical. A valid ID is checked at every pickup.</div>""")

rep("""    <div class="sf-note"><b>Pickup only.</b> Smokers Paradise does not ship and does not deliver. Nothing is
      paid for in this app. You pay at the counter when you collect, ${
        storeOpen() ? 'today until ' + closes : 'next time the shop is open'}.</div>""",
"""    <div class="sf-note"><b>Pickup only.</b> We don&rsquo;t ship and we don&rsquo;t deliver, and nothing is
      paid for in the app. You pay at the counter when you collect.</div>""")

CSS = r'''
/* ---- the checkout, screen by screen -------------------------------------
   The wizard now owns the height it has: the card sits at the top, the one
   action sits above the bottom bar, and the hole between them is gone. */
#v-checkout .ckwrap{padding-bottom:20px}
.ckfoot{margin-top:auto;padding-top:16px}
.ckfoot .btn{width:100%}

/* the step rail: four short words, readable, not tracked-out mono */
.cksteps li .l{
  font-family:var(--body-f);
  font-size:11.5px;
  font-weight:600;
  letter-spacing:.01em;
  text-transform:none;
  color:var(--muted);
}
.cksteps li.now .l{color:var(--ink)}
.cksteps li.done .l{color:var(--body)}

/* card headings inside the wizard are sentence case, at reading contrast */
.ckhead b,.ckcard .ckhead b{
  font-family:var(--body-f);
  font-weight:700;
  font-size:15px;
  letter-spacing:normal;
  text-transform:none;
  color:var(--ink);
}
.cklink{font-family:var(--body-f);font-weight:700;font-size:14px;
  text-transform:none;color:var(--go-ink)}

/* a pickup slot has to look chosen, not merely outlined */
.pickslot{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px}
.pickslot button{
  min-height:52px;padding:0 14px;border-radius:14px;
  font-family:var(--body-f);font-size:15px;font-weight:600;
  color:var(--ink2);
  background:#241536;
  border:1px solid rgba(255,120,205,.20);
}
.pickslot button b{display:block;font-size:11px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--go-ink);margin-bottom:2px}
.pickslot button.on{
  background:var(--go);color:#1A0510;border-color:var(--go);
  box-shadow:0 6px 18px rgba(255,47,168,.30);
}
.pickslot button.on b{color:#4A0A2C}

/* the summary rows: the values are the content, so they read as content */
.ck-row{display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:12px 0;border-bottom:1px solid var(--edge-2)}
.ck-row:last-child{border-bottom:0}
.ck-row > span{font-family:var(--body-f);font-size:15px;color:var(--ink2)}
.ckcard.sum .tot span,.ckcard.sum .tot b{font-size:15px}
.ckcard.sum .tot b{font-family:var(--mono);color:var(--ink)}
.ckcard.sum .tot.grand span{font-size:17px;color:var(--ink)}
.ckcard.sum .tot.grand b{font-size:19px}

/* ---- reviews ------------------------------------------------------------
   The quotation marks are drawn here so the stored text stays exactly what
   the reviewer wrote. */
.gr-q blockquote{
  font-family:var(--body-f);
  font-size:14px;line-height:1.55;color:var(--ink2);
  quotes:'\201C' '\201D';
}
.gr-q blockquote::before{content:open-quote}
.gr-q blockquote::after{content:close-quote}
.gr-q figcaption{font-family:var(--body-f);font-size:12.5px;color:var(--muted)}
.gr-q figcaption i{display:inline-block;width:4px;height:4px;border-radius:50%;
  background:currentColor;opacity:.5;margin:0 7px 2px}
.gr-sum b{font-family:var(--disp);font-weight:800;color:var(--ink)}
.gr-sum span{font-family:var(--body-f);color:var(--muted)}
.gr-stars svg{fill:#5A4A68}
.gr-stars svg.on{fill:#FFC46B}
.gr-link{font-family:var(--body-f);font-weight:700;font-size:14px;
  color:#FFD3EC;text-decoration:none}

/* ---- the footer ---------------------------------------------------------
   Sections, each one line of a kind, all in one language. */
.sitefoot{padding:26px var(--pad) 30px}
.sf-name{font-family:var(--disp);font-weight:800;font-size:19px;color:var(--ink);
  letter-spacing:-.02em}
.sf-row{font-family:var(--body-f);font-size:13.5px;line-height:1.7;color:var(--body);
  margin-top:8px}
.sf-links{display:flex;flex-wrap:wrap;gap:9px;margin-top:14px}
.sf-links a{font-family:var(--body-f);font-size:13.5px;font-weight:600;
  color:#FFD3EC;text-decoration:none;padding:9px 15px;border-radius:99px;
  border:1px solid rgba(255,120,205,.28)}
.sf-note{font-family:var(--body-f);font-size:12.5px;line-height:1.6;
  color:var(--muted);margin-top:14px}
.sf-note b{color:var(--ink2)}
.sf-legal{display:flex;align-items:center;gap:14px;margin-top:20px;
  padding-top:16px;border-top:1px solid var(--edge-2);
  font-family:var(--body-f);font-size:12.5px;color:var(--muted)}
.sf-legal button{background:none;border:0;padding:0;color:#FFD3EC;
  font-family:var(--body-f);font-size:12.5px;font-weight:600;cursor:pointer}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  checkout, review and footer styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
