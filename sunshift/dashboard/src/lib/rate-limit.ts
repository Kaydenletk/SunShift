type Bucket = { count: number; resetAt: number };

export type RateLimiter = {
  check(key: string): { allowed: boolean; resetAt: number };
};

export function createRateLimiter(opts: { max: number; windowMs: number }): RateLimiter {
  const buckets = new Map<string, Bucket>();
  return {
    check(key) {
      const now = Date.now();
      const existing = buckets.get(key);
      if (!existing || existing.resetAt <= now) {
        const resetAt = now + opts.windowMs;
        buckets.set(key, { count: 1, resetAt });
        return { allowed: true, resetAt };
      }
      if (existing.count >= opts.max) {
        return { allowed: false, resetAt: existing.resetAt };
      }
      existing.count += 1;
      return { allowed: true, resetAt: existing.resetAt };
    },
  };
}
