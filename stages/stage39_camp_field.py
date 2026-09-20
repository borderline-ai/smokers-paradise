#!/usr/bin/env python3
# Stage 39 — two things the screenshots settled.
#
# 1. THE FIELD WAS THE WRONG WAY ROUND.
#    White at the top-left behind the copy, colour at the bottom-right under
#    the product — which is exactly backwards. Almost every packshot in this
#    catalogue is printed on white, so putting colour under the product is what
#    draws the white rectangle around it. The colour now sits behind the COPY
#    and the field resolves to clean white across the corner the product stands
#    in, so the packshot's own ground and the campaign's ground are the same
#    white and there is no edge to see. That is also the honest version of what
#    the halos and the plates were trying to fake.
#
# 2. ON A DESKTOP THIS APP RUNS INSIDE A PHONE FRAME.
#    So a viewport media query is measuring the wrong thing: at 1280px the app
#    column is about 372px and every "desktop" rule was firing on a layout that
#    is still a phone. The campaigns now respond to the width of the column
#    they are actually in, which is what container queries are for, and the
#    pair stacks on the same basis.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def cut(start_marker, end_marker):
    global s
    i = s.index(start_marker)
    j = s.index(end_marker, i)
    s = s[:i] + s[j:]
    print('  cut:', start_marker.strip().splitlines()[0][:56])


cut('\n/* ==========================================================================\n   THE CAMPAIGN SYSTEM', '</style>')

