#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 152 — the tool stops filtering and starts recommending.
#
# Marco: "they recommend what is best depending on what they want and like."
#
# Stage 151 fixed the questions. This fixes the answer. What the tool said when
# it was finished asking was:
#
#     3 matches
#     Every one of these meets all of your requirements.
#     [card] [card] [card]
#
# Three cards, the same size, in a row, with no opinion between them. That is a
# search result. Ask the person behind the counter the same five questions and
# they do not hand you three boxes and walk away — they put ONE in your hand,
# tell you why that one, tell you what the other two do differently, and then
# tell you what you are going to need to go with it.
#
# ======================================================================
# THE ONE IN YOUR HAND
# ======================================================================
# The top match gets the big card and a sentence saying why it is the top match.
# That sentence is not written here, it is MEASURED against the other matches
# every time, so it cannot be flattery and cannot go stale:
#
#     the cheapest of the six that fit          (it holds the lowest price)
#     the longest-lasting of them               (it holds the highest puff count)
#     the only rechargeable one                 (it is alone in that)
#     the tallest of them                       (it holds the greatest height)
#
# If none of those is true of it, the sentence says the true thing instead: it
# is the closest to everything that was asked for. No superlative is printed
# unless the shelf proves it, and every one names the figure it comes from.
#
# ======================================================================
# WHY THIS ONE AND NOT THAT ONE
# ======================================================================
# Under the alternates, one line each, and again measured rather than written:
# the first real difference between that product and the top pick, out of price,
# puff count, height, size class, material, brand and flavor. "$6 less."
# "Holds 25,000 puffs instead of 15,000." "Silicone instead of glass." A
# customer can act on that. "Also a great choice" is not a difference.
#
# ======================================================================
# WHAT YOU WILL NEED WITH IT
# ======================================================================
# The last thing the counter does is tell you what else you need, and the app
# has known how to work that out since the fit map was built: a bong gets a
# bowl, a downstem and a screen; a dab rig gets a banger and a torch; an e-rig
# gets a chamber and a charger and never a torch, because it heats itself. That
# map is joint-aware and brand-locked already — it will not offer a 14 mm bowl
# for an 18 mm joint or a Puffco chamber for a Lookah — so the recommendation
# ends where the conversation ends, with the three things that go with it.
#
# Nothing is invented and nothing is pushed: a disposable, a pouch and a snack
# are finished products and the map gives them no companions, so for those the
# screen simply does not show that section.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


