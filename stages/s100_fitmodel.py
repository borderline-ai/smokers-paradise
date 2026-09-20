#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 100 — the app learns what actually fits what.
#
# Marco: "It needs to be very accurate. For example I just saw a lighter
# recommended in the listing for the ELECTRIC nectar collector. Someone buying a
# dab rig is most likely NOT looking for a lighter. You should know how all of
# these things work and function and similar products that could help."
#
# Stage 99 fixed the four worst pairings by adding two more regexes. Auditing
# all 259 afterwards showed the approach itself is the problem. Still wrong:
#
#   Puffco Peak Pro 3DXL      -> a GRAV carb cap, a Pulsar carb cap, and a
#                                KALOUD HOOKAH BOWL
#   Lookah Seahorse           -> a Puffco travel case, which is moulded to a
#                                Puffco and fits nothing else
#   GRAV 12mm Taster          -> three different butane torches, for a glass
#                                one-hitter you light with a lighter
#   GRAV 14mm Quartz Banger   -> two bowls, two downstems and two ash catchers,
#                                when a banger IS the thing that replaces the
#                                bowl
#
# Every one of those is a category-level truth that is false about the product.
# A pile of regexes cannot tell a banger from a bowl, because at the level of
# words they are both glass things with 14mm in the name.
#
# SO THE APP GETS A MODEL INSTEAD. Every product is sorted into a KIND — what it
# is and how it is used — and each kind has an explicit list of the kinds that
# genuinely help it. That is the thing somebody behind a counter knows and a
# keyword list does not:
#
#   a glass dab rig is heated by a torch      an e-rig is heated by its battery
#   a banger replaces the bowl                so it never needs one
#   a carb cap caps a banger                  not an atomizer
#   a nectar collector has no joint at all    so no bowl, stem or ash catcher
#   a taster is lit with a lighter            a torch is for concentrates
#   a disposable is finished and thrown away  it takes no accessory at all
#
# AND FITTED PARTS ARE BRAND-LOCKED. A chamber, a coil, a pod, a charger and a
# moulded case fit one maker's device and nothing else, so they are only ever
# offered for that maker's device. A Puffco chamber is not an accessory to a
# Lookah; it is an accessory to a Puffco.
#
# When nothing honestly fits, the section says "More like this" and shows the
# same kind of product, which is always true.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- the category correction, keyed the way this table is keyed ------------
rep("""const CAT_CORRECTIONS = {
  rx142: 'dab',""",
"""const CAT_CORRECTIONS = {
  /* A $125 electronic device was filed under Glass Parts & Accessories, which
     is how it came to be offered a lighter: it inherited the bong rule. */
  'Lookah|Seahorse Queen Electric Nectar Collector': 'dab',""")

