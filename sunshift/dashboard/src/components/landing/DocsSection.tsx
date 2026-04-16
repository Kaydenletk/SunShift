import Link from 'next/link';
import { ArrowRight, GitBranch } from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { REPO_URL } from './constants';

export function DocsSection() {
  return (
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
            <p><span className="text-green-400">$</span> git clone {REPO_URL}.git</p>
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
          <Link href="/dashboard" className={cn(buttonVariants({ size: 'lg' }))}>
            Live Dashboard
            <ArrowRight className="ml-1 size-4" />
          </Link>
          <Link
            href={REPO_URL}
            className={cn(buttonVariants({ variant: 'outline', size: 'lg' }))}
          >
            <GitBranch className="mr-1.5 size-4" />
            View on GitHub
          </Link>
        </div>
      </div>
    </section>
  );
}
