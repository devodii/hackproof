import math
import time
from collections import defaultdict, deque
from collections.abc import Callable

from pydantic import BaseModel


class Window(BaseModel, frozen=True):
    name: str
    limit: int
    seconds: int


class Denied(BaseModel):
    window: str
    limit: int
    retry_after: int


MINUTE = Window(name="minute", limit=10, seconds=60)
HOUR = Window(name="hour", limit=50, seconds=3600)


class RateLimiter:
    def __init__(
        self,
        windows: tuple[Window, ...] = (MINUTE, HOUR),
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.windows = windows
        self.clock = clock
        self.hits: defaultdict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> Denied | None:
        now = self.clock()
        hits = self.hits[key]
        longest = max(window.seconds for window in self.windows)
        while hits and now - hits[0] >= longest:
            hits.popleft()

        denials = []
        for window in self.windows:
            recent = [hit for hit in hits if now - hit < window.seconds]
            if len(recent) >= window.limit:
                retry_after = math.ceil(recent[0] + window.seconds - now)
                denials.append(
                    Denied(window=window.name, limit=window.limit, retry_after=retry_after)
                )
        if denials:
            return max(denials, key=lambda denied: denied.retry_after)

        hits.append(now)
        return None
