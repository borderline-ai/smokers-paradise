#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 151 — Find Your Fit asks what the person behind the counter asks.
#
# Marco: "the tool to find your fit just sucks and we have been over it a lot of
# times. I want this to resemble the worker that guides you to what you want and
# need. They ask you things like what flavors what brands etc, and they dont just
# ask for vapes, they ask what they want, they recommend what is best depending
# on what they want and like, theres a ton of things."
#
# He is right, and the measurement makes it obvious. Here is every question the
# tool asked before this stage, by shelf:
#
#     Disposable Vapes    flavor direction, flavors, what matters    3
#     Dab Device          what matters, budget                       2
#     Glass Part          part, joint size, connection               3
#     Water Pipe          budget                                     1
#     Dab Rig             budget                                     1
#     Hand Pipe           budget                                     1
#     Rolling Setup       budget                                     1
#     Hookah              budget                                     1
#     Nicotine Pouches    budget                                     1
#     Cleaning & Access.  budget                                     1
#
# Seven of the ten shelves asked ONE question, and that question was money. That
# is not a worker guiding you, it is a price filter with a friendly headline. Ask
# someone at Smoker's Paradise for a hookah and the first thing out of their
# mouth is not "what's your budget".
#
# ======================================================================
# WHAT THE SHELF COULD ALREADY ANSWER, AND NOBODY ASKED
# ======================================================================
# None of this needed new data. It was all sitting in the catalogue:
#
#     brand           every product has one, 8 brands on the vape shelf alone
#     flavor          58 of 62 hookah items, 18 of 24 rolling, 12 of 25 pouches
#                     — the flavor questions were hard-coded to disposables
#     joint size      44 of 58 water pipes, 24 of 32 rigs
#                     — the joint question was hard-coded to glass parts
#     part type       Grinder / Tray / Cleaner / Torch / Storage on the gear
#                     shelf, Hookah / Bowl / Coals / Shisha on the hookah shelf
#                     — the part question was hard-coded to glass parts
#     size class      compact / standard / large across all the glass
#     material        silicone vs glass across all the glass
#     nicotine        3 mg vs 6 mg vs 9 mg on the pouch shelf
#
# So the three questions that already existed are unlocked for every shelf that
# can answer them, and five more are added. Asking a hookah shopper what flavor
# shisha they smoke is the single most obvious question in the shop and it was
# not being asked because the flavor code said `ffPool('disp')`.
#
# ======================================================================
# THE RULE THAT DECIDES WHETHER A QUESTION GETS ASKED
# ======================================================================
# A worker does not ask a question they cannot act on. Neither does this. Every
# question is offered only when the shelf genuinely holds different answers to
# it:
#
#     at least two options survive,
#     each surviving option covers at least 12% of the shelf,
#     and together they account for at least 45% of it.
#
# The last clause is the one that matters for honesty. Eleven of eighty dab
# products publish a battery and twenty four publish a joint size, so "torch or
# plug-in" can only speak for 44% of that shelf — and a question that would
# silently drop more than half the shelf as "unknown" is not asked at all,
# rather than asked and quietly wrong. Every threshold is measured against the
# live catalogue on every run, so a shelf that grows into a question starts
# getting it without anybody editing this file.
#
# ======================================================================
# BRAND, AND THE ONE THING IT IS NOT
# ======================================================================
# "What do you usually smoke" is a real question and its real answer is a brand.
# It is offered with each brand's true count and a "no preference" option that
# is genuinely no filter. What it is NOT is a way to bury the rest of the shelf:
# picking Geek Bar filters to Geek Bar, and the result screen still says how many
# it set aside and offers to widen it in one tap.
#
# Along the way: the pouch shelf had ZYN under two spellings, "Zyn" on three
# products and "ZYN" on two, so the brand question would have offered the same
# brand twice with split counts. Normalised to the wordmark ZYN.
#
# ======================================================================
# FIVE QUESTIONS, NOT THREE
# ======================================================================
# The cap goes from three to five, in the order a counter conversation actually
# runs: what kind of thing, then flavor, then brand, then how it has to be, then
# money last. Every question after the first is skippable, and the running count
# of what still matches is on every screen as it already was.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 0. one brand, one spelling -------------------------------------------
# The pouch shelf carries ZYN under two spellings, "Zyn" on three products and
# "ZYN" on two, so the brand question would offer the same brand twice with its
# count split in half. The DATA is left exactly as it is, because the published
# specification table is keyed on the spelling the product record carries and
# renaming the brand would orphan three products' specs. Instead the brand
# question folds spellings together, and the label map says how it is written.
rep("""const BRAND_LABEL = {'TRE House': 'TR\\u0112 House'}""",
    """const BRAND_LABEL = {'TRE House': 'TR\\u0112 House', 'Zyn': 'ZYN'}""")

