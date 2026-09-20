#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 156 — the wall you could not see coming.
#
# Five questions instead of one is a better conversation and a worse trap.
# Walked down the water pipe shelf taking the second option at every question:
#
#     Which one are you after?      Straight tube
#     Anything you already go with? GRAV
#     How big do you want it?       Big
#     What joint size?              10 mm
#     What's your budget?           $50 to $74.99
#
#     "Nothing on the shelf meets all of this yet."
#
# Every one of those five answers was a real option, printed with a real count
# next to it, and the combination does not exist. The same walk dead-ends on
# hookah and on disposables. The old tool could not do this to you because it
# only ever asked one question.
#
# The recovery screen is good — it names every answer, it offers the single
# changes that are known to open it back up, it shows the closest thing the shop
# actually carries. But recovery is the wrong place to fix this, because the
# person behind the counter never lets it happen in the first place. Ask them
# for a 10 mm GRAV and they say "not in 10, I've got it in 14" WHILE you are
# asking, not after.
#
# ======================================================================
# EVERY OPTION SAYS WHAT IT LEAVES
# ======================================================================
# So every option on every question now carries the count it would leave GIVEN
# THE ANSWERS ALREADY GIVEN, rather than the count it holds on the shelf:
#
#     before   Straight tube   9 items        <- true of the shelf, and useless
#     after    Straight tube   4 left         <- true of this conversation
#              10 mm           none left      <- and it says so before the tap
#
# An option that would leave nothing is marked, greyed, and says "none left"
# instead of a number. It is still tappable, because a customer is allowed to
# change their mind about an earlier answer and this is a shop, not a form —
# but nobody walks into the wall without seeing it.
#
# ======================================================================
# ONE PLACE THAT KNOWS WHAT AN ANSWER DOES
# ======================================================================
# Doing this needed the count for "what if they tapped this", which means
# applying an answer to a COPY of the state. The click handler knew how to apply
# an answer, in a chain of eleven `else if`s reading the button's value, and
# nothing else could do it. So that chain is lifted out into one function,
# ffApply(state, value), and both the click handler and this new count call it.
# They cannot drift apart, which matters more here than anywhere else in the
# tool: a preview that applied an answer differently from the tap would print a
# number that the next screen then contradicts.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. applying an answer becomes a function, not a click handler ---------
rep("""  const o=e.target.closest('[data-ffpick]');
  if(o){
    const v=o.dataset.ffpick;
    if(FF.step===0){
      /* Answers belong to the category they were given for. Reopening the tool
         restores the session, so picking a different category used to carry the
         old requirements and budget across into a shelf where they made no
         sense, and the search died before the first question. */
      if(FF.cat && FF.cat!==v) ffForget();
      FF.cat=v;
    }
    else if(v.indexOf('fam:')===0) ffToggle(FF.families, v.slice(4), 2);
    else if(ffAsk(v.split(':')[0]) && ffAsk(v.split(':')[0]).opt){
      /* One tap sets it, a second tap on the same answer clears it, so every
         one of these questions can be un-answered without a Skip button. */
      const q = ffAsk(v.split(':')[0]);
      const val = v.slice(q.id.length+1);
      FF[q.field] = (FF[q.field]===val || val==='') ? null : val;
    }
    else if(v.indexOf('must:')===0){
      const k=v.slice(5);
      /* Nothing is both strongly cooled and not cooled at all, so choosing one
         releases the other instead of guaranteeing zero results. */
      if(FF.musts.indexOf(k)<0) FF_EXCLUSIVE.forEach(pair=>{
        if(pair.indexOf(k)>=0) pair.forEach(other=>{
          if(other!==k) FF.musts=FF.musts.filter(m=>m!==other) });
      });
      ffToggle(FF.musts, k, 2);
    }
    else if(v.indexOf('bud:')===0) FF.budget=v.slice(4);
    else if(v.indexOf('part:')===0) FF.part=v.slice(5);
    else if(v.indexOf('joint:')===0) FF.joint=+v.slice(6);
    else if(v.indexOf('gen:')===0) FF.gender=v.slice(4)==='0'?null:v.slice(4);
    ffSave(); ffRender(); return;
  }""",
"""  const o=e.target.closest('[data-ffpick]');
  if(o){ ffApply(FF, o.dataset.ffpick, FF.step===0); ffSave(); ffRender(); return }""")

