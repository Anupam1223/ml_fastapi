import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from app.domain.entities import TimeSeriesData, Anomaly
from app.infrastructure.redis import redis_client 

class AnomalyDetector:
    def __init__(self):
        self.model = self.load_model()

    def train(self, data: list[TimeSeriesData]):
        """Train and cache model."""
        values = np.array([d.value for d in data]).reshape(-1, 1)
        model = IsolationForest(contamination=0.05)
        model.fit(values)

        # Store model in Redis
        redis_client.set("anomaly_model", joblib.dumps(model))

        # Update the instance model
        self.model = model

    def load_model(self):
        """Load cached model from Redis or retrain if missing."""
        model_data = redis_client.get("anomaly_model")
        if model_data:
            return joblib.loads(model_data)  # Load from Redis
        else:
            # Train a fresh model if none exists
            return IsolationForest(contamination=0.05)

    def predict(self, data: TimeSeriesData) -> Anomaly:
        """Predict anomaly using pre-trained model."""
        is_anomaly = self.model.predict([[data.value]])[0] == -1
        return Anomaly(timestamp=data.timestamp, value=data.value, is_anomaly=is_anomaly)
