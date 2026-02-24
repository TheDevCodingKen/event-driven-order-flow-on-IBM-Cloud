import json
from datetime import datetime, timedelta, timezone

from confluent_kafka import Consumer, KafkaError

from cos_writer import write_order_json
from kafka_settings import get_base_config, topic
from metrics import ThroughputMeter
from models import Order
from strategy import choose_scorer

# Configure consumer
config = get_base_config()
config.update(
    {
        "group.id": "order-consumer-group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
)

consumer = Consumer(config)
tp = ThroughputMeter(window=timedelta(seconds=30))
consumer.subscribe([topic])

print(f"📥 Subscribed to topic: {topic}")
print("Waiting for messages... (Press Ctrl+C to stop)\n")

try:
    while True:
        # Poll for messages (timeout in seconds)
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            # No message received within timeout
            continue

        if msg.error():
            # Handle errors
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition - not an error
                print(f"Reached end of partition {msg.partition()}")
            else:
                print(f"❌ Error: {msg.error()}")
            continue

        # Deserialize message
        try:
            key = msg.key().decode("utf-8") if msg.key() else None
            value = json.loads(msg.value().decode("utf-8"))
            now = datetime.now(timezone.utc)  # consumed at
            order = Order.from_raw(value)  # RawOrder -> Order dataclass
            latency_ms = None
            latency_sec = order.calculate_latency(now)
            if latency_sec is not None:
                latency_ms = latency_sec * 1000.0

            rate = tp.tick(now)  # events/sec over last 30s

            print(f"📨 Consumed → Key: {key} | {order}")

            if latency_ms is not None:
                print(
                    f"⏲️ E2E latency: {latency_ms:.1f} ms | 30s throughput: {rate:.3f} msg/s"
                )
            else:
                print(
                    f"⏲️ E2E latency: n/a (missing produced_at) | 30s throughput: {rate:.3f} msg/s"
                )

            try:
                scorer = choose_scorer(order.channel)
                risk = scorer.score(order)
                print(f"🎯 Risk score (strategy): {risk:.2f}")
            except ValueError as e:
                print(f"⚠️ Risk scoring failed: {e}")

            # Inside message processing loop, after risk scoring:
            try:
                # Convert Order dataclass back to dict for COS
                order_dict = {
                    "id": order.id,
                    "customer": order.customer,
                    "total": order.total,
                    "channel": order.channel,
                    "produced_at": (
                        order.produced_at.isoformat() if order.produced_at else None
                    ),
                    "consumed_at": now.isoformat(),
                    "latency_ms": latency_ms,
                    "risk_score": risk if "risk" in locals() else None,
                }

                cos_key = write_order_json(order_dict)
                print(f"   💾 Persisted to COS: {cos_key}")

                # Commit offset ONLY after successful processing
                consumer.commit(asynchronous=False)  # Synchronous commit for durability
            except Exception as e:
                print(f"   ⚠️ COS write failed: {e}")

            print(f"   Partition: {msg.partition()}, Offset: {msg.offset()}\n")

        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to decode JSON: {e}")
        except Exception as e:
            print(f"⚠️ Error processing message: {e}")

except KeyboardInterrupt:
    print("\n🛑 Shutting down consumer...")

finally:
    # Clean shutdown
    consumer.close()
    print("✅ Consumer closed")
