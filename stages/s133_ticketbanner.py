#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 133 — the raffle banner, built on his photograph.
#
# Marco: "I also added a picture of tickets, I want you to use that as the
# backround FOR A STATIC BANNER for the raffle ticket in the deals section. I
# thought that banner looked a bit lame. DO NOT drop the picture on the side,
# make a badass design using it in the backround."
#
# What was there: a flat panel with a radial gradient and nothing on it. The
# note in this file says why — "No product photograph on this card. The entry
# mechanic is the whole message, so it is set as one" — which was the right
# call when there was nothing honest to put behind it, and stops being the
# right call the moment the client hands you a photograph.
#
# THE PHOTOGRAPH IS THE CARD, not an inset and not a thumbnail beside the text:
# full bleed, edge to edge, under everything. Three things had to happen to it
# first, because a raw photograph under white type is unreadable:
#
#   IT LEANS INTO THE SHOP'S COLOUR. The source is red-and-blue cloakroom
#   tickets. Pulled two thirds toward luminance and pushed back through the
#   shop's magenta, it stops being a stock photograph and starts being this
#   shop's, without anything being painted onto it.
#
#   IT SITS DARKER AND HARDER. Down about 10%, contrast up about 20%, so the
#   ticket edges stay crisp at a twentieth of a screen while the whole plate
#   drops well below the type that goes on top of it.
#
#   AND IT IS SCRIMMED ON THE DIAGONAL, heavy where the words are and clearing
#   toward the top right so the tickets are plainly readable as tickets. A flat
#   scrim would have killed the photograph to save the text; the diagonal keeps
#   both.
#
# THE STRUCTURE IS A TICKET, because the card is one: perforated edges top and
# bottom, which this card already had, plus a vertical perforation separating
# the stub. The number lives on the stub, the way it does on a cloakroom
# ticket. Nothing here is a drawing of a ticket — it is a card built the way a
# ticket is built, over a photograph of the real thing.
import io
import base64

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


