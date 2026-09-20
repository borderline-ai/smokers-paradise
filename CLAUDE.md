# Smokers Paradise — shop app

A single-file web app built for Smokers Paradise, a smoke shop at 922 N Grand Ave,
Nogales AZ. Built by BorderLine AI. It installs to a phone home screen as a PWA,
with no app store.

Live at **borderline-ai.github.io/smokers-paradise** (GitHub Pages, from the
`smokers-paradise` repo on the `borderline-ai` account, branch `main`, path `/`).

---

## THE BACKEND EXISTS NOW. READ THIS BEFORE BELIEVING ANY OLDER NOTE.

Until stage 171 there was no backend and the product did not work without one.
Everything was `localStorage` on whichever device it happened on, which was fine
for a walkthrough and fatal for a shop. That is fixed. `server/` is a Cloudflare
Worker and a D1 database; stage 171 wired the app to it.

The proof is the same two-device test that used to fail, now run in two real
browser contexts against the real service — `test/live_backend.py`:

```
customer joins on her phone      -> code written to the SHOP's members table
staff type that code on the iPad -> "Ana · 1 of 10 visits"
```

| Claimed | Reality now |
| --- | --- |
| The shop owns a customer list | `members`, `visits`, `redemptions` in D1. Exportable in full as CSV from the counter. |
| Rewards | The counter finds any member from any screen. Only a counter holding a staff session can add a visit. |
| Order ahead | `SP_API` is set by the Worker. A ticket placed on a phone is on the board within two seconds. |
| Staff edits a price | Goes to `catalog`, and every phone picks it up on its next open. Tested. |

**With no `SP_API` — the file opened off a disk — not one line of stage 171 runs
and the behaviour is byte for byte what stage 170 left.** The offline
walkthrough is a product, not a fallback, and all 65 suites still drive it.

### Where everything is

- `server/README.md` — the deploy runbook, the full API, and the limits, stated.
- `server/schema.sql` — the tables, with the reasoning in the comments.
- `server/src/index.js` — the router. Every route in one place.
- `server/scripts/serve.mjs` — the same handler under plain Node. No account, no
  install, no network: `cd server && npm run build && node scripts/serve.mjs`.
- `stages/s171_backend.py` — what changed in the app, and why each piece.

### Rules the backend must not break

These have not changed and each one now has a test that proves it.

1. **Only the counter may write a visit.** There is no route a customer device
   can reach that inserts into `visits`; `/api/staff/*` will not dispatch
   without a session issued against a PIN the *server* checked. A visit the
   customer's own device can create is a coupon anyone can print.
2. **A redemption is priced at the moment it happened.** `redemptions.cost` is
   `NOT NULL` and never recomputed. Stage 167 fixed this bug once, which had
   invented four free visits out of nothing; the schema is what stops it
   coming back.
3. **The shop owns the member data**, exportable in full, on demand. Sales
   promise, keep it true.
4. **Offline must degrade, not break.** The queue-and-retry shape is kept, and
   the CRM forward moved to the server so a join no longer depends on the
   customer reopening the app.

### What is still not done

- **Photographs do not live in the backend.** `catalog` holds prices and names;
  a photo added at the counter stays on the device that added it. Moving the
  261 base64 images out of the 12MB HTML and into R2 is the next real piece of
  work. The build script already refuses a file over 25 MiB, which is the
  Workers asset cap, so this is a deadline and not a preference.
- **The shelf has to be seeded once** from the counter before the server can
  price an order. Until then a ticket is stamped `priced: 'phone'` — reported
  rather than hidden, so a shop can tell which of its tickets it priced.
- **`Loyalty`** is still dormant and the service says so honestly:
  `/api/loyalty/status` answers `provider: 'none'`, which is what makes the app
  fall through to the shop's own programme. If a real provider ever answers,
  `Loyalty` wins.
- **No payments.** The order carries a payment reference field and nothing
  reads it. The register collects.

---

## How this codebase works, and why

**The app is one HTML file, `app/index.html`, about 12MB.** Everything is inline:
CSS, JS, and 261 product photographs as base64 WebP. It runs with the network
completely off, which is tested, not assumed. That was deliberate: a shop demo on
an iPad with no signal has to work.

**It is never edited by hand.** It is edited by numbered Python stage scripts in
`stages/`, run in order, each one making a small set of surgical string
replacements. Every script uses the same helper:

```python
def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:110])
    s = s.replace(a, b)
```

The `assert` is the point. If the anchor text is not present exactly the expected
number of times, the stage fails loudly instead of silently doing nothing or
doing it twice. **Keep this pattern.** When you change the app, write the next
numbered stage.

Stages run to 170. The file itself is the current output of all of them.

**Back up before every stage.** The convention is `app/index.beforeNNN.html`.
Those backups are not in this export (95 copies of a 12MB file is 840MB) but the
habit matters, a bad stage is otherwise unrecoverable.

**Each stage's header comment explains the decision, not the diff.** Read a few,
that is where the reasoning lives. Stage 168 on container queries and stage 162
on image sizing are the two most useful for understanding the design system.

---

## Testing

`test/` holds ~60 Playwright suites. They are not unit tests, they drive the real
app in a real browser with **every network request aborted**, and assert on what
a person would actually see.

