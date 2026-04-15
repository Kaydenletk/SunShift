"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import type { ScheduleResponse } from "../types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const POLL_INTERVAL_MS = 30000 // 30 seconds

interface UseSchedulePollingResult {
  schedule: ScheduleResponse | null
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

export function useSchedulePolling(
  agentId: string,
  enabled: boolean = true
): UseSchedulePollingResult {
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchSchedule = useCallback(async () => {
    if (!agentId) return

    setIsLoading(true)
    setError(null)
    try {
      const resp = await fetch(
        `${API_BASE}/api/v1/scheduler/schedule?agent_id=${encodeURIComponent(agentId)}`
      )
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data: ScheduleResponse = await resp.json()
      setSchedule(data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [agentId])

  useEffect(() => {
    if (!enabled || !agentId) return

    // Initial fetch
    fetchSchedule()

    // Set up polling
    intervalRef.current = setInterval(() => {
      fetchSchedule()
    }, POLL_INTERVAL_MS)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [agentId, enabled, fetchSchedule])

  return { schedule, isLoading, error, refetch: fetchSchedule }
}
