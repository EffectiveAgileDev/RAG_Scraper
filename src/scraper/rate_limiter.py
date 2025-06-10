"""Rate limiting for ethical web scraping."""
import time
from typing import Optional


class RateLimiter:
    """Rate limiter to enforce delays between requests with validation."""

    def __init__(self, delay: float = 2.0, max_delay: float = 60.0):
        """Initialize rate limiter with specified delay in seconds.

        Args:
            delay: Minimum delay between requests in seconds
            max_delay: Maximum allowed delay (safety limit)
        """
        self._validate_configuration(delay, max_delay)
        self.delay = delay
        self.max_delay = max_delay
        self.last_request_time: Optional[float] = None

    def _validate_configuration(self, delay: float, max_delay: float) -> None:
        """Validate rate limiter configuration."""
        if delay < 0:
            raise ValueError("Delay must be non-negative")
        if max_delay <= 0:
            raise ValueError("Max delay must be positive")
        if delay > max_delay:
            raise ValueError("Delay cannot exceed max delay")

    def wait_if_needed(self) -> float:
        """Wait if necessary to enforce rate limiting.

        Returns:
            float: Time actually waited in seconds
        """
        current_time = time.time()

        if self.last_request_time is None:
            self.last_request_time = current_time
            return 0.0

        time_since_last = current_time - self.last_request_time

        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            # Apply safety limit
            sleep_time = min(sleep_time, self.max_delay)
            time.sleep(sleep_time)
            waited = sleep_time
        else:
            waited = 0.0

        self.last_request_time = time.time()
        return waited

    def reset(self) -> None:
        """Reset the rate limiter state."""
        self.last_request_time = None

    def time_until_next_allowed(self) -> float:
        """Calculate time until next request is allowed.

        Returns:
            float: Seconds until next request (0 if allowed now)
        """
        if self.last_request_time is None:
            return 0.0

        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last >= self.delay:
            return 0.0

        return self.delay - time_since_last
