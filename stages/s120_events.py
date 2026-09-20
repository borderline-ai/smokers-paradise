#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 120 — Events and Raffles, which nobody would read.
#
# Marco pasted the whole section back at me and said: "That area is very
# undeveloped and it just doesn't look good. Its not something a customer would
# actually willingly read through."
#
# He is right, and here is what it actually was: five identical blocks stacked
# down the screen, each one an eyebrow, a big headline, two lines of copy and a
# pill. 1,025 pixels of text with no picture, no hierarchy and no reason to
# start reading. Everything was the same size, so nothing was important.
#
# And underneath the layout, a credibility problem he did not name but the shop
# owner will: on a demo shown on 18 September it advertised
#
#     SUNDAY, APRIL 19    Spring Celebration Fest
#     DECEMBER 8 TO 20    Toy Drive
#     JANUARY, IN OUR LOT Car meet
#
# as though they were coming up. Three of the five things in the section had
# already happened or were months away, presented in the present tense. A shop
# owner reads that as an app that does not know what day it is.
#
# THE REDESIGN, and the thinking is the same thinking the shop uses:
#
#   THERE ARE TWO KINDS OF THING HERE and they were mixed together. Two of them
#   happen every week at the counter and are a reason to come in TODAY. Three
#   of them happen once a year. Those are not the same kind of information and
#   should not be the same kind of card.
#
#   WHAT IS ON NOW LEADS, as two side-by-side cards with the one number that
#   matters set large — spend $10, spend $15 — because that is the whole offer
#   and it was previously buried in a pill at the bottom of a paragraph.
#
#   THE ANNUAL ONES BECOME A RAIL, dated by month and marked EVERY YEAR, so
#   nothing claims to be happening on a Sunday that has gone. The Spring Fest
#   keeps its photograph, which the shop supplied and which was being rendered
#   nowhere.
#
#   AND IT IS ONE SCREEN, not four. A horizontal rail is how the rest of this
#   app already shows a set of things, so the section stops being the one part
#   of the page you have to scroll through rather than across.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


rep("""    ${secHead('In the Shop','','Events and raffles')}
    <div class="give">
      ${/* One link at the foot of the section rather than one under every
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
    </div>""",
"""    ${secHead('In the Shop','','Events and raffles')}
    ${(()=>{
      /* TWO KINDS OF THING, PREVIOUSLY STACKED AS ONE.
         Two of these happen every week at the counter and are a reason to come
         in today. Three happen once a year. Rendering them as five identical
         blocks made the weekly ones invisible and made the annual ones read as
         though they were this weekend — on 18 September the section was
         advertising a Sunday in April. */
      const weekly = GIVEAWAYS.filter(g => /counter/i.test(g.eventType||''));
      const yearly = GIVEAWAYS.filter(g => !/counter/i.test(g.eventType||''));
      /* the one number that is the whole offer, pulled out of the sentence */
      const spend = g => { const m = (g.ask||'').match(/\\$\\s?(\\d+)/); return m ? '$'+m[1] : '' };
      const when  = g => (g.ask||'').replace(/Spend \\$\\s?\\d+\\.?/i,'').replace(/^[\\s.]+/,'').trim();
      return `
      <div class="ev-now">
        ${weekly.map(g=>`
          <div class="ev-card">
            <span class="ev-tag">Every week</span>
            <h3>${esc(g.title)}</h3>
            ${spend(g)?`<b class="ev-num">${spend(g)}</b><span class="ev-sub">or more</span>`:''}
            <p>${esc(g.description)}</p>
            ${when(g)?`<span class="ev-when">${esc(when(g))}</span>`:''}
          </div>`).join('')}
      </div>
      ${yearly.length?`
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
        >Follow us for the next one ${ARROW}</a>`;
    })()}""")

# ---- the look ---------------------------------------------------------------
rep(""".gr-sum b{font-size:40px;line-height:1}
""",
""".gr-sum b{font-size:40px;line-height:1}

/* ---- EVENTS AND RAFFLES ----
   Two things happen every week and three happen once a year, and they were
   five identical text blocks down a screen. The weekly ones lead, because they
   are a reason to come in today, with the one number that is the whole offer
   set large. The annual ones are a rail, dated by month and marked EVERY YEAR,
   so a screen in September never advertises a Sunday in April. */
.ev-now{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 15px;margin-top:4px}
.ev-card{position:relative;border-radius:16px;padding:14px 13px 15px;
  background:
    radial-gradient(120% 90% at 84% 0%, rgba(255,86,190,.16) 0%, transparent 62%),
    linear-gradient(170deg,#241533 0%,#180E24 100%);
  border:1px solid rgba(255,120,205,.20);display:flex;flex-direction:column}
.ev-tag{font-family:var(--mono);font-size:8.5px;letter-spacing:1.2px;text-transform:uppercase;
  color:var(--go-ink);border:1px solid rgba(255,120,205,.32);border-radius:99px;
  padding:2px 7px;align-self:flex-start}
.ev-card h3{font-family:var(--disp);font-weight:800;font-size:17px;letter-spacing:-.03em;
  margin:9px 0 0;line-height:1.1;color:var(--ink)}
.ev-num{font-family:var(--disp);font-weight:800;font-size:34px;line-height:1;
  letter-spacing:-.04em;color:var(--go-ink);margin-top:8px;display:block}
.ev-sub{font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase;
  color:var(--faint);margin-top:2px}
.ev-card p{font-size:11.5px;line-height:1.42;color:var(--body);margin:9px 0 0}
.ev-when{font-family:var(--mono);font-size:9.5px;letter-spacing:.4px;color:var(--ink2);
  margin-top:auto;padding-top:10px}
.ev-lab{font-family:var(--mono);font-size:9.5px;letter-spacing:1.3px;text-transform:uppercase;
  color:var(--faint);padding:18px 15px 8px}
.ev-rail{display:flex;gap:11px;overflow-x:auto;padding:0 15px 6px;
  scrollbar-width:none;scroll-snap-type:x proximity}
.ev-rail::-webkit-scrollbar{display:none}
.ev-year{flex:none;width:228px;scroll-snap-align:start;border-radius:15px;overflow:hidden;
  border:1px solid var(--hair);background:var(--card);display:flex;flex-direction:column}
.ev-pic{display:block;height:112px;position:relative;overflow:hidden;background:var(--stage)}
.ev-pic img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ev-body{display:flex;flex-direction:column;padding:12px 13px 13px;gap:3px}
.ev-mon{font-family:var(--mono);font-size:9px;letter-spacing:1.2px;text-transform:uppercase;
  color:var(--go-ink)}
.ev-year b{font-family:var(--disp);font-weight:800;font-size:15.5px;letter-spacing:-.03em;
  line-height:1.15;color:var(--ink);margin-top:2px}
.ev-d{font-size:11.5px;line-height:1.42;color:var(--body);margin-top:4px}
.ev-ask{font-family:var(--mono);font-size:9.5px;color:var(--ink2);margin-top:7px}
.ev-ann{font-family:var(--mono);font-size:8.5px;letter-spacing:1.1px;text-transform:uppercase;
  color:var(--faint);margin-top:9px}
@media (max-width:344px){ .ev-now{grid-template-columns:1fr} }
""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
