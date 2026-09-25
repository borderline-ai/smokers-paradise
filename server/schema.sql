-- =====================================================================
-- Smokers Paradise — the shop's database.
--
-- Everything the app claimed to have and did not. Before this file, a
-- member existed only on the phone that created her, a visit could not be
-- added from the counter because the counter could not find her, and an
-- order never left the browser that placed it.
--
-- Read CLAUDE.md, "What the backend has to hold". This is that list, plus
-- the two things it implies: a way for the counter to prove it is the
-- counter, and a queue so a shop with bad signal degrades instead of
-- breaking.
--
-- D1 is SQLite. Timestamps are ISO-8601 strings in UTC, because they are
-- read by people as often as by code and a shop owner should be able to
-- open the table and understand it.
-- =====================================================================

-- ---------------------------------------------------------------------
-- MEMBERS
--
-- One row per person, one person per phone number, which is exactly what
-- the customer-facing terms already promise: "One membership per phone
-- number."  That promise is a UNIQUE constraint here, not a hope.
--
-- `birthday` is month and day, never a year. The join form has no control
-- that can take a year and this column must never learn to hold one.
--
-- `token` is the phone's key to its own card. The member code is NOT a
-- credential: it is derived from the phone number, it is five digits wide,
-- and it is meant to be read out loud across a counter. Anyone can guess
-- one. So the code opens nothing on its own — the counter reads a member by
-- code only with a staff session, and the customer's own phone reads its own
-- card with this opaque token.
--
-- `left_at` rather than DELETE. Somebody who leaves the programme stops
-- appearing on their phone and stops appearing at the counter, but the visits
-- they already paid for are not rewritten out of the shop's history.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS members (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  shop      TEXT    NOT NULL,
  code      TEXT    NOT NULL,
  phone     TEXT    NOT NULL,              -- digits only, ten of them
  email     TEXT    NOT NULL DEFAULT '',
  first     TEXT    NOT NULL,
  birthday  TEXT    NOT NULL DEFAULT '',   -- 'M-D', or empty. Never a year.
  -- Consent, and what was consented TO. `contact_terms` holds the exact
  -- sentence the person ticked, because "they opted in" is not an answer to a
  -- complaint and the wording on the form will change over time.
  sms       INTEGER NOT NULL DEFAULT 0,
  email_ok  INTEGER NOT NULL DEFAULT 0,
  contact_terms TEXT NOT NULL DEFAULT '',
  token     TEXT    NOT NULL,
  joined    TEXT    NOT NULL,
  /* The year the birthday message last went out. The scheduled handler runs
     every ten minutes; without this a member would get one hundred and forty
     four birthday emails on the day and never open one again. */
  birthday_sent TEXT,
  left_at   TEXT,
  UNIQUE (shop, phone),
  UNIQUE (shop, code)
);
CREATE INDEX IF NOT EXISTS members_token ON members (token);
CREATE INDEX IF NOT EXISTS members_bday  ON members (shop, birthday);

-- ---------------------------------------------------------------------
-- SUBSCRIBERS
--
-- The one-field box on the front page. It is not a membership: no code, no
-- visits, no card — just somebody who wants to hear when a real deal lands.
--
-- It exists because that box used to lie. It took a phone number, wrote it to
-- localStorage, and said "You are on the list. One text when a real deal
-- lands." There was no list, nothing was sent, and nobody was ever told. A
-- form that does nothing is worse than no form: the customer believes they
-- have done something and stops looking for the real way in.
--
-- Email rather than a number, because SMS to a smoke shop's customers means
-- fighting carrier content rules on the phrasing of every promotion. Email
-- has no such fight.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subscribers (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  shop     TEXT    NOT NULL,
  email    TEXT    NOT NULL,
  source   TEXT    NOT NULL DEFAULT '',   -- which screen they came from
  terms    TEXT    NOT NULL DEFAULT '',   -- the sentence they agreed to
  created  TEXT    NOT NULL,
  left_at  TEXT,
  UNIQUE (shop, email)
);

-- ---------------------------------------------------------------------
-- VISITS
--
-- The central honesty property of the whole product: a visit is a fact
-- about the till, so only the till may write one. There is no endpoint a
-- customer's device can reach that inserts into this table. `by` records
-- which staff session added it, so a disputed card has an answer.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS visits (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  shop      TEXT    NOT NULL,
  member_id INTEGER NOT NULL REFERENCES members(id),
  at        TEXT    NOT NULL,
  by        TEXT    NOT NULL DEFAULT 'counter'
);
CREATE INDEX IF NOT EXISTS visits_member ON visits (member_id);
CREATE INDEX IF NOT EXISTS visits_shop_at ON visits (shop, at);

-- ---------------------------------------------------------------------
-- REDEMPTIONS
--
-- `cost` is the whole point of this table, and it is NOT NULL on purpose.
-- Stage 167 fixed a bug where changing the rule from 10 visits to 6
-- re-priced every past redemption and invented four free visits out of
-- nothing. A redemption is priced at the moment it happened. The rule may
-- change tomorrow; this one was already paid for.
--
-- `reward` is stamped for the same reason: "$10 off" today may be
-- "a free lighter" next month, and the history has to still read true.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS redemptions (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  shop      TEXT    NOT NULL,
  member_id INTEGER NOT NULL REFERENCES members(id),
  at        TEXT    NOT NULL,
  reward    TEXT    NOT NULL,
  cost      INTEGER NOT NULL,
  by        TEXT    NOT NULL DEFAULT 'counter'
);
CREATE INDEX IF NOT EXISTS redemptions_member ON redemptions (member_id);

