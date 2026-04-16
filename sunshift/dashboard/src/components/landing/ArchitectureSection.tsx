import Link from 'next/link';
import { ArrowRight, FileText, MapPin } from 'lucide-react';
import type { StoryMoment } from './constants';
import { storyMoments, trustItems, adrLinks } from './constants';

function StoryMomentCard({ moment, index }: { moment: StoryMoment; index: number }) {
  const isInternal = moment.href.startsWith('/') && !moment.href.startsWith('//');
  const linkClass = 'mt-4 flex items-center gap-2 text-sm font-medium text-primary hover:underline';

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
      <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
        {moment.description}
      </p>
      <p className="mt-5 border-t border-border pt-4 font-mono text-xs text-muted-foreground/60">
        {moment.tech}
      </p>
      {isInternal ? (
        <Link href={moment.href} className={linkClass}>
          <span>{moment.ctaLabel}</span>
          <ArrowRight className="size-4" />
        </Link>
      ) : (
        <a href={moment.href} target="_blank" rel="noreferrer" className={linkClass}>
          <span>{moment.ctaLabel}</span>
          <ArrowRight className="size-4" />
        </a>
      )}
    </article>
  );
}

export function ArchitectureSection() {
  return (
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

        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {storyMoments.map((moment, index) => (
            <StoryMomentCard key={moment.moment} moment={moment} index={index} />
          ))}
        </div>

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
