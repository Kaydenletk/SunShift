import { riskStats } from './constants';

export function RealityCheckSection() {
  return (
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
  );
}
