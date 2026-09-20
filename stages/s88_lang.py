#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 88 — the Spanish that was written and never appeared.
#
# THE BUG. applyLang builds its lookup key by collapsing the whitespace in a
# text node:
#
#     const key = raw.replace(/\s+/g,' ').trim();
#
# and then writes the translation back with:
#
#     node.nodeValue = raw.replace(key, hit)
#
# If the sentence in the template runs over two lines, which most of the long
# ones do, then `raw` still holds the newline and the indent, `key` does not,
# and `raw.replace(key, hit)` finds nothing to replace. It fails silently: no
# error, no warning, and the node keeps its English while the dictionary sits
# there holding a perfectly good Spanish sentence that nobody ever sees.
#
# Found by switching the app to Spanish and reading every screen back looking
# for English, rather than by counting dictionary entries. The nicotine notice
# at the foot of every shelf, the line about not shipping, and others were all
# translated months ago and all still in English. The fix keeps whatever
# indentation the node had and puts the translation between it.
#
# AND THE ENTRIES THAT WERE GENUINELY MISSING: the Puffco panel on the home
# screen, three captions on the feed row, the whole discreet shelf, and the
# sentence about what saving an offer does. Twelve in all, plus one flavour
# list whose only English word was the "and" joining the last two flavours.
#
# ONE MORE EM DASH IN CUSTOMER COPY, in a feed caption, written as a literal
# character rather than an entity, which is why the entity sweep in stage 87
# did not catch it.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. a sentence that wraps in the template still gets translated --------
rep("""  jobs.forEach(([node, raw, key]) => {
    if(LANG === 'es'){
      const hit = T_ES[key];
      if(hit && !node.__en){ node.__en = raw; node.nodeValue = raw.replace(key, hit) }
    } else {
      if(node.__en){ node.nodeValue = node.__en; node.__en = null; return }
      const hit = T_EN[key];
      if(hit){ node.__es = raw; node.nodeValue = raw.replace(key, hit) }
    }
  });""",
"""  /* The key has its whitespace collapsed so that a sentence written over two
     lines in the template still matches the dictionary. That means the key is
     usually NOT a substring of the raw node, and raw.replace(key, hit) then
     replaces nothing at all, silently. Keep the node's own leading and
     trailing whitespace, which is what the layout depends on, and put the
     translation between them. */
  const swap = (raw, key, hit) => {
    if(raw.indexOf(key) >= 0) return raw.replace(key, hit);
    const lead = (raw.match(/^\\s*/) || [''])[0];
    const tail = (raw.match(/\\s*$/) || [''])[0];
    return lead + hit + tail;
  };
  jobs.forEach(([node, raw, key]) => {
    if(LANG === 'es'){
      const hit = T_ES[key];
      if(hit && !node.__en){ node.__en = raw; node.nodeValue = swap(raw, key, hit) }
    } else {
      if(node.__en){ node.nodeValue = node.__en; node.__en = null; return }
      const hit = T_EN[key];
      if(hit){ node.__es = raw; node.nodeValue = swap(raw, key, hit) }
    }
  });""")

# ---- 2. the feed caption loses its dash -------------------------------------
rep("cap:'Off-Stamp Crystal Cube " + chr(92) + "u2014 2 for $10, 3 for $12'",
    "cap:'Off-Stamp Crystal Cube, 2 for $10 or 3 for $12'")

# ---- 3. the entries that were never written --------------------------------
NEW = {
    # the Puffco panel on the home screen
    "Puffco at Smokers Paradise": "Puffco en Smokers Paradise",
    "See the Puffco shelf": "Ver el estante de Puffco",
    "The current Puffco line and the chambers and glass that go with it.":
        "La línea actual de Puffco, con sus cámaras y su vidrio.",
    # the feed row
    "Torches and lighters": "Sopletes y encendedores",
    "Off-Stamp Crystal Cube, 2 for $10 or 3 for $12":
        "Off-Stamp Crystal Cube, 2 por $10 o 3 por $12",
    # the discreet shelf
    "In store · 21+": "En la tienda · 21+",
    "Discreet · 21+": "Discreto · 21+",
    "Call the shop": "Llama a la tienda",
    "21+ only. Valid ID at the counter.":
        "Solo 21+. Identificación válida en el mostrador.",
    "Back to the shelf": "Volver al estante",
    "Lingerie": "Lencería", "Toys": "Juguetes",
    "Couples": "Parejas", "Care": "Cuidado",
    # what saving an offer actually does
    "Saving an offer keeps it on this screen so you can find it at the counter. "
    "It does not reserve stock or lock a price, and in-store pricing and any "
    "restrictions on the offer still apply at the register.":
        "Guardar una oferta la deja en esta pantalla para que la encuentres en el "
        "mostrador. No aparta producto ni congela un precio, y el precio de la "
        "tienda y cualquier restricción de la oferta siguen aplicando en la caja.",
    # the flavour list: the flavours keep their names, the joining word does not
    "Peanut Butter, Fruity Cereal, Chocolate Crunch, Cookies & Cream and Chocolate Milk.":
        "Peanut Butter, Fruity Cereal, Chocolate Crunch, Cookies & Cream y Chocolate Milk.",
    "Pineapple Coconut, Polar Mint, Strawberry Watermelon and the rest of the NERA run.":
        "Pineapple Coconut, Polar Mint, Strawberry Watermelon y el resto de la serie NERA.",
}

import json
i = s.index('const T_ES = ')
j = s.index(';\nconst T_EN', i)
cur = json.loads(s[i + len('const T_ES = '):j])
added = 0
for k, v in NEW.items():
    if k not in cur:
        cur[k] = v
        added += 1
s = s[:i] + 'const T_ES = ' + json.dumps(cur, ensure_ascii=False, separators=(',', ':')) + s[j:]
print('  ok: %d new Spanish entries, %d in the dictionary' % (added, len(cur)))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
