# Sunshift Landing Page Refactor — Design

**Date:** 2026-04-16
**Status:** Approved (brainstorming)
**Owner:** kaydenletk

> Note: `docs/superpowers/` is gitignored in this repo, so this spec lives at `docs/specs/` to follow the project's existing `docs/adr/` convention and remain in git history.

---

## 1. Goals

Three problems in one pass on `sunshift/dashboard/src/components/blocks/hero-section-1.tsx` (817 lines, one file):

1. **Broken UX on feature/architecture cards.** Card bodies are full-card `<Link>` elements pointing to external GitHub paths. If the repo resolves at all, users are pulled off the landing page; if it 404s (case/visibility/path issues), the card silently breaks.
2. **Monolithic file.** One 817-line component violates the project rule (200-400 typical, 800 max from `~/.claude/rules/common/coding-style.md`).
3. **No real lead capture.** Both "Start Free Trial" CTAs navigate to `/dashboard`. There's no email collection — no way to build a waitlist or measure intent.

## 2. Non-goals

- No redesign of visual style, palette, or copy.
- No refactor of the `/dashboard` page, scheduler components, or backend.
- No auth, no billing, no real email delivery (waitlist only).
- No framework migration or state-library addition.

## 3. Architecture

### 3.1 File layout (after refactor)

```
sunshift/dashboard/src/
├── app/
│   ├── page.tsx                        # composes landing sections
│   └── api/
│       └── waitlist/
│           └── route.ts                # POST /api/waitlist (new)
├── components/
│   └── landing/                        # new directory
│       ├── constants.ts                # menuItems, features, storyMoments, adrLinks, trustItems, riskStats, techBadges
│       ├── LandingHeader.tsx           # fixed nav + mobile menu
│       ├── HeroSection.tsx             # headline, subhead, CTA, hero image
│       ├── RealityCheckSection.tsx     # 3 Florida risk stats
│       ├── FeaturesSection.tsx         # 3 pillars, 6 capability cards
│       ├── ArchitectureSection.tsx     # geographic callout, 3 story moments, trust strip, ADR links
│       ├── PricingSection.tsx          # 2 tier cards (Starter, Business)
│       ├── WaitlistCTA.tsx             # NEW: email capture band
│       ├── DocsSection.tsx             # terminal mockup + dashboard/repo buttons
│       └── LandingFooter.tsx
└── lib/
    └── waitlist-storage.ts             # JSON read/write + in-memory rate limit map

data/
└── waitlist.json                       # created on first signup, gitignored
```

`sunshift/dashboard/src/components/blocks/hero-section-1.tsx` is deleted at the end of the refactor. `src/app/page.tsx` imports directly from `@/components/landing/*`.

### 3.2 Component responsibilities

Each component is a server component unless it needs browser state.

| Component | Client? | Why |
|---|---|---|
| `LandingHeader` | client | `useState` for mobile menu open, scroll listener |
| `HeroSection` | server | pure markup + `AnimatedGroup` (already client-isolated) |
| `RealityCheckSection` | server | pure markup |
| `FeaturesSection` | server | pure markup, cards render `<div>` not `<Link>` (see §3.3) |
| `ArchitectureSection` | server | pure markup |
| `PricingSection` | server | pure markup |
| `WaitlistCTA` | client | form state, submit handler |
| `DocsSection` | server | pure markup |
| `LandingFooter` | server | pure markup |

### 3.3 Card link strategy (the "doesn't work" fix)

Current shape:
```tsx
<Link href={feature.href} target="_blank">...entire card markup...</Link>
```

New shape:
```tsx
<article className="card">
  {/* icon, title, description */}
  <a href={feature.href} target="_blank" rel="noreferrer" className="secondary-link">
    View source <ArrowRight />
  </a>
</article>
```

- Card body no longer navigates. The only link is a small explicit "View source →" at the bottom.
- If the GitHub URL 404s, only the small link breaks — the card's value (title + description) still lands.
- Card gets a subtle hover treatment to show it is interactive content even without a body-wide link.
- All existing GitHub URLs are preserved but normalized to the actual repo casing: `https://github.com/Kaydenletk/SunShift` (matches the remote) instead of lowercased `kaydenletk/sunshift`. A single `REPO_URL` constant in `constants.ts` is used everywhere.

### 3.4 Waitlist CTA band

Placement: full-width `<section>` inserted between `PricingSection` and `DocsSection` in `page.tsx`.

Layout:
```
┌─────────────────────────────────────────────────────┐
│  Ready to protect your business?                    │
│  Join the Tampa Bay priority list — no credit card. │
│                                                     │
│  [ you@work-email.com       ] [ Join waitlist → ]  │
│                                                     │
│  After submit: green checkmark + "You're in.       │
│  We'll reach out when Business tier opens."         │
└─────────────────────────────────────────────────────┘
```

Interaction states:
- **idle** — input + button active
- **submitting** — button shows spinner, input disabled
- **success** — form replaced by success message (persists for session)
- **error** — message below input, input stays focused, button re-enabled

Validation (client + server, server is authoritative):
- Email matches RFC-ish regex via Zod `z.string().email()`
- Not a disposable domain (optional — skipped for v1, noted as follow-up)

### 3.5 API route `/api/waitlist`

`POST /api/waitlist`

Request body:
```json
{ "email": "user@example.com" }
```

