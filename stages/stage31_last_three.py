#!/usr/bin/env python3
# Stage 31 — the last three inconsistencies the cleanup test found.
#
# 1. Cards carried three different hairlines. A deal card was outlined in a
#    brighter pink than a product card, and the Love card had no outline at all,
#    which is the "unrelated border treatments" note, still true after stage 28.
#
# 2. The featured banner's call to action was a filled magenta pill; the pair
#    beneath it rendered the same call to action as bare text. Two ideas of what
#    "press me" looks like, inside one banner system.
#
# 3. "What just landed" and "New torches just landed" were still claiming
#    recency nobody at the shop has stated.
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


# ---- 3. the last recency claims -------------------------------------------
rep("""    {src:P1_IMG, cap:'New torches just landed', when:'New arrival'},""",
    """    {src:P1_IMG, cap:'Torches and lighters', when:'Seen in Smokers Paradise content'},""")
rep("""'<a class="more" href="'+STORE.instagram+'" target="_blank" rel="noopener">Follow us</a>','What just landed')}""",
    """'<a class="more" href="'+STORE.instagram+'" target="_blank" rel="noopener">Follow us</a>','Seen in Smokers Paradise content')}""")
rep("""    ${secHead('New In Store','<button class="more" data-go="store">See the shop</button>','What just landed')}""",
    """    ${secHead('From Our Feed','<button class="more" data-go="store">See the shop</button>','Seen in Smokers Paradise content')}""")

# ---- 1 + 2: the closing layer gets the last two rules ---------------------
LAST = """
/* ==========================================================================
   THE LAST TWO
   Found by driving the finished app rather than by reading the stylesheet,
   which is the only way these ever turn up.
   ========================================================================== */

/* ---- one hairline ----
   A deal card was outlined in a brighter pink than a product card and the Love
   card in nothing at all. Three ideas of where a card ends. Now one. */
.card,.dcard,.dealrow,.ctile,.spot,.lovecard,.btile,.gcard{
  border:1px solid rgba(255,120,205,.16)}

/* ---- the pair's call to action is the featured banner's ----
   The big banner said "press me" with a solid magenta pill and the two under it
   said it with bare text and an arrow. Same system, same pill, and the arrow
   rides inside it. */
.bnr .cta{background:var(--go);color:#2A0016;border:0;
  box-shadow:var(--sh-2);border-radius:var(--r-chip);
  padding:9px 15px;margin-top:auto;align-self:flex-start;
  font-family:var(--block);text-transform:uppercase;letter-spacing:.045em;
  font-size:10.5px;text-shadow:none}
.bnr .cta svg{stroke:currentColor}
.bnr.sm .txt{padding-bottom:2px}
"""
i = s.rindex('</style>')
s = s[:i] + LAST + s[i:]
print('  closing rules appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
