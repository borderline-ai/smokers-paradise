#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 170 — the retry queue never retried.
#
# Found by walking the owner's own path rather than by reading the code.
#
# A join is queued to localStorage and posted to SHOP_REWARDS.endpoint, and if
# the post fails it stays in the queue to be sent later. That was the design and
# the comment in stage 165 says so in as many words: "failures queue and retry on
# the next open rather than being lost."
#
# They do not retry on the next open. Member.flush() is called from exactly one
# place in the whole file, and that place is inside join() itself:
#
#     grep '\.flush()'   ->   one hit, line 18813, inside join
#
# So the only moment the queue is ever drained is the moment a join is made. A
# join made with no signal, or made before the shop's endpoint is set, sits in
# that phone's localStorage forever and nobody is ever told.
#
# That is exactly the situation this demo is in. The endpoint is empty, so every
# join anyone makes on the live link is queued and silently stranded. The moment
# the shop's webhook is pasted in, those people should arrive as contacts. They
# would not have.
#
# The fix is one call in the right place: drain the queue when the app opens,
# after the config has loaded, so a join made offline or made before the shop was
# connected reaches the shop the next time that phone opens the app.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:68].replace('\n', ' '))


rep("""function saveRewardsCfg(){""",
"""/* DRAIN THE QUEUE ON OPEN. Without this the queue is not a retry queue, it is
   a hole: flush() was only ever called from inside join(), so a join made with
   no signal, or made before the shop's endpoint was set, was stranded on that
   phone forever. Deferred so it never delays the first paint, and guarded so a
   dead endpoint can never break start up. */
setTimeout(function(){
  try{ if(SHOP_REWARDS.endpoint) Member.flush() }catch(e){}
}, 2500);

function saveRewardsCfg(){""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d chars' % (n0, len(s)))
