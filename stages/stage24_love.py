#!/usr/bin/env python3
# Stage 24 — the Love shelf, and discreet pickup.
#
# The point of this shelf is not that it exists. It is that a customer can buy
# from it without standing in front of it, and collect without anything being
# said out loud. So discretion is not a setting bolted on the side: it is the
# default rendering, and the photographs are opt-in.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:60].replace('\n', ' '))

# ---------------------------------------------------------------- 1. shelf
rep('''  ["snack","Snacks & Drinks","Late-night shelf"]''',
    '''  ["snack","Snacks & Drinks","Late-night shelf"],
  ["love","Love","Discreet pickup"]''')

LOVE = '''love:[
["Rechargeable Personal Massager","Paradise",39.99,0,"massager","#B487FF","#6E3FBF","","Rechargeable, quiet, body-safe silicone. USB-C.","hot"],
["Compact Bullet Massager","Paradise",19.99,0,"massager","#FF7BC8","#8A2E63","","Pocket size, ten settings, water resistant.",""],
["Wand Massager","Paradise",49.99,0,"massager","#B487FF","#4E2A93","","Full size, cordless, flexible head.",""],
["Couples Ring","Paradise",14.99,0,"couples","#FF2FA8","#6E0C45","","Stretch silicone, rechargeable.",""],
["Silicone Toy, Beginner","Paradise",29.99,0,"toy","#CFB2FF","#4E2A93","","Body-safe silicone, smooth finish.",""],
["Silicone Toy, Premium","Paradise",59.99,0,"toy","#B487FF","#331B5E","","Body-safe silicone, rechargeable, travel lock.",""],
["Lace Lingerie Set","Paradise",34.99,0,"lingerie","#FF7BC8","#7A1246","S|M|L|XL","Two piece, adjustable straps.","new"],
["Lingerie Bodysuit","Paradise",29.99,0,"lingerie","#FF2FA8","#5C0E38","S|M|L|XL","One piece, stretch lace.",""],
["Water-Based Lubricant","Paradise",12.99,0,"care","#96E89E","#1B6B24","","Water based, toy safe, unscented.",""],
["Toy Cleaner Spray","Paradise",9.99,0,"care","#5FD36A","#12481B","","Alcohol free, rinse free.",""],
["Condoms, 12 ct","Paradise",11.99,0,"care","#FFC46B","#8A5303","","Latex, lubricated, twelve count.",""],
["Massage Oil","Paradise",14.99,0,"care","#FFA51F","#6B3A02","","Warming, light scent, non staining.",""]
],
'''
rep('const RAW={\nshroom:[', 'const RAW={\n' + LOVE + 'shroom:[')

# ---------------------------------------------------------------- 2. the rule
rep("""const HOUSE_BRANDS = ['House','House Select','Smokers Paradise','Assorted'];""",
"""const HOUSE_BRANDS = ['House','House Select','Smokers Paradise','Assorted'];

/* ---- the discreet shelf ----
   One category is rendered without photographs by default, and that is the
   whole product. Somebody buying from this shelf is buying it here precisely
   so they do not have to stand in front of it, and a wall of packshots on
   their phone in a parked car is the same exposure by another route.

   So: plates, not pictures. The photographs exist behind a switch for anyone
   who wants them, the switch is off until it is turned on, and it is never
   remembered across a fresh install. Nothing about this is a placeholder. */
const DISCREET_CAT = 'love';
const isDiscreet = p => !!p && p.cat === DISCREET_CAT;
function discreetPhotosOn(){ try{ return !!(S.ui && S.ui.lovePhotos) }catch(e){ return false } }
function setDiscreetPhotos(on){
  S.ui = S.ui || {}; S.ui.lovePhotos = !!on; save();
  if(typeof renderCat === 'function' && CATSTATE && CATSTATE.c === DISCREET_CAT) renderCat();
}
/* The plate. Its word comes from the shelf the item sits on, not its name, so
   a plate never spells out more than the aisle would. */
const DISCREET_WORD = {massager:'MASSAGER', couples:'COUPLES', toy:'TOY',
                       lingerie:'LINGERIE', care:'CARE'};
function discreetPlate(p){
  const w = DISCREET_WORD[p && p.shape] || 'IN STORE';
  const a = (p && p.c1) || '#B487FF', b = (p && p.c2) || '#4E2A93';
  return `<span class="lvplate" role="img" aria-label="${esc(w.toLowerCase())}"
      style="--lv1:${a};--lv2:${b}">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.6-7-9.4A4.1 4.1 0 0112 8a4.1 4.1 0 017 2.6C19 15.4 12 20 12 20z"/></svg>
      <b>${w}</b></span>`;
}""")

