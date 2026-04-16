'use client';

import { useState, type FormEvent } from 'react';
import { ArrowRight, CheckCircle2, Shield } from 'lucide-react';

type Status = 'idle' | 'submitting' | 'success' | 'error';

const ERROR_MESSAGES: Record<string, string> = {
  INVALID_EMAIL: 'Please enter a valid email address.',
  RATE_LIMITED: 'Too many attempts. Try again in an hour.',
  INTERNAL: 'Something went wrong. Please try again.',
};

export function WaitlistCTA() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState<string>('');

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus('submitting');
    setMessage('');
    try {
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const json = (await res.json()) as
        | { success: true; message: string }
        | { success: false; error: string };

      if (json.success) {
        setStatus('success');
        setMessage(json.message);
      } else {
        setStatus('error');
        setMessage(ERROR_MESSAGES[json.error] ?? ERROR_MESSAGES.INTERNAL);
      }
    } catch {
      setStatus('error');
      setMessage('Network error. Check your connection and try again.');
    }
  }

  return (
    <section aria-labelledby="waitlist-heading" className="py-24">
      <div className="mx-auto max-w-3xl px-6">
        <div className="rounded-2xl border border-primary/20 bg-amber-50/50 dark:bg-amber-900/10 px-8 py-12 text-center shadow-sm">
          <div className="flex items-center justify-center gap-2 text-primary">
            <Shield className="size-4" />
            <span className="text-xs font-bold uppercase tracking-widest">Priority Access</span>
          </div>
          <h2
            id="waitlist-heading"
            className="mt-3 text-2xl font-bold tracking-tight text-foreground sm:text-3xl"
          >
            Ready to protect your business?
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Join the Tampa Bay priority list. No credit card, no commitment.
          </p>

          {status === 'success' ? (
            <div
              role="status"
              className="mt-8 flex items-center justify-center gap-2 rounded-lg border border-primary/30 bg-card px-6 py-4 text-sm font-medium text-foreground"
            >
              <CheckCircle2 className="size-5 text-primary" />
              <span>{message}</span>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="mt-8 flex flex-col items-center gap-3">
              <div className="flex w-full max-w-md flex-col gap-2 sm:flex-row">
                <input
                  type="email"
                  required
                  name="email"
                  autoComplete="email"
                  inputMode="email"
                  placeholder="you@business.com"
                  value={email}
                  disabled={status === 'submitting'}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1 rounded-md border border-border bg-card px-4 py-3 text-sm text-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/40 disabled:opacity-50"
                  aria-invalid={status === 'error'}
                  aria-describedby={status === 'error' ? 'waitlist-error' : undefined}
                />
                <button
                  type="submit"
                  disabled={status === 'submitting' || email.length === 0}
                  className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 disabled:opacity-60"
                >
                  {status === 'submitting' ? 'Joining…' : 'Join waitlist'}
                  {status !== 'submitting' && <ArrowRight className="size-4" />}
                </button>
              </div>
              {status === 'error' && (
                <p id="waitlist-error" role="alert" className="text-sm text-destructive">
                  {message}
                </p>
              )}
            </form>
          )}
        </div>
      </div>
    </section>
  );
}