CSS = r'''
/* ==========================================================================
   THE CAMPAIGN SYSTEM

   A campaign is a composition, not a card.

     .camp.lead    the featured campaign. Colour behind the copy, white under
                   the product, product cropped by the frame.
     .camp.tall    the same language at half height or half width.
     .camp.editor  no product: a real photograph, dark, editorial.

   THE FIELD. Colour arrives behind the copy and clears to white in the corner
   the product stands in. Nearly every packshot here is printed on white, so
   the packshot's ground and the campaign's ground become the same white and
   there is no plate, no edge and nothing to halo.

   THE MEASUREMENTS ARE CONTAINER QUERIES. On a desktop this app runs inside a
   phone frame, so the viewport is not the column: at 1280px the column is
   about 372px wide and still a phone.
   ========================================================================== */

#hero,.bpair{container-type:inline-size}

.camp{position:relative;display:grid;width:100%;text-align:left;border:0;padding:0;
  border-radius:var(--r-card);overflow:hidden;isolation:isolate;
  box-shadow:var(--sh-1);cursor:pointer;background:var(--f0,#150A20)}
.camp:active{transform:scale(.995)}

/* ---- the ground ---- */
.camp-field{position:absolute;inset:0;z-index:0;
  background:
    linear-gradient(163deg,
      var(--f2) 0%, var(--f1) 26%, var(--f0) 56%, var(--f0) 100%)}
/* One shape, behind the copy, cropped by the frame. The product's contact
   shadow crosses its lower edge, and that overlap is the depth. */
.camp-block{position:absolute;z-index:1;pointer-events:none;
  background:var(--blk);opacity:.20;border-radius:50%}

/* ---- the copy ---- */
.camp-copy{position:relative;z-index:4;display:flex;flex-direction:column;
  align-items:flex-start;justify-content:center}
.camp-kick{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;line-height:1;color:var(--acc)}
.camp-head{font-family:var(--disp);font-weight:800;letter-spacing:-.045em;
  line-height:.93;margin:10px 0 0;color:var(--cink);text-wrap:balance}
.camp-offer{display:flex;align-items:baseline;gap:8px;margin:11px 0 0}
.camp-offer b{font-family:var(--block);font-weight:400;letter-spacing:-.02em;
  color:var(--cink);line-height:.9}
.camp-offer i{font-family:var(--mono);font-style:normal;font-size:10px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--acc)}
.camp-sub{font-size:12.5px;line-height:1.38;margin:9px 0 0;color:var(--cink);
  opacity:.7;max-width:28ch;display:-webkit-box;-webkit-line-clamp:3;
  -webkit-box-orient:vertical;overflow:hidden}
.camp-cta{margin:14px 0 0;display:inline-flex;align-items:center;gap:7px;
  background:var(--go);color:#2A0016;border-radius:var(--r-chip);
  padding:10px 17px;box-shadow:var(--sh-2);
  font-family:var(--block);text-transform:uppercase;letter-spacing:.045em;
  font-size:11px;line-height:1;white-space:nowrap}
.camp-cta svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.4;
  stroke-linecap:round;stroke-linejoin:round}
.camp-fine{margin:10px 0 0;font-size:8.5px;line-height:1.35;
  color:var(--cink);opacity:.5;max-width:36ch}

/* where a printed campaign signs itself */
.camp-sig{position:absolute;z-index:5;pointer-events:none;
  font-family:var(--mono);font-size:8.5px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--cink);opacity:.40}

/* ---- the product ---- */
.camp-shot{position:relative;z-index:2;pointer-events:none;overflow:visible}
.camp-shot img{position:absolute;display:block;object-fit:contain;
  width:auto;max-width:none}
/* the contact shadow: on the ground under the product, never behind it */
.camp-ground{position:absolute;border-radius:50%;filter:blur(8px);
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(20,8,30,.28) 0%, rgba(20,8,30,.12) 54%, rgba(20,8,30,0) 100%)}
.camp-lead{filter:drop-shadow(0 16px 20px rgba(20,8,30,.20))}
.camp-back{filter:drop-shadow(0 12px 16px rgba(20,8,30,.14));opacity:.94}

/* ==================== .camp.lead ========================================= */
.camp.lead{grid-template-rows:auto minmax(140px,1fr);min-height:392px}
.camp.lead .camp-copy{grid-row:1;padding:24px 20px 6px}
.camp.lead .camp-head{font-size:clamp(27px,8.4vw,36px)}
.camp.lead .camp-offer b{font-size:34px}
.camp.lead .camp-shot{grid-row:2}
.camp.lead .camp-lead{right:-3%;bottom:-6%;height:112%}
.camp.lead .camp-back{right:40%;bottom:5%;height:72%}
.camp.lead .camp-ground{right:3%;bottom:3%;width:54%;height:16px}
.camp.lead .camp-block{width:190%;height:76%;left:-58%;top:-30%}
.camp.lead .camp-sig{left:20px;bottom:14px}

@container (min-width:560px){
  .camp.lead{grid-template-rows:1fr;grid-template-columns:minmax(0,52%) 1fr;
    min-height:352px;align-items:center}
  .camp.lead .camp-copy{grid-row:1;grid-column:1;padding:32px 8px 32px 34px}
  .camp.lead .camp-head{font-size:40px}
  .camp.lead .camp-offer b{font-size:44px}
  .camp.lead .camp-shot{grid-row:1;grid-column:2;align-self:stretch}
  .camp.lead .camp-lead{right:3%;bottom:-4%;height:96%}
  .camp.lead .camp-back{right:46%;bottom:8%;height:68%}
  .camp.lead .camp-ground{right:6%;bottom:6%;width:48%;height:20px}
  .camp.lead .camp-block{width:120%;height:150%;left:-42%;top:-26%}
  .camp.lead .camp-sig{left:34px;bottom:18px}
}

/* ==================== .camp.tall ========================================= */
/* When the pair is stacked this tile is full width and short: copy left,
   product right. When there is room for two columns it stands up. Half the
   width shows less — dropping the line beats shrinking everything to fit. */
.camp.tall{grid-template-columns:minmax(0,1fr) 40%;grid-template-rows:1fr;
  min-height:232px;align-items:center}
.camp.tall .camp-copy{grid-column:1;padding:20px 6px 20px 18px}
.camp.tall .camp-head{font-size:25px}
.camp.tall .camp-offer b{font-size:30px}
.camp.tall .camp-sub{display:none}
.camp.tall .camp-cta{margin-top:13px;padding:9px 15px;font-size:10.5px}
.camp.tall .camp-fine{font-size:8px;margin-top:9px}
.camp.tall .camp-shot{grid-column:2;align-self:stretch}
.camp.tall .camp-lead{right:2%;bottom:-4%;height:96%}
.camp.tall .camp-back{right:52%;bottom:6%;height:68%}
.camp.tall .camp-ground{right:4%;bottom:5%;width:62%;height:14px}
.camp.tall .camp-block{width:200%;height:150%;left:-70%;top:-28%}
.camp.tall .camp-sig{display:none}

@container (min-width:560px){
  .camp.tall{grid-template-columns:1fr;grid-template-rows:auto minmax(110px,1fr);
    min-height:326px}
  .camp.tall .camp-copy{grid-column:1;grid-row:1;padding:18px 16px 2px}
  .camp.tall .camp-head{font-size:23px}
  .camp.tall .camp-shot{grid-column:1;grid-row:2}
  .camp.tall .camp-lead{left:50%;right:auto;transform:translateX(-44%);
    bottom:-8%;height:118%}
  .camp.tall .camp-back{left:6%;right:auto;bottom:2%;height:80%}
  .camp.tall .camp-ground{left:50%;right:auto;transform:translateX(-44%);
    bottom:3%;width:62%;height:14px}
  .camp.tall .camp-block{width:200%;height:80%;left:-52%;top:-34%}
}

/* ==================== .camp.editor ======================================= */
.camp.dark{background:#150A20;grid-template-rows:1fr;min-height:232px;
  box-shadow:var(--sh-1), inset 0 0 0 1px rgba(255,123,200,.16)}
.camp.dark .camp-photo{position:absolute;inset:0;z-index:0}
.camp.dark .camp-photo img{width:100%;height:100%;object-fit:cover;
  object-position:center 44%}
/* One gradient, weighted to the copy, so the photograph stays a photograph
   instead of disappearing under a flat scrim. */
.camp.dark .camp-photo::after{content:"";position:absolute;inset:0;
  background:linear-gradient(2deg,
    rgba(11,4,18,.95) 0%, rgba(11,4,18,.78) 32%,
    rgba(11,4,18,.30) 62%, rgba(11,4,18,.06) 100%)}
.camp.dark .camp-copy{grid-row:1;align-self:end;padding:0 18px 18px;z-index:4}
.camp.dark .camp-kick{color:var(--go-ink)}
.camp.dark .camp-head{color:#FFF;font-size:26px}
.camp.dark .camp-sub{color:#F3E9F6;opacity:.84;font-size:12px;max-width:24ch}
.camp.dark .camp-fine{color:#F3E9F6}
.camp.dark .camp-mark{position:absolute;z-index:5;pointer-events:none;
  right:17px;top:15px;width:54px}
.camp.dark .camp-mark .hcm{width:100%}

/* the award runs full width in the carousel, so it gets more air */
#hero .camp.dark{min-height:392px}
#hero .camp.dark .camp-head{font-size:clamp(30px,9vw,38px)}
#hero .camp.dark .camp-copy{padding:0 20px 26px}
@container (min-width:560px){
  #hero .camp.dark{min-height:352px}
  #hero .camp.dark .camp-photo img{object-position:center 38%}
  #hero .camp.dark .camp-copy{max-width:58%;padding:0 34px 32px}
  #hero .camp.dark .camp-head{font-size:40px}
}

/* ==================== the carousel shell ================================= */
/* The cell is a track cell and nothing more; the campaign sizes itself. */
#hero .slide{flex:0 0 100%;min-width:100%;height:auto!important;min-height:0;
  padding:0;background:none;border:0;box-shadow:none;border-radius:0;
  overflow:visible;display:grid}
.promoc{border-radius:var(--r-card);overflow:visible;box-shadow:none;
  margin:0 var(--sp-edge);position:relative;padding-bottom:22px}
.promoc .vp{border-radius:var(--r-card);overflow:hidden;align-items:stretch}
.bpair{display:grid;grid-template-columns:1fr;gap:11px;
  margin:11px var(--sp-edge) 0}
@container (min-width:560px){.bpair{grid-template-columns:1fr 1fr}}

/* Dots below the composition, never on it. */
#hero .dots{position:absolute;left:0;right:0;bottom:0;top:auto;
  display:flex;justify-content:center;gap:7px;z-index:6;transform:none;
  background:none;padding:0;box-shadow:none;border:0;backdrop-filter:none}
#hero .dots button{width:6px;height:6px;border-radius:99px;padding:0;border:0;
  background:rgba(255,123,200,.30);box-shadow:none;
  transition:width .2s,background .2s}
#hero .dots button.on{width:20px;background:var(--go);box-shadow:none}
/* Arrows only when there is margin to put them in. The narrow layout is
   swiped, and an arrow sitting on the artwork is the thing this pass is
   removing everywhere else. */
#hero .arw{z-index:6;top:calc(50% - 11px);display:none}
@container (min-width:560px){#hero .arw{display:grid}}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  layout rewritten on container queries')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
