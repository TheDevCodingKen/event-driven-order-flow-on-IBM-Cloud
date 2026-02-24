from dataclasses import dataclass
from heapq import heappush, heappushpop, nlargest
from typing import List

from models import Order


def is_high_risk(o: Order, threshold: float = 500.0) -> bool:
    """
    Pure predicate for identifying high-risk orders.

    GIVEN an Order and threshold
    WHEN total meets or exceeds threshold
    THEN returns True, indicating high risk
    """
    return o.total >= threshold


@dataclass
class TopK:
    """
    Maintains top-K items using a min-heap.

    GIVEN a stream of orders
    WHEN update() is called for an order
    THEN maintains the K highest-value orders in O(log k) time

    Space: O(k), Time per update: O(log k)
    """

    k: int

    def __post_init__(self):
        """Validate k parameter."""
        if self.k < 1:
            raise ValueError("k must be positive")

    def update(
        self, current: List[tuple[float, str]], o: Order
    ) -> List[tuple[float, str]]:
        """
        Update heap with new order, maintaining top-K items.

        GIVEN current heap state and new order
        WHEN order is processed
        THEN returns updated heap with top-K highest totals

        Returns new list (immutable update pattern).
        """
        heap = list(current)
        item = (o.total, o.id)
        if len(heap) < self.k:
            heappush(heap, item)  # O(log k)
        else:
            heappushpop(heap, item)  # O(log k)

        return heap


def render_topk(heap: List[tuple[float, str]]) -> List[tuple[float, str]]:
    """
    Format heap for display, sorted descending by score.

    GIVEN a min-heap of (score, id) tuples
    WHEN render_topk is called
    THEN returns list sorted highest-to-lowest

    Time: O(k log k)
    """
    return nlargest(len(heap), heap)
