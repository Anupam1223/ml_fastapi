import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/upload-data"

def test_send_data():
    """Test if the API correctly processes time-series data and detects anomalies."""
    data = {
        "data": [
            {"timestamp": (datetime.utcnow() - timedelta(seconds=10)).isoformat(), "value": 95.0},  # Normal
            {"timestamp": (datetime.utcnow()).isoformat(), "value": 120.0}  # Anomaly
        ]
    }

    response = requests.post(API_URL, json=data)
    assert response.status_code == 200, "API request failed"
    assert response.json()["message"] == "Data uploaded successfully", "Unexpected response message"
