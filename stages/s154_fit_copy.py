#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 154 — three sentences on the new results screen that are not true.
#
# The recommendation screen from stage 152 reads correctly on the shelves where
# somebody answered the questions, and reads badly on the paths where they did
# not. Read back what it actually printed on an unanswered run:
#
#     "Out of the 58 on this shelf that meet everything you said."
#         Fifty eight water pipes do not meet everything you said. Nothing was
#         said. 58 is the size of the shelf, and printing it beside three
#         products makes the tool look like it cannot count.
#
#     "The closest of the 3 that fit to everything you asked for."
#         Fifty eight of them fit. Three are being SHOWN. "The 3 that fit" is a
#         claim about the shelf and it is false; the true claim is about these
#         three, which is what the sentence is actually comparing.
#
#     "Only parts that actually fit this one: the right joint, and the maker's
#      own fittings."  ...printed under a ROLLING TRAY.
#         A rolling tray has no joint and no fittings. The sentence is true of
#         a bong and nonsense here, because it was written for the case that
#         needed the promise and then shown in every case.
#
# All three are the same fault: a sentence written for one situation and
# printed in all of them. Each one now asks what is actually on the screen.
#
#     nothing answered      "You haven't narrowed it down, so this is where
#                            I'd start you."
#     answered, N matched   "3 of the 12 on this shelf fit everything you
#                            said."
#     one match             "The only one on this shelf that fits."
#     the verdict           "The cheapest of these three, at $19.99."
#     joint-fitted parts    "...the right joint, and the maker's own fittings."
#     anything else         "Things that go with it, on the shelf now."
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. the headline counts what is on the screen --------------------------
rep("""    <p class="ffsub">${r.total>1
      ? `Out of the ${r.total} on this shelf that meet everything you said.`
      : 'The one thing on this shelf that meets everything you said.'}</p>""",
"""    <p class="ffsub">${
      !r.constraints.length
        ? "You haven't narrowed it down, so this is where I'd start you."
        : (r.total<=1
            ? 'The only one on this shelf that fits everything you said.'
            : `${r.matches.length} of the ${r.total} on this shelf that fit everything you said.`)
      }</p>""")

# ---- 2. the verdict compares what it is actually comparing ------------------
rep("""function ffVerdict(top, all){
  const n = all.length;
  const others = all.filter(v=>v!==top);
  if(!others.length) return 'The only thing on the shelf that meets everything you asked for.';
  const of = 'of the ' + n + ' that fit';""",
"""function ffVerdict(top, all){
  const others = all.filter(v=>v!==top);
  if(!others.length) return 'The only one on the shelf that meets everything you asked for.';
  /* `all` is what is on the screen, not what the shelf holds, so the sentence
     says so. Claiming "of the 3 that fit" when fifty eight fit is the kind of
     small false number that costs a shopper their trust in every other number
     on the page. */
  const of = others.length===1 ? 'of the two' : 'of these ' + all.length;""")

# ---- 3. the promise under the companions matches the companions ------------
rep("""  const items = c.items.slice(0,3);
  return `<div class="ffgoes">
    <b>${c.label === 'Keep it running' ? 'Keep it running' : "What you'll want with it"}</b>
    <small>Only parts that actually fit this one: the right joint, and the maker's own fittings.</small>""",
"""  const items = c.items.slice(0,3);
  /* The fit promise is only made where there is a fit to promise. A bowl and a
     downstem are matched on the joint and the maker; a rolling tray and a
     grinder simply go together, and saying "the right joint" under a tray is a
     sentence about nothing. */
  const fitted = items.some(p=>{
    const k = (typeof productKind==='function') ? productKind(p) : '';
    return (typeof JOINT_FITTED!=='undefined' && JOINT_FITTED.indexOf(k)>=0)
        || (typeof BRAND_LOCKED!=='undefined' && BRAND_LOCKED.indexOf(k)>=0);
  });
  return `<div class="ffgoes">
    <b>${c.label === 'Keep it running' ? 'Keep it running' : "What you'll want with it"}</b>
    <small>${fitted
      ? "Only parts that actually fit this one: the right joint, and the maker's own fittings."
      : 'Things that go with it, on the shelf now.'}</small>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
