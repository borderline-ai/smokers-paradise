#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 143 — the iPad, and the home screen.
#
# Marco: "Is it going to look good on iphone and ipad and fit to its size with
# ALL the right measurements? We still havent downloaded the app that will
# apear on the home screen on the ipad."
#
# The honest answer was no, and the reason is that every test in this build has
# run at ONE size — 390 x 844, an iPhone. Nothing had ever been opened at iPad
# size. So I opened it at twelve, and here is what came back.
#
# THE PHONES ARE FINE. 375x667 through 430x932, portrait: the app fills the
# screen edge to edge, nothing scrolls sideways, nothing is cut off. That part
# has been right all along.
#
# THE IPAD IS NOT AN APP, IT IS A MOCKUP. On an iPad Pro the app renders as a
# 404 x 858 phone with a drawn bezel, floating in the middle of a 1024 x 1366
# black screen, with three hundred pixels of nothing down each side. On the
# landscape iPads the sales sidecar appears at 1060 wide and shoves the phone
# off to the right. That is the correct design for showing the demo in a
# browser on a laptop, which is what it was built for, and it is the wrong
# thing entirely for the moment Marco hands an iPad across the counter.
#
# The comment on that breakpoint says a tablet should get "the framed app now,
# the same as a laptop". That was a considered decision and it is now wrong,
# because the use has changed: this is going on the home screen.
#
# SO A TABLET FILLS THE SCREEN, and the extra width is used rather than
# stretched. A 390-wide column blown out to 1024 gives hundred-character lines
# and cards the size of a hand; the layout gets a tablet layer instead:
#
#     product grid      2 columns  ->  3 at 700, 4 at 980
#     brand grid        3          ->  4 at 700, 6 at 980
#     department tiles  104px      ->  132px, so the row fills
#     deals             1 column   ->  2 at 820
#     the events pair, the footer columns, the fact plates: all widened
#     prose             capped at a readable measure instead of running the
#                       full width of a 12.9 inch screen
#
# AND THE HOME SCREEN ITSELF, which had nothing at all:
#
#     no <title>                     the icon would be labelled after the file
#     no apple-touch-icon            the icon would be a grey screenshot
#     no apple-mobile-web-app-capable  it opens in Safari with the address bar
#                                    showing, which is not what "an app" means
#     no status bar style            a white iOS status bar over a black app
#     no manifest                    nothing for Android or Chrome
#
# All five are in now, the icon is the shop's own mark on their own magenta,
# and the name under it is "Smokers Paradise".
import io
import base64

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:64].replace('\n', ' '))


# ---- 1. a tablet fills the screen -----------------------------------------
rep("""/* Below this the app fills the screen, above it the app sits in its own
   frame on the desk. The line used to be at 860, which put tablets in the
   full-bleed phone layout: a phone screen stretched to 820 points wide,
   which looks stretched and costs a great deal more sky to paint than it is
   worth. A tablet gets the framed app now, the same as a laptop. */
@media (max-width:740px){#stage{padding:0;display:block}
  #phone{width:100%;height:100vh;height:100dvh;border-radius:0;box-shadow:none}}""",
"""/* WHO GETS THE FRAME, AND WHO GETS THE SCREEN.
   A browser on a desk gets the phone in its frame, because that is a picture
   of an app and the sidecar beside it explains what it is. A TOUCH DEVICE
   gets the whole screen, because on a touch device this is not a picture of
   an app, it is the app — and that includes every iPad. The old line was at
   740, which left an iPad showing a 404px phone floating in the middle of a
   1024px screen with three hundred pixels of nothing down each side.

   `pointer:coarse` is the test rather than a width, because it is the true
   question: is this being held, or is it being looked at. `display-mode:
   standalone` covers the same app launched from the home screen on anything.
*/
@media (max-width:740px), (pointer:coarse), (display-mode:standalone){
  #stage{padding:0;display:block;min-height:0}
  #sidecar{display:none!important}
  #phone{width:100%;max-width:none;height:100vh;height:100dvh;
    border-radius:0;box-shadow:none}
}""")

