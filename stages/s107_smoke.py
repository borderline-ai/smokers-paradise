#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 107 — the smoke only ever happened on two screens.
#
# Marco: "There should be more animation. All of the logos should have the girl
# smoking, they are smoking in the logo so animate it everywhere you put it.
# I'm imagining smoke going in the background of everything and as you scroll
# you are found with the logos actually putting that smoke in that background.
# In the entrance we already have that, I'm telling you to have it throughout
# as well. I'm not telling you to fill it up with logos or a bunch of shit. I
# want you to look at this if you were a designer, an expert at designing apps."
#
# THE FIRST HALF IS A BUG, NOT A FEATURE REQUEST. The plume engine already
# lights every mark on the page — it walks `.hcm`, measures the artwork, and
# hangs a canvas behind it. It was called exactly three times: once at boot,
# once at the end of renderHome, once at the end of renderOrder. Every other
# screen in this app paints its marks AFTER those calls have run, so the mark
# on the Visit screen, the mark on an empty shelf, the mark on a campaign panel
# and the mark on the menu have been sitting there not smoking since the engine
# was written. He is not asking for a new effect. He is asking why the effect
# he already paid for stops at the door.
#
# It is one observer, not thirty call sites. The language walk already does
# exactly this for the same reason — every render writes fresh DOM, so the pass
# has to run after each one — and this follows it.
#
# THE SECOND HALF IS THE NEW WORK, and the restraint he asked for is the whole
# brief: "not a bunch of shit". So the field is three shapes, not thirty, and
# nothing in it is a logo.
#
#   WHAT IT IS. Three very large, very soft magenta-plum clouds behind the
#   entire app, at four to seven per cent opacity — at the edge of visible,
#   which is where smoke in a room actually is. They drift on their own clocks
#   (61s, 83s, 104s, deliberately coprime so the pattern never repeats), and
#   they are PULLED BY THE SCROLL: the page already computes its own scroll
#   position sixty times a second for the sky, so the field rides that same
#   number and costs one more custom property per frame. Scroll down and the
#   smoke rolls up past you. Stop and it keeps drifting.
#
#   WHY CSS AND NOT A CANVAS. There is already one canvas per mark. A fourth
#   full screen canvas painting a hundred sprites behind every screen is a real
#   phone getting warm in a shop, for something nobody is meant to consciously
#   see. Three blurred gradients on the compositor are free.
#
#   WHERE IT SITS. Inside #appsky, which is already the app's background layer
#   at z-index -1, already inert, already excluded from hit testing. It cannot
#   land on top of anything or take a tap.
#
#   AND IT IS OFF when the phone asks for less motion.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. every mark, on every screen, forever -------------------------------
rep("""  window.smokeUp = smokeUp;""",
"""  window.smokeUp = smokeUp;

  /* ---- and it runs after every render, not after three of them ----

     smokeUp() was called at boot, at the end of renderHome and at the end of
     renderOrder. Every other screen paints its marks after those have already
     run, so the mark on the Visit screen, the mark on an empty shelf, the one
     on a campaign panel and the one on the menu never smoked. Adding a call to
     thirty render functions is thirty chances to forget the thirty first; one
     observer on the view container catches every screen that will ever exist.
     The walk is idempotent — a mark already lit is skipped by the WeakMap — so
     the cost of a spurious run is one querySelectorAll. */
  (function keepSmoking(){
    if(REDUCED() || typeof MutationObserver === 'undefined') return;
    let queued = false;
    const sweep = () => { queued = false; try{ smokeUp() }catch(e){} };
    const mo = new MutationObserver(() => {
      if(queued) return; queued = true; requestAnimationFrame(sweep);
    });
    /* The product sheet and the menu are NOT inside #main, and both can carry
       a mark, so the whole body is watched rather than the view container. */
    const watch = () => { mo.observe(document.body, {childList:true, subtree:true}); sweep() };
    if(document.readyState === 'loading')
      document.addEventListener('DOMContentLoaded', watch, {once:true});
    else watch();
  })();""")

