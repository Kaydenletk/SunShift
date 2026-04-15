"use client"

import { useState, useCallback } from "react"
import type {
  ScheduleResponse,
  SchedulerMode,
  SchedulerSettings,
  SubmitWorkloadData,
  SubmitWorkloadResponse,
  EmergencyResponse,
  SettingsUpdateResponse,
} from "../types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface UseSchedulerResult {
  schedule: ScheduleResponse | null
  settings: SchedulerSettings | null
  mode: SchedulerMode
  isLoading: boolean
  error: Error | null
  fetchSchedule: (agentId: string) => Promise<void>
  updateMode: (mode: SchedulerMode) => Promise<void>
  submitWorkload: (data: SubmitWorkloadData) => Promise<SubmitWorkloadResponse>
  triggerEmergency: (
    agentId: string,
    reason: "hurricane" | "manual"
  ) => Promise<EmergencyResponse>
}

export function useScheduler(): UseSchedulerResult {
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null)
  const [settings, setSettings] = useState<SchedulerSettings | null>(null)
  const [mode, setMode] = useState<SchedulerMode>("balanced")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchSchedule = useCallback(async (agentId: string) => {
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
  }, [])

  const updateMode = useCallback(async (newMode: SchedulerMode) => {
    setIsLoading(true)
    setError(null)
    try {
      const resp = await fetch(`${API_BASE}/api/v1/scheduler/settings`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: newMode }),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data: SettingsUpdateResponse = await resp.json()
      setMode(data.mode)
      setSettings(data.effective_settings)
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [])

  const submitWorkload = useCallback(
    async (data: SubmitWorkloadData): Promise<SubmitWorkloadResponse> => {
      const resp = await fetch(`${API_BASE}/api/v1/scheduler/workloads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      return resp.json()
    },
    []
  )

  const triggerEmergency = useCallback(
    async (
      agentId: string,
      reason: "hurricane" | "manual"
    ): Promise<EmergencyResponse> => {
      const resp = await fetch(`${API_BASE}/api/v1/scheduler/emergency`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: agentId, reason }),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      return resp.json()
    },
    []
  )

  return {
    schedule,
    settings,
    mode,
    isLoading,
    error,
    fetchSchedule,
    updateMode,
    submitWorkload,
    triggerEmergency,
  }
}
