"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Check, ChevronDown, ChevronRight, Shield, Zap, Target } from "lucide-react"
import type { SchedulerMode, SchedulerSettings } from "./types"

interface ModeSelectorProps {
  currentMode: SchedulerMode
  settings: SchedulerSettings | null
  onModeChange: (mode: SchedulerMode) => void
  isLoading?: boolean
}

const MODES: Array<{
  id: SchedulerMode
  name: string
  description: string
  icon: typeof Shield
  colorClass: string
  selectedBg: string
}> = [
  {
    id: "conservative",
    name: "Conservative",
    description: "Max safety, may miss some savings",
    icon: Shield,
    colorClass: "text-amber-600",
    selectedBg: "bg-amber-50 border-amber-300",
  },
  {
    id: "balanced",
    name: "Balanced",
    description: "Recommended for most users",
    icon: Target,
    colorClass: "text-green-600",
    selectedBg: "bg-green-50 border-green-300",
  },
  {
    id: "aggressive",
    name: "Aggressive",
    description: "Max savings, longer wait times",
    icon: Zap,
    colorClass: "text-orange-600",
    selectedBg: "bg-orange-50 border-orange-300",
  },
]

export function ModeSelector({
  currentMode,
  settings,
  onModeChange,
  isLoading = false,
}: ModeSelectorProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  return (
    <Card className="rounded-xl shadow-sm transition-shadow duration-200 hover:shadow-md cursor-default">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Scheduler Mode
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {MODES.map((mode) => {
          const isSelected = mode.id === currentMode
          const Icon = mode.icon
          return (
            <button
              key={mode.id}
              onClick={() => onModeChange(mode.id)}
              disabled={isLoading}
              className={`w-full p-3 rounded-lg text-left transition-all border ${
                isSelected
                  ? mode.selectedBg
                  : "bg-white border-gray-200 hover:border-gray-300 hover:bg-gray-50"
              } ${isLoading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`p-2 rounded-lg ${
                    isSelected ? "bg-white/80" : "bg-gray-100"
                  }`}
                >
                  <Icon className={`h-4 w-4 ${mode.colorClass}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p
                      className={`font-medium ${
                        isSelected ? mode.colorClass : "text-foreground"
                      }`}
                    >
                      {mode.name}
                    </p>
                    {isSelected && (
                      <Check className={`h-4 w-4 ${mode.colorClass}`} />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {mode.description}
                  </p>
                </div>
              </div>
            </button>
          )
        })}

        {/* Advanced Settings Toggle */}
        <div className="pt-2 border-t border-gray-100">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full py-1"
          >
            {showAdvanced ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
            Advanced Settings
          </button>

          {showAdvanced && settings && (
            <div className="mt-3 space-y-2 text-sm rounded-lg bg-gray-50 p-3">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Min Confidence</span>
                <span className="font-medium text-foreground">
                  {(settings.min_confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Lookahead Horizon</span>
                <span className="font-medium text-foreground">
                  {settings.lookahead_hours}h
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Max Batch Wait</span>
                <span className="font-medium text-foreground">
                  {settings.batch_wait_max_hours}h
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Replan Frequency</span>
                <span className="font-medium text-foreground">
                  {settings.replan_frequency_hours}h
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Hurricane Trigger</span>
                <span className="font-medium text-foreground capitalize">
                  {settings.hurricane_trigger_level}
                </span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
