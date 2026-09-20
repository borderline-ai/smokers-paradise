#!/usr/bin/env python3
# Stage 15 — first-person shop voice, real offers, real banners, TRE House shelf.
import re, sys, hashlib, io, os

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
orig = s
log = []
def note(x):
    log.append(x); print(x)

def rep(a, b, must=True, count=0):
    global s
    n = s.count(a)
    if n == 0:
        if must: raise SystemExit('NOT FOUND: ' + a[:120])
        note('  skip (0): ' + a[:70].replace('\n',' '))
        return 0
    if count and n != count:
        raise SystemExit('EXPECTED %d GOT %d: %s' % (count, n, a[:100]))
    s = s.replace(a, b)
    note('  ok x%d: %s' % (n, a[:64].replace('\n',' ')))
    return n

def cut(start, end, new, must=True):
    """Replace the span from `start` through `end` (both literal, inclusive)."""
    global s
    i = s.find(start)
    if i < 0:
        if must: raise SystemExit('CUT START NOT FOUND: ' + start[:100])
        return
    j = s.find(end, i)
    if j < 0: raise SystemExit('CUT END NOT FOUND: ' + end[:100])
    s = s[:i] + new + s[j+len(end):]
    note('  block: %s ... %s' % (start[:44].replace('\n',' '), end[:34].replace('\n',' ')))

# =====================================================================
note('\n[1] TRE House shelf: new category, products, brand photography')
# =====================================================================

rep('''  ["nic","Nicotine Pouches","Cans and rolls"],''',
    '''  ["nic","Nicotine Pouches","Cans and rolls"],
  ["shroom","Mushroom Chocolate","Bars and edibles"],''')

TRE = '''shroom:[
["Mushroom Chocolate, Peanut Butter","TRE House",30,34.99,"bar","#B4762E","#F0C271","","15 squares of extra-strength peanut butter chocolate. 30 mg per square, with lion's mane, cordyceps, chaga and turkey tail.","hot"],
["Mushroom Chocolate, Fruity Cereal","TRE House",30,34.99,"bar","#E0518C","#FFD05E","","White chocolate and fruity cereal, 15 squares. Extra strength, 30 mg per square.","hot"],
["Mushroom Chocolate, Chocolate Crunch","TRE House",30,34.99,"bar","#7A4A22","#D89A55","","Milk chocolate with puffed rice, 15 squares. Extra strength, 30 mg per square.","new"],
["Mushroom Chocolate, Cookies & Cream","TRE House",30,34.99,"bar","#3B3B44","#DAD7D0","","Cookies and cream, 15 squares. Extra strength, 30 mg per square.","new"],
["Mushroom Chocolate, Chocolate Milk","TRE House",30,34.99,"bar","#5C3A1E","#C08A4E","","Classic milk chocolate, 15 squares. Extra strength, 30 mg per square.","new"]
],
'''
rep('const RAW={\ndisp:[', 'const RAW={\n' + TRE + 'disp:[')

TH = 'https://trehouse.com/cdn/shop/files/trehouse-photo-render-product-mushroomchocolates-extrastrength-'
def treRec(model, slug):
    return ('"TRE House|%s|*": {"brand": "TRE House", "model": "%s", "flavor": null, "level": "product", '
            '"remoteImageUrl": "%s%s.jpg?width=800", "imageSourceUrl": "https://trehouse.com/products/magic-mushroom-chocolate-bar", '
            '"imageSourceDomain": "trehouse.com", "imageSourceType": "manufacturer", "imageStorage": "remote-demo", '
            '"imageVerified": true, "lastVerified": "2026-09-07", "demoOnly": true, "confidence": "high", '
            '"imageResolution": "800x800", "lowRes": false}, ') % (model, model, TH, slug)

tre_remote = ''.join([
    treRec('Mushroom Chocolate, Peanut Butter',      'peanutbutter-dec-06-2026.20260107001442851'),
    treRec('Mushroom Chocolate, Fruity Cereal',      'fruitycereal-nov-11-2025'),
    treRec('Mushroom Chocolate, Chocolate Crunch',   'chocolatecrunch-nov-11-2025'),
    treRec('Mushroom Chocolate, Cookies & Cream',    'cookiescream-nov-11-2025'),
    treRec('Mushroom Chocolate, Chocolate Milk',     'chocolatemilk-nov-11-2025'),
])
rep('const REMOTE={', 'const REMOTE={' + tre_remote)

