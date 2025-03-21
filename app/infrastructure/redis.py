import redis
import json
from app.presentation.websockets import send_anomaly_update
import asyncio

REDIS_HOST = "ml_redis"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

async def cache_anomaly(data):
    """Cache anomaly in Redis and notify WebSockets."""
    redis_client.set(f"anomaly:{data['timestamp']}", json.dumps(data))
    """print what data is inside the redis client"""
    print(redis_client.get(f"anomaly:{data['timestamp']}"))
    # Notify WebSocket clients
    await asyncio.create_task(send_anomaly_update(data))

def get_anomaly(timestamp):
    """Fetch anomaly data from Redis."""
    data = redis_client.get(f"anomaly:{timestamp}")
    return json.loads(data) if data else None
