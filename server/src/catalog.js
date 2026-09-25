/* =====================================================================
   THE CATALOGUE THE SHOP OWNS.

   Proven before this existed: the owner edited a price from 30 to 999.99 on
   the shop device, and the customer device still showed 30. A price edit that
   reaches nobody is not an edit, it is a note to self.

   Two moving parts.

   SEEDING is a one-off. The app holds 259 researched products inline; the
   server holds none. Until the server knows what a thing costs it cannot
   price an order, and a server that cannot price is a postbox. So the counter
   posts the shelf up once and the server has a baseline.

   OVERRIDES are forever. Every price change, every hidden product, every new
   product typed in at the counter lands here and every phone picks it up on
   its next open. The shape of `patch` is the shape of `S.edits[id]` in the
   app, so the client applies it with code it already has.

   A PHOTOGRAPH IS A PATH, NEVER BASE64. Since stage 172 the app references
   pictures as `img/<hash>.webp`, and `rebuildCatalog()` already turns
   `S.edits[id].photo` straight into `PHOTOS[id]` and then into an <img src>.
   So a patch may carry a photo, as long as it carries a reference to one.

   A data: URI is still refused, and loudly. Some of them are megabytes, a D1
   row is not a photo store, and quietly truncating one would put a broken
   image on a customer's phone — which is what rule 2 in CLAUDE.md exists to
   prevent. Before stage 172 this rejected the word `photo` outright; that was
   right when a photo meant a megabyte and wrong the moment it meant a path.
   ===================================================================== */

import { ok, fail, str, money, nowIso } from './http.js';
import { readCatalogue } from './importer.js';

const MAX_PATCH = 8 * 1024;        /* a price and some words, not a picture */

/* `img/ab12….webp` as stage 172 writes them, or a full https URL for a shop
   hosting its pictures somewhere else. Never a data: URI, and never a path
   that climbs out of the image directory. */
function cleanPhoto(v) {
  const p = str(v, 400);
  if (!p) return { value: '' };
  if (/^data:/i.test(p)) return { error: 'photo' };
  if (p.includes('..')) return { error: 'path' };
  if (/^img\/[A-Za-z0-9._-]+$/.test(p)) return { value: p };
  if (/^https:\/\//.test(p)) {
    try { return { value: new URL(p).toString() }; } catch { return { error: 'path' }; }
  }
  return { error: 'path' };
}

function cleanPatch(p) {
  if (!p || typeof p !== 'object') return null;
  const out = {};
  if ('photo' in p && p.photo) {
    const ph = cleanPhoto(p.photo);
    if (ph.error) return { error: ph.error };
    out.photo = ph.value;
  }
  if ('name'  in p) out.name  = str(p.name, 120);
  if ('brand' in p) out.brand = str(p.brand, 60);
  if ('cat'   in p) out.cat   = str(p.cat, 30);
  if ('desc'  in p) out.desc  = str(p.desc, 600);
  if ('price' in p) {
    const v = money(p.price);
    if (!(v >= 0 && v < 100000)) return { error: 'price' };
    out.price = v;
  }
  if ('published' in p) out.published = !!p.published;
  if ('hidden'    in p) out.hidden    = !!p.hidden;
  if ('stock'     in p) out.stock     = Math.max(0, Math.min(99999, parseInt(p.stock, 10) || 0));
  if (JSON.stringify(out).length > MAX_PATCH) return { error: 'big' };
  return { value: out };
}

/* GET /api/catalog/overrides
   Only what the counter changed, never the baseline. The phone already has
   the catalogue; shipping it back would be shipping it twice. */
export async function overrides(env, shop) {
  const rows = await env.DB.prepare(
    `SELECT id, patch, custom FROM catalog
      WHERE shop = ?1 AND (edited = 1 OR custom = 1) ORDER BY updated DESC LIMIT 2000`
  ).bind(shop).all();

  const edits = {};
  const custom = [];
  for (const r of (rows.results || [])) {
    let p; try { p = JSON.parse(r.patch); } catch { continue; }
    if (r.custom) custom.push(Object.assign({ id: r.id }, p));
    else edits[r.id] = p;
  }
  return ok({ edits, custom });
}

/* GET /api/catalog — the Commerce provider's shape. Answered only once the
   shelf has actually been seeded; an empty list from here would read to the
   client as "the shop stocks nothing", so an unseeded server says so instead
   of lying quietly. */
