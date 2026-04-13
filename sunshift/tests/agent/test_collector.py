import pytest
from pathlib import Path

from agent.config import AgentConfig
from agent.db import LocalDB
from agent.collector import MetricsCollector


class TestAgentConfig:
    def test_load_defaults(self):
        config = AgentConfig()
        assert config.agent_id == "dev-agent-001"
        assert config.metrics_interval_sec == 60

    def test_load_from_yaml(self, tmp_path):
        yaml_content = """
agent:
  id: "test-clinic-001"
  api_endpoint: "http://localhost:8000"
sync:
  watch_paths: ["/tmp/data"]
  encrypt: false
schedule:
  metrics_interval_sec: 30
"""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(yaml_content)
        config = AgentConfig.from_yaml(config_path)
        assert config.agent_id == "test-clinic-001"
        assert config.metrics_interval_sec == 30


class TestLocalDB:
    def test_create_tables(self, tmp_path):
        db = LocalDB(tmp_path / "test.db")
        db.init()
        # Should not raise
        db.store_metric({"cpu_percent": 50, "memory_percent": 60, "disk_percent": 70})

    def test_get_recent_metrics(self, tmp_path):
        db = LocalDB(tmp_path / "test.db")
        db.init()
        for i in range(5):
            db.store_metric({"cpu_percent": 10 * i, "memory_percent": 50, "disk_percent": 50})
        recent = db.get_recent_metrics(limit=3)
        assert len(recent) == 3


class TestMetricsCollector:
    def test_collect_returns_valid_metrics(self):
        collector = MetricsCollector()
        metrics = collector.collect()
        assert 0 <= metrics["cpu_percent"] <= 100
        assert 0 <= metrics["memory_percent"] <= 100
        assert 0 <= metrics["disk_percent"] <= 100
        assert metrics["network_bytes_sent"] >= 0