# ---- 1. the question bank --------------------------------------------------
rep("""function ffSteps(cat){""",
"""/* ======================================================================
   THE QUESTION BANK
   Each question knows four things: what to call itself, what options the
   CURRENT shelf can offer for it, what constraint an answer imposes, and
   where the answer lives on the state object. Nothing here is hard-coded to
   a shelf; the shelf decides what it can answer by what it holds.
   ====================================================================== */
/* WHEN IS A QUESTION WORTH ASKING. Not one rule, because the questions are not
   one shape. "Which kind of thing" is a long tail — twelve kinds of accessory,
   none of them a majority — and demanding that the options cover half the shelf
   would delete the most useful question in the shop. "Glass or silicone" is a
   split, and a split that only speaks for a third of the shelf is a question
   that quietly bins the other two thirds.

   by      what a count means: 'prod' counts products, 'var' counts every
           flavour and colourway. A brand with one device and forty-eight
           flavours is one thing on the shelf, not forty-eight.
   share   the least of the shelf an option can hold and still be offered
   opts    how many options have to survive before the question is asked
   cover   how much of the shelf the survivors have to speak for
   all     an option that imposes nothing, for a tail this question cannot name */
const FF_GATE = {
  brand:  {by:'prod', share:0.05, opts:3, cover:0.50, max:8, all:'No preference'},
  part:   {by:'prod', share:0.00, opts:3, cover:0.00, max:8, all:'Not sure yet'},
  size:   {by:'var',  share:0.12, opts:2, cover:0.45},
  mat:    {by:'var',  share:0.12, opts:2, cover:0.45},
  nicstr: {by:'prod', share:0.10, opts:2, cover:0.40},
  joint:  {by:'var',  share:0.08, opts:2, cover:0.45},
  gender: {by:'var',  share:0.10, opts:2, cover:0.40}
};

/* WHICH QUESTIONS SURVIVE THE CAP. Five is the most anyone will answer, and a
   shelf can now offer seven, so the ones that change the answer most win. Fit
   beats taste beats brand beats money: a 14 mm bowl on an 18 mm joint is not a
   preference, it is a part that does not go on, so the joint question outranks
   everything except knowing which part it is. */
const FF_RANK = {part:10, joint:9, gender:9, fam:8, note:7, must:6,
                 brand:5, size:4, nicstr:4, mat:3, budget:0};

/* Pull a comparable value out of a variant for a given question, or null when
   the product does not publish it. null always means "cannot answer", never
   "no" — a product with no published material is not silicone. */
const FF_VAL = {
  /* folded, so "Zyn" and "ZYN" are one brand with one count */
  brand:  v => v.product.brand ? String(v.product.brand).toLowerCase() : null,
  size:   v => known(v.attrs.sizeClass) ? v.attrs.sizeClass.value : null,
  mat:    v => {
    if(!known(v.attrs.material)) return null;
    const m = String(v.attrs.material.value).toLowerCase();
    if(m.indexOf('silicone') >= 0) return 'silicone';
    if(m.indexOf('glass') >= 0 || m.indexOf('borosilicate') >= 0) return 'glass';
    return null;                                   /* steel, ceramic, nylon  */
  },
  nicstr: v => {
    if(!known(v.attrs.nicotineStrength)) return null;
    const m = String(v.attrs.nicotineStrength.value).match(/(\\d+(?:\\.\\d+)?)\\s*mg/i);
    return m ? m[1] + ' mg' : null;
  },
  part:   v => known(v.attrs.partType) ? v.attrs.partType.value
             : (known(v.attrs.deviceType) ? v.attrs.deviceType.value : null),
  joint:  v => known(v.attrs.jointSize) ? String(v.attrs.jointSize.value) : null,
  gender: v => known(v.attrs.jointGender) ? v.attrs.jointGender.value : null
};

/* How a raw value is said out loud, and the line under it. A size class is
   "compact" in the data and "small enough to put away" at the counter. */
const FF_SAY = {
  size:   {compact:['Small', 'Easy to put away or take with you'],
           standard:['Normal size', 'The usual shelf size'],
           large:['Big', 'A piece that lives on the table']},
  mat:    {silicone:['Silicone', 'Will not break if it goes over'],
           glass:['Glass', 'For the taste and the look']}
};

const FF_ASK = [
  /* ---- what kind of thing, first, the way it is asked out loud ---------- */
  {id:'part', field:'part', title:'Which one are you after?',
   sub:'Pick the kind of thing, or skip it and we will show you the lot.',
   opt:(cat)=>ffTally(cat,'part')
     .map(o=>({v:o.v, label:o.v, n:o.n, prod:o.prod}))
     /* The kinds a shelf publishes never add up to the whole shelf, so this
        question always carries a way through that hides nothing. */
     .concat([{v:'', label:'Not sure yet', sub:'Show me everything', n:0}]),
   con:(st)=>!st.part ? null : {code:'part', label:'A '+st.part.toLowerCase(),
     short:st.part.toLowerCase(), drop:'Show every kind',
     test:v => String(FF_VAL.part(v)||'').toLowerCase().indexOf(st.part.toLowerCase())>=0,
     clear:s2 => { s2.part=null }}},

  /* ---- flavor, on EVERY shelf that has flavors, not only disposables ---- */
  {id:'fam'},                                  /* bespoke UI, kept as it was */
  {id:'note'},                                 /* bespoke UI, kept as it was */

  /* ---- what do you usually smoke ---------------------------------------- */
  {id:'brand', field:'brand', title:'Anything you already go with?',
   sub:'Pick a brand you stick to, or skip it and we will show you everything.',
   opt:(cat)=>{
     const t = ffTally(cat,'brand');
     if(!t.length) return [];
     return t.map(o=>({v:o.v, label:brandLabel(ffBrandSpelling(cat,o.v)),
       n:o.n, prod:o.prod}))
       .concat([{v:'', label:'No preference', sub:'Show me everything', n:0}]);
   },
   con:(st)=>!st.brand ? null : {code:'brand',
     label:'The brand '+brandLabel(ffBrandSpelling(st.cat, st.brand)),
     short:brandLabel(ffBrandSpelling(st.cat, st.brand)), drop:'Show every brand',
     test:v => FF_VAL.brand(v) === st.brand,
     clear:s2 => { s2.brand=null }}},

  /* ---- how it has to be -------------------------------------------------- */
  {id:'must'},                                 /* bespoke UI, kept as it was */

  {id:'size', field:'size', title:'How big do you want it?',
   sub:'Measured from the published height or capacity, not guessed.',
   opt:(cat)=>ffTally(cat,'size').map(o=>({v:o.v,
     label:(FF_SAY.size[o.v]||[o.v])[0], sub:(FF_SAY.size[o.v]||[])[1], n:o.n})),
   con:(st)=>!st.size ? null : {code:'size',
     label:'The '+((FF_SAY.size[st.size]||[st.size])[0]).toLowerCase()+' size',
     short:(FF_SAY.size[st.size]||[st.size])[0].toLowerCase(), drop:'Show every size',
     test:v => FF_VAL.size(v)===st.size,
     clear:s2 => { s2.size=null }}},

  {id:'mat', field:'mat', title:'Glass or silicone?',
   sub:'Both are on the shelf. It changes how it feels and what happens if it falls.',
   opt:(cat)=>ffTally(cat,'mat').map(o=>({v:o.v,
     label:(FF_SAY.mat[o.v]||[o.v])[0], sub:(FF_SAY.mat[o.v]||[])[1], n:o.n})),
   con:(st)=>!st.mat ? null : {code:'mat', label:st.mat==='silicone'?'Silicone':'Glass',
     short:st.mat, drop:'Show glass and silicone',
     test:v => FF_VAL.mat(v)===st.mat,
     clear:s2 => { s2.mat=null }}},

  {id:'nicstr', field:'nicstr', title:'How strong?',
   sub:'The strength the maker prints on the tin.',
   opt:(cat)=>ffTally(cat,'nicstr')
     .sort((a,b)=>parseFloat(a.v)-parseFloat(b.v))
     .map(o=>({v:o.v, label:o.v, n:o.n})),
   con:(st)=>!st.nicstr ? null : {code:'nicstr', label:st.nicstr,
     short:st.nicstr, drop:'Show every strength',
     test:v => FF_VAL.nicstr(v)===st.nicstr,
     clear:s2 => { s2.nicstr=null }}},

  {id:'joint'},                                /* bespoke UI, kept as it was */
  {id:'gender'},                               /* bespoke UI, kept as it was */

  /* ---- money last, the way it comes up last at the counter -------------- */
  {id:'budget'}
];
const ffAsk = id => FF_ASK.find(q=>q.id===id);

/* Which spelling of a folded brand the shop actually writes: the one on the
   most products, and BRAND_LABEL has the last word where a wordmark differs
   from what the catalogue happens to carry. */
function ffBrandSpelling(cat, folded){
  const seen = {};
  ffPool(cat).forEach(v=>{
    const b = v.product.brand;
    if(b && String(b).toLowerCase()===folded) seen[b] = (seen[b]||0)+1;
  });
  const keys = Object.keys(seen);
  if(!keys.length) return folded;
  return keys.sort((a,b)=>seen[b]-seen[a])[0];
}

/* Count the shelf by one question's values, keeping only options that carry
   their weight, and report how much of the shelf the survivors speak for. */
function ffTally(cat, key){
  const pool = ffPool(cat);
  const g = FF_GATE[key];
  if(!pool.length || !g) return [];
  const by = {};
  pool.forEach(v=>{
    const val = FF_VAL[key] ? FF_VAL[key](v) : null;
    if(val===null || val===undefined || val==='') return;
    by[val] = by[val] || {v:val, n:0, ids:new Set()};
    by[val].n++;
    by[val].ids.add(v.product.id);
  });
  const rows = Object.values(by).map(o=>({v:o.v, n:o.n, prod:o.ids.size}));
  const size = g.by==='prod' ? new Set(pool.map(v=>v.product.id)).size : pool.length;
  const cnt  = o => g.by==='prod' ? o.prod : o.n;
  const min  = Math.max(1, Math.floor(size * g.share));
  const keep = rows.filter(o=>cnt(o)>=min).sort((a,b)=>cnt(b)-cnt(a));
  const covered = keep.reduce((a,o)=>a+cnt(o),0);
  if(keep.length < g.opts || covered < size * g.cover) return [];
  return keep.slice(0, g.max || 99);
}

/* ---------- which questions this shelf can actually answer ---------- */
function ffSteps(cat){""")

