#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 101 — the fit model, audited against all 259 and corrected four ways.
#
# The model from stage 100 got the big things right and then made four mistakes
# of its own, all of them the same mistake: a word that means two things.
#
# 1. "JAR" IS NOT ALWAYS STORAGE. "Adalya Hookah Tobacco - 250 Gram Jar" was
#    being classed as storage, so a nectar collector was offered a jar of
#    shisha. The hookah kinds now come before the storage kind, and storage no
#    longer answers to a jar that is sold by the gram.
#
# 2. "BOWL" IS NOT ALWAYS A BONG BOWL. The Kaloud Samsaris Kore Ceramic HOOKAH
#    Bowl was being offered as the bowl for a Session Goods bong. A hookah bowl
#    holds shisha over charcoal. It gets its own kind.
#
# 3. "FILTER" IS NOT ALWAYS A ROLLING TIP. The Smokebuddy Personal Air Filter
#    was being classed as tips and offered with rolling papers. It is a sploof.
#
# 4. A PART THAT FITS ONE LINE IS NOT A PART FOR THE WHOLE BRAND. Brand-locking
#    chambers stopped a Puffco chamber being offered for a Lookah, but inside
#    Puffco it still offered a Peak Pro a Proxy chamber and a Pivot chamber.
#    Peak, Peak Pro, Proxy and Pivot are four different devices. A fitted part
#    now has to match the device LINE, not just the maker.
#
# AND A REAL FITTING RULE. Bowls, downstems and ash catchers are cut to a joint
# size and the catalogue prints it: 10mm, 14mm, 18mm, 19mm. Where both the
# product and the candidate state a size, they now have to be the same size.
# That is not a guess about compatibility, it is the number on the label.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1, 2, 3: the words that mean two things -------------------------------
rep(r"""  ['screen',    /\bscreens?\b/i],""",
    r"""  ['screen',    /\bscreens?\b/i],
  /* before the general kinds below: a hookah bowl is not a bong bowl, a jar of
     shisha sold by the gram is not a storage jar, and a personal air filter is
     not a rolling tip */
  ['hookahbowl',/hookah bowl|shisha bowl|samsaris|\bphunnel\b|\bvortex bowl\b/i],
  ['airfilter', /air filter|smokebuddy|\bsploof\b/i],
  ['shisha',    /shisha|hookah tobacco|\bmolasses\b/i],
  ['charcoal',  /charcoal|\bcoals?\b/i],
  ['hookah',    /\bhookah\b|\bnargile\b/i],""")

rep(r"""  ['storage',   /\bjars?\b|storage|stash|\bcvault\b|smell.?proof|\bmats?\b/i],""",
    r"""  /* a jar sold by the gram is a jar OF something, not a jar to put things in */
  ['storage',   /\bjars?\b(?!.*\bgram)|storage|stash|\bcvault\b|smell.?proof|\bmats?\b/i],""")

rep(r"""  ['charcoal',  /charcoal|\bcoals?\b/i],
  ['hose',      /\bhoses?\b|\btongs?\b|\bfoil\b/i],
  ['shisha',    /shisha|hookah tobacco|\bmolasses\b/i],
  ['hookah',    /\bhookah\b|\bnargile\b/i],
  ['airfilter', /air filter|smokebuddy|\bsploof\b/i]
];""",
    r"""  ['hose',      /\bhoses?\b|\btongs?\b|\bfoil\b/i]
];""")

# ---- the hookah bowl belongs to the hookah, not to the bong ----------------
rep("""  hookah:    ['charcoal','hose','shisha','cleaner'],
  shisha:    ['charcoal','hose','hookah'],
  charcoal:  ['hose','shisha'],""",
"""  hookah:    ['charcoal','hose','shisha','hookahbowl','cleaner'],
  shisha:    ['charcoal','hose','hookahbowl','hookah'],
  charcoal:  ['hose','shisha','hookahbowl'],
  hookahbowl:['charcoal','shisha','hose'],
  airfilter: [],""")

# ---- 4: a fitted part has to match the device line, and the joint size ------
rep("""/* A part that fits ONE maker's fitting is only ever offered for that maker's
   device. A Puffco chamber is not an accessory to a Lookah. */
const BRAND_LOCKED = ['chamber','coil','charger','case'];""",
"""/* A part that fits ONE maker's fitting is only ever offered for that maker's
   device. A Puffco chamber is not an accessory to a Lookah. */
const BRAND_LOCKED = ['chamber','coil','charger','case'];

/* And not even the whole maker. Peak, Peak Pro, Proxy and Pivot are four
   different devices from one company, and a Proxy chamber does not go in a Peak
   Pro. Where a product names its line, a fitted part has to name the same one. */
const DEVICE_LINES = [
  'peak pro','peak','proxy','pivot','seahorse','dragon egg',
  'caliburn','xros','novo','wenax','xlim','ursa'
];
function deviceLine(p){
  const t = ((p.brand || '') + ' ' + (p.name || '')).toLowerCase();
  return DEVICE_LINES.find(l => t.indexOf(l) >= 0) || '';
}

/* Bowls, downstems and ash catchers are cut to a joint size, and the catalogue
   prints it. Where both sides state a size, it has to be the same size. This is
   not a guess about what fits: it is the number on the label. */
const JOINT_FITTED = ['bowl','downstem','ashcatcher','banger'];
function jointSize(p){
  const m = ((p.name || '') + '').match(/\\b(10|14|18|19)\\s?mm\\b/i);
  return m ? m[1] : '';
}""")

rep("""      if(BRAND_LOCKED.indexOf(k) >= 0 && x.brand !== p.brand) return false;
      return true;""",
"""      if(BRAND_LOCKED.indexOf(k) >= 0){
        if(x.brand !== p.brand) return false;
        const lp = deviceLine(p), lx = deviceLine(x);
        if(lp && lx && lp !== lx) return false;
      }
      if(JOINT_FITTED.indexOf(k) >= 0){
        const jp = jointSize(p), jx = jointSize(x);
        if(jp && jx && jp !== jx) return false;
      }
      return true;""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
