#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 175 — the last of the texts, and the Spanish that went with them.
#
# Stage 174 went through the app deleting claims that a text gets sent, and
# missed one. The note under the register board still read:
#
#     "Mark it ready and the customer gets a text."
#
# The button above it had been corrected to "Mark ready" and the ticket state
# to "showing on their order screen", so the screen contradicted itself: two
# honest sentences and one false one, three inches apart.
#
# Found by opening the counter on a phone and reading it, not by a test. Worth
# recording why the tests missed it: they assert on the button and the ticket
# state, which are the controls, and this is prose. A string that only a person
# reads is exactly the kind of thing a test walks past.
#
# The fix is also the honest description of what the board actually does, which
# is better copy than the false version: the customer's own screen follows the
# counter, and the shop does not need anybody's permission for that to be true.
#
# Two more turned up in the same sweep, both missed for the same reason.
#
# THE JOIN PROMPT. "21+ only. We text you, and STOP stops it." The sheet that
# asks a browsing customer to join the programme, promising the one thing the
# programme does not do.
#
# THE SPANISH. Stage 174 changed the English strings and left the translation
# map keyed on the old ones. The lookup is by exact English string, so
# "Deal alerts by email" matched nothing and the Spanish silently fell back to
# English — a Spanish-speaking customer in a border town gets the untranslated
# version of a screen that was translated yesterday. The keys are updated here
# and the wording follows: "por mensaje" becomes "por correo".
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'app', 'index.html')
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""A ticket lands here the second someone taps Place order. Mark it ready and the customer gets a text. It runs in a browser on whatever screen is already by the counter, nothing to install.""",
    """A ticket lands here the second someone taps Place order. Mark it ready and their own order screen says so within a few seconds. It runs in a browser on whatever screen is already by the counter, nothing to install.""")

rep("""    <p class="ckfine">21+ only. We text you, and STOP stops it.</p>`;""",
    """    <p class="ckfine">21+ only. We email you, and one tap unsubscribes.</p>`;""")

# ---- the Spanish, re-keyed onto the strings that now exist ----
rep('"Text me when it\u2019s bagged":"M\u00e1ndame mensaje cuando est\u00e9 listo"',
    '"Tell me the moment my bag is ready":"Av\u00edsame apenas est\u00e9 lista mi bolsa"')
rep('"Deals by text":"Ofertas por mensaje"',
    '"Deals by email":"Ofertas por correo"')
rep('"Deal alerts by text":"Avisos de ofertas por mensaje"',
    '"Deal alerts by email":"Avisos de ofertas por correo"')
rep('"One message when a real deal lands. Not a newsletter.":"Un mensaje cuando de verdad cae una oferta. No es un bolet\u00edn."',
    '"One message when a real deal lands. Not a newsletter.":"Un correo cuando de verdad cae una oferta. No es un bolet\u00edn."')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
