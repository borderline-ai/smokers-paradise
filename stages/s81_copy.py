#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 81 — the things that read like a template rather than like this shop.
#
# 1. THE WHEEL RUNS MONDAY TO WEDNESDAY. The app says "spend $15 or more and
#    spin the prize wheel at the counter" with no days on it, in three places.
#    Somebody reads that on a Saturday, spends fifteen dollars for the spin, and
#    finds out at the counter. An offer that is wrong about when it runs is
#    worse than no offer, because the customer has already acted on it.
#
# 2. FIVE EVENTS, FIVE IDENTICAL BUTTONS. The shop's five things each ended
#    with the same "Follow us for the next one" link to the same Instagram
#    page. Stacked down one screen it is the tell that a list was rendered
#    rather than written. They also want different things from you: the fest is
#    a date, the raffle is ten dollars, the wheel is fifteen dollars on three
#    days, the toy drive is a toy, the meet is a date. So each one now says what
#    it actually asks of you, and the follow link goes once, at the foot of the
#    section, where it belongs.
#
# 3. "NEW-GENERATION FAVORITES" and "EXPLORE THE COLLECTION". Nobody behind
#    this counter has ever said either sentence. They were also sitting over
#    the same three TRĒ House bars that appear again forty pixels further down
#    under "Exotic Snacks", so the home screen showed one rail twice and named
#    it something nobody would say. It says what it is.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


# ---- 1. the wheel has days -------------------------------------------------
rep("     d:'Spend $15 or more and spin the prize wheel at the counter.', src:''},",
    "     d:'Monday to Wednesday. Spend $15 or more and spin the prize wheel at '\n"
    "       + 'the counter.', src:''},")
rep("    subtitle:'Spend $15 or more and spin the prize wheel at the counter.',",
    "    subtitle:'Monday to Wednesday. Spend $15 or more and spin the wheel at the counter.',")

for old, new in [
    ("Spend $15+ and spin the prize wheel", "Mon to Wed: spend $15+ and spin the wheel"),
    ("In store only. One spin per visit.", "Monday to Wednesday, in store. One spin per visit."),
]:
    if s.count(old):
        s = s.replace(old, new)
        print('  ok: %s' % old[:50])

# ---- 2. the events read as five different things ---------------------------
rep("""      ${GIVEAWAYS.map(g=>`
        <div class="eye">${g.eventType||'Giveaway'}</div>
        <h3>${esc(g.title)}</h3><p>${esc(g.description)}</p>
        ${g.image?`<div class="gcard"><div class="gth"><img src="${g.image}" alt="${esc(g.title)}"></div>
          <div><b>How to enter</b><small>${esc(g.entryInstructions)}</small></div></div>`:''}
        <a class="gbtn" href="${g.instagramUrl}" target="_blank" rel="noopener">Follow us for the next one ${ARROW}</a>`).join('')}
    </div>
  </div>`:''}""",
"""      ${/* One link at the foot of the section rather than one under every
             item. Five identical buttons down a screen is the thing that makes
             a hand-written list look generated. */''}
      ${GIVEAWAYS.map(g=>`
        <div class="gitem">
          <div class="eye">${esc(g.eventType||'In the shop')}</div>
          <h3>${esc(g.title)}</h3><p>${esc(g.description)}</p>
          ${g.ask?`<span class="gask">${esc(g.ask)}</span>`:''}
        </div>`).join('')}
      <a class="gbtn" href="${STORE.instagram}" target="_blank" rel="noopener"
        >Follow us for the next one ${ARROW}</a>
    </div>
  </div>`:''}""")

rep("""const GIVEAWAYS = STORE_CONTENT.community.map((c,i)=>({
  id:'g'+i, title:c.t, description:c.d, image:c.src||'', eventType:c.when,
  entryInstructions:'', instagramUrl:STORE.instagram,
  active:true, featured:i===0, status:'in-store'
}));""",
"""/* Each of these wants something different from you: a date, ten dollars, a
   toy. The one-line ask is what makes the list read as five things the shop
   runs rather than five rows of the same component. */
const EVENT_ASK = {
  'Spring Celebration Fest': 'Free entry. A raffle ticket at the door.',
  'Raffles':                 'Spend $10. One entry per visit.',
  'Spin-N-Win':              'Monday to Wednesday. Spend $15.',
  'Toy Drive':               'Bring a toy. Free keychain with any purchase.',
  'Car meet':                'Free. Bring the car, or just come through.'
};
const GIVEAWAYS = STORE_CONTENT.community.map((c,i)=>({
  id:'g'+i, title:c.t, description:c.d, image:c.src||'', eventType:c.when,
  ask: EVENT_ASK[c.t] || '',
  entryInstructions:'', instagramUrl:STORE.instagram,
  active:true, featured:i===0, status:'in-store'
}));""")

rep(".burger{flex-direction:column;gap:4px}",
    "/* An item in the events list, and the single line that says what it asks\n"
    "   of you. The ask is set apart from the description because it is the part\n"
    "   somebody has to act on. */\n"
    ".gitem{padding:14px 0;border-bottom:1px solid var(--edge)}\n"
    ".gitem:last-of-type{border-bottom:0}\n"
    ".gask{display:inline-block;margin-top:9px;font-family:var(--mono);font-size:11px;\n"
    "  letter-spacing:.04em;color:var(--brand);background:var(--panel-2);\n"
    "  border:1px solid var(--edge);border-radius:var(--rpill);padding:5px 11px}\n"
    ".burger{flex-direction:column;gap:4px}")

# ---- 3. the rail says what it is -------------------------------------------
rep("  ${famous.length?railSec('New-Generation Favorites',",
    "  ${famous.length?railSec('Mushroom Chocolate',")

for old, new in [
    ("'Explore the collection'", "'See the shelf'"),
    ('"Explore the collection"', '"See the shelf"'),
    (">Explore the collection<", ">See the shelf<"),
]:
    if s.count(old):
        s = s.replace(old, new)
        print('  ok: %s' % old)

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
