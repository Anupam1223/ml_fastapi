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
from app.domain.services import AnomalyDetector
from app.domain.entities import TimeSeriesData
import joblib

router = APIRouter()

class TimeSeriesInput(BaseModel):
    timestamp: datetime
    value: float

class BulkTimeSeriesInput(BaseModel):
    data: List[TimeSeriesInput]

# Basic anomaly detection: If value > threshold, it's an anomaly
ANOMALY_THRESHOLD = 100.0
detector = AnomalyDetector()  # Initialize anomaly detector

@router.post("/upload-data")
async def upload_data(payload: BulkTimeSeriesInput):
    """Uploads time series data, detects anomalies, and notifies WebSockets."""
    use_case = SaveTimeSeriesData(UnitOfWork())
    for item in payload.data:
        use_case.execute(item.timestamp, item.value)
    
    # Step 2: Train the anomaly detection model
    detector.train(payload.data)  # Train the model with new data

    # Step 3: Persist the trained model to a file
    model_file_path = "models/anomaly_model.pkl"
    joblib.dump(detector.model, model_file_path)

    return {"message": "Data uploaded successfully"}

@router.post("/predict-anomaly")
async def predict_anomaly(payload: TimeSeriesInput):
    """Predicts if a time series data point is an anomaly using the loaded model."""

    # Create the TimeSeriesData object from the payload
    data = TimeSeriesData(timestamp=payload.timestamp, value=payload.value)
    
    # Use the detector to predict if it's an anomaly
    anomaly = detector.predict(data)

    # Return the anomaly result
    return {
        "timestamp": anomaly.timestamp,
        "value": anomaly.value,
        "is_anomaly": anomaly.is_anomaly
    }

@router.get("/ws/active_connections")
async def get_active_connections():
    """Returns the number of currently connected WebSocket clients."""
    return {"active_connections": get_active_websocket_connections()}