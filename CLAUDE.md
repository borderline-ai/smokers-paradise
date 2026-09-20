# Smokers Paradise — shop app

A single-file web app built for Smokers Paradise, a smoke shop at 922 N Grand Ave,
Nogales AZ. Built by BorderLine AI. It installs to a phone home screen as a PWA,
with no app store.

Live at **borderline-ai.github.io/smokers-paradise** (GitHub Pages, from the
`smokers-paradise` repo on the `borderline-ai` account, branch `main`, path `/`).

---

## THE ONE THING THAT MATTERS RIGHT NOW

**There is no backend, and the product does not work without one.**

Everything is `localStorage` on whichever device it happened on. That is fine for
a walkthrough and fatal for a shop. Proven, not assumed — two browser contexts
are two devices:

```
customer joins on her phone      -> code SP26699 written to HER localStorage
staff type SP26699 on the iPad   -> "No member with that code on this device."
```

So today:

| Claimed | Reality |
| --- | --- |
| The shop owns a customer list | Every member record lives only on the phone that created it. The shop has nothing. |
| Rewards | The counter can never find a real customer. No visit can ever be added. |
| Order ahead | `SP_API = null`, `OrderStore.live = false`. Orders never reach the counter. |
| Staff edits a price | Never reaches a customer's phone. Verified: edited 30 -> 999.99 on the shop device, the customer device still showed 30. |

**Building that backend is the job.** Until it exists, nothing transactional can
be sold, and no usage-based price can be defended because nothing is counted.

### What the backend has to hold

- **members** — first name, phone (digits only), birthday as month-day with no
  year, sms consent, member code, joined timestamp, shop id
- **visits** — member, timestamp, who added it
- **redemptions** — member, timestamp, and **the visit cost at the time**, see
  stage 167 for why
- **orders** — the existing ticket shape that `OrderStore` already expects
- **catalogue overrides** — price and menu edits made from the counter screen
- **shop config** — the `SHOP_REWARDS` rule, currently in `sp_rewards_cfg_v1`

### Rules the backend must not break

1. **Only the counter may write a visit.** A visit the customer's own device can
   create is a coupon anyone can print. The customer's screen is read-only about
   its own count. This is the central honesty property of the whole product and
   there is a test that proves it (`test/member.py`, "pressing every control on
   the card adds no visit").
2. **A redemption is priced at the moment it happened.** If the owner changes the
   rule from 10 visits to 6, past redemptions must not be re-priced. Stage 167
   fixed exactly this bug, which invented four free visits out of nothing.
3. **The shop owns the member data.** It must be exportable in full, on demand.
   That is a sales promise, keep it true.
4. **Offline must degrade, not break.** A shop with bad signal still has to take
   a join. The existing queue-and-retry shape (`Member.flush`, stage 170) is the
   right idea, keep it.

### Where the wiring already is

- `SHOP_REWARDS.endpoint` — set it and a join POSTs one flat JSON object:
  `{first, phone, birthday, sms, code, joined, shop}`. That shape was chosen for
  a GoHighLevel inbound webhook.
- `Member.flush()` — drains a retry queue. Called on join and, since stage 170,
  2.5s after open.
- `SP_API` / `OrderStore` — an ordering client already written against an API
  that does not exist. Read it before designing the order endpoints, it tells
  you the shape that was expected.
- `Loyalty` — a ~5,700 char module that reads an EXTERNAL loyalty provider. It is
  dormant (`SP_API` null). The in-house `Member` programme sits beside it, not
  inside it. If a real provider ever answers, `Loyalty` wins.

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
test/*.py             Playwright suites, network-dead
test/tablet/*.py      the same, at iPad sizes
data/                 Spanish strings, hero device map, language data
docs/                 the Holy Cow source this was converted from, and its checksum
```

## Working on it

```bash
cp app/index.html app/index.before171.html      # always
python3 stages/s171_whatever.py
python3 test/member.py && python3 test/counter.py
```

Then open `app/index.html` in a browser. There is no build step and no server.
