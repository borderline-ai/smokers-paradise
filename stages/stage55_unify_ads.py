#!/usr/bin/env python3
# Stage 55 — the home rail and the opening offer become advertisements too.
#
# Two places still built their own card out of `d.theme`, which the ads no
# longer carry, so both threw and took their section down with them. Rather
# than hand them a theme back, they render the same advertisement the deals
# page does — one at rail size, one at dialog size. Three surfaces, one
# design, no third idea of what a promotion looks like.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:130])
    s = s.replace(a, b)
    print('  ok:', a[:56].replace('\n', ' '))


# ---- the home rail --------------------------------------------------------
i = s.index('function dealCardBig(d,i){')
j = s.index('/* ---------- the mark in the header ----------')
s = s[:i] + '''function dealCardBig(d,i){
  /* The rail shows the same advertisement, at rail width. It used to build a
     second kind of card out of a per-deal theme; there is one design now. */
  return `<div class="adwrap" data-dealgo="${d.id}">${adHTML(d, i)}</div>`;
}

''' + s[j:]
print('  rail routed through the ad')

# ---- the opening offer ----------------------------------------------------
rep("""  const im = typeof d.image==='function' ? d.image() : d.image;
  $('#interCard').innerHTML = `
    <div style="background:${d.theme.bg};color:${d.theme.ink}">
      <button class="x" data-interx="1" aria-label="Close offer"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      <div class="art">
        ${im?`<span class="stage-panel">
                <img src="${im}" alt="${esc(d.title)}" referrerpolicy="no-referrer"
                  onerror="this.closest('.stage-panel').style.display='none'">
              </span>`
            : d.art==='prize' ? prizeBundle(true)
            : d.art==='wheel' ? `<div class="ddraw" style="width:100%;height:100%">${wheelSVG()}</div>`
            :`<div style="font-family:var(--block);font-size:${(d.discountAmount||'').length>6?'34px':'60px'};line-height:1;
                 letter-spacing:.5px;text-align:center;padding:0 18px;color:${d.theme.accent};position:relative">${esc(d.discountAmount||'')}</div>`}
      </div>
      <div class="body">
        <div class="eye" style="color:${d.theme.accent}">${d.badge}</div>
        <h3>${d.title}</h3>
        <p>${d.subtitle}</p>
        <button class="go" data-intergo="${d.id}">${d.ctaLabel}</button>
        <button class="skip" data-interx="1">Keep browsing</button>
        ${d.disclaimer?`<div class="fine">${d.disclaimer}</div>`:''}
      </div>
    </div>`;""",
"""  /* the same advertisement, in a dialog */
  $('#interCard').innerHTML = `
    <div class="interad">
      <button class="x" data-interx="1" aria-label="Close offer"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      ${adHTML(d, 0)}
      <button class="skip" data-interx="1">Keep browsing</button>
    </div>`;""")

CSS = r'''
/* the advertisement at rail width, and in the opening dialog */
.adwrap{flex:0 0 84%;max-width:340px;scroll-snap-align:start;cursor:pointer}
.adwrap .ad{min-height:266px}
.adwrap .ad .ad-title{font-size:22px}
.adwrap .ad-offer b{font-size:36px}
.adwrap .ad .ad-sub{-webkit-line-clamp:2;display:-webkit-box;
  -webkit-box-orient:vertical;overflow:hidden}
.adwrap .ad-save{display:none}
.adwrap .ad-copy{padding:18px 16px}

#interCard{background:none;box-shadow:none}
.interad{position:relative}
.interad .ad{min-height:300px;border-radius:var(--r-card)}
.interad .x{position:absolute;right:10px;top:10px;z-index:9}
.interad .skip{display:block;width:100%;margin:10px 0 0;padding:12px;
  background:transparent;border:0;color:var(--ink2);font-size:12.5px;
  font-family:var(--body-f);cursor:pointer}
'''
i = s.rindex('</style>')
s = s[:i] + CSS + s[i:]
print('  rail and dialog styles appended')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