rep("""function ffStill(){""",
"""/* WHAT AN ANSWER DOES TO A STATE. The one place that knows, so that the tap
   and the "what would this leave" count below can never disagree about it. */
function ffApply(st, v, atStart){
  if(atStart){
    /* Answers belong to the category they were given for. Reopening the tool
       restores the session, so picking a different category used to carry the
       old requirements and budget across into a shelf where they made no
       sense, and the search died before the first question. */
    if(st.cat && st.cat!==v && st===FF) ffForget();
    else if(st.cat && st.cat!==v) Object.keys(FF_ANSWERS).forEach(k=>{
      st[k] = Array.isArray(FF_ANSWERS[k]) ? [] : FF_ANSWERS[k] });
    st.cat=v;
    return st;
  }
  if(v.indexOf('fam:')===0) ffToggle(st.families, v.slice(4), 2);
  else if(ffAsk(v.split(':')[0]) && ffAsk(v.split(':')[0]).opt){
    /* One tap sets it, a second tap on the same answer clears it, so every
       one of these questions can be un-answered without a Skip button. */
    const q = ffAsk(v.split(':')[0]);
    const val = v.slice(q.id.length+1);
    st[q.field] = (st[q.field]===val || val==='') ? null : val;
  }
  else if(v.indexOf('must:')===0){
    const k=v.slice(5);
    /* Nothing is both strongly cooled and not cooled at all, so choosing one
       releases the other instead of guaranteeing zero results. */
    if(st.musts.indexOf(k)<0) FF_EXCLUSIVE.forEach(pair=>{
      if(pair.indexOf(k)>=0) pair.forEach(other=>{
        if(other!==k) st.musts=st.musts.filter(m=>m!==other) });
    });
    ffToggle(st.musts, k, 2);
  }
  else if(v.indexOf('bud:')===0) st.budget=v.slice(4);
  else if(v.indexOf('part:')===0) st.part=v.slice(5);
  else if(v.indexOf('joint:')===0) st.joint=+v.slice(6);
  else if(v.indexOf('gen:')===0) st.gender=v.slice(4)==='0'?null:v.slice(4);
  return st;
}

/* How many PRODUCTS a state leaves standing. Products, not variants, for the
   same reason the line under every question counts products: eleven devices in
   ninety flavours is eleven things to choose between. */
function ffProducts(st){
  if(!st.cat) return 0;
  try{
    const cs = ffConstraints(st);
    const live = ffPool(st.cat).filter(v => cs.every(c => c.test(v)));
    return new Set(live.map(v => (v.product && v.product.id) || v.id)).size;
  }catch(e){ return 0 }
}

/* EVERY OPTION SAYS WHAT IT WOULD LEAVE. Run after the question is drawn: for
   each option, apply it to a copy of the answers so far and count what
   survives. An option that empties the shelf says so before it is tapped
   rather than after. */
function ffAnnotate(){
  const body = $('#ffBody');
  if(!body || FF.step===0 || ffOnResults() || !FF.cat) return;
  const opts = [...body.querySelectorAll('[data-ffpick]')];
  if(!opts.length || opts.length > 14) return;        /* keep the render cheap */
  opts.forEach(el=>{
    let n;
    try{ n = ffProducts(ffApply(ffClone(FF), el.dataset.ffpick, false)) }
    catch(e){ return }
    const sub = el.querySelector('.fftx small');
    if(n===0){
      el.classList.add('ffdead');
      if(sub) sub.textContent = 'none left';
      else el.querySelector('.fftx').insertAdjacentHTML('beforeend','<small>none left</small>');
    } else {
      el.classList.remove('ffdead');
      const t = n + (n===1?' left':' left');
      if(sub) sub.textContent = t;
      else el.querySelector('.fftx').insertAdjacentHTML('beforeend','<small>'+t+'</small>');
    }
  });
}

function ffStill(){""")

rep("""  b.innerHTML=h;
  ffFoot();
}""",
"""  b.innerHTML=h;
  ffAnnotate();
  ffFoot();
}""")

# ---- 2. what a dead end looks like -----------------------------------------
rep(""".ffdisc{""",
""".ffopt.ffdead{opacity:.42}
.ffopt.ffdead .fftx small{color:var(--faint)}
.ffopt.ffdead .ffcheck{opacity:.3}
.ffdisc{""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
