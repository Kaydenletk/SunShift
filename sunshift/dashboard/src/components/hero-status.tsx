"use client"

import { useState } from "react"
import { ShieldCheck, Zap, Shield, ChevronDown } from "lucide-react"

type StatusMode = "protected" | "peak" | "hurricane"

interface HeroStatusProps {
  /** Override the initial status for testing / demo purposes */
  initialMode?: StatusMode
}

const STATUS_CONFIG = {
  protected: {
    bg: "bg-emerald-50 border-emerald-200",
    icon: ShieldCheck,
    iconClass: "text-emerald-600",
    title: "All Protected",
    titleClass: "text-emerald-700",
    subtitle: "Your data is being monitored and backed up",
    subtitleClass: "text-emerald-600/70",
    detail: "Last backup: 2h ago",
    detailClass: "text-emerald-600",
  },
  peak: {
    bg: "bg-orange-50 border-orange-200",
    icon: Zap,
    iconClass: "text-orange-500",
    title: "Peak Hours Active",
    titleClass: "text-orange-700",
    subtitle: "Workloads shifted to cloud — avoiding peak pricing",
    subtitleClass: "text-orange-600/70",
    detail: "Saving $4.82 today",
    detailClass: "text-orange-600",
  },
  hurricane: {
    bg: "bg-red-50 border-red-200",
    icon: Shield,
    iconClass: "text-red-500 animate-pulse",
    title: "Hurricane Shield Active",
    titleClass: "text-red-700",
    subtitle: "Protecting 127GB → AWS Ohio",
    subtitleClass: "text-red-600/70",
    detail: "ETA: ~45 min",
    detailClass: "text-red-600",
  },
} as const

const MODE_ORDER: StatusMode[] = ["protected", "peak", "hurricane"]

export function HeroStatus({ initialMode = "protected" }: HeroStatusProps) {
  const [mode, setMode] = useState<StatusMode>(initialMode)
  const config = STATUS_CONFIG[mode]
  const Icon = config.icon
  const uploadPercent = 78

  function cycleMode() {
    setMode((prev) => {
      const idx = MODE_ORDER.indexOf(prev)
      return MODE_ORDER[(idx + 1) % MODE_ORDER.length]
    })
  }

  return (
    <div className={`w-full rounded-xl border p-4 sm:p-5 ${config.bg}`}>
      {/* Top row: icon + title + detail */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <Icon
            className={`mt-0.5 h-6 w-6 shrink-0 ${config.iconClass}`}
            aria-hidden="true"
          />
          <div className="min-w-0">
            <h2 className={`text-lg font-semibold leading-tight ${config.titleClass}`}>
              {config.title}
            </h2>
            <p className={`mt-0.5 text-sm ${config.subtitleClass}`}>
              {config.subtitle}
            </p>
          </div>
        </div>
        <span className={`shrink-0 text-sm font-medium ${config.detailClass}`}>
          {mode === "hurricane" ? `Uploading: ${uploadPercent}%` : config.detail}
        </span>
      </div>

      {/* Hurricane progress bar */}
      {mode === "hurricane" && (
        <div className="mt-3 space-y-1.5">
          <div className="flex items-center justify-between text-xs text-red-600/70">
            <span>{config.detail}</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-red-100">
            <div
              className="h-full rounded-full bg-red-500 transition-all duration-700"
              style={{ width: `${uploadPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Demo mode switcher — small, unobtrusive */}
      <button
        type="button"
        onClick={cycleMode}
        className="mt-3 flex items-center gap-1 rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-black/5 cursor-pointer transition-colors"
      >
        Demo: cycle status
        <ChevronDown className="h-3 w-3" aria-hidden="true" />
      </button>
    </div>
  )
}
