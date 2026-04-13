import { Header } from "@/components/header"
import { StatusCard } from "@/components/status-card"
import { PredictionChart } from "@/components/prediction-chart"
import { SavingsTracker } from "@/components/savings-tracker"
import { HurricaneCard } from "@/components/hurricane-card"
import { OptimalWindows } from "@/components/optimal-windows"

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <Header />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
        <div className="space-y-5">
          {/* Row 1: Status + Hurricane */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <StatusCard />
            <HurricaneCard />
          </div>

          {/* Row 2: Prediction chart — full width */}
          <PredictionChart />

          {/* Row 3: Savings + Optimal windows */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <SavingsTracker />
            <OptimalWindows />
          </div>
        </div>
      </main>
    </div>
  )
}
