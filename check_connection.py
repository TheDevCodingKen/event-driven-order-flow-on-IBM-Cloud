from confluent_kafka import Consumer

from kafka_settings import bootstrap, get_base_config

# Configure consumer for connection test
config = get_base_config()
config.update({
    "group.id": "test-connection-group",
    "auto.offset.reset": "earliest",
    "session.timeout.ms": "10000",
})

# Try to connect and fetch cluster metadata
consumer = Consumer(config)
cluster_metadata = consumer.list_topics(timeout=10)

print("Connected successfully!")
print("Brokers:", bootstrap.split(","))
print(f"Available topics: {list(cluster_metadata.topics.keys())}")

consumer.close()
