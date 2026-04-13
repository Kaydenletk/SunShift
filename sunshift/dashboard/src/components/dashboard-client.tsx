"use client"

import { useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"

interface DashboardClientProps {
  children: React.ReactNode
  /** Interval in milliseconds between auto-refreshes. Default: 60 000 (1 min) */
  refreshIntervalMs?: number
}

/**
 * Thin client wrapper that auto-refreshes server data by calling
 * router.refresh() on a fixed interval. This re-runs the Server Component
 * data fetch without a full page navigation.
 */
export function DashboardClient({
  children,
  refreshIntervalMs = 60_000,
}: DashboardClientProps) {
  const router = useRouter()

  const refresh = useCallback(() => {
    router.refresh()
  }, [router])

  useEffect(() => {
    const id = setInterval(refresh, refreshIntervalMs)
    return () => clearInterval(id)
  }, [refresh, refreshIntervalMs])

  return <>{children}</>
}
