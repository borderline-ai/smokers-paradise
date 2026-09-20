#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 96 — three promotions cut off mid-word on the home screen.
#
# `.ad-sub` is clamped to two lines. Three of the six deal cards write more
# than two lines into it, so the sentence ends in an ellipsis on the screen the
# app opens on:
#
#   "Monday to Wednesday. Spend $15 or more and spin the wheel at the…"
#   "Spend $10 or more and we'll write your name on a ticket. One entry per…"
#   "Pulsar, GRAV, Diamond Glass and Session, on the wall behind the counte…"
#
# and in Spanish, which is longer, two of the three clip harder.
#
# The spin card was also saying the same thing twice: the clamped sentence
# opened with "Monday to Wednesday" and the fine print eleven pixels below
# opened with "Monday to Wednesday" again. And both of them repeated the $15
# that is already set in 46px type in the offer block directly above.
#
# Every one of these cards has FOUR places to put a fact — the kicker, the
# offer block, the subtitle and the fine print — and each of the three was
# using the subtitle to repeat two of the others and then running out of room
# for the part only it could say. Written so each line says its own thing and
# all of it fits.
#
# Found by measuring scrollHeight against clientHeight on every clamped element
# on six screens in both languages, rather than by reading the cards, because
# an ellipsis at the end of a sentence is exactly the kind of thing the eye
# forgives and a shop owner does not.
import io
import json

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- the wheel: the days are the point, the $15 is already in 46px type ----
rep("""    subtitle:'Monday to Wednesday. Spend $15 or more and spin the wheel at the counter.',""",
    """    subtitle:'Monday to Wednesday. Spin the prize wheel at the counter.',""")
rep("""    badge:'', disclaimer:'Monday to Wednesday, in store. One spin per visit.',""",
    """    badge:'', disclaimer:'In store only. One spin per visit.',""")

# ---- the raffle: the mechanic in the subtitle, the limit in the fine print --
rep("""    subtitle:'Spend $10 or more and we\\u2019ll write your name on a ticket. One entry per visit.',""",
    """    subtitle:'Spend $10 or more and your name goes on a ticket.',""")
rep("""    badge:'', disclaimer:'In store only. 21+ only.',
    art:[],
    featured:false, active:true, endDate:null },

  { id:'d-glass', concept:'glass', layout:'hero',""",
"""    badge:'', disclaimer:'In store only. One entry per visit. 21+ only.',
    art:[],
    featured:false, active:true, endDate:null },

  { id:'d-glass', concept:'glass', layout:'hero',""")

# ---- the glass wall: the kicker already says Glass ------------------------
rep("""    subtitle:'Pulsar, GRAV, Diamond Glass and Session, on the wall behind the counter.',""",
    """    subtitle:'Pulsar, GRAV, Diamond Glass and Session, behind the counter.',""")

# ---- Spanish ---------------------------------------------------------------
NEW = {
 'Monday to Wednesday. Spin the prize wheel at the counter.':
   'De lunes a miércoles. Gira la ruleta de premios en el mostrador.',
 'In store only. One spin per visit.':
   'Solo en la tienda. Un giro por visita.',
 'Spend $10 or more and your name goes on a ticket.':
   'Gasta $10 o más y tu nombre va en un boleto.',
 'In store only. One entry per visit. 21+ only.':
   'Solo en la tienda. Una entrada por visita. Solo 21+.',
 'Pulsar, GRAV, Diamond Glass and Session, behind the counter.':
   'Pulsar, GRAV, Diamond Glass y Session, detrás del mostrador.',
}
i = s.index('const T_ES = ')
j = s.index(';\nconst T_EN', i)
cur = json.loads(s[i + len('const T_ES = '):j])
for k, v in NEW.items():
    cur[k] = v
s = s[:i] + 'const T_ES = ' + json.dumps(cur, ensure_ascii=False, separators=(',', ':')) + s[j:]
print('  ok: %d Spanish entries' % len(cur))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
