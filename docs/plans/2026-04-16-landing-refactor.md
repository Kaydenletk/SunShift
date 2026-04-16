# Sunshift Landing Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the 817-line `hero-section-1.tsx` into focused section components, fix broken anchor links + GitHub card UX, and add a real `/api/waitlist` email capture.

**Architecture:** Nine section components under `src/components/landing/` with data-only `constants.ts`. New Next.js App Router API route `/api/waitlist` with Zod validation, in-memory rate limiting, and atomic JSON storage at `data/waitlist.json`. Cards get a secondary "View source →" link instead of a card-wide `<Link>` so broken external URLs degrade gracefully.

**Tech Stack:** Next.js 16 (App Router) · React 19 · TypeScript 5 · Tailwind 4 · Zod · `node:test` runner (no new test framework).

**Spec:** See `docs/specs/2026-04-16-landing-refactor-design.md`.

---

## Working Directory

All paths below are relative to the monorepo root:
```
/Users/khanhle/Desktop/Desktop - Khanh's MacBook Pro/💻 Dev-Projects/Sunshift
```

Dashboard source lives in `sunshift/dashboard/`. Run all `pnpm` commands from `sunshift/dashboard/` unless noted.

---

## Pre-flight check (before Task 0)

- [ ] Confirm `pnpm --version` returns a value
- [ ] Confirm `cd sunshift/dashboard && pnpm install` completes without errors
- [ ] Confirm `cd sunshift/dashboard && pnpm build` succeeds against the current (pre-refactor) code — this establishes a green baseline

---

### Task 0: Fix root-qualified anchors, normalize REPO_URL, add Zod

**Goal:** Make the existing `tests/landing-links.test.mjs` pass without any structural refactor. Two real bugs fixed: (1) bare `#features` anchors don't work from `/dashboard`, (2) repo URL case mismatch.

**Files:**
- Modify: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx` (menuItems constant + repoUrl constant)
- Modify: `sunshift/dashboard/package.json` (add `zod` dependency)
- Modify: `sunshift/dashboard/tests/landing-links.test.mjs` (no changes yet — confirm it passes)

**Acceptance Criteria:**
- [ ] All four menu items use root-qualified hashes (`/#features`, `/#architecture`, `/#pricing`, `/#docs`)
- [ ] `repoUrl` constant is `https://github.com/Kaydenletk/SunShift` (correct casing)
- [ ] `zod@^3.23` installed
- [ ] `pnpm build` succeeds
- [ ] `node --test tests/landing-links.test.mjs` passes (from `sunshift/dashboard/`)

**Verify:**
```bash
cd sunshift/dashboard && pnpm build && node --test tests/landing-links.test.mjs
```
Expected: build completes with no errors; test runner prints `# pass 3`.

**Steps:**

- [ ] **Step 1: Update menuItems in hero-section-1.tsx (lines 19–24)**

Change:
```tsx
const menuItems = [
  { label: 'Features', href: '#features' },
  { label: 'Architecture', href: '#architecture' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'Docs', href: '#docs' },
];
```
To:
```tsx
const menuItems = [
  { label: 'Features', href: '/#features' },
  { label: 'Architecture', href: '/#architecture' },
  { label: 'Pricing', href: '/#pricing' },
  { label: 'Docs', href: '/#docs' },
];
```

Also update the inline anchor on line ~317 (`<a href="#features"...>Now protecting Tampa Bay businesses`) and every `<a href="#pricing">` in the header CTA (~245) and mobile CTA (~282) to their root-qualified form. Use your editor's find-all for the full list — expected 6 occurrences.

- [ ] **Step 2: Fix repoUrl casing (line 16)**

Change:
```tsx
const repoUrl = 'https://github.com/kaydenletk/sunshift';
```
To:
```tsx
const repoUrl = 'https://github.com/Kaydenletk/SunShift';
```

- [ ] **Step 3: Install Zod**

Run: `cd sunshift/dashboard && pnpm add zod`
Expected: `package.json` `dependencies` gains `"zod": "^3.x"`.

- [ ] **Step 4: Run test + build to verify green**

Run:
```bash
cd sunshift/dashboard && node --test tests/landing-links.test.mjs
```
Expected output includes: `# tests 3` and `# pass 3`.

Then: `cd sunshift/dashboard && pnpm build`
Expected: `✓ Compiled successfully`.

- [ ] **Step 5: Commit**

```bash
git add sunshift/dashboard/src/components/blocks/hero-section-1.tsx sunshift/dashboard/package.json sunshift/dashboard/pnpm-lock.yaml
git commit -m "$(cat <<'EOF'
fix(landing): root-qualify nav anchors and normalize repo URL

Bare hash anchors (#features) fail when the user is on /dashboard
because there is no #features on that page. Root-qualifying them
(/#features) navigates to / and scrolls. Also corrects the GitHub
repo casing and installs zod in preparation for the waitlist API.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1: Extract `constants.ts` (landing data module)

**Goal:** Pull all landing-page data (navigation items, features, story moments, trust items, ADRs, risk stats, tech badges, URLs) into one data-only module. No JSX, no runtime logic — just typed exports.

**Files:**
- Create: `sunshift/dashboard/src/components/landing/constants.ts`
- Modify: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx` (delete inline constants, import from new module)

**Acceptance Criteria:**
- [ ] `constants.ts` exports: `REPO_URL`, `REPO_BLOB_URL`, `REPO_TREE_URL`, `menuItems`, `techBadges`, `riskStats`, `features`, `storyMoments`, `trustItems`, `adrLinks`
- [ ] Each exported array/object is `as const` or has an explicit type
- [ ] `hero-section-1.tsx` no longer declares any of those consts inline
- [ ] `pnpm build` succeeds, landing page renders identically

**Verify:** `cd sunshift/dashboard && pnpm build && node --test tests/landing-links.test.mjs`
Expected: build OK, but the existing test WILL BREAK because it greps `hero-section-1.tsx` directly. Update the test at this step to read from `src/components/landing/constants.ts` instead (see Step 4 below).

**Steps:**

- [ ] **Step 1: Create `src/components/landing/constants.ts`**