-- ---------------------------------------------------------------------
-- ORDERS
--
-- `body` is the ticket exactly as it was placed, as JSON, and it is the
-- record. The columns beside it exist so the register board can be drawn
-- without parsing every ticket, not because they are a second truth.
--
-- The order carries its own copy of names, variants and unit prices as they
-- were at the moment it was placed. Read back in a year it still says what
-- the customer actually bought, whatever the shelf says by then.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
  shop      TEXT    NOT NULL,
  code      TEXT    NOT NULL,
  n         INTEGER NOT NULL,
  who       TEXT    NOT NULL DEFAULT '',
  phone     TEXT    NOT NULL DEFAULT '',
  subtotal  REAL    NOT NULL DEFAULT 0,
  fee       REAL    NOT NULL DEFAULT 0,
  tax       REAL    NOT NULL DEFAULT 0,
  total     REAL    NOT NULL DEFAULT 0,
  pickup    TEXT    NOT NULL DEFAULT '',
  source    TEXT    NOT NULL DEFAULT '',
  status    TEXT    NOT NULL DEFAULT 'placed',
  status_at TEXT    NOT NULL,
  arriving  TEXT    NOT NULL DEFAULT 'none',
  member_id INTEGER REFERENCES members(id),
  placed_at TEXT    NOT NULL,
  body      TEXT    NOT NULL,
  PRIMARY KEY (shop, code)
);
CREATE INDEX IF NOT EXISTS orders_board ON orders (shop, status, placed_at);

-- One row per line. The ticket JSON above is the record; this is so the shop
-- can answer "what actually sells" without reading every ticket by hand.
CREATE TABLE IF NOT EXISTS order_items (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  shop       TEXT    NOT NULL,
  code       TEXT    NOT NULL,
  product_id TEXT    NOT NULL,
  name       TEXT    NOT NULL DEFAULT '',
  brand      TEXT    NOT NULL DEFAULT '',
  variant    TEXT    NOT NULL DEFAULT '',
  qty        INTEGER NOT NULL DEFAULT 1,
  unit       REAL    NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS order_items_code ON order_items (shop, code);
CREATE INDEX IF NOT EXISTS order_items_pid  ON order_items (shop, product_id);

-- ---------------------------------------------------------------------
-- CATALOGUE
--
-- Two jobs in one table, told apart by `edited`.
--
--   edited = 0   the baseline, seeded once from the app's own product list.
--                It exists so the server can price an order. A server that
--                cannot price is not an authority, it is a postbox.
--   edited = 1   what the counter changed. Only these rows, plus anything
--                the counter added (custom = 1), are sent back to customer
--                phones as overrides. Sending the whole baseline back would
--                be shipping the catalogue twice.
--
-- `patch` is JSON in the shape the app's own S.edits already uses, so the
-- client applies it with the code it already has.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog (
  shop    TEXT    NOT NULL,
  id      TEXT    NOT NULL,
  patch   TEXT    NOT NULL,
  custom  INTEGER NOT NULL DEFAULT 0,
  edited  INTEGER NOT NULL DEFAULT 0,
  updated TEXT    NOT NULL,
  PRIMARY KEY (shop, id)
);
CREATE INDEX IF NOT EXISTS catalog_changed ON catalog (shop, edited, custom);

-- ---------------------------------------------------------------------
-- CONFIG
--
-- The shop's rule, in the shop's words and the shop's numbers, held where
-- every device can read it. Before this, the owner changed the rule on the
-- iPad and no customer phone ever heard about it.
--
-- `rev` bumps on every write so a client can tell "nothing changed" cheaply.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS config (
  shop    TEXT    NOT NULL,
  key     TEXT    NOT NULL,
  value   TEXT    NOT NULL,
  rev     INTEGER NOT NULL DEFAULT 1,
  updated TEXT    NOT NULL,
  PRIMARY KEY (shop, key)
);

-- ---------------------------------------------------------------------
-- STAFF SESSIONS
--
-- The PIN is checked here, not in JavaScript. A PIN compared in the browser
-- is a decoration: the customer app is public and anyone can read its source.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS staff_sessions (
  id      TEXT PRIMARY KEY,
  shop    TEXT NOT NULL,
  created TEXT NOT NULL,
  expires TEXT NOT NULL,
  ua      TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS staff_sessions_exp ON staff_sessions (expires);

-- Failed PIN attempts, so a four digit PIN on a public address cannot be
-- walked through ten thousand tries by a script.
CREATE TABLE IF NOT EXISTS pin_attempts (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  shop TEXT NOT NULL,
  who  TEXT NOT NULL,          -- the caller's IP, as the edge reports it
  at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS pin_attempts_who ON pin_attempts (shop, who, at);

-- ---------------------------------------------------------------------
-- OUTBOUND QUEUE
--
-- The shop's CRM webhook, retried by the server instead of by the customer's
-- phone. Stage 170 found that the phone-side queue only drained when the app
-- was reopened, which means a join made by somebody who never opens the app
-- again is a join the shop never hears about. A queue on the server does not
-- depend on the customer coming back.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS outbound (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  shop     TEXT    NOT NULL,
  url      TEXT    NOT NULL,
  body     TEXT    NOT NULL,
  tries    INTEGER NOT NULL DEFAULT 0,
  next_try TEXT    NOT NULL,
  last_err TEXT    NOT NULL DEFAULT '',
  created  TEXT    NOT NULL,
  sent_at  TEXT
);
CREATE INDEX IF NOT EXISTS outbound_pending ON outbound (sent_at, next_try);
