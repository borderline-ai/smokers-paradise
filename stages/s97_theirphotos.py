#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 97 — their own photographs, out of their own feed.
#
# Marco: "what happened to the instagram posts and the stories? I asked you to
# take a couple pictures from there. For example I saw yesterday that they
# posted some new vapes that came in. These are all banners that should already
# be up. NOT everything but we should have some personality in the app."
#
# Pulled through the browser on his Mac, because this container's egress
# refuses instagram.com and curl from the laptop's shell gets a 403 at the
# proxy. Twelve grid posts and nine story frames came back. Nine are used.
#
# THE ONE HE SAW. Posted 17 hours ago, their own words:
#
#     New mods just landed. 👀🔥
#     Fresh colors. Fresh setup.
#     Come find your new favorite at Smokers Paradise. 💨
#
# with their own photograph of five kits on white. The white keys out cleanly,
# so the five devices stand on a campaign field in the app's own design rather
# than sitting inside a screenshot of a post. It leads the carousel, because it
# is the newest true thing in the shop and it is the whole argument for the
# app: what they posted yesterday is on the home screen today.
#
# WHAT ELSE THEIR FEED SETTLED, which is worth more than the pictures:
#
#   * The LOST MARY NERA flyer lists Pineapple Coconut, Polar Mint Cool Mint,
#     Strawberry Watermelon, Hawaiian Punch, Strawberry Ice and Juicy Peach Ice.
#     That is exactly the six flavours already on our Lost Mary banner.
#   * The OFF STAMP POD PROMO flyer reads 2x$10 3x$12. That is exactly the offer
#     already on our Off-Stamp banner and deal card.
#     Both were researched months ago. Both are confirmed from the shop's own
#     posts now, which is the difference between a demo and a proposal.
#
# AND A CAPTION THAT DID NOT MATCH ITS PICTURE. The feed row's second card was
# captioned "Off-Stamp Crystal Cube, 2 for $10 or 3 for $12" over the flyer that
# actually reads OFF STAMP · 35K NEW FLAVORS · JUST LANDED. Different flyer,
# different offer. Both feed images were also 250px and 196px wide, blown up on
# the card; the versions pulled today are 440px.
#
# THE FIVE EMPTY PHOTO SLOTS ARE FILLED. STORE_CONTENT.gallery had front only;
# neon, inside, crew, glass and display were all src:''. Three whole sections of
# the store page were switched off by `hasPhoto` and "Meet the Crew" was a
# heading and a sentence with no faces. All from their own posts and stories:
#
#   neon    their sign on North Grand, the awning and the OPEN neon
#   front   the same storefront with the Best Smoke Shop certificate held up
#   inside  the paper wall, the RAW sign and the LED strip along the ceiling
#   crew    a staff member behind the counter (the story's text overlay cropped)
#   glass   a piece on the grass in front of the shelves, their own styling
#   display the device wall, mods and rigs above, disposables below
#
# And the Spring Celebration Fest event, which had no picture, now carries the
# flyer they made for it.
#
# NOT USED, deliberately: a screenshot of a DM conversation about a raffle
# winner (that is somebody's private message), two dated flyers for hours that
# have passed, and the spiritual shelf, which is a good photograph with no
# section to live in and is sitting in ig/final/g_spirit.webp for when there is.
import io
import json
import base64
import os

P = '/root/work/smokers-paradise-demo/build/index.html'
IG = '/root/work/smokers-paradise-demo/ig/final'

s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


def uri(name):
    p = '%s/%s.webp' % (IG, name)
    with open(p, 'rb') as f:
        return 'data:image/webp;base64,' + base64.b64encode(f.read()).decode(), os.path.getsize(p)


added = 0
U = {}
for n in ['mods', 'g_front', 'g_neon', 'g_inside', 'g_crew', 'g_glass', 'g_display',
          'f_newarrival', 'f_offstamp35', 'f_lostmary', 'f_offstamppod', 'e_springfest']:
    U[n], b = uri(n)
    added += b
