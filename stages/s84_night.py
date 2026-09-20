#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 84 — the overnight pass.
#
# Three things found by pressing all 555 controls and auditing every image on
# every screen with the network switched off.
#
# 1. THE NICOTINE WARNING IS BACK, ON THE SECOND HERO SLIDE. The earlier pass
#    cropped the device out of the carton for the three products that LEAD a
#    campaign. Every campaign also carries a BACK product standing behind the
#    lead, and those were never done: Lost Mary MO20000 Pro and Geek Bar
#    Pulse X2 50K are both cartons with WARNING: THIS PRODUCT CONTAINS NICOTINE
#    printed across the front, and on the Lost Mary slide it is the most
#    readable thing on the banner. Same crop, same rule, applied to the halves
#    that were missed. Off-Stamp's SW9000 was already a device on its own.
#
# 2. THE TWO SWITCHES IN YOUR ACCOUNT HAVE NO NAME. They work: the state flips
#    and the switch moves. But they are bare <button>s with no aria-label, no
#    role and no aria-checked, so a screen reader announces "button", twice,
#    with nothing to say which is text alerts and which is order alerts, and no
#    way to know whether either is on.
#
# 3. THE BRAND IS TRĒ HOUSE, AND THE APP SAYS BOTH. The banner kicker reads
#    "TRĒ House · Exotic Snacks" and every product card underneath it reads
#    "TRE HOUSE". The catalogue key has to stay "TRE House" because the image
#    table, the deal art and the ticker all resolve through it, so the macron
#    goes on at the moment the name is printed and nowhere else.
import io
import json
import base64

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


# ---- 1. the two back products lose their cartons ---------------------------
extra = {}
# gb2 was re-cropped once more: the first cut at column 127 kept a pale
# sliver of the carton's cyan edge running the full height of the device,
# which showed on the banner as a thin blue line beside it. 142 is the
# device's own edge.
for pid, tag in [('rx088', 'lm2'), ('disp3', 'gb2')]:
    with open('/tmp/spback/dev-%s.webp' % tag, 'rb') as f:
        extra[pid] = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()

i = s.index('const HERO_DEVICE = ')
j = s.index(';\n', i)
cur = json.loads(s[i + len('const HERO_DEVICE = '):j])
cur.update(extra)
s = s[:i] + 'const HERO_DEVICE = ' + json.dumps(cur, separators=(',', ':')) + s[j:]
print('  ok: HERO_DEVICE now holds %d devices (%s added)'
      % (len(cur), ', '.join(extra)))

# ---- 2. the switches say what they are -------------------------------------
rep("""      <button class="sw ${S.notif?'on':''}" data-tog="notif"></button></div>""",
"""      <button class="sw ${S.notif?'on':''}" data-tog="notif" type="button"
        role="switch" aria-checked="${S.notif?'true':'false'}"
        aria-label="Order alerts"></button></div>""")

n_sms = s.count("""<button class="sw ${S.sms?'on':''}" data-tog="sms"></button>""")
if n_sms:
    s = s.replace("""<button class="sw ${S.sms?'on':''}" data-tog="sms"></button>""",
"""<button class="sw ${S.sms?'on':''}" data-tog="sms" type="button"
        role="switch" aria-checked="${S.sms?'true':'false'}"
        aria-label="Deal alerts by text"></button>""")
    print('  ok: the text-alerts switch is named')
else:
    print('  !! the sms switch markup did not match; left alone')

# ---- 3. the brand keeps its macron where it is printed ---------------------
rep("""      <div class="br">${p.brand}</div><div class="nm">${p.name}</div>""",
"""      <div class="br">${brandLabel(p.brand)}</div><div class="nm">${p.name}</div>""")

rep("""function art(p, vkey, strict){""",
"""/* The catalogue key and the printed name are not the same string. Every image
   record, every deal's art list and one line of the ticker resolve through
   "TRE House", so the key stays exactly as it is and the macron goes on at the
   moment a customer reads it. The banner over these products has always said
   TRĒ House; the cards under it said TRE HOUSE. */
const BRAND_LABEL = {'TRE House': 'TR\\u0112 House'};
function brandLabel(b){ return BRAND_LABEL[b] || b || '' }

function art(p, vkey, strict){""")

# the product page prints it too
rep("""    <div class="eyebrow" style="margin-top:15px">${p.brand}</div>""",
    """    <div class="eyebrow" style="margin-top:15px">${brandLabel(p.brand)}</div>""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