```ts
import type { LucideIcon } from 'lucide-react';
import {
  BarChart3, CloudLightning, DollarSign, Lock, Server, Zap,
} from 'lucide-react';

export const REPO_URL = 'https://github.com/Kaydenletk/SunShift';
export const REPO_BLOB_URL = `${REPO_URL}/blob/main`;
export const REPO_TREE_URL = `${REPO_URL}/tree/main`;

export type MenuItem = { label: string; href: string };

export const menuItems: readonly MenuItem[] = [
  { label: 'Features', href: '/#features' },
  { label: 'Architecture', href: '/#architecture' },
  { label: 'Pricing', href: '/#pricing' },
  { label: 'Docs', href: '/#docs' },
] as const;

export const techBadges = [
  'AWS', 'Terraform', 'Docker', 'FastAPI', 'Next.js',
  'PostgreSQL', 'HIPAA Certified', 'SOC 2 Ready',
] as const;

export type RiskStat = { stat: string; label: string; source: string };

export const riskStats: readonly RiskStat[] = [
  { stat: '60%',    label: 'of Florida SMBs never reopen after a natural disaster', source: 'FEMA' },
  { stat: '58%',    label: 'of backups fail when recovery is actually attempted',   source: '' },
  { stat: '11 days', label: 'without power for some Tampa businesses after Hurricane Milton', source: '2024' },
] as const;

export type Feature = {
  icon: LucideIcon;
  title: string;
  description: string;
  href: string;
  ctaLabel: string;
  external?: boolean;
};

export const features: readonly Feature[] = [
  // Pillar 1 — Never Lose Your Data
  {
    icon: CloudLightning,
    title: 'When a hurricane hits, your data is already 920 miles away',
    description:
      'SunShift watches NOAA storm alerts 24/7. When a hurricane threatens Tampa Bay, it automatically backs up everything to AWS Ohio — completely outside any Florida hurricane path. You get notified. Nothing breaks.',
    href: `${REPO_BLOB_URL}/sunshift/backend/services/hurricane_shield.py`,
    ctaLabel: 'View hurricane_shield.py',
    external: true,
  },
  {
    icon: Lock,
    title: 'Bank-level encryption from your office to Ohio and back',
    description:
      'Every file is AES-256 encrypted before it leaves your server. Every access is logged automatically. HIPAA-ready infrastructure — no scrambling when regulators ask for proof.',
    href: `${REPO_BLOB_URL}/docs/adr/004-hipaa-compliance.md`,
    ctaLabel: 'Read ADR-004: HIPAA Compliance',
    external: true,
  },
  // Pillar 2 — Never Go Down
  {
    icon: Server,
    title: 'Power goes out in Tampa. Your team keeps working.',
    description:
      'A lightweight Python asyncio daemon monitors your server health every minute. If your office loses power or connectivity, SunShift fails over to the cloud automatically. Average failover: 4 minutes. Failback is automatic too.',
    href: `${REPO_TREE_URL}/sunshift/agent`,
    ctaLabel: 'View agent runtime',
    external: true,
  },
  {
    icon: BarChart3,
    title: 'Check everything from your phone. In plain English.',
    description:
      "Next.js dashboard with 60-second auto-refresh. See if your server is running, when the last backup happened, and how much you've saved this month. Three states: Protected, Peak, Hurricane. Green means good.",
    href: '/dashboard',
    ctaLabel: 'Open live dashboard',
  },
  // Pillar 3 — Never Overpay
  {
    icon: Zap,
    title: 'SunShift finds the cheapest hours to run your server. Automatically.',
    description:
      'Tampa FPL rates swing from 6¢ to 27¢/kWh during peak hours. A Prophet + XGBoost ensemble forecasts costs 48h ahead with 87% accuracy. Heavy workloads shift to off-peak windows — customers save $100–150/month.',
    href: `${REPO_BLOB_URL}/sunshift/backend/ml/model.py`,
    ctaLabel: 'View model.py (Prophet + XGBoost)',
    external: true,
  },
  {
    icon: DollarSign,
    title: "Tax season hits. Your server doesn't choke.",
    description:
      'Hybrid Greedy + Lookahead scheduler picks the cheapest migration window dynamically. Burst to the cloud during demand peaks, pull back when the rush ends. No new hardware for a two-month problem.',
    href: `${REPO_BLOB_URL}/sunshift/backend/services/scheduler_service.py`,
    ctaLabel: 'View scheduler_service.py',
    external: true,
  },
] as const;

export type StoryMoment = {
  icon: LucideIcon;
  moment: string;
  description: string;
  tech: string;
  href: string;
  ctaLabel: string;
  external?: boolean;
};

export const storyMoments: readonly StoryMoment[] = [
  {
    icon: Server,
    moment: 'Right now, while you work',
    description:
      'Your files live on your office server — fast, local, under your control. In the background, SunShift quietly syncs everything to a secure vault in Ohio. Your team never notices.',
    tech: 'Python asyncio daemon · AES-256 S3 Transfer Acceleration · WebSocket',
    href: `${REPO_TREE_URL}/sunshift/agent`,
    ctaLabel: 'View agent code',
    external: true,
  },
  {
    icon: CloudLightning,
    moment: 'When a storm is coming',
    description:
      'SunShift polls NOAA every 30 minutes. When a hurricane threatens Tampa Bay, it automatically migrates your operations to Ohio — hours before landfall. Your team can keep working from laptops, phones, anywhere.',
    tech: 'FastAPI + EventBridge · 5-level threat scale · < 15-min RTO',
    href: `${REPO_TREE_URL}/sunshift/backend`,
    ctaLabel: 'Explore backend services',
    external: true,
  },
  {
    icon: DollarSign,
    moment: 'When electricity prices spike',
    description:
      'Florida power rates change every hour. When FPL rates spike 4.5×, SunShift shifts heavy computing to the cloud where it costs less. When rates drop, it shifts back. You see the savings on your next bill.',
    tech: 'Prophet + XGBoost ensemble · 48h lookahead · Hybrid Greedy scheduler',
    href: '/dashboard',
    ctaLabel: 'Open live dashboard',
  },
] as const;

export const trustItems = [
  { label: 'Bank-level encryption',       sub: 'AES-256 before files leave your office' },
  { label: 'Weather checked every 30 min', sub: 'NOAA NHC integration, 24/7' },
  { label: '99.99% uptime',                sub: 'Less than 1 hour of downtime per year' },
  { label: 'Fully automatic',              sub: 'No phone calls, no IT guy required' },
] as const;

export const adrLinks = [
  { id: 'ADR-001', title: 'Hybrid Cloud Architecture', href: `${REPO_BLOB_URL}/docs/adr/001-hybrid-cloud-architecture.md` },
  { id: 'ADR-002', title: 'AWS Ohio Destination',      href: `${REPO_BLOB_URL}/docs/adr/002-aws-ohio-destination.md` },
  { id: 'ADR-003', title: 'TOU-Based Scheduling',      href: `${REPO_BLOB_URL}/docs/adr/003-tou-based-scheduling.md` },
  { id: 'ADR-004', title: 'HIPAA Compliance',          href: `${REPO_BLOB_URL}/docs/adr/004-hipaa-compliance.md` },
  { id: 'ADR-005', title: 'Hurricane Shield',          href: `${REPO_BLOB_URL}/docs/adr/005-hurricane-shield.md` },
] as const;
```

- [ ] **Step 2: Delete the inline constants from `hero-section-1.tsx` (lines ~15–170) and import them**

At the top of `hero-section-1.tsx`, replace the deleted consts with:
```tsx
import {
  REPO_URL, REPO_BLOB_URL, REPO_TREE_URL,
  menuItems, techBadges, riskStats, features, storyMoments, trustItems, adrLinks,
} from '@/components/landing/constants';
```

Keep the lucide-react icon imports only for icons still used directly in JSX (Sun, Menu, X, Shield, MapPin, ArrowRight, ChevronRight, FileText, GitBranch). Remove imports that are now only used inside `constants.ts`.

