"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { OptimalWindow } from "@/types"

const MOCK_WINDOWS: OptimalWindow[] = [
  {
    rank: 1,
    start: (() => {
      const d = new Date()
      d.setHours(2, 0, 0, 0)
      return d.toISOString()
    })(),
    end: (() => {
      const d = new Date()
      d.setHours(5, 0, 0, 0)
      return d.toISOString()
    })(),
    avg_cost_cents_kwh: 6.2,
    estimated_savings_dollars: 4.8,
    workload_recommendation: "Heavy compute — backups, ML training",
  },
  {
    rank: 2,
    start: (() => {
      const d = new Date()
      d.setHours(5, 0, 0, 0)
      return d.toISOString()
    })(),
    end: (() => {
      const d = new Date()
      d.setHours(8, 0, 0, 0)
      return d.toISOString()
    })(),
    avg_cost_cents_kwh: 8.7,
    estimated_savings_dollars: 3.1,
    workload_recommendation: "Database syncs, large uploads",
  },
  {
    rank: 3,
    start: (() => {
      const d = new Date()
      d.setHours(22, 0, 0, 0)
      return d.toISOString()
    })(),
    end: (() => {
      const d = new Date()
      d.setHours(24, 0, 0, 0)
      return d.toISOString()
    })(),
    avg_cost_cents_kwh: 10.4,
    estimated_savings_dollars: 2.2,
    workload_recommendation: "Light syncs, analytics jobs",
  },
]

function formatTimeRange(startIso: string, endIso: string): string {
  const fmt = (iso: string) =>
    new Date(iso).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    })
  return `${fmt(startIso)} – ${fmt(endIso)}`
}

const RANK_STYLES = {
  1: {
    border: "border-green-200",
    bg: "bg-green-50",
    rankBg: "bg-green-500",
    costColor: "text-green-700",
    badgeClass: "bg-green-100 text-green-700 border-green-200",
  },
  2: {
    border: "border-blue-100",
    bg: "bg-blue-50/40",
    rankBg: "bg-sky-500",
    costColor: "text-sky-500",
    badgeClass: "bg-blue-50 text-blue-700 border-blue-100",
  },
  3: {
    border: "border-gray-100",
    bg: "bg-gray-50/50",
    rankBg: "bg-gray-400",
    costColor: "text-gray-600",
    badgeClass: "bg-gray-100 text-gray-600 border-gray-200",
  },
} as const

interface OptimalWindowsProps {
  windows?: OptimalWindow[]
}

export function OptimalWindows({ windows = MOCK_WINDOWS }: OptimalWindowsProps) {
  const top3 = windows.slice(0, 3)

  return (
    <Card className="rounded-xl shadow-sm transition-shadow duration-200 hover:shadow-md cursor-default">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold">Best Times to Run Workloads</CardTitle>
        <CardDescription>
          Ranked by lowest electricity cost. Schedule backups and heavy compute during these windows.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {top3.map((win) => {
          const rank = win.rank as 1 | 2 | 3
          const style = RANK_STYLES[rank] ?? RANK_STYLES[3]

          return (
            <div
              key={win.rank}
              className={`flex items-start gap-3 rounded-xl border p-3 ${style.border} ${style.bg}`}
            >
              {/* Rank badge */}
              <div
                className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${style.rankBg}`}
              >
                {win.rank}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-foreground truncate">
                    {formatTimeRange(win.start, win.end)}
                  </p>
                  <span className={`font-mono text-sm font-bold shrink-0 ${style.costColor}`}>
                    {win.avg_cost_cents_kwh.toFixed(1)}¢
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground truncate">
                  {win.workload_recommendation}
                </p>
                <div className="mt-1.5 flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={`text-xs h-4 ${style.badgeClass}`}
                  >
                    Save ${win.estimated_savings_dollars.toFixed(2)}
                  </Badge>
                  {win.rank === 1 && (
                    <Badge
                      variant="outline"
                      className="text-xs h-4 bg-green-100 text-green-700 border-green-200"
                    >
                      Recommended
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