# ---- the model -------------------------------------------------------------
old_start = s.index("/* Every token is anchored on a word boundary.")
old_end = s.index("/* The Deals screen and the home rail render the same audited DEALCARDS list,")
new = r'''/* ==========================================================================
   WHAT FITS WHAT

   Two questions decide every recommendation, and neither of them can be
   answered by looking for words:

     1. WHAT KIND OF THING IS THIS, and how is it used?
     2. WHICH KINDS GENUINELY HELP IT?

   A banger and a bowl are both glass, both 14mm, both go on a bong. One
   replaces the other. A dab rig and an e-rig do the same job; one is heated by
   a torch and one by its own battery, so fire is an accessory to the first and
   a contradiction to the second. A nectar collector looks like a pipe and has
   no joint anywhere on it. None of that is visible in the product name, so the
   app is told it here, once, in the order a person behind the counter would
   say it.
   ========================================================================== */

/* The order matters: the first pattern that matches wins, so the specific
   things come before the general ones. */
const KIND_TESTS = [
  ['coil',      /\bcoils?\b|replacement (?:coil|pod)|pod pack|\bcartridges?\b/i],
  ['chamber',   /\bchambers?\b|atomi[sz]er|\bbucket\b|joystick cap/i],
  ['charger',   /\bchargers?\b|charging (?:dock|cable|cube)|\busb\b/i],
  ['case',      /travel (?:case|bag|pack)|carry(?:ing)? case|\bcases?\b|pouch bag/i],
  ['straw',     /nectar collector|honey straw|dab straw|seahorse|\bnectar\b/i],
  ['erig',      /puffco|peak\b|proxy|pivot|e.?rig|erig|electric.*(?:rig|collector|dab)|\bdragon egg\b/i],
  ['banger',    /\bbangers?\b|\bnails?\b|terp slurp|\bquartz\b(?!.*\bcap\b)|\binserts?\b/i],
  ['carbcap',   /carb cap|\bcaps?\b(?=.*(?:carb|bubble|vortex|terp))|terp pearls?/i],
  ['dabtool',   /dab tools?|dabbers?|\bscoops?\b|hot knife/i],
  ['torch',     /\btorch(?:es)?\b|butane|\bfuel\b/i],
  ['lighter',   /\blighters?\b|clipper|\bbic\b|zippo/i],
  ['downstem',  /\bdownstems?\b|\bstems?\b/i],
  ['ashcatcher',/ash catcher|ashcatcher/i],
  ['bowl',      /\bbowl(?: piece)?s?\b|\bslides?\b|\bfunnels?\b/i],
  ['screen',    /\bscreens?\b/i],
  ['onehitter', /\btaster\b|chillum|one.?hitter|\bdugout\b/i],
  ['handpipe',  /\bspoon\b|sherlock|gandalf|\bhand pipe\b|\bbubbler\b|\bpipe\b(?!.*water)/i],
  ['dabrig',    /\bdab rig\b|\brig\b|recycler/i],
  ['bong',      /\bbong\b|water pipe|\bbeaker\b|straight tube|\bperc\b|gravity/i],
  ['grinder',   /\bgrinders?\b|shredder/i],
  ['tray',      /rolling tray|\btrays?\b/i],
  ['papers',    /rolling papers?|\bpapers?\b|\bcones?\b|\bwraps?\b|\brolls?\b|blunt/i],
  ['cigars',    /\bcigars?\b|cigarillo|backwoods|swisher|\bdutch\b/i],
  ['tips',      /\btips?\b|\bfilters?\b(?!.*air)/i],
  ['cleaner',   /clean\w*|\biso\b|alcohol|\bswabs?\b|\bwipes?\b|formula 420/i],
  ['storage',   /\bjars?\b|storage|stash|\bcvault\b|smell.?proof|\bmats?\b/i],
  ['scale',     /\bscales?\b/i],
  ['charcoal',  /charcoal|\bcoals?\b/i],
  ['hose',      /\bhoses?\b|\btongs?\b|\bfoil\b/i],
  ['shisha',    /shisha|hookah tobacco|\bmolasses\b/i],
  ['hookah',    /\bhookah\b|\bnargile\b/i],
  ['airfilter', /air filter|smokebuddy|\bsploof\b/i]
];

/* Category is the fallback when the name says nothing useful. */
const CAT_KIND = {
  disp:'disposable', hard:'poddevice', eliq:'eliquid', nic:'pouch',
  dab:'erig', rig:'dabrig', water:'bong', hand:'handpipe', parts:'glasspart',
  roll:'papers', cig:'cigars', hook:'hookah', gear:'gear',
  snack:'snack', exotic:'exotic', love:'love'
};

function productKind(p){
  const t = (p.brand || '') + ' ' + (p.name || '');
  for(const [kind, re_] of KIND_TESTS) if(re_.test(t)) return kind;
  return CAT_KIND[p.cat] || 'other';
}

/* WHAT GENUINELY HELPS WHAT.
   Read each line as a sentence a person would say across a counter. An empty
   list means the honest answer is "nothing, it is complete" and the section
   falls through to More like this. */
const FITS = {
  /* a glass rig is heated by a flame, and the banger is the part that wears */
  dabrig:    ['banger','carbcap','dabtool','torch','cleaner','storage'],
  /* an e-rig is heated by its own battery: a torch here would be a contradiction */
  erig:      ['chamber','carbcap','dabtool','cleaner','case','charger','storage'],
  /* a straw has no joint anywhere on it, so nothing screws into it */
  straw:     ['dabtool','cleaner','storage','case'],
  banger:    ['carbcap','dabtool','torch','cleaner'],
  carbcap:   ['banger','dabtool','torch'],
  dabtool:   ['banger','carbcap','cleaner'],
  torch:     ['banger','dabtool','carbcap'],

  bong:      ['bowl','downstem','ashcatcher','screen','cleaner','lighter','grinder'],
  handpipe:  ['cleaner','grinder','lighter','screen','storage'],
  /* a one-hitter is lit with a lighter; a torch is for concentrates */
  onehitter: ['cleaner','grinder','lighter','storage'],
  bowl:      ['downstem','screen','cleaner','lighter'],
  downstem:  ['bowl','screen','cleaner'],
  ashcatcher:['bowl','downstem','cleaner'],
  screen:    ['bowl','cleaner'],
  glasspart: ['cleaner','bowl','downstem'],

  papers:    ['tips','tray','grinder','lighter'],
  cigars:    ['tray','grinder','lighter'],
  tips:      ['papers','tray','grinder'],
  tray:      ['grinder','papers','storage'],
  grinder:   ['tray','papers','storage'],

  hookah:    ['charcoal','hose','shisha','cleaner'],
  shisha:    ['charcoal','hose','hookah'],
  charcoal:  ['hose','shisha'],

  poddevice: ['coil','eliquid','charger','case'],
  eliquid:   ['poddevice','coil'],
  coil:      ['poddevice','eliquid'],
  chamber:   ['erig','cleaner','dabtool'],
  charger:   ['poddevice','erig'],

  /* Nothing is an accessory to these. A disposable is finished and thrown
     away; a pouch, a snack and a chocolate bar are eaten. Saying otherwise to
     sell one more thing is exactly the noise this app is supposed to replace. */
  disposable: [],
  pouch:      [],
  snack:      [],
  exotic:     [],
  love:       [],
  cleaner:    [],
  storage:    [],
  case:       [],
  airfilter:  [],
  scale:      [],
  gear:       [],
  other:      []
};

/* A part that fits ONE maker's fitting is only ever offered for that maker's
   device. A Puffco chamber is not an accessory to a Lookah. */
const BRAND_LOCKED = ['chamber','coil','charger','case'];

function companions(p){
  const kind = productKind(p);
  const wants = FITS[kind] || [];
  const label = (kind === 'erig' || kind === 'straw' || kind === 'dabrig'
                 || kind === 'poddevice') ? 'Keep it running' : 'Goes with this';
  if(wants.length){
    const hits = PRODUCTS.filter(x => {
      if(x.id === p.id || x.published === false) return false;
      const k = productKind(x);
      if(wants.indexOf(k) < 0) return false;
      if(BRAND_LOCKED.indexOf(k) >= 0 && x.brand !== p.brand) return false;
      return true;
    }).sort((a,b) => ((b.brand===p.brand)?1:0)-((a.brand===p.brand)?1:0)
                  || (wants.indexOf(productKind(a)) - wants.indexOf(productKind(b)))
                  || (b.featured?1:0)-(a.featured?1:0)
                  || a.price-b.price).slice(0, 6);
    if(hits.length >= 2) return {label, items: hits};
  }
  /* Nothing honestly fits it, so say the true thing instead: the same kind of
     product, the same maker first, then the nearest price. */
  const near = PRODUCTS.filter(x => x.id !== p.id && x.published !== false
                 && (productKind(x) === kind || x.cat === p.cat))
    .sort((a,b) => ((b.brand===p.brand)?1:0)-((a.brand===p.brand)?1:0)
                || Math.abs(a.price - p.price) - Math.abs(b.price - p.price)).slice(0, 6);
  return near.length >= 2 ? {label: 'More like this', items: near} : null;
}

'''
s = s[:old_start] + new + s[old_end:]
print('  ok: the recommendation engine is a fit model, not a keyword list')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