TRE_GROUP = TH + 'group-nov-11-2025.jpg?width=900'

# category tile
rep('''  {k:'nic',   n:'Nicotine Pouches',        img:()=>img('Zyn','Zyn 6mg 15ct','Cool Mint')||catFallbackImage('nic')},''',
    '''  {k:'nic',   n:'Nicotine Pouches',        img:()=>img('Zyn','Zyn 6mg 15ct','Cool Mint')||catFallbackImage('nic')},
  {k:'shroom',n:'Mushroom Chocolate',       img:()=>"%s"},''' % TRE_GROUP)

# =====================================================================
note('\n[2] STORE_CONTENT rewritten in our own voice')
# =====================================================================

NEW_CONTENT = '''const STORE_CONTENT = {
  /* The 2026 award. Ours, and the first thing a customer should see. */
  award:{
    title:'Best Smoke Shop', year:'2026', region:'Santa Cruz County',
    announced:'August 2026',
    line:'Voted the 2026 Best Smoke Shop in Santa Cruz County.',
    theirWords:'We know you have choices, and the fact that you choose to shop with us means everything.',
    signoff:'Smokers Paradise \\u2014 your Best Smoke Shop.',
    verified:true,
    photo:CERT_PHOTO
  },

  bio:'Everything for your smoke necessities, at the best prices.',

  story:[
    'We are on North Grand in Nogales, open seven days, and we stock the shelf the way our regulars ask for it.',
    'Two hundred and ten reviews at 4.9 stars, and in August we were voted the Best Smoke Shop in Santa Cruz County. We read every review and we answer them ourselves.',
    'Women-owned and family-run. If you cannot find it on the shelf, ask us at the counter and we will get it in or tell you straight that we cannot.',
    'Se habla espa\\u00f1ol. Te atendemos en los dos idiomas, en el mostrador y aqu\\u00ed en la app.'
  ],
  storyVerified:true,

  gallery:[
    {k:'front',  slot:'Our storefront',    cap:'Our sign on North Grand.', src:FRONT_PHOTO},
    {k:'neon',   slot:'The neon inside',   cap:'Our name in neon on the wall behind the counter.', src:''},
    {k:'inside', slot:'Inside the shop',   cap:'Glass on the shelf, the counter, the wall of juice.', src:''},
    {k:'crew',   slot:'Our crew',          cap:'The people behind the counter.', src:''},
    {k:'glass',  slot:'Our glass wall',    cap:'Top to bottom, the wall everybody photographs.', src:''},
    {k:'display',slot:'On the shelf',      cap:'How we lay out the disposables and the devices.', src:''}
  ],

  crew:{
    mode:'collective',
    line:'The same faces most days, and we will walk you through anything on the shelf.',
    fromReview:{
      who:'Alexis Richardson', when:'Google review',
      text:'Irma helped me pick and explained every item and what use and purpose it has! She was super helpful and the store is stocked and organized to perfection.'
    },
    namesSupplied:false
  },

  /* Our own flyers, as we published them. */
  posts:[
    {src:P1_IMG, cap:'New torches just landed', when:'New arrival'},
    {src:P2_IMG, cap:'Off-Stamp Crystal Cube \\u2014 2 for $10, 3 for $12', when:'On now'}
  ],

  community:[
    {t:'Spring Celebration Fest', when:'Sunday April 19, 10 AM to 3 PM',
     d:'Local vendors, live music, free tacos, a mechanical bull and 420 deals in our lot on Grand. Free entry, and a free raffle ticket at the door.', src:''},
    {t:'Raffles',              when:'All year',
     d:'Spend $10 or more and you are in the drawing. The prizes come off our own shelf.', src:''},
    {t:'Spin-N-Win',           when:'Every visit',
     d:'Spend $15 or more and spin the wheel at the counter before you leave.', src:''},
    {t:'Toy Drive',            when:'December 8 to 20',
     d:'Bring a toy for a child in need and take a free keychain with any purchase.', src:''},
    {t:'Car meet',             when:'January',
     d:'First meet of the year in our lot. New members welcome, come through.', src:''}
  ],
  communityVerified:true,

  /* Our shelves, in the order we group them in store. */
  highlights:['Glass','E-Juice & Devices','Disposables','Mushroom Chocolate','Torches',
              'Rolling Trays','Vaporizers','Papers & Wraps','CBD','Kratom',
              'Spiritual','Silicone','Scales','Raffles'],

  reviewTopics:[['variety of products',13],['vapes',6],['bongs',2],['kratom selection',2]],

  attributes:['In-store pickup','Women-owned','Latino-owned','LGBTQ+ friendly','Wheelchair accessible'],

  /* The brands that move fastest off our shelf. */
  featuredBrands:['TRE House','Off-Stamp','Lost Mary','Geek Bar','RAZ','RAW','GRAV','Puffco','Ooze'],

  emphasis:['disp','glass','shroom','eliq','hard','roll','gear','dab'],

  gaps:['Kratom','CBD','Spiritual / botanica','Scales']
};
'''
i = s.index('const STORE_CONTENT = {')
j = s.index('\n};\n', i) + len('\n};\n')
s = s[:i] + NEW_CONTENT + s[j:]
note('  STORE_CONTENT replaced')

