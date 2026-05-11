import asyncio
import time
from aoptk.literature.id import ID


class AsyncRequestLimiter:
    """Asynchronous request limiter to control the rate of API calls."""

    def __init__(self, requests_per_second: int):
        self.min_interval = 1.0 / requests_per_second
        self._lock = asyncio.Lock()
        self._next_allowed = 0.0

    async def wait_turn(self) -> None:
        """Wait until it's the turn for the next request based on the rate limit."""
        async with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                await asyncio.sleep(self._next_allowed - now)
                now = time.monotonic()
            self._next_allowed = now + self.min_interval


def is_europepmc_id(publication_id: ID) -> bool:
    """Check if the given publication ID is a EuropePMC ID."""
    return bool(str(publication_id).startswith("PMC"))
