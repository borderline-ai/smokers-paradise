#!/usr/bin/env python3
# Stage 74 — two controls that did nothing at all.
#
# 1. "Shop by category" on the home screen.
#
#    It scrolls to #catRail using el.offsetTop, which is measured from the
#    nearest POSITIONED ancestor and not from the scroller. The rail sits 1606px
#    down the page; its offsetTop is 53, because the section it lives in is
#    position:relative. Math.max(0, 53 - 150) is 0, so the button scrolled the
#    page to the top, which is where it already was. Pressing it did nothing,
#    and nothing in the console said so.
#
#    Measuring from the rectangles instead is correct wherever the element
#    sits and whatever gets a position property later.
#
# 2. The offer that greets a first visit.
#
#    Its button carries data-dealgo, like the same advertisement on the home
#    screen does, so pressing it navigates -- but nothing closes the dialog.
#    It happens to shut because navigating scrolls #main and a scroll listener
#    dismisses it. That is a side effect holding the front door shut. The
#    data-intergo branch written for this never fires, because nothing in the
#    app has ever carried that attribute.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


rep("""  const sc2=t.closest('[data-scrollto]'); if(sc2){
    const el=document.getElementById(sc2.dataset.scrollto);
    if(el) $('#main').scrollTo({top:Math.max(0, el.offsetTop-150), behavior:'smooth'});
    return;
  }""",
"""  const sc2=t.closest('[data-scrollto]'); if(sc2){
    const el=document.getElementById(sc2.dataset.scrollto);
    /* offsetTop is measured from the nearest POSITIONED ancestor, not from the
       scroller, so as soon as anything between the two took position:relative
       this button started scrolling to 53px and calling it done. The rail is
       1606px down. Rectangles are measured against the viewport, so the sum
       below is the real distance however the page is nested. */
    const main=$('#main');
    if(el && main){
      const to = main.scrollTop + el.getBoundingClientRect().top
                                - main.getBoundingClientRect().top - 90;
      main.scrollTo({top: Math.max(0, to), behavior:'smooth'});
    }
    return;
  }""")

rep("""document.addEventListener('click',e=>{
  if(e.target.closest('[data-interx]')){ hideInter(); return }
  const ig=e.target.closest('[data-intergo]');
  if(ig){ const d=DEALCARDS.find(x=>x.id===ig.dataset.intergo); hideInter(); if(d)goTarget(d.ctaTarget); }
});""",
"""document.addEventListener('click',e=>{
  if(e.target.closest('[data-interx]')){ hideInter(); return }
  /* The dialog shows the ordinary advertisement, so its button is the ordinary
     data-dealgo one and the ordinary handler navigates. Closing the dialog is
     this one's job, and it has to be explicit: it used to shut only because
     navigating scrolls #main and a scroll listener dismisses it, which is a
     side effect holding the front door shut. */
  if(e.target.closest('[data-dealgo]') && e.target.closest('#inter')) hideInter();
});""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
