interface Metric {
  label: string
  value: string
  sub?: string
  trend?: "up" | "down"
}

const METRICS: Metric[] = [
  {
    label: "Current Cost",
    value: "12.4¢/kWh",
    trend: "down",
  },
  {
    label: "Today's Savings",
    value: "$4.82",
    trend: "up",
  },
  {
    label: "Next Optimal Window",
    value: "11PM – 5AM",
  },
  {
    label: "Prediction Confidence",
    value: "91%",
  },
]

function TrendArrow({ direction }: { direction: "up" | "down" }) {
  if (direction === "down") {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-green-500"
        aria-label="trending down (good)"
      >
        <path d="m7 7 10 10" />
        <path d="M17 7v10H7" />
      </svg>
    )
  }
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-green-500"
      aria-label="trending up (good)"
    >
      <path d="m7 17 10-10" />
      <path d="M7 7h10v10" />
    </svg>
  )
}

export function MetricsBar() {
  return (
    <div className="w-full rounded-xl border border-gray-100 bg-white px-4 py-3 shadow-sm">
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-4 sm:gap-y-0 sm:divide-x sm:divide-gray-100">
        {METRICS.map((metric) => (
          <div
            key={metric.label}
            className="flex flex-col gap-0.5 px-0 sm:px-4 first:sm:pl-0 last:sm:pr-0"
          >
            <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {metric.label}
            </dt>
            <dd className="flex items-center gap-1.5">
              <span className="font-mono text-lg font-semibold text-foreground">
                {metric.value}
              </span>
              {metric.trend && <TrendArrow direction={metric.trend} />}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
