from fastapi import FastAPI

from app.presentation.routes import router as api_router
from app.presentation.websockets import router as ws_router
from app.infrastructure.kafka import init_kafka_producer
import asyncio
from app.infrastructure.kafka import consume_messages
from prometheus_fastapi_instrumentator import Instrumentator
from app.presentation.websockets import active_connections
from prometheus_client import Gauge
from threading import Thread
import time

app = FastAPI()
app.include_router(api_router)
app.include_router(ws_router, prefix="")

ws_connection_gauge = Gauge("websocket_connections_total", "Current active WebSocket connections")

@app.on_event("startup")
def startup_event():
    """Initialize Kafka producer on startup"""
    init_kafka_producer()

# to open the consumer just once because i am running the app with --reload
# and the consumer will be opened multiple times
consumer_started = False

@app.on_event("startup")
async def start_kafka_consumer():
    global consumer_started
    if not consumer_started:
        loop = asyncio.get_event_loop()
        loop.create_task(consume_messages(callback=None))
        consumer_started = True
    
Instrumentator().instrument(app).expose(app)

def update_gauge():
    while True:
        ws_connection_gauge.set(len(active_connections))  # ✅ uses the correct reference
        time.sleep(10)

@app.on_event("startup")
def start_metrics_updater():
    Thread(target=update_gauge, daemon=True).start()