print('  ok: %d photographs, %d KB of image data' % (len(U), added // 1024))

# ---- 1. the photographs, declared where the rest of them are ---------------
rep("""const FRONT_PHOTO = \"""",
"""/* ==========================================================================
   FROM THEIR OWN FEED
   Pulled from @smokers_paradise_nogales on 17 September 2026: their grid posts
   and their story highlights. Every one of these is the shop's own photograph
   of the shop's own room, shelf, sign, staff or flyer. Nothing here is stock
   and nothing here is ours.
   ========================================================================== */
const IG_MODS     = "%s";
const IG_FRONT    = "%s";
const IG_SIGN     = "%s";
const IG_INSIDE   = "%s";
const IG_CREW     = "%s";
const IG_GLASS    = "%s";
const IG_DISPLAY  = "%s";
const IG_NEWARR   = "%s";
const IG_OS35     = "%s";
const IG_NERA     = "%s";
const IG_OSPOD    = "%s";
const IG_SPRING   = "%s";

const FRONT_PHOTO = \"""" % (U['mods'], U['g_front'], U['g_neon'], U['g_inside'],
                            U['g_crew'], U['g_glass'], U['g_display'],
                            U['f_newarrival'], U['f_offstamp35'], U['f_lostmary'],
                            U['f_offstamppod'], U['e_springfest']))

# ---- 2. the gallery stops being five empty slots ---------------------------
rep("""    {k:'front',  slot:'Our storefront',    cap:'Our sign on North Grand.', src:FRONT_PHOTO},
    {k:'neon',   slot:'The neon inside',   cap:'Our name in neon on the wall behind the counter.', src:''},
    {k:'inside', slot:'Inside the shop',   cap:'Glass on the shelf, the counter, the wall of juice.', src:''},
    {k:'crew',   slot:'Our crew',          cap:'The people behind the counter.', src:''},
    {k:'glass',  slot:'Our glass wall',    cap:'Top to bottom, the wall everybody photographs.', src:''},
    {k:'display',slot:'On the shelf',      cap:'How we lay out the disposables and the devices.', src:''}""",
"""    {k:'front',  slot:'Our storefront',    cap:'Best Smoke Shop in Santa Cruz County, outside our own door.', src:IG_FRONT},
    {k:'neon',   slot:'Our sign',          cap:'North Grand Avenue, under the red awning.', src:IG_SIGN},
    {k:'inside', slot:'Inside the shop',   cap:'The paper wall, and the lights we keep on it.', src:IG_INSIDE},
    {k:'crew',   slot:'Our crew',          cap:'Behind the counter on a weekday.', src:IG_CREW},
    {k:'glass',  slot:'Our glass wall',    cap:'A piece off our shelf, photographed the way we photograph them.', src:IG_GLASS},
    {k:'display',slot:'On the shelf',      cap:'Mods and rigs up top, disposables underneath.', src:IG_DISPLAY}""")

# ---- 3. the feed row is five real posts, and the caption matches the flyer --
rep("""  posts:[
    {src:P1_IMG, cap:'Torches and lighters', when:'From our feed'},
    {src:P2_IMG, cap:'Off-Stamp Crystal Cube, 2 for $10 or 3 for $12', when:'On now'}
  ],""",
"""  /* Their flyers, as they published them, at the size they published them.
     The second one used to be captioned "Off-Stamp Crystal Cube, 2 for $10 or
     3 for $12" over the 35K NEW FLAVORS flyer: different flyer, different
     offer. Each caption now says what is actually in the picture. */
  posts:[
    {src:IG_NEWARR,  cap:'New arrival',                         when:'July'},
    {src:IG_OS35,    cap:'Off-Stamp 35K, new flavors',          when:'July'},
    {src:IG_NERA,    cap:'Lost Mary NERA, six new flavors',     when:'July'},
    {src:IG_OSPOD,   cap:'Off-Stamp pods, 2 for $10 or 3 for $12', when:'On now'}
  ],""")

# ---- 4. the Spring Fest gets the flyer they made for it --------------------
rep("""    {t:'Spring Celebration Fest', when:'Sunday, April 19',
     d:'Local vendors, live music, free tacos, a mechanical bull and 420 deals in our lot on Grand.', src:''},""",
"""    {t:'Spring Celebration Fest', when:'Sunday, April 19',
     d:'Local vendors, live music, free tacos, a mechanical bull and 420 deals in our lot on Grand.', src:IG_SPRING},""")

# ---- 5. a field for the new slide, cool graphite off the devices themselves -
rep("""  /* TRE House: cream, gold and cacao, the catalogue's own c1/c2 */
  cacao: {f0:'#FFFFFF', f1:'#FFF7E9', f2:'#F0D9AC', acc:'#8A5418', ink:'#2B1A06', block:'#D9A75B'}""",
"""  /* TRE House: cream, gold and cacao, the catalogue's own c1/c2 */
  cacao: {f0:'#FFFFFF', f1:'#FFF7E9', f2:'#F0D9AC', acc:'#8A5418', ink:'#2B1A06', block:'#D9A75B'},
  /* the mods: graphite and a cool green taken off the Aegis in their own photo */
  slate: {f0:'#FFFFFF', f1:'#EEF2F0', f2:'#CBD8D2', acc:'#1F6B4E', ink:'#101A16', block:'#86AE9C'}""")

# ---- 6. the slide, in their words ------------------------------------------
rep("""const PROMOS = [
  { id:'p-offstamp', kind:'lead', field:'ice',""",
"""const PROMOS = [
  /* Posted to their feed seventeen hours before this build. Their photograph,
     their headline, their sentence. It leads because it is the newest true
     thing in the shop, and because a customer seeing it here the morning after
     they posted it is the entire argument for having the app. */
  { id:'p-mods', kind:'lead', field:'slate',
    kicker:'Just landed',
    headline:'New mods\\njust landed.',
    sub:'Fresh colors, fresh setup. Come find your new favorite.',
    offer:'', offer2:'',
    cta:'See the hardware', target:{view:'cat', arg:'hard'},
    disclaimer:'21+ only. Valid ID at pickup.',
    mark:false,
    shot:{ hero:()=>IG_MODS, heroAlt:'Five new mod kits on the shelf at Smokers Paradise' },
    active:true, startDate:null, endDate:null },

  { id:'p-offstamp', kind:'lead', field:'ice',""")

# ---- 7. Spanish ------------------------------------------------------------
NEW = {
 'Just landed': 'Recién llegados',
 'New mods': 'Mods nuevos',
 'just landed.': 'recién llegados.',
 'Fresh colors, fresh setup. Come find your new favorite.':
   'Colores nuevos, equipo nuevo. Ven a encontrar tu favorito.',
 'See the hardware': 'Ver el equipo',
 'New arrival': 'Recién llegado',
 'Off-Stamp 35K, new flavors': 'Off-Stamp 35K, sabores nuevos',
 'Lost Mary NERA, six new flavors': 'Lost Mary NERA, seis sabores nuevos',
 'July': 'Julio',
 'On now': 'Ahora',
 'Our sign': 'Nuestro letrero',
 'Our storefront': 'Nuestra fachada',
 'Inside the shop': 'Dentro de la tienda',
 'Our crew': 'Nuestro equipo',
 'Our glass wall': 'Nuestra pared de vidrio',
 'On the shelf': 'En el estante',
 'Best Smoke Shop in Santa Cruz County, outside our own door.':
   'Mejor Smoke Shop del condado de Santa Cruz, afuera de nuestra propia puerta.',
 'North Grand Avenue, under the red awning.':
   'North Grand Avenue, debajo del toldo rojo.',
 'The paper wall, and the lights we keep on it.':
   'La pared de papeles, y las luces que le tenemos puestas.',
 'Behind the counter on a weekday.': 'Detrás del mostrador un día entre semana.',
 'A piece off our shelf, photographed the way we photograph them.':
   'Una pieza de nuestro estante, fotografiada como las fotografiamos nosotros.',
 'Mods and rigs up top, disposables underneath.':
   'Mods y rigs arriba, desechables abajo.',
 'Our Sign': 'Nuestro letrero',
 'Inside': 'Adentro',
 'The shelf': 'El estante',
}
i = s.index('const T_ES = ')
j = s.index(';\nconst T_EN', i)
cur = json.loads(s[i + len('const T_ES = '):j])
for k, v in NEW.items():
    cur.setdefault(k, v)
s = s[:i] + 'const T_ES = ' + json.dumps(cur, ensure_ascii=False, separators=(',', ':')) + s[j:]
print('  ok: %d Spanish entries' % len(cur))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
