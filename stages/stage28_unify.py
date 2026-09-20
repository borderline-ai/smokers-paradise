#!/usr/bin/env python3
# Stage 28 — one design system, applied as a final layer.
#
# Twenty components had each been given their own idea of what a button, a
# radius, a badge and a heading look like. Rewriting twenty rules in place is
# how that happened in the first place, so instead this is one closing layer
# that every component resolves through. Two calls to action exist. One
# radius. One badge. One shadow set. Headings are near-white.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:120])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))

# ---- the drawn ticket comes out -------------------------------------------
rep("""    dealType:'note', discountAmount:'$10+', art:'ticket', qualifyingCategory:'',""",
    """    dealType:'note', discountAmount:'$10+', qualifyingCategory:'',""")
rep("""function ticketSVG(){
  return `<svg class="tkt" viewBox="0 0 100 100" aria-hidden="true">
    <path d="M14 32h72a6 6 0 016 6v8a7 7 0 000 14v8a6 6 0 01-6 6H14a6 6 0 01-6-6v-8a7 7 0 000-14v-8a6 6 0 016-6z"
      fill="none" stroke="#FF7BC8" stroke-width="3.4" stroke-linejoin="round"/>
    <path d="M50 34v6M50 47v6M50 60v6" stroke="#FF7BC8" stroke-width="3.4" stroke-linecap="round"/>
  </svg>`;
}
""", """/* The raffle card used to carry a drawn ticket. A drawing of a thing the shop
   sells is not a photograph of it, and this app does not do that: the card is
   text now, and stays text until there is a real photograph of a real raffle. */
""")
rep("""          : d.art==='ticket' ? `<div class="drart"><div class="ddraw">${ticketSVG()}</div></div>` : ''}""",
    """          : ''}""")
rep("""            : d.art ? `<div class="ddraw" style="width:100%;height:100%">${d.art==='wheel'?wheelSVG():ticketSVG()}</div>`""",
    """            : d.art==='wheel' ? `<div class="ddraw" style="width:100%;height:100%">${wheelSVG()}</div>`""")
rep("""       : drawn ? `<div class="ddraw">${drawn}</div>`""",
    """       : drawn ? `<div class="ddraw">${drawn}</div>`""")
rep("""  const drawn = !im && d.art === 'wheel' ? wheelSVG() : (!im && d.art === 'ticket' ? ticketSVG() : '');""",
    """  const drawn = !im && d.art === 'wheel' ? wheelSVG() : '';""")

# ---- no claim that something is running right now -------------------------
rep("""    {t:'Raffles',              when:'All year',""",
    """    {t:'Raffles',              when:'Seen in Smokers Paradise content',""")
rep("""    {t:'Spin-N-Win',           when:'Every visit',""",
    """    {t:'Spin-N-Win',           when:'Seen in Smokers Paradise content',""")
rep("""    {t:'Spring Celebration Fest', when:'Sunday April 19, 10 AM to 3 PM',""",
    """    {t:'Spring Celebration Fest', when:'Seen in Smokers Paradise content',""")
rep("""    {t:'Toy Drive',            when:'December 8 to 20',""",
    """    {t:'Toy Drive',            when:'Seen in Smokers Paradise content',""")
rep("""    {t:'Car meet',             when:'January',""",
    """    {t:'Car meet',             when:'Seen in Smokers Paradise content',""")

# ---- the closing layer ----------------------------------------------------
SYSTEM = """
/* ==========================================================================
   THE SYSTEM, APPLIED LAST

   Everything above this line was written component by component, and that is
   exactly how an app ends up with a skewed yellow slab, a gold outline, a
   round green tab and a white pill all meaning "press me". Rather than edit
   twenty rules in place and produce a twenty-first idea, every component is
   resolved here, once.

   Two calls to action. One radius. One badge. One shadow set. One heading
   colour. Nothing below invents anything; it only points existing components
   at the tokens.
   ========================================================================== */

/* ---- radius ---- */
.card,.dcard,.dealrow,.ctile,.btile,.spot,.give,.whyb,.storeb,.lovecard,
.lvnote,.gcard,.social,.signup,.finder,.rvw,.comm,.awardblk,.storystack,
.promoc,.slide,.dcard.big{border-radius:var(--r-card)}

/* ---- primary: the one that moves an order forward ---- */
.btn.neon,.slide .cta,.spot .sgo,.give .gbtn,.sbtns a.pri,.whybtns .pri,
.storecta .btn,#inter .go,.lvnote .lvtog.on,.dealrow .use{
  background:var(--go);color:#2A0016;border:0;
  box-shadow:var(--sh-2);border-radius:var(--r-chip);
  transform:none;text-shadow:none;
  font-family:var(--block);text-transform:uppercase;letter-spacing:.045em}
.btn.neon::before,.btn.neon::after,.slide .cta::before,.slide .cta::after{
  display:none;content:none}
.btn.neon:active,.slide .cta:active{transform:scale(.97)}

/* ---- secondary: everything that does not ---- */
.btn.ghost,.spot .sgo.alt,.sec2,.sinfo .sbtns .sec2,.dealrow .drgo,
.dcard .dcta,.sec-h .more,.lvnote .lvtog,.whybtns button,.sbtns a:not(.pri),
.ckfoot .btn.ghost{
  background:transparent;color:var(--ink);border:0;
  box-shadow:inset 0 0 0 1.4px rgba(255,123,200,.42);
  border-radius:var(--r-chip);transform:none;text-shadow:none}
.band-deal .sec-h .more,.band-new .sec-h .more,.band-rew .sec-h .more{
  background:transparent;color:var(--ink);
  box-shadow:inset 0 0 0 1.4px rgba(255,123,200,.42)}

/* ---- headings read first, always ----
   Near-white, no offset shadow. A drop shadow in the brand colour under a
   heading reads as a printing error at small sizes and as low contrast at
   every size. Eyebrows may carry colour; headings may not. */
.sec-h h3,.shelfhead h2,.backbar h2,.spot h3,.whyb .why-h,.give h3{
  color:#FFF;text-shadow:none}
.band-deal .sec-h h3,.band-new .sec-h h3,.band-rew .sec-h h3{text-shadow:none}
.sh-eye,.eyebrow,.g-eye,.sc-eye,.spot .eye,.whyb .why-eye{
  color:var(--go-ink);opacity:1}
.sec-lead,.whyb .why-p,.spot p{color:var(--ink2)}

/* ---- one badge ---- */
.dbadge,.flag,.chip,.attr,.hl,.hero-award,.lv-eye{border-radius:var(--r-chip)}

/* ---- one shadow ---- */
.card,.dcard,.dealrow,.ctile,.spot,.lovecard{box-shadow:var(--sh-1)}

/* ---- one page margin ---- */
.sec-h,.pad,.sec-lead{padding-inline:var(--sp-edge)}
"""
i = s.rindex('</style>')
s = s[:i] + SYSTEM + s[i:]
print('  system layer appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
