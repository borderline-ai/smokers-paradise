#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 158 — three things the finished tool says badly.
#
# The conversation works now. Read back what it SAYS at the end of it:
#
#   1. "3 of the 3 on this shelf fit everything you said."
#      "2 of the 2 on this shelf fit everything you said."
#      Nobody says this. Where the number of matches and the number shown are
#      the same number, saying it twice makes the sentence sound like a
#      database rather than a person: "The three on this shelf that fit
#      everything you said."
#
#   2. "The closest of these 3 to everything you asked for."
#      Printed when all three meet every single thing that was asked. Nothing
#      is "closest" when everything qualifies — it is the sentence the tool
#      falls back to when no superlative can be proved, and the fallback should
#      not invent a comparison that was not made. What is honestly true at that
#      point is that this is the one it would start you on.
#
#   3. "shisha"
#      Lower case, in a list beside "Hookah", "Bowl" and "Coals", because that
#      is how one product's spec sheet happened to type it. The catalogue's
#      capitalisation is not a design decision and should not reach the screen.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. do not say the same number twice -----------------------------------
rep("""        : (r.total<=1
            ? 'The only one on this shelf that fits everything you said.'
            : `${r.matches.length} of the ${r.total} on this shelf fit everything you said.`)""",
"""        : (r.total<=1
            ? 'The only one on this shelf that fits everything you said.'
            : (r.matches.length>=r.total
                ? `The ${ffWord(r.total)} on this shelf that fit everything you said.`
                : `${r.matches.length} of the ${r.total} on this shelf fit everything you said.`))""")

rep("""const ffNum = (v,k) =>""",
"""/* Small numbers read as words in a sentence; anything a person would not say
   out loud stays a numeral. */
const FF_WORDS = ['no','one','two','three','four','five','six','seven','eight',
                  'nine','ten','eleven','twelve'];
const ffWord = n => FF_WORDS[n] || String(n);

const ffNum = (v,k) =>""")

# ---- 2. the fallback stops inventing a comparison --------------------------
rep("""  const of = others.length===1 ? 'of the two' : 'of these ' + all.length;""",
"""  const of = others.length===1 ? 'of the two' : 'of these ' + ffWord(all.length);""")

rep("""  /* nothing is provably best, so say the true thing instead */
  return 'The closest ' + of + ' to everything you asked for.';""",
"""  /* Nothing here is provably best, so the sentence stops comparing. "The
     closest to everything you asked for" is a claim about a gap, and when all
     of them meet everything there is no gap to be closest across. What is
     still true is which one it would put in your hand first. */
  return 'Any of these does what you asked. This is the one I\\'d start you on.';""")

# ---- 3. the catalogue's capitalisation does not reach the screen -----------
rep("""   opt:(cat)=>ffTally(cat,'part')
     .map(o=>({v:o.v, label:o.v, n:o.n, prod:o.prod}))""",
"""   opt:(cat)=>ffTally(cat,'part')
     /* "shisha" beside "Hookah" and "Coals" is one spec sheet's typing, not a
        decision anyone made about this screen. */
     .map(o=>({v:o.v, label:o.v.charAt(0).toUpperCase()+o.v.slice(1),
               n:o.n, prod:o.prod}))""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