- [ ] **Step 3: Update the existing test to read from `constants.ts`**

Edit `sunshift/dashboard/tests/landing-links.test.mjs` to read from the new location:
```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';

const constantsPath = path.join(process.cwd(), 'src/components/landing/constants.ts');
const source = readFileSync(constantsPath, 'utf8');

test('landing navigation uses root-qualified hash links', () => {
  assert.match(source, /label: 'Features', href: '\/#features'/);
  assert.match(source, /label: 'Architecture', href: '\/#architecture'/);
  assert.match(source, /label: 'Pricing', href: '\/#pricing'/);
  assert.match(source, /label: 'Docs', href: '\/#docs'/);
});

test('feature entries have destination hrefs', () => {
  assert.match(source, /export const features[\s\S]*?href: `/);
});

test('story moments and ADR links have destination hrefs', () => {
  assert.match(source, /export const storyMoments[\s\S]*?href: /);
  assert.match(source, /export const adrLinks[\s\S]*?href: /);
});
```

- [ ] **Step 4: Verify build and test**

```bash
cd sunshift/dashboard
pnpm build
node --test tests/landing-links.test.mjs
```
Expected: build succeeds, `# pass 3`.

- [ ] **Step 5: Commit**

```bash
git add sunshift/dashboard/src/components/landing/constants.ts \
        sunshift/dashboard/src/components/blocks/hero-section-1.tsx \
        sunshift/dashboard/tests/landing-links.test.mjs
git commit -m "$(cat <<'EOF'
refactor(landing): extract data constants to landing/constants.ts

Pure data module — no JSX, no runtime. Types exported so section
components can rely on them. Test updated to read from the new
location.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Extract `LandingHeader.tsx` (client component)

**Goal:** Move the fixed nav + mobile menu + scroll listener into its own client component. Zero behavior change.

**Files:**
- Create: `sunshift/dashboard/src/components/landing/LandingHeader.tsx`
- Modify: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx` (delete `HeroHeader`, import `LandingHeader`)

**Acceptance Criteria:**
- [ ] New file starts with `'use client'`
- [ ] Imports `menuItems` from `constants.ts`
- [ ] Header renders identically (same classes, same behavior)
- [ ] Mobile menu closes on link click (same as before)
- [ ] Scroll listener is cleaned up in effect return

**Verify:** `pnpm build`, then manual check at `pnpm dev` — header scrolls and toggles correctly.

**Steps:**

- [ ] **Step 1: Create `src/components/landing/LandingHeader.tsx`**

```tsx
'use client';

import Link from 'next/link';
import { ArrowRight, Menu, Sun, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { menuItems } from './constants';

export function LandingHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    let ticking = false;
    function handleScroll() {
      if (!ticking) {
        requestAnimationFrame(() => {
          setScrolled(window.scrollY > 20);
          ticking = false;
        });
        ticking = true;
      }
    }
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={cn(
        'fixed top-0 z-50 w-full transition-all duration-300',
        scrolled
          ? 'bg-background/80 border-b border-border backdrop-blur-md shadow-sm'
          : 'bg-transparent'
      )}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <Sun className="size-7 text-primary" />
          <span className="text-xl font-bold tracking-tight text-foreground">SunShift</span>
        </Link>

        <nav aria-label="Main navigation" className="hidden md:flex items-center gap-8">
          {menuItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <Link href="/dashboard" className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }))}>
            Login
          </Link>
          <a href="/#pricing" className={cn(buttonVariants({ size: 'sm' }))}>
            Start Free Trial
            <ArrowRight className="ml-1 size-3.5" />
          </a>
        </div>

        <button
          className="md:hidden text-foreground"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
        >
          {menuOpen ? <X className="size-6" /> : <Menu className="size-6" />}
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden border-t border-border bg-background/95 backdrop-blur-md px-6 py-4">
          <nav aria-label="Mobile navigation" className="flex flex-col gap-4">
            {menuItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                onClick={() => setMenuOpen(false)}
              >
                {item.label}
              </a>
            ))}
            <div className="flex flex-col gap-2 pt-2 border-t border-border">
              <Link href="/dashboard" className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }))}>
                Login
              </Link>
              <a href="/#pricing" className={cn(buttonVariants({ size: 'sm' }))}>
                Start Free Trial
                <ArrowRight className="ml-1 size-3.5" />
              </a>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
```

- [ ] **Step 2: Delete `HeroHeader` function from `hero-section-1.tsx` and import `LandingHeader`**

At the top:
```tsx
import { LandingHeader } from '@/components/landing/LandingHeader';
```

Inside `HeroSection`:
```tsx
return (
  <>
    <LandingHeader />
    <main className="overflow-hidden">
      {/* ... rest unchanged ... */}
```

- [ ] **Step 3: Build + manual dev check**

```bash
cd sunshift/dashboard && pnpm build
```
Expected: success.

```bash
cd sunshift/dashboard && pnpm dev
```
Visit `http://localhost:3000`. Scroll → header background fades in. Resize to mobile → hamburger toggles menu → clicking a link closes menu.

- [ ] **Step 4: Commit**

```bash
git add sunshift/dashboard/src/components/landing/LandingHeader.tsx \
        sunshift/dashboard/src/components/blocks/hero-section-1.tsx
git commit -m "$(cat <<'EOF'
refactor(landing): extract LandingHeader client component

Nav + mobile menu + scroll listener moved out of the monolithic
hero block. Behavior identical.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Extract `HeroSection.tsx` and `RealityCheckSection.tsx`

**Goal:** Move the above-the-fold hero (headline, subhead, CTAs, hero image, tech badges) and the three-stat reality check into dedicated server components.

**Files:**
- Create: `sunshift/dashboard/src/components/landing/HeroSection.tsx`
- Create: `sunshift/dashboard/src/components/landing/RealityCheckSection.tsx`
- Modify: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx`

**Acceptance Criteria:**
- [ ] `HeroSection.tsx` imports `techBadges` from constants and contains all markup from the `<section className="relative pt-32...">` block (hero).
- [ ] `RealityCheckSection.tsx` imports `riskStats` and renders the three-stat grid.
- [ ] `hero-section-1.tsx` now renders `<LandingHeader />`, `<HeroSection />`, `<RealityCheckSection />` and the remaining unextracted sections.
- [ ] `pnpm build` passes.
- [ ] Page renders byte-for-byte identical (manual inspection).

**Verify:** `cd sunshift/dashboard && pnpm build` → success. Visit `/` in dev → no visual diff vs. Task 2 state.

**Steps:**

- [ ] **Step 1: Create `src/components/landing/HeroSection.tsx`**

Copy the full `<section className="relative pt-32 pb-16 md:pt-40 md:pb-24">` block from `hero-section-1.tsx` (currently starting around line 295 and ending before the reality-check section). Wrap in a component:

