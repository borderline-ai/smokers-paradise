#!/usr/bin/env python3
# Stage 52 — the three things underneath every complaint on the list.
#
# 1. THE "DISTRESSED FONT" IS A SYNTHESISED BOLD.
#    Anton ships one weight, 400. The app asked it for 700 in twenty places,
#    so the browser smeared the glyphs to fake a bold — and at 12-15px on a
#    phone that smear is the eroded, barely-readable look. Anton is replaced
#    with Oswald, which is the same condensed attitude and has real 500/600/700
#    cut by a type designer.
#
# 2. HEADINGS WERE GREY BECAUSE THE REVEAL ANIMATION FAILS CLOSED.
#    `.reveal{opacity:0}` and an IntersectionObserver to bring it back. Miss the
#    observer — a programmatic scroll, a fast flick, a section already on screen
#    at first paint — and the heading sits at opacity 0 or halfway. That is the
#    "dark gray text on a nearly black background". It now starts VISIBLE and
#    the animation is an enhancement, with a timer that gives up after a second
#    and shows everything regardless.
#
# 3. TRANSPARENT CUTOUTS.
#    The white rectangle behind every product was the photograph's own studio
#    sweep. The promotional surfaces now use real cut-outs: the white ground
#    keyed away, or the manufacturer's own alpha where they shipped a PNG.
#    Nothing recoloured, stretched or redrawn — only the background removed.
import io, os, json, base64

P = '/root/work/smokers-paradise-demo/build/index.html'
CUT = '/root/work/assets/cutouts'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:52].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:56].replace('\n', ' '))


# ---------------------------------------------------------------- 1. type
rep("""  --disp:'Schibsted Grotesk','Helvetica Neue',Arial,sans-serif;
  --body-f:'Figtree','Helvetica Neue',Arial,sans-serif;
  --mono:'JetBrains Mono','SF Mono',Menlo,monospace;
  --block:'Anton','Arial Narrow',sans-serif;""",
"""  --disp:'Schibsted Grotesk','Helvetica Neue',Arial,sans-serif;
  --body-f:'Figtree','Helvetica Neue',Arial,sans-serif;
  --mono:'JetBrains Mono','SF Mono',Menlo,monospace;
  /* Oswald, not Anton. Anton has exactly one weight; every `font-weight:700`
     against it was a browser-synthesised bold, and a faked bold at 12px on a
     phone is the smeared, half-legible "distressed" look. Oswald is the same
     condensed attitude with real 500/600/700 drawn by a type designer. */
  --block:'Oswald','Arial Narrow',Arial,sans-serif;""")

rep("""  --block:'Anton','Arial Narrow',sans-serif;
  --disp:'Schibsted Grotesk','Helvetica Neue',Arial,sans-serif;""",
"""  --block:'Oswald','Arial Narrow',Arial,sans-serif;
  --disp:'Schibsted Grotesk','Helvetica Neue',Arial,sans-serif;""")

rep("""  --script:'Anton','Arial Narrow',sans-serif;""",
    """  --script:'Oswald','Arial Narrow',Arial,sans-serif;""")

rep("""family=Anton&family=Figtree:wght@400;500;600;700""",
    """family=Oswald:wght@400;500;600;700&family=Figtree:wght@400;500;600;700""")

# ---------------------------------------------------------------- 2. reveal
rep(""".reveal{opacity:0;transform:translateY(16px)}
.reveal.in{opacity:1;transform:none;transition:opacity .55s cubic-bezier(.2,.8,.3,1),transform .55s cubic-bezier(.2,.8,.3,1)}
@media (prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none}}""",
"""/* ---- reveal, failing OPEN ----
   This used to start at opacity 0 and depend on an IntersectionObserver to
   bring it back. Miss the observer — a programmatic scroll, a fast flick, a
   section already on screen at first paint — and a heading sits at zero or
   halfway, which is exactly the "dark grey text on a nearly black background"
   this app was showing. Content is visible by default now; the animation only
   happens when JS has explicitly armed it, and gives up after a second. */
.reveal{opacity:1;transform:none}
.reveal.armed{opacity:0;transform:translateY(16px)}
.reveal.armed.in{opacity:1;transform:none;
  transition:opacity .55s cubic-bezier(.2,.8,.3,1),transform .55s cubic-bezier(.2,.8,.3,1)}
@media (prefers-reduced-motion:reduce){.reveal,.reveal.armed{opacity:1;transform:none}}""")

