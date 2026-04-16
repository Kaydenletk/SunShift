import Image from 'next/image';
import { ArrowRight, ChevronRight, Shield } from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { AnimatedGroup } from '@/components/ui/animated-group';
import { cn } from '@/lib/utils';
import { techBadges } from './constants';

export function HeroSection() {
  return (
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
  );
}
