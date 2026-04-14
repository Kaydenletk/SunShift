import { Header } from "@/components/header"
import { HeroStatus } from "@/components/hero-status"
import { QuickStats } from "@/components/quick-stats"
import { StatusCard } from "@/components/status-card"
import { PredictionChart } from "@/components/prediction-chart"
import { SavingsTracker } from "@/components/savings-tracker"
import { HurricaneCard } from "@/components/hurricane-card"
import { OptimalWindows } from "@/components/optimal-windows"
import { DashboardClient } from "@/components/dashboard-client"
import { fetchPredictions } from "@/lib/api"
import type { HourlyForecast, OptimalWindow, PredictionResponse } from "@/types"

// ---------------------------------------------------------------------------
// Mock data — used as fallback when the backend is unreachable.
// This ensures the dashboard always renders something for portfolio demos.
// ---------------------------------------------------------------------------

function buildMockForecast(): HourlyForecast[] {
  return Array.from({ length: 48 }, (_, i) => {
    const hour = new Date()
    hour.setHours(hour.getHours() + i, 0, 0, 0)
    const h = hour.getHours()
    const cost = 16 + 11 * Math.sin(((h - 6) / 24) * 2 * Math.PI)
    return {
      hour: hour.toISOString(),
      cost_cents_kwh: Math.max(5, Math.round(cost * 10) / 10),
      demand_mw: 5000 + 3000 * Math.sin(((h - 6) / 24) * 2 * Math.PI),
      confidence: 0.88,
    }
  })
}

function buildMockWindows(): OptimalWindow[] {
  const today = new Date()
  const at = (h: number) => {
    const d = new Date(today)
    d.setHours(h, 0, 0, 0)
    return d.toISOString()
  }
  return [
    {
      rank: 1,
      start: at(2),
      end: at(5),
      avg_cost_cents_kwh: 6.2,
      estimated_savings_dollars: 4.8,
      workload_recommendation: "Heavy compute — backups, ML training",
    },
    {
      rank: 2,
      start: at(5),
      end: at(8),
      avg_cost_cents_kwh: 8.7,
      estimated_savings_dollars: 3.1,
      workload_recommendation: "Database syncs, large uploads",
    },
    {
      rank: 3,
      start: at(22),
      end: at(24),
      avg_cost_cents_kwh: 10.4,
      estimated_savings_dollars: 2.2,
      workload_recommendation: "Light syncs, analytics jobs",
    },
  ]
}

const MOCK_PREDICTIONS: Pick<
  PredictionResponse,
  "hourly_forecast" | "optimal_windows" | "hurricane_status"
> = {
  hourly_forecast: buildMockForecast(),
  optimal_windows: buildMockWindows(),
  hurricane_status: { active_threats: 0, shield_mode: "standby" },
}

// ---------------------------------------------------------------------------
// Server Component
// ---------------------------------------------------------------------------

export default async function DashboardPage() {
  // Try to fetch live data; fall back to mock on any failure.
  let forecast = MOCK_PREDICTIONS.hourly_forecast
  let windows = MOCK_PREDICTIONS.optimal_windows
  let hurricaneStatus = MOCK_PREDICTIONS.hurricane_status

  try {
    const data = await fetchPredictions("tampa_fl")
    forecast = data.hourly_forecast
    windows = data.optimal_windows
    hurricaneStatus = data.hurricane_status
  } catch {
    // Backend unreachable — mock data stays in place. Silently continue.
  }

  return (
    <DashboardClient refreshIntervalMs={60_000}>
      <div className="flex min-h-screen flex-col bg-gray-50">
        <Header />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <div className="space-y-5">
            {/* Level 1: Hero status banner — first thing users see */}
            <HeroStatus />

            {/* Level 2: Savings + Quick Stats + Hurricane — 3-col grid */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
              <SavingsTracker
                monthlySavings={
                  windows.length > 0
                    ? Math.round(
                        windows.reduce((sum, w) => sum + w.estimated_savings_dollars, 0) * 30
                      )
                    : 142
                }
              />
              <div className="flex flex-col gap-5">
                <QuickStats />
              </div>
              <HurricaneCard
                status={{
                  active_threats: hurricaneStatus.active_threats,
                  shield_mode: hurricaneStatus.shield_mode as "standby" | "active",
                  last_check_minutes_ago: 0,
                }}
              />
            </div>

            {/* Level 3: Prediction chart — full width */}
            <PredictionChart forecast={forecast} />

            {/* Level 3-4: Optimal windows + Status */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <OptimalWindows windows={windows} />
              <StatusCard />
            </div>
          </div>
        </main>
      </div>
    </DashboardClient>
  )
}
