export interface HourlyForecast {
  hour: string;
  cost_cents_kwh: number;
  demand_mw: number;
  confidence: number;
}

export interface OptimalWindow {
  rank: number;
  start: string;
  end: string;
  avg_cost_cents_kwh: number;
  estimated_savings_dollars: number;
  workload_recommendation: string;
}

export interface PredictionResponse {
  prediction_id: string;
  location: string;
  generated_at: string;
  model_version: string;
  hourly_forecast: HourlyForecast[];
  optimal_windows: OptimalWindow[];
  explanation: string;
  hurricane_status: {
    active_threats: number;
    shield_mode: string;
  };
}

export interface AgentStatus {
  agent_id: string;
  status: "online" | "offline" | "syncing" | "error";
  last_seen: string;
  cpu_percent: number | null;
  memory_percent: number | null;
  disk_percent: number | null;
  last_sync: string | null;
  bytes_synced: number;
}