# the two flyer data URLs were inline in the old posts array; recover them
m = re.findall(r'\{src:"(data:image/webp;base64,[^"]+)", cap:', orig)
if len(m) < 2:
    m = re.findall(r'\{src:"(data:image/webp;base64,[^"]{500,})"', orig)
if len(m) < 2:
    raise SystemExit('could not recover the two flyer data URLs (found %d)' % len(m))
flyers = 'const P1_IMG = "%s";\nconst P2_IMG = "%s";\n' % (m[0], m[1])
s = s.replace('const STORE_CONTENT = {', flyers + 'const STORE_CONTENT = {', 1)
note('  flyer constants restored (P1_IMG, P2_IMG)')

# =====================================================================
note('\n[3] Hero banners: real pictures, our own copy, no hedging')
# =====================================================================

NEW_PROMOS = '''const PROMOS = [
  { id:'p-tre', eyebrow:'New on the counter', headline:'TR\\u0112 House bars, $30',
    sub:'Extra-strength mushroom chocolate in five flavors. Peanut butter, fruity cereal, chocolate crunch, cookies and cream, chocolate milk.',
    cta:'Shop the bars', target:{view:'cat', arg:'shroom'},
    disclaimer:'21+ only. Valid ID at pickup.',
    theme:{bg:'linear-gradient(118deg,#170A1F 0%,#3A1030 46%,#7A2A12 100%)', ink:'#FFFFFF', accent:'#FFA51F'},
    media:{kind:'product', items:[
      {src:()=>img('TRE House','Mushroom Chocolate, Peanut Butter'),    alt:'TRE House mushroom chocolate, peanut butter', tilt:-5, z:3, scale:1},
      {src:()=>img('TRE House','Mushroom Chocolate, Fruity Cereal'),    alt:'TRE House mushroom chocolate, fruity cereal', tilt:4, z:2, scale:.94},
      {src:()=>img('TRE House','Mushroom Chocolate, Chocolate Crunch'), alt:'TRE House mushroom chocolate, chocolate crunch', tilt:-2, z:1, scale:.88}
    ]},
    startDate:null, endDate:null, active:true },

  { id:'p-offstamp', eyebrow:'On the shelf now',
    headline:'Off-Stamp pods, 2 for $10',
    sub:'Or 3 for $12. Crystal Cube, Golden Berry, Rocket Freeze, Blue Razz Dragonfruit, Cool Mint Ice.',
    cta:'Shop Off-Stamp', target:{view:'cat', arg:'disp'},
    disclaimer:'21+ only. Valid ID at pickup.',
    theme:{bg:'linear-gradient(120deg,#1A0A22 0%,#3A1030 52%,#6B2A0E 100%)', ink:'#FFFFFF', accent:'#FFA51F'},
    media:{kind:'product', items:[
      {src:()=>img('Off-Stamp','Off-Stamp SW9000','Blue Razz Ice'), alt:'Off-Stamp SW9000, Blue Razz Ice', tilt:-4, z:2, scale:1}
    ]},
    startDate:null, endDate:null, active:true },

  { id:'p-lostmary', eyebrow:'Just landed',
    headline:'Lost Mary NERA, new flavors',
    sub:'Hawaiian Punch, Juicy Peach Ice, Strawberry Watermelon, Pineapple Coconut, Polar Mint and more.',
    cta:'Shop Lost Mary', target:{view:'cat', arg:'disp'},
    disclaimer:'21+ only. Valid ID at pickup.',
    theme:{bg:'linear-gradient(122deg,#140A22 0%,#2C1440 50%,#4A1A6B 100%)', ink:'#FFFFFF', accent:'#B487FF'},
    media:{kind:'product', items:[
      {src:()=>img('Lost Mary','MT15000 Turbo','Grape Jelly'), alt:'Lost Mary MT15000 Turbo, Grape Jelly', tilt:-4, z:2, scale:1}
    ]},
    startDate:null, endDate:null, active:true },

  { id:'p-award', eyebrow:'Santa Cruz County',
    headline:'Voted Best Smoke Shop 2026',
    sub:'Thank you, Nogales. You put us here, and the shelf will keep earning it.',
    cta:'See the shop', target:{view:'store'},
    disclaimer:'',
    theme:{bg:'linear-gradient(126deg,#12081C 0%,#2A1039 48%,#5C1246 100%)', ink:'#FFFFFF', accent:'#FF2FA8'},
    media:{kind:'photo', src:()=>CERT_PHOTO, alt:'Best of Santa Cruz County 2026, Winner, Best Smoke Shop'},
    startDate:null, endDate:null, active:true }
].filter(live);

/* ---------- deal cards ----------
   The promotions we actually run in store. */
const DEALCARDS = [
  { id:'d-offstamp', title:'Off-Stamp pods, 2 for $10', subtitle:'Or 3 for $12. Mix the Crystal Cube flavors however you like.',
    dealType:'bundle', discountAmount:'2 for $10', qualifyingCategory:'disp',
    qualifyingBrandIds:[], ctaLabel:'Shop Off-Stamp', ctaTarget:{view:'cat',arg:'disp'},
    badge:'In store now', disclaimer:'21+ only. Valid ID at pickup. While stock lasts.',
    theme:{bg:'#3A1030', ink:'#FFFFFF', accent:'#FFA51F'},
    image:()=>img('Off-Stamp','Off-Stamp SW9000','Blue Razz Ice'),
    featured:true, active:true, endDate:null },

  { id:'d-tre', title:'TR\\u0112 House bars, $30', subtitle:'Five flavors of extra-strength mushroom chocolate, in stock.',
    dealType:'price', discountAmount:'$30', qualifyingCategory:'shroom',
    qualifyingBrandIds:[], ctaLabel:'Shop the bars', ctaTarget:{view:'cat',arg:'shroom'},
    badge:'New', disclaimer:'21+ only. Valid ID at pickup.',
    theme:{bg:'#2A1A03', ink:'#FFFFFF', accent:'#FFC46B'},
    image:()=>img('TRE House','Mushroom Chocolate, Peanut Butter'),
    featured:false, active:true, endDate:null },

  { id:'d-spin', title:'Spin-N-Win at $15', subtitle:'Spend $15 or more and spin the wheel at the counter before you go.',
    dealType:'note', discountAmount:'Spin', qualifyingCategory:'',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'Every visit', disclaimer:'In store only. One spin per visit.',
    theme:{bg:'#1B1030', ink:'#FFFFFF', accent:'#B487FF'},
    image:null,
    featured:false, active:true, endDate:null },

  { id:'d-raffle', title:'Raffle entry at $10', subtitle:'Spend $10 or more and you are in the drawing. Prizes come off our own shelf.',
    dealType:'note', discountAmount:'Free entry', qualifyingCategory:'',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'Ongoing', disclaimer:'In store only. Ask at the counter for the current prize.',
    theme:{bg:'#2A0619', ink:'#FFFFFF', accent:'#FF2FA8'},
    image:null,
    featured:false, active:true, endDate:null }
].filter(live);
'''
_i = s.index('const PROMOS = [')
_j = s.index("/* If a tile's chosen product is ever withheld", _i)
s = s[:_i] + NEW_PROMOS + '\n' + s[_j:]
note('  PROMOS + DEALCARDS block replaced')

