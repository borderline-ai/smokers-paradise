/* =====================================================================
   A D1 STAND-IN, SO THE TESTS RUN WITH NOTHING INSTALLED.

   The app's own test suites drive a real browser with every network request
   aborted, on the principle that a test which needs the world to be up is a
   test that will not be run. The same principle here: these tests need Node
   and nothing else. No wrangler, no npm install, no Cloudflare account, no
   network.

   Node 24 ships node:sqlite, and D1 is SQLite, so the shim is thin — it maps
   D1's prepare/bind/first/all/run/batch onto it and nothing more. It is a
   test double and it says so: if it ever grows a behaviour D1 does not have,
   the tests stop meaning anything.
   ===================================================================== */

import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';

/* node:sqlite refuses a boolean or an undefined. D1 accepts both and coerces,
   so the shim has to as well or it would fail tests the real thing passes. */
const coerce = v => {
  if (v === undefined) return null;
  if (typeof v === 'boolean') return v ? 1 : 0;
  return v;
};

class Stmt {
  constructor(db, sql) { this.db = db; this.sql = sql; this.args = []; }
  bind(...args) { const s = new Stmt(this.db, this.sql); s.args = args.map(coerce); return s; }
  #prep() { return this.db.prepare(this.sql); }
  async first() { const r = this.#prep().get(...this.args); return r === undefined ? null : r; }
  async all() { return { results: this.#prep().all(...this.args), success: true }; }
  async run() { const r = this.#prep().run(...this.args); return { success: true, meta: r }; }
}

/* `file` is ':memory:' for tests and a path for the local server, which is the
   only difference between the two: the same schema, the same shim, the same
   handler. A local run that behaved differently from the test would be worth
   nothing. */
export function makeD1(schemaPath, file = ':memory:') {
  const db = new DatabaseSync(file);
  db.exec(readFileSync(schemaPath, 'utf8'));
  return {
    prepare: sql => new Stmt(db, sql),
    batch: async stmts => { const out = []; for (const s of stmts) out.push(await s.run()); return out; },
    _raw: db
  };
}
