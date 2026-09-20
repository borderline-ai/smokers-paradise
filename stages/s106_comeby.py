#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 106 — Come By, which was four facts in a box.
#
# Marco: "There is a screenshot of the Come by section. I think its missing
# detail just like everywhere in the app. The app itself it looks good. But
# when you actually go through all of the different pages like these you find
# half assed ai work. There is clearly an empty space in the square that says
# SMOKERS PARADISE / 922 N Grand Ave Ste B / Nogales, AZ 85621 / 83XC+9G .
# Nogales — On the right you should put our smoker's paradise logo."
#
# He is right about the hole and right about the cause. The address plate is a
# flex column pinned to the left of a 132px band, so the right two thirds of it
# are empty by construction. Nothing was ever going to be there.
#
# What goes in it: the shop's own mark, at the size it can be read, with its
# smoke running. The logo is a woman lighting a cigarette and the smoke is
# already drawn into the artwork; the app's plume picks up where that drawn
# line stops. On the one screen that says COME TO THIS BUILDING, the sign is
# the thing that should be on the wall.
#
# And while the plate is open, the rest of the screen gets the detail it was
# missing — all of it from what the shop has actually told us, none of it
# invented:
#
#   OPEN OR CLOSED, RIGHT NOW. storeStatus() already computes it off
#   STORE.hoursByDay for the bar under the header and the hero sign. The one
#   screen about visiting the shop did not show it. It does now, on the plate,
#   from the same clock, so it can never disagree with the other two.
#
#   WHICH ROW IS TODAY. A table of hours with nothing marked makes a customer
#   work out what day it is before it answers their question. Today's row is
#   now marked and carries the live status.
#
#   THE THINGS A PERSON ASKS BEFORE DRIVING OVER. Pickup only, ID at the door,
#   staff who speak Spanish, and the plus code for the map apps that want one.
#   Every one of these is already stated somewhere else in this app; on the
#   Visit screen they were missing.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the plate: address left, the shop's own sign right ------------------
rep("""function mapArt(){
  return `<span class="addrplate">
    <b>SMOKERS PARADISE</b>
    <i>922 N Grand Ave Ste B</i><i>Nogales, AZ 85621</i>
    <em>83XC+9G &middot; Nogales</em></span>`;
}""",
"""function mapArt(){
  /* The right two thirds of this band were empty because the plate was a flex
     column pinned left. The shop's own mark goes there, at a size it can be
     read, with the plume running off the cigarette the artwork already draws.
     On the screen that asks somebody to drive to a building, the sign on that
     building is the picture. */
  const st = (typeof storeStatus === 'function') ? storeStatus()
           : {open:true, label:'', word:''};
  return `<span class="addrplate">
    <span class="ap-txt">
      <b>SMOKERS PARADISE</b>
      <i>922 N Grand Ave Ste B</i><i>Nogales, AZ 85621</i>
      <em>83XC+9G &middot; Nogales</em>
      <span class="ap-now ${st.open?'ap-open':'ap-shut'}"><i></i>${esc(st.word)}
        <b>${esc(st.label)}</b></span>
    </span>
    <span class="ap-mark">${(typeof markHTML==='function')
      ? markHTML('idle','platemark smokes') : ''}</span>
  </span>`;
}""")

# ---- 2. today's row is marked, and the hours answer the question -----------
rep("""      <div class="sinfo">
        <div class="hrs">${STORE.hours.map(([d,h])=>`<div class="hr"><span>${d}</span><b>${h}</b></div>`).join('')}</div>""",
"""      <div class="sinfo">
        ${/* A table of hours with nothing marked makes a customer work out what
             day it is before it answers their question. Sunday is its own row
             here, so the match is exact rather than a guess at what "Mon - Sat"
             covers. */''}
        <div class="hrs">${STORE.hours.map(([d,h])=>{
          const sun = /sunday/i.test(d), today = (new Date()).getDay()===0;
          const isToday = sun ? today : !today;
          return `<div class="hr${isToday?' today':''}"><span>${d}${
            isToday?'<em>Today</em>':''}</span><b>${h}</b></div>`}).join('')}</div>
        ${/* The four things a person asks before driving over. Every one of
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
        </ul>""", 2)

