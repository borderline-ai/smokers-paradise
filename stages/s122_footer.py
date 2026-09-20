#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 122 — the bottom of every page.
#
# Marco: "everything under the reviews section is underdeveloped. The logo
# looks weird off to the right and it just doesnt look right."
#
# WHAT WAS ACTUALLY THERE, measured on a 390 screen: one column, left aligned,
# top to bottom — a 208px logo with 180px of empty black to the right of it,
# four lines of address and hours in body text, three pill links of three
# different widths wrapping onto two rows, three paragraphs of legal set at
# nearly the same size as the address, and a copyright. Every item the same
# weight, nothing lining up with anything, and the largest object on the screen
# with nothing beside it.
#
# THE LOGO. He is right and here is the mechanism: the mark's own artwork puts
# the girl and the cigarette on the LEFT and the wordmark on the RIGHT, so the
# optical weight sits right of centre inside its own box. Left-align that box
# in a wide column and the logo reads as drifting right into empty space. It is
# not fixed by centring the box, which pushes the weight further right still.
# It is fixed by giving it something to sit opposite: the mark is smaller and
# sits on a row with the shop's live open/closed state on the other end, so the
# line is balanced and the empty space is gone.
#
# WHAT "UNDERDEVELOPED" MEANT, and this is the part worth doing properly: a
# footer on a real retail app is the second navigation. Every one of them —
# every chain, every dispensary — puts the departments down there, because the
# bottom of a long page is exactly where somebody who did not find what they
# wanted has arrived. This footer had no links at all except a phone number.
# It now carries the whole shelf, in two columns, every one of them live.
#
# AND THE HOURS ARE A TABLE, not four lines of prose, with today's row marked,
# because "which day is that" is the only question hours have to answer.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- 1. the markup ---------------------------------------------------------
rep("""    <div class="sf-mark">${(typeof markHTML==='function')
      ? markHTML('idle','footmark smokes') : ''}
      <span class="sf-name-a11y">Smokers Paradise</span></div>
    <div class="sf-row">${STORE.street}<br>${STORE.city}<br>
      ${STORE.hours.map(([a,b])=>`${a} &nbsp;${b}`).join('<br>')}</div>
    <div class="sf-links">
      <a href="${STORE.phoneHref}">${STORE.phone}</a>
      <a href="${STORE.mapHref}" target="_blank" rel="noopener">Directions</a>
      <a href="${STORE.instagram}" target="_blank" rel="noopener">${STORE.instagramHandle}</a>
    </div>
    <div class="sf-note"><b>Selection and pricing.</b> ${STORE.demoDisclaimer}</div>
    <div class="sf-note"><b>21+ only.</b> Products on this menu contain nicotine or are intended for
      adults 21 and over. Nicotine is an addictive chemical. A valid ID is checked at every pickup.</div>
    <div class="sf-note"><b>Pickup only.</b> We don&rsquo;t ship and we don&rsquo;t deliver, and nothing is
      paid for in the app. You pay at the counter when you collect.</div>""",
"""    ${/* THE MARK HAS SOMETHING TO SIT OPPOSITE.
         The artwork's own weight is right of its centre — girl and cigarette
         left, wordmark right — so left-aligned in a wide column it reads as
         drifting into empty space, which is what Marco saw. Smaller, with the
         shop's live state on the other end of the line. */''}
    <div class="sf-head">
      <div class="sf-mark">${(typeof markHTML==='function')
        ? markHTML('idle','footmark smokes') : ''}
        <span class="sf-name-a11y">Smokers Paradise</span></div>
      <div class="sf-state${st.open?' on':''}"><i></i>${esc(st.label)}</div>
    </div>

    ${/* THE SECOND NAVIGATION. The bottom of a long page is where somebody who
         did not find what they wanted ends up, and this footer had no links in
         it at all. Every department, live, straight to that shelf. */''}
    <div class="sf-cols">
      <div class="sf-col">
        <h5>Shop the shelf</h5>
        <div class="sf-nav">${CATTILES.slice(0,8).map(c=>
          `<button data-cat="${c.k}">${esc(c.n)}</button>`).join('')}</div>
      </div>
      <div class="sf-col">
        <h5>More</h5>
        <div class="sf-nav">${CATTILES.slice(8).map(c=>
          `<button data-cat="${c.k}">${esc(c.n)}</button>`).join('')}</div>
      </div>
    </div>

    <div class="sf-visit">
      <h5>Come by</h5>
      <div class="sf-addr">${STORE.street}<br>${STORE.city}</div>
      ${/* hours as a table with today marked, because the only question hours
             have to answer is "what about today" */''}
      <div class="sf-hrs">${STORE.hours.map(([a,b],i)=>
        `<div class="sf-hr${(new Date().getDay()===0?(i===STORE.hours.length-1):(i===0))?' now':''}"
          ><span>${esc(a)}</span><b>${esc(b)}</b></div>`).join('')}</div>
      <div class="sf-acts">
        <a href="${STORE.phoneHref}">${STORE.phone}</a>
        <a href="${STORE.mapHref}" target="_blank" rel="noopener">Directions</a>
        <a href="${STORE.instagram}" target="_blank" rel="noopener">Instagram</a>
      </div>
    </div>

    <div class="sf-fine">
      <div class="sf-note"><b>Selection and pricing.</b> ${STORE.demoDisclaimer}</div>
      <div class="sf-note"><b>21+ only.</b> Products on this menu contain nicotine or are intended for
        adults 21 and over. Nicotine is an addictive chemical. A valid ID is checked at every pickup.</div>
      <div class="sf-note"><b>Pickup only.</b> We don&rsquo;t ship and we don&rsquo;t deliver, and nothing is
        paid for in the app. You pay at the counter when you collect.</div>
    </div>""")

