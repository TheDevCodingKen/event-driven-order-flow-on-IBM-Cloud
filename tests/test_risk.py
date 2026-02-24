from datetime import datetime, timezone

import pytest

from models import Order
from risk import TopK, is_high_risk, render_topk


def mk(total: float, id: str = "id"):
    """Helper to create Order with minimal required fields."""
    return Order(
        id=id,
        customer="C",
        total=total,
        channel="web",
        produced_at=datetime.now(timezone.utc),
    )


def test_is_high_risk():
    """Test high-risk predicate with >= threshold logic."""
    # Implementation: o.total >= threshold
    assert is_high_risk(mk(600.0)) is True
    assert (
        is_high_risk(mk(500.0)) is True
    )  # Boundary: exactly at threshold returns True
    assert is_high_risk(mk(499.99)) is False

    # Custom threshold
    assert is_high_risk(mk(100.0), threshold=100.0) is True  # Exactly at threshold
    assert is_high_risk(mk(99.99), threshold=100.0) is False


def test_topk_maintains_highest():
    """Test TopK maintains correct top-K items through stream of updates."""
    tk = TopK(k=3)
    heap = []

    for idx, total in enumerate([10, 500, 250, 1000, 5, 700], start=1):
        heap = tk.update(heap, mk(total, f"o{idx}"))

    top_scores = [score for score, _ in render_topk(heap)]
    assert top_scores == [1000, 700, 500]

    # Verify correct IDs
    top_items = render_topk(heap)
    assert top_items[0] == (1000, "o4")
    assert top_items[1] == (700, "o6")
    assert top_items[2] == (500, "o2")


def test_topk_with_fewer_than_k():
    """Test TopK when stream has fewer items than k."""
    tk = TopK(k=5)
    heap = []

    for idx, total in enumerate([100, 200, 50], start=1):
        heap = tk.update(heap, mk(total, f"o{idx}"))

    assert len(heap) == 3
    top_scores = [score for score, _ in render_topk(heap)]
    assert top_scores == [200, 100, 50]


def test_topk_immutability():
    """Test that update returns new list (immutable pattern)."""
    tk = TopK(k=2)
    heap1 = []
    heap2 = tk.update(heap1, mk(100, "o1"))
    heap3 = tk.update(heap2, mk(200, "o2"))

    assert heap1 == []
    assert len(heap2) == 1
    assert len(heap3) == 2


def test_render_topk_empty():
    """Test render_topk handles empty heap."""
    assert render_topk([]) == []
