"use client"

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceArea,
  ResponsiveContainer,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { HourlyForecast } from "@/types"

function generateMockForecast(): HourlyForecast[] {
  return Array.from({ length: 48 }, (_, i) => {
    const hour = new Date()
    hour.setHours(hour.getHours() + i, 0, 0, 0)
    const h = hour.getHours()
    const cost = 16 + 11 * Math.sin(((h - 6) / 24) * 2 * Math.PI)
    return {
      hour: hour.toISOString(),
      cost_cents_kwh: Math.max(5, Math.round(cost * 10) / 10),
      demand_mw: 5000 + 3000 * Math.sin(((h - 6) / 24) * 2 * Math.PI),
      confidence: 0.85 + Math.random() * 0.1,
    }
  })
}

const MOCK_FORECAST = generateMockForecast()

function formatHour(isoString: string): string {
  const d = new Date(isoString)
  const h = d.getHours()
  if (h === 0) return "12AM"
  if (h === 12) return "12PM"
  return h < 12 ? `${h}AM` : `${h - 12}PM`
}

interface TooltipPayloadItem {
  value: number
  payload: HourlyForecast
}

interface CustomTooltipProps {
  active?: boolean
  payload?: TooltipPayloadItem[]
  label?: string
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload as HourlyForecast
  const time = new Date(d.hour).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
  return (
    <div className="rounded-lg border border-border bg-white px-3 py-2 shadow-lg text-sm">
      <p className="font-medium text-foreground">{time}</p>
      <p className="font-mono text-[#0ea5e9]">{d.cost_cents_kwh.toFixed(1)}¢/kWh</p>
      <p className="text-xs text-muted-foreground">
        Confidence: {(d.confidence * 100).toFixed(0)}%
      </p>
    </div>
  )
}

// Peak window indices (12PM–9PM): find which data points fall in that range
function isPeakHour(isoString: string): boolean {
  const h = new Date(isoString).getHours()
  return h >= 12 && h < 21
}

export function PredictionChart() {
  // Find the first and last index of peak hours for ReferenceArea
  const peakStart = MOCK_FORECAST.findIndex((d) => isPeakHour(d.hour))
  const peakEnd = MOCK_FORECAST.reduce(
    (last, d, i) => (isPeakHour(d.hour) ? i : last),
    -1
  )

  const peakX1 = peakStart >= 0 ? MOCK_FORECAST[peakStart].hour : undefined
  const peakX2 = peakEnd >= 0 ? MOCK_FORECAST[peakEnd].hour : undefined

  return (
    <Card className="rounded-xl shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base font-semibold">48-Hour Energy Forecast</CardTitle>
            <CardDescription className="mt-0.5">
              Electricity cost prediction — Tampa, FL
            </CardDescription>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <span className="inline-block h-2.5 w-2.5 rounded-sm bg-[#0ea5e9]/30 border border-[#0ea5e9]" />
              Cost
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2.5 w-2.5 rounded-sm bg-[#e9520d]/20 border border-[#e9520d]/40" />
              Peak hours
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={MOCK_FORECAST}
              margin={{ top: 8, right: 8, left: -8, bottom: 0 }}
            >
              <defs>
                <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis
                dataKey="hour"
                tickFormatter={formatHour}
                tick={{ fontSize: 11, fill: "#9ca3af" }}
                tickLine={false}
                axisLine={false}
                interval={5}
              />
              <YAxis
                tickFormatter={(v: number) => `${v}¢`}
                tick={{ fontSize: 11, fill: "#9ca3af" }}
                tickLine={false}
                axisLine={false}
                domain={[0, 32]}
                ticks={[0, 8, 16, 24, 32]}
              />
              {peakX1 && peakX2 && (
                <ReferenceArea
                  x1={peakX1}
                  x2={peakX2}
                  fill="#e9520d"
                  fillOpacity={0.07}
                  stroke="#e9520d"
                  strokeOpacity={0.2}
                  strokeDasharray="4 4"
                  label={{
                    value: "Peak",
                    position: "insideTop",
                    fontSize: 10,
                    fill: "#e9520d",
                    opacity: 0.7,
                  }}
                />
              )}
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="cost_cents_kwh"
                stroke="#0ea5e9"
                strokeWidth={2}
                fill="url(#costGradient)"
                dot={false}
                activeDot={{ r: 4, fill: "#0ea5e9", strokeWidth: 0 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