# ---- 1. the photograph, embedded -------------------------------------------
blob = open('/tmp/sp5/tickets_bg.webp', 'rb').read()
uri = 'data:image/webp;base64,' + base64.b64encode(blob).decode()
rep("""const IG_SPRING   = "data:image/webp;base64,""",
"""/* The raffle tickets Marco supplied, worked for this use: two thirds toward
   luminance and back through the shop's magenta so it is this shop's picture
   rather than a stock one, then darkened and hardened so ticket edges survive
   at banner size while the plate drops under the type. */
const IG_TICKETS  = "%s";
const IG_SPRING   = "data:image/webp;base64,""" % uri)
print('  ok: tickets photograph embedded, %d KB' % (len(uri) // 1024))

# ---- 2. the art ------------------------------------------------------------
rep("""  if(d.art_kind === 'prize')""",
"""  if(d.art_kind === 'tickets')
    /* full bleed, under everything, with the scrim carried by CSS so the
       weight of it can be tuned against the type without re-encoding a
       photograph */
    return `<div class="ad-art tktart" aria-hidden="true">
      <span class="tkt-ph" style="background-image:url(${IG_TICKETS})"></span>
      <span class="tkt-scrim"></span>
      <span class="tkt-perf"></span>
    </div>`;
  if(d.art_kind === 'prize')""")

rep("""    dealType:'note', discountAmount:'$10+', qualifyingCategory:'',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'', disclaimer:'In store only. One entry per visit. 21+ only.',
    art:[],""",
"""    dealType:'note', discountAmount:'$10+', qualifyingCategory:'',
    art_kind:'tickets',
    qualifyingBrandIds:[], ctaLabel:'Shop the shelf', ctaTarget:{view:'all'},
    badge:'', disclaimer:'In store only. One entry per visit. 21+ only.',
    art:[],""")

# ---- 3. the look -----------------------------------------------------------
rep(""".ad.l-ticket .ad-art,.ad.c-raffle .ad-art,.ad.c-raffle .prizeart,
.ad.c-raffle .pz-stage{display:none}""",
"""/* the old rule hid every art layer on this card, from when there was nothing
   to put on it; the ticket plate is the exception */
.ad.l-ticket .ad-art:not(.tktart),.ad.c-raffle .ad-art:not(.tktart),
.ad.c-raffle .prizeart,.ad.c-raffle .pz-stage{display:none}

/* ---- THE RAFFLE, ON HIS PHOTOGRAPH ----
   The picture is the card: full bleed, under everything, scrimmed on the
   diagonal so it is heavy where the words are and clears toward the top right
   where the tickets should read as tickets. */
.ad.c-raffle.l-ticket{position:relative;overflow:hidden;background:#0B0410}
.tktart{position:absolute;inset:0;z-index:0;display:block;pointer-events:none}
.tkt-ph{position:absolute;inset:0;display:block;
  background-size:cover;background-position:58% 42%;
  transform:scale(1.06);filter:saturate(.96)}
.tkt-scrim{position:absolute;inset:0;display:block;
  background:
    linear-gradient(104deg, rgba(8,3,11,.95) 0%, rgba(11,4,14,.90) 38%,
                            rgba(24,5,22,.62) 66%, rgba(40,7,34,.34) 100%),
    radial-gradient(120% 90% at 4% 100%, rgba(255,47,168,.20) 0%, transparent 62%)}
/* the stub, separated the way a cloakroom ticket is separated */
.tkt-perf{position:absolute;top:0;bottom:0;left:69%;width:12px;display:block;
  background-image:radial-gradient(circle at 6px 8px, rgba(0,0,0,.52) 4.5px, transparent 5px);
  background-size:12px 20px}
.ad.c-raffle.l-ticket .ad-copy{position:relative;z-index:2;max-width:70%}
.ad.c-raffle .ad-kick{color:#FFC9E8}
.ad.c-raffle .ad-title{text-shadow:0 2px 18px rgba(0,0,0,.6)}
.ad.c-raffle .ad-offer b{color:#FFFFFF;text-shadow:0 3px 20px rgba(0,0,0,.65)}
.ad.c-raffle .ad-sub{color:rgba(255,236,247,.86);max-width:24ch}
.ad.c-raffle .ad-fine{color:rgba(255,232,246,.52)}
/* the number sits on the stub, which is where a number sits on a ticket */
.ad.c-raffle.l-ticket .tkt-no{position:absolute;right:0;top:0;bottom:0;width:31%;
  z-index:2;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:2px;pointer-events:none}
.tkt-no b{font-family:var(--mono);font-size:11px;letter-spacing:2.2px;
  color:rgba(255,220,240,.9);writing-mode:vertical-rl;transform:rotate(180deg)}
.tkt-no i{font-family:var(--mono);font-style:normal;font-size:8.5px;letter-spacing:1.6px;
  color:rgba(255,220,240,.42);writing-mode:vertical-rl;transform:rotate(180deg)}
@media (max-width:344px){
  .ad.c-raffle.l-ticket .ad-copy{max-width:100%}
  .tkt-perf,.ad.c-raffle.l-ticket .tkt-no{display:none}
}""")

# the stub label, rendered with the card
rep("""  if(d.art_kind === 'tickets')""",
"""  if(d.art_kind === 'tickets')""")

rep("""    return `<div class="ad-art tktart" aria-hidden="true">
      <span class="tkt-ph" style="background-image:url(${IG_TICKETS})"></span>
      <span class="tkt-scrim"></span>
      <span class="tkt-perf"></span>
    </div>`;""",
"""    return `<div class="ad-art tktart" aria-hidden="true">
      <span class="tkt-ph" style="background-image:url(${IG_TICKETS})"></span>
      <span class="tkt-scrim"></span>
      <span class="tkt-perf"></span>
    </div>
    <span class="tkt-no" aria-hidden="true"><b>ONE ENTRY</b><i>PER VISIT</i></span>`;""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
