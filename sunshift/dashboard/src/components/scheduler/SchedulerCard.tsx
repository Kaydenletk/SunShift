"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Calendar, CheckCircle2, Layers, DollarSign } from "lucide-react"
import { useSchedulePolling } from "./hooks/useSchedulePolling"
import type { SchedulerMode } from "./types"

interface SchedulerCardProps {
  agentId: string
  mode: SchedulerMode
  onModeChange?: (mode: SchedulerMode) => void
}

const MODE_CONFIG = {
  conservative: {
    label: "Conservative",
    badgeClass: "bg-amber-50 text-amber-700 border-amber-200",
  },
  balanced: {
    label: "Balanced",
    badgeClass: "bg-green-50 text-green-700 border-green-200",
  },
  aggressive: {
    label: "Aggressive",
    badgeClass: "bg-orange-50 text-orange-700 border-orange-200",
  },
} satisfies Record<SchedulerMode, { label: string; badgeClass: string }>

function formatTime(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
}

export function SchedulerCard({ agentId, mode }: SchedulerCardProps) {
  const { schedule, isLoading, error } = useSchedulePolling(agentId)

  const modeConfig = MODE_CONFIG[mode]
  const nextJob = schedule?.jobs.find((j) => j.status === "scheduled")
  const completedToday =
    schedule?.jobs.filter((j) => j.status === "completed").length ?? 0
  const queueCount = schedule?.batch_queue_status.count ?? 0

  // Calculate estimated savings (mock for now)
  const savedToday = 12.5

  if (isLoading && !schedule) {
    return (
      <Card className="rounded-xl shadow-sm">
        <CardHeader className="pb-2">
          <div className="h-5 bg-gray-100 rounded w-1/3 animate-pulse" />
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="h-20 bg-gray-100 rounded animate-pulse" />
          <div className="grid grid-cols-3 gap-3">
            <div className="h-16 bg-gray-100 rounded animate-pulse" />
            <div className="h-16 bg-gray-100 rounded animate-pulse" />
            <div className="h-16 bg-gray-100 rounded animate-pulse" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="rounded-xl shadow-sm transition-shadow duration-200 hover:shadow-md cursor-default">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            AI Scheduler
          </CardTitle>
          <Badge variant="outline" className={modeConfig.badgeClass}>
            {modeConfig.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Next Job Preview */}
        <div className="rounded-lg bg-blue-50 p-4">
          <div className="flex items-start gap-3">
            <Calendar className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-xs text-blue-600 font-medium mb-1">
                Next Scheduled Job
              </p>
              {nextJob ? (
                <>
                  <p className="text-sm font-semibold text-blue-900">
                    {formatTime(nextJob.window.start)} -{" "}
                    {formatTime(nextJob.window.end)}
                  </p>
                  <p className="text-xs text-blue-700 mt-1">
                    {nextJob.workloads.length} workload
                    {nextJob.workloads.length > 1 ? "s" : ""} batched
                    <span className="mx-1.5">|</span>
                    {(nextJob.confidence * 100).toFixed(0)}% confidence
                  </p>
                </>
              ) : (
                <p className="text-sm text-blue-700">No jobs scheduled</p>
              )}
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-2">
          <div className="rounded-lg bg-gray-50 p-3 text-center">
            <Layers className="h-4 w-4 text-blue-500 mx-auto mb-1" />
            <p className="text-lg font-bold text-foreground">{queueCount}</p>
            <p className="text-xs text-muted-foreground">In Queue</p>
          </div>
          <div className="rounded-lg bg-gray-50 p-3 text-center">
            <CheckCircle2 className="h-4 w-4 text-green-500 mx-auto mb-1" />
            <p className="text-lg font-bold text-foreground">{completedToday}</p>
            <p className="text-xs text-muted-foreground">Completed</p>
          </div>
          <div className="rounded-lg bg-gray-50 p-3 text-center">
            <DollarSign className="h-4 w-4 text-purple-500 mx-auto mb-1" />
            <p className="text-lg font-bold text-foreground">
              ${savedToday.toFixed(0)}
            </p>
            <p className="text-xs text-muted-foreground">Saved Today</p>
          </div>
        </div>

        {/* Queue Status */}
        {queueCount > 0 && schedule?.batch_queue_status.flush_at && (
          <div className="flex items-center justify-between text-xs text-muted-foreground rounded-lg bg-gray-50 px-3 py-2">
            <span>Queue flushes at</span>
            <span className="font-medium text-foreground">
              {formatTime(schedule.batch_queue_status.flush_at)}
            </span>
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2">
            <p className="text-xs text-red-600">Error: {error.message}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