# ---- 2. the tablet layer: use the width, do not stretch into it ------------
rep(""".gr-sum b{font-size:40px;line-height:1}
""",
""".gr-sum b{font-size:40px;line-height:1}

/* ======================================================================
   THE TABLET LAYER
   Everything above this line was written for a 390 point column and never
   saw anything wider, because #phone was capped at 404. On a screen that is
   held rather than looked at, the app now fills it, so for the first time
   these grids get real width — and a two column grid stretched to 1024
   points is not a design, it is a phone screen pulled out of shape. The
   columns go up with the width; the prose does not.
   ====================================================================== */
@media (pointer:coarse) and (min-width:700px), (display-mode:standalone) and (min-width:700px){
  .grid{grid-template-columns:repeat(3,1fr);gap:12px;padding:0 22px}
  .brandgrid{grid-template-columns:repeat(4,1fr);gap:11px;padding:0 22px}
  .ctile{width:132px}
  .cattiles,.rail,.feedrow,.ev-rail,.brandstrip,.adstack,.xsell{padding-left:22px;padding-right:22px}
  .sec-h,.sec-lead,.pad,.dealgrid,.sfgrid,.ev-now,.ev-two,.storeb,.give,
  .sitefoot,.prizecard,.signup,.social,.note{padding-left:22px;padding-right:22px}
  .storeb,.ev-flyer,.ad,.adwrap,.give{margin-left:22px;margin-right:22px}
  /* a line of text stops being readable somewhere around 75 characters */
  .sec-lead,.ad-sub,.sfp span,.sf-note,.stnote,.ckfine,.why p,.whyb p,
  .ev-card p,.ev-d,.gr-note,.pz-copy p{max-width:64ch}
  .card .nm{font-size:15px}
  .sec-h h3{font-size:23px}
}
@media (pointer:coarse) and (min-width:980px), (display-mode:standalone) and (min-width:980px){
  .grid{grid-template-columns:repeat(4,1fr);gap:14px;padding:0 30px}
  .brandgrid{grid-template-columns:repeat(6,1fr);padding:0 30px}
  .dealgrid{grid-template-columns:1fr 1fr;gap:14px}
  .ctile{width:150px}
  .cattiles,.rail,.feedrow,.ev-rail,.brandstrip,.adstack,.xsell,
  .sec-h,.sec-lead,.pad,.sfgrid,.ev-now,.ev-two,.sitefoot,.prizecard,
  .signup,.social,.note{padding-left:30px;padding-right:30px}
  .storeb,.ev-flyer,.ad,.adwrap,.give{margin-left:30px;margin-right:30px}
  .sf-cols{grid-template-columns:repeat(4,1fr)}
  .sec-h h3{font-size:26px}
}
/* landscape on a tablet is short and wide: the hero must not eat the screen */
@media (pointer:coarse) and (min-width:900px) and (max-height:840px){
  .skyhero{height:300px}
  .promoc,.bpair{max-height:none}
}
""")

# ---- 3. the home screen ----------------------------------------------------
# the shop's mark on their own magenta, drawn at the two sizes iOS asks for
icon_svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180">'
    '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#2A0F33"/><stop offset="1" stop-color="#12060F"/>'
    '</linearGradient></defs>'
    '<rect width="180" height="180" fill="url(#g)"/>'
    '<g fill="none" stroke="#FF2FA8" stroke-width="5" stroke-linecap="round">'
    '<path d="M62 118c-9-7-14-17-14-29 0-23 19-41 42-41s42 18 42 41c0 12-5 22-14 29"/>'
    '</g>'
    '<text x="90" y="104" text-anchor="middle" font-family="Georgia,serif" '
    'font-style="italic" font-size="52" fill="#FFFFFF">SP</text>'
    '<text x="90" y="134" text-anchor="middle" font-family="Helvetica,Arial" '
    'font-size="13" letter-spacing="3" fill="#FF7BC8">SMOKE SHOP</text>'
    '</svg>'
)
icon_uri = 'data:image/svg+xml;base64,' + base64.b64encode(icon_svg.encode()).decode()

manifest = (
    '{"name":"Smokers Paradise","short_name":"Smokers Paradise",'
    '"start_url":".","display":"standalone","orientation":"any",'
    '"background_color":"#08060F","theme_color":"#08060F",'
    '"icons":[{"src":"' + icon_uri + '","sizes":"180x180","type":"image/svg+xml","purpose":"any"}]}'
)
man_uri = 'data:application/manifest+json;base64,' + base64.b64encode(manifest.encode()).decode()

rep("""<meta name="theme-color" content="#08080A">""",
    """<meta name="theme-color" content="#08060F">
<title>Smokers Paradise</title>
<!-- ADDED TO THE HOME SCREEN, THIS IS WHAT AN IPAD USES.
     Without these, tapping Add to Home Screen gives a grey screenshot for an
     icon, the file name for a label, and a window with the Safari address bar
     across the top — which is not what anybody means by "the app". -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Smokers Paradise">
<meta name="application-name" content="Smokers Paradise">
<link rel="apple-touch-icon" href="%s">
<link rel="icon" href="%s">
<link rel="manifest" href="%s">""" % (icon_uri, icon_uri, man_uri))

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