# ---- 1. the measured verdict and the measured difference -------------------
rep("""function ffResults(){""",
"""/* ======================================================================
   WHY THIS ONE. Measured against the other matches, never written in advance.
   Each candidate sentence is only produced when the shelf proves it, and the
   figure that proves it is named inside the sentence.
   ====================================================================== */
const ffNum = (v,k) => (v.attrs[k] && known(v.attrs[k]) && typeof v.attrs[k].value==='number')
  ? v.attrs[k].value : null;

function ffVerdict(top, all){
  const n = all.length;
  const others = all.filter(v=>v!==top);
  if(!others.length) return 'The only thing on the shelf that meets everything you asked for.';
  const of = 'of the ' + n + ' that fit';

  /* cheapest, and genuinely cheapest: a tie is not a superlative */
  const price = ffNum(top,'price');
  if(price!=null && others.every(v=>{const p=ffNum(v,'price'); return p==null || p>price}))
    return 'The cheapest ' + of + ', at ' + money(price) + '.';

  /* longest-lasting, where the maker publishes a puff count for all of them */
  const puffs = ffNum(top,'puffCount');
  if(puffs!=null && others.every(v=>{const p=ffNum(v,'puffCount'); return p==null || p<puffs}))
    return 'The longest-lasting ' + of + ', at ' +
      Number(puffs).toLocaleString() + ' puffs.';

  /* alone in something, which is the strongest thing a shelf can say */
  const alone = [
    ['rechargeable', 'the only rechargeable one'],
    ['temperatureControl', 'the only one with temperature control'],
    ['portable', 'the only one made to be carried'],
    ['nicotineFree', 'the only nicotine-free one']
  ].find(([k]) => known(top.attrs[k]) && top.attrs[k].value===true
    && others.every(v=>!(known(v.attrs[k]) && v.attrs[k].value===true)));
  if(alone) return 'It is ' + alone[1] + ' ' + of + '.';

  const h = ffNum(top,'heightIn');
  if(h!=null && others.every(v=>{const x=ffNum(v,'heightIn'); return x==null || x<h}))
    return 'The biggest ' + of + ', at ' + h + ' inches.';
  if(h!=null && others.every(v=>{const x=ffNum(v,'heightIn'); return x==null || x>h}))
    return 'The smallest ' + of + ', at ' + h + ' inches.';

  /* nothing is provably best, so say the true thing instead */
  return 'The closest ' + of + ' to everything you asked for.';
}

/* THE FIRST REAL DIFFERENCE between an alternate and the one being handed over.
   Price first, because it is the difference people act on, then the figures the
   makers publish, then what it is made of, then who made it. */
function ffDiffer(v, top){
  const pa = ffNum(v,'price'), pb = ffNum(top,'price');
  if(pa!=null && pb!=null && Math.abs(pa-pb) >= 1)
    return money(Math.abs(pa-pb)) + (pa<pb ? ' less.' : ' more.');

  const ua = ffNum(v,'puffCount'), ub = ffNum(top,'puffCount');
  if(ua!=null && ub!=null && ua!==ub)
    return Number(ua).toLocaleString() + ' puffs instead of ' + Number(ub).toLocaleString() + '.';

  const ha = ffNum(v,'heightIn'), hb = ffNum(top,'heightIn');
  if(ha!=null && hb!=null && Math.abs(ha-hb) >= 1)
    return ha + ' inches instead of ' + hb + '.';

  const ma = FF_VAL.mat(v), mb = FF_VAL.mat(top);
  if(ma && mb && ma!==mb)
    return ma.charAt(0).toUpperCase()+ma.slice(1) + ' instead of ' + mb + '.';

  const sa = FF_VAL.size(v), sb = FF_VAL.size(top);
  if(sa && sb && sa!==sb)
    return ((FF_SAY.size[sa]||[sa])[0]) + ' instead of ' + ((FF_SAY.size[sb]||[sb])[0]).toLowerCase() + '.';

  if(v.product.brand && top.product.brand && v.product.brand!==top.product.brand)
    return 'The same thing from ' + brandLabel(v.product.brand) + '.';

  if(v.variant && top.variant && v.variant!==top.variant)
    return v.variant + ' instead of ' + top.variant + '.';

  return 'Also meets everything you asked for.';
}

/* WHAT YOU WILL NEED WITH IT. The fit map is already joint-aware and locked to
   a maker's own fittings, so this only ever offers a part that really goes on
   the thing being recommended — and offers nothing at all for a product that
   honestly takes nothing, which is most of the vape shelf. */
function ffGoesWith(v){
  if(typeof companions !== 'function') return '';
  let c = null;
  try { c = companions(v.product) } catch(e){ return '' }
  if(!c || c.label === 'More like this' || !c.items || c.items.length < 2) return '';
  const items = c.items.slice(0,3);
  return `<div class="ffgoes">
    <b>${c.label === 'Keep it running' ? 'Keep it running' : "What you'll want with it"}</b>
    <small>Only parts that actually fit this one: the right joint, and the maker's own fittings.</small>
    <div class="ffgoes-r">${items.map(p=>`
      <button class="ffgoes-c" data-ffview="${p.id}">
        <span class="ffgoes-im">${art(p,'',true)}</span>
        <span class="ffgoes-nm">${esc(titleOf(p))}</span>
        <span class="ffgoes-pr">${p.priceKnown===false?'Ask':money(p.price)}</span>
      </button>`).join('')}</div>
  </div>`;
}

function ffResults(){""")

# ---- 2. the result screen itself -------------------------------------------
old = """  return `${ffProgress()}
    <h3>${r.matches.length} match${r.matches.length>1?'es':''}</h3>
    <p class="ffsub">${r.total>r.matches.length?`Showing the ${r.matches.length} closest of ${r.total} that met every requirement.`:'Every one of these meets all of your requirements.'}</p>
    <div class="ffres">${r.matches.map(v=>{"""
new = """  const top = r.matches[0];
  const rest = r.matches.slice(1);
  return `${ffProgress()}
    <h3>Here's what I'd hand you</h3>
    <p class="ffsub">${r.total>1
      ? `Out of the ${r.total} on this shelf that meet everything you said.`
      : 'The one thing on this shelf that meets everything you said.'}</p>

    ${/* THE ONE IN YOUR HAND */''}
    <div class="ffpick">
      <div class="ffpick-im">${top.variant?art(top.product,vslug(top.variant),true):art(top.product,'',true)}</div>
      <div class="ffpick-tx">
        <div class="ffc-br">${brandLabel(top.product.brand)}</div>
        <div class="ffpick-nm">${esc(titleOf(top.product))}</div>
        ${top.variant?`<div class="ffc-vr">${esc(top.variant)}</div>`:''}
        <div class="ffpick-pr">${known(top.attrs.price)?money(top.attrs.price.value):'Price at the counter'}</div>
      </div>
    </div>
    <p class="ffverdict">${ffVerdict(top, r.matches)}</p>
    <ul class="ffc-why">${top._reasons.map(x=>`<li>${x}</li>`).join('')}</ul>
    ${top._uncertain.length?`<div class="ffc-un">${top._uncertain.join(' ')}</div>`:''}
    <div class="ffc-act">
      <button class="ffbtn" data-ffview="${top.product.id}">View Product</button>
      <button class="ffbtn ghost" data-ffbag="${top.product.id}|${top.variant||''}">Add to Bag</button>
      ${top.product.cat==='disp'?`<button class="ffbtn ghost" data-ffcmp="${top.product.id}">Compare</button>`:''}
      <button class="ffbtn ghost" data-ffask="1">Ask In Store</button>
    </div>

    ${ffGoesWith(top)}

    ${/* AND WHAT THE OTHERS DO DIFFERENTLY */''}
    ${rest.length?`<div class="ffalts">
      <b>If you'd rather</b>
      <small>Each of these meets everything you asked for too. What is different about it is the line under it.</small>
      ${rest.map(v=>`<button class="ffalt" data-ffview="${v.product.id}">
        <span class="ffalt-im">${v.variant?art(v.product,vslug(v.variant),true):art(v.product,'',true)}</span>
        <span class="ffalt-tx">
          <b>${brandLabel(v.product.brand)} ${esc(titleOf(v.product))}</b>
          ${v.variant?`<i>${esc(v.variant)}</i>`:''}
          <u>${known(v.attrs.price)?money(v.attrs.price.value):'Price at the counter'}</u>
          <em>${ffDiffer(v, top)}</em>
        </span></button>`).join('')}
    </div>`:''}

    <div class="ffdisc">Recommendations are based on published specifications and flavor
      descriptions, not a guarantee of personal preference. Anyone at the counter will
      tell you the same thing in person.</div>`;
  return `${''}
    <div class="ffres">${r.matches.map(v=>{"""
