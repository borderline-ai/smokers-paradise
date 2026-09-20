#!/usr/bin/env python3
# Stage 68 — the page margin, applied where it was actually missing.
#
# Measured rather than guessed: every element inside a section was asked for
# its bounding box at 390px and anything whose content started at x = 0 was
# listed. Twelve containers came back — the flyer row (which was at x = -15,
# so it bled past the screen), the "what we carry" chips, the community
# cards, the crew quote, the loose paragraphs under a section, the review
# strip, the brand grid, the deal grid and the attribute row.
#
# Also here: the announcement strip was running its longest line under both
# arrows, and "FOLLOW US" was an underlined all-caps link — the last piece of
# browser-default styling left on a control.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

CSS = r'''
/* ==========================================================================
   THE PAGE MARGIN, EVERYWHERE IT WAS MISSING
   One value, --pad. A rail keeps its bleed but starts at the margin, so the
   first card is never sliced by the screen edge; everything else simply sits
   inside it.
   ========================================================================== */
.commlist,.storystack,.attrrow,.dealgrid,.brandgrid,.grrow,
.emptycats,.ordwrap,.bagwrap,.bagtot,.baywhy,.sitefoot,.lvnote{
  padding-left:var(--pad);
  padding-right:var(--pad);
}
/* rails: bleed, but start and end on the margin */
.feedrow,.hlrow,.gr-strip,.rail-cards,.storyrow,.cattiles,.chips{
  padding-left:var(--pad);
  padding-right:var(--pad);
  margin-left:0;
  margin-right:0;
  scroll-padding-left:var(--pad);
}
/* a paragraph dropped straight into a section is not full bleed */
.sec > p,.sec > .ckfine,.sec > blockquote,.sec > .crewline,.sec > small{
  padding-left:var(--pad);
  padding-right:var(--pad);
}

/* ---- the announcement strip -------------------------------------------
   Its longest line ran under both arrows. The track keeps clear of them. */
#annb .track{padding:0 34px}
#annb .track b,#annb .track span{
  display:block;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}

/* ---- the last browser-default control ---------------------------------
   "FOLLOW US": an <a> with the user-agent underline, uppercase, and a border
   nothing else in the app uses. */
.sec-h .more,.more{
  font-family:var(--body-f);
  font-weight:600;
  font-size:13.5px;
  letter-spacing:normal;
  text-transform:none;
  text-decoration:none;
  color:#FFD3EC;
  padding:9px 15px;
  border-radius:99px;
  border:1px solid rgba(255,120,205,.30);
  background:rgba(255,120,205,.06);
  white-space:nowrap;
}

/* ---- section rhythm ----------------------------------------------------
   Sections were spaced by whatever their last child happened to leave
   behind. One value between them, one inside them. */
.sec{margin-bottom:30px}
.sec.tight{margin-bottom:22px}
.sec-h{margin-bottom:12px}
.sec-lead{margin:0 0 14px}

/* the community cards were a stack of full-bleed slabs with no gap */
.commlist{display:flex;flex-direction:column;gap:10px}
.comm{
  border-radius:var(--r-card);
  border:1px solid var(--edge-2);
  background:var(--card);
  padding:15px 16px;
}
.comm h4{
  font-family:var(--disp);font-weight:800;font-size:17px;
  letter-spacing:-.02em;text-transform:none;color:var(--ink);margin:5px 0 6px;
}
.comm p{font-size:13.5px;line-height:1.55;color:var(--body);margin:0}
.comm-when{
  font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--go-ink);
}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  margins appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