# ---- 2. the new step builder ----------------------------------------------
old_steps = """  if(!cat) return [];
  const st=[];
  const banded = () => Object.keys(ffBudgetBands(cat)).length>1;
  if(cat==='disp'){
    const fams=new Set();
    ffPool('disp').forEach(v=>{ if(v.flavor) v.flavor.flavorFamilies.forEach(f=>fams.add(f)) });
    if(fams.size>=2) st.push('fam');
    if(ffAvailableNotes(cat).length>=2) st.push('note');
    if(ffRuleAvailability('disp',['longer','smaller','cooled','uncooled','cheap','recharge','nicfree']).length) st.push('must');
  } else if(cat==='dab'){
    if(ffRuleAvailability('dab',['battery','portable','water','tempctl']).length) st.push('must');
    if(banded()) st.push('budget');
  } else if(cat==='parts'){
    if(ffDistinct('parts', v=>v.attrs.partType.value)>=2) st.push('part');
    if(ffDistinct('parts', v=>known(v.attrs.jointSize)?v.attrs.jointSize.value:null)>=2) st.push('joint');
    if(ffDistinct('parts', v=>known(v.attrs.jointGender)?v.attrs.jointGender.value:null)>=2) st.push('gender');
    if(!st.length && banded()) st.push('budget');
  } else {
    if(banded()) st.push('budget');
  }
  return st.slice(0,3);
}"""
new_steps = """  if(!cat) return [];
  const st=[];
  const pool = ffPool(cat);
  if(!pool.length) return [];

  /* A shelf answers a question or it does not. Nothing below names a category:
     the hookah shelf gets the flavor questions because 58 of its 62 items
     publish a flavor, and the pouch shelf gets the strength question because
     its tins print 3 mg and 6 mg. The same code asks a shelf that grows into a
     question without anyone editing it. */
  const fams = new Set();
  pool.forEach(v=>{ if(v.flavor && v.flavor.confidence!=='unknown')
    v.flavor.flavorFamilies.forEach(f=>fams.add(f)) });
  const flavoured = pool.filter(v=>v.flavor && v.flavor.confidence!=='unknown').length;
  const hasFlavor = fams.size>=2 && flavoured >= pool.length*0.45;

  /* "What matters most" only where the shelf makes the answer mean something.
     Water filtration is not a question to ask on the water pipe shelf: every
     item on it draws through water, so the answer is yes and the question is
     noise. Same for a dab rig. */
  const MUSTS = {
    disp:['longer','smaller','cooled','uncooled','cheap','recharge','nicfree'],
    dab: ['battery','portable','tempctl'],
    water:['portable'],
    rig: ['portable']
  };

  if(ffTally(cat,'part').length)   st.push('part');
  if(hasFlavor)                    st.push('fam');
  if(hasFlavor && ffAvailableNotes(cat).length>=2) st.push('note');
  if(ffTally(cat,'brand').length)  st.push('brand');
  if(MUSTS[cat] && ffRuleAvailability(cat, MUSTS[cat]).length) st.push('must');
  if(ffTally(cat,'size').length)   st.push('size');
  if(ffTally(cat,'mat').length)    st.push('mat');
  if(ffTally(cat,'nicstr').length) st.push('nicstr');
  if(ffTally(cat,'joint').length)  st.push('joint');
  if(ffTally(cat,'gender').length) st.push('gender');
  if(Object.keys(ffBudgetBands(cat)).length>1) st.push('budget');

  /* Five is the cap. A counter conversation is four or five questions; ten is
     an interrogation and people walk away from it. When a shelf can answer more
     than five, the ones that change the answer most are kept (FF_RANK), and
     then they are put back into the order a conversation runs — kind of thing,
     taste, brand, requirements, and money last, the way it comes up last at the
     counter. */
  if(st.length <= 5) return st;
  const order = st.slice();
  const money = st.indexOf('budget') >= 0;        /* money is never the one cut */
  const kept = st.filter(x=>x!=='budget')
    .sort((a,b)=>(FF_RANK[b]||1)-(FF_RANK[a]||1))
    .slice(0, money ? 4 : 5)
    .sort((a,b)=>order.indexOf(a)-order.indexOf(b));
  return money ? kept.concat(['budget']) : kept;
}"""
rep(old_steps, new_steps)