# ---------------------------------------------------------------- 3. artwork
rep("""function art(p, vkey, strict){
  const alt = `${p.brand} ${p.name}${vkey?', '+(variantNameFor(p,vkey)||vkey):''}`;""",
"""function art(p, vkey, strict){
  /* The discreet shelf answers before anything else looks for a file. */
  if(isDiscreet(p) && !discreetPhotosOn()) return discreetPlate(p);
  const alt = `${p.brand} ${p.name}${vkey?', '+(variantNameFor(p,vkey)||vkey):''}`;""")

# the publish gate asks for a photograph. This shelf is published without one
# on purpose, so it answers first.
rep("""function applyPublishGate(list){
  return list.map(p=>{""",
"""function applyPublishGate(list){
  return list.map(p=>{
    /* No photograph is the intended state here, so the gate does not apply. */
    if(isDiscreet(p)) return Object.assign({}, p, {published:true, hiddenVariants:0});""")

# ---------------------------------------------------------------- 4. plate css
rep(""".card .pr.ask b{""",
"""/* the discreet plate: a shelf label, not a product shot */
.lvplate{position:relative;display:grid;place-items:center;gap:6px;width:100%;height:100%;
  border-radius:12px;background:
    radial-gradient(120% 90% at 50% 0%, color-mix(in srgb, var(--lv1) 28%, transparent) 0%, transparent 62%),
    linear-gradient(160deg, var(--lv2) 0%, #16101F 78%);
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.09)}
.lvplate svg{width:26px;height:26px;fill:none;stroke:var(--lv1);stroke-width:1.6;
  stroke-linecap:round;stroke-linejoin:round;opacity:.9}
.lvplate b{font-family:var(--mono);font-size:8.5px;letter-spacing:.26em;
  color:var(--lv1);opacity:.85;text-transform:uppercase}
.ctile .lvplate svg{width:22px;height:22px}
.card .pr.ask b{""")

# ---------------------------------------------------------------- 5. tiles
rep("""  {k:'shroom',n:'Mushroom Chocolate',       img:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter')||\"""",
    """  {k:'love',  n:'Love',                     img:()=>'', plate:()=>discreetPlate({shape:'couples',c1:'#FF7BC8',c2:'#5C0E38'})},
  {k:'shroom',n:'Mushroom Chocolate',       img:()=>heroShot('TRE House','Mushroom Chocolate, Peanut Butter')||\"""")

rep("""      const src=c.img();
      return `<button class="ctile" data-cat="${c.k}">
        <span class="ph">${src?`<img src="${src}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer"
          onerror="this.style.visibility='hidden'">`:''}</span>""",
"""      const src=c.img();
      return `<button class="ctile" data-cat="${c.k}">
        <span class="ph">${src?`<img src="${src}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer"
          onerror="this.style.visibility='hidden'">`:(c.plate?c.plate():'')}</span>""")

