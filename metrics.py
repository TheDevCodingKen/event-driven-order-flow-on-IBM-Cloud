from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class ThroughputMeter:
    """
    Measures throughput using a sliding time window.

    GIVEN a stream of events
    WHEN tick() is called for each event
    THEN returns current events/second over the window
    """
    window: timedelta = timedelta(seconds=30)

    def __post_init__(self):
        self._events = deque()  # stores datetime stamps

    def tick(self, now: datetime | None = None) -> float:
        "Record an event at 'now' and return events/sec over the window."
        now = now or datetime.now(timezone.utc)
        self._events.append(now)
        cutoff = now - self.window
        while self._events and self._events[0] < cutoff:
            self._events.popleft()
        # rate = count / seconds
        return len(self._events) / self.window.total_seconds()

    def reset(self) -> None:
        """Clear all recorded events."""
        self._events.clear()
