#!/usr/bin/env python3
# Stage 82 — the reviews section asks for something.
#
# It ended with a full-width pink "Read all 210 reviews" and, underneath it, a
# small bordered "Write a review". The weighting is exactly backwards. Reading
# the reviews is what a shopper does on their own; a 4.9 with 210 behind it has
# already made its point in the number at the top of the section. Writing one
# is the thing the shop actually wants, and it is the thing the app can ask for
# at the only moment a customer is reliably willing: after they have picked the
# order up.
#
# So the two swap weight. And the ask gets a reason: it is the shop's own
# sentence about answering every review, said once, next to the button.
#
# The section is also the wrong place for the shop to ASK, because somebody
# browsing has nothing to review yet. The real ask goes on the order screen
# once an order is collected. That is a separate change; this one stops the
# section shouting the passive half.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


rep("""      <div class="gr-acts">""",
"""      <p class="gr-ask">We read every one of these and we answer them ourselves.</p>
      <div class="gr-acts">""")

rep("""        <a class="btn neon sm" href="${GOOGLE_REVIEWS_URL}" target="_blank" rel="noopener noreferrer"><span>${reviewsRestLabel()}</span></a>
        ${GOOGLE_WRITE_URL ? `<a class="gr-link" href="${GOOGLE_WRITE_URL}" target="_blank" rel="noopener noreferrer">Write a review</a>` : ''}""",
"""        ${/* The shop's ask leads. Reading the rest is the quieter one: the
              4.9 and the count at the top of this section have already made
              that case, and nobody needs a pink button to be persuaded to go
              and read more praise. */''}
        ${GOOGLE_WRITE_URL ? `<a class="btn neon sm" href="${GOOGLE_WRITE_URL}"
          target="_blank" rel="noopener noreferrer"><span>Write a review</span></a>` : ''}
        <a class="gr-link" href="${GOOGLE_REVIEWS_URL}" target="_blank"
          rel="noopener noreferrer">${reviewsRestLabel()}</a>""")

rep(".gr-acts{display:flex;align-items:center;gap:16px;margin-top:14px}",
    ".gr-ask{font-size:12.5px;color:var(--body);line-height:1.5;margin:14px 0 0}\n"
    "/* The link beside the button is a link, not a second button: two filled\n"
    "   pills side by side make a customer choose before they have read either. */\n"
    ".gr-link{font-size:12.5px;color:var(--ink2);text-decoration:none;\n"
    "  border-bottom:1px solid var(--edge);padding-bottom:2px}\n"
    ".gr-link:hover{color:var(--ink);border-bottom-color:var(--brand)}\n"
    ".gr-acts{display:flex;align-items:center;gap:16px;margin-top:14px}")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
