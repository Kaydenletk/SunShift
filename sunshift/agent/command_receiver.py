from __future__ import annotations

import asyncio
import json
from typing import Callable


class CommandReceiver:
    def __init__(self, ws_url: str, agent_id: str):
        self.ws_url = ws_url
        self.agent_id = agent_id
        self._handlers: dict[str, Callable] = {}
        self._retry_count = 0
        self._running = False

    def register_handler(self, command: str, handler: Callable) -> None:
        self._handlers[command] = handler

    def _backoff_delay(self, retry: int) -> int:
        return min(2**retry, 60)

    def _dispatch(self, message: dict) -> None:
        command = message.get("command")
        handler = self._handlers.get(command)
        if handler:
            handler(message)

    async def connect(self) -> None:
        import websockets

        self._running = True
        while self._running:
            try:
                async with websockets.connect(
                    f"{self.ws_url}/ws/agent/{self.agent_id}"
                ) as ws:
                    self._retry_count = 0
                    heartbeat_task = asyncio.create_task(self._heartbeat_loop(ws))
                    try:
                        async for raw in ws:
                            message = json.loads(raw)
                            if message.get("type") != "ack":
                                self._dispatch(message)
                    finally:
                        heartbeat_task.cancel()
            except Exception:
                delay = self._backoff_delay(self._retry_count)
                self._retry_count += 1
                await asyncio.sleep(delay)

    async def _heartbeat_loop(self, ws) -> None:
        while True:
            await ws.send(
                json.dumps({"type": "heartbeat", "agent_id": self.agent_id})
            )
            await asyncio.sleep(30)

    def stop(self) -> None:
        self._running = False
