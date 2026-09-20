#!/usr/bin/env python3
# Stage 33 — what looking at the finished screens turned up.
#
# 1. THREE different definitions of --stage were live in three different
#    :root blocks (#FFFFFF, #ECE6F0, #F8F3FB), and the last one won. That is
#    the "one design system" note in miniature: even the token had three ideas.
#    One definition now, and one shade down from paper, because near-white
#    filling a full-width square on the product page is a sheet of paper and
#    "white squares behind the products" is the note this pass exists to answer.
#
# 2. A TRE House card printed "$30 in store" under the price. That is an
#    inventory claim about a shop whose inventory we cannot see. The price is
#    the honest half of it.
#
# 3. Products in a department with no spec rule printed "demo selection" in the
#    slot where a puff count or a capacity goes. It read like a bug. A chocolate
#    bar says what it is; anything else says nothing.
#
# 4. The product page printed the brand in the green reserved for freshness
#    while every other eyebrow in the app is magenta.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

# Just off white. Most of this catalogue's packshots are printed on white, so a
# markedly darker plate puts a visible square inside a square; this is far
# enough from paper to read as a lit plate against the dark UI and close enough
# that a white-ground render melts into it.
STAGE = '#F2EFF5'


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:120])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


# ---- 1. one stage token, one shade down from paper ------------------------
rep("""  --stage:#FFFFFF;            /* product photographs keep a white plate */""",
    """  --stage:%s;            /* the one panel a packshot sits on       */""" % STAGE)
rep("""  --stage:#ECE6F0;      /* the neutral panel a packshot sits on */
  --stage-line:rgba(20,10,30,.10);""",
    """  --stage:%s;      /* the one panel a packshot sits on */
  --stage-line:rgba(20,10,30,.13);""" % STAGE)
rep("""  --stage:#F8F3FB;             /* the lit plate product photos sit on   */""",
    """  --stage:%s;             /* the one panel a packshot sits on      */""" % STAGE)

# ---- 2. the price without the claim ---------------------------------------
rep("""  if(p.brand==='TRE House') return '$30 in store';""",
    """  if(p.brand==='TRE House') return '$30 a bar';""")

# ---- 3. the spec slot ------------------------------------------------------
rep("""    case 'nic':   sp.push('pouches'); break;
    default:      sp.push('demo selection');
  }""",
"""    case 'nic':   sp.push('pouches'); break;
    case 'exotic': sp.push('chocolate bar'); break;
    /* No rule for this department yet. A spec line that says nothing is worse
       than no spec line, so nothing is what it gets. */
    default:      break;
  }""")

# ---- 4. one eyebrow colour, including the product page --------------------
CLOSE = """
/* The product page kept the brand line in the green reserved for freshness;
   every other eyebrow in the app is magenta, so this one is too. */
#sheet .eyebrow,.pdp .eyebrow,.sheet .eyebrow{color:var(--go-ink)}
"""
i = s.rindex('</style>')
s = s[:i] + CLOSE + s[i:]
print('  eyebrow rule appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
