#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage 80 — English and Spanish, in the header.
#
# The store page already says "Se habla español. Te atendemos en los dos
# idiomas, en el mostrador y aquí en la app." The app was not keeping that
# promise: three lines of the announcement ticker and one line of the front
# door were in Spanish and everything else was in English, which reads less
# like bilingual and more like a translation that stopped.
#
# The bag icon in the header is where the switch goes. It was a third route to
# a screen the bottom bar already owns -- Bag is a tab, always visible, with the
# count on it -- so the header was spending one of its three slots on a
# duplicate. Same slot, same 44px, same row of three.
#
# HOW IT TRANSLATES. Not by rewriting two hundred template literals. After
# every render, a walk over the text nodes swaps the ones this file names, and
# the original is kept on the node so switching back is exact rather than a
# second translation. That means the dictionary is the only thing that can
# change: a product name, a brand, a flavour or a price cannot be touched by
# accident, because none of them are in it. Nobody translates "Geek Bar
# Pulse X", and a shop whose own shelf came out in machine Spanish would look
# worse than one that never offered the switch.
#
# The Spanish is the Spanish spoken at this counter: tú rather than usted,
# "recoger" rather than "recogida", "charolas" rather than "bandejas".
import io
import json

P = '/root/work/smokers-paradise-demo/build/index.html'
LANG = '/root/work/smokers-paradise-demo/data_lang.json'

s = io.open(P, encoding='utf-8').read()
n0 = len(s)
d = json.load(open(LANG, encoding='utf-8'))


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))


# ---- 1. the header slot ----------------------------------------------------
rep("""          <button class="hdr-ic" data-go="orders" aria-label="Your bag">
            <svg viewBox="0 0 24 24"><path d="M6 7h12l1.1 13H4.9z"/><path d="M9 9V6.2a3 3 0 016 0V9"/></svg>
            <span class="hdr-badge" id="hdrBag" hidden>0</span></button>""",
"""          <button class="hdr-ic hdr-lang" data-lang="1" id="langBtn"
            aria-label="Cambiar a espa&ntilde;ol"><b>ES</b></button>""")

rep(".burger{flex-direction:column;gap:4px}",
    "/* The language switch stands in the slot the bag used to hold, at the same\n"
    "   44px as the magnifier and the menu beside it. It shows the language you\n"
    "   would be switching TO, which is the only unambiguous label for a switch\n"
    "   with two states: a button marked EN in an English app tells you nothing\n"
    "   about what pressing it does. */\n"
    ".hdr-lang b{font-family:var(--mono);font-size:12.5px;font-weight:700;letter-spacing:.06em;\n"
    "  line-height:1;color:var(--ink)}\n"
    ".hdr-lang.on b{color:var(--brand)}\n"
    ".burger{flex-direction:column;gap:4px}")

