from kafka import KafkaProducer, KafkaConsumer
import json
from aiokafka import AIOKafkaConsumer

KAFKA_BROKER = "ml_kafka:9092"
TOPIC = "anomaly_detection"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_message(data):
    producer.send(TOPIC, data)

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

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
            await callback(msg.value)
    finally:
        await consumer.stop()
