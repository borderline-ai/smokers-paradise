#!/usr/bin/env python3
# Stage 63 — the finishing layer, and the one bug underneath the whole
# "everything is dark grey on dark purple" complaint.
#
# =====================================================================
# THE VEIL
# =====================================================================
# `#appsky` paints the evening-sky background. Its `.sky` is
# `position:absolute; inset:0; z-index:0`, inserted as the first child of
# `#phone`. Being first in the DOM, it looks like it should sit behind the app.
#
# It does not. CSS paints in this order inside a stacking context:
#
#     1. the element's own background
#     2. children with negative z-index
#     3. block-level, in-flow, NON-POSITIONED descendants   <- #main lives here
#     4. floats
#     5. inline content
#     6. POSITIONED descendants with z-index auto or 0      <- .sky lives here
#     7. positive z-index
#
# `#main` and its sections are static, so they are painted at step 3, and the
# sky — positioned, z-index 0 — is painted over them at step 6. It carries
# `background:#100A18` at `opacity:.75`, so every heading, label, price and
# paragraph in the app was being composited through a 75% dark veil:
#
#     white text  255 -> 255*0.25 + 16*0.75 = 76      measured: rgb(76,71,82)
#
# That is exactly the "dark gray text on a nearly black background" in the
# brief, and it is why raising colour tokens never fixed it: the computed
# colour really was #FFFFFF the whole time. The fix is one line.
#
# =====================================================================
# THE FINISHING LAYER
# =====================================================================
# This file is ~4.8 MB with a dozen passes of CSS layered on it, and several
# selectors are now defined four or five times (there are four live `.ckfine`
# rules and three `.bk` rules). Rather than hunt every duplicate, everything
# below is appended as ONE last-wins layer at the end of the stylesheet, so
# there is a single place that decides the type, the contrast, the controls
# and the spacing.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

