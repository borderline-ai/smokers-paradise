#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 135 — Come By, in the footer.
#
# Marco: "Also do me the favor of working on the COME BY section its missing
# that attention to detail."
#
# Stage 122 rebuilt this footer from a ragged left-aligned column into
# something with structure, and Come By got the least of that work: an
# eyebrow, two lines of address, a two-row hours table and three outline
# buttons. Nothing in it is wrong. Nothing in it was designed either — it is
# the same four blocks the rest of the footer has, stacked.
#
# WHAT IT IS MISSING, read as somebody who has scrolled the whole app and
# arrived at the bottom of it:
#
#   IT DOES NOT SAY WHETHER THE SHOP IS OPEN. The header says so, the Visit
#   card says so, and the last thing on the page — the block literally headed
#   COME BY — does not. That is the one fact that decides whether somebody
#   acts on it right now.
#
#   THE ADDRESS IS NOT A LINK. Two lines of plain text sitting directly above
#   a Directions button. The address is the thing a thumb goes for.
#
#   AND THE FOUR THINGS THAT GOVERN A VISIT — pickup only, 21+ with ID, se
#   habla espanol, free parking — are stated in three other places in this app
#   and not here, where somebody is deciding whether to drive over.
#
# So: the address becomes the heading and the link, the live state sits beside
# it, the plus code goes under it in mono because that is what a plus code is
# for, the hours keep today marked, and the four conditions run as a single
# line of chips rather than four more rows. It is more information in about the
# same height, and every line of it earns its place by answering something.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""    <div class="sf-visit">
      <h5>Come by</h5>
      <div class="sf-addr">${STORE.street}<br>${STORE.city}</div>""",
"""    <div class="sf-visit">
      <div class="sf-vhead">
        <h5>Come by</h5>
        ${/* THE LAST BLOCK ON THE PAGE IS THE ONE HEADED "COME BY" AND IT DID
               NOT SAY WHETHER THE SHOP WAS OPEN. It does now, off the same
               clock as the header and the Visit card. */''}
        <span class="sf-vstate${st.open?' on':''}"><i></i>${esc(st.label)}</span>
      </div>
      ${/* the address is what a thumb goes for, so it is the link, not the
             paragraph sitting above the link */''}
      <a class="sf-addr" href="${STORE.mapHref}" target="_blank" rel="noopener">
        <b>${STORE.street}</b><span>${STORE.city}</span>
        <em>Plus code 83XC+9G</em></a>""")

rep("""      <div class="sf-acts">
        <a href="${STORE.phoneHref}">${STORE.phone}</a>
        <a href="${STORE.mapHref}" target="_blank" rel="noopener">Directions</a>
        <a href="${STORE.instagram}" target="_blank" rel="noopener">Instagram</a>
      </div>
    </div>""",
"""      ${/* THE FOUR THINGS THAT GOVERN A VISIT, stated where somebody is
             deciding whether to make one. They are in three other places in
             this app and were not in this one. One line, not four rows. */''}
      <div class="sf-cond">
        <span>Pickup only</span><span>21+ with ID</span>
        <span>Se habla espa&ntilde;ol</span><span>Free parking</span>
      </div>
      <div class="sf-acts">
        <a href="${STORE.phoneHref}">${STORE.phone}</a>
        <a href="${STORE.mapHref}" target="_blank" rel="noopener">Directions</a>
        <a href="${STORE.instagram}" target="_blank" rel="noopener">Instagram</a>
      </div>
    </div>""")

# ---- the look --------------------------------------------------------------
rep(""".sf-visit{margin-top:22px;padding-top:18px;border-top:1px solid var(--hair2)}
.sf-addr{font-family:var(--body-f);font-size:13.5px;line-height:1.55;color:var(--ink2)}""",
""".sf-visit{margin-top:22px;padding-top:18px;border-top:1px solid var(--hair2)}
.sf-vhead{display:flex;align-items:center;justify-content:space-between;gap:12px}
.sf-vhead h5{margin:0}
.sf-vstate{display:inline-flex;align-items:center;gap:6px;flex:none;
  font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase;
  color:var(--muted);border:1px solid var(--hair);border-radius:99px;padding:5px 9px}
.sf-vstate i{width:5px;height:5px;border-radius:50%;background:var(--muted);flex:none}
.sf-vstate.on{color:var(--go-ink);border-color:rgba(255,120,205,.32)}
.sf-vstate.on i{background:var(--go);box-shadow:0 0 0 3px rgba(255,47,168,.16)}

/* the address IS the directions control */
a.sf-addr{display:flex;flex-direction:column;gap:1px;margin-top:11px;
  padding:12px 13px;border-radius:13px;border:1px solid var(--hair);
  background:var(--card);text-decoration:none}
a.sf-addr b{font-family:var(--body-f);font-size:14px;font-weight:700;color:var(--ink);
  line-height:1.25}
a.sf-addr span{font-family:var(--body-f);font-size:13px;color:var(--ink2);line-height:1.3}
a.sf-addr em{font-family:var(--mono);font-style:normal;font-size:9.5px;letter-spacing:.8px;
  color:var(--faint);margin-top:5px}
a.sf-addr:focus-visible{outline:2.5px solid var(--brand);outline-offset:2px}

.sf-cond{display:flex;flex-wrap:wrap;gap:6px;margin-top:11px}
.sf-cond span{font-family:var(--mono);font-size:9px;letter-spacing:.9px;
  text-transform:uppercase;color:var(--muted);border:1px solid var(--hair2);
  border-radius:99px;padding:5px 9px}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
