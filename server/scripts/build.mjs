/* The app is a 12MB single file with no build step, and that stays true. This
   is not a build, it is a copy: the one output of stages/ is put where the
   Worker's asset handler can find it.
   Kept as a script rather than a `cp` in package.json so it says why, and so
   it fails loudly when the file it expects is not there. */
import { copyFileSync, mkdirSync, statSync, existsSync, readdirSync, rmSync,
         readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, '..', '..', 'app', 'index.html');
const outDir = join(here, '..', 'public');
const out = join(outDir, 'index.html');

let s;
try { s = statSync(src); }
catch {
  console.error('No app/index.html. That file is the output of stages/ — run the stages first.');
  process.exit(1);
}

/* Workers caps a single static asset at 25 MiB. The app is about 12MB today
   and grows every time a photograph is added, so this is worth saying out
   loud before a deploy fails halfway. */
const MiB = 1024 * 1024;
if (s.size > 25 * MiB) {
  console.error('app/index.html is %s MiB. A Workers static asset caps at 25 MiB.',
    (s.size / MiB).toFixed(1));
  console.error('Photographs have to move out of the HTML before this can deploy.');
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(src, out);
console.log('app/index.html -> server/public/index.html  (%s MiB)', (s.size / MiB).toFixed(1));

/* THE PHOTOGRAPHS. Since stage 172 they are files rather than 7 MB of base64
   inside the document. Named by the hash of their own bytes, so they are
   served immutable and a replaced photograph arrives under a new name instead
   of as a stale copy on somebody's phone. */
const imgSrc = join(here, '..', '..', 'app', 'img');
const imgOut = join(outDir, 'img');
let n = 0, bytes = 0;
if (existsSync(imgSrc)) {
  rmSync(imgOut, { recursive: true, force: true });
  mkdirSync(imgOut, { recursive: true });
  for (const f of readdirSync(imgSrc)) {
    const from = join(imgSrc, f);
    if (!statSync(from).isFile()) continue;
    copyFileSync(from, join(imgOut, f));
    bytes += statSync(from).size;
    n++;
  }
}
console.log('app/img -> server/public/img            (%d files, %s MiB)',
  n, (bytes / MiB).toFixed(1));
if (!n) {
  console.error('No app/img. Run stages/s172_media_out.py — without it every');
  console.error('product photograph on the deployed shop is a broken image.');
  process.exit(1);
}

/* THE SERVICE WORKER, stamped with the hash of the document it caches. The
   version is what makes a deploy evict the old shell; without it a browser
   would go on serving last week's app out of its own cache. */
const version = createHash('sha256').update(readFileSync(src)).digest('hex').slice(0, 12);
const sw = readFileSync(join(here, '..', 'assets', 'sw.js'), 'utf8')
  .replace('__VERSION__', version);
writeFileSync(join(outDir, 'sw.js'), sw);
console.log('assets/sw.js -> server/public/sw.js     (shell version %s)', version);
