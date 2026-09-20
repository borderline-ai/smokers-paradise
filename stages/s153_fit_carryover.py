#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 153 — two faults the new questions exposed.
#
# 1. ANSWERS CARRIED ACROSS SHELVES.
#    Find Your Fit remembers a session, which is right: half-answer it, look at
#    something, come back and it is where you left it. When the shelf CHANGES it
#    has to forget, because a 10 mm joint is not a thing you can want from the
#    pouch shelf. That forgetting was written out by hand as a list of fields:
#
#        FF.musts=[]; FF.budget=null; FF.families=[]; FF.notes=[]; FF.avoid=[];
#
#    and stage 151 added four more answers (brand, size, material, strength)
#    that the list does not name. So picking Diamond Glass on the water pipe
#    shelf and then opening the tool on Hookah carried Diamond Glass into a
#    shelf that has never stocked it, and the tool answered "nothing matches"
#    for a reason the customer could not see and had not chosen.
#
#    The list of fields is the bug. What the tool keeps between shelves is the
#    step it is on and nothing else, so it is written that way: everything that
#    is an ANSWER is cleared by naming the answers once, in one place, and both
#    of the places that need to forget call it.
#
# 2. A CRASH BEHIND A STALE SESSION.
#    findFit's early exit, for a category it cannot recognise, returns an object
#    missing the `summary` field that the no-results screen reads:
#
#        if(!spec) return {matches:[], total:0, excluded:[], relax:[], closest:[], pool:0};
#        ...
#        const asked = r.summary.length ? ... : '';     <- throws
#
#    Reachable in one step: a session restored with a step number but no
#    category — which is exactly what a stored session from an older build
#    looks like — renders the results screen with no category and the tool dies
#    with a white panel instead of asking the first question. One field.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. one place that knows what an answer is -----------------------------
rep("""function ffOpen(opener, cat){ ffLoad(); FF.step=0;
  if(cat && FF_CATS.some(c=>c.k===cat) && ffPool(cat).length){
    if(FF.cat !== cat){ FF.musts=[]; FF.budget=null; FF.families=[];
                        FF.notes=[]; FF.avoid=[]; }""",
"""/* EVERY ANSWER, NAMED ONCE. Anywhere the shelf changes, the answers go with
   it — and a question added later is forgotten correctly the day it is added,
   because it is added to this one list rather than to three hand-written
   copies of it. */
const FF_ANSWERS = {families:[], notes:[], avoid:[], musts:[],
  budget:null, joint:null, gender:null, part:null, use:null,
  brand:null, size:null, mat:null, nicstr:null};
function ffForget(){
  Object.keys(FF_ANSWERS).forEach(k=>{
    FF[k] = Array.isArray(FF_ANSWERS[k]) ? [] : FF_ANSWERS[k];
  });
}

function ffOpen(opener, cat){ ffLoad(); FF.step=0;
  if(cat && FF_CATS.some(c=>c.k===cat) && ffPool(cat).length){
    if(FF.cat !== cat) ffForget();""")

rep("""      if(FF.cat && FF.cat!==v){
        FF.families=[]; FF.notes=[]; FF.avoid=[]; FF.musts=[];
        FF.budget=null; FF.joint=null; FF.gender=null; FF.part=null;
        FF.brand=null; FF.size=null; FF.mat=null; FF.nicstr=null;
      }""",
"""      if(FF.cat && FF.cat!==v) ffForget();""")

rep("""function ffRestart(){ FF={step:0,cat:null,families:[],notes:[],avoid:[],musts:[],budget:null,
  joint:null,gender:null,part:null,use:null,brand:null,size:null,mat:null,nicstr:null};
  ffSave(); ffRender(); }""",
"""function ffRestart(){ FF={step:0,cat:null}; ffForget(); ffSave(); ffRender(); }""")

# ---- 2. the early exit answers the same shape as the real one --------------
rep("""  if(!spec) return {matches:[], total:0, excluded:[], relax:[], closest:[], pool:0};""",
"""  /* The same shape as a real result, `summary` included: the no-results screen
     reads it, and a session restored with a step but no category used to reach
     this line and take the whole panel down with it. */
  if(!spec) return {matches:[], total:0, excluded:[], relax:[], closest:[],
    pool:0, summary:[]};""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
