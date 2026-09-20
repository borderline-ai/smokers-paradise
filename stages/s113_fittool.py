#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 113 — the counter staff looked like a form.
#
# Marco: "Also work on the tools that help select what you want to buy, it
# looks ai. We want attention to detail. Maybe some smoke coming out, some
# animations around the app, SOMETHING to show that we put in detail."
#
# He is right and the reason is embarrassing. The first question of the tool —
# "What are you shopping for?" — draws eleven identical rows, each with a
# 44px grey square on the left where a picture of that shelf should be, and an
# empty circle on the right. The grey squares were never meant to be empty:
#
#     const im = remoteFor(ex, ...)            // a URL on somebody's server
#     ffChoice(..., im ? im.remoteImageUrl : '')
#
# It asks the REMOTE table for a picture, which is a link to the maker's site.
# In the shop in Nogales there is no wifi, so eleven empty grey squares. Every
# photograph this app owns is embedded in the file and none of them were being
# used here. One line.
#
# WHAT ELSE WAS WRONG, found by reading it as a customer would:
#
#   "461 products still match." The app carries 259 products. The counter was
#   counting FLAVOURS, so the one line that is supposed to build trust in the
#   tool contradicted the number on the front of the shelf. It counts products
#   now, and says how many flavours those come in, which is the honest version
#   and the more useful one.
#
#   Eleven questions in a row with no shop in them. The panel now opens with
#   the shop's own mark, smoking, above the first question — the one screen in
#   this app where a customer is being ASKED something is the one screen where
#   the person behind the counter should be visible.
#
#   The empty circle. A choice that has been made should look made: the row
#   lights in the shop's magenta, and a wisp lifts off it once, the way
#   something lit does. Two hundred milliseconds, once, on the row you touched.
#
#   And the copy. "Tell us what you like. We'll narrow the shelf." is a form
#   talking. The shop's line is what the staff actually do.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the picture is in this file, so use it ----------------------------
rep("""        const ex=PRODUCTS.find(p=>c.cats.indexOf(p.cat)>=0);
        const g=ex?(ex.opts||[]).find(o=>o.k==='v'):null;
        const im=ex?(remoteFor(ex, g?g.vals[0].n:null)||remoteFor(ex,null)):null;
        const rows=PRODUCTS.filter(p=>c.cats.indexOf(p.cat)>=0).length;
        return ffChoice(c.k, c.label, FF.cat===c.k, rows+(rows===1?' item':' items'), im?im.remoteImageUrl:'');""",
"""        /* THE PICTURE IS IN THIS FILE. This asked remoteFor() for a link to
           the maker's server, and in a shop with no wifi that is eleven empty
           grey squares where eleven shelves should be. Take the best
           photograph this app is already carrying for that shelf: the
           featured one if there is one, otherwise the first that has a file. */
        const on = PRODUCTS.filter(p => c.cats.indexOf(p.cat) >= 0 && p.published !== false);
        /* Where a department already has a picture chosen for it on Shop by
           Category, use that one: it was picked to be a single clean unit and
           two different pictures of the same shelf, two screens apart, is the
           kind of thing that reads as nobody looking. */
        const tile = (typeof CATTILES !== 'undefined')
          ? CATTILES.find(t => t.k === c.k) : null;
        let im = '';
        if(tile && tile.img){ try{ im = tile.img() || '' }catch(e){} }
        if(!im){
          const ex = on.find(p => p.featured && LOCAL_PHOTOS[p.id])
                  || on.find(p => LOCAL_PHOTOS[p.id]) || on[0];
          im = ex ? (LOCAL_PHOTOS[ex.id] || '') : '';
        }
        const rows = on.length;
        return ffChoice(c.k, c.label, FF.cat===c.k, rows+(rows===1?' item':' items'), im);""")

