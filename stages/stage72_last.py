#!/usr/bin/env python3
# Stage 72 — the last sweep.
#
# Every control in the app was queried for its computed text-transform and
# letter-spacing and read back. Three were still shouting: GET DIRECTIONS on
# the store teaser, SHOP THE SHELF on the store page, and the brand tiles.
#
# Then the punctuation: seven straight apostrophes were left in copy we wrote
# ("Today's Deals", "it's bagged", "the manufacturer's own photography") while
# the rest of the app uses a typographic one. The apostrophes inside real
# product and brand names — Farley's Gnarly Salt, Juicy Jay's — are left
# exactly as those companies print them.
#
# And the two walkthrough controls sitting unlabelled in the customer's
# account list get a heading, so they read as a deliberate section rather than
# as something nobody cleaned up.
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


# ---------------------------------------------------------------- apostrophes
for a, b in [("Today's Deals", "Today’s Deals"),
             ("Text me when it's bagged", "Text me when it’s bagged"),
             ("the manufacturer's own photography", "the manufacturer’s own photography")]:
    n = s.count(a)
    if n:
        s = s.replace(a, b)
        print('  apostrophe x%d:' % n, a[:44])

CSS = r'''
/* ---- the last three controls that were still shouting ---------------- */
.storeteaser .pri,.storeteaser a,.st-cta,.storecta .btn,
.btile b,.btile .bn,.ecat b{
  text-transform:none;
  letter-spacing:normal;
}
.btile b,.btile .bn{
  font-family:var(--body-f);font-weight:700;font-size:13.5px;color:var(--ink);
}
.btile small,.ecat small{
  font-family:var(--body-f);font-size:11.5px;letter-spacing:normal;
  text-transform:none;color:var(--muted);
}

/* ---- the walkthrough controls are a labelled section, not leftovers --- */
.acct-sec{
  display:block;
  margin:22px var(--pad) 8px;
  font-family:var(--mono);
  font-size:9.5px;
  letter-spacing:.12em;
  text-transform:uppercase;
  color:var(--muted);
}

/* ---- one last look at the empty screens -------------------------------
   Rewards, account and the empty bag each ended with a third of the screen
   doing nothing. They start at the top and stop; the space below is quiet
   rather than a hole under a stretched panel. */
#v-rewards .ckwrap,#v-account .ckwrap,#v-orders .pad{padding-bottom:8px}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  final styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
