from fastapi import FastAPI

from app.presentation.routes import router as api_router
from app.presentation.websockets import router as ws_router
from app.infrastructure.kafka import init_kafka_producer

app = FastAPI()
app.include_router(api_router)
app.include_router(ws_router, prefix="")

@app.on_event("startup")
def startup_event():
    """Initialize Kafka producer on startup"""
    init_kafka_producer()