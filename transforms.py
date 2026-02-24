from typing import Callable, Iterable

from models import Order, RawOrder


def map_orders(records: Iterable[RawOrder]) -> Iterable[Order]:
    """Transform raw records to Order objects using factory method."""
    return map(Order.from_raw, records)


def filter_orders(orders: Iterable[Order], predicate: Callable[[Order], bool]) -> Iterable[Order]:
    """Filter orders using custom predicate (composable)."""
    return filter(predicate, orders)


def compose_pipeline(*functions: Callable) -> Callable:
    """Compose multiple functions right-to-left"""
    def composed(arg):
        for func in reversed(functions):
            arg = func(arg)
            return arg
        return composed
