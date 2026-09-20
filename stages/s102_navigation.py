#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 102 — 259 items in a pile, and no way out of it.
#
# Marco: "A lot of buttons take us to the shop all but its hard to find what you
# want when you're thrown into a pool of 259 items and have no way to filter
# what you want. We need the categories layed out, and the tool that acts as the
# employee at the shop... That tool should be inside the categories as well. We
# want the whole app to be easy to navigate."
#
# He is describing two different failures that feel like one.
#
# THE FIRST: Shop All is the app's dumping ground. Fourteen controls point at
# it, and it is the one screen with no way to narrow anything. Every category
# shelf has a brand filter, a sort, and sub-groups; Shop All has a sort. So the
# app's most-linked screen is also its least usable, and a customer who presses
# "Shop the shelf" lands in a 259-item scroll with no exit but the back button.
#
# Shop All now opens on the departments. Same filter bar, same chips, same
# counts as every shelf screen, so it reads as part of the app rather than a
# list. One tap and the 259 is 50, with a brand filter and a sort waiting.
#
# THE SECOND, AND THE MORE INTERESTING ONE: "the tool that acts as the employee
# at the shop... a lot of people like to go to the smokeshop because they know
# what to recommend."
#
# Find Your Fit is that person, and it was only reachable from the home screen,
# the search sheet and one Puffco panel. It was NOT on any shelf — which is the
# exact moment a customer needs it, standing in front of fifty disposables
# deciding between them.
#
# It is on every shelf now, under the filters, and it opens ALREADY KNOWING
# which shelf you are on. Pressing it from Disposable Vapes does not ask "what
# are you shopping for?" — it skips straight to the questions that matter for a
# disposable, which is what the person behind the counter does when you are
# already holding one.
#
# Ten of the fifteen shelves have a matcher pool. The other five do not get a
# button that leads to an empty question, they get nothing.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the tool can be opened already knowing the shelf -------------------
rep("""function ffOpen(opener){ ffLoad(); FF.step=0;""",
"""/* `cat` is the shelf the customer pressed it from. Opening the tool from
   Disposable Vapes should not ask which department they want: they are standing
   in it. The category question is skipped and the first real question is the
   one that narrows fifty disposables. */
function ffOpen(opener, cat){ ffLoad(); FF.step=0;
  if(cat && FF_CATS.some(c=>c.k===cat) && ffPool(cat).length){
    if(FF.cat !== cat){ FF.musts=[]; FF.budget=null; FF.families=[];
                        FF.notes=[]; FF.avoid=[]; }
    FF.cat = cat;
    FF.step = 1;
  }""")

# ---- 2. the handler passes the shelf through -------------------------------
rep("""  const ffo=e.target.closest('[data-ffopen]'); if(ffo){ ffOpen(ffo); return }""",
    """  const ffo=e.target.closest('[data-ffopen]'); if(ffo){ ffOpen(ffo, ffo.dataset.ffcat||''); return }""")

# ---- 3. every shelf carries it, and only where it can answer ---------------
rep("""  <div class="activef" id="activeFilters"></div>
  <div class="grid" id="catGrid"></div><div style="height:18px"></div>`;""",
"""  ${ffShelfCTA(cat[0])}
  <div class="activef" id="activeFilters"></div>
  <div class="grid" id="catGrid"></div><div style="height:18px"></div>`;""")

rep("""function paintCat(){""",
"""/* The counter staff, on the shelf itself.

   Find Your Fit was reachable from the home screen, the search sheet and one
   Puffco panel, and from no shelf at all — which is the one moment a customer
   actually needs it, standing in front of fifty disposables trying to choose.
   It is here now, under the filters, and it opens already knowing which shelf
   it was pressed from.

   Only where the matcher has something to work with. A button that leads to an
   empty question is worse than no button. */
function ffShelfCTA(catKey){
  if(typeof FF_CATS === 'undefined' || typeof ffPool !== 'function') return '';
  const spec = FF_CATS.find(c => c.k === catKey);
  if(!spec) return '';
  let n = 0;
  try { n = ffPool(catKey).length } catch(e) { return '' }
  if(n < 4) return '';
  return `<div class="pad" style="margin:2px 0 10px">
    <button class="ffcta inline" data-ffopen="1" data-ffcat="${esc(catKey)}" style="margin:0">
      <span class="ffcta-i"><svg viewBox="0 0 24 24"><path d="M5 7h14M8 12h8M11 17h2"/></svg></span>
      <span class="ffcta-t"><b>Not sure which one?</b><small>Three questions and we narrow this
        shelf to what suits you</small></span>
      <span class="ffcta-a"><svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg></span></button></div>`;
}

function paintCat(){""")

# ---- 4. Shop All opens on the departments ----------------------------------
rep("""    <div class="fl-lab">Sort</div>
    <div class="chips" id="allSorts">${sorts.map(([k,l])=>
      `<button class="chip ${ALLSORT===k?'on':''}" data-allsort="${k}" aria-pressed="${ALLSORT===k}">${l}</button>`).join('')}</div>""",
"""    ${/* THE DEPARTMENTS COME FIRST. Fourteen controls in this app point at
          Shop All, and it was the only screen with nothing to narrow it: every
          category shelf has a brand filter, a sort and sub-groups, and the
          most-linked screen in the app had a sort. One tap here and 259 is 50,
          with a brand filter and a sort already waiting on the other side. */''}
    <div class="filterbar">
      <div class="fl-lab">Departments</div>
      <div class="chips" role="group" aria-label="Jump to a department">
        ${CATS.filter(c=>PRODUCTS.some(p=>p.cat===c[0] && p.published!==false)
                          || c[0]===DISCREET_CAT)
             .map(c=>{
               const n = PRODUCTS.filter(p=>p.cat===c[0] && p.published!==false).length;
               return `<button class="chip" data-cat="${c[0]}">${esc(c[1])}${
                 n?`<em>${n} item${n===1?'':'s'}</em>`:''}</button>`}).join('')}
      </div>
      <div class="fl-lab">Sort</div>
      <div class="chips" id="allSorts">${sorts.map(([k,l])=>
        `<button class="chip ${ALLSORT===k?'on':''}" data-allsort="${k}" aria-pressed="${ALLSORT===k}">${l}</button>`).join('')}</div>
    </div>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