```tsx
import Link from 'next/link';
import Image from 'next/image';
import { ArrowRight, ChevronRight, GitBranch, Shield } from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { AnimatedGroup } from '@/components/ui/animated-group';
import { cn } from '@/lib/utils';
import { REPO_URL, techBadges } from './constants';

export function HeroSection() {
  return (
    <section className="relative pt-32 pb-16 md:pt-40 md:pb-24">
      {/* background gradients — PASTE EXACTLY from original */}
      {/* hero badge, headline, subhead, CTA row, hero image, tech badges — PASTE EXACTLY */}
    </section>
  );
}
```

The engineer should paste the existing JSX unchanged — the only differences are the imports above (from `./constants`) and wrapping in a function. Preserve every className, every `AnimatedGroup` prop.

- [ ] **Step 2: Create `src/components/landing/RealityCheckSection.tsx`**

```tsx
import { riskStats } from './constants';

export function RealityCheckSection() {
  return (
    <section className="py-20 bg-muted/30">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-primary">
            The Reality
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Florida SMBs face two threats every summer
          </h2>
        </div>
        <div className="mt-12 grid gap-8 sm:grid-cols-3">
          {riskStats.map((item) => (
            <div
              key={item.label}
              className="flex flex-col items-center rounded-xl border border-border bg-card p-8 text-center shadow-sm"
            >
              <div className="text-5xl font-bold tracking-tight text-primary sm:text-6xl">
                {item.stat}
              </div>
              <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                {item.label}
              </p>
              {item.source && (
                <p className="mt-3 text-xs text-muted-foreground/60">Source: {item.source}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

*Note:* If the original reality-check section has slightly different copy or classes, PRESERVE the original. Reading `hero-section-1.tsx` around line 380–420 is the source of truth — copy its JSX verbatim into the new file and only change imports + the function wrapper.

- [ ] **Step 3: Wire into `hero-section-1.tsx`**

```tsx
import { LandingHeader } from '@/components/landing/LandingHeader';
import { HeroSection as LandingHero } from '@/components/landing/HeroSection';
import { RealityCheckSection } from '@/components/landing/RealityCheckSection';

function HeroSection() {
  return (
    <>
      <LandingHeader />
      <main className="overflow-hidden">
        <LandingHero />
        <RealityCheckSection />
        {/* Features, Architecture, Pricing, Docs, Footer — still inline */}
      </main>
    </>
  );
}

export { HeroSection };
```

- [ ] **Step 4: Verify build and page render**

```bash
cd sunshift/dashboard && pnpm build && pnpm dev
```
Visit `/`. Confirm hero and reality-check sections render identically to before.

- [ ] **Step 5: Commit**

```bash
git add sunshift/dashboard/src/components/landing/HeroSection.tsx \
        sunshift/dashboard/src/components/landing/RealityCheckSection.tsx \
        sunshift/dashboard/src/components/blocks/hero-section-1.tsx
git commit -m "$(cat <<'EOF'
refactor(landing): extract HeroSection and RealityCheckSection

Two server components. No behavior change.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Extract `FeaturesSection.tsx` with degraded-safe card structure

**Goal:** Move features into its own server component AND change the card markup so the card body is not a `<Link>`. GitHub URL becomes a small "View source →" secondary link. If the URL 404s, only that link breaks — the card's content lands.

**Files:**
- Create: `sunshift/dashboard/src/components/landing/FeaturesSection.tsx`
- Modify: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx` (delete features block, import new component)

**Acceptance Criteria:**
- [ ] Each feature renders as `<article>` (not `<Link>`).
- [ ] Icon, title, description render inside the article.
- [ ] A secondary `<a>` at the card footer with class `text-sm font-medium text-primary hover:underline` wraps `{feature.ctaLabel}` and an `ArrowRight`.
- [ ] External links still use `target="_blank"` and `rel="noreferrer"`.
- [ ] Internal links (starting with `/`) render as `<Link>` instead of `<a>`.
- [ ] The three-pillar grouping (Never Lose Your Data / Never Go Down / Never Overpay) is preserved.

**Verify:** `pnpm build` + visual check in dev — features section looks almost identical, except: clicking the card body no longer navigates. Only the "View source →" text at the bottom is clickable.

**Steps:**

- [ ] **Step 1: Create `src/components/landing/FeaturesSection.tsx`**

```tsx
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import type { Feature } from './constants';
import { features } from './constants';

