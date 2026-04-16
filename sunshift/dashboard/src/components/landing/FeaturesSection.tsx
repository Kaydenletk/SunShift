import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import type { Feature } from './constants';
import { features } from './constants';

function FeatureCard({ feature }: { feature: Feature }) {
  const isInternal = feature.href.startsWith('/') && !feature.href.startsWith('//');
  const linkClass =
    'mt-6 flex items-center gap-2 text-sm font-medium text-primary hover:underline';

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
      {isInternal ? (
        <Link href={feature.href} className={linkClass}>
          <span>{feature.ctaLabel}</span>
          <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
        </Link>
      ) : (
        <a
          href={feature.href}
          target="_blank"
          rel="noreferrer"
          className={linkClass}
        >
          <span>{feature.ctaLabel}</span>
          <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
        </a>
      )}
    </article>
  );
}

function PillarLabel({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="shrink-0 rounded-full bg-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-primary">
        {label}
      </span>
      <div className="h-px flex-1 bg-border" />
    </div>
  );
}

export function FeaturesSection() {
  return (
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

        {/* Pillar 1 — Never Lose Your Data */}
        <div className="mt-16">
          <PillarLabel label="Never Lose Your Data" />
          <div className="mt-4 grid gap-6 sm:grid-cols-2">
            {features.slice(0, 2).map((feature) => (
              <FeatureCard key={feature.title} feature={feature} />
            ))}
          </div>
        </div>

        {/* Pillars 2 & 3 */}
        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <div>
            <PillarLabel label="Never Go Down" />
            <div className="mt-4 space-y-6">
              {features.slice(2, 4).map((feature) => (
                <FeatureCard key={feature.title} feature={feature} />
              ))}
            </div>
          </div>
          <div>
            <PillarLabel label="Never Overpay" />
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
