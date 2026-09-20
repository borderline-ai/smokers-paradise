#!/usr/bin/env python3
# Stage 54 — the art direction itself.
#
# Six grounds, six lighting setups, four layouts. The rule that makes it hold
# together as one page: the type system, the radius, the CTA and the spacing
# are shared, and NOTHING else is. Each concept owns its colour, its light and
# where the product sits.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

CSS = r'''
/* ==========================================================================
   ADVERTISEMENTS

   .ad            the shell: shared radius, type scale, CTA, spacing
   .c-*           the concept: ground, lighting, product placement
   .l-*           the layout: where the copy and the artwork sit

   Products are transparent cut-outs, so each one is lit from behind by its
   concept's own glow and stands on a real floor shadow. No white boxes.
   ========================================================================== */
.adstack{display:flex;flex-direction:column;gap:14px}

.ad{position:relative;display:grid;border-radius:var(--r-card);overflow:hidden;
  isolation:isolate;box-shadow:var(--sh-1);min-height:300px;
  padding:0;border:0;text-align:left}
.ad-bg{position:absolute;inset:0;z-index:0;background:var(--ground)}

/* ---- artwork ---- */
.ad-art{position:relative;z-index:1;pointer-events:none}
.ad-glow{position:absolute;left:50%;top:46%;width:118%;aspect-ratio:1/1;
  transform:translate(-50%,-50%);border-radius:50%;
  background:radial-gradient(circle, var(--lite) 0%, transparent 66%);
  opacity:.9;filter:blur(2px)}
/* the floor the product stands on, not a halo around it */
.ad-floor{position:absolute;left:50%;bottom:8%;width:74%;height:16px;
  transform:translateX(-50%);border-radius:50%;filter:blur(9px);
  background:radial-gradient(50% 50% at 50% 50%,
    rgba(0,0,0,.62) 0%, rgba(0,0,0,.24) 56%, rgba(0,0,0,0) 100%)}
.ad-p{position:absolute;display:block;width:auto;height:auto;max-width:none;
  object-fit:contain}
/* a cut-out casts a real shadow; a rectangle cannot */
.ad-p.lead{filter:drop-shadow(0 18px 22px rgba(0,0,0,.55))
                 drop-shadow(0 2px 3px rgba(0,0,0,.35));z-index:3}
.ad-p.back{filter:drop-shadow(0 14px 18px rgba(0,0,0,.45));z-index:2;opacity:.96}

/* ---- copy ---- */
.ad-copy{position:relative;z-index:4;display:flex;flex-direction:column;
  align-items:flex-start;justify-content:center;padding:22px 18px}
.ad .ad-kick{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;line-height:1.2;color:var(--kick);opacity:1}
.ad .ad-title{font-family:var(--disp);font-weight:800;letter-spacing:-.04em;
  line-height:.96;font-size:26px;margin:9px 0 0;color:#FFF;text-shadow:none;
  text-transform:none}
.ad-offer{display:flex;align-items:baseline;gap:9px;margin:12px 0 0}
.ad-offer b{font-family:var(--block);font-weight:600;letter-spacing:-.01em;
  line-height:.88;font-size:46px;color:var(--price)}
.ad-offer i{font-family:var(--mono);font-style:normal;font-size:10.5px;
  letter-spacing:.08em;text-transform:uppercase;color:#FFF;opacity:.82;
  padding:5px 9px;border-radius:var(--r-chip);
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.30)}
.ad .ad-sub{font-size:12.5px;line-height:1.45;margin:10px 0 0;color:#FFF;
  opacity:.82;max-width:30ch;text-shadow:none}
.ad-acts{display:flex;align-items:center;gap:10px;margin:16px 0 0;flex-wrap:wrap}
.ad-cta{display:inline-flex;align-items:center;gap:7px;background:var(--go);
  color:#2A0016;border:0;border-radius:var(--r-chip);padding:11px 18px;
  box-shadow:var(--sh-2);font-family:var(--block);font-weight:600;
  text-transform:uppercase;letter-spacing:.05em;font-size:11.5px;line-height:1;
  white-space:nowrap;cursor:pointer}
.ad-cta svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2.4;
  stroke-linecap:round;stroke-linejoin:round}
.ad-save{background:transparent;color:#FFF;border:0;border-radius:var(--r-chip);
  padding:11px 16px;box-shadow:inset 0 0 0 1.4px rgba(255,255,255,.36);
  font-family:var(--block);font-weight:500;text-transform:uppercase;
  letter-spacing:.05em;font-size:11.5px;line-height:1;cursor:pointer}
.ad-save.got{background:rgba(255,255,255,.16);box-shadow:none}
.ad .ad-fine{font-size:9px;line-height:1.42;margin:12px 0 0;color:#FFF;
  opacity:.58;max-width:40ch}

/* ==========================================================================
   LAYOUTS
   ========================================================================== */
/* copy above, artwork below and bleeding off the right corner */
.ad.l-split{grid-template-rows:auto minmax(128px,1fr)}
.ad.l-split .ad-copy{grid-row:1;padding-bottom:2px}
.ad.l-split .ad-art{grid-row:2}
.ad.l-split .ad-p.lead{right:6%;bottom:-6%;max-height:126%;max-width:52%}
.ad.l-split .ad-p.back{right:44%;bottom:2%;max-height:92%;max-width:40%}
.ad.l-split .ad-glow{left:66%;top:52%;width:104%}
.ad.l-split .ad-floor{left:56%;width:66%}

/* artwork large and low, copy sitting above it */
.ad.l-stack{grid-template-rows:auto minmax(150px,1fr);min-height:340px}
.ad.l-stack .ad-copy{grid-row:1;padding-bottom:0}
.ad.l-stack .ad-art{grid-row:2}
.ad.l-stack .ad-p.lead{left:52%;bottom:-10%;transform:translateX(-50%) rotate(-3deg);
  max-height:132%;max-width:88%}
.ad.l-stack .ad-p.back{left:12%;bottom:12%;transform:rotate(6deg);
  max-height:82%;max-width:52%}
.ad.l-stack .ad-glow{left:50%;top:56%;width:130%}
.ad.l-stack .ad-floor{left:52%;width:72%;bottom:4%}

/* artwork the whole panel, copy over a scrim at the bottom */
.ad.l-hero{grid-template-rows:1fr;min-height:340px}
.ad.l-hero .ad-art{grid-row:1;grid-column:1}
.ad.l-hero .ad-copy{grid-row:1;grid-column:1;align-self:end;justify-content:flex-end;
  padding-top:96px;
  background:linear-gradient(to top, var(--scrim) 0%, var(--scrim) 42%,
    transparent 100%)}
.ad.l-hero .ad-p.lead{left:66%;top:-4%;transform:translateX(-50%);
  max-height:82%;max-width:60%}
.ad.l-hero .ad-p.back{left:24%;top:8%;transform:translateX(-50%);
  max-height:60%;max-width:42%}
.ad.l-hero .ad-glow{left:60%;top:34%;width:110%}
.ad.l-hero .ad-floor{display:none}

/* artwork on the left, copy on the right */
.ad.l-reverse{grid-template-rows:auto minmax(140px,1fr);min-height:330px}
.ad.l-reverse .ad-copy{grid-row:1;align-items:flex-end;text-align:right;
  padding-bottom:0}
.ad.l-reverse .ad-copy .ad-offer{justify-content:flex-end}
.ad.l-reverse .ad-acts{justify-content:flex-end}
.ad.l-reverse .ad-art{grid-row:2}
.ad.l-reverse .ad-p.lead{left:6%;bottom:-4%;max-height:122%;max-width:52%}
.ad.l-reverse .ad-p.back{left:46%;bottom:6%;max-height:84%;max-width:40%}
.ad.l-reverse .ad-glow{left:34%;top:52%;width:104%}
.ad.l-reverse .ad-floor{left:40%;width:66%}

/* artwork centred above its own copy */
.ad.l-center{grid-template-rows:minmax(190px,auto) auto;min-height:360px}
.ad.l-center .ad-art{grid-row:1}
.ad.l-center .ad-copy{grid-row:2}
.ad.l-center .ad-glow{left:50%;top:52%;width:120%}
.ad.l-center .ad-floor{display:none}

/* ==========================================================================
   CONCEPTS — the ground, the light, and the colour of the price
   ========================================================================== */

/* iced cyan, off the Crystal Cube packaging */
.ad.c-offstamp{--ground:linear-gradient(152deg,#06212F 0%,#0B3B50 52%,#10586E 100%);
  --lite:rgba(94,214,255,.42);--kick:#7FE0FF;--price:#FFFFFF;--scrim:rgba(4,20,28,.92)}
.ad.c-offstamp .ad-p.lead{transform:rotate(-7deg)}
.ad.c-offstamp .ad-p.back{transform:rotate(8deg)}

/* cacao and gold, off the TRE House wrapper */
.ad.c-tre{--ground:linear-gradient(158deg,#1B0F06 0%,#3E200A 50%,#6A3D12 100%);
  --lite:rgba(255,186,92,.34);--kick:#FFC876;--price:#FFD9A0;--scrim:rgba(20,10,4,.92)}

/* carnival: magenta into gold */
.ad.c-spin{--ground:linear-gradient(150deg,#2C0738 0%,#630C4E 48%,#9A1440 100%);
  --lite:rgba(255,196,60,.40);--kick:#FFD166;--price:#FFD166;--scrim:rgba(24,4,28,.92)}

/* the raffle table, lit from behind */
.ad.c-raffle{--ground:linear-gradient(163deg,#170922 0%,#2B0F33 54%,#43122F 100%);
  --lite:rgba(255,47,168,.30);--kick:var(--go-ink);--price:#FFFFFF;--scrim:rgba(14,5,20,.92)}

/* near-black graphite, one cool rim light: glass photographed as glass */
.ad.c-glass{--ground:linear-gradient(155deg,#07080C 0%,#12141C 58%,#0B1622 100%);
  --lite:rgba(150,220,255,.30);--kick:#9FD8F5;--price:#FFFFFF;--scrim:rgba(5,6,10,.94)}

/* graphite and violet: the device as technology */
.ad.c-puffco{--ground:linear-gradient(160deg,#0A0713 0%,#1D1036 54%,#301457 100%);
  --lite:rgba(168,139,242,.36);--kick:#C7B0FF;--price:#FFFFFF;--scrim:rgba(8,5,16,.92)}

/* ---- the wheel: whole, never cropped ---- */
.ad.c-spin .wheelart{display:grid;place-items:center;overflow:hidden}
.ad-rays{position:absolute;left:62%;top:50%;width:150%;aspect-ratio:1/1;
  transform:translate(-50%,-50%);border-radius:50%;opacity:.5;
  background:repeating-conic-gradient(from 0deg,
    rgba(255,209,102,.20) 0deg 9deg, rgba(255,209,102,0) 9deg 18deg);
  -webkit-mask-image:radial-gradient(circle, #000 24%, transparent 72%);
  mask-image:radial-gradient(circle, #000 24%, transparent 72%)}
.ad-wheel{position:relative;z-index:3;width:min(72%, 190px);aspect-ratio:1/1;
  margin-left:auto;margin-right:6%;
  filter:drop-shadow(0 16px 22px rgba(0,0,0,.55))}
.ad-wheel svg{width:100%;height:100%;display:block}

/* ---- the prize table on a dark stage ---- */
.ad.c-raffle .prizeart{padding:6px 0 0}
.pz-stage.lit{position:relative;width:100%;aspect-ratio:16/9;background:none}
.pz-stage.lit .pz-i img{filter:drop-shadow(0 14px 18px rgba(0,0,0,.6))}
.pz-stage.lit .pz-sh{background:radial-gradient(50% 50% at 50% 50%,
  rgba(0,0,0,.66) 0%, rgba(0,0,0,.26) 56%, rgba(0,0,0,0) 100%)}

/* ---- more room once the column is wide enough ---- */
@container (min-width:560px){
  .ad.l-split,.ad.l-reverse{grid-template-rows:1fr;
    grid-template-columns:minmax(0,54%) 1fr;align-items:stretch;min-height:300px}
  .ad.l-split .ad-copy{grid-row:1;grid-column:1;padding:30px 12px 30px 30px}
  .ad.l-split .ad-art{grid-row:1;grid-column:2}
  .ad.l-reverse .ad-copy{grid-row:1;grid-column:2;padding:30px 30px 30px 12px}
  .ad.l-reverse .ad-art{grid-row:1;grid-column:1}
  .ad .ad-title{font-size:32px}
  .ad-offer b{font-size:54px}
}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
io.open(P, 'w', encoding='utf-8').write(s)
print('%d -> %d bytes' % (n0, len(s)))