# ---- 3. the flavor questions stop being about disposables ------------------
rep("""        const n=ffPool('disp').filter(v=>v.flavor&&v.flavor.flavorFamilies.indexOf(k)>=0).length;""",
    """        const n=ffPool(FF.cat).filter(v=>v.flavor&&v.flavor.flavorFamilies.indexOf(k)>=0).length;""")

# ---- 4. part / joint / gender stop being about glass parts -----------------
# The bespoke "which part" screen goes entirely: it was written for one shelf,
# it had no way past it, and the generic question block below does the same job
# for every shelf with an escape on it.
rep("""else if(ffStepId()==='part'){
    const types=[...new Set(ffPool('parts').map(v=>v.attrs.partType.value).filter(Boolean))];
    h=`${ffProgress()}<h3>Which part do you need?</h3>
      <p class="ffsub">Fit comes first here. We only show pieces that actually connect.</p>
      <div class="ffgrid two">${types.map(t=>{
        const n=ffPool('parts').filter(x=>(x.attrs.partType.value||'').toLowerCase().indexOf(t.toLowerCase())>=0).length;
        return ffChoice('part:'+t,t,FF.part===t,n+(n===1?' item':' items'))}).join('')}</div>
      ${ffStill()}`;
  }
  """, "")
# and nothing is mandatory any more, because every question has a way past it
rep("""  if(id==='part')  return !!FF.part  || !document.querySelector('#ffBody [data-ffpick]');
  if(id==='joint') return FF.joint!==null || !document.querySelector('#ffBody [data-ffpick]');""",
    """  if(id==='joint') return FF.joint!==null || !document.querySelector('#ffBody [data-ffpick]');""")
