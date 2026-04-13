import type { PredictionResponse, AgentStatus } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchPredictions(
  location = "tampa_fl"
): Promise<PredictionResponse> {
  const res = await fetch(
    `${API_BASE}/api/v1/predictions/energy?location=${location}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to fetch predictions");
  return res.json() as Promise<PredictionResponse>;
}

export async function fetchAgentStatus(agentId: string): Promise<AgentStatus> {
  const res = await fetch(`${API_BASE}/api/v1/agents/status/${agentId}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch agent status");
  return res.json() as Promise<AgentStatus>;
}