function FeatureCard({ feature }: { feature: Feature }) {
  const isInternal = feature.href.startsWith('/');
  const LinkTag = isInternal ? Link : 'a';
  const linkProps = isInternal
    ? { href: feature.href }
    : { href: feature.href, target: '_blank', rel: 'noreferrer' as const };

  return (
    <article className="group relative flex h-full flex-col rounded-xl border border-border bg-card p-6 shadow-sm transition-all hover:border-primary/30 hover:shadow-md">
      <div className="flex size-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <feature.icon className="size-5" />
      </div>
      <h3 className="mt-4 text-lg font-semibold leading-snug text-foreground">
        {feature.title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        {feature.description}
      </p>
      <LinkTag
        {...linkProps}
        className="mt-6 flex items-center gap-2 text-sm font-medium text-primary hover:underline"
      >
        <span>{feature.ctaLabel}</span>
        <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
      </LinkTag>
    </article>
  );
}

export function FeaturesSection() {
  return (
    <section id="features" className="scroll-mt-20 py-24 bg-muted/30">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-primary">What You Get</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            What SunShift Actually Does
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            No jargon. No guesswork. Three outcomes, six capabilities, one system.
          </p>
        </div>

        {/* Pillar 1 — Never Lose Your Data */}
        <div className="mt-16">
          <div className="flex items-center gap-3">
            <span className="shrink-0 rounded-full bg-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-primary">
              Never Lose Your Data
            </span>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="mt-4 grid gap-6 sm:grid-cols-2">
            {features.slice(0, 2).map((feature) => (
              <FeatureCard key={feature.title} feature={feature} />
            ))}
          </div>
        </div>

        {/* Pillars 2 & 3 */}
        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <div>
            <div className="flex items-center gap-3">
              <span className="shrink-0 rounded-full bg-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-primary">
                Never Go Down
              </span>
              <div className="h-px flex-1 bg-border" />
            </div>
            <div className="mt-4 space-y-6">
              {features.slice(2, 4).map((feature) => (
                <FeatureCard key={feature.title} feature={feature} />
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-3">
              <span className="shrink-0 rounded-full bg-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-primary">
                Never Overpay
              </span>
              <div className="h-px flex-1 bg-border" />
            </div>
            <div className="mt-4 space-y-6">
              {features.slice(4, 6).map((feature) => (
                <FeatureCard key={feature.title} feature={feature} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Delete features block from `hero-section-1.tsx` and import `FeaturesSection`**

Replace the `<section id="features" ...>...</section>` block with:
```tsx
<FeaturesSection />
```
And add the import at top:
```tsx
import { FeaturesSection } from '@/components/landing/FeaturesSection';
```

- [ ] **Step 3: Verify build + visual parity**

```bash
cd sunshift/dashboard && pnpm build
```
Expected: success.

Visit `/` in dev. Click a feature card body: should NOT navigate. Click "View hurricane_shield.py" link: should open GitHub in new tab.

- [ ] **Step 4: Commit**

```bash
git add sunshift/dashboard/src/components/landing/FeaturesSection.tsx \
        sunshift/dashboard/src/components/blocks/hero-section-1.tsx
git commit -m "$(cat <<'EOF'
refactor(landing): extract FeaturesSection with graceful-degrade cards

Card body no longer a Link. GitHub URL is a secondary "View source"
link at the card footer — if it 404s, the card's content still lands.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Extract `ArchitectureSection.tsx` with same card structure

**Goal:** Move architecture (geographic callout + 3 story moments + trust strip + ADR pills + closer) into its own component. Story moment cards follow the same non-link-body pattern as FeaturesSection.

**Files:**
- Create: `sunshift/dashboard/src/components/landing/ArchitectureSection.tsx`
- Modify: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx`

**Acceptance Criteria:**
- [ ] Story moment cards are `<article>` elements — the entire card is NOT a link.
- [ ] ADR pills remain as `<Link>` (they are small, obviously link-like, safe).
- [ ] Geographic callout, trust strip, closer copy, and section IDs preserved.

**Verify:** `pnpm build` + visual parity.

**Steps:**

- [ ] **Step 1: Create `src/components/landing/ArchitectureSection.tsx`**

```tsx
import Link from 'next/link';
import { ArrowRight, FileText, MapPin } from 'lucide-react';
import type { StoryMoment } from './constants';
import { storyMoments, trustItems, adrLinks } from './constants';

function StoryMomentCard({ moment, index }: { moment: StoryMoment; index: number }) {
  const isInternal = moment.href.startsWith('/');
  const LinkTag = isInternal ? Link : 'a';
  const linkProps = isInternal
    ? { href: moment.href }
    : { href: moment.href, target: '_blank', rel: 'noreferrer' as const };

  return (
    <article className="relative flex flex-col rounded-xl border border-border bg-card p-8 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="flex size-7 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
          {index + 1}
        </span>
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {moment.moment}
        </span>
      </div>
      <div className="mt-5 flex size-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <moment.icon className="size-5" />
      </div>
      <p className="mt-4 text-sm leading-relaxed text-muted-foreground">{moment.description}</p>
      <p className="mt-5 border-t border-border pt-4 font-mono text-xs text-muted-foreground/60">
        {moment.tech}
      </p>
      <LinkTag
        {...linkProps}
        className="mt-4 flex items-center gap-2 text-sm font-medium text-primary hover:underline"
      >
        <span>{moment.ctaLabel}</span>
        <ArrowRight className="size-4" />
      </LinkTag>
    </article>
  );
}

export function ArchitectureSection() {
  return (
    <section id="architecture" className="scroll-mt-20 py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-primary">How It Works</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            How SunShift Protects Your Business
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Three layers of protection that keep you running — and saving — no matter what Florida throws at you.
          </p>
        </div>

        <div className="mt-12 mx-auto max-w-3xl overflow-hidden rounded-2xl border border-primary/20 bg-amber-50/50 dark:bg-amber-900/10 px-8 py-10 text-center">
          <div className="flex items-center justify-center gap-2 text-primary">
            <MapPin className="size-4" />
            <span className="text-xs font-bold uppercase tracking-widest">Geographic Safety</span>
          </div>
          <p className="mt-3 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            Your backup is 920 miles from the nearest hurricane.
          </p>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
            When a storm threatens Tampa Bay, your data is already safe in Ohio — farther away than Atlanta, Nashville, or Charlotte. No Florida hurricane has ever reached it. Not once.
          </p>
          <p className="mt-5 text-xs text-muted-foreground/60">
            AWS us-east-2 (Columbus, OH) &middot; Tier III+ data center &middot; AES-256 encrypted
          </p>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {storyMoments.map((moment, index) => (
            <StoryMomentCard key={moment.moment} moment={moment} index={index} />
          ))}
        </div>

        <div className="mt-10 grid gap-6 rounded-xl border border-border bg-muted/40 px-8 py-6 sm:grid-cols-2 lg:grid-cols-4">
          {trustItems.map((item) => (
            <div key={item.label} className="flex flex-col gap-1">
              <span className="text-sm font-semibold text-foreground">{item.label}</span>
              <span className="text-xs text-muted-foreground">{item.sub}</span>
            </div>
          ))}
        </div>

        <div className="mt-10">
          <p className="mb-4 text-center text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Engineering Decisions
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {adrLinks.map((adr) => (
              <Link
                key={adr.id}
                href={adr.href}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground transition-colors hover:border-primary/30 hover:text-foreground"
              >
                <FileText className="size-3" />
                {adr.id}: {adr.title}
              </Link>
            ))}
          </div>
        </div>

        <p className="mt-12 text-center text-lg font-medium text-foreground">
          Set it up once. Never think about it again.
        </p>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Wire into `hero-section-1.tsx`**

Replace the architecture `<section>` block with `<ArchitectureSection />` and add import.

- [ ] **Step 3: Verify build + parity**

`cd sunshift/dashboard && pnpm build` → success. Dev check.

- [ ] **Step 4: Commit**

```bash
git add sunshift/dashboard/src/components/landing/ArchitectureSection.tsx \
        sunshift/dashboard/src/components/blocks/hero-section-1.tsx
git commit -m "$(cat <<'EOF'
refactor(landing): extract ArchitectureSection with graceful-degrade cards

Story moment cards follow the same non-link-body pattern as features.
ADR pills remain as Link (small, obviously interactive).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Extract `PricingSection.tsx`, `DocsSection.tsx`, `LandingFooter.tsx`

**Goal:** Bundle the remaining three pure-presentational extractions into one task — each is small and follows an established pattern.

**Files:**
- Create: `sunshift/dashboard/src/components/landing/PricingSection.tsx`
- Create: `sunshift/dashboard/src/components/landing/DocsSection.tsx`
- Create: `sunshift/dashboard/src/components/landing/LandingFooter.tsx`
- Modify: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx`

**Acceptance Criteria:**
- [ ] Pricing keeps both tier cards, "Most Popular" badge, and Zap list icons.
- [ ] Docs keeps the terminal mockup and both CTA buttons.
- [ ] Footer keeps copyright + tagline + Sun icon.
- [ ] All three are server components (no `'use client'`).

**Verify:** `pnpm build` + visual parity.

**Steps:**

- [ ] **Step 1: Create `PricingSection.tsx`** — copy the `<section id="pricing" ...>` block from `hero-section-1.tsx` into a function. Import `Link`, `ArrowRight`, `Zap`, `buttonVariants`, `cn`. No data from `constants.ts` needed (pricing tier copy is inline — leave as is, since the spec doesn't mandate a data extraction).

- [ ] **Step 2: Create `DocsSection.tsx`** — copy the `<section id="docs" ...>` block. Import `Link`, `ArrowRight`, `GitBranch`, `buttonVariants`, `cn`, `REPO_URL` from constants. Replace the hardcoded GitHub URL in the "View on GitHub" button with `{REPO_URL}`.

- [ ] **Step 3: Create `LandingFooter.tsx`**

```tsx
import { Sun } from 'lucide-react';

export function LandingFooter() {
  return (
    <footer className="border-t border-border bg-muted/30 py-10">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-4 px-6 text-sm text-muted-foreground sm:flex-row sm:justify-between">
        <div className="flex items-center gap-2">
          <Sun className="size-4 text-primary" />
          <span className="font-medium text-foreground">SunShift</span>
          <span>&copy; {new Date().getFullYear()}</span>
        </div>
        <p>Built for Tampa Bay SMBs. Powered by AWS Ohio.</p>
      </div>
    </footer>
  );
}
```

- [ ] **Step 4: Wire all three into `hero-section-1.tsx`** — replace inline blocks with component tags. Add imports.

- [ ] **Step 5: Verify build + visual parity**

```bash
cd sunshift/dashboard && pnpm build && pnpm dev
```
Visit `/`. Compare each section to the original.

- [ ] **Step 6: Commit**

```bash
git add sunshift/dashboard/src/components/landing/PricingSection.tsx \
        sunshift/dashboard/src/components/landing/DocsSection.tsx \
        sunshift/dashboard/src/components/landing/LandingFooter.tsx \
        sunshift/dashboard/src/components/blocks/hero-section-1.tsx
git commit -m "$(cat <<'EOF'
refactor(landing): extract Pricing, Docs, and Footer sections

Completes the per-section extraction. hero-section-1.tsx is now
a thin composition file. Next task deletes it entirely.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Wire `app/page.tsx` to landing components, delete `hero-section-1.tsx`

**Goal:** Make `app/page.tsx` compose the landing components directly. Delete the now-empty `hero-section-1.tsx` and any imports pointing to it.

**Files:**
- Modify: `sunshift/dashboard/src/app/page.tsx`
- Delete: `sunshift/dashboard/src/components/blocks/hero-section-1.tsx`
- Delete: `sunshift/dashboard/src/components/blocks/` (directory — if now empty)

**Acceptance Criteria:**
- [ ] `page.tsx` imports 9 landing components and renders them in order: Header, Hero, RealityCheck, Features, Architecture, Pricing, Docs, Footer.
- [ ] `hero-section-1.tsx` deleted.
- [ ] `tests/landing-links.test.mjs` still passes (already updated in Task 1 to read `constants.ts`).
- [ ] `pnpm build` passes.

**Verify:** `cd sunshift/dashboard && pnpm build && node --test tests/landing-links.test.mjs`
Expected: build OK, `# pass 3`.

**Steps:**

- [ ] **Step 1: Replace `app/page.tsx`**

```tsx
import { LandingHeader } from '@/components/landing/LandingHeader';
import { HeroSection } from '@/components/landing/HeroSection';
import { RealityCheckSection } from '@/components/landing/RealityCheckSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import { ArchitectureSection } from '@/components/landing/ArchitectureSection';
import { PricingSection } from '@/components/landing/PricingSection';
import { DocsSection } from '@/components/landing/DocsSection';
import { LandingFooter } from '@/components/landing/LandingFooter';

export default function RootPage() {
  return (
    <>
      <LandingHeader />
      <main className="overflow-hidden">
        <HeroSection />
        <RealityCheckSection />
        <FeaturesSection />
        <ArchitectureSection />
        <PricingSection />
        <DocsSection />
      </main>
      <LandingFooter />
    </>
  );
}
```

- [ ] **Step 2: Delete `hero-section-1.tsx`**

```bash
rm sunshift/dashboard/src/components/blocks/hero-section-1.tsx
rmdir sunshift/dashboard/src/components/blocks 2>/dev/null || true
```

- [ ] **Step 3: Search for any remaining imports**

```bash
cd sunshift/dashboard && grep -rn "blocks/hero-section" src tests 2>/dev/null
```
Expected: no matches.

- [ ] **Step 4: Verify build + test**

```bash
cd sunshift/dashboard && pnpm build && node --test tests/landing-links.test.mjs
```
Expected: build succeeds, `# pass 3`.

- [ ] **Step 5: Commit**

```bash
git add -A sunshift/dashboard/src sunshift/dashboard/tests
git commit -m "$(cat <<'EOF'
refactor(landing): replace monolithic hero-section-1 with composed page

app/page.tsx now composes 8 focused components. The 817-line
hero-section-1.tsx is deleted. No behavioral change; visual parity
verified via build + dev-server manual check.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Waitlist storage helper + Zod schema (unit tests first)

**Goal:** Build the file-backed waitlist store with atomic writes and the email Zod schema. Pure logic — no Next.js runtime.

**Files:**
- Create: `sunshift/dashboard/src/lib/waitlist-schema.ts`
- Create: `sunshift/dashboard/src/lib/waitlist-storage.ts`
- Create: `sunshift/dashboard/tests/waitlist-storage.test.mjs`
- Modify: `.gitignore` (root) — add `data/waitlist.json`

**Acceptance Criteria:**
- [ ] `waitlistEntrySchema` validates `{ email: string }` (z.string().email()), strips unknown keys.
- [ ] `loadWaitlist(path)` returns `{ entries: [] }` when file missing, parses existing JSON otherwise.
- [ ] `appendToWaitlist(path, entry)` atomically writes via `.tmp` + rename.
- [ ] `hasEmail(waitlist, email)` is case-insensitive.
- [ ] All helpers are async (return `Promise<...>`).
- [ ] `data/waitlist.json` added to root `.gitignore`.
- [ ] Unit tests cover: schema valid/invalid; load missing file; append creates file; duplicate check case-insensitive; malformed JSON on disk surfaces a clear error.

**Verify:**
```bash
cd sunshift/dashboard && node --test tests/waitlist-storage.test.mjs
```
Expected: `# pass 7` or higher (one per test case).

**Steps:**

- [ ] **Step 1: Write the tests first**

`sunshift/dashboard/tests/waitlist-storage.test.mjs`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

// Use dynamic import so TS is compiled on the fly via tsx if needed.
// For now, keep sources as .ts — the test imports the compiled .js only after build.
// If running directly: `node --import tsx --test tests/waitlist-storage.test.mjs`
//
// Simpler: write helpers in a way that tests can import .ts via tsx.
// We'll install tsx as a devDependency in Step 2.

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
  if (result.success) {
    assert.deepEqual(Object.keys(result.data), ['email']);
  }
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
    await assert.rejects(storage.loadWaitlist(file), /waitlist file is malformed/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
```

- [ ] **Step 2: Install `tsx` as a devDependency so tests can import `.ts` directly**

```bash
cd sunshift/dashboard && pnpm add -D tsx
```

- [ ] **Step 3: Run tests to verify RED**

```bash
cd sunshift/dashboard && node --import tsx --test tests/waitlist-storage.test.mjs
```
Expected: all tests fail with `Cannot find module` or similar — the implementations don't exist yet.

- [ ] **Step 4: Create `src/lib/waitlist-schema.ts`**

```ts
import { z } from 'zod';

export const waitlistEntrySchema = z
  .object({ email: z.string().trim().email() })
  .transform((data) => ({ email: data.email.toLowerCase() }));

export type WaitlistEntryInput = z.input<typeof waitlistEntrySchema>;
export type WaitlistEntry = z.output<typeof waitlistEntrySchema>;
```

Zod's default `.object()` strips unknown keys silently — this satisfies the "strips unknown keys" test. `.transform` normalizes to lowercase after validation so the stored form is canonical.

- [ ] **Step 5: Create `src/lib/waitlist-storage.ts`**

```ts
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
```

- [ ] **Step 6: Run tests to verify GREEN**

```bash
cd sunshift/dashboard && node --import tsx --test tests/waitlist-storage.test.mjs
```
Expected: all 7 tests pass.

- [ ] **Step 7: Add `data/waitlist.json` to root `.gitignore`**

Edit `.gitignore` (at the repo root — this is where it already lives) and add under the existing `# Build outputs` or under its own heading:
```
# Runtime data (waitlist, logs)
data/
```

Or just `data/waitlist.json` if you want to keep other files in `data/` trackable. Recommend `data/` as a directory since we don't expect anything else tracked there.

- [ ] **Step 8: Commit**

```bash
git add sunshift/dashboard/src/lib/waitlist-schema.ts \
        sunshift/dashboard/src/lib/waitlist-storage.ts \
        sunshift/dashboard/tests/waitlist-storage.test.mjs \
        sunshift/dashboard/package.json \
        sunshift/dashboard/pnpm-lock.yaml \
        .gitignore
git commit -m "$(cat <<'EOF'
feat(waitlist): add storage helper + Zod schema with unit tests

- Atomic write (tmp + rename)
- Case-insensitive dedupe
- Graceful error on malformed JSON
- Schema lowercases and trims emails

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Rate limiter + `POST /api/waitlist` route (integration tests)

**Goal:** Build the Next.js App Router API route and the in-memory rate limiter. Integration-test the route end-to-end.

**Files:**
- Create: `sunshift/dashboard/src/lib/rate-limit.ts`
- Create: `sunshift/dashboard/src/app/api/waitlist/route.ts`
- Create: `sunshift/dashboard/tests/waitlist-route.test.mjs`

**Acceptance Criteria:**
- [ ] `createRateLimiter({ max, windowMs })` returns `{ check(key): { allowed: boolean; resetAt: number } }`.
- [ ] Route returns `{ success: true, message }` on valid new email.
- [ ] Route returns `{ success: false, error: 'INVALID_EMAIL' }` on invalid body (400).
- [ ] Route returns `{ success: true, message }` with "already on the list" copy on duplicate email (200).
- [ ] Route returns `{ success: false, error: 'RATE_LIMITED' }` after 5 requests from the same IP (429).
- [ ] Route never echoes internals (no stack traces, no filesystem paths).

**Verify:**
```bash
cd sunshift/dashboard && node --import tsx --test tests/waitlist-route.test.mjs
```
Expected: 5 tests pass.

**Steps:**

- [ ] **Step 1: Write integration tests first**

`sunshift/dashboard/tests/waitlist-route.test.mjs`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
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
```

- [ ] **Step 2: Run tests to verify RED**

```bash
cd sunshift/dashboard && node --import tsx --test tests/waitlist-route.test.mjs
```
Expected: all fail, `route.ts` doesn't exist yet.

- [ ] **Step 3: Create `src/lib/rate-limit.ts`**

```ts
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
```

- [ ] **Step 4: Create `src/app/api/waitlist/route.ts`**

```ts
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
  if (!limit.allowed) {
    return error('RATE_LIMITED', 429);
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return error('INVALID_EMAIL', 400);
  }

  const parsed = waitlistEntrySchema.safeParse(body);
  if (!parsed.success) {
    return error('INVALID_EMAIL', 400);
  }

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
```

- [ ] **Step 5: Run tests to verify GREEN**

```bash
cd sunshift/dashboard && node --import tsx --test tests/waitlist-route.test.mjs
```
Expected: all 5 tests pass.

*Gotcha:* Rate-limit test may fail if the limiter is module-scoped and shared across tests in the same process. The test intentionally uses a unique IP per test (`10.0.0.99` etc.) so buckets don't collide. Keep IPs unique.

- [ ] **Step 6: Commit**

```bash
git add sunshift/dashboard/src/lib/rate-limit.ts \
        sunshift/dashboard/src/app/api/waitlist/route.ts \
        sunshift/dashboard/tests/waitlist-route.test.mjs
git commit -m "$(cat <<'EOF'
feat(api): POST /api/waitlist with Zod + rate limit + storage

5 requests per hour per IP, case-insensitive dedupe, discriminated
error codes. Integration-tested against a temp file via WAITLIST_FILE
env override.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: Build `WaitlistCTA.tsx` (client component with form states)

**Goal:** User-facing email form with four states: idle, submitting, success, error. Error codes from the API map to friendly messages.

**Files:**
- Create: `sunshift/dashboard/src/components/landing/WaitlistCTA.tsx`

**Acceptance Criteria:**
- [ ] `'use client'` directive at top.
- [ ] `useState` for `email`, `status` (`'idle' | 'submitting' | 'success' | 'error'`), `message`, `errorCode`.
- [ ] On submit: `fetch('/api/waitlist', { method: 'POST', headers, body })`.
- [ ] Response maps: 429 → "Too many attempts. Try again in an hour." / 400 → "Please enter a valid email address." / 500 → "Something went wrong. Try again." / success → replace form with "You're in." / duplicate (200 with message matching /already on the list/i) → green message.
- [ ] Input disabled during submit. Button shows spinner (or "Joining…" text if adding an SVG is heavy).
- [ ] Full-width amber band styling matching the spec's mockup: dark background variant uses `bg-neutral-950` / light uses `bg-amber-50/50` — go with the light version to match the rest of the landing.

**Verify:** `pnpm build` succeeds. Manual dev test: submit valid, invalid, duplicate, and rate-limited (submit 6 times fast) emails.

**Steps:**

- [ ] **Step 1: Create `src/components/landing/WaitlistCTA.tsx`**

```tsx
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
```

- [ ] **Step 2: Verify build**

```bash
cd sunshift/dashboard && pnpm build
```
Expected: success.

- [ ] **Step 3: Commit**

```bash
git add sunshift/dashboard/src/components/landing/WaitlistCTA.tsx
git commit -m "$(cat <<'EOF'
feat(landing): add WaitlistCTA client component

Four-state form (idle/submitting/success/error). Maps API error
codes to friendly messages. Accessible: aria-invalid, aria-describedby,
role=status for success, role=alert for error.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 11: Wire `WaitlistCTA` into `app/page.tsx` + end-to-end smoke

**Goal:** Insert the waitlist band between Pricing and Docs. Run the dev server and submit the form for real against the actual API.

**Files:**
- Modify: `sunshift/dashboard/src/app/page.tsx`

**Acceptance Criteria:**
- [ ] `WaitlistCTA` rendered between `PricingSection` and `DocsSection`.
- [ ] Dev server: submit a valid email → success message appears → `data/waitlist.json` at repo root contains the entry.
- [ ] Submitting the same email twice → second shows "already on the list" in green.
- [ ] Submitting `not-an-email` → red error message.

**Verify:** Manual end-to-end.

**Steps:**

- [ ] **Step 1: Edit `app/page.tsx`**

```tsx
import { LandingHeader } from '@/components/landing/LandingHeader';
import { HeroSection } from '@/components/landing/HeroSection';
import { RealityCheckSection } from '@/components/landing/RealityCheckSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import { ArchitectureSection } from '@/components/landing/ArchitectureSection';
import { PricingSection } from '@/components/landing/PricingSection';
import { WaitlistCTA } from '@/components/landing/WaitlistCTA';
import { DocsSection } from '@/components/landing/DocsSection';
import { LandingFooter } from '@/components/landing/LandingFooter';

export default function RootPage() {
  return (
    <>
      <LandingHeader />
      <main className="overflow-hidden">
        <HeroSection />
        <RealityCheckSection />
        <FeaturesSection />
        <ArchitectureSection />
        <PricingSection />
        <WaitlistCTA />
        <DocsSection />
      </main>
      <LandingFooter />
    </>
  );
}
```

- [ ] **Step 2: Run dev server and test manually**

```bash
cd sunshift/dashboard && pnpm dev
```

Visit `http://localhost:3000`. Scroll past pricing — you should see the "Priority Access / Ready to protect your business?" band.

Submit `test@example.com` → success message. Verify:
```bash
cat data/waitlist.json
```
Expected: JSON with one entry containing `test@example.com`.

Submit `test@example.com` again → "already on the list" message.

Submit `not-an-email` → red error.

- [ ] **Step 3: Commit**

```bash
git add sunshift/dashboard/src/app/page.tsx
git commit -m "$(cat <<'EOF'
feat(landing): wire WaitlistCTA between Pricing and Docs

Manual end-to-end validated: happy path, duplicate, and invalid
email all render correct UI.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 12: Final verification + PR prep

**Goal:** Run the full local validation suite and open a PR. Clean up any stray temp files.

**Files:** None modified — verification only.

**Acceptance Criteria:**
- [ ] `pnpm build` succeeds from `sunshift/dashboard/`.
- [ ] `pnpm lint` runs without new errors (baseline errors are acceptable if pre-existing).
- [ ] All three test files pass: `tests/landing-links.test.mjs`, `tests/waitlist-storage.test.mjs`, `tests/waitlist-route.test.mjs`.
- [ ] `pnpm dev` — manual click-through of every anchor link and form state.
- [ ] `data/waitlist.json` is gitignored (`git status` shows it as untracked or ignored, never staged).
- [ ] PR created with a summary referencing the spec and plan.

**Verify:**
```bash
cd sunshift/dashboard && pnpm build && pnpm lint && \
  node --test tests/landing-links.test.mjs && \
  node --import tsx --test tests/waitlist-storage.test.mjs && \
  node --import tsx --test tests/waitlist-route.test.mjs
```
Expected: build succeeds, lint passes, all three test files print pass summaries.

**Steps:**

- [ ] **Step 1: Clean the playwright-mcp artifact directory**

```bash
rm -rf .playwright-mcp
```
(Already in git status as untracked; remove it so it doesn't show up in the PR.)

- [ ] **Step 2: Run the full verification chain**

```bash
cd sunshift/dashboard && pnpm build && pnpm lint
node --test tests/landing-links.test.mjs
node --import tsx --test tests/waitlist-storage.test.mjs
node --import tsx --test tests/waitlist-route.test.mjs
```

All should be green. If any test is red, fix before continuing.

- [ ] **Step 3: Manual browser click-through**

```bash
cd sunshift/dashboard && pnpm dev
```

Checklist:
- [ ] Desktop nav: click each of Features / Architecture / Pricing / Docs → scrolls to the matching section
- [ ] Scroll: header fades in after ~20px
- [ ] Mobile (resize to <768px): hamburger opens menu → click link closes menu + scrolls
- [ ] Feature cards: clicking body does nothing; clicking "View hurricane_shield.py" opens GitHub
- [ ] Architecture cards: same as features
- [ ] ADR pills: each opens the right ADR markdown on GitHub
- [ ] Waitlist form: valid → success / invalid → error / duplicate → success with duplicate copy
- [ ] `data/waitlist.json` at repo root contains your test submissions
- [ ] Pricing CTA buttons: both still navigate to `/dashboard` (unchanged from before)
- [ ] "Live Dashboard" button in Docs: navigates to `/dashboard`
- [ ] Navigating from `/dashboard` and clicking "Features" in the header: now works (was broken before — this was the original "doesn't work" bug)

- [ ] **Step 4: Commit any final cleanup**

If anything needed fixing during manual QA, commit those fixes:
```bash
git add -A
git commit -m "chore(landing): address QA findings from final verification"
```

- [ ] **Step 5: Push and open PR**

```bash
git push -u origin HEAD
gh pr create --title "Landing refactor: section components + waitlist API + graceful card links" --body "$(cat <<'EOF'
## Summary

- Split 817-line `hero-section-1.tsx` into 8 section components + data-only `constants.ts`
- Added `POST /api/waitlist` with Zod validation, in-memory rate limiting (5/hr per IP), and atomic JSON storage
- New `WaitlistCTA` band between Pricing and Docs captures real emails to `data/waitlist.json` (gitignored)
- Feature / architecture card bodies are no longer `<Link>` — secondary "View source →" link at card footer degrades gracefully if GitHub URLs 404
- Root-qualified nav hashes (`/#features` etc.) so anchors work from `/dashboard`
- Fixed GitHub repo casing: `kaydenletk/sunshift` → `Kaydenletk/SunShift`

## Spec & Plan

- Design: `docs/specs/2026-04-16-landing-refactor-design.md`
- Plan: `docs/plans/2026-04-16-landing-refactor.md`

## Test plan

- [x] `pnpm build` passes
- [x] `pnpm lint` passes
- [x] `tests/landing-links.test.mjs` — 3 pass
- [x] `tests/waitlist-storage.test.mjs` — 7 pass
- [x] `tests/waitlist-route.test.mjs` — 5 pass
- [x] Manual click-through of every anchor and form state
- [x] Waitlist submissions persist to `data/waitlist.json`
- [x] Nav anchors now work from `/dashboard` (previously broken)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-review checklist (run before handing off for execution)

- [ ] Every task produces a commit
- [ ] Every code block is complete (no `// ...rest...` placeholders)
- [ ] All file paths are absolute-from-repo-root
- [ ] All commands show expected output
- [ ] Types used in later tasks match types defined in earlier tasks
- [ ] The existing `tests/landing-links.test.mjs` is updated in Task 1 (not left broken)
- [ ] `data/waitlist.json` path is consistent between storage helper, API route, and gitignore
- [ ] Zod schema semantics in Task 8 match what the route expects in Task 9
- [ ] `WAITLIST_FILE` env override exists for test isolation (Task 9 tests use it, production uses default)
