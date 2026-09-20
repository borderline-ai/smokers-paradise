#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 155 — a sentence that does not parse, and a crash one argument away.
#
# 1. "3 of the 69 on this shelf that fit everything you said."
#    Read it out loud. It is a noun phrase with no verb: the "that" turns the
#    whole line into a fragment. It wants to be a sentence.
#
#        3 of the 69 on this shelf fit everything you said.
#
# 2. dialogClosed() calls document.body.contains(back) on whatever was handed
#    to dialogOpened() as the opener. Every real caller passes the element that
#    was clicked, so this never fires in the app — and the moment anything
#    passes a string, an id or null, `contains` throws a TypeError, and because
#    it throws inside the close path the dialog stays open on screen with the
#    app behind it locked. A guard is one clause, and the difference between a
#    wrong argument and a dead app is worth one clause.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


rep("""            : `${r.matches.length} of the ${r.total} on this shelf that fit everything you said.`)""",
    """            : `${r.matches.length} of the ${r.total} on this shelf fit everything you said.`)""")

rep("""    if(back && document.body.contains(back) && typeof back.focus==='function')""",
"""    /* `back` is whatever was handed in as the opener. Every caller in this
       file passes the element that was clicked, and the one that does not
       would take the whole close path down with a TypeError and leave the
       dialog on screen over a locked page. */
    if(back && back.nodeType===1 && document.body.contains(back)
       && typeof back.focus==='function')""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
