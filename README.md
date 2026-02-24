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

## Architecture

### Phase 1: Secure Event-Driven Foundation

![Phase 1 Architecture](./diagrams/Phase%201%20—%20Secure%20Event-Driven%20Foundation.png)

**Key Components:**

- Producer with at-least-once delivery guarantees (acks=all, retries=3)
- IBM Event Streams (Kafka) with SASL_SSL authentication
- Consumer with manual offset commits after successful COS writes
- IBM Cloud Object Storage with Hive-style partitioning

**Delivery Guarantee:** At-least-once from producer to storage. Offsets committed only after successful COS write, ensuring no message loss even on consumer failure.

---

### Phase 2: Observability, Analytics, and Clean Architecture

![Phase 2 Architecture](./diagrams/Phase%202%20—%20Observability,%20Analytics,%20and%20Clean%20Architecture.png)

**Design Patterns:**

- **Factory Pattern**: `Order.from_raw()` transforms raw JSON to validated domain objects
- **Strategy Pattern**: Pluggable risk scoring algorithms (Web, Partner, Mobile)
- **Registry Pattern**: Runtime extensibility for new channels without code modification
- **Immutable ADT**: Type-safe, frozen dataclasses prevent bugs

**Key Enhancements:**

- Domain modeling with type safety (RawOrder TypedDict → Order dataclass)
- Risk scoring with O(log k) TopK heap algorithm
- In-app observability (latency tracking, throughput monitoring)
- Functional data transformation pipelines

---

### Class Diagram: Domain Models and Risk Scoring

![Class Diagram](./diagrams/Class%20Diagram.png)

### End-to-End Data Flow

![End-to-End Flow](./diagrams/Phase%203%20—%20End-to-End%20Data%20Flow%20with%20Guarantees.png)

**Data Transformations:**

1. **Producer**: Python dict → JSON bytes (UTF-8, Snappy compressed)
2. **Kafka**: Durable storage with replication
3. **Consumer**: JSON bytes → RawOrder (TypedDict)
4. **Domain Layer**: RawOrder → Order (immutable dataclass)
5. **Enrichment**: Add consumed_at, latency_ms, risk_score
6. **Storage**: Enriched JSON → COS with Hive partitioning

**Failure Handling:** COS write failures prevent offset commits, triggering message reprocessing. Idempotent writes (same key) ensure safe retries.

---

## Scaling Plan

**Current (IBM Cloud Lite)**

- Single partition, single consumer
- Ideal for PoC and development
- No cost, sufficient for learning and validation

**Production Recommendations (IBM Subscription)**

- **Increase partitions**: Enable parallel processing (1 consumer per partition)
- **Consumer groups**: Add multiple consumers for horizontal scaling
- **Monitoring**: Integrate IBM Cloud Monitoring or Instana for production observability
- **Durability**: Upgrade to Standard/Enterprise for 3x replication (service-managed)
- **Retention**: Configure topic retention based on compliance requirements

## Project Structure

```python

├── producer.py             # Kafka producer with delivery guarantees
├── consumer.py             # Kafka consumer with metrics and COS sink
├── kafka_settings.py       # Shared Kafka configuration
├── cos_writer.py           # IBM COS integration with Hive partitioning
├── models.py               # Domain models (Order, RawOrder)
├── strategy.py             # Risk scoring strategies (Strategy pattern)
├── risk.py                 # Risk algorithms (TopK heap, predicates)
├── metrics.py              # Throughput monitoring (sliding window)
├── transforms.py           # Functional data transformations
├── check_connection.py     # Kafka connectivity validator
├── tests/
│   ├── test_cos_writer.py  # COS writer unit tests
│   └── test_risk.py        # Risk algorithm unit tests
├── diagrams/
    ├── Phase 1 — Secure Event-Driven Foundation 
    ├── Phase 2 — Observability, Analytics, and Clean Architecture  
│   └── Phase 3 — End-to-End Data Flow with Guarantees   
└── README.md
```

---

## Key Learnings

1. **At-least-once delivery** requires producer acknowledgments (`acks=all`) and manual consumer offset commits AFTER processing completes
2. **Hive-style partitioning** enables efficient analytics queries on object storage
3. **Strategy pattern** provides extensibility without modifying existing code
4. **Immutable domain models** prevent bugs and enable safe concurrent processing
5. **In-app metrics** are sufficient for PoC observability without external APM costs

---

---

## Project Evolution

This project was developed iteratively to demonstrate incremental software development practices:

### [Phase 1: Secure Event-Driven Foundation](../../tree/v1.0.0-phase1) (`v1.0.0-phase1`)

**Focus:** Minimal viable pipeline with delivery guarantees

**Implemented:**

- Producer with at-least-once delivery to Kafka (`acks=all`, `retries=3`)
- Consumer with basic Kafka integration
- SASL_SSL authentication with IBM Event Streams
- COS integration with Hive-style partitioning
- End-to-end latency tracking

**Key Files:** [`producer.py`](producer.py), [`consumer.py`](consumer.py), [`kafka_settings.py`](kafka_settings.py), [`cos_writer.py`](cos_writer.py)

---

### [Phase 2: Observability and Clean Architecture](../../tree/v2.0.0-phase2) (`v2.0.0-phase2`)

**Focus:** Design patterns, type safety, and enhanced observability

**Added:**

- Domain modeling with immutable dataclasses ([`models.py`](models.py))
- Risk scoring with Strategy + Registry patterns ([`strategy.py`](strategy.py), [`risk.py`](risk.py))
- TopK heap algorithm for high-value order tracking
- Throughput monitoring with sliding window ([`metrics.py`](metrics.py))
- Functional data transformation pipelines ([`transforms.py`](transforms.py))
- Unit test coverage ([`tests/`](tests/))
- Manual offset commits for true at-least-once guarantee

**Design Patterns:** Factory, Strategy, Registry, Immutable ADT

---

### Release (`v2.1.0`)

**Added:**

- Architecture diagrams for all phases
- Enhanced documentation with visual representations
- Verified at-least-once guarantee implementation

**Status:** Production-ready PoC on IBM Cloud Lite tier

### Current State (`v2.2.0`)

**Added:**

- Class diagram for domain models and design patterns
- Complete visual documentation suite (4 diagrams)
- Enhanced Architecture section with code structure visualization

**Status:** Production-ready PoC on IBM Cloud Lite tier with comprehensive documentation

---

### Exploring Phase History

**View specific phases:**

```bash
# Checkout Phase 1 to see initial implementation
git checkout v1.0.0-phase1

# Checkout Phase 2 to see design pattern additions
git checkout v2.0.0-phase2

# Return to latest version
git checkout main

---

## External Artifacts

- IBM Design Thinking Hills (WHO-WHAT-WOW format)
- Playback validation results (≤ 2 min processing time)
- Sequence diagrams (event flow visualization)
- Instana Sandbox observability walkthrough (if applicable)

*Note: These artifacts are maintained separately and available upon request.*
