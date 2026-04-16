import { NextResponse } from 'next/server';
import path from 'node:path';
import { waitlistEntrySchema } from '@/lib/waitlist-schema';
import {
  appendToWaitlist,
  hasEmail,
  loadWaitlist,
} from '@/lib/waitlist-storage';
import { createRateLimiter } from '@/lib/rate-limit';

const WAITLIST_FILE =
  process.env.WAITLIST_FILE ??
  path.join(process.cwd(), '..', '..', 'data', 'waitlist.json');

const limiter = createRateLimiter({ max: 5, windowMs: 60 * 60 * 1000 });

type ErrorCode = 'INVALID_EMAIL' | 'RATE_LIMITED' | 'INTERNAL';

function error(code: ErrorCode, status: number) {
  return NextResponse.json({ success: false, error: code }, { status });
}

function getClientIp(request: Request): string {
  const fwd = request.headers.get('x-forwarded-for');
  if (fwd) return fwd.split(',')[0]?.trim() ?? 'unknown';
  return request.headers.get('x-real-ip') ?? 'unknown';
}

export async function POST(request: Request) {
  const ip = getClientIp(request);
  const limit = limiter.check(ip);
  if (!limit.allowed) return error('RATE_LIMITED', 429);

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return error('INVALID_EMAIL', 400);
  }

  const parsed = waitlistEntrySchema.safeParse(body);
  if (!parsed.success) return error('INVALID_EMAIL', 400);

  try {
    const current = await loadWaitlist(WAITLIST_FILE);
    if (hasEmail(current, parsed.data.email)) {
      return NextResponse.json({
        success: true,
        message: "You're already on the list. We'll be in touch.",
      });
    }
    await appendToWaitlist(WAITLIST_FILE, { email: parsed.data.email, ip });
    return NextResponse.json({
      success: true,
      message: "You're on the list.",
    });
  } catch (err) {
    console.error('[waitlist] write failed:', err);
    return error('INTERNAL', 500);
  }
}
