import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

type ShieldMode = "standby" | "active"

interface HurricaneStatus {
  active_threats: number
  shield_mode: ShieldMode
  last_check_minutes_ago: number
}

const MOCK_HURRICANE_STATUS: HurricaneStatus = {
  active_threats: 0,
  shield_mode: "standby",
  last_check_minutes_ago: 30,
}

interface HurricaneCardProps {
  status?: HurricaneStatus
}

export function HurricaneCard({ status = MOCK_HURRICANE_STATUS }: HurricaneCardProps) {
  const isActive = status.shield_mode === "active"

  return (
    <Card className="rounded-xl shadow-sm transition-shadow duration-200 hover:shadow-md cursor-default">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Hurricane Shield
          </CardTitle>
          {isActive ? (
            <Badge className="relative bg-red-500 text-white border-0">
              <span className="absolute -inset-0.5 animate-ping rounded-full bg-red-400 opacity-60" />
              <span className="relative">ACTIVE</span>
            </Badge>
          ) : (
            <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50">
              Standby
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Shield icon area */}
        <div
          className={`flex items-center justify-center rounded-xl py-6 ${
            isActive ? "bg-red-50" : "bg-blue-50"
          }`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={isActive ? "text-red-500" : "text-blue-500"}
            aria-hidden="true"
          >
            <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
            {!isActive && (
              <path d="m9 12 2 2 4-4" />
            )}
          </svg>
        </div>

        {/* Status info */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2">
            <span className="text-muted-foreground">Active threats</span>
            <span className="font-mono font-semibold text-foreground">
              {status.active_threats}
            </span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2">
            <span className="text-muted-foreground">Last check</span>
            <span className="font-medium text-foreground">
              {status.last_check_minutes_ago} min ago
            </span>
          </div>
        </div>

        {isActive && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Uploading to AWS Ohio</span>
              <span className="font-mono font-semibold">78%</span>
            </div>
            <div className="h-2 rounded-full bg-red-100">
              <div className="h-full rounded-full bg-red-500 transition-all" style={{ width: "78%" }} />
            </div>
            <p className="text-xs text-muted-foreground">127 GB — ETA ~45 minutes</p>
          </div>
        )}

        <p className={`text-xs text-center ${isActive ? "text-red-600" : "text-blue-600"}`}>
          {isActive
            ? "Workloads rescheduled for storm safety"
            : "No active storms — operating normally"}
        </p>
      </CardContent>
    </Card>
  )
}
