#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 148 — the spec line that was cut in half on twenty four cards.
#
# Nobody had ever asked whether TEXT was being clipped. cropcheck.py asks it of
# pictures; test/cliptext.py now asks it of words, and the first run came back
# with twenty four:
#
#     '4mm thick heat-tempered borosilicate glass in De'   413px past the box
#     'Anodized aluminum cup, ceramic 3D Chamber and te'   400px
#     'Quartz coils with anti-slip housing'                 77px
#     'Soft silicone mouthpiece'                             8px
#
# Every one of them is the same thing: the product card's spec row is a single
# 10px mono line 141px wide, and when a product has no height, joint, size,
# nicotine figure or battery published, the card falls back to the maker's
# MATERIAL sentence — which is a sentence, not a spec. 141px holds about
# twenty two characters of that font, so a seventy four character sentence is
# shown as its first third with an ellipsis: "4mm thick heat-tempered borosi…".
#
# The ellipsis is the reason no test caught it and the reason it still has to be
# fixed. It does not look broken, it looks careless, which is worse on a card
# next to a price.
#
# WHAT IT IS NOT. It is not a wrapping problem. Letting the row run to two
# lines changes the height of every card in the app on the morning of the demo,
# for a line of small print. And it is not a truncation problem either: cutting
# at a word instead of mid-word still throws away the useful half.
#
# WHAT IT IS. A card wants the material, not the sentence about the material.
# So the sentence is condensed to the material it names, out of its own words:
#
#     4mm thick heat-tempered borosilicate glass with removable silicone accents
#         -> 4mm borosilicate        (thickness stated before the material)
#     Anodized aluminum cup, ceramic 3D Chamber and terp pearls, silicone foot
#         -> Anodized aluminum       (the FIRST material named, with its adjective)
#     Platinum-cured silicone with borosilicate glass bowl
#         -> Silicone                ("Platinum-cured silicone" is 23, one over)
#     Natural broadleaf tobacco wrapper       -> Tobacco wrapper
#     Organic Cordia leaf with cornhusk tips  -> Organic Cordia leaf
#     Heavy-wall smoked glass                 -> Smoked glass
#     Shatterproof stainless steel and silicone -> Stainless steel
#
# Three rules make it honest rather than merely short:
#
#   1. THE EARLIEST MATERIAL WINS, not a favourite from a list. "Platinum-cured
#      silicone with borosilicate glass bowl" is a silicone bong with a glass
#      bowl, so it reads Silicone. Ranking glass above silicone would have
#      called it a glass piece, which it is not.
#   2. A THICKNESS COUNTS ONLY IF IT IS STATED BEFORE THE MATERIAL. "4mm thick
#      heat-tempered borosilicate" is 4mm borosilicate. "Borosilicate glass,
#      7mm thick chamber / 4mm thick neck" is NOT 7mm borosilicate — the 7mm is
#      one part of it — so that one keeps the plain material.
#   3. "TOBACCO-FREE" IS NOT TOBACCO. Without that, "Organic hemp, tobacco-free"
#      condenses to "Tobacco leaf", which is the exact opposite of what the
#      maker printed on the packet. It reads Organic hemp.
#
# A string already short enough is left exactly as the maker wrote it, so the
# twenty six products whose material is the two words "Borosilicate glass" are
# untouched. Nothing is invented and nothing is rounded: every output is a
# phrase lifted from the maker's own sentence. Run against all 93 published
# material fields in the catalogue, every result fits the line, and the product
# page still prints the full sentence — this is the CARD only.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:70].replace('\n', ' '))


# ---- the condenser ---------------------------------------------------------
rep("""function specs(p){""",
"""/* A MAKER'S MATERIAL SENTENCE, CUT DOWN TO THE MATERIAL.
   The card's spec row is one 141px line of 10px mono, about 22 characters.
   Anything longer was being shown as its first third with an ellipsis. This
   takes the material the sentence names, in the maker's own words, and never
   in more than 22 characters. See scripts/s148_specline.py for the three
   rules that keep it honest. */
const SPEC_LINE = 22;
const SPEC_MATS = [/borosilicate/, /quartz/, /silicone/, /ceramic/,
  /stainless steel/, /aluminum/, /nylon/, /cordia/, /tobacco(?!-free)/,
  /hemp/, /papers?/, /glass/, /walnut/];
const SPEC_HEADS = ['glass','leaf','paper','steel','nylon','wrapper','tubing'];
function shortSpec(t){
  t = String(t || '').trim();
  if(t.length <= SPEC_LINE) return t;              /* the maker's own words */
  const low = t.toLowerCase();
  let at = -1, end = -1;
  SPEC_MATS.forEach(re=>{                          /* the EARLIEST material */
    const m = low.match(re);
    if(m && (at < 0 || m.index < at)){ at = m.index; end = m.index + m[0].length; }
  });
  if(at < 0){                                      /* no material named at all */
    let c = t.split(/[,(\\/]| with | in | and /)[0].trim();
    while(c.length > SPEC_LINE && c.indexOf(' ') > 0) c = c.slice(0, c.lastIndexOf(' '));
    return c;
  }
  /* a thickness counts only where the maker states it before the material */
  const mm = low.slice(0, at).match(/(\\d+(?:\\.\\d+)?)\\s*mm/);
  if(mm){
    const kind = low.slice(at, end).indexOf('boro') === 0 ? 'borosilicate'
               : (low.slice(at, end) === 'glass' ? 'glass' : '');
    if(kind && (mm[1] + 'mm ' + kind).length <= SPEC_LINE) return mm[1] + 'mm ' + kind;
  }
  /* run on over the head noun the material belongs to: tobacco WRAPPER */
  for(;;){
    const m = t.slice(end).match(/^\\s+([A-Za-z]+)/);
    if(!m) break;
    const w = m[1].toLowerCase();
    if(!SPEC_HEADS.some(h => h === w || h + 's' === w)) break;
    end += m[0].length;
  }
  let core = t.slice(at, end).trim();
  const adj = t.slice(0, at).match(/([A-Za-z][A-Za-z\\-]*)\\s+$/);
  if(adj && (adj[1] + ' ' + core).length <= SPEC_LINE)
    return (adj[1] + ' ' + core).replace(/^./, c=>c.toUpperCase());
  while(core.length > SPEC_LINE && core.indexOf(' ') > 0)
    core = core.slice(0, core.lastIndexOf(' '));
  return core.replace(/^./, c=>c.toUpperCase());
}

function specs(p){""")

rep("""    if(!sp.length && r.material) sp.push(r.material);""",
    """    if(!sp.length && r.material) sp.push(shortSpec(r.material));""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
