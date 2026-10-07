-- =====================================================================
-- PARADISE REWARDS, POINTS ON SPEND.  *** PROPOSAL — NOT YET APPLIED ***
--
-- Replaces the visit-based programme. $1 spent earns 10 points; points come
-- off a sale as money. Five tiers, every one landing between 4% and 5% back
-- so no rung is obviously the right one to farm.
--
-- WRITTEN FOR D1 (SQLite), NOT POSTGRES. The brief specifies Supabase; the
-- backend it was written against did not exist yet and now does, deployed and
-- tested on Cloudflare. What Supabase genuinely offered was auth and RLS, and
-- the staff table below closes that gap without rewriting six stages. Say the
-- word and I will port this to Postgres instead — the shape does not change.
--
-- THE COMPLIANCE STRUCTURE IS LOAD-BEARING. Read the brief's compliance
-- section before editing anything here. In short: FDA prohibits distributing
-- free tobacco products, and names loyalty programmes explicitly. A discount
-- inside a sale is permitted; handing over a product is not. That is why
-- `discount_cents` exists and why there is no concept of an entitled item.
-- =====================================================================

-- ---------------------------------------------------------------------
-- STAFF.  The gap Supabase would have filled.
--
-- Today there is one shared PIN, so `visits.by` records a session rather than
-- a person. On a spend-based programme an employee types the dollar amount,
-- which means an employee can type $500 instead of $50 and hand a friend a
-- free vape. The audit log is the control that makes the programme safe to
-- run, and an audit log that cannot name a person is decoration.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS staff (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  shop       TEXT    NOT NULL,
  name       TEXT    NOT NULL,
  email      TEXT    NOT NULL DEFAULT '',
  role       TEXT    NOT NULL,          -- owner | manager | employee
  pin_hash   TEXT    NOT NULL,          -- PBKDF2, per person. Never the PIN.
  pin_salt   TEXT    NOT NULL,
  active     INTEGER NOT NULL DEFAULT 1,
  created_at TEXT    NOT NULL,
  last_seen  TEXT,
  UNIQUE (shop, name)
);

-- ---------------------------------------------------------------------
-- THE RULE
--
-- `min_tender_cents` defaults to 1 and MAY NEVER BE 0. The sale subtotal must
-- be strictly greater than the discount so the customer tenders something
-- above zero. That is the legal requirement, not a business preference: it is
-- what makes the reward part of a sale rather than a free distribution. It is
-- not configurable to zero and no manager may override it.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS program_config (
  shop              TEXT PRIMARY KEY,
  on_               INTEGER NOT NULL DEFAULT 1,
  name              TEXT    NOT NULL DEFAULT 'Paradise Rewards',
  points_per_dollar INTEGER NOT NULL DEFAULT 10,
  -- pre or post tax. Arizona tobacco excise on top of a points rate is the
  -- owner paying rewards on the state's money, so: pre.
  accrue_on_tax     TEXT    NOT NULL DEFAULT 'pre',
  rounding          TEXT    NOT NULL DEFAULT 'nearest',
  min_tender_cents  INTEGER NOT NULL DEFAULT 1 CHECK (min_tender_cents >= 1),
  max_txn_cents     INTEGER NOT NULL DEFAULT 30000,
  points_expire_months INTEGER,          -- null = no expiry. Ships null.
  perk              TEXT    NOT NULL DEFAULT '',
  terms             TEXT    NOT NULL DEFAULT '',
  updated_at        TEXT    NOT NULL,
  updated_by        INTEGER REFERENCES staff(id)
);

-- ---------------------------------------------------------------------
-- THE TIERS
--
-- A tier is a dollar amount off a sale. It is never "a free vape". The
-- programme does not classify its tiers either: papers and pipes are
-- regulated differently from grinders, and deciding which of five tiers is a
-- tobacco product is a question you would have to get right five times and
-- keep right forever. Everything being a discount means the question is never
-- asked. One rule, uniformly safe, less code.
--
--   750 pts -> $3 off    ($75 spend, 4.0% back)
--  2500 pts -> $10 off  ($250 spend, 4.0%)
--  3000 pts -> $12 off  ($300 spend, 4.0%)
--  5000 pts -> $25 off  ($500 spend, 5.0%)
-- 15000 pts -> $75 off ($1500 spend, 5.0%)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reward_tiers (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  shop               TEXT    NOT NULL,
  name               TEXT    NOT NULL,   -- the owner's label, for reports
  description        TEXT    NOT NULL DEFAULT '',
  points_cost        INTEGER NOT NULL CHECK (points_cost > 0),
  discount_cents     INTEGER NOT NULL CHECK (discount_cents > 0),
  min_subtotal_cents INTEGER,            -- null = the shop default applies
  active             INTEGER NOT NULL DEFAULT 1,
  sort_order         INTEGER NOT NULL DEFAULT 0,
  created_at         TEXT    NOT NULL,
  updated_at         TEXT    NOT NULL,
  updated_by         INTEGER REFERENCES staff(id)
);

