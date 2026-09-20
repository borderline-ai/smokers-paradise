#!/usr/bin/env python3
# Stage 38 — the campaign gets a real layout.
#
# Stage 36 got the art direction right and the geometry wrong: the copy was in
# flow, everything else was absolute, and nothing reserved space for anything
# else. The headline ran under the product, the CTA sat on the legal line, the
# mark sat under the CTA and the carousel dots sat on all of it.
#
# A campaign is laid out, not stacked with z-index. So:
#
#   mobile   one column, two rows. Copy owns the top row and takes exactly the
#            height it needs. The product owns the rest and is cropped by the
#            bottom-right corner.
#   desktop  two columns. Copy left, product right, cropped by the right edge.
#
# The legal line lives inside the copy, because it is copy. The signature is a
# wordmark in the corner, set in ink — the neon mark is for dark grounds and
# vanishes on a light one, so it stays on the editorial pieces where it works.
# The dots move out from under the composition and sit below the carousel.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def cut(start_marker, end_marker):
    """Remove a whole CSS block that a previous stage appended."""
    global s
    i = s.index(start_marker)
    j = s.index(end_marker, i)
    s = s[:i] + s[j:]
    print('  cut:', start_marker.strip().splitlines()[0][:56])


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


# ---- take stage 36's and 37's layout rules out; the language stays, the
#      geometry is rewritten below in one piece -----------------------------
cut('\n/* ==========================================================================\n   THE CAMPAIGN SYSTEM', '</style>')

# ---- the signature: a wordmark in ink, not the neon mark on a light field --
rep("""    ${c.mark?`<span class="camp-mark">${markImg('cmark'+c.id)}</span>`:''}
    ${c.disclaimer?`<span class="camp-fine">${esc(c.disclaimer)}</span>`:''}""",
"""    ${c.mark && !light ? `<span class="camp-mark">${markImg('cmark'+c.id)}</span>` : ''}
    ${light ? `<span class="camp-sig" aria-hidden="true">Smokers Paradise</span>` : ''}""")

# the legal line is copy, so it sits in the copy
rep("""    <span class="camp-cta">${esc(c.cta)} ${ARROW}</span>
  </div>`;""",
"""    <span class="camp-cta">${esc(c.cta)} ${ARROW}</span>
    ${c.disclaimer?`<span class="camp-fine">${esc(c.disclaimer)}</span>`:''}
  </div>`;""")

# campCopy needs the campaign to hand it the disclaimer
rep("""    ${campCopy(c)}""", """    ${campCopy(c)}""")

