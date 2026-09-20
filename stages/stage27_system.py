#!/usr/bin/env python3
# Stage 27 — one image stage, one design system.
#
# The halos go. In their place a single product stage used everywhere: the
# manufacturer photograph, whole and undistorted, inside a neutral panel of
# one colour, one radius, one padding, with one soft contact shadow under it.
# Almost every render this catalogue hotlinks is printed on white, so the
# panel is the honest answer to that and it is applied identically to every
# surface rather than reinvented per component.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:120])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))

# ---------------------------------------------------------------- tokens
rep("""  --glow:rgba(255,47,168,.18);""",
"""  --glow:rgba(255,47,168,.18);

  /* ---- the design system ----
     Every radius, every shadow, every call to action in the app resolves to
     one of these. Components stopped being allowed their own ideas. */
  --r-card:14px;        /* cards, panels, banners, image stages */
  --r-chip:999px;       /* chips, badges, pills, both CTAs */
  --sp-edge:16px;       /* the page's side margin, everywhere */
  --sh-1:0 10px 26px rgba(0,0,0,.34);      /* a card off the page */
  --sh-2:0 3px 10px rgba(0,0,0,.26);       /* a small element */
  --sh-cont:0 8px 12px -6px rgba(0,0,0,.55);/* a product's contact shadow */
  --stage:#F1EDF4;      /* the neutral panel a packshot sits on */
  --stage-line:rgba(20,10,30,.10);""")

# ---------------------------------------------------------------- the stage
rep("""/* Masking, not blending. Blend modes resolve against the nearest stacking
   context, and half these plates sit inside one (a z-index on the art, an
   overflow on the card), so multiply silently returned the source white on
   exactly the surfaces that needed it most. A mask has no such dependency:
   it removes the corners of the file itself, wherever the file happens to be.
   Generous ellipse, long feather, so it eats the white margin a packshot is
   printed on and never the product standing in the middle of it. */
.card .thumb>img,
.ctile .ph img,
.btile .bp img,
.slide .stage .pz.flat img,
.dcard .dart .dplate img,
.dealrow .drart .dplate img,
.spotitem .sp img,
.pdp-art>img{
  -webkit-mask-image:radial-gradient(48% 63% at 50% 48%,
    #000 0%, #000 58%, rgba(0,0,0,.55) 76%, rgba(0,0,0,0) 92%);
  mask-image:radial-gradient(48% 63% at 50% 48%,
    #000 0%, #000 58%, rgba(0,0,0,.55) 76%, rgba(0,0,0,0) 92%)}""",
"""/* ---- ONE PRODUCT STAGE ----
   Masking the white ground away worked, but it left a soft glowing egg behind
   every product, which is its own kind of cheap: the product stopped looking
   photographed and started looking pasted on.

   So the photograph is used whole and on purpose. A neutral panel, one colour
   and one radius across the entire app, the product contained inside it at a
   consistent scale with consistent padding, and one soft contact shadow under
   the PANEL rather than a halo around the product. Nothing glows. Nothing is
   blurred. Every shelf, rail, tile, banner and deal card uses this. */
.stage-panel{background:var(--stage);border-radius:var(--r-card);
  box-shadow:var(--sh-cont), inset 0 0 0 1px var(--stage-line);
  overflow:hidden;position:relative;display:grid;place-items:center}
.stage-panel>img{width:100%;height:100%;object-fit:contain;padding:9%;
  -webkit-mask-image:none;mask-image:none;filter:none;mix-blend-mode:normal}""")

# every surface adopts it
rep(""".card .thumb{aspect-ratio:1/1;height:auto;position:relative;padding:0;overflow:visible}""",
""".card .thumb{aspect-ratio:1/1;height:auto;position:relative;padding:0;overflow:hidden;
  background:var(--stage);border-radius:var(--r-card) var(--r-card) 0 0}""")
rep(""".card .thumb{background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%)}""",
""".card .thumb{background:var(--stage)}""")
rep(""".card .thumb>svg,.card .thumb>img{position:absolute;inset:10.5%;width:79%;height:79%;
  object-fit:contain;object-position:center}""",
""".card .thumb>svg,.card .thumb>img{position:absolute;inset:9%;width:82%;height:82%;
  object-fit:contain;object-position:center}""")

rep(""".ctile .ph{width:104px;height:104px;border-radius:16px;
  background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%);
  display:grid;place-items:center;overflow:visible;position:relative;transition:transform .18s}""",
""".ctile .ph{width:104px;height:104px;border-radius:var(--r-card);
  background:var(--stage);box-shadow:var(--sh-cont),inset 0 0 0 1px var(--stage-line);
  display:grid;place-items:center;overflow:hidden;position:relative;transition:transform .18s}""")

rep(""".btile .bp{height:56px;display:grid;place-items:center;width:100%;border-radius:8px;
  background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%)}""",
""".btile .bp{height:56px;display:grid;place-items:center;width:100%;border-radius:10px;
  background:var(--stage);box-shadow:inset 0 0 0 1px var(--stage-line);overflow:hidden}""")

rep(""".dcard .dart .dplate{position:absolute;inset:0;border-radius:12px;
  background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%);""",
""".dcard .dart .dplate{position:absolute;inset:0;border-radius:var(--r-card);
  background:var(--stage);box-shadow:var(--sh-cont),inset 0 0 0 1px var(--stage-line);overflow:hidden;""")
rep(""".dealrow .drart .dplate{position:absolute;inset:0;border-radius:13px;
  background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%);""",
""".dealrow .drart .dplate{position:absolute;inset:0;border-radius:var(--r-card);
  background:var(--stage);box-shadow:var(--sh-cont),inset 0 0 0 1px var(--stage-line);overflow:hidden;""")

rep(""".spotitem .sp{height:104px;border-radius:13px;
  background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%);""",
""".spotitem .sp{height:104px;border-radius:var(--r-card);
  background:var(--stage);box-shadow:var(--sh-cont),inset 0 0 0 1px var(--stage-line);overflow:hidden;""")

# the hero fan: same panel, no pool, no halo
rep("""  background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%)}
.slide .stage .pz.flat img{filter:none}""",
"""  background:var(--stage);box-shadow:var(--sh-cont),inset 0 0 0 1px var(--stage-line);
  overflow:hidden}
.slide .stage .pz.flat img{filter:none;padding:7%;width:100%;height:100%;object-fit:contain}""")
rep(""".pool{background:radial-gradient(34% 52% at 50% 47%,rgba(255,255,255,.98) 0%, rgba(255,255,255,.90) 34%,rgba(255,255,255,.60) 55%, rgba(255,255,255,.28) 72%,rgba(255,255,255,.08) 86%, rgba(255,255,255,0) 100%)}""",
""".pool{background:var(--stage)}""", must=False)
rep(""".slide .stage .pz.flat{border-radius:13px;padding:9px;""",
    """.slide .stage .pz.flat{border-radius:var(--r-card);padding:0;""")

# ---------------------------------------------------------------- CTAs
rep("""/* ---- the discreet shelf ----""",
"""/* ---- CALLS TO ACTION ----
   Two, and only two. A solid magenta pill that moves the order forward, and
   an outlined pill that does not. Everything that used to be a skewed yellow
   slab, a gold outline, a round chip or a green tab is now one of these two.
   A third treatment exists only for a text link, which is not a button. */
const CTA_NOTE = 1;

/* ---- the discreet shelf ----""", must=False)

rep(""".btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:14px;border-radius:12px;""",
    """.btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:14px;border-radius:var(--r-chip);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
