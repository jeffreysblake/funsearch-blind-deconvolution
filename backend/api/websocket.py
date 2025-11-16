"""WebSocket endpoints for real-time updates."""

import asyncio
import json
from datetime import datetime
from typing import Set
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for experiments."""

    def __init__(self):
        # Map experiment_id -> set of active connections
        self.active_connections: dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, experiment_id: str):
        """Connect a WebSocket to an experiment."""
        await websocket.accept()

        if experiment_id not in self.active_connections:
            self.active_connections[experiment_id] = set()

        self.active_connections[experiment_id].add(websocket)
        print(f"✓ WebSocket connected to experiment {experiment_id}")

    def disconnect(self, websocket: WebSocket, experiment_id: str):
        """Disconnect a WebSocket from an experiment."""
        if experiment_id in self.active_connections:
            self.active_connections[experiment_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[experiment_id]:
                del self.active_connections[experiment_id]

        print(f"✓ WebSocket disconnected from experiment {experiment_id}")

    async def broadcast(self, experiment_id: str, message: dict):
        """Broadcast message to all connections for an experiment."""
        if experiment_id not in self.active_connections:
            return

        # Remove disconnected clients
        disconnected = set()

        for connection in self.active_connections[experiment_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected
        for connection in disconnected:
            self.disconnect(connection, experiment_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/experiments/{experiment_id}")
async def experiment_websocket(websocket: WebSocket, experiment_id: str):
    """
    WebSocket endpoint for real-time experiment updates.

    Clients can subscribe to:
    - metrics: Metrics updates
    - islands: Island state updates
    - best_program: Best program updates
    - logs: Log messages
    - status: Status changes
    """
    await manager.connect(websocket, experiment_id)

    try:
        # Send initial connection message
        await websocket.send_json(
            {
                "type": "connected",
                "timestamp": datetime.utcnow().isoformat(),
                "experiment_id": experiment_id,
                "message": "WebSocket connected successfully",
            }
        )

        # Keep connection alive and handle client messages
        while True:
            # Receive messages from client (subscriptions, pings, etc.)
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle ping
                if message.get("type") == "ping":
                    await websocket.send_json(
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                    )

                # Handle subscription (future: filter messages based on channels)
                elif message.get("type") == "subscribe":
                    channels = message.get("channels", [])
                    await websocket.send_json(
                        {
                            "type": "subscribed",
                            "timestamp": datetime.utcnow().isoformat(),
                            "channels": channels,
                        }
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": "invalid_json",
                        "message": "Invalid JSON message",
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, experiment_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, experiment_id)


# Helper functions for broadcasting updates

async def broadcast_metric_update(experiment_id: str, metric_data: dict):
    """Broadcast metric update to all clients watching an experiment."""
    await manager.broadcast(
        experiment_id,
        {
            "type": "metrics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": metric_data,
        },
    )


async def broadcast_status_change(
    experiment_id: str, old_status: str, new_status: str, reason: str = None
):
    """Broadcast status change to all clients."""
    await manager.broadcast(
        experiment_id,
        {
            "type": "status_change",
            "timestamp": datetime.utcnow().isoformat(),
            "old_status": old_status,
            "new_status": new_status,
            "reason": reason,
        },
    )


async def broadcast_best_program_update(experiment_id: str, program_data: dict):
    """Broadcast new best program to all clients."""
    await manager.broadcast(
        experiment_id,
        {
            "type": "best_program_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": program_data,
        },
    )


async def broadcast_log(experiment_id: str, level: str, message: str):
    """Broadcast log message to all clients."""
    await manager.broadcast(
        experiment_id,
        {
            "type": "log",
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
        },
    )
