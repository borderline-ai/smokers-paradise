#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does Spanish make the app feel slow?

The language layer walks the text nodes after every render. That is cheap on a
laptop and the question is whether it is cheap on the phone that gets handed
across a counter. Each screen is painted five times in each language and the
median is taken, so one unlucky frame does not decide it.
"""
import asyncio
import json
from playwright.async_api import async_playwright

B = '/root/work/smokers-paradise-demo/build/index.html'


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page(viewport={'width': 390, 'height': 844})
        await pg.route('**/*', lambda r: r.abort()
                       if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + B)
        await pg.wait_for_timeout(1700)
        await pg.evaluate("document.querySelector('#gateYes').click()")
        await pg.wait_for_timeout(1800)
        await pg.evaluate("hideInter()")

        out = {}
        for lang in ['en', 'es']:
            out[lang] = await pg.evaluate("""async (lang) => {
              setLang(lang); await new Promise(r=>setTimeout(r,1400));
              const t = {};
              const screens = [['home', ()=>go('home')], ['shelf', ()=>go('cat','disp')],
                               ['all', ()=>go('all')], ['deals', ()=>go('deals')],
                               ['store', ()=>go('store')]];
              for(const [k, fn] of screens){
                const runs = [];
                for(let i=0;i<5;i++){
                  go('home'); await new Promise(r=>setTimeout(r,260));
                  const t0 = performance.now();
                  fn();
                  await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
                  runs.push(performance.now()-t0);
                }
                runs.sort((a,b)=>a-b);
                t[k] = Math.round(runs[2]);
              }
              return t }""", lang)
            print('%s  %s' % (lang, json.dumps(out[lang])))

        worst = max((out['es'][k] - out['en'][k]) for k in out['en'])
        print('worst extra cost of Spanish on a screen paint: %d ms' % worst)

        r = await pg.evaluate("""async () => {
          const runs = [];
          for(let i=0;i<4;i++){
            go('home'); await new Promise(r=>setTimeout(r,420));
            const t0 = performance.now();
            setLang(LANG==='es' ? 'en' : 'es');
            await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
            runs.push(performance.now()-t0);
            await new Promise(r=>setTimeout(r,420));
          }
          runs.sort((a,b)=>a-b);
          return {medianMs: Math.round(runs[1]), runs: runs.map(Math.round)} }""")
        print('pressing the language button ->', json.dumps(r))
        await br.close()


asyncio.run(main())
