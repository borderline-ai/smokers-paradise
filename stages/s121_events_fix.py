#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 121 — finishing what 120 started, and three things 120 broke.
#
# I shipped 120 and screenshotted it, which is the part I have been skipping.
# Three faults, all mine:
#
#   1. THE BUTTON LOST EVERY LINE OF ITS STYLING. Every rule for that link is
#      written `.give .gbtn`, and 120 removed the `.give` wrapper. So the link
#      rendered as a default blue underlined browser link with a 200px black
#      triangle next to it, because the arrow SVG was sized by `.give .gbtn svg`
#      too. That is exactly the "looks like nobody checked" that Marco keeps
#      pointing at, and it was on screen for one stage only because I looked.
#
#   2. THE MONTH SAID "SUNDAY". I took the first comma-separated piece of
#      'Sunday, April 19', which is the weekday, not the month. The whole point
#      of that label was to stop a September screen claiming a day in April.
#
#   3. THE POSTER WAS BEING CROPPED, by me, in the same week he told me to stop
#      cropping things. It is a 560x747 flyer the shop made: the logo, the date,
#      the address, FREE TACOS, a raffle ticket drawn in the corner. Rendered
#      112px tall with object-fit:cover it was a band of pink with half a word
#      in it.
#
# THE SHAPE, REVISED. The flyer earns its own wide card with the whole poster
# beside the text, because it is the shop's own artwork and it answers every
# question the card would otherwise have to ask. The two events with no artwork
# sit under it as a plain two-up. No horizontal rail: a rail is for a set of
# things you scan across, and there were two.
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
rep("""      ${yearly.length?`
      <div class="ev-lab">Through the year</div>
      <div class="ev-rail">
        ${yearly.map(g=>`
          <div class="ev-year${g.image?' haspic':''}">
            ${g.image?`<span class="ev-pic"><img src="${g.image}" alt="" loading="lazy"
                 onerror="this.closest('.ev-year').classList.remove('haspic'); this.remove()"></span>`:''}
            <span class="ev-body">
              ${/* the month, and the fact that it comes round again, so a
                     September screen never claims a date in April */''}
              <span class="ev-mon">${esc((g.eventType||'').split(',')[0])}</span>
              <b>${esc(g.title)}</b>
              <span class="ev-d">${esc(g.description)}</span>
              ${g.ask?`<span class="ev-ask">${esc(g.ask)}</span>`:''}
              <span class="ev-ann">Every year</span>
            </span>
          </div>`).join('')}
      </div>`:''}
      <a class="gbtn" href="${STORE.instagram}" target="_blank" rel="noopener"
        >Follow us for the next one ${ARROW}</a>`;""",
"""      ${yearly.length?`
      <div class="ev-lab">Through the year</div>
      ${withArt.map(g=>`
        <div class="ev-flyer">
          ${/* THE SHOP'S OWN FLYER, WHOLE.
                560x747 of their artwork with the date, the address and what is
                being given away printed on it. Rendered 112px tall and cropped
                to fill, it was a band of pink. It is contained, on its own
                plate, at the size it can be read at. */''}
          <span class="ev-fpic"><img src="${g.image}" alt="${esc(g.title)} flyer" loading="lazy"
               onerror="this.closest('.ev-flyer').classList.add('nopic'); this.remove()"></span>
          <span class="ev-fbody">
            <span class="ev-mon">${esc(evMonth(g))}</span>
            <b>${esc(g.title)}</b>
            <span class="ev-d">${esc(g.description)}</span>
            ${g.ask?`<span class="ev-ask">${esc(g.ask)}</span>`:''}
            <span class="ev-ann">Every year</span>
          </span>
        </div>`).join('')}
      ${plain.length?`
      <div class="ev-two">
        ${plain.map(g=>`
          <div class="ev-year">
            ${/* the month, and the fact that it comes round again, so a screen
                   in September never claims a date in April */''}
            <span class="ev-mon">${esc(evMonth(g))}</span>
            <b>${esc(g.title)}</b>
            <span class="ev-d">${esc(g.description)}</span>
            ${g.ask?`<span class="ev-ask">${esc(g.ask)}</span>`:''}
            <span class="ev-ann">Every year</span>
          </div>`).join('')}
      </div>`:''}`:''}
      ${/* `.gbtn` is styled only as `.give .gbtn`, and the `.give` wrapper is
             gone, so this carries the app's own button classes instead of a
             class that no longer matches anything. */''}
      <a class="btn neon ev-cta" href="${STORE.instagram}" target="_blank" rel="noopener"
        >Follow us for the next one ${ARROW}</a>`;""")

