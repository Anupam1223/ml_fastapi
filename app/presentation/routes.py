from datetime import datetime
from typing import List

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from app.application.commands import SaveTimeSeriesData
from app.infrastructure.unit_of_work import UnitOfWork
from app.presentation.websockets import get_active_websocket_connections
from app.domain.services import AnomalyDetector
from app.domain.entities import TimeSeriesData
import joblib
import os
import pandas as pd
import io
from app.infrastructure import kafka
from app.infrastructure.model_version_manager import get_next_model_version


router = APIRouter()

class TimeSeriesInput(BaseModel):
    timestamp: datetime
    value: float

class BulkTimeSeriesInput(BaseModel):
    data: List[TimeSeriesInput]

detector = AnomalyDetector()  # Initialize anomaly detector
# Ensure "models" directory exists
MODEL_DIR = "models"
MODEL_FILE_PATH = os.path.join(MODEL_DIR, "anomaly_model.pkl")
os.makedirs(MODEL_DIR, exist_ok=True)

@router.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):

    # Read CSV file into Pandas DataFrame
    df = pd.read_csv(io.BytesIO(await file.read()))
    # Ensure correct column names
    if not {"timestamp", "value"}.issubset(df.columns):
        return {"error": "CSV must contain 'timestamp' and 'value' columns"}
    
    # Convert timestamp column to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Convert DataFrame to list of TimeSeriesData
    time_series_data = [
        TimeSeriesData(timestamp=row["timestamp"], value=row["value"])
        for _, row in df.iterrows()
    ]

    """Uploads time series data, detects anomalies, and notifies WebSockets."""
    # Store data in database
    use_case = SaveTimeSeriesData(UnitOfWork())
    for data in time_series_data:
        use_case.execute(data.timestamp, data.value)
    
    # Train anomaly detector
    detector.train(time_series_data)

    # Version the model
    version = get_next_model_version()
    model_path = os.path.join(MODEL_DIR, f"anomaly_model_v{version}.pkl")
    joblib.dump(detector.model, model_path)

    return {
        "message": f"Data uploaded and model v{version} trained with {len(df)} data points.",
        "model_version": version
    }

@router.get("/ws/active_connections")
async def get_active_connections():
    """Returns the number of currently connected WebSocket clients."""
    return {"active_connections": get_active_websocket_connections()}

@router.post("/stream-data/")
async def stream_data(payload: TimeSeriesInput):
    """Sends real-time data to Kafka for anomaly detection."""
    data = {"timestamp": str(payload.timestamp), "value": payload.value}
    kafka.producer.send(kafka.TOPIC, data)
    