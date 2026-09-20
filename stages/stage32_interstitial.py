#!/usr/bin/env python3
# Stage 32 — the offer card that opens the app uses the same stage as the app.
#
# The first thing a customer sees was still floating a packshot on its own white
# ground, full bleed, square corners, over a coloured glow. Every other surface
# in the app puts a photograph on one neutral panel with one radius and one
# hairline. This is the surface that sets the expectation, so it goes first.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:120])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


rep("""      <div class="art">
        <div style="position:absolute;inset:0;background:radial-gradient(circle at 62% 34%,${d.theme.accent}4D 0%,${d.theme.accent}00 68%)"></div>
        ${im?`<img src="${im}" alt="${esc(d.title)}" referrerpolicy="no-referrer" onerror="this.style.display='none'">`""",
"""      <div class="art">
        ${im?`<span class="stage-panel">
                <img src="${im}" alt="${esc(d.title)}" referrerpolicy="no-referrer"
                  onerror="this.closest('.stage-panel').style.display='none'">
              </span>`""")

rep("""#inter .art{height:132px;position:relative;display:grid;place-items:center;overflow:hidden}
#inter .art img{height:118px;width:auto;max-width:74%;object-fit:contain;filter:drop-shadow(0 12px 20px rgba(0,0,0,.42))}""",
"""#inter .art{height:150px;position:relative;display:grid;place-items:center;
  overflow:hidden;padding:14px}
/* the same panel the shelf, the rails, the banners and the product page use */
#inter .art .stage-panel{width:132px;height:122px}
#inter .art img{width:100%;height:100%;object-fit:contain;padding:9%;filter:none}""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