-- ---------------------------------------------------------------------
-- MEMBERS.  Extends what is already live; nothing is dropped.
--
-- Age verification is new and it gates redemption. A member who has never
-- been verified at a counter cannot redeem however many points they hold.
-- Joining on a phone verifies nobody — the 21+ gate is a checkbox.
--
-- NO POINT TRANSFERS, GIFTING, SHARED ACCOUNTS OR FAMILY PLANS. Ever. They
-- are a way to move a tobacco benefit to somebody nobody age verified. If
-- anyone asks for the feature later, this comment is the answer.
-- ---------------------------------------------------------------------
-- ALTER TABLE members ADD COLUMN age_verified_at   TEXT;
-- ALTER TABLE members ADD COLUMN age_verified_by   INTEGER REFERENCES staff(id);
-- ALTER TABLE members ADD COLUMN age_verify_method TEXT;   -- id_checked | null
-- ALTER TABLE members ADD COLUMN notes             TEXT NOT NULL DEFAULT '';

-- ---------------------------------------------------------------------
-- TRANSACTIONS.  Every sale that earned points.
--
-- POINTS ACCRUE ON tender_cents, NEVER ON subtotal_cents. The discounted
-- portion earns nothing: a $30 basket with $25 off earns 50 points, not 300.
--
-- Money is integers, always. Points are integers. No float ever touches a
-- balance.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  shop            TEXT    NOT NULL,
  member_id       INTEGER NOT NULL REFERENCES members(id),
  subtotal_cents  INTEGER NOT NULL CHECK (subtotal_cents >= 0),
  discount_cents  INTEGER NOT NULL DEFAULT 0,
  tender_cents    INTEGER NOT NULL CHECK (tender_cents > 0),
  points_earned   INTEGER NOT NULL,
  multiplier      REAL    NOT NULL DEFAULT 1.0,  -- double points Tuesday, later
  created_at      TEXT    NOT NULL,
  created_by      INTEGER NOT NULL REFERENCES staff(id),
  source          TEXT    NOT NULL DEFAULT 'counter', -- counter|promo|adjustment|import|pos
  approved_by     INTEGER REFERENCES staff(id),   -- only when over the ceiling
  voided_at       TEXT,
  voided_by       INTEGER REFERENCES staff(id),
  void_reason     TEXT,
  idempotency_key TEXT    NOT NULL,
  UNIQUE (shop, idempotency_key)
);

-- ---------------------------------------------------------------------
-- REDEMPTIONS.  Priced at the moment they happened.
--
-- points_cost, tier_name, discount_cents, subtotal_cents and tender_cents are
-- all stamped here. Move tier 4 from 5,000 points to 6,000 and this row still
-- reads 5,000. That bug shipped once on the visit version and invented four
-- free visits out of nothing; stage 167 fixed it client side and this is the
-- server-side version of the same rule.
--
-- transaction_id is NOT NULL. A redemption requires a qualifying sale, and
-- the cleanest way to make an invalid state unrepresentable is to refuse to
-- store one. That is also why there is no standalone redeem endpoint.
--
-- id_checked is NOT NULL with no default. The employee answers it every time.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS redemptions (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  shop            TEXT    NOT NULL,
  member_id       INTEGER NOT NULL REFERENCES members(id),
  transaction_id  INTEGER NOT NULL REFERENCES transactions(id),
  tier_id         INTEGER NOT NULL REFERENCES reward_tiers(id),
  tier_name       TEXT    NOT NULL,      -- denormalised, at that moment
  points_cost     INTEGER NOT NULL,      -- at that moment
  discount_cents  INTEGER NOT NULL,      -- at that moment
  subtotal_cents  INTEGER NOT NULL,
  tender_cents    INTEGER NOT NULL,
  id_checked      INTEGER NOT NULL,      -- no default, on purpose
  id_checked_by   INTEGER NOT NULL REFERENCES staff(id),
  applied_to      TEXT    NOT NULL DEFAULT '',  -- reporting colour, never gates
  created_at      TEXT    NOT NULL,
  created_by      INTEGER NOT NULL REFERENCES staff(id),
  voided_at       TEXT,
  voided_by       INTEGER REFERENCES staff(id),
  void_reason     TEXT,
  idempotency_key TEXT    NOT NULL,
  UNIQUE (shop, idempotency_key),
  -- one reward per sale
  UNIQUE (transaction_id)
);