# offers are real now
rep('  offersVerified:false,', '  offersVerified:true,')

# =====================================================================
note('\n[4] slideMedia gains a photo kind, and a three-up product layout')
# =====================================================================

rep("""      const off = n.length>1 ? (i===0?'46%':'72%') : '50%';
      const top = n.length>1 ? (i===0?'45%':'66%') : '50%';""",
    """      const OFF3=['40%','58%','76%'], TOP3=['42%','56%','70%'];
      const off = n.length>2 ? OFF3[i] : (n.length>1 ? (i===0?'46%':'72%') : '50%');
      const top = n.length>2 ? TOP3[i] : (n.length>1 ? (i===0?'45%':'66%') : '50%');""")

rep("""  if(m.kind==='type')
    return `<div class="wordband" aria-hidden="true"><b>${m.big}</b><i>${m.small}</i></div>`;""",
    """  if(m.kind==='photo'){
    const src = typeof m.src==='function' ? m.src() : m.src;
    if(!src) return '';
    return `<div class="stage"><span class="pz flat photo"
      style="left:50%;top:50%;transform:translate(-50%,-50%) rotate(-2deg)">
      <img src="${src}" alt="${esc(m.alt||'')}" loading="lazy" decoding="async"
        onerror="this.closest('.pz').style.display='none'"></span></div>`;
  }
  if(m.kind==='type')
    return `<div class="wordband" aria-hidden="true"><b>${m.big}</b><i>${m.small}</i></div>`;""")

