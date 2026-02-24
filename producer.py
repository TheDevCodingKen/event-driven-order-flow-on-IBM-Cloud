import json
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

from kafka_settings import get_base_config, topic

# Configure producer
config = get_base_config()
config.update(
    {
        # Batch messages for up to 50ms (good for throughput)
        "linger.ms": 50,
        "compression.type": "snappy",  # Compress messages
        "acks": "all",  # Wait for all replicas (durability)
        "retries": 3,  # Retry failed sends
    }
)

producer = Producer(config)


def delivery_report(err, msg):
    """Callback for message delivery confirmation."""
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(
            f"✅ Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}"
        )


# Sample orders
orders = [
    {"id": "o-1001", "customer": "C-9", "total": 149.99, "channel": "web"},
    {"id": "o-1002", "customer": "C-10", "total": 879.00, "channel": "partner"},
    {"id": "o-1003", "customer": "C-11", "total": 42.50, "channel": "mobile"},
]

# Produce messages
for order in orders:
    order["produced_at"] = datetime.now(
        timezone.utc
    ).isoformat()  # Add timestamp when producing
    value = json.dumps(order).encode("utf-8")
    key = order["id"].encode("utf-8")

    producer.produce(topic, key=key, value=value, callback=delivery_report)

    print(f"Produced -> {order}")
    time.sleep(0.2)

    # Poll to handle delivery callbacks
    producer.poll(0)

# Wait for all messages to be delivered
producer.flush()
print("\n✅ All messages sent successfully!")
