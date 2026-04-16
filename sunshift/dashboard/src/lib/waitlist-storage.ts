import { promises as fs } from 'node:fs';
import path from 'node:path';

export type StoredEntry = {
  email: string;
  submittedAt: string;
  ip: string;
};

export type Waitlist = { entries: StoredEntry[] };

export async function loadWaitlist(filePath: string): Promise<Waitlist> {
  try {
    const raw = await fs.readFile(filePath, 'utf8');
    try {
      const parsed = JSON.parse(raw) as Waitlist;
      if (!parsed || !Array.isArray(parsed.entries)) {
        throw new Error('waitlist file is malformed: missing "entries" array');
      }
      return parsed;
    } catch (err) {
      if (err instanceof SyntaxError) {
        throw new Error('waitlist file is malformed: invalid JSON');
      }
      throw err;
    }
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
      return { entries: [] };
    }
    throw err;
  }
}

export async function appendToWaitlist(
  filePath: string,
  entry: { email: string; ip: string },
): Promise<void> {
  const current = await loadWaitlist(filePath);
  const next: Waitlist = {
    entries: [
      ...current.entries,
      { email: entry.email, ip: entry.ip, submittedAt: new Date().toISOString() },
    ],
  };
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  const tmp = `${filePath}.tmp`;
  await fs.writeFile(tmp, JSON.stringify(next, null, 2), 'utf8');
  await fs.rename(tmp, filePath);
}

export function hasEmail(waitlist: Waitlist, email: string): boolean {
  const target = email.trim().toLowerCase();
  return waitlist.entries.some((e) => e.email.trim().toLowerCase() === target);
}
