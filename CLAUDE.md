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

## THE PHOTOGRAPHS ARE FILES NOW (stages 172 and 173)

They were 77% of the document: 328 base64 blobs, measured at 8.9 MB against
2.3 MB of actual code. Stage 172 took them out to `app/img/`, named by the
hash of their own bytes. **11.56 MB -> 1.94 MB.**

The trick worth knowing before editing anything here is the missing slash.
Paths are written `img/<hash>.webp`, relative, never `/img/...`:

```
opened off a disk   file:///.../app/index.html  ->  file:///.../app/img/x.webp
served by the shop  <base href="/"> is injected ->  /img/x.webp
```

That one character is why all 65 file:// suites still pass with the network
dead — a file:// image is not a network request — and why `/counter`, which is
one path segment deep, does not ask for `/counter/img/...`. The `<base>` is
injected by the Worker, in `injectBoot`.

Offline was rebuilt rather than dropped. `server/assets/sw.js` caches the
document and each photograph the first time it is shown. It does **not**
pre-download all 309: a customer on cellular should not pay for the whole shelf
to look at one vape. What it buys is a shop that keeps taking orders through an
internet outage. What it does not buy is a cold first load with no signal ever
— for that, `app/index.html` off a disk still works.

Photographs are named by content, so they are served `immutable` for a year and
a replacement arrives under a new name rather than as a stale copy.

### The owner's real list

The 259 products in the app were always a starter catalogue. `npm run import`
replaces them:

```bash
cd server
npm run import -- inventory.csv --photos ~/photos --url https://theshop --retire
```

It reads the spreadsheet the way one actually turns up — "Item" or "Product" or
"Description" for a header, "$12.99" and "1,299.00" and "12.50 ea" for a price,
a blank row in the middle, the same product twice — and it reports every row it
would not import, with the line number, before it sends anything.

Two refusals in there are load-bearing and should not be softened:

- **A row with no price is skipped, never priced at zero.** The register is the
  final word, but the screen is what the customer read before they walked in.
- **A photograph the folder does not contain is blanked, never passed through.**
  A product with no picture has a gap the app already draws; a product pointing
  at a 404 does not. That is rule 2, and the first version of the script got it
  wrong — it wrote `img/nosuchfile` into a live listing.

`--retire` hides the starter products the file does not mention. Hides, not
deletes, so importing the wrong file at four in the afternoon is recoverable.

## EMAIL IS THE CHANNEL. SMS IS NOT, AND WILL NOT BE (stage 174)

**Do not reintroduce SMS without reading this.** It is a decision, not an
omission.

US application-to-person messaging is filtered by carriers on content, under
the heading SHAFT: Sex, Hate, Alcohol, Firearms, **Tobacco**. A smoke shop is
the T. Registration for a vape retailer is uncertain, and even an approved
campaign has promotional messages dropped when the body names a product —
silently, which is the worst failure available. Every deal, reward and birthday
note would be a fight over phrasing that the shop loses without being told.

Email has no such fight. The legal regime is CAN-SPAM rather than TCPA:
accurate sender, a physical address in the message, an unsubscribe that is
honoured. The shop's address is already in `STORE`.

The same restriction is why this app is a PWA. Both app stores prohibit apps
facilitating the sale of tobacco and vape products, so the home-screen install
is not a shortcut — it is the only distribution channel this business has.

And the same rule applies to picking a provider: **ask, do not omit.** A
smoke shop is a lawful business, and providers who serve regulated verticals
will approve it in writing. An account obtained by not mentioning the industry
is a channel that works until it doesn't, and for an agency a terminated
provider account takes every other client down with it.

### Four things the app used to claim and could not do

Stage 174 deleted all four. If any of them come back, they are lies:

| It said | What was true |
| --- | --- |
| "Mark ready, text them" | no text was sent |
| "Ready · customer notified" | nobody was notified |
| "we'll text you when the bag is ready" | no |
| **"You are on the list. One text when a real deal lands."** | **there was no list** |

The last one is the bad one, and it is worse than doing nothing. The front page
box took a phone number, wrote it to that browser's `localStorage`, and said
that sentence. A form that silently discards what it is given makes a customer
believe they have done something and stop looking for the real way in. It has a
`subscribers` table behind it now, and an unsubscribe that needs no account.

Two switches in Account were the same kind of decoration — they flipped a flag
nothing ever read. **Order alerts** now gates the toast the app genuinely
raises when the status poll sees a bag marked ready.

