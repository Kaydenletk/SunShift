"""WebSocket handler for agent communication."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.deps import get_agent_store

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/agent/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str) -> None:
    """
    WebSocket endpoint for persistent agent communication.

    - On connect: acknowledges the agent is connected and updates status.
    - On heartbeat message: replies with a heartbeat_ack.
    - On disconnect: marks agent as offline.
    """
    store = get_agent_store()
    await websocket.accept()

    # Update agent status to online if registered
    if agent_id in store:
        agent = store[agent_id]
        store[agent_id] = agent.model_copy(
            update={"status": "online", "last_seen": datetime.now(timezone.utc)}
        )

    # Send connection acknowledgement
    await websocket.send_json(
        {
            "type": "connected",
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON"})
                continue

            msg_type = message.get("type", "")

            if msg_type == "heartbeat":
                # Update last_seen if agent is registered
                if agent_id in store:
                    agent = store[agent_id]
                    store[agent_id] = agent.model_copy(
                        update={"last_seen": datetime.now(timezone.utc)}
                    )
                await websocket.send_json(
                    {
                        "type": "heartbeat_ack",
                        "agent_id": agent_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            else:
                await websocket.send_json(
                    {"type": "error", "detail": f"Unknown message type: {msg_type}"}
                )

    except WebSocketDisconnect:
        if agent_id in store:
            agent = store[agent_id]
            store[agent_id] = agent.model_copy(update={"status": "offline"})
