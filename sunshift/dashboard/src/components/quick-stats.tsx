"use client"

import { CheckCircle2, Clock, Gauge, Tag } from "lucide-react"
import type { ReactNode } from "react"

interface StatItem {
  icon: ReactNode
  label: string
  value: string
  accent?: string
}

const STATS: StatItem[] = [
  {
    icon: <CheckCircle2 className="h-4 w-4 text-green-500" aria-hidden="true" />,
    label: "Last Backup",
    value: "2 hours ago",
    accent: "text-green-600",
  },
  {
    icon: <Gauge className="h-4 w-4 text-sky-500" aria-hidden="true" />,
    label: "Prediction Confidence",
    value: "91%",
    accent: "text-sky-600",
  },
  {
    icon: <Clock className="h-4 w-4 text-violet-500" aria-hidden="true" />,
    label: "Next Window",
    value: "11PM – 5AM",
    accent: "text-violet-600",
  },
  {
    icon: <Tag className="h-4 w-4 text-gray-400" aria-hidden="true" />,
    label: "Model Version",
    value: "v0.1.0",
  },
]

export function QuickStats() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {STATS.map((stat) => (
        <div
          key={stat.label}
          className="flex flex-col gap-1.5 rounded-xl border border-gray-100 bg-white p-3 shadow-sm"
        >
          <div className="flex items-center gap-1.5">
            {stat.icon}
            <span className="text-xs font-medium text-muted-foreground">
              {stat.label}
            </span>
          </div>
          <span className={`font-mono text-sm font-semibold ${stat.accent ?? "text-foreground"}`}>
            {stat.value}
          </span>
        </div>
      ))}
    </div>
  )
}
