import pytest
from unittest.mock import AsyncMock, MagicMock

from agent.command_receiver import CommandReceiver


class TestCommandReceiver:
    def test_backoff_increases_exponentially(self):
        receiver = CommandReceiver(ws_url="ws://test", agent_id="test-001")
        assert receiver._backoff_delay(0) == 1
        assert receiver._backoff_delay(1) == 2
        assert receiver._backoff_delay(2) == 4
        assert receiver._backoff_delay(10) == 60  # capped at 60

    def test_dispatches_sync_command(self):
        handler = MagicMock()
        receiver = CommandReceiver(ws_url="ws://test", agent_id="test-001")
        receiver.register_handler("START_SYNC", handler)
        receiver._dispatch({"command": "START_SYNC", "paths": ["/data"]})
        handler.assert_called_once_with({"command": "START_SYNC", "paths": ["/data"]})

    def test_ignores_unknown_command(self):
        receiver = CommandReceiver(ws_url="ws://test", agent_id="test-001")
        # Should not raise
        receiver._dispatch({"command": "UNKNOWN"})