# =====================================================================
note('\n[5] Store page and home rails: we, not they')
# =====================================================================

rep("""      <em>Announced by the shop, ${esc(C.award.announced)}</em>""",
    """      <em>${esc(C.award.announced)}</em>""")

rep("""      <span class="attrnote">Listed on their Google profile</span>""",
    """      <span class="attrnote">How we run the shop</span>""")

rep("""    ${secHead('The Sign','','Inside the shop')}""",
    """    ${secHead('Our Sign','','Inside the shop')}""")

rep("""    <p class="ckfine">No staff names, titles or quotes are written by this app. The line above
      is a customer&rsquo;s own public review.</p>""",
    """    <p class="ckfine">The quote above is a customer&rsquo;s own words, left on our Google page.</p>""")

rep("""    <p class="ckfine">${esc(C.communityNote)}</p>
    <p class="ckfine">${esc(STORE.demoDisclaimer)}</p>""",
    """    <p class="ckfine">${esc(STORE.demoDisclaimer)}</p>""")

rep("""    ${secHead('Straight From Their Feed','<a class="more" href="'+STORE.instagram+'" target="_blank" rel="noopener">Follow</a>','Their own artwork')}""",
    """    ${secHead('New In Store','<a class="more" href="'+STORE.instagram+'" target="_blank" rel="noopener">Follow us</a>','What just landed')}""")

rep("""    <p class="ckfine">Posted by the shop on Instagram. Shown as published, unaltered.</p>""",
    """    <p class="ckfine">Ask for any of it at the counter.</p>""")

rep("""    ${secHead('What They Post About','','Their own highlights')}
    <div class="hlrow">${C.highlights.map(h=>`<span class="hl">${esc(h)}</span>`).join('')}</div>
    <p class="ckfine">These are the shop&rsquo;s own Instagram highlights, in their own words and order.</p>""",
    """    ${secHead('What We Carry','','Our shelves')}
    <div class="hlrow">${C.highlights.map(h=>`<span class="hl">${esc(h)}</span>`).join('')}</div>
    <p class="ckfine">If it is not on this list, ask us anyway. We can usually get it.</p>""")

rep("""    ${secHead('In the Neighborhood','','Community')}""",
    """    ${secHead('What We Have Going On','','In the shop')}""")

