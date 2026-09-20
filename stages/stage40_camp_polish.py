#!/usr/bin/env python3
# Stage 40 — the campaign stops inheriting the old banner's clothes.
#
# The campaign markup sits inside the carousel's .slide, and the old banner
# styled its children by tag: `.slide h2` carried an uppercase face and a
# coloured drop shadow, `.slide p` carried near-white ink meant for a dark
# ground. Both out-specify a plain `.camp-sub` class, so on a light field the
# headline ghosted and the sub-line went almost invisible.
#
# The old banner's tag rules are scoped to `.slide .txt`, the copy block only
# the old banner had, so they cannot reach a campaign at all; and every
# campaign rule is written as `.camp .camp-x`.
#
# Composition, from looking at the render:
#   - the product bleeds further past the bottom-right corner
#   - the second product moves into the white zone so it overlaps the first
#     instead of sitting on the tint, where its own white ground shows an edge
#   - the colour block lifts clear of the sub-line
#   - the legal line is one line, not three
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


# ---- 1. the old banner's tag rules cannot reach a campaign ----------------
for old in ['.slide h2{', '.slide p{', '.slide h2,', '.slide p,']:
    pass
rep(""".slide h2{font-family:var(--disp);font-weight:800;font-size:29px;line-height:1;letter-spacing:-.05em;""",
    """.slide .txt h2{font-family:var(--disp);font-weight:800;font-size:29px;line-height:1;letter-spacing:-.05em;""")
rep(""".slide p{font-size:12px;line-height:1.35;margin:7px 0 0;opacity:.85;max-width:22ch;""",
    """.slide .txt p{font-size:12px;line-height:1.35;margin:7px 0 0;opacity:.85;max-width:22ch;""")
rep("""@media (max-width:420px){ .slide{height:286px} .slide h2{font-size:24px} }""",
    """@media (max-width:420px){ .slide .txt h2{font-size:24px} }""")
rep(""".slide h2{font-family:var(--block);text-transform:uppercase;font-size:26px;letter-spacing:.012em;""",
    """.slide .txt h2{font-family:var(--block);text-transform:uppercase;font-size:26px;letter-spacing:.012em;""")
rep(""".slide p{opacity:.9;color:var(--ink2)}""",
    """.slide .txt p{opacity:.9;color:var(--ink2)}""")
rep("""  .slide h2{font-size:21px}
  .slide p{font-size:11.5px;-webkit-line-clamp:2}""",
    """  .slide .txt h2{font-size:21px}
  .slide .txt p{font-size:11.5px;-webkit-line-clamp:2}""")

# ---- 2. the campaign owns its own type, at a specificity nothing beats ----
CLOSE = r'''
/* ==========================================================================
   THE CAMPAIGN'S OWN TYPE
   Written as `.camp .camp-x` so a tag rule further up the file — `.slide h2`,
   `.slide p` — cannot reach in and repaint it. Both of those were written for
   a dark banner and were putting a coloured drop shadow under the headline
   and near-white ink on a light field.
   ========================================================================== */
.camp .camp-kick{font-family:var(--mono);font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;line-height:1;color:var(--acc);opacity:1;
  text-shadow:none;background:none;padding:0;border:0;box-shadow:none}
.camp .camp-head{font-family:var(--disp);font-weight:800;letter-spacing:-.045em;
  line-height:.93;margin:10px 0 0;color:var(--cink);text-transform:none;
  text-shadow:none;opacity:1;max-width:none}
.camp .camp-sub{font-size:12.5px;line-height:1.38;margin:9px 0 0;
  color:var(--cink);opacity:.72;max-width:27ch;text-shadow:none;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;
  overflow:hidden}
.camp .camp-fine{margin:10px 0 0;font-size:8.5px;line-height:1.35;
  color:var(--cink);opacity:.52;max-width:38ch;text-shadow:none}
.camp.dark .camp-head{color:#FFF}
.camp.dark .camp-sub{color:#F3E9F6;opacity:.85}
.camp.dark .camp-fine{color:#F3E9F6}
.camp.dark .camp-kick{color:var(--go-ink)}

/* ---- composition, after looking at it ---- */
/* the product bleeds past the corner; a photograph that stops inside the
   frame is a photograph that was dropped in */
.camp.lead .camp-lead{right:-9%;bottom:-9%;height:122%}
/* the second product moves onto the white, overlapping the first, so its own
   white ground has nothing to show an edge against */
.camp.lead .camp-back{right:34%;bottom:1%;height:78%}
.camp.lead .camp-ground{right:0;bottom:2%;width:58%;height:17px}
/* the colour lifts clear of the copy it sits behind */
.camp.lead .camp-block{width:200%;height:74%;left:-64%;top:-36%}

.camp.tall .camp-lead{right:-10%;bottom:-8%;height:104%}
.camp.tall .camp-back{right:44%;bottom:6%;height:66%}

@container (min-width:560px){
  .camp.lead .camp-lead{right:-6%;bottom:-7%;height:106%}
  .camp.lead .camp-back{right:38%;bottom:6%;height:72%}
  .camp.tall .camp-lead{left:50%;right:auto;transform:translateX(-44%);
    bottom:-9%;height:122%}
  .camp.tall .camp-back{left:4%;right:auto;bottom:2%;height:80%}
}
'''
i = s.rindex('</style>')
s = s[:i] + CLOSE + s[i:]
print('  campaign type layer appended')

# ---- 3. one line of legal, not three -------------------------------------
rep("""    disclaimer:'Sample offer taken from Smokers Paradise content. Pending store confirmation. 21+ only.',
    mark:true,
    shot:{ hero:()=>heroShot('Off-Stamp','X Cube 25K'),""",
"""    disclaimer:'Sample offer. Pending store confirmation. 21+ only.',
    mark:true,
    shot:{ hero:()=>heroShot('Off-Stamp','X Cube 25K'),""")
rep("""    disclaimer:'Demo selection. Flavours and pricing are confirmed with the store.',""",
    """    disclaimer:'Demo selection. Confirmed with the store.',""")
rep("""    disclaimer:'Demo selection. Selection and pricing are confirmed with the store.',""",
    """    disclaimer:'Demo selection. Confirmed with the store.',""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
