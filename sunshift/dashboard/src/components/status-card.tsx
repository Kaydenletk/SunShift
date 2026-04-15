"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { AgentStatus } from "@/types"

interface StatusCardProps {
  status?: AgentStatus
}

const STATUS_CONFIG = {
  online: {
    label: "Monitoring Active",
    dotClass: "bg-green-500",
    pulseClass: "animate-ping bg-green-400",
    textClass: "text-green-600",
    bgClass: "bg-green-50",
  },
  syncing: {
    label: "Syncing Data",
    dotClass: "bg-amber-500",
    pulseClass: "animate-ping bg-amber-400",
    textClass: "text-amber-600",
    bgClass: "bg-amber-50",
  },
  error: {
    label: "System Error",
    dotClass: "bg-red-500",
    pulseClass: "animate-ping bg-red-400",
    textClass: "text-red-600",
    bgClass: "bg-red-50",
  },
  offline: {
    label: "Agent Offline",
    dotClass: "bg-gray-400",
    pulseClass: "bg-gray-300",
    textClass: "text-gray-500",
    bgClass: "bg-gray-50",
  },
} satisfies Record<AgentStatus["status"], {
  label: string
  dotClass: string
  pulseClass: string
  textClass: string
  bgClass: string
}>

const MOCK_STATUS: AgentStatus = {
  agent_id: "sunshift-agent-01",
  status: "online",
  last_seen: new Date().toISOString(),
  cpu_percent: 12.4,
  memory_percent: 38.7,
  disk_percent: 54.1,
  last_sync: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
  bytes_synced: 1_240_832,
}

function formatRelativeTime(isoString: string | null): string {
  if (!isoString) return "Never"
  const diff = Date.now() - new Date(isoString).getTime()
  const minutes = Math.floor(diff / 60_000)
  if (minutes < 1) return "Just now"
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.floor(minutes / 60)
  return `${hours}h ago`
}

export function StatusCard({ status = MOCK_STATUS }: StatusCardProps) {
  const config = STATUS_CONFIG[status.status]

  return (
    <Card className="rounded-xl shadow-sm transition-shadow duration-200 hover:shadow-md cursor-default">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            System Protection
          </CardTitle>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-muted-foreground"
            aria-hidden="true"
          >
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Backup status — promoted to top */}
        <div className="flex items-center gap-2 rounded-lg bg-green-50 px-3 py-2.5">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="shrink-0 text-green-600"
            aria-hidden="true"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <span className="text-sm font-semibold text-green-700" suppressHydrationWarning>
            Last backup: {formatRelativeTime(status.last_sync)}
          </span>
        </div>

        {/* Main status indicator */}
        <div className={`flex items-center gap-3 rounded-lg p-3 ${config.bgClass}`}>
          <div className="relative flex h-3 w-3 shrink-0">
            <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${config.pulseClass}`} />
            <span className={`relative inline-flex h-3 w-3 rounded-full ${config.dotClass}`} />
          </div>
          <span className={`text-sm font-semibold ${config.textClass}`}>
            {config.label}
          </span>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="rounded-lg bg-gray-50 p-2">
            <p className="text-xs text-muted-foreground">CPU</p>
            <p className="font-mono text-sm font-semibold">
              {status.cpu_percent != null ? `${status.cpu_percent.toFixed(0)}%` : "—"}
            </p>
          </div>
          <div className="rounded-lg bg-gray-50 p-2">
            <p className="text-xs text-muted-foreground">Memory</p>
            <p className="font-mono text-sm font-semibold">
              {status.memory_percent != null ? `${status.memory_percent.toFixed(0)}%` : "—"}
            </p>
          </div>
          <div className="rounded-lg bg-gray-50 p-2">
            <p className="text-xs text-muted-foreground">Disk</p>
            <p className="font-mono text-sm font-semibold">
              {status.disk_percent != null ? `${status.disk_percent.toFixed(0)}%` : "—"}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="space-y-1 text-xs text-muted-foreground">
          <div className="flex justify-between">
            <span>Last seen</span>
            <span className="font-medium text-foreground" suppressHydrationWarning>
              {formatRelativeTime(status.last_seen)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
