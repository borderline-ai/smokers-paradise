#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 176 — the service worker registration was wrong for any address that
# is not the root of a domain.
#
# Stage 172 registered it like this:
#
#     navigator.serviceWorker.register('/sw.js', {scope: '/'})
#
# Two faults, both invisible on the Worker and both fatal on GitHub Pages,
# which is where the link people have actually been given points.
#
# THE PATH IS ABSOLUTE. On the shop's own service the app is served at / and
# '/sw.js' is right. On Pages the app lives at /smokers-paradise/, so '/sw.js'
# asks borderline-ai.github.io for a file that is not there and never will be.
# A scope of '/' is refused outright for a script served from a subdirectory.
#
# THE FAILURE IS NOT CAUGHT. register() returns a promise. A try/catch around
# it catches nothing, because nothing throws synchronously — the rejection
# arrives later and lands as an unhandled rejection on every single page load.
# The suites that check "no page errors" drive file://, where this code does
# not run at all, so they would never have seen it.
#
# Relative, with the scope left to default to the directory the script is in.
# That is correct at the root and correct in a subdirectory, and the catch
# means a host that has no service worker at all just quietly has none.
#
# AND IT ONLY REGISTERS WHERE THERE IS A SHOP. The worker exists to keep the
# shop working through an internet outage. A copy of this file served from
# somewhere with no API behind it is a walkthrough, and caching a walkthrough
# buys nothing — while a failed registration logs a fetch error on every load,
# which is noise in the one place somebody looks when something is wrong.
#
# Checked on window.SP_API rather than the SP_API const, which is declared
# further down the file. Inside a load handler either would work, but reading
# the window property has no temporal-dead-zone question to think about.
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'app', 'index.html')
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:66].replace('\n', ' '))


rep("""  window.addEventListener('load', function(){
    try{ navigator.serviceWorker.register('/sw.js', {scope: '/'}) }catch(e){}
  });""",
"""  window.addEventListener('load', function(){
    /* Relative, and the scope left to default to whatever directory this
       page is in. Absolute '/sw.js' is right only when the app is served
       from the root of a domain; on a project page like
       borderline-ai.github.io/smokers-paradise/ it asks the domain root for
       a file that is not there, and a scope of '/' is refused outright.

       The catch matters as much as the path. register() returns a promise,
       so a try/catch around it catches nothing and the rejection lands as an
       unhandled error on every page load. A host with no service worker
       should simply have no service worker. */
    /* No API base means no shop: this is the standalone walkthrough, and
       there is nothing to keep running through an outage. */
    if(!window.SP_API) return;
    try{
      navigator.serviceWorker.register('sw.js').catch(function(){});
    }catch(e){}
  });""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