The ones to run after any change:

```
python3 test/member.py       23 checks   the customer's half of rewards
python3 test/counter.py      23 checks   the counter's half
python3 test/askprompt.py    11 checks   the join prompt
python3 test/hittest.py                  every control reachable by a finger
python3 test/cliptext.py                 no text cut off
python3 test/cropcheck.py                no picture cut off by its box
python3 test/imgaudit5.py                654 images, network dead, none broken
python3 test/verify84.py     8 checks    campaign slides resolve
python3 test/tablet/journey_ipad.py      29 checks, the iPad walkthrough
```

And, since stage 171, the two that cover the backend:

```
cd server && npm test                    40 checks, the service, offline
python3 test/live_backend.py             23 checks, two real browsers, real service
```

`npm test` needs nothing installed — Node 24 ships `node:sqlite` and D1 is
SQLite, so the real Worker handler runs against a file-free stand-in. Two
"devices" means two cookie jars, which is the exact shape of the bug the
backend exists to end.

`live_backend.py` starts the service and drives the actual 12MB app in two
browser contexts. It is the only test that proves the headline claim end to end.

The suites used to have the build's absolute path typed into them
(`/root/work/...`), which made all 65 unrunnable anywhere but the container they
were written in. They resolve it now — see `test/sppath.py`, and set `SP_BUILD`
to point at a build somewhere else.

A caution learned the hard way: **two green suites can both be right and still
miss the bug.** The image audit said zero broken images on the same build where
the button walk found seven thousand errors. Ask what a number means, not just
whether it passes.

---

## Hard constraints, non-negotiable

1. **Never modify or deploy** `docs/base_from_holycow.html` or the Holy Cow
   reference. Its checksum is in `docs/holycow_reference.md5` and must not change.
   This app was converted from it; that source stays pristine.
2. **No AI-generated or drawn product imagery, ever.** Every product picture is a
   real photograph published by the brand or retailer. A gap is left as a gap.
   Three products are deliberately withheld because no real photo exists.
3. **Never invent** awards, claims, prices, inventory, reviews, stock counts or
   urgency. If a number is not verified, it does not ship. A `Verified` flag
   convention exists on `STORE` fields, honour it.
4. **The register is always the final word** on any discount. The app says a
   reward is ready, it never applies one.
5. **21+ gating** stays in front of everything.
6. Do not fetch manufacturer CDNs from this container, the proxy refuses them,
   and do not work around it with curl or python.

---

## Known gaps, beyond the backend

- **The catalogue is a starter list**, not the shop's real inventory. 259
  researched products with real brands and plausible prices. The owner's real
  list replaces it. Prices, stock, ratings and review counts are placeholder.
- **AI phone line** — the Staff view tab is sample call logs. Nothing is built.
- **Text blast** — no list imported, no A2P carrier registration passed.
- **Staff view Customers tab** — six hardcoded sample people.
- **The two-up banner pair** under the carousel is one column on tablet because
  `.bpair` declares `container-type` and then queries itself, which can never
  match. Fixing it means every banner inside starts measuring the pair rather
  than its own width. See the note at the end of `stages/s168_ipadbanners.py`.
- **Shop name, phone and address** are hardcoded in `STORE`, not editable in
  settings.

---

## The shop, as verified

Read off their own Google listing and Instagram on 7 Sep 2026. Anything not
listed here is not verified.

- Smokers Paradise, 922 N Grand Ave Ste B, Nogales AZ 85621
- (520) 338-2119
- Mon to Sat 8 AM to 9 PM, Sunday 10 AM to 7 PM
- 4.9 stars, 210 Google reviews
- Best of Santa Cruz County 2026, Best Smoke Shop
- @smokers_paradise_nogales
- Tagline, their own words: "Everything for your smoke necessities, at the best prices."
- Their logo, storefront photograph, award plaque and two of their flyers are
  real assets pulled from their own public posts, not redrawn.
- No website. Their Google listing's order button appears to point at a
  third-party ordering provider, worth confirming.

Name spelling: their sign and logo read **Smokers Paradise**, no apostrophe.
Google and the award certificate read *Smoker's Paradise*. The app uses the
version on their sign.

---

## Layout

```
app/index.html        the whole app, the build output
stages/sNNN_*.py      the numbered edits that produced it, in order
server/               the shop's backend: Cloudflare Worker + D1, and its own tests
test/*.py             Playwright suites, network-dead
test/tablet/*.py      the same, at iPad sizes
test/live_backend.py  the one suite that is NOT network-dead: it drives the
                      local service, and blocks everything that is not it
data/                 Spanish strings, hero device map, language data
docs/                 the Holy Cow source this was converted from, and its checksum
```

## Working on it

```bash
cp app/index.html app/index.before172.html      # always
python3 stages/s172_whatever.py
python3 test/member.py && python3 test/counter.py
```

Then open `app/index.html` in a browser. There is still no build step for the
app itself.

To see it as a shop rather than as a file — with a real counter, a real member
list and a real order board — run the service locally. It needs no account, no
install and no network:

```bash
cd server && npm run build && node scripts/serve.mjs
#   the shop     http://127.0.0.1:8787/
#   the counter  http://127.0.0.1:8787/counter   PIN 7413
```
