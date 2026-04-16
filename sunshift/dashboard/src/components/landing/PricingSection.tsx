import Link from 'next/link';
import { ArrowRight, Zap } from 'lucide-react';
import { buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function PricingSection() {
  return (
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
          <div className="rounded-xl border border-border bg-card p-8 shadow-sm">
            <h3 className="text-lg font-semibold text-foreground">Starter</h3>
            <p className="mt-1 text-sm text-muted-foreground">For small offices with 1–3 servers</p>
            <div className="mt-6 flex items-baseline gap-1">
              <span className="text-4xl font-bold text-foreground">$49</span>
              <span className="text-muted-foreground">/month</span>
            </div>
            <ul className="mt-8 space-y-3 text-sm text-muted-foreground">
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> 1 on-prem agent</li>
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> TOU cost optimization</li>
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> Hurricane Shield alerts</li>
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> Dashboard access</li>
            </ul>
            <Link
              href="/dashboard"
              className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'mt-8 w-full')}
            >
              Start Free Trial
            </Link>
          </div>

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
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> Up to 5 agents</li>
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> ML-powered scheduling</li>
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> Auto hurricane backup</li>
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> HIPAA compliance</li>
              <li className="flex items-center gap-2"><Zap className="size-4 text-primary" /> Priority support</li>
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
  );
}
