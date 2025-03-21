from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
import asyncio

from app.application.commands import SaveTimeSeriesData
from app.application.queries import GetTimeSeriesData
from app.infrastructure.unit_of_work import UnitOfWork
from app.infrastructure.redis import cache_anomaly
from app.presentation.websockets import get_active_websocket_connections

router = APIRouter()

class TimeSeriesInput(BaseModel):
    timestamp: datetime
    value: float

class BulkTimeSeriesInput(BaseModel):
    data: List[TimeSeriesInput]

# Basic anomaly detection: If value > threshold, it's an anomaly
ANOMALY_THRESHOLD = 100.0

@router.post("/upload-data")
async def upload_data(payload: BulkTimeSeriesInput):
    """Uploads time series data, detects anomalies, and notifies WebSockets."""
    use_case = SaveTimeSeriesData(UnitOfWork())
    for item in payload.data:
        use_case.execute(item.timestamp, item.value)
        if item.value > ANOMALY_THRESHOLD:
            anomaly_data = {
                "timestamp": item.timestamp.isoformat(),
                "value": item.value,
                "is_anomaly": True
            }
            await cache_anomaly(anomaly_data)

    return {"message": "Data uploaded successfully"}

@router.get("/ws/active_connections")
async def get_active_connections():
    """Returns the number of currently connected WebSocket clients."""
    return {"active_connections": get_active_websocket_connections()}