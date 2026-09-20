# The shop's backend

One Cloudflare Worker and one D1 database. It serves the app **and** answers
the app, from the same origin.

That is not a deployment preference. `call()` in `app/index.html` sends
`credentials: 'same-origin'`, and the counter's proof that it is the counter is
a cookie. Split the two across origins and the register board stops working —
or it only works with `SameSite=None`, which is the setting that would let a
link in a text message make the counter's own browser add a visit.

**So this replaces GitHub Pages as the address customers are given.** Pages can
keep serving the standalone walkthrough file. It cannot be the shop.

---

## What it holds

| Table | What it is |
| --- | --- |
| `members` | first name, phone, birthday as month-day with no year, sms consent, code, joined, and an opaque token that is the phone's key to its own card |
| `visits` | one row per visit, with which staff session wrote it |
| `redemptions` | with `cost` — **the visit price at the moment it happened**, see stage 167 |
| `orders` / `order_items` | the ticket exactly as placed, plus lines so the shop can see what sells |
| `catalog` | the seeded shelf, and every price or menu edit made at the counter |
| `config` | the `SHOP_REWARDS` rule, held where every device can read it |
| `staff_sessions`, `pin_attempts` | the counter's door |
| `outbound` | the CRM webhook queue, retried by the server |

---

## Run it here, first

No account, no install, no network:

```bash
cd server && npm run build && node scripts/serve.mjs
```

```
the shop     http://127.0.0.1:8787/
the counter  http://127.0.0.1:8787/counter   PIN 7413
```

Data is in memory and gone when you stop it. `SP_DB=shop.db node scripts/serve.mjs`
keeps it in a file.

This is the same handler that deploys — `src/index.js`, the same schema, the
same code paths. The only difference is D1 versus a file on this disk.

---

## Deploy it

```bash
npm install
npx wrangler login

npm run db:create          # prints a database_id
#   paste that id into wrangler.toml, replacing PASTE_THE_ID_FROM_db:create
npm run db:init            # creates the tables on the remote database

npm run pin                # set the staff PIN. It is a Worker secret, not a
                           # row and not a line in the app. Change it any time
                           # with this same command.
npm run deploy             # copies app/index.html into public/ and ships
```

Then, once, from the counter screen on the deployed address: open **Staff →
Menu** and save anything. That seeds the shelf so the server can price an
order. Until it is seeded, the server takes the phone's prices and marks the
ticket `priced: 'phone'` rather than pretending otherwise.

### Afterwards

```bash
npm run deploy             # any time app/index.html changes
npm run members            # the last 50 joins, from the terminal
```

The shop's whole member list downloads as CSV from the counter's Rewards tab,
or at `/api/staff/members/export.csv` with a staff session. In full, on demand.
That is a sales promise; keep it true.

---

## The rules this service enforces

These are the four in `CLAUDE.md`, and each one has a test.

**1. Only the counter may write a visit.** There is no route a customer device
can reach that inserts into `visits`. `/api/staff/*` will not dispatch without
a session issued against a PIN the *server* checked. A PIN compared in
JavaScript is a decoration — the customer app is public and anyone can read its
source.

**2. A redemption is priced at the moment it happened.** `redemptions.cost` is
`NOT NULL` and is never recomputed. Change the rule from 10 visits to 6 and
every past redemption still cost what it cost. Stage 167 fixed exactly this bug
once already; the schema is what stops it coming back.

**3. The shop owns the member data**, exportable in full, on demand.

**4. Offline degrades, it does not break.** A join queued on a phone with no
signal posts here whenever that phone next has one, and posting it twice is not
an error — the same phone number is the same membership, which is what the
customer-facing terms already promise. From here the shop's CRM webhook is
retried by the server, on a timer, so a join no longer depends on the customer
reopening the app.

---

## The API

Everything answers JSON, **including every refusal**. That is forced: `call()`
reads the content-type before the body, and anything that is not JSON reads to
the app as "there is no shop here", which quietly turns the whole ordering
surface off.

### Anyone

| | |
| --- | --- |
| `GET /api/config` | the rewards rule and tax. The CRM webhook is **not** in here. |
| `POST /api/members` | join. Body is the flat `{first, phone, birthday, sms, code, joined, shop}` the app already sends to a GoHighLevel webhook. |
| `GET /api/members/me?token=` | a phone reading its own card. Read only. |
| `POST /api/members/me/leave` | leaving. The row is kept, flagged. |
| `POST /api/orders` | place. The shop re-prices and the shop wins. |
| `GET /api/orders/status?codes=` | statuses and nothing else — a pickup code never reveals a name, a number or a basket. |
| `POST /api/orders/:code/arriving` | "on my way" / "I'm here". Forward only. |
| `GET /api/catalog/overrides` | what the counter changed. |
| `GET /api/availability?ids=` | stock, where the shop tracks it. Never invented. |
| `GET /api/loyalty/status` | answers `provider: 'none'`, which is what makes the app fall through to the shop's own programme instead of showing a broken points screen. |

### The counter — staff session required

| | |
| --- | --- |
| `POST /api/staff/session` | `{pin}`. Rate limited: eight wrong PINs from one address buys a quarter of an hour. |
| `GET /api/staff/orders` | the register board. |
| `POST /api/staff/orders/:code/status` | mark ready, mark collected. |
| `GET /api/staff/members?code=` | **the call that did not exist.** Its absence is what made the rewards programme a demo. |
| `POST /api/staff/members/:code/visit` | `{force}` gets past the thirty-second double-tap guard. |
| `POST /api/staff/members/:code/redeem` | refused when nothing is ready, stamped with what it cost. |
| `GET /api/staff/members/export.csv` | the whole list. |
| `GET` / `POST /api/staff/config` | the rule. The owner's copy includes the CRM webhook. |
| `POST /api/staff/catalog/seed` | the shelf, once. |
| `POST /api/staff/catalog/overrides` | price and menu edits. Photos are refused, not truncated. |

---

## Tests

```bash
npm test                     # 40 checks, offline, nothing installed
python3 ../test/live_backend.py   # 23 checks, two real browsers, real service
```

`npm test` drives the real Worker handler over real requests, against
`node:sqlite` standing in for D1. Two "devices" means two cookie jars, which is
the exact shape of the bug this service exists to end.

`live_backend.py` starts the service and drives the actual 12MB app in two
browser contexts: a customer joins on one, the counter finds her code and adds
a visit on the other, and her card moves. That was impossible before this
existed.

A caution from `CLAUDE.md` that applies here too: **two green suites can both be
right and still miss the bug.** Ask what a number means, not just whether it
passes.

---

## Known limits, stated rather than hidden

- **Photographs do not live here.** `catalog` holds prices and names. A photo
  added at the counter stays on the device that added it. Moving them out of
  the 12MB HTML into R2 is the next piece of work, not this one.
- **The order's reward field is a request, never a discount.** It carries a
  label and a status and cannot move a total. The register is the final word.
- **`priced: 'phone'`** on a ticket means the server had no price for that line.
  Seed the shelf and it goes away. It is reported rather than hidden because a
  shop should be able to tell which of its tickets it actually priced.
- **One shop per database.** `SHOP` namespaces every row so a second shop is a
  second database and a different value, never a shared table.
- **The app is 11.5 MiB and a Workers static asset caps at 25 MiB.** `npm run
  build` refuses rather than letting a deploy fail halfway.