# ---- 2. the counter says products, because the shelf says products --------
rep("""function ffStill(){
  if(!FF.cat) return '';
  let n;
  try{ n = ffCount(FF) }catch(e){ return '' }
  if(n===0) return `<div class="ffstill none">Nothing on the shelf meets all of this yet. Change an answer above, or carry on and we'll show you what is closest.</div>`;
  if(n<=3) return `<div class="ffstill low">${n} product${n>1?'s':''} still match${n>1?'':'es'}.</div>`;
  return `<div class="ffstill">${n} products still match.</div>`;
}""",
"""function ffStill(){
  if(!FF.cat) return '';
  /* THIS SAID "461 products still match" ON A SHELF OF 259 PRODUCTS.
     ffCount counts VARIANTS — every flavour of every device — so the one line
     whose whole job is to make the tool trustworthy was contradicting the
     number printed on the front of the shelf. Count the products, and say how
     many flavours they come in, which is the true answer and the more useful
     one: eleven devices in ninety flavours is a different shop from ninety
     devices. */
  let vars, prods;
  try{
    const cs = ffConstraints(FF);
    const live = ffPool(FF.cat).filter(v => cs.every(c => c.test(v)));
    vars = live.length;
    prods = new Set(live.map(v => v.id || (v.product && v.product.id) || v.pid)).size || vars;
  }catch(e){ return '' }
  if(prods===0) return `<div class="ffstill none">Nothing on the shelf meets all of this yet. Change an answer above, or carry on and we'll show you what is closest.</div>`;
  const tail = (vars > prods) ? ` in ${vars} flavors` : '';
  if(prods<=3) return `<div class="ffstill low">${prods} product${prods>1?'s':''}${tail} still match${prods>1?'':'es'}.</div>`;
  return `<div class="ffstill">${prods} products${tail} still match.</div>`;
}""")

# ---- 3. the shop is in the room ------------------------------------------
rep("""    h=`<div class="ffprog"><i></i><i></i><i></i><span>Start</span></div>
      <h3>What are you shopping for?</h3>""",
"""    h=`${/* The one screen where a customer is being ASKED something is the
             one screen the person behind the counter should be visible on.
             The mark smokes here like it does everywhere else. */''}
      <div class="ffmark">${(typeof markHTML==='function')?markHTML('idle','ffm smokes'):''}</div>
      <div class="ffprog"><i></i><i></i><i></i><span>Start</span></div>
      <h3>What are you shopping for?</h3>""")

# ---- 4. a choice that has been made looks made ----------------------------
rep(""".ffopt.on{border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}""",
"""/* A CHOICE THAT HAS BEEN MADE SHOULD LOOK MADE. This was a white hairline —
   the same weight as the unselected row — on a screen whose whole purpose is
   to show what you have picked. It takes the shop's colour, and a wisp lifts
   off the row once, for a fifth of a second, the way something lit does. */
.ffopt.on{border-color:var(--go);background:linear-gradient(120deg,
    rgba(255,86,190,.13) 0%, rgba(255,86,190,.05) 60%, transparent 100%);
  box-shadow:inset 0 0 0 1px rgba(255,86,190,.45)}
.ffopt{position:relative;overflow:hidden}
.ffopt.on::after{content:"";position:absolute;right:26px;top:50%;width:26px;height:26px;
  border-radius:50%;pointer-events:none;
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(255,190,235,.55) 0%, rgba(255,150,220,.22) 45%, rgba(255,150,220,0) 75%);
  animation:ffpuff .9s ease-out 1 both}
@keyframes ffpuff{
  0%  {transform:translate(0,-50%) scale(.35); opacity:0}
  25% {opacity:.9}
  100%{transform:translate(-10px,-190%) scale(2.1); opacity:0}}
@media (prefers-reduced-motion:reduce){ .ffopt.on::after{animation:none;opacity:0} }

/* the mark at the top of the first question */
.ffmark{width:112px;margin:0 auto 4px;line-height:0}
.ffmark .hcm{width:100%}
@media (prefers-reduced-motion:reduce){ .ffmark{opacity:.9} }""")

# ---- 5. the shop's line, not a form's ------------------------------------
rep("""Tell us what you like. We&rsquo;ll narrow the shelf.""",
"""Same as asking at the counter. A few questions, then what we&rsquo;d hand you.""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