# ---------------------------------------------------------------- 6. the shelf page
rep("""    <h2>${cat[1]}</h2>
    <div class="sh-meta" id="catMeta"></div>
    <span class="hcrule"></span>
  </div>
  <div class="filterbar">""",
"""    <h2>${cat[1]}</h2>
    <div class="sh-meta" id="catMeta"></div>
    <span class="hcrule"></span>
  </div>
  ${cat[0]===DISCREET_CAT?`<div class="lvnote">
    <b>Bought here, bagged before you arrive.</b>
    <p>Order it on your phone and collect it at the counter. The bag is plain,
       the counter screen says <em>Personal care</em> and a code, and nothing on
       it names what is inside. You give the code, we hand it over.</p>
    <p class="es">P&iacute;delo desde tu tel&eacute;fono y rec&oacute;gelo en el mostrador. La bolsa
       va sin nada escrito y la pantalla solo dice <em>Personal care</em> y un
       c&oacute;digo. T&uacute; das el c&oacute;digo y te lo entregamos.</p>
    <button class="lvtog ${discreetPhotosOn()?'on':''}" data-lvphotos="1"
      aria-pressed="${discreetPhotosOn()}">
      ${discreetPhotosOn()?'Hide product photos':'Show product photos'}</button>
    <span class="lvfine">Photos are off until you turn them on, and they go back off
      on a fresh install. 21+ only, same as the rest of the shop.</span>
  </div>`:''}
  <div class="filterbar">""")

rep(""".card .pr.ask b{font-size:13px""",
""".lvnote{margin:12px 16px 4px;padding:14px 15px 13px;border-radius:15px;
  background:linear-gradient(160deg,rgba(180,135,255,.10),rgba(255,47,168,.06));
  box-shadow:inset 0 0 0 1px rgba(180,135,255,.22)}
.lvnote b{display:block;font-size:14px;letter-spacing:-.01em;margin-bottom:6px}
.lvnote p{font-size:12.5px;line-height:1.5;color:var(--body);margin:0 0 7px}
.lvnote p.es{color:var(--muted);font-size:12px}
.lvnote .lvtog{margin-top:4px;padding:9px 14px;border-radius:99px;font-size:12px;font-weight:700;
  background:rgba(180,135,255,.16);color:var(--reward-ink);
  box-shadow:inset 0 0 0 1px rgba(180,135,255,.34)}
.lvnote .lvtog.on{background:var(--reward);color:#1B1030;box-shadow:none}
.lvnote .lvfine{display:block;margin-top:9px;font-size:10.5px;line-height:1.4;color:var(--faint)}
.lovecard{display:grid;grid-template-columns:1fr auto;align-items:center;gap:12px;width:100%;
  padding:16px 16px 15px;border-radius:17px;text-align:left;
  background:linear-gradient(150deg,#2A1040 0%,#3A1030 56%,#1A0B22 100%);
  box-shadow:inset 0 0 0 1px rgba(180,135,255,.26)}
.lovecard .lv-eye{grid-column:1/-1;font-family:var(--mono);font-size:9.5px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--reward-ink);opacity:.9}
.lovecard b{font-family:var(--disp);font-weight:800;font-size:23px;letter-spacing:-.03em;margin-top:5px}
.lovecard small{grid-column:1;font-size:12px;line-height:1.45;color:var(--body);margin-top:4px}
.lovecard .lv-go{grid-row:2/4;grid-column:2;width:34px;height:34px;border-radius:99px;
  display:grid;place-items:center;background:rgba(180,135,255,.18);
  box-shadow:inset 0 0 0 1px rgba(180,135,255,.3)}
.lovecard .lv-go svg{width:14px;height:14px;stroke:var(--reward-ink);fill:none;stroke-width:2.4;
  stroke-linecap:round;stroke-linejoin:round}
.card .pr.ask b{font-size:13px""")

rep("""document.addEventListener('click', e=>{
  const a = e.target.closest('[data-again]'); if(!a) return;""",
"""document.addEventListener('click', e=>{
  const t = e.target.closest('[data-lvphotos]');
  if(t){ setDiscreetPhotos(!discreetPhotosOn()); return }
}, true);

document.addEventListener('click', e=>{
  const a = e.target.closest('[data-again]'); if(!a) return;""")