rep("""      const weekly = GIVEAWAYS.filter(g => /counter/i.test(g.eventType||''));
      const yearly = GIVEAWAYS.filter(g => !/counter/i.test(g.eventType||''));""",
"""      const weekly = GIVEAWAYS.filter(g => /counter/i.test(g.eventType||''));
      const yearly = GIVEAWAYS.filter(g => !/counter/i.test(g.eventType||''));
      /* THE MONTH, NOT THE WEEKDAY. 'Sunday, April 19' split on the comma gives
         'Sunday', which is what shipped and which says nothing about when. Read
         the month out of the string; if there is no month in it, say nothing
         rather than something wrong. */
      const MONTHS = ['January','February','March','April','May','June','July',
                      'August','September','October','November','December'];
      const evMonth = g => {
        const w = g.eventType || '';
        const hit = MONTHS.find(m => w.indexOf(m) >= 0);
        return hit || '';
      };
      const withArt = yearly.filter(g => g.image);
      const plain   = yearly.filter(g => !g.image);""")

# ---- 2. the look -----------------------------------------------------------
rep(""".ev-lab{font-family:var(--mono);font-size:9.5px;letter-spacing:1.3px;text-transform:uppercase;
  color:var(--faint);padding:18px 15px 8px}
.ev-rail{display:flex;gap:11px;overflow-x:auto;padding:0 15px 6px;
  scrollbar-width:none;scroll-snap-type:x proximity}
.ev-rail::-webkit-scrollbar{display:none}
.ev-year{flex:none;width:228px;scroll-snap-align:start;border-radius:15px;overflow:hidden;
  border:1px solid var(--hair);background:var(--card);display:flex;flex-direction:column}
.ev-pic{display:block;height:112px;position:relative;overflow:hidden;background:var(--stage)}
.ev-pic img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ev-body{display:flex;flex-direction:column;padding:12px 13px 13px;gap:3px}
.ev-mon{""",
""".ev-lab{font-family:var(--mono);font-size:9.5px;letter-spacing:1.3px;text-transform:uppercase;
  color:var(--faint);padding:18px 15px 8px}

/* the shop's own flyer, whole, beside the words */
.ev-flyer{display:flex;gap:13px;margin:0 15px;padding:13px;border-radius:16px;
  border:1px solid var(--hair);background:var(--card)}
.ev-fpic{position:relative;flex:none;width:118px;border-radius:11px;overflow:hidden;
  background:var(--stage);align-self:stretch;min-height:158px}
.ev-fpic img{position:absolute;inset:0;width:100%;height:100%;
  object-fit:contain;object-position:center}
.ev-flyer.nopic .ev-fpic{display:none}
.ev-fbody{display:flex;flex-direction:column;gap:3px;min-width:0;padding:2px 0}

/* the two with no artwork, side by side */
.ev-two{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px 15px 0}
.ev-year{border-radius:15px;border:1px solid var(--hair);background:var(--card);
  display:flex;flex-direction:column;padding:13px 13px 14px;gap:3px}
.ev-mon{""")

rep(""".ev-ann{font-family:var(--mono);font-size:8.5px;letter-spacing:1.1px;text-transform:uppercase;
  color:var(--faint);margin-top:9px}
@media (max-width:344px){ .ev-now{grid-template-columns:1fr} }""",
""".ev-ann{font-family:var(--mono);font-size:8.5px;letter-spacing:1.1px;text-transform:uppercase;
  color:var(--faint);margin-top:auto;padding-top:9px}
.ev-cta{margin:16px 15px 0;display:inline-flex}
.ev-cta svg{width:14px;height:14px;flex:none}
@media (max-width:344px){ .ev-now,.ev-two{grid-template-columns:1fr} }""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