export async function catalog(env, shop) {
  const rows = await env.DB
    .prepare('SELECT id, patch FROM catalog WHERE shop = ?1 LIMIT 2000').bind(shop).all();
  const list = rows.results || [];
  if (!list.length) {
    return fail(404, 'not seeded',
      'This service has no catalogue yet. Seed it from the counter before pointing the app at it.');
  }
  const items = [];
  for (const r of list) {
    let p; try { p = JSON.parse(r.patch); } catch { continue; }
    if (p.hidden) continue;
    items.push({
      id: r.id, name: p.name || '', brand: p.brand || '',
      price: typeof p.price === 'number' ? p.price : null,
      stock: { tracked: 'stock' in p, onHand: 'stock' in p ? p.stock : null,
               reserved: 0, availableToOrder: 'stock' in p ? p.stock : null,
               inStock: 'stock' in p ? p.stock > 0 : true }
    });
  }
  return ok({ items });
}

/* GET /api/availability?ids=a,b,c */
export async function availability(env, shop, params) {
  const ids = str(params.get('ids') || '', 4000).split(',')
    .map(s => s.trim()).filter(Boolean).slice(0, 60);
  if (!ids.length) return ok({ availability: {} });

  const q = ids.map((_, i) => '?' + (i + 2)).join(',');
  const rows = await env.DB
    .prepare('SELECT id, patch FROM catalog WHERE shop = ?1 AND id IN (' + q + ')')
    .bind(shop, ...ids).all();

  const out = {};
  for (const r of (rows.results || [])) {
    let p; try { p = JSON.parse(r.patch); } catch { continue; }
    /* No stock count means no stock count. Rule 3 in CLAUDE.md: never invent
       a stock number. `tracked:false` is the app's way of saying "the shelf is
       the answer, ask at the counter". */
    out[r.id] = 'stock' in p
      ? { tracked: true, onHand: p.stock, availableToOrder: p.stock, inStock: p.stock > 0 }
      : { tracked: false, onHand: null, availableToOrder: null, inStock: !p.hidden };
  }
  return ok({ availability: out });
}

/* POST /api/staff/catalog/seed  {items:[{id,name,brand,price,...}]}
   Idempotent, and it never clobbers an edit: a row the counter has changed
   keeps its patch. Re-seeding after adding products to the app is safe. */
export async function seed(env, shop, body) {
  const items = Array.isArray(body.items) ? body.items.slice(0, 2000) : [];
  if (!items.length) return fail(400, 'empty', 'Nothing to seed.');

  const stamp = nowIso();
  const stmts = [];
  let skipped = 0;
  for (const it of items) {
    const id = str(it && it.id, 60);
    if (!id) { skipped++; continue; }
    const c = cleanPatch({
      name: it.name, brand: it.brand, cat: it.cat,
      price: typeof it.price === 'number' ? it.price : 0
    });
    if (!c || c.error) { skipped++; continue; }
    stmts.push(env.DB.prepare(
      `INSERT INTO catalog (shop, id, patch, custom, edited, updated)
       VALUES (?1, ?2, ?3, 0, 0, ?4)
       ON CONFLICT (shop, id) DO UPDATE SET patch = ?3, updated = ?4
         WHERE catalog.edited = 0 AND catalog.custom = 0`
    ).bind(shop, id, JSON.stringify(c.value), stamp));
  }
  /* D1 batches are capped; send them in chunks rather than one enormous one. */
  for (let i = 0; i < stmts.length; i += 100) await env.DB.batch(stmts.slice(i, i + 100));
  return ok({ seeded: stmts.length, skipped });
}

/* POST /api/staff/catalog/overrides  {edits:{id:patch}, custom:[{id,...}], remove:[id]}
   This is the counter pressing Save on the menu screen. */
export async function saveOverrides(env, shop, body) {
  const stamp = nowIso();
  const stmts = [];

  const edits = (body.edits && typeof body.edits === 'object') ? body.edits : {};
  for (const id of Object.keys(edits).slice(0, 500)) {
    const c = cleanPatch(edits[id]);
    if (!c) continue;
    if (c.error === 'photo') {
      return fail(413, 'photo',
        'A photograph has to be sent as a path, not as the picture itself. Put the file in app/img and send its name.');
    }
    if (c.error === 'path') {
      return fail(400, 'bad photo', 'That is not a picture this shop serves.');
    }
    if (c.error) return fail(400, 'bad edit', 'That price is not a number the register could ring.');
    stmts.push(env.DB.prepare(
      `INSERT INTO catalog (shop, id, patch, custom, edited, updated)
       VALUES (?1, ?2, ?3, 0, 1, ?4)
       ON CONFLICT (shop, id) DO UPDATE SET patch = ?3, edited = 1, updated = ?4`
    ).bind(shop, str(id, 60), JSON.stringify(c.value), stamp));
  }

  const custom = Array.isArray(body.custom) ? body.custom.slice(0, 500) : [];
  for (const it of custom) {
    const id = str(it && it.id, 60);
    if (!id) continue;
    const c = cleanPatch(it);
    if (!c || c.error === 'photo') {
      return fail(413, 'photo',
        'A photograph has to be sent as a path, not as the picture itself. Put the file in app/img and send its name.');
    }
    if (c.error) continue;
    stmts.push(env.DB.prepare(
      `INSERT INTO catalog (shop, id, patch, custom, edited, updated)
       VALUES (?1, ?2, ?3, 1, 1, ?4)
       ON CONFLICT (shop, id) DO UPDATE SET patch = ?3, custom = 1, edited = 1, updated = ?4`
    ).bind(shop, id, JSON.stringify(c.value), stamp));
  }

  /* Removing an override puts the product back to whatever the app ships.
     Deleting the row is right: an override that says "no change" is a lie
     waiting to be believed. */
  const remove = Array.isArray(body.remove) ? body.remove.slice(0, 500) : [];
  for (const id of remove) {
    stmts.push(env.DB.prepare('DELETE FROM catalog WHERE shop = ?1 AND id = ?2')
      .bind(shop, str(id, 60)));
  }

  if (!stmts.length) return ok({ saved: 0 });
  for (let i = 0; i < stmts.length; i += 100) await env.DB.batch(stmts.slice(i, i + 100));
  return ok({ saved: stmts.length });
}