rep("""  const d = new Date();
  const closes = storeStatus().label.replace('Open until ','').replace('Opens ','');""",
"""  const d = new Date();
  const st = (typeof storeStatus === 'function')
    ? storeStatus() : {open:true, label:'Open today'};""")

# ---- 2. the look -----------------------------------------------------------
rep(""".sf-mark{width:min(66%,208px);margin:0 0 14px;line-height:0;position:relative}""",
"""/* ==== THE FOOTER, REBUILT ====
   One left-aligned column of same-weight blocks with a 208px logo and 180px of
   nothing beside it. Now: a balanced head row, the whole shelf as live links,
   the hours as a table with today marked, and the legal demoted to legal. */
.sf-head{display:flex;align-items:center;justify-content:space-between;gap:12px;
  margin:0 0 18px}
.sf-mark{width:min(46%,150px);margin:0;line-height:0;position:relative;flex:none}
.sf-state{display:inline-flex;align-items:center;gap:7px;flex:none;
  font-family:var(--mono);font-size:10px;letter-spacing:.9px;text-transform:uppercase;
  color:var(--muted);border:1px solid var(--hair);border-radius:99px;padding:6px 11px}
.sf-state i{width:6px;height:6px;border-radius:50%;background:var(--muted);flex:none}
.sf-state.on{color:var(--go-ink);border-color:rgba(255,120,205,.34)}
.sf-state.on i{background:var(--go);box-shadow:0 0 0 3px rgba(255,47,168,.18)}

.sf-cols{display:grid;grid-template-columns:1fr 1fr;gap:16px 14px;
  padding-top:18px;border-top:1px solid var(--hair2)}
.sitefoot h5,.sf-visit h5{font-family:var(--mono);font-size:9.5px;letter-spacing:1.3px;
  text-transform:uppercase;color:var(--faint);margin:0 0 9px}
.sf-nav{display:flex;flex-direction:column;align-items:flex-start;gap:1px}
.sf-nav button{background:none;border:0;padding:7px 0;text-align:left;
  font-family:var(--body-f);font-size:13px;font-weight:600;color:var(--ink2);
  line-height:1.25;min-height:0}
.sf-nav button:active{color:var(--go-ink)}
.sf-nav button:focus-visible{outline:2.5px solid var(--brand);outline-offset:3px;border-radius:4px}

.sf-visit{margin-top:22px;padding-top:18px;border-top:1px solid var(--hair2)}
.sf-addr{font-family:var(--body-f);font-size:13.5px;line-height:1.55;color:var(--ink2)}
.sf-hrs{margin-top:11px;border-radius:12px;border:1px solid var(--hair);overflow:hidden}
.sf-hr{display:flex;justify-content:space-between;gap:10px;padding:9px 12px;
  font-size:12.5px;color:var(--body);border-top:1px solid var(--hair2)}
.sf-hr:first-child{border-top:0}
.sf-hr b{font-family:var(--mono);font-size:11.5px;color:var(--ink2);font-weight:400}
.sf-hr.now{background:rgba(255,47,168,.07)}
.sf-hr.now span{color:var(--go-ink);font-weight:700}
.sf-hr.now b{color:var(--ink)}
.sf-acts{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px}
.sf-acts a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;
  padding:0 6px;border-radius:99px;border:1px solid var(--hair);
  font-family:var(--body-f);font-size:12.5px;font-weight:700;color:var(--ink2);
  text-decoration:none;text-align:center}
.sf-acts a:focus-visible{outline:2.5px solid var(--brand);outline-offset:2px}

.sf-fine{margin-top:22px;padding-top:16px;border-top:1px solid var(--hair2)}
.sf-fine .sf-note{font-size:11px;line-height:1.55;color:var(--faint);margin-top:9px}
.sf-fine .sf-note:first-child{margin-top:0}
.sf-fine .sf-note b{color:var(--muted)}
@media (max-width:344px){ .sf-cols,.sf-acts{grid-template-columns:1fr 1fr} }""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
