import asyncio
import websockets
import pytest

@pytest.mark.asyncio
async def test_websocket():
    """Test if the WebSocket connection receives anomaly updates."""
    uri = "ws://localhost:8000/ws/anomalies"
    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        assert "is_anomaly" in message, "WebSocket did not receive anomaly update"