rep("""    const sizes=[...new Set(ffPool('parts').filter(v=>known(v.attrs.jointSize))
      .map(v=>v.attrs.jointSize.value))].sort((a,b)=>a-b);""",
    """    const sizes=[...new Set(ffPool(FF.cat).filter(v=>known(v.attrs.jointSize))
      .map(v=>v.attrs.jointSize.value))].sort((a,b)=>a-b);""")
rep("""        const n=ffPool('parts').filter(x=>known(x.attrs.jointSize)&&x.attrs.jointSize.value===v).length;""",
    """        const n=ffPool(FF.cat).filter(x=>known(x.attrs.jointSize)&&x.attrs.jointSize.value===v).length;""")
rep("""        const n=ffPool('parts').filter(x=>known(x.attrs.jointGender)&&x.attrs.jointGender.value===v).length;""",
    """        const n=ffPool(FF.cat).filter(x=>known(x.attrs.jointGender)&&x.attrs.jointGender.value===v).length;""")

# ---- 5. one render branch for every registry question ----------------------
rep("""  else { h=ffResults(); }""",
"""  else if(ffAsk(ffStepId()) && ffAsk(ffStepId()).opt){
    /* THE GENERIC QUESTION. Brand, size, material and strength all render from
       the same block, because the only thing that differs between them is what
       the shelf can offer — and that is the question's own business, not this
       screen's. */
    const q = ffAsk(ffStepId());
    const opts = q.opt(FF.cat);
    const cur = FF[q.field];
    h=`${ffProgress()}<h3>${q.title}</h3><p class="ffsub">${q.sub}</p>
      <div class="ffgrid two">${opts.map(o=>ffChoice(q.id+':'+o.v, o.label,
        (cur||'')===o.v,
        o.sub || (o.n ? (o.prod && o.prod!==o.n
          ? o.prod+(o.prod===1?' product':' products')
          : o.n+(o.n===1?' item':' items')) : ''))).join('')}</div>
      ${ffStill()}`;
  }
  else { h=ffResults(); }""")