/* ---------------------------------------------------------------------
   POST /api/staff/catalog/import   {csv, retireStarter}

   The owner's real inventory, replacing the starter catalogue. The 259
   researched products in the app were always placeholders and CLAUDE.md
   always said so; this is the call that makes that true.

   `retireStarter` hides every seeded product the spreadsheet did not
   mention. Hides, not deletes — an owner who imports the wrong file at
   four in the afternoon can import the right one and get their shelf
   back, and a deleted row would have taken the order history's only
   record of what a thing used to be called with it.

   Nothing is silently dropped. A row without a price does not become a
   product priced at nothing; it comes back in `skipped` with its line
   number, because a shop that uploads 400 products and sees 380 is
   entitled to know which twenty and why.
   --------------------------------------------------------------------- */
export async function importCatalogue(env, shop, body) {
  const read = readCatalogue(body.csv || '');
  if (read.error) return fail(400, 'bad file', read.error);
  if (!read.items.length) {
    return fail(400, 'nothing',
      'Not one row in that file became a product. ' +
      (read.skipped.length ? 'The first problem was on line ' + read.skipped[0].line +
        ': ' + read.skipped[0].why + '.' : ''));
  }

  const stamp = nowIso();
  const stmts = [];
  const bad = [];

  for (const it of read.items) {
    const c = cleanPatch(it);
    if (!c || c.error) {
      bad.push({ id: it.id, name: it.name,
                 why: c && c.error === 'photo' ? 'the photo was sent as a picture, not a path'
                    : c && c.error === 'path'  ? 'that photo is not one this shop serves'
                    : 'the price is not a number the register could ring' });
      continue;
    }
    /* custom = 1: these are the shop's own products, not edits to ours. They
       arrive on customer phones through S.custom, which the app already
       merges into the shelf and already reads photos from. */
    stmts.push(env.DB.prepare(
      `INSERT INTO catalog (shop, id, patch, custom, edited, updated)
       VALUES (?1, ?2, ?3, 1, 1, ?4)
       ON CONFLICT (shop, id) DO UPDATE SET patch = ?3, custom = 1, edited = 1, updated = ?4`
    ).bind(shop, it.id, JSON.stringify(c.value), stamp));
  }

  let retired = 0;
  if (body.retireStarter) {
    const keep = new Set(read.items.map(i => i.id));
    const rows = await env.DB
      .prepare('SELECT id, patch FROM catalog WHERE shop = ?1 AND custom = 0').bind(shop).all();
    for (const r of (rows.results || [])) {
      if (keep.has(r.id)) continue;
      let patch = {};
      try { patch = JSON.parse(r.patch); } catch { patch = {}; }
      patch.hidden = true;
      stmts.push(env.DB.prepare(
        'UPDATE catalog SET patch = ?3, edited = 1, updated = ?4 WHERE shop = ?1 AND id = ?2'
      ).bind(shop, r.id, JSON.stringify(patch), stamp));
      retired++;
    }
    if (!rows.results || !rows.results.length) {
      /* Nothing to retire means the shelf was never seeded, and the starter
         catalogue is still living inside the app where this service cannot
         reach it. Saying so is better than reporting a clean sweep. */
      return fail(409, 'not seeded',
        'The starter catalogue has not been seeded, so there is nothing here to retire. ' +
        'Open Staff then Menu once on the shop address, then import again.');
    }
  }

  for (let i = 0; i < stmts.length; i += 100) await env.DB.batch(stmts.slice(i, i + 100));

  return ok({
    imported: read.items.length - bad.length,
    retired,
    /* Both lists, in full. A summary that hides the rejects is how a shop
       finds out about a missing product from a customer. */
    skipped: read.skipped.concat(bad).slice(0, 200),
    skippedCount: read.skipped.length + bad.length
  });
}
