from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypedDict


class RawOrder(TypedDict):
    """
    Raw order data structure from Kafka message.

    GIVEN a Kafka message payload
    WHEN deserialized from JSON
    THEN represents the raw order data before validation
    """

    id: str
    customer: str
    total: float
    channel: str
    produced_at: Optional[str]  # ISO 8601 timestamp;


@dataclass(frozen=True)
class Order:
    """
    Validated, immutable order domain model.

    GIVEN raw order data
    WHEN validated and transformed
    THEN represents a business-ready order with parsed timestamp
    """

    id: str
    customer: str
    total: float
    channel: str
    produced_at: Optional[datetime]  # Parsed for latency calculations

    @classmethod
    def from_raw(cls, raw: RawOrder) -> 'Order':
        """
        Factory method to create an Order from RawOrder.

        GIVEN a RawOrder with string timestamp
        WHEN from_raw is called
        THEN returns ORder with parsed datetime
        """
        produced_at = None
        if raw.get('produced_at'):
            produced_at = datetime.fromisoformat(
                raw['produced_at'].replace('Z', '+00:00')
            )

        return cls(
            id=raw['id'],
            customer=raw['customer'],
            total=raw['total'],
            channel=raw['channel'],
            produced_at=produced_at
        )

    def calculate_latency(self, consumed_at: datetime) -> Optional[float]:
        """
        Calculate message latency in seconds.

        GIVEN an Order with produced_at timestamp
        WHEN consumed_at is provided
        THEN returns latency in seconds, or None if produced_at is missing
        """

        if self.produced_at is None:
            return None
        return (consumed_at - self.produced_at).total_seconds()
