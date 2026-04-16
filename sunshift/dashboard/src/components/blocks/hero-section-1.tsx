'use client';

import Link from 'next/link';
import {
  ArrowRight, Sun, Zap,
  GitBranch, FileText, MapPin,
} from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { LandingHeader } from '@/components/landing/LandingHeader';
import { HeroSection as HeroLandingSection } from '@/components/landing/HeroSection';
import { RealityCheckSection } from '@/components/landing/RealityCheckSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import {
  REPO_URL,
  storyMoments,
  trustItems,
  adrLinks,
} from '@/components/landing/constants';

const repoUrl = REPO_URL;

function HeroSection() {
  return (
    <>
      <LandingHeader />
      <main className="overflow-hidden">

        <HeroLandingSection />
        <RealityCheckSection />

        <FeaturesSection />

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
