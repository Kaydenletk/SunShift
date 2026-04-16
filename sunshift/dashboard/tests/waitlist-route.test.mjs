import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

process.env.WAITLIST_FILE = path.join(mkdtempSync(path.join(tmpdir(), 'wl-')), 'waitlist.json');

const { POST } = await import('../src/app/api/waitlist/route.ts');

function req(body, ip = '1.2.3.4') {
  return new Request('http://localhost/api/waitlist', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-forwarded-for': ip },
    body: typeof body === 'string' ? body : JSON.stringify(body),
  });
}

test('POST with valid email succeeds', async () => {
  const res = await POST(req({ email: 'new.user@example.com' }, '10.0.0.1'));
  assert.equal(res.status, 200);
  const json = await res.json();
  assert.equal(json.success, true);
});

test('POST with invalid email returns 400 INVALID_EMAIL', async () => {
  const res = await POST(req({ email: 'nope' }, '10.0.0.2'));
  assert.equal(res.status, 400);
  const json = await res.json();
  assert.equal(json.success, false);
  assert.equal(json.error, 'INVALID_EMAIL');
});

test('POST with duplicate email returns success with duplicate copy', async () => {
  await POST(req({ email: 'dupe@example.com' }, '10.0.0.3'));
  const res = await POST(req({ email: 'DUPE@example.com' }, '10.0.0.3'));
  assert.equal(res.status, 200);
  const json = await res.json();
  assert.equal(json.success, true);
  assert.match(json.message, /already on the list/i);
});

test('POST 6 times from same IP — 6th is RATE_LIMITED', async () => {
  const ip = '10.0.0.99';
  for (let i = 0; i < 5; i++) {
    await POST(req({ email: `user${i}@example.com` }, ip));
  }
  const res = await POST(req({ email: 'blocked@example.com' }, ip));
  assert.equal(res.status, 429);
  const json = await res.json();
  assert.equal(json.error, 'RATE_LIMITED');
});

test('POST with malformed JSON returns 400 INVALID_EMAIL', async () => {
  const res = await POST(req('{ not json', '10.0.0.4'));
  assert.equal(res.status, 400);
  const json = await res.json();
  assert.equal(json.error, 'INVALID_EMAIL');
});
