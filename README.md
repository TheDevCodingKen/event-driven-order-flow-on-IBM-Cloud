# Event-Driven Order Flow on IBM Cloud

## Concept

An event-driven, cloud-native order processing pipeline demonstrating production-ready patterns on IBM Cloud's free tier:

- **Producer**: Python application publishes JSON order messages to IBM Event Streams (managed Kafka)
- **Consumer**: Python application consumes orders, computes metrics, scores risk, and persists to cloud storage
- **Storage**: IBM Cloud Object Storage (COS) with Hive-style partitioning for analytics

This Proof of Concept uses IBM Event Streams (Lite tier), which provides managed Apache Kafka with SASL_SSL authentication.

## Objectives

Demonstrate knowledge and understanding of key software engineering fundamentals:

- **Cloud Services**: IBM Event Streams (Kafka), IBM Cloud Object Storage
- **Security**: SASL_SSL authentication with PLAIN mechanism (username token, password from Event Streams service credential)
- **Observability**: End-to-end latency tracking, throughput monitoring
- **Python Proficiency**: Type hints, dataclasses, functional programming, design patterns
- **Software Design**: Clean architecture, testability, scalability

---

---

## Getting Started

### Prerequisites

- Python 3.9+
- IBM Cloud Pay-as-you-go account (free tier)
- IBM Event Streams (Lite) instance
- IBM Cloud Object Storage (Lite) instance

### Setup

1. **Clone the repository:**

   ```python
   git clone <your-repo-url>
   cd event-driven-order-flow

2. Install dependencies

    ```python
    pip install confluent-kafka ibm-cos-sdk python-dotenv pytest pytest-cov

3. Configure environment variables:

    ```python
    cp .env.example .env        # Edit .env with your IBM Cloud credentials

4. Get IBM Cloud credentials:

    Event Streams (Kafka):

    - Go to IBM Cloud Console → Event Streams → Service Credentials
    - Copy kafka_brokers_sasl, user, password

    Cloud Object Storage:

    - Go to IBM Cloud Console → Object Storage → Service Credentials
    - Copy apikey, resource_instance_id, endpoints (use public endpoint)
    - Create a bucket and note its name

5. Verify connection:

    ```python
    python check_connection.py

6. Run the pipeline

    ```python
    # Terminal 1: Start consumer
    python consumer.py

    # Terminal 2: Send orders
    python producer.py

---

## Phase 1 — Secure Event-Driven Foundation

### Goal

Design a minimal, secure, and durable order flow on IBM Cloud Free tier that demonstrates production-ready messaging patterns.

### Outcomes

**1. IBM Design Thinking Framework**

- Defined end-user outcomes as WHO-WHAT-WOW Hills
- Validated one Hill via Playback session (≤ 2 min submit→processed latency)

**2. Secure Kafka Configuration** ([`kafka_settings.py`](kafka_settings.py))

- SASL_SSL protocol with PLAIN authentication
- Environment-based credential management
- Connection validation utility ([`check_connection.py`](check_connection.py))

**3. Producer Implementation** ([`producer.py`](producer.py))

Configured for **at-least-once delivery guarantee** with no message loss:

- `acks=all` — Wait for all in-sync replicas
- `retries=3` — Automatic retry on transient failures
- `linger.ms=50` — Batch messages for throughput
- `compression.type=snappy` — Reduce network bandwidth
- Synchronous flush — Ensure all messages delivered before exit
- Delivery callbacks — Confirm per-message success/failure

**4. Consumer Implementation** ([`consumer.py`](consumer.py))

- Polls messages with 1-second timeout
- Synchronous processing with manual offset commits after successful COS writes (at-least-once guarantee)
- End-to-end latency calculation (producer timestamp → consumer timestamp)
- Graceful shutdown on interrupt

---

## Phase 2 — Observability, Analytics, and Clean Architecture

### Goal

Extend the pipeline with cloud storage integration, in-app metrics, risk scoring, and demonstrate software design best practices—all within IBM Cloud Lite tier limits.

### Outcomes

**1. Cloud Object Storage Integration** ([`cos_writer.py`](cos_writer.py))

- **Hive-style partitioning**: `orders/dt=YYYY-MM-DD/orderId=<id>.json`
- Enables efficient date-based queries in analytics tools (Spark, Presto, Athena)
- Batch write convenience function with error isolation
- Comprehensive error handling and logging

**2. Domain Modeling** ([`models.py`](models.py))

- **Abstract Data Type**: Immutable `Order` dataclass with type safety
- **Factory Pattern**: `Order.from_raw()` transforms raw JSON to validated domain object
- **Type Safety**: `RawOrder` TypedDict for JSON schema validation
- Encapsulated latency calculation logic

**3. Risk Scoring System** ([`risk.py`](risk.py), [`strategy.py`](strategy.py))

**Algorithm**: Top-K tracking using min-heap (O(log k) per update)

- Maintains highest-value orders in streaming fashion
- Space-efficient: O(k) memory regardless of stream size

**Design Pattern**: Strategy pattern for channel-specific risk scoring

- `WebRiskScorer`: Proportional to order total (0-0.99 scale)
- `PartnerRiskScorer`: Threshold-based ($2000 cutoff)
- `MobileRiskScorer`: Fixed baseline risk (0.5)
- Extensible via registry pattern — add new channels without modifying core code

**4. Functional Programming** ([`transforms.py`](transforms.py))

- Pure functions for data transformation pipelines
- Composable filter/map operations
- Lazy evaluation with Python iterators

**5. Observability Metrics** ([`metrics.py`](metrics.py), [`consumer.py`](consumer.py))

- **End-to-end latency**: Producer timestamp → Consumer timestamp (milliseconds)
- **Throughput monitoring**: Sliding 30-second window (events/second)
- **Risk scoring**: Per-order risk assessment logged in real-time
- All metrics computed in-app (no external APM required for Lite tier)

**6. Test Coverage** ([`tests/`](tests/))

- Unit tests for COS writer with mocked IBM SDK
- Unit tests for risk algorithms (TopK heap, predicates)
- Pytest fixtures for environment isolation

---
