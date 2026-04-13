from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AgentConfig:
    agent_id: str = "dev-agent-001"
    api_endpoint: str = "http://localhost:8000"
    watch_paths: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=lambda: ["*.tmp", "*.log"])
    max_bandwidth_mbps: int = 50
    encrypt: bool = True
    metrics_interval_sec: int = 60
    heartbeat_interval_sec: int = 30
    retry_max: int = 5

    @classmethod
    def from_yaml(cls, path: Path) -> AgentConfig:
        with open(path) as f:
            raw = yaml.safe_load(f)
        agent = raw.get("agent", {})
        sync = raw.get("sync", {})
        schedule = raw.get("schedule", {})
        defaults = cls()
        return cls(
            agent_id=agent.get("id", defaults.agent_id),
            api_endpoint=agent.get("api_endpoint", defaults.api_endpoint),
            watch_paths=sync.get("watch_paths", []),
            exclude_patterns=sync.get("exclude", defaults.exclude_patterns),
            max_bandwidth_mbps=sync.get("max_bandwidth_mbps", defaults.max_bandwidth_mbps),
            encrypt=sync.get("encrypt", defaults.encrypt),
            metrics_interval_sec=schedule.get("metrics_interval_sec", defaults.metrics_interval_sec),
            heartbeat_interval_sec=schedule.get("heartbeat_interval_sec", defaults.heartbeat_interval_sec),
        )