# arm on observe, and disarm everything after a second whatever happened
rep("""  if(!('IntersectionObserver' in window)) return;""",
"""  if(!('IntersectionObserver' in window)) return;
  /* Arm only what the observer is actually watching, and drop the safety net
     a second later so nothing can be left invisible by a missed callback. */
  (function(){
    const armed=[...document.querySelectorAll('.reveal:not(.in):not(.armed)')];
    armed.forEach(e=>e.classList.add('armed'));
    setTimeout(()=>armed.forEach(e=>e.classList.add('in')), 1000);
  })();""")

# ---------------------------------------------------------------- 3. cutouts
# only the surfaces that need them: campaigns, deals, tiles, the prize bundle
NEED = [
    # category tiles
    'disp2', 'rx184', 'r046', 'nic0', 'exotic0', 'rx001', 'r000', 'r011',
    'rx102', 'r028', 'r066', 'cig0', 'r055', 'r034', 'r068',
    # campaigns and deals
    'rx065', 'rx063', 'rx089', 'rx088', 'disp3', 'exotic1', 'rx003',
    # the prize table
    'rx119', 'rx097', 'r039', 'rx092',
    # spares used by the ads
    'rx086', 'rx090', 'rx066', 'exotic2',
]
table = {}
missing = []
for pid in NEED:
    f = os.path.join(CUT, pid + '.webp')
    if not os.path.exists(f):
        missing.append(pid); continue
    table[pid] = 'data:image/webp;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
print('  %d cutouts, %.0f KB embedded; missing %s'
      % (len(table), sum(len(v) for v in table.values()) / 1024, missing or 'none'))

BLOCK = (
"/* ==========================================================================\n"
"   THE CUTOUTS\n"
"   The same official photographs as LOCAL_PHOTOS, with the studio sweep taken\n"
"   off: keyed away where the source was printed on white, or the\n"
"   manufacturer's own alpha where they shipped a transparent PNG. Only the\n"
"   background was removed — no pixel of any product was recoloured, stretched\n"
"   or redrawn.\n"
"\n"
"   This is what lets a product sit ON a designed ground with its own lighting\n"
"   and shadow instead of inside a white rectangle.\n"
"   ========================================================================== */\n"
"const CUTOUTS = " + json.dumps(table, separators=(',', ':')) + ";\n"
"/* the cut-out if there is one, else the photograph; never nothing */\n"
"const cutout = id => (CUTOUTS[id] || (typeof LOCAL_PHOTOS!=='undefined' ? LOCAL_PHOTOS[id] : '') || '');\n"
"/* find the product a brand+model names, so a design can ask for it by name */\n"
"function pidFor(brand, model){\n"
"  const list=(typeof ALL_PRODUCTS!=='undefined'&&ALL_PRODUCTS.length)?ALL_PRODUCTS:(typeof PRODUCTS!=='undefined'?PRODUCTS:[]);\n"
"  const n=x=>String(x||'').toLowerCase().replace(/[^a-z0-9]/g,''), want=n(model);\n"
"  const hit=list.find(p=>p.brand===brand&&p.name===model)\n"
"        || list.find(p=>p.brand===brand&&(n(p.name).indexOf(want)>=0||want.indexOf(n(p.name))>=0))\n"
"        || list.find(p=>p.brand===brand);\n"
"  return hit?hit.id:'';\n"
"}\n"
)
rep("const SEED_PHOTOS=[];", BLOCK + "const SEED_PHOTOS=[];")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes (%.2f MB)' % (n0, len(s), len(s) / 1048576))
