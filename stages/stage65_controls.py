#!/usr/bin/env python3
# Stage 65 — the controls, the labels and three things that were simply wrong.
#
# Read on screen at 390px:
#   * Every call to action was set in the condensed face, UPPERCASE, tracked
#     out: SHOP THE BARS, START AN ORDER, BROWSE THE SHELF, SHOP THE SHELF,
#     OUR STORE. Nine different selectors did it in nine different ways, with
#     four button heights and three corner radii between them.
#   * Category tiles shouted DISPOSABLE VAPES / NICOTINE POUCHES. A department
#     name is not an eyebrow label.
#   * The announcement strip was rotating "Selection and prices are confirmed
#     with the store." — a note to ourselves, printed across the top of the
#     storefront — and still promised discreet pickup on a shelf that is now
#     in store only.
#   * The store page printed the shop's name, street and city twice, once in
#     the address plate and again underneath it in grey.
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


# ======================================================== 1. the announcements
rep("""  {t:'Discreet pickup on the Love shelf. Plain bag, just a code', k:''},""",
    """  {t:'Love shelf in store. Ask at the counter', k:''},""")
rep("""  {t:'Solo 21+. Identificacion valida', k:''},""",
    """  {t:'Solo 21+. Identificaci\\u00f3n v\\u00e1lida en cada recogida', k:''},""")
rep("""  {t:'Selection and prices are confirmed with the store.', k:''}
].filter(live);""",
    """  {t:'Free parking in our lot on North Grand', k:''}
].filter(live);""")

# ========================================================= 2. the store page
# `mapArt()` already draws the address plate: name, street, city, plus code.
# Directly underneath it the same name and the same two address lines were
# printed again in grey. The plate keeps them; the panel keeps the hours and
# the three ways to reach the shop.
rep("""        <h4>${STORE.name}</h4>
        <div class="addr">${STORE.street}<br>${STORE.city}</div>
        <div class="hrs">""",
    """        <div class="hrs">""", count=2)

CSS = r'''
/* ==========================================================================
   CONTROLS, ROUND TWO
   Nine selectors were each inventing a button. They are one button now: one
   height, one radius, one face, sentence case, and a label a person reads
   rather than decodes. The condensed face stays where it belongs — short
   promotional headlines — and never on a control.
   ========================================================================== */
.btn,.slide .cta,.ad-cta,.camp-cta,.dcard .cta,.deal .cta,.bnr .cta,
.spot .sgo,.give .gbtn,.sbtns a,.whybtns a,.storecta .btn,#inter .go,
.dealrow .use,.skyhero .btn,.skyhero .btn.ghost,.lv-acts a,.lv-back,
.gr-acts .btn,.emptycats .btn,.cklink,.mnu-call{
  font-family:var(--body-f);
  font-weight:700;
  text-transform:none;
  letter-spacing:.005em;
  text-decoration:none;
}
.btn,.slide .cta,.ad-cta,.camp-cta,.dcard .cta,.deal .cta,
.spot .sgo,.give .gbtn,.sbtns a,.whybtns a,.storecta .btn,#inter .go,
.dealrow .use,.skyhero .btn,.skyhero .btn.ghost,.lv-acts a,.gr-acts .btn{
  min-height:46px;
  padding:0 20px;
  border-radius:99px;
  transform:none;                 /* the skewed sign-board slab is gone */
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  font-size:14.5px;
  line-height:1;
}
/* primary: solid magenta, dark ink — 6.6:1, against 3.3:1 for white on pink */
.btn.neon,.slide .cta,.ad-cta,.camp-cta,.dcard .cta,.deal .cta,
.spot .sgo,.give .gbtn,.sbtns a.pri,.whybtns .pri,.storecta .btn,#inter .go,
.dealrow .use,.gr-acts .btn.neon{
  background:var(--go);
  color:#1A0510;
  border:0;
  box-shadow:0 8px 22px rgba(255,47,168,.24);
}
/* secondary: outline, never a second solid */
.btn.ghost,.btn.outline,.skyhero .btn.ghost,.sbtns a:not(.pri),.lv-acts .sec2,
.whybtns a:not(.pri){
  background:rgba(255,120,205,.06);
  color:#FFD3EC;
  border:1px solid rgba(255,120,205,.34);
  box-shadow:none;
}
.btn.neon > span,.slide .cta > span,#inter .go > span,.storecta .btn > span{
  transform:none;                 /* the counter-skew that went with the slab */
}
/* an arrow is decoration, so it never gets its own weight */
.btn svg,.slide .cta svg,.ad-cta svg,.camp-cta svg{width:15px;height:15px;opacity:.85}

/* ---- department tiles: a name, not a shout --------------------------- */
.ctile b{
  font-family:var(--body-f);
  font-weight:700;
  font-size:13.5px;
  letter-spacing:normal;
  text-transform:none;
  line-height:1.2;
  color:var(--ink);
}
.ctile small{
  font-family:var(--body-f);
  font-size:11.5px;
  letter-spacing:normal;
  text-transform:none;
  color:var(--muted);
  opacity:1;
}
/* the count beside a section heading is secondary information */
.sec-h .sh-count,.sec-h .count,.sh-r .count{color:var(--muted);opacity:1}

/* ---- the pickup slots -------------------------------------------------
   A grid with a fixed track count left an empty bordered cell beside the
   only slot on offer. Flex, so one slot fills the row and four share it. */
.pickslot,.pickslot.big{
  display:flex;flex-wrap:wrap;gap:9px;
  background:none;border:0;padding:0;
}
.pickslot button{flex:1 1 150px}

/* ---- the money block --------------------------------------------------
   One hairline, above the total. Rules under every line made it read as a
   spreadsheet. */
.ckcard.sum .ck-row{border-bottom:0;padding:9px 0}
.ckcard.sum .ck-row.big{
  border-top:1px solid rgba(255,120,205,.24);
  margin-top:6px;padding-top:14px;
}
.ckcard.sum .ck-row.big > span{font-size:17px;color:var(--ink);font-weight:600}
.ckcard.sum .ck-row.big b{font-size:21px;color:var(--ink)}
.ckcard.sum .ck-row b{font-family:var(--mono);font-size:16px;color:var(--ink2)}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  control styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
