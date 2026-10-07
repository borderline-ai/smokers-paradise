/* =====================================================================
   GOHIGHLEVEL THROUGH ITS FRONT DOOR.

   The other way in is an inbound webhook, and it works, but GHL bills that
   trigger per execution. For one shop that is a few dollars a month. For an
   agency running this across every client it is a per-client charge paid
   forever, on every join, every reward, every bag marked ready.

   This writes the contact properly instead — real fields, not a payload
   somebody hand-maps — and then adds a tag. Workflows trigger on "Contact
   Tag", which is a standard trigger and costs nothing.

   It is the better integration regardless of price. The shop's people arrive
   in GHL as contacts with a name, an email, a phone and a birthday, which
   means segmentation works on day one: "everyone tagged sp-reward-ready who
   has not been in for thirty days" is a query rather than a project.

   WHY THE TAG IS REMOVED BEFORE IT IS ADDED. "Contact Tag" fires when a tag
   is ADDED. A member who earns a second reward already carries
   sp-reward-ready from the first, so adding it again changes nothing and no
   workflow runs. Removing it first makes every event a real add. The delete
   is allowed to fail — on the first event there is nothing to remove, and
   that is not a problem worth reporting.
   ===================================================================== */

import { str } from './http.js';

const API = 'https://services.leadconnectorhq.com';
const VERSION = '2021-07-28';

function headers(token) {
  return {
    'Authorization': 'Bearer ' + token,
    'Version': VERSION,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
}

/* The tag each event adds. One per event, prefixed so a shop using GHL for
   other things can see at a glance which tags this service owns. */
export const TAGS = {
  'member.joined':       'sp-member',
  'member.reward_ready': 'sp-reward-ready',
  'member.birthday':     'sp-birthday',
  'order.ready':         'sp-order-ready',
  'list.subscribed':     'sp-subscriber'
};

/* GHL wants a first name and either an email or a phone. An event carrying
   neither cannot become a contact, and saying so is better than sending a
   request that will be refused. */
function contactFrom(payload, locationId) {
  const email = str(payload.email, 160).toLowerCase();
  const phone = str(payload.phone, 20);
  if (!email && !phone) return null;

  const c = { locationId };
  if (payload.first) c.firstName = str(payload.first, 60);
  if (email) c.email = email;
  if (phone) c.phone = '+1' + phone.replace(/\D/g, '').slice(-10);
  c.source = 'Smokers Paradise app';

  /* Month and day, never a year — the app does not collect one and this must
     not be the place that invents it. GHL wants a date, so the year is a
     placeholder and the real information is the month and the day. */
  if (payload.birthday && /^\d{1,2}-\d{1,2}$/.test(payload.birthday)) {
    const [m, d] = payload.birthday.split('-');
    c.dateOfBirth = '1900-' + String(m).padStart(2, '0') + '-' + String(d).padStart(2, '0');
  }

  /* The member code is what the counter reads off a customer's screen, so it
     has to be visible in GHL for anybody doing support. */
  if (payload.code) c.customFields = [{ key: 'member_code', field_value: str(payload.code, 12) }];
  return c;
}

async function call(token, path, init) {
  const r = await fetch(API + path, Object.assign({ headers: headers(token) }, init));
  const text = await r.text();
  let body = null;
  try { body = text ? JSON.parse(text) : null; } catch { body = null; }
  return { ok: r.ok, status: r.status, body, text: text.slice(0, 300) };
}

/* Sends one event. Returns {ok, detail} — the detail is kept because the
   thing that goes wrong here is a scope or a token, and "it did not work" is
   not enough to fix either. */
export async function send(env, cfg, type, payload) {
  const token = env.GHL_TOKEN;
  const locationId = str(cfg.ghlLocationId, 60);
  if (!token) return { ok: false, detail: 'No GHL_TOKEN secret is set on this service.' };
  if (!locationId) return { ok: false, detail: 'No GHL location id is set in the shop config.' };

  const contact = contactFrom(payload, locationId);
  if (!contact) return { ok: false, detail: 'That event carries no email and no phone, so it cannot become a contact.' };

  const up = await call(token, '/contacts/upsert', { method: 'POST', body: JSON.stringify(contact) });
  if (!up.ok) {
    return { ok: false, detail: 'GHL refused the contact: HTTP ' + up.status + ' ' + up.text };
  }
  const id = up.body && (up.body.contact ? up.body.contact.id : up.body.id);
  if (!id) return { ok: false, detail: 'GHL accepted the contact but returned no id.' };

  const tag = TAGS[type];
  if (!tag) return { ok: true, detail: 'contact upserted, no tag for ' + type };

  /* Remove then add, so a second reward is a second trigger. The remove is
     expected to fail the first time and that is fine. */
  await call(token, '/contacts/' + id + '/tags',
    { method: 'DELETE', body: JSON.stringify({ tags: [tag] }) }).catch(() => {});
  const add = await call(token, '/contacts/' + id + '/tags',
    { method: 'POST', body: JSON.stringify({ tags: [tag] }) });
  if (!add.ok) {
    return { ok: false, detail: 'Contact saved but the tag failed: HTTP ' + add.status + ' ' + add.text };
  }
  return { ok: true, detail: 'contact ' + id + ' tagged ' + tag };
}