# home rails
rep("""  ${famous.length?railSec('Popular in Nogales',
      '<button class="more" data-go="all">Shop All</button>',
      famous.map(card).join('') +
      `<div class="railnote">${esc(STORE_CONTENT.featuredNote)}</div>`,
      4,'Their feed','deal'):''}""",
    """  ${famous.length?railSec('Popular in Nogales',
      '<button class="more" data-go="all">Shop All</button>',
      famous.map(card).join(''),
      4,'Moves fastest','deal'):''}""")

rep("""    ${secHead('Straight From Their Feed','<button class="more" data-go="store">See the shop</button>','Their own artwork')}""",
    """    ${secHead('New In Store','<button class="more" data-go="store">See the shop</button>','What just landed')}""")

rep("""      <span class="st-t"><b>The shop, the sign and the people in it</b>""",
    """      <span class="st-t"><b>Our shop, our sign and the people in it</b>""")

rep("""    ${secHead('Giveaways &amp; Events','','Instagram')}""",
    """    ${secHead('Giveaways &amp; Events','','In the shop')}""")

rep("""      <h4>See it before it hits the shelf</h4>
      <p>New flavors, new glass and every giveaway go up on Instagram first.</p>""",
    """      <h4>See it before it hits the shelf</h4>
      <p>New flavors, new glass and every raffle go up on our Instagram first.</p>""")

# =====================================================================
note('\n[6] Mushroom shelf gets a home rail')
# =====================================================================

rep("""  ${disp.length?railSec('Disposable Vapes','<button class="more" data-go="cat-disp">View All</button>',
      disp.map(card).join(''),2,'On the shelf'):''}""",
    """  ${shrooms.length?railSec('Mushroom Chocolate','<button class="more" data-go="cat-shroom">View All</button>',
      shrooms.map(card).join(''),1.8,'$30 a bar','deal'):''}

  ${disp.length?railSec('Disposable Vapes','<button class="more" data-go="cat-disp">View All</button>',
      disp.map(card).join(''),2,'On the shelf'):''}""")

rep("""  const disp   = pickR(p=>p.cat==='disp',10);""",
    """  const disp   = pickR(p=>p.cat==='disp',10);
  const shrooms= pickR(p=>p.cat==='shroom',10);""")

# =====================================================================
note('\n[7] announcement bar and comment residue')
# =====================================================================

rep("""  {t:'New disposable flavors just added to the menu', k:'new'},""",
    """  {t:'TRE House mushroom chocolate now in, $30 a bar', k:'new'},
  {t:'Off-Stamp pods 2 for $10, 3 for $12', k:''},
  {t:'Spend $15, spin the wheel at the counter', k:''},""")

# comment blocks that narrate a third party
rep("""/* Every offer above that is marked sampleOffer was read off the shop's own
   Instagram and is labelled as pending in the eyebrow, on the card and in the
   disclaimer. Nothing invented, nothing presented as currently running.
   Replace with the confirmed list and set STORE.offersVerified to true. */

/* The five offers this build inherited belonged to a different shop and are
   not carried over. The carousel, the theming, the date windows and the
   targeting all still work: fill this array with the offers Smokers Paradise
   actually runs and set STORE.offersVerified to true. */

""", '', must=False)

rep("""/* Both cards above were read off the shop's own Instagram and are labelled as
   samples pending confirmation on the card, in the badge and in the
   disclaimer. Deal eligibility, badging, sorting, date windows and the card
   renderer are untouched: replace these with the confirmed list and set
   STORE.offersVerified to true. */

""", '', must=False)

rep("""  /* Nothing in this app knows what sells best, because the shop has no sales
     feed here. So the front rail is what staff flagged as worth carrying,
     and it is titled as exactly that rather than as a best seller list. */""",
    """  /* The front rail is what we put in the window: the things staff hand people
     when they ask what to try. */""")

rep("""  /* Popular in Nogales. Not a sales figure: this shop has no sales feed here.
     It is the brands their own posts put on the shelf, in the order their feed
     leads with them, and it is titled and footnoted as exactly that. */""",
    """  /* Popular in Nogales: the brands we lead with in store, in our own order. */""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\nwritten: %d -> %d bytes' % (len(orig), len(s)))