CSS = r'''
/* ==========================================================================
   THE CAMPAIGN SYSTEM

   Three shapes, one language.

     .camp.lead    full width. Copy over product on a phone, copy beside
                   product on a desktop. The product is cropped by the frame.
     .camp.tall    the same language at half width, vertical, showing less.
     .camp.editor  no product: a real photograph, dark, editorial.

   The light campaigns put white under the product and the packaging colour
   away from it. That is why there is no plate, no edge and no halo — a
   manufacturer packshot printed on white has nothing to sit on.
   ========================================================================== */

.camp{position:relative;display:grid;width:100%;text-align:left;border:0;padding:0;
  border-radius:var(--r-card);overflow:hidden;isolation:isolate;
  box-shadow:var(--sh-1);cursor:pointer;background:var(--f0,#150A20)}
.camp:active{transform:scale(.995)}

/* ---- the ground ---- */
.camp-field{position:absolute;inset:0;z-index:0;
  background:linear-gradient(158deg,
    var(--f0) 0%, var(--f0) 30%, var(--f1) 66%, var(--f2) 100%)}
/* One shape. The product overlaps it, and overlap is what reads as depth;
   on its own it is a colour field, not a decoration. */
.camp-block{position:absolute;z-index:1;pointer-events:none;
  background:var(--blk);opacity:.22;border-radius:50%}

/* ---- the copy ---- */
.camp-copy{position:relative;z-index:4;display:flex;flex-direction:column;
  align-items:flex-start;justify-content:center}
.camp-kick{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;line-height:1;color:var(--acc)}
.camp-head{font-family:var(--disp);font-weight:800;letter-spacing:-.045em;
  line-height:.93;margin:10px 0 0;color:var(--cink);text-wrap:balance}
.camp-offer{display:flex;align-items:baseline;gap:8px;margin:12px 0 0}
.camp-offer b{font-family:var(--block);font-weight:400;letter-spacing:-.02em;
  color:var(--cink);line-height:.9}
.camp-offer i{font-family:var(--mono);font-style:normal;font-size:10px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--acc)}
.camp-sub{font-size:12.5px;line-height:1.4;margin:9px 0 0;color:var(--cink);
  opacity:.7;max-width:26ch}
.camp-cta{margin:15px 0 0;display:inline-flex;align-items:center;gap:7px;
  background:var(--go);color:#2A0016;border-radius:var(--r-chip);
  padding:10px 17px;box-shadow:var(--sh-2);
  font-family:var(--block);text-transform:uppercase;letter-spacing:.045em;
  font-size:11px;line-height:1}
.camp-cta svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.4;
  stroke-linecap:round;stroke-linejoin:round}
.camp-fine{margin:11px 0 0;font-size:8.5px;line-height:1.35;
  color:var(--cink);opacity:.5;max-width:34ch}

/* the signature, where a printed campaign signs itself */
.camp-sig{position:absolute;z-index:5;pointer-events:none;
  font-family:var(--mono);font-size:8.5px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--cink);opacity:.42}

/* ---- the product ---- */
.camp-shot{position:relative;z-index:2;pointer-events:none;overflow:visible}
.camp-shot img{position:absolute;display:block;object-fit:contain;
  width:auto;max-width:none}
/* the contact shadow: on the ground under the product, never behind it */
.camp-ground{position:absolute;border-radius:50%;filter:blur(8px);
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(20,8,30,.30) 0%, rgba(20,8,30,.13) 54%, rgba(20,8,30,0) 100%)}
.camp-lead{filter:drop-shadow(0 16px 22px rgba(20,8,30,.22))}
.camp-back{filter:drop-shadow(0 12px 18px rgba(20,8,30,.16));opacity:.94}

/* ==================== .camp.lead ========================================= */
/* phone: copy takes what it needs, the product takes the rest */
.camp.lead{grid-template-rows:auto minmax(150px,1fr);min-height:412px}
.camp.lead .camp-copy{grid-row:1;padding:24px 20px 4px}
.camp.lead .camp-head{font-size:clamp(28px,8.6vw,38px)}
.camp.lead .camp-offer b{font-size:36px}
.camp.lead .camp-shot{grid-row:2}
.camp.lead .camp-lead{right:-4%;bottom:-6%;height:112%}
.camp.lead .camp-back{right:38%;bottom:4%;height:74%}
.camp.lead .camp-ground{right:2%;bottom:3%;width:56%;height:16px}
.camp.lead .camp-block{width:150%;height:80%;right:-46%;bottom:-24%}
.camp.lead .camp-sig{left:20px;bottom:14px}

@media (min-width:620px){
  .camp.lead{grid-template-rows:1fr;grid-template-columns:minmax(0,50%) 1fr;
    min-height:360px;align-items:center}
  .camp.lead .camp-copy{grid-row:1;grid-column:1;padding:34px 10px 34px 36px}
  .camp.lead .camp-head{font-size:44px}
  .camp.lead .camp-offer b{font-size:46px}
  .camp.lead .camp-shot{grid-row:1;grid-column:2;align-self:stretch}
  .camp.lead .camp-lead{right:2%;bottom:-4%;height:100%}
  .camp.lead .camp-back{right:44%;bottom:8%;height:70%}
  .camp.lead .camp-ground{right:6%;bottom:6%;width:50%;height:20px}
  .camp.lead .camp-block{width:120%;height:150%;right:-30%;bottom:-40%}
  .camp.lead .camp-sig{left:36px;bottom:18px}
}

/* ==================== .camp.tall ========================================= */
/* Half the width shows less. Dropping the line beats shrinking everything
   until it fits. */
.camp.tall{grid-template-rows:auto minmax(120px,1fr);min-height:336px}
.camp.tall .camp-copy{grid-row:1;padding:18px 16px 2px}
.camp.tall .camp-head{font-size:23px}
.camp.tall .camp-offer b{font-size:30px}
.camp.tall .camp-sub{display:none}
.camp.tall .camp-cta{margin-top:13px;padding:9px 14px;font-size:10.5px}
.camp.tall .camp-fine{font-size:8px}
.camp.tall .camp-shot{grid-row:2}
.camp.tall .camp-lead{left:50%;transform:translateX(-46%);bottom:-8%;height:116%}
.camp.tall .camp-back{left:6%;bottom:2%;height:82%}
.camp.tall .camp-ground{left:50%;transform:translateX(-46%);bottom:3%;
  width:62%;height:14px}
.camp.tall .camp-block{width:190%;height:80%;left:-45%;bottom:-30%}
.camp.tall .camp-sig{left:16px;bottom:11px}

/* ==================== .camp.editor ======================================= */
.camp.dark{background:#150A20;min-height:336px;grid-template-rows:1fr;
  box-shadow:var(--sh-1), inset 0 0 0 1px rgba(255,123,200,.16)}
.camp.dark .camp-photo{position:absolute;inset:0;z-index:0}
.camp.dark .camp-photo img{width:100%;height:100%;object-fit:cover;
  object-position:center 42%}
/* One gradient, weighted to the copy, so the photograph stays a photograph
   instead of disappearing under a flat scrim. */
.camp.dark .camp-photo::after{content:"";position:absolute;inset:0;
  background:linear-gradient(2deg,
    rgba(11,4,18,.95) 0%, rgba(11,4,18,.80) 34%,
    rgba(11,4,18,.34) 64%, rgba(11,4,18,.08) 100%)}
.camp.dark .camp-copy{grid-row:1;align-self:end;padding:0 18px 20px;z-index:4}
.camp.dark .camp-kick{color:var(--go-ink)}
.camp.dark .camp-head{color:#FFF;font-size:27px}
.camp.dark .camp-sub{color:#F3E9F6;opacity:.84;font-size:12px;max-width:24ch}
.camp.dark .camp-fine{color:#F3E9F6}
.camp.dark .camp-mark{position:absolute;z-index:5;pointer-events:none;
  right:18px;top:16px;width:58px}
.camp.dark .camp-mark .hcm{width:100%}

/* the award runs full width in the carousel, so it gets more air */
#hero .camp.dark{min-height:412px}
#hero .camp.dark .camp-head{font-size:clamp(30px,9vw,40px)}
#hero .camp.dark .camp-copy{padding:0 20px 26px}
@media (min-width:620px){
  #hero .camp.dark{min-height:360px}
  #hero .camp.dark .camp-photo img{object-position:center 38%}
  #hero .camp.dark .camp-copy{max-width:56%;padding:0 36px 34px}
  #hero .camp.dark .camp-head{font-size:44px}
}

/* ==================== the carousel shell ================================= */
/* The cell is a track cell and nothing more; the campaign sizes itself. */
#hero .slide{flex:0 0 100%;min-width:100%;height:auto!important;min-height:0;
  padding:0;background:none;border:0;box-shadow:none;border-radius:0;
  overflow:visible;display:grid}
.promoc{border-radius:var(--r-card);overflow:visible;box-shadow:none;
  margin:0 var(--sp-edge);position:relative;padding-bottom:22px}
.promoc .vp{border-radius:var(--r-card);overflow:hidden;align-items:stretch}
.bpair{display:grid;grid-template-columns:1fr 1fr;gap:11px;
  margin:11px var(--sp-edge) 0}
@media (max-width:480px){.bpair{grid-template-columns:1fr}}

/* Dots below the composition, never on it. */
#hero .dots{position:absolute;left:0;right:0;bottom:0;top:auto;
  display:flex;justify-content:center;gap:7px;z-index:6;transform:none;
  background:none;padding:0;box-shadow:none;border:0;backdrop-filter:none}
#hero .dots button{width:6px;height:6px;border-radius:99px;padding:0;border:0;
  background:rgba(255,123,200,.30);box-shadow:none;transition:width .2s,background .2s}
#hero .dots button.on{width:20px;background:var(--go);box-shadow:none}
/* Arrows sit in the outer margin on a wide screen and are hidden on a phone,
   where the carousel is swiped. */
#hero .arw{z-index:6;top:calc(50% - 11px)}
@media (max-width:619px){#hero .arw{display:none}}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  layout written')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