LAYER = r'''
/* ==========================================================================
   THE FINISHING LAYER
   Appended last on purpose. Every rule above this point has been layered on
   by an earlier pass, and several selectors are defined four or five times
   over. This block is the single authority on ink, type, controls and
   spacing, so there is one place to read and one place to change.
   ========================================================================== */

/* ---- 1. THE VEIL -------------------------------------------------------
   #appsky is the background. It was painting on TOP of the whole app: a
   positioned element with z-index:0 is painted after every non-positioned
   in-flow descendant, and #main is not positioned. Its 75% dark ground was
   dimming white text to rgb(76,71,82) everywhere in the app. One line. */
#appsky, #appsky .sky{z-index:-1}
#main{position:relative; z-index:1}

/* ---- 2. INK ------------------------------------------------------------
   A controlled scale, not "make everything pink". Contrast is against the
   page ground #100A18.
     ink    #FFFFFF  headings                        21.0:1
     ink2   #F1E9F6  card titles, values, prices     18.4:1
     body   #CBBBD8  normal reading copy             10.6:1
     muted  #A797B6  genuinely secondary              6.6:1
     faint  #8E7F9D  the faintest allowed, legal only 4.7:1
   --faint was #786888 (3.5:1) and was carrying disclaimers and form help. */
:root{
  --ink:#FFFFFF; --ink2:#F1E9F6; --body:#CBBBD8;
  --muted:#A797B6; --faint:#8E7F9D;
  --pad:16px;
}

/* ---- 3. TYPE -----------------------------------------------------------
   One copy style:
     Title Case  page and section headings
     sentence    body, form help, disclaimers, buttons
     UPPERCASE   short eyebrow labels only, and never with wide tracking
   The condensed display face carries short promotional headlines. Everything
   a customer has to READ — forms, prices, descriptions, reviews, policies,
   navigation — is set in the text face. */
h1,h2,h3,h4,
.sec-h h3,.pagehead h2,.shelfhead h2,.backbar h2,.spot h3,.give h3,
.lv-panel h3,.storyc b,.signup h4{
  font-family:var(--disp);
  font-weight:800;
  text-transform:none;
  letter-spacing:-.022em;
  color:var(--ink);
  text-shadow:none;
}
.shelfhead h2{font-size:27px;line-height:1.06}
.sec-h h3{font-size:21px;line-height:1.12}
.backbar h2{font-size:23px;line-height:1.1}

/* eyebrows: still uppercase, but readable — tracking down from .22em/.26em */
.eyebrow,.sh-kick,.sh-eye,.sec-h .eyebrow,.lv-kick,.ad-kicker,.ck-eye,
.storyc .st-eye,.lovecard .lv-eye,.pz-eye{
  font-family:var(--mono);
  font-size:10px;
  letter-spacing:.12em;
  text-transform:uppercase;
  color:var(--go-ink);
  opacity:1;
}
/* a whole paragraph never gets the condensed or the mono face */
p,li,.ckfine,.fine,.bagnote,.sec-lead,.lvfine,.sub,.desc,.rvw p,.foot p{
  font-family:var(--body-f);
  letter-spacing:normal;
}
.sec-lead,.bagnote,.desc{color:var(--body);opacity:1}
.fine,.ckfine,.lv-fine{color:var(--muted)}

/* prices stay in the mono face — it is what makes a price read as a price —
   but at full ink, never faint */
.price,.bunit,.ck-money b,.tot b,.card .pr,.pdp .pr{color:var(--ink2)}

/* ---- 4. FORMS ----------------------------------------------------------
   Labels were 10px mono, .18em tracking, in --faint. They are sentence-case
   text now, at reading contrast, because a form label is not decoration. */
.ckfield span,.optlab,.fl-lab,.lvnote b{
  font-family:var(--body-f);
  font-size:13px;
  font-weight:600;
  letter-spacing:normal;
  text-transform:none;
  color:var(--ink2);
  margin-bottom:7px;
  display:block;
}
.ckfield span em{font-style:normal;font-weight:400;color:var(--muted)}
.ckfield input,.optrow input,input[type="tel"],input[type="text"],input[type="email"]{
  background:#241536;
  border:1px solid rgba(255,120,205,.26);
  color:var(--ink);
  font-family:var(--body-f);
  font-size:16px;
  min-height:48px;
}
.ckfield input::placeholder,input::placeholder{color:var(--faint);opacity:1}
.ckfield input:focus,input:focus{
  border-color:rgba(255,47,168,.75);
  box-shadow:0 0 0 3px rgba(255,47,168,.16);
  outline:none;
}

/* ---- 5. CONTROLS -------------------------------------------------------
   Two, and only two: a solid pill that moves the order forward and an
   outlined pill that does not. Same height, same radius, same label case,
   in every corner of the app — including the ones that are <a> tags and were
   picking up the browser's underline. */
.btn,.lv-acts a,.sbtns a,.storecta .btn,.ck-next,#ckNext,#placeBtn,
.cta,.give .btn,.bagacts .btn{
  min-height:48px;
  border-radius:99px;
  font-family:var(--body-f);
  font-weight:700;
  font-size:15px;
  letter-spacing:.005em;
  text-transform:none;
  text-decoration:none;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:0 22px;
}
.btn.neon,.btn:not(.ghost):not(.sec2):not(.outline),.lv-acts .pri,.sbtns .pri,
#ckNext,#placeBtn{
  background:var(--go);
  color:#1A0510;
  border:0;
}
.btn.ghost,.btn.outline,.lv-acts .sec2,.sbtns .sec2{
  background:transparent;
  color:#FFD3EC;
  border:1px solid rgba(255,120,205,.36);
}
.btn:disabled{opacity:.45}
/* nothing full-bleed: a button keeps the page margin */
.storecta,.bagacts,.ckacts{padding-left:var(--pad);padding-right:var(--pad)}

/* ---- 6. SPACING AND CLIPPING ------------------------------------------
   One page margin. Rails bleed on purpose but start at the margin, so the
   first tile is never sliced by the screen edge. Nothing ends underneath the
   bottom bar. */
.pad,.sec-h,.sec-lead,.ckwrap,.backbar,.shelfhead,.filterbar,.lovepage{
  padding-left:var(--pad);
  padding-right:var(--pad);
}
.cattiles,.rail,.dealrail,.brandrail,.chips,.cardrail{
  padding-left:var(--pad);
  padding-right:var(--pad);
  scroll-padding-left:var(--pad);
}
#main{padding-bottom:calc(96px + env(safe-area-inset-bottom,0px))}
.view{min-height:0}

/* the back control sits BESIDE the title, never on it */
.backbar,.backbar.ck{
  display:flex;
  align-items:center;
  gap:12px;
  padding:16px var(--pad) 6px;
}
.backbar h2{flex:1;min-width:0}
.ck-back,.bk{
  width:38px;height:38px;flex:none;
  border-radius:99px;
  display:grid;place-items:center;
  border:1px solid rgba(255,120,205,.3);
  background:rgba(255,120,205,.08);
  color:var(--ink);
}
.ck-back svg,.bk svg{width:17px;height:17px;stroke:#FFD3EC;fill:none;stroke-width:2.1}

/* ---- 7. THE CHECKOUT IS NOT A SHOPPING SCREEN --------------------------
   The search field and the store strip are shop chrome. In the wizard they
   ate 180px of an 844px phone, pushed the step title toward the header and
   left the Continue button under the bottom bar. They are hidden for the
   four checkout steps and the receipt. */
body:has(#v-checkout.on) .srow,
body:has(#v-checkout.on) .storebar,
body:has(#v-order.on) .srow,
body:has(#v-order.on) .storebar{display:none}

/* the wizard fills the height it has instead of leaving a hole above the nav */
#v-checkout .ckwrap{
  min-height:calc(100dvh - 300px);
  display:flex;
  flex-direction:column;
}
#v-checkout .ckwrap > .ckacts,
#v-checkout .ckwrap > #ckNext,
#v-checkout .ckwrap > #placeBtn{margin-top:auto}
'''

i = s.rindex('</style>')
s = s[:i] + LAYER + s[i:]
print('  finishing layer appended (%d bytes)' % len(LAYER))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
