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
