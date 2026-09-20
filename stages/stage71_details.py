#!/usr/bin/env python3
# Stage 71 — the small things, found by reading the screens.
#
#  * The product page title rendered SWITCH PRO 30K and the source line
#    SPECIFICATIONS PUBLISHED BY FOGER. Both were being uppercased by a rule
#    more specific than the copy-style layer, so both are named here.
#  * "From our feed" was the date stamp on all five community cards, so the
#    same three words sat above every one of them. They carry the real timing
#    the shop published instead.
#  * The product page showed the model photograph while the selected flavour
#    was a different one. It cannot show a photograph that does not exist, so
#    it says so in one line rather than letting the wrong sleeve pass as the
#    chosen flavour.
#  * The announcement strip ran its longest line under both arrows.
#  * The save control on a product card was a plain white circle.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:60].replace('\n', ' '))


# ---------------------------------------------- the community date stamps
rep("""    {t:'Spring Celebration Fest', when:'From our feed',""",
    """    {t:'Spring Celebration Fest', when:'Sunday, April 19',""")
rep("""    {t:'Raffles',              when:'From our feed',""",
    """    {t:'Raffles',              when:'At the counter',""")
rep("""    {t:'Spin-N-Win',           when:'From our feed',""",
    """    {t:'Spin-N-Win',           when:'At the counter',""")
rep("""    {t:'Toy Drive',            when:'From our feed',""",
    """    {t:'Toy Drive',            when:'December 8 to 20',""")
rep("""    {t:'Car meet',             when:'From our feed',""",
    """    {t:'Car meet',             when:'January, in our lot',""")

# ------------------------------------- the product page and its flavour art
rep("""    <div class="eyebrow" style="margin-top:15px">${p.brand}</div>
    <h3>${p.name}</h3>
    ${p.sourceUrl?`<div class="ratebar"><span class="srcline">Specifications published by ${p.brand}</span></div>`:''}""",
"""    <div class="eyebrow" style="margin-top:15px">${p.brand}</div>
    <h3>${p.name}</h3>
    ${/* When the chosen flavour has no photograph of its own, the stage falls
         back to the model shot — which wears a different sleeve. Saying so is
         better than letting the wrong packaging pass for the right one. */''}
    ${(function(){
       const g=(p.opts||[]).find(o=>o.k==='v'); if(!g) return '';
       const v=g.vals[(PICK.sel||{}).v||0]; if(!v) return '';
       const own = typeof PHOTOS!=='undefined' && PHOTOS[p.id+'::'+vslug(v.n)];
       return own ? '' : `<div class="artnote">Pictured: this model. Packaging differs by flavor.</div>`;
     })()}
    ${p.sourceUrl?`<div class="ratebar"><span class="srcline">Specifications published by ${p.brand}</span></div>`:''}""")

CSS = r'''
/* ==========================================================================
   THE LAST OF THE SHOUTING
   These four selectors out-specify the copy-style layer, so they are named.
   ========================================================================== */
.pdp h3,.sheet h3,.pdp .name{
  font-family:var(--disp);font-weight:800;font-size:27px;line-height:1.08;
  letter-spacing:-.028em;text-transform:none;color:var(--ink);margin:6px 0 0;
}
.srcline,.pdp .srcline{
  font-family:var(--body-f);font-size:12.5px;letter-spacing:normal;
  text-transform:none;color:var(--muted);
}
.varct,.card .varct{
  font-family:var(--body-f);font-size:11.5px;letter-spacing:normal;
  text-transform:none;color:var(--muted);
}
.sbtns a,.sbtns a.pri,.storeb .sbtns a{text-transform:none}
.bnr h2,.bnr b,.spot h3,.give h3{text-transform:none}

/* eyebrows keep their caps but lose the extreme tracking */
.camp-kick,.ad-kick,.aw-kick,.camp-sig,.sh-eye,.sh-kick,.eyebrow,.comm-when{
  letter-spacing:.12em;
}

/* the honest note under a fallback packshot */
.artnote{
  font-family:var(--body-f);font-size:12px;line-height:1.45;
  color:var(--muted);margin:8px 0 0;
}

/* the product page stage: the product, not the panel, is the subject */
.pdp-art{padding:16px}
.pdp-art img{max-width:88%;max-height:88%}

/* ---- the save control -------------------------------------------------
   A solid white circle on a dark card. It is a control, not a product. */
.card .fav,.card .save,.card .heart,.fav-btn{
  background:rgba(20,12,30,.62);
  border:1px solid rgba(255,255,255,.22);
  backdrop-filter:blur(6px);
  color:#FFD3EC;
}
.card .fav svg,.card .save svg,.card .heart svg,.fav-btn svg{
  stroke:#FFD3EC;fill:none;
}
.card .fav.on svg,.card .save.on svg,.card .heart.on svg,.fav-btn.on svg{
  fill:var(--go);stroke:var(--go);
}

/* ---- the announcement strip clears its arrows ------------------------- */
#annb{position:relative}
#annb .track{padding-left:38px;padding-right:38px}
#annb .nb{z-index:3}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  detail styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
