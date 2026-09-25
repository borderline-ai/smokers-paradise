-- =====================================================================
-- MIGRATION 001 — the visit programme becomes a points programme.
--
-- Run ONCE, before schema.loyalty.sql. It is separate from that file because
-- a schema is something you can re-run and a migration is not.
--
-- THE OLD TABLES ARE RENAMED, NOT DROPPED. A shop that ran the visit
-- programme has real history in them — visits somebody paid for and rewards
-- somebody redeemed — and it is not this migration's business to delete it.
-- They stay as `visits_v1` and `redemptions_v1`, readable forever.
--
-- Smokers Paradise has zero rows in both today, so nothing is carried across.
-- A shop with real visits would need a decision about conversion: visits are
-- not points and there is no honest exchange rate that does not either invent
-- value or take it away. Ask the owner; do not pick a number.
-- =====================================================================

ALTER TABLE visits      RENAME TO visits_v1;
ALTER TABLE redemptions RENAME TO redemptions_v1;