# ---- 6. the answers land on the state object -------------------------------
rep("""    else if(v.indexOf('fam:')===0) ffToggle(FF.families, v.slice(4), 2);""",
"""    else if(v.indexOf('fam:')===0) ffToggle(FF.families, v.slice(4), 2);
    else if(ffAsk(v.split(':')[0]) && ffAsk(v.split(':')[0]).opt){
      /* One tap sets it, a second tap on the same answer clears it, so every
         one of these questions can be un-answered without a Skip button. */
      const q = ffAsk(v.split(':')[0]);
      const val = v.slice(q.id.length+1);
      FF[q.field] = (FF[q.field]===val || val==='') ? null : val;
    }""")

# ---- 7. the new answers become real constraints ----------------------------
rep("""  if(state.part){
    cs.push({code:'part', label:'A '+state.part.toLowerCase(),
      short:state.part.toLowerCase(), drop:'Show every part',
      test:v => (v.attrs.partType.value||'').toLowerCase().indexOf(state.part.toLowerCase())>=0,
      clear:s => { s.part=null }});
  }
  return cs;""",
"""  /* every registry question that has been answered, as its own constraint,
     so the no-results screen can name it and offer to drop just that one */
  FF_ASK.forEach(q=>{
    if(!q.con) return;
    const c = q.con(state);
    if(c) cs.push(c);
  });
  return cs;""")

# ---- 8. a fresh run clears the new answers too ------------------------------
rep("""function ffRestart(){ FF={step:0,cat:null,families:[],notes:[],avoid:[],musts:[],budget:null,
  joint:null,gender:null,part:null,use:null}; ffSave(); ffRender(); }""",
"""function ffRestart(){ FF={step:0,cat:null,families:[],notes:[],avoid:[],musts:[],budget:null,
  joint:null,gender:null,part:null,use:null,brand:null,size:null,mat:null,nicstr:null};
  ffSave(); ffRender(); }""")
rep("""        FF.budget=null; FF.joint=null; FF.gender=null; FF.part=null;""",
"""        FF.budget=null; FF.joint=null; FF.gender=null; FF.part=null;
        FF.brand=null; FF.size=null; FF.mat=null; FF.nicstr=null;""")

# ---- 9. and the shelf button stops promising three ---------------------------
rep("""<small>Three questions and we narrow this
        shelf to what suits you</small>""",
    """<small>A few questions, the way you'd be asked
        at the counter</small>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
