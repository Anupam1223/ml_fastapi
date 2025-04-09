from kafka import KafkaProducer
import json
import joblib
from aiokafka import AIOKafkaConsumer
from app.domain.services import AnomalyDetector
from app.infrastructure.redis import redis_client
import os
from app.domain.entities import TimeSeriesData
from app.infrastructure.redis import cache_anomaly
import time
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = "ml_kafka:9092"
TOPIC = "anomaly_detection"
MODEL_FILE_PATH = "models/anomaly_model.pkl"

detector = AnomalyDetector()
producer = None

def init_kafka_producer(retries=10, delay=5):
    global producer
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Connecting to Kafka at {KAFKA_BROKER}...")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Kafka Producer connected.")
            break
        except NoBrokersAvailable as e:
            print(f"Kafka not available (attempt {attempt}). Retrying in {delay}s...")
            time.sleep(delay)
    else:
        raise RuntimeError("Kafka broker not available after retries.")
    
def get_kafka_producer():
    return producer

async def consume_messages(callback):
    """Consumes Kafka messages asynchronously and triggers callback."""
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    await consumer.start()

    try:
        async for msg in consumer:
            data = msg.value
            print(f"Received Data: {data}")

            # Load model if not already in memory
            if not redis_client.get("anomaly_model"):
                if os.path.exists(MODEL_FILE_PATH):
                    detector.model = joblib.load(MODEL_FILE_PATH)
                    redis_client.set("anomaly_model", json.dumps(True))
                    print("Model loaded.")

            # Predict anomaly
            time_series_data = TimeSeriesData(timestamp=data["timestamp"], value=data["value"])
            anomaly = detector.predict(time_series_data)

            if anomaly.is_anomaly:
                print(f"Anomaly Detected: {anomaly}")
                anomaly_data = {
                    "timestamp": str(anomaly.timestamp),
                    "value": anomaly.value,
                    "is_anomaly": anomaly.is_anomaly
                }

                # Cache anomaly in Redis and notify WebSockets
                await cache_anomaly(anomaly_data)
                if callback:
                    callback(anomaly_data)
    finally:
        await consumer.stop()
