'use client';

import Link from 'next/link';
import Image from 'next/image';
import {
  Sun, ArrowRight, ChevronRight, Menu, X, Shield, Zap,
  GitBranch, FileText, MapPin,
} from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { AnimatedGroup } from '@/components/ui/animated-group';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import {
  REPO_URL,
  menuItems,
  techBadges,
  riskStats,
  features,
  storyMoments,
  trustItems,
  adrLinks,
} from '@/components/landing/constants';

const repoUrl = REPO_URL;

function HeroHeader() {
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
          <span className="text-xl font-bold tracking-tight text-foreground">
            SunShift
          </span>
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
          <Link
            href="/dashboard"
            className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }))}
          >
            Login
          </Link>
          <a
            href="/#pricing"
            className={cn(buttonVariants({ size: 'sm' }))}
          >
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
              <Link
                href="/dashboard"
                className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }))}
              >
                Login
              </Link>
              <a
                href="/#pricing"
                className={cn(buttonVariants({ size: 'sm' }))}
              >
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

function HeroSection() {
  return (
    <>
      <HeroHeader />
      <main className="overflow-hidden">

        {/* ─── Hero ─── */}
        <section className="relative pt-32 pb-16 md:pt-40 md:pb-24">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 -z-10"
          >
            <div className="absolute inset-x-0 top-0 h-[600px] bg-gradient-to-b from-amber-50/60 via-background to-background dark:from-amber-950/20 dark:via-background dark:to-background" />
            <div className="absolute left-1/2 top-0 -translate-x-1/2 h-[500px] w-[800px] rounded-full bg-amber-200/20 blur-3xl dark:bg-amber-900/10" />
          </div>

          <div className="mx-auto max-w-7xl px-6">
            <AnimatedGroup
              preset="blur-slide"
              className="flex flex-col items-center text-center"
            >
              <a
                href="/#features"
                className="group flex items-center gap-2 rounded-full border border-border bg-muted px-4 py-1.5 text-sm text-muted-foreground shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
              >
                <Shield className="size-3.5 text-primary" />
                <span>Now protecting Tampa Bay businesses</span>
                <ChevronRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
              </a>

              <h1 className="mt-8 max-w-4xl text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl">
                Your Data. Protected from{' '}
                <span className="text-primary">Storms</span> and{' '}
                <span className="text-primary">Peak Rates</span>.
              </h1>

              <p className="mt-6 max-w-2xl text-base text-muted-foreground md:text-lg">
                SunShift auto-migrates your workloads to AWS when electricity
                spikes or hurricanes approach. Save $100–150/month. Sleep
                through hurricane season.
              </p>

              <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row">
                <a
                  href="/#pricing"
                  className={cn(buttonVariants({ size: 'lg' }))}
                >
                  Start Free Trial
                  <ArrowRight className="ml-1 size-4" />
                </a>
                <a
                  href="/#architecture"
                  className={cn(buttonVariants({ variant: 'outline', size: 'lg' }))}
                >
                  How It Works
                </a>
              </div>
            </AnimatedGroup>

            <AnimatedGroup preset="fade" className="mt-16 sm:mt-20">
              <div className="relative mx-auto max-w-5xl overflow-hidden rounded-xl border border-border bg-background shadow-2xl shadow-black/5 ring-1 ring-black/5 dark:shadow-white/5 dark:ring-white/5">
                <Image
                  src="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=2700&h=1440&fit=crop"
                  alt="SunShift cloud infrastructure dashboard"
                  width={2700}
                  height={1440}
                  sizes="(max-width: 1280px) 100vw, 1280px"
                  className="block dark:hidden"
                  priority
                />
                <Image
                  src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=2700&h=1440&fit=crop"
                  alt="SunShift cloud infrastructure network view"
                  width={2700}
                  height={1440}
                  sizes="(max-width: 1280px) 100vw, 1280px"
                  className="hidden dark:block"
                  priority
                />
              </div>
            </AnimatedGroup>

            <AnimatedGroup preset="slide" className="mt-16 flex flex-col items-center">
              <p className="text-sm font-medium text-muted-foreground">
                Built with industry-leading technologies
              </p>
              <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
                {techBadges.map((badge) => (
                  <span
                    key={badge}
                    className="inline-flex items-center rounded-md border border-border bg-muted/50 px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
                  >
                    {badge}
                  </span>
                ))}
              </div>
            </AnimatedGroup>
          </div>
        </section>

        {/* ─── Reality Check ─── */}
        <section
          aria-label="Florida business risk statistics"
          className="border-y border-border bg-foreground/[0.03] dark:bg-white/[0.02] py-14"
        >
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid gap-10 sm:grid-cols-3">
              {riskStats.map((item) => (
                <div key={item.stat} className="flex flex-col items-center text-center">
                  <span className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                    {item.stat}
                  </span>
                  <p className="mt-2 max-w-xs text-sm leading-relaxed text-muted-foreground">
                    {item.label}
                    {item.source && (
                      <span className="ml-1 text-xs text-muted-foreground/60">
                        ({item.source})
                      </span>
                    )}
                  </p>
                </div>
              ))}
            </div>
            <p className="mt-10 text-center text-sm font-medium text-muted-foreground">
              SunShift doesn&apos;t ask you to predict the next hurricane.{' '}
              <span className="text-foreground">
                It keeps your business running through one.
              </span>
            </p>
          </div>
        </section>

        {/* ─── Features ─── */}
        <section id="features" className="scroll-mt-20 py-24 bg-muted/30">
          <div className="mx-auto max-w-7xl px-6">
            <div className="text-center">
              <p className="text-sm font-semibold uppercase tracking-wider text-primary">
                What You Get
              </p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                What SunShift Actually Does
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
                No jargon. No guesswork. Three outcomes, six capabilities, one system.
              </p>
            </div>

            <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((feature) => (
                <Link
                  key={feature.title}
                  href={feature.href}
                  target={feature.external ? '_blank' : undefined}
                  rel={feature.external ? 'noreferrer' : undefined}
                  className="group relative flex h-full flex-col rounded-xl border border-border bg-card p-6 shadow-sm transition-all hover:border-primary/30 hover:shadow-md"
                >
                  <div className="flex size-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <feature.icon className="size-5" />
                  </div>
                  <h3 className="mt-4 text-lg font-semibold leading-snug text-foreground">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {feature.description}
                  </p>
                  <div className="mt-6 flex items-center gap-2 text-sm font-medium text-primary">
                    <span>{feature.ctaLabel}</span>
                    <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Architecture / How It Works ─── */}
        <section id="architecture" className="scroll-mt-20 py-24">
          <div className="mx-auto max-w-7xl px-6">
            <div className="text-center">
              <p className="text-sm font-semibold uppercase tracking-wider text-primary">
                How It Works
              </p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                How SunShift Protects Your Business
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
                Three layers of protection that keep you running — and saving — no matter
                what Florida throws at you.
              </p>
            </div>

            {/* 920-mile geographic safety callout */}
            <div className="mt-12 mx-auto max-w-3xl overflow-hidden rounded-2xl border border-primary/20 bg-amber-50/50 dark:bg-amber-900/10 px-8 py-10 text-center">
              <div className="flex items-center justify-center gap-2 text-primary">
                <MapPin className="size-4" />
                <span className="text-xs font-bold uppercase tracking-widest">
                  Geographic Safety
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                Your backup is 920 miles from the nearest hurricane.
              </p>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                When a storm threatens Tampa Bay, your data is already safe in Ohio —
                farther away than Atlanta, Nashville, or Charlotte.
                No Florida hurricane has ever reached it. Not once.
              </p>
              <p className="mt-5 text-xs text-muted-foreground/60">
                AWS us-east-2 (Columbus, OH) &middot; Tier III+ data center &middot; AES-256 encrypted
              </p>
            </div>

            {/* Three story moments */}
            <div className="mt-12 grid gap-6 lg:grid-cols-3">
              {storyMoments.map((moment, index) => (
                <div
                  key={moment.moment}
                  className="relative flex flex-col rounded-xl border border-border bg-card p-8 shadow-sm"
                >
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
                  <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                    {moment.description}
                  </p>
                  <p className="mt-5 border-t border-border pt-4 font-mono text-xs text-muted-foreground/60">
                    {moment.tech}
                  </p>
                  <Link
                    href={moment.href}
                    target={moment.external ? '_blank' : undefined}
                    rel={moment.external ? 'noreferrer' : undefined}
                    className="mt-4 flex items-center gap-2 text-sm font-medium text-primary hover:underline"
                  >
                    <span>{moment.ctaLabel}</span>
                    <ArrowRight className="size-4" />
                  </Link>
                </div>
              ))}
            </div>

            {/* Trust strip */}
            <div className="mt-10 grid gap-6 rounded-xl border border-border bg-muted/40 px-8 py-6 sm:grid-cols-2 lg:grid-cols-4">
              {trustItems.map((item) => (
                <div key={item.label} className="flex flex-col gap-1">
                  <span className="text-sm font-semibold text-foreground">
                    {item.label}
                  </span>
                  <span className="text-xs text-muted-foreground">{item.sub}</span>
                </div>
              ))}
            </div>

            {/* Engineering Decision Records — visible for recruiters / technical evaluators */}
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

            {/* Closer */}
            <p className="mt-12 text-center text-lg font-medium text-foreground">
              Set it up once. Never think about it again.
            </p>
          </div>
        </section>

        {/* ─── Pricing ─── */}
        <section id="pricing" className="scroll-mt-20 py-24 bg-muted/30">
          <div className="mx-auto max-w-7xl px-6">
            <div className="text-center">
              <p className="text-sm font-semibold uppercase tracking-wider text-primary">
                Pricing
              </p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Enterprise protection, SMB pricing
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
                Disaster recovery and cost optimization that pays for itself. No $250K enterprise contracts.
              </p>
            </div>
            <div className="mx-auto mt-16 grid max-w-4xl gap-8 lg:grid-cols-2">
              {/* Starter */}
              <div className="rounded-xl border border-border bg-card p-8 shadow-sm">
                <h3 className="text-lg font-semibold text-foreground">Starter</h3>
                <p className="mt-1 text-sm text-muted-foreground">For small offices with 1–3 servers</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-foreground">$49</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                <ul className="mt-8 space-y-3 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> 1 on-prem agent
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> TOU cost optimization
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> Hurricane Shield alerts
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> Dashboard access
                  </li>
                </ul>
                <Link
                  href="/dashboard"
                  className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'mt-8 w-full')}
                >
                  Start Free Trial
                </Link>
              </div>

              {/* Business */}
              <div className="relative rounded-xl border-2 border-primary bg-card p-8 shadow-lg shadow-primary/10">
                <span className="absolute -top-3 right-6 rounded-full bg-primary px-3 py-0.5 text-xs font-semibold text-primary-foreground">
                  Most Popular
                </span>
                <h3 className="text-lg font-semibold text-foreground">Business</h3>
                <p className="mt-1 text-sm text-muted-foreground">For practices and offices with 3–10 servers</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-foreground">$149</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                <ul className="mt-8 space-y-3 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> Up to 5 agents
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> ML-powered scheduling
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> Auto hurricane backup
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> HIPAA compliance
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="size-4 text-primary" /> Priority support
                  </li>
                </ul>
                <Link
                  href="/dashboard"
                  className={cn(buttonVariants({ size: 'lg' }), 'mt-8 w-full')}
                >
                  Start Free Trial
                  <ArrowRight className="ml-1 size-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Docs ─── */}
        <section id="docs" className="scroll-mt-20 py-24">
          <div className="mx-auto max-w-7xl px-6">
            <div className="text-center">
              <p className="text-sm font-semibold uppercase tracking-wider text-primary">
                Documentation
              </p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                Get started in minutes
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
                One-command setup with Docker Compose. Full API documentation included.
              </p>
            </div>
            <div className="mx-auto mt-12 max-w-2xl overflow-hidden rounded-xl border border-border bg-neutral-950 p-6 font-mono text-sm shadow-lg">
              <div className="flex items-center gap-2 text-neutral-500">
                <span className="size-3 rounded-full bg-red-500/80" />
                <span className="size-3 rounded-full bg-yellow-500/80" />
                <span className="size-3 rounded-full bg-green-500/80" />
                <span className="ml-2">terminal</span>
              </div>
              <div className="mt-4 space-y-2 text-neutral-300">
                <p><span className="text-green-400">$</span> git clone {repoUrl}.git</p>
                <p><span className="text-green-400">$</span> cd sunshift</p>
                <p><span className="text-green-400">$</span> make demo</p>
                <p className="mt-4 text-amber-400">[SunShift] Starting demo environment...</p>
                <p className="text-amber-400">[SunShift] Dashboard:  http://localhost:3000</p>
                <p className="text-amber-400">[SunShift] API docs:   http://localhost:8000/docs</p>
                <p className="text-amber-400">[SunShift] Scheduler:  running (hybrid mode)</p>
                <p className="text-green-400">[SunShift] Demo ready. Simulating peak-hour migration...</p>
              </div>
            </div>
            <div className="mt-8 flex justify-center gap-4">
              <Link
                href="/dashboard"
                className={cn(buttonVariants({ size: 'lg' }))}
              >
                Live Dashboard
                <ArrowRight className="ml-1 size-4" />
              </Link>
              <Link
                href={repoUrl}
                className={cn(buttonVariants({ variant: 'outline', size: 'lg' }))}
              >
                <GitBranch className="mr-1.5 size-4" />
                View on GitHub
              </Link>
            </div>
          </div>
        </section>

        {/* ─── Footer ─── */}
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

      </main>
    </>
  );
}

export { HeroSection };
