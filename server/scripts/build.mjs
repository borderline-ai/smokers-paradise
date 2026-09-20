/* The app is a 12MB single file with no build step, and that stays true. This
   is not a build, it is a copy: the one output of stages/ is put where the
   Worker's asset handler can find it.
   Kept as a script rather than a `cp` in package.json so it says why, and so
   it fails loudly when the file it expects is not there. */
import { copyFileSync, mkdirSync, statSync } from 'node:fs';
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
