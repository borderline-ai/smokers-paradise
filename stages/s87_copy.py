#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 87 — the copy read back, line by line, in both languages.
#
# Every string a customer can reach was pulled out of the rendered app across
# eight screens and read as prose rather than as code. Six things.
#
# 1. SEVEN EM DASHES IN CUSTOMER SENTENCES. Marco does not use them and neither
#    should the shop. Each one was joining two complete thoughts, which is what
#    a full stop is for, so each becomes two sentences or takes a comma. The
#    em dashes that remain in the file are the typographic kind — the one that
#    stands in an empty table cell for a price that is not published — and
#    those are correct.
#
# 2. THE LOVE SHELF PRINTED ITSELF TWICE, ONCE IN EACH LANGUAGE. That was the
#    right answer in a border town before there was a language button in the
#    header. There is one now, so the page says it once, in the language the
#    customer chose, like every other page.
#
# 3. THE APP CLOSED ON SATURDAY IN THREE PLACES. "Open 8 AM to 9 PM, Monday
#    through Saturday." sits in the store strip, the account footer and the
#    glass-fitting sheet, while the store page, the hours table and the
#    announcement bar all say seven days. Sunday is 10 to 7 and now it says so.
#
# 4. "PRICES AND SELECTION ARE CONFIRMED WITH THE SHOP." Nobody has confirmed
#    anything with this shop yet. That line is in the footer of the account
#    screen, which is exactly the kind of small print an owner reads closely,
#    and the answer to "when did I confirm this?" is not one we want to give
#    across a counter. The app already owns a true sentence for this and says
#    it on the checkout screen, so the footer says the same thing.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1 + 2. the discreet shelf, said once ----------------------------------
rep("""      <p>Lingerie, toys, couples and the care that goes with them. We don&rsquo;t
         put this one in the app &mdash; come in and ask at the counter.</p>
      <p class="es">Lencer&iacute;a, juguetes, parejas y el cuidado que va con eso.
         Esta secci&oacute;n no va en la app. Pasa y pregunta en el mostrador.</p>""",
"""      <p>Lingerie, toys, couples and the care that goes with them. We keep this one off the app. Come in and ask at the counter.</p>""")

# ---- 1. the rest of the dashes ---------------------------------------------
rep("""    <p class="ckfine pad">Pay at the counter and show a valid ID &mdash; 21+ on every pickup.
      Collect at ${STORE.street}. Pickup only; we don&rsquo;t ship or deliver.</p>""",
"""    <p class="ckfine pad">Pay at the counter and show a valid ID. 21+ on every pickup.
      Collect at ${STORE.street}. Pickup only; we don&rsquo;t ship or deliver.</p>""")

rep("""      <p class="ckfine">Staff call this name out at the counter. Add a number and we&rsquo;ll
        text you when the bag is ready &mdash; or leave it blank and watch this screen.</p>""",
"""      <p class="ckfine">Staff call this name out at the counter. Add a number and we&rsquo;ll
        text you when the bag is ready, or leave it blank and watch this screen.</p>""")

rep("""      <p class="ffsub">Choose up to two. Each one is applied strictly &mdash; a product with no published figure for what you pick is left out rather than guessed at.</p>""",
"""      <p class="ffsub">Choose up to two. Each one is applied strictly. A product with no published figure for what you pick is left out rather than guessed at.</p>""")

rep("""bring the piece &mdash; it takes a minute to fit it properly and beats guessing a joint size.</p>""",
    """bring the piece. It takes a minute to fit it properly and beats guessing a joint size.</p>""")

rep("""and we&rsquo;ll match it in a minute &mdash; guessing a joint size is how people end up with a part that doesn't seat.</p>""",
    """and we&rsquo;ll match it in a minute. Guessing a joint size is how people end up with a part that doesn't seat.</p>""")

rep("""    It does not reserve stock or lock a price &mdash; in-store pricing and any
    restrictions on the offer still apply at the register.</p>""",
"""    It does not reserve stock or lock a price, and in-store pricing and any
    restrictions on the offer still apply at the register.</p>""")

# ---- 3. the shop is open on Sunday -----------------------------------------
rep("""<span class="sb-item" id="sbOpen"><i class="dot"></i><b>Open 8 AM to 9 PM, Monday through Saturday.</b></span>""",
    """<span class="sb-item" id="sbOpen"><i class="dot"></i><b>Open 8 AM to 9 PM. Sundays 10 to 7.</b></span>""")

rep("""(520) 338-2119 &middot; Open 8 AM to 9 PM, Monday through Saturday.<br>""",
    """(520) 338-2119 &middot; Open 8 AM to 9 PM, Sundays 10 to 7.<br>""")

rep("""      <div class="idnote">Open 8 AM to 9 PM, Monday through Saturday.</div>""",
    """      <div class="idnote">Open 8 AM to 9 PM. Sundays 10 to 7.</div>""")

# ---- 4. the footer stops claiming a confirmation nobody gave ---------------
rep("""Prices and selection are confirmed with the shop, and the register is the final word at the counter.</p>""",
    """Selection and prices can change at the shop, and the register is the final word.</p>""")

# ---- Spanish for the strings that changed ----------------------------------
rep(""""Across the shelf":"En todo el estante"};""",
""""Across the shelf":"En todo el estante","Lingerie, toys, couples and the care that goes with them. We keep this one off the app. Come in and ask at the counter.":"Lencería, juguetes, parejas y el cuidado que va con eso. Esta sección no va en la app. Pasa y pregunta en el mostrador.","(520) 338-2119 · Open 8 AM to 9 PM, Sundays 10 to 7.":"(520) 338-2119 · Abierto de 8 AM a 9 PM, domingos de 10 a 7.","This shelf stays in store":"Esta sección se queda en la tienda","Built for Smokers Paradise by BorderLine AI. Every product shown is a real, listed product with the manufacturer’s own photography. Selection and prices can change at the shop, and the register is the final word.":"Hecha para Smokers Paradise por BorderLine AI. Cada producto que se muestra es un producto real y listado, con la fotografía de su propio fabricante. La selección y los precios pueden cambiar en la tienda, y la caja tiene la última palabra."};""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
