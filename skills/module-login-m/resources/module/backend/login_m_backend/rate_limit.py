from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class LimitRule:
    max_requests: int
    window_seconds: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._store: dict[str, deque[datetime]] = defaultdict(deque)

    def hit(self, key: str, rule: LimitRule) -> bool:
        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=rule.window_seconds)
        bucket = self._store[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= rule.max_requests:
            return False
        bucket.append(now)
        return True
