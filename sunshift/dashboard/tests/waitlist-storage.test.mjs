import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const { waitlistEntrySchema } = await import('../src/lib/waitlist-schema.ts');
const storage = await import('../src/lib/waitlist-storage.ts');

function makeTempDir() {
  return mkdtempSync(path.join(tmpdir(), 'waitlist-test-'));
}

test('schema accepts a valid email', () => {
  const result = waitlistEntrySchema.safeParse({ email: 'user@example.com' });
  assert.equal(result.success, true);
});

test('schema rejects a malformed email', () => {
  const result = waitlistEntrySchema.safeParse({ email: 'not-an-email' });
  assert.equal(result.success, false);
});

test('schema strips unknown keys', () => {
  const result = waitlistEntrySchema.safeParse({ email: 'a@b.co', extra: 'ignored' });
  assert.equal(result.success, true);
  if (result.success) assert.deepEqual(Object.keys(result.data), ['email']);
});

test('schema lowercases and trims email', () => {
  const result = waitlistEntrySchema.safeParse({ email: '  User@Example.COM  ' });
  assert.equal(result.success, true);
  if (result.success) assert.equal(result.data.email, 'user@example.com');
});

test('loadWaitlist returns empty on missing file', async () => {
  const dir = makeTempDir();
  try {
    const data = await storage.loadWaitlist(path.join(dir, 'waitlist.json'));
    assert.deepEqual(data, { entries: [] });
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('appendToWaitlist creates file and persists entry', async () => {
  const dir = makeTempDir();
  const file = path.join(dir, 'waitlist.json');
  try {
    await storage.appendToWaitlist(file, { email: 'a@b.co', ip: '127.0.0.1' });
    const loaded = await storage.loadWaitlist(file);
    assert.equal(loaded.entries.length, 1);
    assert.equal(loaded.entries[0].email, 'a@b.co');
    assert.ok(loaded.entries[0].submittedAt);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('hasEmail is case-insensitive', () => {
  const waitlist = {
    entries: [{ email: 'User@Example.COM', submittedAt: '2026-01-01T00:00:00Z', ip: '' }],
  };
  assert.equal(storage.hasEmail(waitlist, 'user@example.com'), true);
  assert.equal(storage.hasEmail(waitlist, 'USER@EXAMPLE.COM'), true);
  assert.equal(storage.hasEmail(waitlist, 'other@example.com'), false);
});

test('loadWaitlist surfaces a clear error on malformed JSON', async () => {
  const dir = makeTempDir();
  const file = path.join(dir, 'waitlist.json');
  writeFileSync(file, '{ not valid json');
  try {
    await assert.rejects(storage.loadWaitlist(file), /malformed/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
