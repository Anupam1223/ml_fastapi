from fastapi import FastAPI

from app.presentation.routes import router as api_router
from app.presentation.websockets import router as ws_router
from app.infrastructure.kafka import init_kafka_producer
import asyncio
from app.infrastructure.kafka import consume_messages
from prometheus_fastapi_instrumentator import Instrumentator
from app.presentation.websockets import active_connections
from prometheus_client import Gauge, Counter
from threading import Thread
import time
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Add CORS middleware to allow all methods for your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify the domain of your frontend if you want to restrict
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


app.include_router(api_router)
app.include_router(ws_router, prefix="")

# ----------------- Prometheus Metrics -----------------
ws_connection_gauge = Gauge("websocket_connections_total", "Current active WebSocket connections")
anomaly_counter = Counter("anomalies_detected_total", "Total number of anomalies detected")
last_anomaly_value = Gauge("last_anomaly_value", "Value of the last detected anomaly")
# ------------------------------------------------------

@app.on_event("startup")
def startup_event():
    """Initialize Kafka producer on startup"""
    init_kafka_producer()

# to open the consumer just once because i am running the app with --reload
# and the consumer will be opened multiple times
consumer_started = False

# Define the callback to update metrics
def anomaly_callback(data: dict):
    try:
        parsed = data if isinstance(data, dict) else json.loads(data)
        print("[CALLBACK DATA]", parsed)
        if parsed.get("is_anomaly"):
            print("[METRIC] Incrementing anomaly counter")
            anomaly_counter.inc()
            last_anomaly_value.set(parsed.get("value", 0.0))
    except Exception as e:
        print(f"Callback Error: {e}")

@app.on_event("startup")
async def start_kafka_consumer():
    global consumer_started
    if not consumer_started:
        loop = asyncio.get_event_loop()
        loop.create_task(consume_messages(callback=anomaly_callback))
        consumer_started = True
    
Instrumentator().instrument(app).expose(app)

def update_gauge():
    while True:
        ws_connection_gauge.set(len(active_connections))
        time.sleep(10)

@app.on_event("startup")
def start_metrics_updater():
    Thread(target=update_gauge, daemon=True).start()