#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 123 — the spin banner was clipart, and clipart is not allowed here.
#
# Marco: "honestly this spin the wheel banner looks SHITTY and completely AI.
# You have seen the type of wheel they have at the shop, if you haven't you can
# see it in their insta but it cant be that I'm the only one that sees all this
# bs."
#
# He is right twice over, and the second time is worse than the first.
#
# IT LOOKS LIKE CLIPART because it IS clipart. wheelSVG() is a drawing: ten
# flat wedges in pink, orange, green and lilac, a gold ring with sixteen dots
# on it for bulbs, a triangle for a pointer, on a sunburst. Nothing in that
# picture was photographed. It is the single most conspicuous object in the
# deals rail and it is the one thing on the screen that a designer did not make
# and a camera did not take.
#
# AND THIS APP ALREADY HAD A RULE ABOUT THAT, written into this very file
# forty lines below wheelSVG: "The raffle card used to carry a drawn ticket. A
# drawing of a thing the shop sells is not a photograph of it, and this app
# does not do that." The wheel broke the rule the file states. I wrote both.
#
# WHAT REPLACES IT, and why not a photograph of their wheel. Their wheel does
# exist and it is on their counter, and the honest way to show it is a picture
# of it. I could not get one: their Instagram grid did not surface one and I
# am not going to draw a better cartoon instead. So the banner shows the thing
# the offer is actually about — the prizes come off their own shelf, and their
# shelf is photographed. Three real products on a lit counter plate, with the
# three days the offer runs set as the mechanic, which is the one fact a
# customer needs and which the drawing never carried.
#
# When Smokers Paradise sends a photograph of the wheel on their counter, it
# drops straight into this block and the composition does not change.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- 1. the drawing goes ---------------------------------------------------
rep("""  if(d.art_kind === 'wheel')
    return `<div class="ad-art wheelart">
      <span class="ad-glow" aria-hidden="true"></span>
      <span class="ad-rays" aria-hidden="true"></span>
      <div class="ad-wheel">${wheelSVG()}</div></div>`;""",
"""  if(d.art_kind === 'wheel'){
    /* WAS A DRAWING OF A PRIZE WHEEL. Ten flat wedges, a gold ring, sixteen
       dots for bulbs, on a sunburst — the one object in this app that no
       camera took, in the middle of the deals rail. The shop's real wheel is
       on their counter and a photograph of it belongs here; there is not one
       yet. Until there is, the banner shows what the offer is actually about:
       the prizes, which come off their own shelf, photographed. */
    const shot = SPIN_ITEMS.map(prizeItem).join('');
    if(!shot) return '';
    return `<div class="ad-art spinart">
      <span class="ad-glow" aria-hidden="true"></span>
      ${/* the mechanic, which the drawing never carried: it runs three days */''}
      <div class="spn-days" aria-hidden="true">
        <b>Mon</b><i></i><b>Tue</b><i></i><b>Wed</b></div>
      <div class="pz-stage lit spn-stage">${shot}</div>
      <span class="spn-fine">Prizes come off our own shelf. Pictured items are
        examples, not a promised prize.</span>
    </div>`;
  }""")

# the function itself, and a note in its place so nobody puts it back
i = s.index('function wheelSVG(){')
j = s.index('/* The raffle card used to carry a drawn ticket.', i)
assert 300 < j - i < 2600, 'wheelSVG block looks wrong: %d' % (j - i)
s = s[:i] + """/* wheelSVG() USED TO LIVE HERE and drew a prize wheel: ten wedges, a gold
   ring, sixteen dots for bulbs, a triangle pointer. It is gone for the same
   reason the drawn raffle ticket below is gone, and the note below is the rule
   it broke. A photograph of the wheel on their counter is welcome the day the
   shop sends one; a drawing of it is not a photograph of it. */

""" + s[j:]
print('  ok: wheelSVG removed (%d chars)' % (j - i))

# ---- 2. what stands on the plate -------------------------------------------
rep("""function prizeItem(it){""",
"""/* THE THREE THAT GO ON THE SPIN PLATE.
   Smaller than the raffle table on purpose: a wheel prize at the counter is a
   disposable, a torch, a pod — not a beaker bong — and a different set of
   products keeps the two banners from reading as the same picture twice. Every
   one is the maker's own photograph, already in this file. */
const SPIN_ITEMS = [
  {id:'r039',  label:'Blazer Big Shot torch',    x:'19%', y:'6%',  h:'78%', z:2},
  {id:'rx089', label:'Lost Mary MT35000 Turbo',  x:'50%', y:'16%', h:'64%', z:4},
  {id:'rx065', label:'Off-Stamp X Cube 25K',     x:'80%', y:'14%', h:'66%', z:3}
];

function prizeItem(it){""")

# ---- 3. the look -----------------------------------------------------------
rep("""/* ---- the wheel: whole, never cropped ---- */
.ad.c-spin .wheelart{display:grid;place-items:center;overflow:hidden}
.ad-rays{position:absolute;left:62%;top:50%;width:150%;aspect-ratio:1/1;
  transform:translate(-50%,-50%);border-radius:50%;opacity:.5;
  background:repeating-conic-gradient(from 0deg,
    rgba(255,209,102,.20) 0deg 9deg, rgba(255,209,102,0) 9deg 18deg);
  -webkit-mask-image:radial-gradient(circle, #000 24%, transparent 72%);
  mask-image:radial-gradient(circle, #000 24%, transparent 72%)}
.ad-wheel{position:relative;z-index:3;width:min(72%, 190px);aspect-ratio:1/1;
  margin-left:auto;margin-right:6%;
  filter:drop-shadow(0 16px 22px rgba(0,0,0,.55))}
.ad-wheel svg{width:100%;height:100%;display:block}""",
"""/* ---- the spin plate: three real products, and the three days ---- */
.ad.c-spin .spinart{position:relative;display:flex;flex-direction:column;
  justify-content:flex-end;gap:8px;padding:14px 16px 16px;overflow:hidden}
.spn-days{display:flex;align-items:center;gap:9px;position:relative;z-index:3}
.spn-days b{font-family:var(--mono);font-size:10px;letter-spacing:1.6px;
  text-transform:uppercase;color:#FFE1A6;border:1px solid rgba(255,209,102,.34);
  border-radius:99px;padding:5px 10px;font-weight:400}
.spn-days i{flex:1;height:1px;background:linear-gradient(90deg,
  rgba(255,209,102,.34), rgba(255,209,102,.10))}
.spn-stage{position:relative;width:100%;aspect-ratio:16/7.4;z-index:2}
.spn-fine{position:relative;z-index:3;font-family:var(--body-f);font-size:10px;
  line-height:1.45;color:rgba(255,255,255,.44);max-width:38ch}""")

rep("""/* ---- the wheel is sized from the row it stands in, so it is always whole -- */
.ad.c-spin .wheelart{position:relative;display:grid;place-items:center;
  min-height:196px;overflow:hidden}
/* sized from its own width, not from a parent whose height is auto — a
   percentage height against an auto-height row resolves to zero */
.ad-wheel{position:relative;z-index:3;width:min(74%,200px);height:auto;
  aspect-ratio:1/1;margin:0 6% 0 auto;
  filter:drop-shadow(0 16px 22px rgba(0,0,0,.55))}
.ad-rays{left:66%}""",
"""/* the plate is sized from its own width, so nothing on it is ever clipped */
.ad.c-spin .spinart{min-height:196px}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
