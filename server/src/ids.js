/* =====================================================================
   IDENTIFIERS, AND WHICH OF THEM ARE SECRETS.

   Two things in this system look alike and are not alike at all.

   THE MEMBER CODE is public. It is derived from the phone number so it is
   stable, it is five digits so it can be read across a counter and typed
   without asking twice, and that makes it guessable — a hundred thousand of
   them exist and a script could walk the lot in an afternoon. It is a name,
   not a key. Nothing is granted by holding one.

   THE MEMBER TOKEN is a secret. 160 bits from the platform's CSPRNG, handed
   to the phone that made the join and to nobody else. It is what lets a phone
   read its own card.

   Everything in this file exists to keep those two apart.
   ===================================================================== */

/* Matches codeFor() in app/index.html exactly, and must keep matching it: a
   phone that joined offline computed its own code locally and is showing it
   on a card right now. If the server disagreed, the counter would type what
   is on the screen and find nobody. */
export function codeFor(phone) {
  const d = String(phone || '').replace(/\D/g, '');
  let h = 7;
  for (let i = 0; i < d.length; i++) h = (h * 31 + d.charCodeAt(i)) % 100000;
  return 'SP' + String(h).padStart(5, '0');
}

/* A hundred thousand codes and a hash means two different phone numbers
   collide long before the shop has a hundred thousand members — by the
   birthday bound, somewhere around four hundred. The client cannot know that
   has happened; only the table can. So the server is the one that decides,
   and it decides by walking forward until it finds a free code.
   The phone is told what it actually got and shows that. */
export function codeVariants(phone, max = 64) {
  const base = codeFor(phone);
  const n = parseInt(base.slice(2), 10);
  const out = [];
  for (let i = 0; i < max; i++) out.push('SP' + String((n + i) % 100000).padStart(5, '0'));
  return out;
}

const HEX = '0123456789abcdef';
function randomHex(bytes) {
  const b = new Uint8Array(bytes);
  crypto.getRandomValues(b);
  let s = '';
  for (let i = 0; i < b.length; i++) s += HEX[b[i] >> 4] + HEX[b[i] & 15];
  return s;
}

export const memberToken  = () => 'mt_' + randomHex(20);
export const sessionId    = () => 'ss_' + randomHex(20);

/* Constant time, because the staff PIN is compared with it. A comparison that
   returns early on the first wrong digit tells an attacker how many digits
   were right, which turns ten thousand guesses into forty. */
export function sameSecret(a, b) {
  const x = String(a == null ? '' : a);
  const y = String(b == null ? '' : b);
  let diff = x.length ^ y.length;
  const n = Math.max(x.length, y.length);
  for (let i = 0; i < n; i++) diff |= (x.charCodeAt(i) || 0) ^ (y.charCodeAt(i) || 0);
  return diff === 0;
}
