#!/usr/bin/env python3
# Stage 30 — the product page adopts the same stage as everything else.
#
# The one surface stage 27 missed. The product page still lit its plate with a
# white-hot radial and then laid a second white sheen over the top of it, which
# is exactly the halo the rest of the app just had removed. It is now the same
# neutral panel used by every card, tile, rail and banner: one colour, one
# radius, one hairline, no glow, no sheen.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1, must=True):
    global s
    n = s.count(a)
    if n == 0 and not must:
        print('  skip:', a[:56].replace('\n', ' ')); return
    assert n == count, 'count %d for: %s' % (n, a[:120])
    s = s.replace(a, b)
    print('  ok:', a[:58].replace('\n', ' '))


rep(""".pdp-art{position:relative;width:100%;max-height:none;margin-top:8px;border-radius:var(--r5);overflow:hidden;
  background:radial-gradient(70% 58% at 50% 30%,#FFFFFF 0%,var(--stage) 55%,#DED7F2 100%);
  box-shadow:var(--lip),0 18px 40px rgba(0,0,0,.5),0 0 0 1px var(--edge);
  aspect-ratio:1/1;display:flex;align-items:center;justify-content:center}
.pdp-art::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 60% at 50% -10%,rgba(255,255,255,.9),transparent 45%)}""",
""".pdp-art{position:relative;width:100%;max-height:none;margin-top:8px;
  border-radius:var(--r-card);overflow:hidden;
  background:var(--stage);
  box-shadow:var(--sh-1), inset 0 0 0 1px var(--stage-line);
  aspect-ratio:1/1;display:flex;align-items:center;justify-content:center}""")

rep(""".pdp-art img,.pdp-art svg{position:relative;z-index:1}""",
""".pdp-art img,.pdp-art svg{position:relative;z-index:1;
  width:100%;height:100%;object-fit:contain;padding:8%}""")

rep(""".pdp-art .flag{position:absolute;left:11px;top:11px;z-index:3;font-family:var(--mono);font-size:9.5px;
  letter-spacing:.12em;text-transform:uppercase;padding:5px 8px;border-radius:4px;""",
""".pdp-art .flag{position:absolute;left:11px;top:11px;z-index:3;font-family:var(--mono);font-size:9.5px;
  letter-spacing:.12em;text-transform:uppercase;padding:5px 8px;border-radius:var(--r-chip);""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