# ---------------------------------------------------------------- 7. home entry
rep("""  ${glassBandHTML()}""",
"""  ${glassBandHTML()}

  ${PRODUCTS.some(isDiscreet)?`<div class="sec loose reveal" style="--i:7.5">
    <button class="lovecard" data-cat="love">
      <span class="lv-eye">Discreet pickup</span>
      <b>Love</b>
      <small>Order it here and collect it bagged. The counter screen says
        <em>Personal care</em> and a code, nothing else.</small>
      <span class="lv-go">${ARROW}</span>
    </button>
  </div>`:''}""")

# ---------------------------------------------------------------- 8. the counter
rep("""    return {id: l.id,
            n: p?fullName(p):'Item',""",
"""    return {id: l.id,
            /* carried on the order so a line stays discreet even after the
               shelf changes under it */
            d: isDiscreet(p) ? 1 : 0,
            n: p?fullName(p):'Item',""")

rep("""        ${items.map(i=>`<div class="ck-row"><span>${i.q} &times; ${esc(i.n)}${
          i.v?` <em>${esc(i.v)}</em>`:''}</span><b>${
          (typeof i.unit==='number' && i.unit>0) ? money(i.unit*i.q) : '<em>at the counter</em>'}</b></div>`).join('')}""",
"""        ${/* This screen is held up to a person on the other side of a counter,
              so a line off the discreet shelf is a line nobody else reads. The
              customer knows what they ordered; the counter only needs the code
              and a count. Tapping the row shows it, on this phone only. */''}
        ${items.map((i,ix)=>{
          const hid = i.d || (P(i.id) && isDiscreet(P(i.id)));
          const label = `${i.q} &times; ${esc(i.n)}${i.v?` <em>${esc(i.v)}</em>`:''}`;
          return `<div class="ck-row${hid?' priv':''}"${hid?` data-reveal="${ix}"`:''}>
            <span>${hid?`<span class="privlab">Personal care</span>
                    <span class="privreal" hidden>${label}</span>`:label}</span><b>${
            (typeof i.unit==='number' && i.unit>0) ? money(i.unit*i.q) : '<em>at the counter</em>'}</b></div>`;
        }).join('')}
        ${items.some(i=>i.d||(P(i.id)&&isDiscreet(P(i.id))))?`<p class="ckfine">
          Some of this is bagged before you get here and shows as
          <em>Personal care</em> above. Tap a line to check it on your own screen.</p>`:''}""")

rep(""".lvnote{margin:12px 16px 4px;""",
""".ck-row.priv .privlab{color:var(--reward-ink);letter-spacing:.01em}
.ck-row.priv{cursor:pointer}
.ck-row.priv.shown .privlab{display:none}
.lvnote{margin:12px 16px 4px;""")

rep("""document.addEventListener('click', e=>{
  const t = e.target.closest('[data-lvphotos]');""",
"""document.addEventListener('click', e=>{
  const r = e.target.closest('.ck-row.priv[data-reveal]');
  if(r){ r.classList.toggle('shown');
         const real=r.querySelector('.privreal'); if(real) real.hidden=!r.classList.contains('shown');
         return }
}, true);

document.addEventListener('click', e=>{
  const t = e.target.closest('[data-lvphotos]');""")

# ---------------------------------------------------------------- 9. the shelves list
rep("""  highlights:['Glass','E-Juice & Devices','Disposables','Mushroom Chocolate','Torches',""",
    """  highlights:['Glass','E-Juice & Devices','Disposables','Mushroom Chocolate','Love','Torches',""")

rep("""  {t:'TRE House mushroom chocolate now in, $30 a bar', k:'new'},""",
    """  {t:'TRE House mushroom chocolate now in, $30 a bar', k:'new'},
  {t:'Discreet pickup on the Love shelf. Plain bag, just a code', k:''},""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