# ---- 3. the band grows to fit what is now in it ---------------------------
rep(""".storeb .map{height:132px;position:relative;display:block;background:#101418;overflow:hidden}""",
""".storeb .map{height:auto;position:relative;display:block;
  background:#101418;overflow:hidden}""")

# ---- 4. the stylesheet: two columns, a live dot, a marked row --------------
rep("""/* ---- the address plate, where a drawn map used to be ---- */
.addrplate{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;
  gap:2px;width:100%;height:100%;box-sizing:border-box;padding:18px 20px;
  background:linear-gradient(120deg,#1C1029 0%,#2A1739 100%);
  border-radius:12px;border:1px solid var(--edge)}""",
"""/* ---- the address plate, where a drawn map used to be ----
   TWO COLUMNS, because one column in a 132px band leaves two thirds of it
   empty and no amount of type fills that honestly. Address left, the shop's
   own sign right, and the sign is the live one: its smoke runs. */
.addrplate{display:flex;flex-direction:row;align-items:center;justify-content:space-between;
  gap:14px;width:100%;height:auto;min-height:152px;box-sizing:border-box;padding:16px 18px;
  background:
    radial-gradient(120% 140% at 88% 50%, rgba(255,86,190,.16) 0%, transparent 62%),
    linear-gradient(120deg,#1C1029 0%,#2A1739 100%);
  border-radius:12px;border:1px solid var(--edge);overflow:hidden}
.addrplate .ap-txt{display:flex;flex-direction:column;align-items:flex-start;
  justify-content:center;gap:2px;min-width:0;flex:1 1 auto}
.addrplate .ap-txt b{font-size:17px}
.addrplate .ap-mark{flex:0 0 104px;width:104px;display:block;line-height:0;opacity:.97}
.addrplate .ap-mark .hcm{width:100%;max-width:100%}
.addrplate .ap-mark .hcm-img{width:100%;height:auto}
/* Open or closed, right now, from the same clock as the bar and the sign.
   The selectors carry .addrplate because .addrplate b and .addrplate i are
   declared after this block and would otherwise set the status line in 19px
   block caps and knock the shop's name out of the plate. */
.addrplate .ap-now{position:static;display:inline-flex;align-items:center;gap:6px;margin-top:7px;
  font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase;
  color:var(--muted);line-height:1}
.addrplate .ap-now i{width:6px;height:6px;border-radius:99px;background:var(--faint);
  flex:none;font-size:0}
.addrplate .ap-now.ap-open i{background:#6BE28A;box-shadow:0 0 0 3px rgba(107,226,138,.18)}
.addrplate .ap-now.ap-open{color:#9AE9AE}
.addrplate .ap-now b{font-family:var(--mono);font-weight:600;font-size:9px;
  letter-spacing:.6px;color:var(--body);text-transform:none}
@media (max-width:344px){ .addrplate .ap-mark{display:none} }

/* today's row, and the four things people ask before they drive over */
.hrs .hr.today{color:var(--ink)}
.hrs .hr.today b{color:var(--go-ink)}
.hrs .hr.today span em{font-style:normal;font-family:var(--mono);font-size:8.5px;
  letter-spacing:1px;text-transform:uppercase;color:var(--go-ink);
  border:1px solid rgba(255,120,205,.34);border-radius:5px;padding:1px 5px;margin-left:7px}
.sfacts{list-style:none;margin:13px 0 0;padding:12px 0 0;border-top:1px solid var(--hair2);
  display:flex;flex-direction:column;gap:9px}
.sfacts li{display:flex;align-items:flex-start;gap:9px;font-size:12px;line-height:1.4;
  color:var(--body)}
.sfacts li svg{width:15px;height:15px;flex:none;margin-top:1px;stroke:var(--go-ink);
  fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
