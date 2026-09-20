#!/usr/bin/env python3
# Stage 79 — the search box waits until it is asked for.
#
# It sat open under the header on every screen of the app, seventy pixels of
# empty field above the shelf, the hero, the bag and the checkout. A shop app
# is browsed far more than it is searched, and the newer builds tuck it behind
# the magnifier in the header, which is also what every shopper already expects
# that icon to do. Here the icon focused a field that was already on screen, so
# it appeared to do nothing.
#
# Now the row is closed until the magnifier is pressed, and it closes again on
# Escape, on an empty blur, and whenever the customer navigates away. The
# shelf pills open it with their term already in it, so what was searched is
# visible rather than magic.
import io

P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


# ---- 1. closed by default --------------------------------------------------
rep(".srow{padding:10px 15px 11px;background:var(--card)}",
    ".srow{padding:10px 15px 11px;background:var(--card)}\n"
    "/* Closed until the magnifier is pressed. Animated on height rather than\n"
    "   display, so the header does not jump and the field can be focused the\n"
    "   moment it starts opening. */\n"
    ".srow{display:grid;grid-template-rows:0fr;padding-top:0;padding-bottom:0;\n"
    "  opacity:0;transition:grid-template-rows .22s var(--spring),opacity .16s,\n"
    "    padding .22s var(--spring)}\n"
    ".srow>*{overflow:hidden;min-height:0}\n"
    ".srow.on{grid-template-rows:1fr;opacity:1;padding-top:10px;padding-bottom:11px}\n"
    "@media (prefers-reduced-motion:reduce){.srow{transition:none}}")

# ---- 2. the magnifier opens it ---------------------------------------------
rep("""  const fs = t.closest('[data-focussearch]');
  if(fs){
    closeMenu();
    const q = $('#q');
    if(q){ q.focus(); q.select(); q.scrollIntoView({block:'nearest'}); }
    return;
  }""",
"""  const fs = t.closest('[data-focussearch]');
  if(fs){ closeMenu(); toggleSearchRow(); return }""")

# ---- 3. the machinery ------------------------------------------------------
rep("""function interKey(){ return 'sp_demo_inter_""",
"""/* The search row: open it, close it, or open it with something in it. One
   place, so the magnifier, the shelf pills and every navigation agree about
   whether it is showing. */
function searchRowOpen(){ const r=$('.srow'); return !!(r && r.classList.contains('on')) }
function openSearchRow(focus){
  const r=$('.srow'); if(!r) return;
  r.classList.add('on');
  const q=$('#q');
  if(q && focus!==false) setTimeout(()=>{ q.focus(); q.select() }, 60);
}
function closeSearchRow(){
  const r=$('.srow'); if(!r) return;
  r.classList.remove('on');
  const q=$('#q'); if(q) q.blur();
}
function toggleSearchRow(){ searchRowOpen() ? closeSearchRow() : openSearchRow(true) }
/* A shelf pill searches with the word showing, so the customer can see what
   was asked for and edit it, rather than landing on results out of nowhere. */
function openSearchFor(term){
  openSearchRow(false);
  const q=$('#q'); if(!q) return;
  q.value = term;
  q.dispatchEvent(new Event('input', {bubbles:true}));
  setTimeout(()=>{ q.focus(); q.setSelectionRange(q.value.length, q.value.length) }, 60);
}
document.addEventListener('keydown', e => {
  if(e.key === 'Escape' && searchRowOpen()){ closeSearchRow() }
});
function interKey(){ return 'sp_demo_inter_""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
