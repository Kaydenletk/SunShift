import { Badge } from "@/components/ui/badge"

export function Header() {
  const now = new Date()
  const dateStr = now.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  })

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo + name */}
        <div className="flex items-center gap-3">
          <div
            className="flex h-8 w-8 items-center justify-center rounded-lg text-white font-bold text-sm"
            style={{ backgroundColor: "#0ea5e9" }}
          >
            S
          </div>
          <span className="text-lg font-semibold tracking-tight text-foreground">
            SunShift
          </span>
          <Badge variant="outline" className="hidden sm:inline-flex text-[#0ea5e9] border-[#0ea5e9]/30 bg-[#0ea5e9]/5">
            AI-Powered
          </Badge>
        </div>

        {/* Location + date */}
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            <span className="font-medium text-foreground">Tampa, FL</span>
          </div>
          <span className="hidden md:block">{dateStr}</span>
        </div>
      </div>
    </header>
  )
}
