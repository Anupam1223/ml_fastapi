import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from app.domain.entities import TimeSeriesData, Anomaly
from app.infrastructure.redis import redis_client 
import io

class AnomalyDetector:
    def __init__(self):
        self.model = self.load_model()

    def train(self, data: list[TimeSeriesData]):
        """Train and cache model."""
        values = np.array([d.value for d in data]).reshape(-1, 1)
        model = IsolationForest(contamination=0.1)
        model.fit(values)

        # Serialize the model to bytes using a file-like object
        model_bytes = io.BytesIO()
        joblib.dump(model, model_bytes)  # Save the model to the file-like object
        model_bytes.seek(0)  # Move the pointer to the start

        # Store model in Redis
        redis_client.set("anomaly_model", model_bytes.read())

        # Update the instance model
        self.model = model

    def load_model(self):
        """Load cached model from Redis or retrain if missing."""
        model_data = redis_client.get("anomaly_model")
        if model_data:
            print("here at model loading")
            model_bytes = io.BytesIO(model_data)  # Convert bytes to file-like object
            return joblib.load(model_bytes)  # Load model from Redis
        else:
            return IsolationForest(contamination=0.05)  # Fresh model if none exists

    def predict(self, data: TimeSeriesData) -> Anomaly:
        """Predict anomaly using pre-trained model."""
        is_anomaly = bool(self.model.predict([[data.value]])[0] == -1)
        return Anomaly(timestamp=data.timestamp, value=data.value, is_anomaly=is_anomaly)
