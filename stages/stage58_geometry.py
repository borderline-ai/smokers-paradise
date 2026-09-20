#!/usr/bin/env python3
# Stage 58 — the geometry, measured rather than guessed.
#
# Three things the render showed:
#
#   1. The TRE House photograph is not a packshot. It is a lifestyle shot of
#      the bar on a dark surface with peanut butter beside it, so keying it
#      does nothing and floating it does not work. It becomes the GROUND —
#      which is what "rich, premium chocolate-inspired atmosphere" actually
#      wants — with the copy over a scrim. That is a fifth layout, earned by
#      the material rather than invented.
#
#   2. The wheel was sized as a share of the card and then cropped by the row
#      it lived in. It is now sized from the row itself, so it is always whole.
#
#   3. .l-hero put the products at 82% of the card height starting near the
#      top, which ran them straight through the headline. Art owns the upper
#      three fifths, the copy owns the lower two, and they no longer meet.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:56].replace('\n', ' '))


# ---- TRE becomes a photographic hero --------------------------------------
rep("""  { id:'d-tre', concept:'tre', layout:'stack',""",
    """  { id:'d-tre', concept:'tre', layout:'photo',""")

rep("""function adArt(d){
  if(d.art_kind === 'wheel')""",
"""function adArt(d){
  /* A layout whose artwork IS a photograph: the picture is the ground and the
     copy sits on a scrim over it. Used where the source is a lifestyle shot
     rather than a packshot, because keying a scene does nothing useful. */
  if(d.layout === 'photo'){
    const a = (d.art||[])[0]; if(!a) return '';
    const pid = pidFor(a.b, a.m); if(!pid) return '';
    const src = (typeof LOCAL_PHOTOS!=='undefined' && LOCAL_PHOTOS[pid]) || cutout(pid);
    if(!src) return '';
    const p = P(pid);
    return `<div class="ad-art photoart">
      <img class="ad-photo" src="${src}" alt="${esc(p?p.brand+' '+p.name:'')}"
        loading="lazy" decoding="async"></div>`;
  }
  if(d.art_kind === 'wheel')""")

CSS = r'''
/* ---- .l-photo: the photograph is the ground ---- */
.ad.l-photo{grid-template-rows:1fr;min-height:360px}
.ad.l-photo .ad-art{grid-row:1;grid-column:1;position:relative}
.ad.l-photo .photoart{position:absolute;inset:0}
.ad.l-photo .ad-photo{position:absolute;inset:0;width:100%;height:100%;
  object-fit:cover;object-position:center 42%}
.ad.l-photo .ad-copy{grid-row:1;grid-column:1;align-self:end;
  justify-content:flex-end;padding:80px 18px 22px;
  background:linear-gradient(to top, var(--scrim) 0%, var(--scrim) 46%,
    rgba(0,0,0,.24) 74%, transparent 100%)}
.ad.l-photo .ad-glow,.ad.l-photo .ad-floor{display:none}

/* ---- .l-hero: art owns the top, copy owns the bottom, they never meet ---- */
.ad.l-hero{grid-template-rows:1fr;min-height:352px}
.ad.l-hero .ad-copy{padding:0 18px 20px;justify-content:flex-end;
  background:linear-gradient(to top, var(--scrim) 0%, var(--scrim) 38%,
    rgba(0,0,0,.30) 62%, transparent 82%)}
.ad.l-hero .ad-p.lead{left:64%;top:3%;transform:translateX(-50%);
  max-height:52%;max-width:50%}
.ad.l-hero .ad-p.back{left:26%;top:9%;transform:translateX(-50%);
  max-height:40%;max-width:36%}
.ad.l-hero .ad-glow{left:58%;top:26%;width:96%}

/* ---- the wheel is sized from the row it stands in, so it is always whole -- */
.ad.c-spin .wheelart{position:relative;display:grid;place-items:center;
  min-height:196px;overflow:hidden}
.ad-wheel{position:relative;z-index:3;height:86%;aspect-ratio:1/1;width:auto;
  max-width:82%;margin:0 6% 0 auto;
  filter:drop-shadow(0 16px 22px rgba(0,0,0,.55))}
.ad-rays{left:66%}

/* ---- the raffle table sits inside its frame ---- */
.ad.c-raffle .prizeart{padding:10px 10px 0}
.pz-stage.lit{aspect-ratio:16/8.4}
.pz-stage.lit .pz-i{transform:translateX(-50%) scale(.9);transform-origin:bottom center}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  geometry appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