CREATE TABLE IF NOT EXISTS adjustments (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  shop       TEXT    NOT NULL,
  member_id  INTEGER NOT NULL REFERENCES members(id),
  points_delta INTEGER NOT NULL,
  reason     TEXT    NOT NULL,           -- required
  created_at TEXT    NOT NULL,
  created_by INTEGER NOT NULL REFERENCES staff(id)   -- manager only
);

CREATE TABLE IF NOT EXISTS audit_log (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  shop        TEXT    NOT NULL,
  actor       INTEGER REFERENCES staff(id),
  action      TEXT    NOT NULL,
  target_type TEXT    NOT NULL,
  target_id   TEXT    NOT NULL,
  before      TEXT,                      -- JSON
  after       TEXT,                      -- JSON
  created_at  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS txn_member   ON transactions (member_id, voided_at);
CREATE INDEX IF NOT EXISTS txn_by       ON transactions (shop, created_by, created_at);
CREATE INDEX IF NOT EXISTS red_member   ON redemptions  (member_id, voided_at);
CREATE INDEX IF NOT EXISTS adj_member   ON adjustments  (member_id);
CREATE INDEX IF NOT EXISTS audit_actor  ON audit_log    (shop, actor, created_at);

-- =====================================================================
-- BALANCE IS COMPUTED, NEVER STORED.
--
--   SUM(points_earned) on non-voided transactions
-- + SUM(points_delta)  on adjustments
-- - SUM(points_cost)   on non-voided redemptions
--
-- A stored running total is exactly how the phone and the iPad end up
-- disagreeing, and it is how a void becomes unfixable.
-- =====================================================================

-- =====================================================================
-- THE TIERS AS THE OWNER SET THEM.  Seed data, not a migration.
--
-- Every value here is the shop's, editable from the counter. Nothing in this
-- table is a number chosen by whoever wrote the code.
--
--  points   off    min basket   spend to earn   back
--     400    $1      $15           $40          2.5%
--     750    $3       —            $75          4.0%
--   2,500   $10       —           $250          4.0%
--   3,000   $12       —           $300          4.0%
--   5,000   $25       —           $500          5.0%
--  15,000   $75       —         $1,500          5.0%
--
-- THE FIRST RUNG IS DELIBERATELY WORSE VALUE, AND DELIBERATELY GATED.
--
-- 2.5% against 4-5% on everything above it, because impatience should cost
-- the shop less than patience — the same direction the rest of the ladder
-- runs in. It exists to be reachable on somebody's second visit, which is
-- where a punch card either hooks a person or loses them.
--
-- The $15 floor is not about economics, it is about the counter. Compliance
-- requires an ID check on every redemption, recorded, every time. Without a
-- floor, a dollar off is the same work at the till as seventy-five dollars
-- off, and during a rush staff quietly stop offering it — which is worse than
-- not having the rung, because the customer can see it on their card and will
-- ask for it. A floor means the dollar is never the whole interaction.
--
-- The tiers above it need no floor of their own: the shop-wide rule already
-- refuses any sale where the discount is not strictly less than the subtotal,
-- so $25 off can never be applied to a $19.99 basket.
-- =====================================================================
INSERT INTO reward_tiers
  (shop, name, description, points_cost, discount_cents, min_subtotal_cents,
   active, sort_order, created_at, updated_at)
VALUES
  ('smokers-paradise', 'A dollar off',  '$1 off any purchase over $15',
     400,   100, 1500, 1, 1, datetime('now'), datetime('now')),
  ('smokers-paradise', 'Papers',        '$3 off',
     750,   300, NULL, 1, 2, datetime('now'), datetime('now')),
  ('smokers-paradise', 'Ten off',       '$10 off',
    2500,  1000, NULL, 1, 3, datetime('now'), datetime('now')),
  ('smokers-paradise', 'Twelve off',    '$12 off',
    3000,  1200, NULL, 1, 4, datetime('now'), datetime('now')),
  ('smokers-paradise', 'Disposable',    '$25 off',
    5000,  2500, NULL, 1, 5, datetime('now'), datetime('now')),
  ('smokers-paradise', 'Glass',         '$75 off',
   15000,  7500, NULL, 1, 6, datetime('now'), datetime('now'));

-- The `name` column is the owner's label, for her reports. THE CUSTOMER NEVER
-- SEES IT. Their card says "$25 off" and nothing else — no product name sits
-- next to a reward anywhere in this app, which is both the legal structure and
-- the better product, because the customer spends it on whatever they want.