rep(old, new)

# the old card loop is now unreachable, so it goes
i = s.index("""  return `${''}
    <div class="ffres">${r.matches.map(v=>{""")
j = s.index("""    <div class="ffdisc">Recommendations are based on product specifications and flavor descriptions, not a guarantee of personal preference.</div>`;
}""")
s = s[:i] + "}" + s[j + len("""    <div class="ffdisc">Recommendations are based on product specifications and flavor descriptions, not a guarantee of personal preference.</div>`;
}"""):]
print('  ok: the old three-equal-cards loop removed')

# ---- 3. the look of it ------------------------------------------------------
rep(""".ffdisc{""",
""".ffpick{display:flex;gap:13px;align-items:center;background:var(--card2);
  border:1px solid rgba(255,47,168,.32);border-radius:16px;padding:13px;margin:2px 0 0;
  box-shadow:0 0 0 1px rgba(255,47,168,.10),0 10px 30px -18px rgba(255,47,168,.55)}
.ffpick-im{width:104px;height:104px;flex:none;display:grid;place-items:center;
  background:var(--card);border-radius:12px;overflow:hidden}
.ffpick-im img{width:88%;height:88%;object-fit:contain}
.ffpick-tx{min-width:0;flex:1}
.ffpick-nm{font-size:17px;font-weight:750;line-height:1.2;color:var(--ink);margin-top:2px}
.ffpick-pr{font-family:var(--mono);font-size:16px;font-weight:700;color:var(--ink);margin-top:6px}
.ffverdict{margin:11px 2px 4px;font-size:14px;line-height:1.45;color:var(--ink)}
.ffgoes{margin:16px 0 4px;border-top:1px solid var(--line);padding-top:14px}
.ffgoes b{display:block;font-size:14px;color:var(--ink)}
.ffgoes small{display:block;color:var(--muted);font-size:11.5px;margin:3px 0 10px;line-height:1.4}
.ffgoes-r{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.ffgoes-c{display:flex;flex-direction:column;gap:5px;align-items:center;text-align:center;
  background:var(--card);border:1px solid var(--line);border-radius:12px;padding:9px 6px;
  color:var(--ink);font:inherit;cursor:pointer}
.ffgoes-im{width:100%;aspect-ratio:1;display:grid;place-items:center;overflow:hidden}
.ffgoes-im img{width:86%;height:86%;object-fit:contain}
.ffgoes-nm{font-size:11px;line-height:1.25;display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;overflow:hidden}
.ffgoes-pr{font-family:var(--mono);font-size:11px;color:var(--muted)}
.ffalts{margin:16px 0 4px;border-top:1px solid var(--line);padding-top:14px}
.ffalts>b{display:block;font-size:14px;color:var(--ink)}
.ffalts>small{display:block;color:var(--muted);font-size:11.5px;margin:3px 0 10px;line-height:1.4}
.ffalt{display:flex;gap:11px;align-items:center;width:100%;text-align:left;margin-bottom:8px;
  background:var(--card);border:1px solid var(--line);border-radius:14px;padding:10px;
  color:var(--ink);font:inherit;cursor:pointer}
.ffalt-im{width:56px;height:56px;flex:none;display:grid;place-items:center;overflow:hidden}
.ffalt-im img{width:90%;height:90%;object-fit:contain}
.ffalt-tx{min-width:0;display:flex;flex-direction:column;gap:2px}
.ffalt-tx b{font-size:13px;font-weight:650;line-height:1.25}
.ffalt-tx i{font-style:normal;font-size:11px;color:var(--muted)}
.ffalt-tx u{text-decoration:none;font-family:var(--mono);font-size:12.5px}
.ffalt-tx em{font-style:normal;font-size:11.5px;color:var(--brand);line-height:1.35}
.ffdisc{""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
