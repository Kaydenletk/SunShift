'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Sun, ArrowRight, ChevronRight, Menu, X, Shield } from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { AnimatedGroup } from '@/components/ui/animated-group';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

const menuItems = [
  { label: 'Features', href: '#features' },
  { label: 'Architecture', href: '#architecture' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'Docs', href: '#docs' },
];

const techBadges = [
  'AWS',
  'Terraform',
  'Docker',
  'FastAPI',
  'Next.js',
  'PostgreSQL',
  'HIPAA Certified',
  'SOC 2 Ready',
];

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
            <Link
              key={item.label}
              href={item.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/dashboard"
            className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }))}
          >
            Login
          </Link>
          <Link
            href="#pricing"
            className={cn(buttonVariants({ size: 'sm' }))}
          >
            Start Free Trial
            <ArrowRight className="ml-1 size-3.5" />
          </Link>
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
              <Link
                key={item.label}
                href={item.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                onClick={() => setMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <div className="flex flex-col gap-2 pt-2 border-t border-border">
              <Link
                href="/dashboard"
                className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }))}
              >
                Login
              </Link>
              <Link
                href="#pricing"
                className={cn(buttonVariants({ size: 'sm' }))}
              >
                Start Free Trial
                <ArrowRight className="ml-1 size-3.5" />
              </Link>
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
        <section className="relative pt-32 pb-16 md:pt-40 md:pb-24">
          {/* Background gradient */}
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
              {/* Pill badge */}
              <Link
                href="#features"
                className="group flex items-center gap-2 rounded-full border border-border bg-muted px-4 py-1.5 text-sm text-muted-foreground shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
              >
                <Shield className="size-3.5 text-primary" />
                <span>Now protecting Tampa Bay businesses</span>
                <ChevronRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
              </Link>

              {/* Headline */}
              <h1 className="mt-8 max-w-4xl text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl">
                Your Data. Protected from{' '}
                <span className="text-primary">Storms</span> and{' '}
                <span className="text-primary">Peak Rates</span>.
              </h1>

              {/* Description */}
              <p className="mt-6 max-w-2xl text-base text-muted-foreground md:text-lg">
                SunShift auto-migrates your workloads to AWS when electricity
                spikes or hurricanes approach. Save $100-150/month. Sleep
                through hurricane season.
              </p>

              {/* CTAs */}
              <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row">
                <Link
                  href="#pricing"
                  className={cn(buttonVariants({ size: 'lg' }))}
                >
                  Start Free Trial
                  <ArrowRight className="ml-1 size-4" />
                </Link>
                <Link
                  href="#architecture"
                  className={cn(buttonVariants({ variant: 'outline', size: 'lg' }))}
                >
                  View Architecture
                </Link>
              </div>
            </AnimatedGroup>

            {/* App screenshot */}
            <AnimatedGroup
              preset="fade"
              className="mt-16 sm:mt-20"
            >
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

            {/* Tech badges */}
            <AnimatedGroup
              preset="slide"
              className="mt-16 flex flex-col items-center"
            >
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
      </main>
    </>
  );
}

export { HeroSection };
