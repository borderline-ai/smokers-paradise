#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 157 — knowing when to stop asking.
#
# With every option now showing what it would leave (stage 156), the walk down
# the water pipe shelf reads like this:
#
#     Which one are you after?        Straight tube       2 left
#     Anything you already go with?   every brand         none left
#     How big do you want it?         Small               none left
#     What joint size?                10 mm               none left
#     What's your budget?             under $50           none left
#
# Nobody walks into a wall any more, which was the point. But look at what the
# tool is DOING: it narrowed to two products on the first question and then
# asked four more questions about two products. Every screen after the first is
# a row of greyed-out options with one live one. That is not a conversation, it
# is an interrogation about a decision that has already been made.
#
# The person behind the counter does the obvious thing instead. Once there are
# two left they stop asking and say "then it's this one".
#
# ======================================================================
# THE RULE
# ======================================================================
# When three or fewer products are still standing, the remaining questions are
# not asked. There is nothing left for them to narrow, and the screen that
# matters — the one with the recommendation on it — is one tap away instead of
# four. The footer button says what it will do:
#
#     more than three left      "Continue"
#     three or fewer            "Show me the one"   /   "Show me the two"
#
# Back still works, every answer can still be changed from the results screen,
# and nothing is hidden: the count that triggered it is printed on the screen
# that triggers it.
#
# ======================================================================
# AND ONE QUESTION THAT WAS NEVER WORTH ASKING
# ======================================================================
# "Which one are you after?" is the best question on the hookah shelf and the
# worst on the water pipe shelf, for a reason that is in the data rather than
# in the wording: 9 of 43 water pipes publish what KIND of water pipe they are.
# So the question offered six kinds that between them accounted for a fifth of
# the shelf, and every one of them cut 43 products to 2 — not because the shop
# only has two beakers, but because only two beakers say so.
#
# A question whose answers speak for a fifth of the shelf is a question that
# mostly measures the catalogue's gaps. The bar for this one goes to a quarter,
# which keeps it where it is genuinely known (hookah 50%, accessories 56%, glass
# parts 56%, hand pipes 35%) and drops it where it is not (water pipes 21%, dab
# rigs 22%, dab devices 10%). Those shelves have better questions anyway, and
# they now get asked instead.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. a question that mostly measures the catalogue's gaps ---------------
rep("""  part:   {by:'prod', share:0.00, opts:3, cover:0.00, max:8, all:'Not sure yet'},""",
"""  /* cover 0.25: below that this question is not asking what kind of thing the
     customer wants, it is asking which handful of products happen to publish
     what kind of thing they are. */
  part:   {by:'prod', share:0.00, opts:3, cover:0.25, max:8, all:'Not sure yet'},""")

# ---- 2. stop asking once there is nothing left to narrow -------------------
rep("""  if(e.target.closest('[data-ffnext]')){ FF.step++; ffSave(); ffRender(); return }""",
"""  if(e.target.closest('[data-ffnext]')){
    /* ONCE IT IS DOWN TO THREE, STOP ASKING. The questions that are left have
       nothing to narrow — every option on them would be greyed out but one —
       and the counter's answer at this point is "then it's this one", not four
       more questions about two products. */
    FF.step = (FF.step>0 && ffProducts(FF)<=3) ? ffTotal()+1 : FF.step+1;
    ffSave(); ffRender(); return }""")

# ---- 3. and the button says what it is about to do -------------------------
rep("""      ${FF.step===0?'Continue':'Next'}</button>`""",
    """      ${ffNextLabel()}</button>`""")

rep("""function ffFoot(){""",
"""/* The forward button says what pressing it does. Once the shelf is down to
   three there are no more questions worth asking, so it stops saying Next and
   says what it is about to show. */
function ffNextLabel(){
  if(FF.step===0) return 'Continue';
  if(ffOnResults()) return 'Done';
  let n = 0;
  try{ n = ffProducts(FF) }catch(e){ return 'Next' }
  if(n===0 || n>3) return 'Next';
  if(n===1) return 'Show me the one';
  return n===2 ? 'Show me the two' : 'Show me the three';
}

function ffFoot(){""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
