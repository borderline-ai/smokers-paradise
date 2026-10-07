/* =====================================================================
   SOMEWHERE TO PUT A PHOTOGRAPH.

   Stage 172 took the shipped pictures out of the document and made them
   files, and the counter's own photo import was left behind: it still wrote
   base64 into one device's localStorage, where it was stranded. A photograph
   the owner takes on the shop's iPad reached nobody.

   This is the missing half. Same naming scheme as stage 172 — the file is
   called after the hash of its own bytes — which buys three things for free:
   identical uploads collapse to one object, a name can never refer to
   different bytes later, so it is safe to cache for a year, and replacing a
   picture produces a new name instead of a stale copy on somebody's phone.

   R2 in production, a directory on disk under `npm run serve`. The Worker
   reads both: a path is tried against the shipped assets first and then
   against the bucket, so `img/<hash>.webp` means the same thing whether the
   picture came from stages/ or from somebody's camera.

   WHAT IT WILL NOT ACCEPT. Only real image bytes, checked by reading the
   file's own magic numbers rather than by trusting what the browser called
   it. A content-type header is a claim by whoever is uploading.
   ===================================================================== */

import { ok, fail, str } from './http.js';

const MAX_BYTES = 4 * 1024 * 1024;

/* Magic numbers. A browser will happily label anything image/webp, and a
   shop's product page is not the place to find out it was wrong. */
function sniff(bytes) {
  const b = new Uint8Array(bytes);
  if (b.length < 12) return '';
  const ascii = (o, s) => [...s].every((c, i) => b[o + i] === c.charCodeAt(0));
  if (b[0] === 0xFF && b[1] === 0xD8 && b[2] === 0xFF) return '.jpg';
  if (ascii(1, 'PNG') && b[0] === 0x89) return '.png';
  if (ascii(0, 'RIFF') && ascii(8, 'WEBP')) return '.webp';
  if (ascii(0, 'GIF8')) return '.gif';
  return '';
}

async function sha16(bytes) {
  const d = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(d)].map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 16);
}

const TYPE = { '.jpg': 'image/jpeg', '.png': 'image/png',
               '.webp': 'image/webp', '.gif': 'image/gif' };

/* POST /api/staff/media   the raw bytes, with the real content-type
   Answers the path the app should store, which is the same shape stage 172
   writes into the document: `img/<hash>.<ext>` */
export async function upload(request, env) {
  if (!env.MEDIA) {
    return fail(503, 'no bucket',
      'No photo storage is configured on this service. Add an R2 bucket bound as MEDIA.');
  }
  const len = Number(request.headers.get('content-length') || 0);
  if (len > MAX_BYTES) {
    return fail(413, 'too big', 'That picture is over 4 MB. Shrink it and try again.');
  }

  const bytes = await request.arrayBuffer();
  if (!bytes.byteLength) return fail(400, 'empty', 'There was nothing in that upload.');
  if (bytes.byteLength > MAX_BYTES) {
    return fail(413, 'too big', 'That picture is over 4 MB. Shrink it and try again.');
  }

  const ext = sniff(bytes);
  if (!ext) {
    return fail(415, 'not an image',
      'That file is not a JPEG, PNG, WebP or GIF. Nothing was stored.');
  }

  const name = (await sha16(bytes)) + ext;
  const key = 'img/' + name;

  /* Already there means already there. The name IS the bytes, so re-uploading
     the same photograph is not a conflict and not a second object. */
  const have = await env.MEDIA.head(key);
  if (!have) {
    await env.MEDIA.put(key, bytes, { httpMetadata: { contentType: TYPE[ext] } });
  }
  return ok({ path: key, bytes: bytes.byteLength, reused: !!have });
}

/* Serves an uploaded picture. Only called when the shipped assets did not
   have it, so stages/ always wins over an upload with the same name — which
   cannot happen anyway, because the name is the hash. */
export async function serve(env, pathname) {
  if (!env.MEDIA) return null;
  const obj = await env.MEDIA.get(pathname.replace(/^\//, ''));
  if (!obj) return null;
  const h = new Headers();
  obj.writeHttpMetadata(h);
  h.set('etag', obj.httpEtag);
  h.set('cache-control', 'public, max-age=31536000, immutable');
  return new Response(obj.body, { status: 200, headers: h });
}

/* GET /api/staff/catalog — the whole shelf as the editor needs it, which is
   different from /api/catalog: it includes what is hidden, because hiding is
   the thing the owner came here to undo. */
export async function editorCatalog(env, shop, params) {
  const q = str(params.get('q') || '', 60).toLowerCase();
  const rows = await env.DB
    .prepare('SELECT id, patch, custom, edited, updated FROM catalog WHERE shop = ?1 LIMIT 3000')
    .bind(shop).all();

  const items = [];
  for (const r of (rows.results || [])) {
    let p; try { p = JSON.parse(r.patch); } catch { continue; }
    const hay = ((p.name || '') + ' ' + (p.brand || '')).toLowerCase();
    if (q && hay.indexOf(q) < 0) continue;
    items.push({
      id: r.id, name: p.name || '', brand: p.brand || '',
      price: typeof p.price === 'number' ? p.price : null,
      cat: p.cat || '', photo: p.photo || '', stock: 'stock' in p ? p.stock : null,
      hidden: !!p.hidden, custom: !!r.custom, edited: !!r.edited, updated: r.updated
    });
  }
  items.sort((a, b) => (a.brand || '').localeCompare(b.brand || '') ||
                       (a.name || '').localeCompare(b.name || ''));
  return ok({ items, total: items.length });
}
