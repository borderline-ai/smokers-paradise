# Smokers Paradise

Shop app for Smokers Paradise, Nogales AZ. Built by BorderLine AI.

Open `CLAUDE.md` first. It explains how the codebase works and the constraints.

The app is one HTML file with no build step, edited only by the numbered stage
scripts in `stages/`. Since stage 172 it is 1.9 MB, with the 309 product
photographs beside it in `app/img/` rather than inlined as base64. Open
`app/index.html` in a browser and it still runs with the network completely off
— that is tested, not assumed.

Since stage 171 it also has a backend. `server/` is a Cloudflare Worker and a
D1 database holding the member list, visits, redemptions, orders, the catalogue
edits and the rewards rule. Before it, every member record lived only on the
phone that created it and the counter could never find a real customer.

## See it as a shop

No account, no install, no network:

```bash
cd server && npm run build && node scripts/serve.mjs
#   the shop     http://127.0.0.1:8787/
#   the counter  http://127.0.0.1:8787/counter   PIN 7413
```

Join on one browser, look the code up on the counter in another, add a visit,
watch the first card move. `server/README.md` is the deploy runbook.

## Change the app

```bash
cp app/index.html app/index.before172.html      # always
python3 stages/s172_yourchange.py
python3 test/member.py && python3 test/counter.py
```

## Tests

```bash
python3 test/member.py            # the customer's half of rewards
python3 test/counter.py           # the counter's half
python3 test/tablet/journey_ipad.py
cd server && npm test             # 58 checks, the service, offline
python3 test/live_backend.py      # 29 checks, two real browsers, real service
```

## Load the shop's real inventory

```bash
cd server
npm run import -- inventory.csv --photos ~/photos --url https://theshop --retire
```

Playwright is needed for the Python suites:
`python3 -m pip install playwright && python3 -m playwright install chromium`.
