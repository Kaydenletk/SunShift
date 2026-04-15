/**
 * TypeScript types for the AI Scheduler system.
 * These types mirror the backend Pydantic models in sunshift/backend/models/scheduler.py
 */

export type WorkloadType = "BACKUP" | "SYNC" | "AI_TRAIN"
export type Priority = "normal" | "urgent"
export type JobStatus = "scheduled" | "running" | "completed" | "failed"
export type SchedulerMode = "conservative" | "balanced" | "aggressive"
export type RiskLevel = "low" | "medium" | "high"

export interface TimeWindow {
  start: string
  end: string
}

export interface Workload {
  id: string
  agent_id: string
  type: WorkloadType
  size_gb: number
  priority: Priority
  deadline: string | null
  created_at: string
}

export interface ScheduledJob {
  id: string
  workloads: Workload[]
  window: TimeWindow
  estimated_cost: string
  confidence: number
  status: JobStatus
}

export interface BatchQueueStatus {
  count: number
  total_size_gb: number
  oldest_arrival: string | null
  flush_at: string | null
  target_window_start: string | null
}

export interface HourlyCost {
  hour: string
  cost_cents_kwh: number
  confidence: number
}

export interface CostWindow {
  start: string
  end: string
  avg_cost_cents_kwh: number
  confidence: number
  score: number
  weather_risk: RiskLevel
}

export interface ScheduleResponse {
  jobs: ScheduledJob[]
  next_window: CostWindow | null
  batch_queue_status: BatchQueueStatus
  cost_forecast: HourlyCost[]
}

export interface SchedulerSettings {
  min_confidence: number
  lookahead_hours: number
  batch_wait_max_hours: number
  replan_frequency_hours: number
  hurricane_trigger_level: string
}

export interface SubmitWorkloadData {
  agent_id: string
  type: WorkloadType
  size_gb: number
  priority?: Priority
  deadline?: string
}

export interface SubmitWorkloadResponse {
  workload_id: string
  scheduled_window: TimeWindow | null
  batch_queue_position: number | null
  estimated_savings: string
}

export interface EmergencyResponse {
  job_id: string
  status: string
  eta_minutes: number
}

export interface SettingsUpdateResponse {
  mode: SchedulerMode
  effective_settings: SchedulerSettings
}
