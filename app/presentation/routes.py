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

    joblib.dump(detector.model, MODEL_FILE_PATH) 

    return {"message": f"Data uploaded, saved in DB, and model trained with {len(df)} data points."}

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