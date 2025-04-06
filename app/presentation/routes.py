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
from app.infrastructure.redis import cache_anomaly
from app.infrastructure.redis import redis_client
import json
from app.infrastructure import kafka

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
    # Check if model exists in Redis
    model_in_redis = redis_client.get("anomaly_model")

    if not model_in_redis:
        # Try loading from disk
        if os.path.exists(MODEL_FILE_PATH):
            loaded_model = joblib.load(MODEL_FILE_PATH)
            detector.model = loaded_model
            redis_client.set("anomaly_model", json.dumps(True))  # Mark model as loaded in Redis
            print("Model loaded from disk and stored in Redis.")
        else:
            return {"error": "No trained model found. Please upload data first using `/upload-data`."}

    # Create the TimeSeriesData object from the payload
    data = TimeSeriesData(timestamp=payload.timestamp, value=payload.value)
    
    # Use the detector to predict if it's an anomaly
    anomaly = detector.predict(data)

    # If an anomaly is detected, store in Redis and notify WebSockets
    if anomaly.is_anomaly:
        anomaly_data = {
            "timestamp": str(anomaly.timestamp),
            "value": anomaly.value,
            "is_anomaly": anomaly.is_anomaly
        }
        
        # Cache anomaly in Redis and notify WebSockets
        await cache_anomaly(anomaly_data)

    return {
        "timestamp": anomaly.timestamp,
        "value": anomaly.value,
        "is_anomaly": anomaly.is_anomaly
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
    return {"message": "Data sent to Kafka", "data": data}