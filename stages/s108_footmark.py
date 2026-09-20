#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 108 — the sign at the bottom of the page.
#
# Marco: "as you scroll you are found with the logos actually putting that
# smoke in that background... I'm not telling you to fill it up with logos or a
# bunch of shit."
#
# Both halves of that sentence decide this one. The smoke field from stage 107
# is behind everything; what it needed was a source in the page that a reader
# arrives at by scrolling, rather than one they left behind at the door.
#
# There is exactly one place in this app where a shop's sign belongs and is not
# already there: the foot of the page. It was the shop's name set in a script
# face — a typeface standing in for a logo that exists. So the logo goes there,
# at the size a sign is read at, and because every mark in this app smokes, the
# bottom of a long shelf now has smoke rising out of it into the field behind
# the whole screen. That is the picture he described, and it costs one mark,
# not thirty.
#
# The name stays in the markup underneath it, visually hidden, because the
# artwork is a picture and the foot of a page is where a search engine and a
# screen reader look for who this is.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""  <div class="sitefoot">
    <div class="sf-name">Smokers Paradise</div>""",
"""  <div class="sitefoot">
    ${/* The shop's own sign, not a script typeface standing in for one. It is
         the last thing on every long page, so a reader who scrolls the whole
         shelf arrives at it — and because every mark in this app smokes, they
         arrive at the thing feeding the smoke behind the screen. */''}
    <div class="sf-mark">${(typeof markHTML==='function')
      ? markHTML('idle','footmark smokes') : ''}
      <span class="sf-name-a11y">Smokers Paradise</span></div>""")

rep(""".sf-name{font-family:var(--disp);font-weight:800;font-size:19px;color:var(--ink);""",
"""/* the sign at the foot of the page */
.sf-mark{width:min(66%,208px);margin:0 0 14px;line-height:0;position:relative}
.sf-mark .hcm{width:100%}
.sf-name-a11y{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);
  clip-path:inset(50%);white-space:nowrap}
.sf-name{font-family:var(--disp);font-weight:800;font-size:19px;color:var(--ink);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
