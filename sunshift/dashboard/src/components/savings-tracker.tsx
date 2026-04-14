"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const MOCK_SAVINGS_DOLLARS = 142
const MONTHLY_GOAL = 160

function useCountUp(target: number, durationMs = 1200): number {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      setCount(target)
      return
    }

    const startTime = performance.now()

    function step(now: number) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / durationMs, 1)
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.round(target * eased))
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }

    const raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
  }, [target, durationMs])

  return count
}

interface SavingsTrackerProps {
  monthlySavings?: number
}

export function SavingsTracker({ monthlySavings = MOCK_SAVINGS_DOLLARS }: SavingsTrackerProps) {
  const annualEstimate = Math.round(monthlySavings * 12)
  const displayValue = useCountUp(monthlySavings)

  return (
    <Card className="rounded-xl shadow-sm transition-shadow duration-200 hover:shadow-md cursor-default">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          You Saved
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Big number */}
        <div className="flex items-end gap-1">
          <span className="font-mono text-5xl font-bold text-green-600">
            ${displayValue}
          </span>
          <span className="mb-1.5 text-sm text-muted-foreground">/ month</span>
        </div>

        <p className="text-sm text-muted-foreground">
          by scheduling workloads during off-peak hours
        </p>

        {/* Divider-like progress bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Monthly goal</span>
            <span className="font-medium text-green-600">
              {Math.round((monthlySavings / MONTHLY_GOAL) * 100)}%
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-green-500 transition-all duration-1000"
              style={{ width: `${Math.min((monthlySavings / MONTHLY_GOAL) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Annual estimate */}
        <div className="rounded-lg bg-green-50 px-3 py-2.5">
          <p className="text-xs text-green-700/70">Estimated annual savings</p>
          <p className="font-mono text-lg font-semibold text-green-700">
            ${annualEstimate.toLocaleString()}
          </p>
        </div>

        {/* Breakdown */}
        <div className="space-y-1.5 text-xs text-muted-foreground">
          <div className="flex justify-between">
            <span>Off-peak scheduling</span>
            <span className="font-medium text-foreground font-mono">$89</span>
          </div>
          <div className="flex justify-between">
            <span>Peak avoidance</span>
            <span className="font-medium text-foreground font-mono">$53</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