Response (success):
```json
{ "success": true, "message": "You're on the list." }
```

Response (error):
```json
{ "success": false, "error": "INVALID_EMAIL" | "DUPLICATE" | "RATE_LIMITED" | "INTERNAL" }
```

Behavior:
1. Parse JSON body. Fail 400 with `INVALID_EMAIL` if parse fails or Zod schema fails.
2. Check rate limit: in-memory `Map<ip, {count, resetAt}>`. 5 requests per hour per IP. Over limit → 429 `RATE_LIMITED`.
3. Read `data/waitlist.json` (create if missing). If email already present (case-insensitive), return 200 with `DUPLICATE` — idempotent, friendly.
4. Append `{ email, submittedAt, ip }` to the array, write file atomically (write to `.tmp` then rename).
5. Return 200 success.

Error shape is discriminated union — UI maps each code to a user-facing message.

### 3.6 `data/waitlist.json` storage

- Lives at repo root `data/waitlist.json` (not inside `dashboard/` — keeps it out of the build output).
- Added to `.gitignore`.
- File shape: `{ "entries": [{ email, submittedAt, ip }, ...] }`.
- `src/lib/waitlist-storage.ts` exports `loadWaitlist()` / `appendToWaitlist(entry)` / `hasEmail(email)`. Uses `node:fs/promises`. Atomic write via `write → rename`.
- Concurrency: Next.js API routes on the same process serialize naturally for file I/O within one request, but concurrent requests can race. Good enough for a portfolio; documented as a known limitation with a migration path (Supabase / Postgres) in the module header comment.

## 4. Data flow (waitlist)

```
User types email
  → WaitlistCTA useState(email, status)
  → onSubmit → fetch('/api/waitlist', {method: POST, body})
  → route.ts
    → Zod validate
    → rate-limit check (in-memory Map)
    → waitlist-storage.appendToWaitlist
    → respond {success, message} or {success:false, error}
  → WaitlistCTA maps response to UI state (success | error toast)
```

## 5. Error handling

| Layer | Failure | User sees |
|---|---|---|
| Client | network down | "Connection lost. Try again." (retry button) |
| Client | 400 INVALID_EMAIL | "Please enter a valid email address." (under input) |
| Client | 429 RATE_LIMITED | "Too many attempts. Try again in an hour." |
| Client | 200 DUPLICATE | "You're already on the list. We'll be in touch." (green, not red) |
| Server | file I/O failure | Logs real error server-side, returns 500 `INTERNAL` to client |
| Server | malformed JSON | Zod fails → 400 `INVALID_EMAIL` |

No stack traces or filesystem paths leak to the client.

## 6. Testing

### Unit
- `waitlist-storage.test.ts` — append creates file, duplicates not added twice (case-insensitive), sequential appends preserve all entries, malformed JSON on disk surfaces a clear error.
- Zod schema tests — valid, invalid format, missing field, extra fields stripped.

> Note: We do not claim concurrent-write safety. §3.6 flags this as a known limitation with a documented migration path. Tests exercise the single-caller happy path.

### Integration
- `route.test.ts` — POST valid, POST invalid email (400), POST duplicate (200 with DUPLICATE code), POST 6 times from same IP (6th returns 429), POST malformed JSON (400).

### Visual / manual
- Playwright screenshot landing page at 320 / 768 / 1440 widths (per `~/.claude/rules/web/testing.md`).
- Manual click: every external link in cards, every anchor nav link, mobile menu open/close, form submit happy path + error paths.

### Coverage target
- 80% minimum per project rule. Focus on route.ts + storage.ts + Zod schema (pure logic). UI components covered by visual regression.

## 7. Rollout

This is a net-positive refactor on a pre-launch landing page. No feature flag, no migration, no DB. One PR:

1. Create `constants.ts` + new section components.
2. Wire `page.tsx` to use new components.
3. Delete `hero-section-1.tsx`.
4. Add API route + storage helper + Zod schema.
5. Wire `WaitlistCTA` to API.
6. Add tests.
7. Run build, type-check, visual regression. Open PR.

Visual parity is the main regression risk — screenshot comparison is the gate.

## 8. Open questions (non-blocking)

- Do you want the waitlist submissions emailed to you? (Out of scope v1 — `data/waitlist.json` is the source of truth. Adding Resend later is a 30-line change.)
- Should duplicate submissions surface the original signup date? (Currently: no, they just get a friendly "you're already on the list.")
- Is there an analytics target for the waitlist button? (Out of scope.)

## 9. File count and line budget

| File | Expected LOC |
|---|---|
| `constants.ts` | ~180 (data-only) |
| `LandingHeader.tsx` | ~80 |
| `HeroSection.tsx` | ~100 |
| `RealityCheckSection.tsx` | ~40 |
| `FeaturesSection.tsx` | ~140 |
| `ArchitectureSection.tsx` | ~180 |
| `PricingSection.tsx` | ~100 |
| `WaitlistCTA.tsx` | ~120 (form logic + states) |
| `DocsSection.tsx` | ~60 |
| `LandingFooter.tsx` | ~25 |
| `app/page.tsx` | ~20 |
| `app/api/waitlist/route.ts` | ~80 |
| `lib/waitlist-storage.ts` | ~80 |
| **Total** | **~1,205** LOC across 13 focused files vs. 817 LOC in one |

Each file well under the 800-line max and most under the 200-line "ideal" band.
