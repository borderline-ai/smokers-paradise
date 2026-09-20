/* =====================================================================
   THE SHOP, ON THIS MACHINE.

   The same Worker handler, the same schema, the same D1 shim the tests use,
   behind a plain node:http server. No wrangler, no npm install, no Cloudflare
   account, no network.

   It exists for three reasons and they are all the same reason — that a thing
   you cannot run is a thing you cannot check:

     - the owner can see the real product, with a real counter and a real
       member list, before anybody signs anything;
     - test/live_backend.py drives a real browser against it, which is the only
       way to prove the headline fix end to end rather than in a unit;
     - a developer can work on the backend on a plane.

   It is not the production server. Production is `npm run deploy`. The
   difference is D1 versus a file on this disk, and nothing else.

       node scripts/serve.mjs [port]
   =====================================================================*/

import { createServer } from 'node:http';
import { Readable } from 'node:stream';
import { dirname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync, statSync } from 'node:fs';

import worker from '../src/index.js';
import { makeD1 } from '../test/d1.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const PORT = Number(process.argv[2] || process.env.PORT || 8787);
const PUBLIC = join(ROOT, 'public');

if (!existsSync(join(PUBLIC, 'index.html'))) {
  console.error('No server/public/index.html. Run: npm run build');
  process.exit(1);
}

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json', '.png': 'image/png',
  '.webp': 'image/webp', '.svg': 'image/svg+xml', '.ico': 'image/x-icon'
};

const env = {
  DB: makeD1(join(ROOT, 'schema.sql'), process.env.SP_DB || ':memory:'),
  SHOP: process.env.SHOP || 'smokers-paradise',
  STAFF_PIN: process.env.STAFF_PIN || '7413',
  ASSETS: {
    async fetch(request) {
      const p = normalize(decodeURIComponent(new URL(request.url).pathname));
      /* Never let a path climb out of public/. A dev server is still a server
         and somebody will eventually run this on a machine that matters. */
      if (p.includes('..')) return new Response('', { status: 404 });
      const file = join(PUBLIC, p);
      if (!file.startsWith(PUBLIC) || !existsSync(file) || !statSync(file).isFile()) {
        return new Response('', { status: 404 });
      }
      const ext = file.slice(file.lastIndexOf('.'));
      return new Response(readFileSync(file),
        { status: 200, headers: { 'content-type': TYPES[ext] || 'application/octet-stream' } });
    }
  }
};

const server = createServer(async (req, res) => {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const body = chunks.length ? Buffer.concat(chunks) : undefined;

  const url = 'http://' + (req.headers.host || ('127.0.0.1:' + PORT)) + req.url;
  const request = new Request(url, {
    method: req.method,
    headers: req.headers,
    body: (req.method === 'GET' || req.method === 'HEAD') ? undefined : body
  });

  let out;
  try {
    out = await worker.fetch(request, env, { waitUntil: p => { Promise.resolve(p).catch(() => {}); },
                                             passThroughOnException() {} });
  } catch (e) {
    console.error(e);
    out = new Response(JSON.stringify({ ok: false, reason: 'server' }),
      { status: 500, headers: { 'content-type': 'application/json' } });
  }

  const headers = {};
  for (const [k, v] of out.headers) {
    if (k.toLowerCase() === 'set-cookie') (headers['set-cookie'] ||= []).push(v);
    else headers[k] = v;
  }
  res.writeHead(out.status, headers);
  if (out.body) Readable.fromWeb(out.body).pipe(res); else res.end();
});

server.listen(PORT, () => {
  console.log('Smokers Paradise, running locally.');
  console.log('  the shop     http://127.0.0.1:' + PORT + '/');
  console.log('  the counter  http://127.0.0.1:' + PORT + '/counter   PIN ' + env.STAFF_PIN);
  console.log(process.env.SP_DB
    ? '  data         ' + process.env.SP_DB
    : '  data         in memory, gone when this stops. Set SP_DB=shop.db to keep it.');
});
