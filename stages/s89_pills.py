#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 89 — the last five chips, said properly.
#
# All fifteen "What We Carry" chips were pressed one at a time and the app was
# asked where each one landed. Ten open a shelf or a search that returns real
# products. The other five fell through to one generated sentence, and the
# generated sentence was the problem:
#
#     toast('We carry ' + label.toLowerCase() + ' in the shop. ...')
#
#   CBD       -> "We carry cbd in the shop."        the brand is CBD, not cbd
#   Spiritual -> "We carry spiritual in the shop."  not a sentence
#   Raffles   -> "We carry raffles in the shop. It is not on the app shelf
#                 yet, so ask for it at the counter."
#
# The raffle one is the worst of the three: a raffle is not something the shop
# carries, it is something the shop runs, it IS in the app, and the app has a
# card for it on the deals screen. So the chip was telling a customer to go ask
# at the counter about a thing that was two taps away.
#
# This is the same fault Marco pressed a button and found on the entrance
# offer: a control that goes SOMEWHERE rather than where it says. Lowercasing
# a label into a template is how you get four right answers and one absurd one.
# Each of the five now has its own line, written out, and Raffles goes to the
# raffle card.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""const SHELF_PILL = {"Glass":"water","E-Juice & Devices":"eliq","Disposables":"disp","Mushroom Chocolate":"exotic","Love":"love","Papers & Wraps":"roll","Vaporizers":"hard"};
const FIND_PILL  = {"Torches":"torch","Rolling Trays":"tray","Silicone":"silicone"};
function pillGo(label){
  const cat = SHELF_PILL[label];
  if(cat && CATS.some(c=>c[0]===cat)){ go('cat', cat); return }
  const q = FIND_PILL[label];
  if(q){ openSearchFor(q); return }
  toast('We carry ' + label.toLowerCase() + ' in the shop. It is not on the app '
      + 'shelf yet, so ask for it at the counter.');
}""",
"""const SHELF_PILL = {"Glass":"water","E-Juice & Devices":"eliq","Disposables":"disp","Mushroom Chocolate":"exotic","Love":"love","Papers & Wraps":"roll","Vaporizers":"hard"};
const FIND_PILL  = {"Torches":"torch","Rolling Trays":"tray","Silicone":"silicone"};
/* A chip for something that is on a screen goes to that screen. */
const VIEW_PILL  = {"Raffles":"deals"};
/* And a chip for something the shop stocks that the app does not list yet says
   so in its own words. A template that lowercases the label produced "We carry
   cbd in the shop" and "We carry spiritual in the shop", which is four right
   answers and two wrong ones. Five lines is cheaper than one clever line. */
const ASK_PILL = {
  "CBD":       'We keep CBD behind the counter: tinctures, gummies, flower and '
             + 'topicals. It is not on the app shelf yet, so ask us for it.',
  "Kratom":    'Kratom is one of the things people come to us for, and it is not '
             + 'on the app shelf yet. Ask at the counter and we will show you '
             + 'what is in.',
  "Spiritual": 'Candles, incense, sage and the rest of the spiritual shelf are in '
             + 'the shop, not in the app. Ask at the counter.',
  "Scales":    'We keep digital scales at the counter. They are not on the app '
             + 'shelf yet, so ask us and we will bring them out.'
};
function pillGo(label){
  const cat = SHELF_PILL[label];
  if(cat && CATS.some(c=>c[0]===cat)){ go('cat', cat); return }
  const v = VIEW_PILL[label];
  if(v){ go(v); return }
  const q = FIND_PILL[label];
  if(q){ openSearchFor(q); return }
  toast(ASK_PILL[label] || ('We carry this in the shop. It is not on the app '
      + 'shelf yet, so ask for it at the counter.'));
}""")

# ---- Spanish for the four asks ---------------------------------------------
import json
i = s.index('const T_ES = ')
j = s.index(';\nconst T_EN', i)
cur = json.loads(s[i + len('const T_ES = '):j])
NEW = {
 'We keep CBD behind the counter: tinctures, gummies, flower and topicals. '
 'It is not on the app shelf yet, so ask us for it.':
 'El CBD lo tenemos detrás del mostrador: tinturas, gomitas, flor y tópicos. '
 'Todavía no está en el estante de la app, así que pídenoslo.',
 'Kratom is one of the things people come to us for, and it is not on the app '
 'shelf yet. Ask at the counter and we will show you what is in.':
 'El kratom es una de las cosas por las que la gente viene, y todavía no está '
 'en el estante de la app. Pregunta en el mostrador y te enseñamos lo que hay.',
 'Candles, incense, sage and the rest of the spiritual shelf are in the shop, '
 'not in the app. Ask at the counter.':
 'Las veladoras, el incienso, la salvia y el resto del estante espiritual están '
 'en la tienda, no en la app. Pregunta en el mostrador.',
 'We keep digital scales at the counter. They are not on the app shelf yet, '
 'so ask us and we will bring them out.':
 'Las básculas digitales las tenemos en el mostrador. Todavía no están en el '
 'estante de la app, así que pídenoslas y te las sacamos.',
}
for k, v in NEW.items():
    cur.setdefault(k, v)
s = s[:i] + 'const T_ES = ' + json.dumps(cur, ensure_ascii=False, separators=(',', ':')) + s[j:]
print('  ok: %d Spanish entries' % len(cur))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