What IS true about an order, and is what the words say now: the customer's own
screen follows the counter within about five seconds while the app is open.

### The consent sentence travels with the consent

`MB_TERMS` is one constant, put on the form and sent with the join, and stored
in `members.contact_terms` and on the CSV export. "They opted in" is not an
answer to a complaint; what they opted in **to** is.

## THE COUNTER IS A SEPARATE APP NOW

`app/counter.html`, 36 KB, served at `/counter`. It replaced "the customer app
with `window.SP_STAFF` injected", which meant the register screen downloaded
1.9 MB of document and 309 photographs to show a lookup box and a ticket list —
fifty times a day, on whatever phone the person behind the till owns.

**It is written by hand, not by a stage script.** That convention exists because
`app/index.html` is 12 MB of generated output that must never be hand-edited.
`counter.html` is a source file. Edit it directly.

**It owns nothing.** No `localStorage` anywhere in it, and that is deliberate:
the customer app keeps a local cache because it has to work in a dead spot, but
a till that guesses is worse than a till that says it cannot reach the shop. If
the service is down it says so and refuses.

**It contains no sample screens.** The old Staff view carried an AI phone tab of
invented call logs, a text blast tab with nothing behind it, and six customers
who did not exist. None came across. Carrying a fake screen into the thing an
owner uses every day is how they stop believing the real ones. There is a test
asserting the tab list is exactly `Orders, Rewards, Menu, Customers, Settings`.

Three endpoints exist for it and nothing else: `GET /api/staff/catalog` (the
shelf including what is hidden, because hiding is what the owner came to undo),
`GET /api/staff/members/list`, and `POST /api/staff/media`.

### Photographs from the counter, at last

`POST /api/staff/media` takes raw bytes and answers `img/<hash>.webp` — the same
naming as stage 172, so an uploaded picture and a shipped one mean the same
thing. R2 in production, `server/media/` under `npm run serve`. The Worker tries
the shipped assets first and the bucket second.

**The type is read from the bytes, not the header.** A content-type is a claim
by whoever is uploading, and a shop's product page is not where you find out it
was wrong.

### The old Staff view is still inside index.html

Stripping it is the obvious follow-up and it has a real cost: `STAFF_DOOR` puts
that view behind the PIN on `file://`, which is how the offline walkthrough
demos the counter with no server. Removing it makes the customer app smaller and
stops shipping counter code to shoppers; it also ends the offline staff demo.
Decide before doing it.

### What is still not done

- **The app still ships the starter catalogue inline.** `PRODUCTS` is built
  from `BASE_PRODUCTS` in the document and then merged with what the server
  sends. Making the server the only source is the next stage, and it is only
  worth doing once the owner's real list is actually in.
- **Web push is the next stage.** It is how an order-ready alert reaches a
  closed app, and it needs no carrier's permission at all — it goes through
  Apple's and Google's push services, not the phone network, so SHAFT does not
  apply. iOS has supported it since 16.4, but only once the app is on the home
  screen, which makes the install prompt worth building at the same time.
  Right now there is none: Android users get Chrome's ignorable infobar and
  iOS users get nothing.
- **Nothing sends email yet.** The join and the deal-alerts signup both reach
  the shop and both forward to the CRM webhook, which is where GoHighLevel
  picks them up. The service itself has no sender. Check the ESP's acceptable
  use policy covers vape retail before building one — several mainstream ones
  do not, and the failure mode is an account closed with the list inside it.
- **There is no photo upload from the counter.** The bulk photo import still
  writes base64 into one device's localStorage, where it is stranded. The
  service now accepts a photo *path*, so the missing piece is somewhere to PUT
  the bytes — R2, and an endpoint. `npm run import --photos` is the way in
  until then.
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
python3 test/member.py       28 checks   the customer's half of rewards
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
cd server && npm test                    81 checks, the service, offline
python3 test/live_backend.py             40 checks, two real browsers, real service
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
app/index.html        the customer app, the build output (1.9 MB since stage 172)
app/counter.html      the register. A hand-written source file, 36 KB, no photos.
                      Served at /counter. Not produced by a stage.
app/img/              309 photographs, named by the hash of their own bytes.
                      Referenced as `img/<hash>.webp` — relative, no slash.
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
cp app/index.html app/index.before175.html      # always
python3 stages/s175_whatever.py
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
