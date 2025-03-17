from fastapi import APIRouter, WebSocket
import asyncio
import json

router = APIRouter()

# Store connected clients
active_connections = set()

@router.websocket("/ws/anomalies")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint to stream anomalies in real-time."""
    await websocket.accept()
    active_connections.add(websocket)

    try:
        while True:
            await asyncio.sleep(1)  # Simulate real-time anomaly updates
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        active_connections.remove(websocket)

async def send_anomaly_update(data):
    """Send new anomaly to all connected clients asynchronously."""
    disconnected_clients = set()

    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(data))
        except Exception as e:
            print(f"WebSocket Send Error: {e}")
            disconnected_clients.add(connection)
            
    active_connections.difference_update(disconnected_clients)