# ---- 2. the dictionary and the walk ----------------------------------------
BLOCK = (
    "\n/* ==========================================================================\n"
    "   ENGLISH AND SPANISH\n"
    "   The shop serves in both at the counter and says so on its own store page.\n"
    "   Everything below is the shop's own voice and the app's own furniture.\n"
    "   Brands, product names, flavours and prices are deliberately absent: they\n"
    "   are the same word in both languages, and a catalogue run through a\n"
    "   translator is how an app stops sounding like the shop that owns it.\n"
    "   ========================================================================== */\n"
    "const T_ES = " + json.dumps(d['es'], ensure_ascii=False, separators=(',', ':')) + ";\n"
    "const T_EN = " + json.dumps(d['en'], ensure_ascii=False, separators=(',', ':')) + ";\n"
    "let LANG = 'en';\n"
    "try{ LANG = localStorage.getItem('sp_lang') || 'en' }catch(e){}\n"
    "\n"
    "/* Swap the text nodes this dictionary names, and remember what each one\n"
    "   said. Switching back reads that memory rather than translating a second\n"
    "   time, so a round trip is exact and a node can never drift. */\n"
    "function applyLang(root){\n"
    "  const scope = root || document.body;\n"
    "  let walker;\n"
    "  try{ walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT) }catch(e){ return }\n"
    "  const jobs = [];\n"
    "  let n;\n"
    "  while((n = walker.nextNode())){\n"
    "    const p = n.parentElement;\n"
    "    if(!p || p.tagName === 'SCRIPT' || p.tagName === 'STYLE') continue;\n"
    "    const raw = n.nodeValue;\n"
    "    const key = raw.replace(/\\s+/g,' ').trim();\n"
    "    if(key.length < 2) continue;\n"
    "    jobs.push([n, raw, key]);\n"
    "  }\n"
    "  jobs.forEach(([node, raw, key]) => {\n"
    "    if(LANG === 'es'){\n"
    "      const hit = T_ES[key];\n"
    "      if(hit && !node.__en){ node.__en = raw; node.nodeValue = raw.replace(key, hit) }\n"
    "    } else {\n"
    "      if(node.__en){ node.nodeValue = node.__en; node.__en = null; return }\n"
    "      const hit = T_EN[key];\n"
    "      if(hit){ node.__es = raw; node.nodeValue = raw.replace(key, hit) }\n"
    "    }\n"
    "  });\n"
    "  /* A few things a customer reads are attributes rather than text. */\n"
    "  const q = document.getElementById('q');\n"
    "  if(q){ const ph = 'Search the whole shelf';\n"
    "    q.placeholder = (LANG === 'es' && T_ES[ph]) ? T_ES[ph] : ph; }\n"
    "  const b = document.getElementById('langBtn');\n"
    "  if(b){ b.innerHTML = '<b>' + (LANG === 'es' ? 'EN' : 'ES') + '</b>';\n"
    "    b.classList.toggle('on', LANG === 'es');\n"
    "    b.setAttribute('aria-label', LANG === 'es' ? 'Switch to English'\n"
    "                                              : 'Cambiar a espa\\u00f1ol'); }\n"
    "}\n"
    "function setLang(v){\n"
    "  LANG = (v === 'es') ? 'es' : 'en';\n"
    "  try{ localStorage.setItem('sp_lang', LANG) }catch(e){}\n"
    "  document.documentElement.lang = LANG;\n"
    "  /* Repaint first so the new screen exists, then translate it. */\n"
    "  if(typeof paint === 'function'){ try{ paint() }catch(e){} }\n"
    "  applyLang();\n"
    "}\n"
    "/* Every render writes fresh English into the page, so the walk has to run\n"
    "   after each one. One observer on the view container catches every screen\n"
    "   without a call being added to thirty render functions. */\n"
    "(function watchLang(){\n"
    "  const main = document.getElementById('main');\n"
    "  if(!main || typeof MutationObserver === 'undefined') return;\n"
    "  let queued = false;\n"
    "  const mo = new MutationObserver(() => {\n"
    "    if(queued) return; queued = true;\n"
    "    requestAnimationFrame(() => { queued = false; applyLang() });\n"
    "  });\n"
    "  mo.observe(main, {childList:true, subtree:true});\n"
    "  mo.observe(document.body, {childList:true});\n"
    "})();\n"
)

i = s.index('function interKey()')
s = s[:i] + BLOCK + s[i:]
print('  ok: %d Spanish strings, %d English strings embedded'
      % (len(d['es']), len(d['en'])))

# ---- 3. the button ---------------------------------------------------------
rep("""  const pl=t.closest('[data-pill]'); if(pl){ pillGo(pl.dataset.pill); return }""",
"""  const lg=t.closest('[data-lang]'); if(lg){ setLang(LANG === 'es' ? 'en' : 'es'); return }
  const pl=t.closest('[data-pill]'); if(pl){ pillGo(pl.dataset.pill); return }""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
