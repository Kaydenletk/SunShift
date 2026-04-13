#!/usr/bin/env python3
"""SunShift On-Prem Agent — main entry point."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import AgentConfig
from agent.db import LocalDB
from agent.collector import MetricsCollector
from agent.command_receiver import CommandReceiver


async def metrics_loop(collector: MetricsCollector, db: LocalDB, interval: int) -> None:
    while True:
        metrics = collector.collect()
        db.store_metric(metrics)
        await asyncio.sleep(interval)


async def main() -> None:
    config_path = Path("sunshift-agent.yaml")
    config = AgentConfig.from_yaml(config_path) if config_path.exists() else AgentConfig()

    db = LocalDB(Path("agent_data.db"))
    db.init()

    collector = MetricsCollector()
    receiver = CommandReceiver(
        ws_url=config.api_endpoint.replace("http", "ws"),
        agent_id=config.agent_id,
    )

    print(f"[SunShift Agent] Starting agent '{config.agent_id}'")
    print(f"[SunShift Agent] API: {config.api_endpoint}")
    print(f"[SunShift Agent] Watch paths: {config.watch_paths}")

    await asyncio.gather(
        metrics_loop(collector, db, config.metrics_interval_sec),
        receiver.connect(),
    )


if __name__ == "__main__":
    asyncio.run(main())
