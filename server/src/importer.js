/* =====================================================================
   THE OWNER'S REAL LIST.

   The 259 products in the app are a starter catalogue — researched, real
   brands, plausible prices, and every one of them a placeholder. CLAUDE.md
   has said so from the beginning: "The owner's real list replaces it."

   This is the replacing. A shop's inventory arrives as a spreadsheet, so
   that is what this reads, and it reads it the way a spreadsheet actually
   turns up rather than the way one would like it to:

     - the header row says "Item" or "Product" or "Description", not "name"
     - prices say "$12.99" and sometimes "12.99 ea"
     - there is a blank row in the middle where somebody hit enter
     - the same product appears twice because two people maintained the file

   None of that is an error worth stopping for. What IS worth stopping for is
   a row that would put a wrong price in front of a customer, and those are
   collected and reported rather than guessed at. Rule 3 in CLAUDE.md: if a
   number is not verified it does not ship.
   ===================================================================== */

import { str, money } from './http.js';

/* ---------------------------------------------------------------------
   CSV, properly. Quoted fields, embedded commas, embedded newlines,
   doubled quotes. Excel writes all four and a split(',') meets all four
   within about a hundred rows of a real shop's file.
   --------------------------------------------------------------------- */
export function parseCsv(text) {
  const rows = [];
  let row = [], field = '', quoted = false, i = 0;
  const s = String(text || '').replace(/^﻿/, '');   /* Excel's BOM */

  while (i < s.length) {
    const c = s[i];
    if (quoted) {
      if (c === '"') {
        if (s[i + 1] === '"') { field += '"'; i += 2; continue; }
        quoted = false; i++; continue;
      }
      field += c; i++; continue;
    }
    if (c === '"') { quoted = true; i++; continue; }
    if (c === ',') { row.push(field); field = ''; i++; continue; }
    if (c === '\r') { i++; continue; }
    if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; i++; continue; }
    field += c; i++;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  return rows;
}

/* Header matching that survives "Retail Price ", "PRICE", "price_usd".
   The first name in each list is what the rest of this file calls it. */
const COLUMNS = {
  id:        ['id', 'sku', 'itemid', 'itemnumber', 'productid', 'upc'],
  name:      ['name', 'product', 'productname', 'item', 'itemname', 'title', 'description'],
  brand:     ['brand', 'manufacturer', 'vendor', 'make', 'supplier'],
  price:     ['price', 'retail', 'retailprice', 'priceusd', 'msrp', 'sellprice', 'unitprice'],
  cat:       ['cat', 'category', 'type', 'department', 'group'],
  stock:     ['stock', 'qty', 'quantity', 'onhand', 'instock', 'count'],
  photo:     ['photo', 'image', 'picture', 'img', 'imagefile', 'photofile'],
  published: ['published', 'active', 'visible', 'live', 'enabled']
};

const norm = h => String(h || '').toLowerCase().replace(/[^a-z0-9]/g, '');

export function mapHeader(header) {
  const map = {};
  header.forEach((h, i) => {
    const n = norm(h);
    for (const key of Object.keys(COLUMNS)) {
      if (map[key] === undefined && COLUMNS[key].includes(n)) { map[key] = i; return; }
    }
  });
  return map;
}

/* "$12.99", "12.99 ea", "1,299.00", "12,99" all mean a number. An empty cell
   does not mean zero — it means nobody said, and a product priced at zero is
   a product a customer expects free. Those rows are refused. */
function readPrice(raw) {
  const t = str(raw, 40);
  if (!t) return null;
  let v = t.replace(/[^0-9.,-]/g, '');
  if (/,\d{2}$/.test(v) && !/\./.test(v)) v = v.replace(',', '.');   /* 12,99 */
  v = v.replace(/,/g, '');
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? money(n) : null;
}

const slug = s => String(s || '').toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 44);

const TRUTHY = new Set(['1', 'y', 'yes', 'true', 'active', 'live', 'published', 'visible']);
const FALSY  = new Set(['0', 'n', 'no', 'false', 'inactive', 'hidden', 'draft']);

/* ---------------------------------------------------------------------
   One spreadsheet in, a list of products and a list of complaints out.
   Nothing is silently dropped: every row that does not become a product
   comes back with the row number and the reason, because a shop that
   uploads 400 products and gets 380 is entitled to know which twenty.
   --------------------------------------------------------------------- */
export function readCatalogue(text) {
  const rows = parseCsv(text).filter(r => r.some(c => str(c, 200) !== ''));
  if (!rows.length) return { items: [], skipped: [], error: 'That file has no rows in it.' };

  const map = mapHeader(rows[0]);
  if (map.name === undefined) {
    return { items: [], skipped: [],
      error: 'No product name column. The header needs one of: ' +
             COLUMNS.name.slice(0, 5).join(', ') + '.' };
  }
  if (map.price === undefined) {
    return { items: [], skipped: [],
      error: 'No price column. The header needs one of: ' +
             COLUMNS.price.slice(0, 4).join(', ') + '.' };
  }

  const cell = (r, k) => map[k] === undefined ? '' : str(r[map[k]], 200);
  const items = [], skipped = [], seen = new Map();

  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const line = i + 1;
    const name = cell(r, 'name');
    if (!name) { skipped.push({ line, why: 'no product name' }); continue; }

    const price = readPrice(map.price === undefined ? '' : r[map.price]);
    if (price === null) {
      /* The most important refusal in this file. A row with no price becomes
         a product priced at nothing, and the register is the final word but
         the screen is what the customer read before they walked in. */
      skipped.push({ line, name, why: 'no price the register could ring' });
      continue;
    }

    const brand = cell(r, 'brand');
    const id = cell(r, 'id') || ('shop-' + (slug(brand + ' ' + name) || 'item-' + line));

    if (seen.has(id)) {
      skipped.push({ line, name, why: 'same product as line ' + seen.get(id) });
      continue;
    }
    seen.set(id, line);

    const item = { id, name, price };
    if (brand) item.brand = brand;

    const cat = cell(r, 'cat');
    if (cat) item.cat = cat;

    const photo = cell(r, 'photo');
    if (photo) item.photo = /^(img\/|https:)/.test(photo) ? photo : 'img/' + photo;

    if (map.stock !== undefined) {
      const q = parseInt(String(r[map.stock]).replace(/[^0-9-]/g, ''), 10);
      /* A blank stock cell is "we do not count this", which is different from
         "we have none". Rule 3: never invent a stock number. */
      if (Number.isFinite(q) && q >= 0) item.stock = q;
    }

    if (map.published !== undefined) {
      const p = norm(r[map.published]);
      if (FALSY.has(p)) item.published = false;
      else if (TRUTHY.has(p)) item.published = true;
    }

    items.push(item);
  }

  return { items, skipped, error: '' };
}