# ---- 2. the field itself ---------------------------------------------------
rep("""    back.innerHTML=skyHTML('back');""",
"""    /* Three clouds behind the whole app. Not a logo, not a texture, not a
       hundred sprites: three shapes at the edge of visible, on three clocks
       that never line up, pulled by the same scroll number the sky already
       reads. */
    back.innerHTML=skyHTML('back') +
      '<div class="smokefield" aria-hidden="true"><i class="s1"></i><i class="s2"></i><i class="s3"></i></div>';""")

rep("""#appsky, #appsky .sky{z-index:-1}""",
"""#appsky, #appsky .sky{z-index:-1}

/* ---- THE ROOM HAS SMOKE IN IT ------------------------------------------
   Three clouds, four to seven per cent, behind everything. Smoke in a room is
   at the edge of what you can see; anything you can actually point at is fog,
   and fog on a shopping screen is a bug. They drift on 61, 83 and 104 second
   clocks — coprime on purpose, so the three never return to the same
   arrangement and the loop cannot be spotted — and --smkY rides the page's own
   scroll, so scrolling down rolls the smoke up past you.

   Three composited gradients, not a canvas. There is already one canvas per
   mark in this app; a fourth full screen one painting behind every screen is a
   warm phone in a shop for something nobody is meant to consciously notice. */
.smokefield{position:absolute;inset:-14% -10%;z-index:-1;pointer-events:none;
  overflow:hidden;contain:strict;will-change:transform}
.smokefield i{position:absolute;display:block;border-radius:50%;
  transform:translate3d(0,var(--smkY,0px),0);
  will-change:transform,opacity}
.smokefield .s1{left:-18%;top:8%;width:86%;height:52%;
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(255,110,205,.085) 0%, rgba(214,96,214,.05) 46%, rgba(214,96,214,0) 74%);
  animation:smkA 61s ease-in-out infinite}
.smokefield .s2{right:-24%;top:34%;width:96%;height:58%;
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(186,120,255,.075) 0%, rgba(150,90,220,.042) 44%, rgba(150,90,220,0) 72%);
  animation:smkB 83s ease-in-out infinite}
.smokefield .s3{left:6%;top:64%;width:78%;height:48%;
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(255,150,220,.062) 0%, rgba(255,120,200,.032) 48%, rgba(255,120,200,0) 76%);
  animation:smkC 104s ease-in-out infinite}
@keyframes smkA{
  0%  {transform:translate3d(-4%,calc(var(--smkY,0px) + 6%),0) scale(1)}
  50% {transform:translate3d(9%,calc(var(--smkY,0px) - 5%),0) scale(1.22)}
  100%{transform:translate3d(-4%,calc(var(--smkY,0px) + 6%),0) scale(1)}}
@keyframes smkB{
  0%  {transform:translate3d(5%,calc(var(--smkY,0px) - 3%),0) scale(1.1)}
  50% {transform:translate3d(-8%,calc(var(--smkY,0px) + 7%),0) scale(.9)}
  100%{transform:translate3d(5%,calc(var(--smkY,0px) - 3%),0) scale(1.1)}}
@keyframes smkC{
  0%  {transform:translate3d(0,calc(var(--smkY,0px) + 4%),0) scale(.95)}
  50% {transform:translate3d(11%,calc(var(--smkY,0px) - 8%),0) scale(1.3)}
  100%{transform:translate3d(0,calc(var(--smkY,0px) + 4%),0) scale(.95)}}
@media (prefers-reduced-motion:reduce){
  .smokefield i{animation:none;transform:none}
  .smokefield{opacity:.5}}""")

# ---- 3. it rides the scroll the sky already measures ------------------------
rep("""    st.setProperty('--py', Math.min(main.scrollTop, 900) + 'px');""",
"""    st.setProperty('--py', Math.min(main.scrollTop, 900) + 'px');
    /* The smoke rides the same number. Unclamped and negative, so it keeps
       rolling up past the reader all the way down a long shelf instead of
       stopping at 900px like the parallax ground does; 0.14 is slow enough to
       read as air moving rather than as a layer sliding. */
    const field = document.querySelector('#appsky .smokefield');
    if(field) field.style.setProperty('--smkY',
      (-main.scrollTop * 0.14).toFixed(1) + 'px');""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
