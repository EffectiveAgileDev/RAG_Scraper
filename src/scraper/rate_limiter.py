"""Rate limiting for ethical web scraping."""
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from email.utils import parsedate_to_datetime
import datetime


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


class EnhancedRateLimiter:
    """Enhanced rate limiter with per-domain support and advanced features."""

    def __init__(
        self,
        default_delay: float = 2.0,
        per_domain_enabled: bool = True,
        max_delay: float = 60.0,
        exponential_backoff_enabled: bool = False,
        base_backoff_delay: float = 1.0,
        max_backoff_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        retry_after_enabled: bool = False,
        max_retry_after_delay: float = 300.0,
    ):
        """Initialize enhanced rate limiter.

        Args:
            default_delay: Default delay between requests in seconds
            per_domain_enabled: Whether to enable per-domain rate limiting
            max_delay: Maximum allowed delay (safety limit)
            exponential_backoff_enabled: Whether to enable exponential backoff
            base_backoff_delay: Base delay for exponential backoff in seconds
            max_backoff_delay: Maximum backoff delay in seconds
            backoff_multiplier: Multiplier for exponential backoff
            retry_after_enabled: Whether to enable retry-after header support
            max_retry_after_delay: Maximum allowed retry-after delay in seconds
        """
        self.default_delay = default_delay
        self.per_domain_enabled = per_domain_enabled
        self.max_delay = max_delay

        # Exponential backoff configuration
        self.exponential_backoff_enabled = exponential_backoff_enabled
        self.base_backoff_delay = base_backoff_delay
        self.max_backoff_delay = max_backoff_delay
        self.backoff_multiplier = backoff_multiplier

        # Retry-after configuration
        self.retry_after_enabled = retry_after_enabled
        self.max_retry_after_delay = max_retry_after_delay

        # Validate configurations
        if exponential_backoff_enabled:
            self._validate_backoff_configuration()
        if retry_after_enabled:
            self._validate_retry_after_configuration()

        # For single-limiter mode when per-domain is disabled
        self._single_limiter = RateLimiter(default_delay, max_delay)

        # Per-domain storage
        self.domain_limiters: Dict[str, RateLimiter] = {}
        self.domain_configs: Dict[str, Dict[str, Any]] = {}
        self.domain_statistics: Dict[str, Dict[str, Any]] = {}

        # Exponential backoff storage
        self.domain_retry_counts: Dict[str, int] = {}
        self.domain_backoff_statistics: Dict[str, Dict[str, Any]] = {}

        # Retry-after storage
        self.domain_retry_after_delays: Dict[str, float] = {}
        self.domain_retry_after_statistics: Dict[str, Dict[str, Any]] = {}

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL.

        Args:
            url: URL to extract domain from

        Returns:
            str: Domain name
        """
        parsed = urlparse(url)
        return parsed.netloc.split(":")[0]  # Remove port if present

    def configure_domain_delay(self, domain: str, delay: float) -> None:
        """Configure delay for a specific domain.

        Args:
            domain: Domain name
            delay: Delay in seconds

        Raises:
            ValueError: If domain is empty or delay is invalid
        """
        if not domain:
            raise ValueError("Domain cannot be empty")
        if delay < 0:
            raise ValueError("Delay must be non-negative")

        self.domain_configs[domain] = {"delay": delay}

        # Update existing limiter if it exists
        if domain in self.domain_limiters:
            self.domain_limiters[domain] = RateLimiter(delay, self.max_delay)

    def _get_domain_limiter(self, domain: str) -> RateLimiter:
        """Get or create rate limiter for a domain.

        Args:
            domain: Domain name

        Returns:
            RateLimiter: Rate limiter for the domain
        """
        if domain not in self.domain_limiters:
            # Use configured delay or default
            delay = self.domain_configs.get(domain, {}).get("delay", self.default_delay)
            self.domain_limiters[domain] = RateLimiter(delay, self.max_delay)

            # Initialize statistics
            self.domain_statistics[domain] = {
                "total_requests": 0,
                "total_wait_time": 0.0,
                "average_wait_time": 0.0,
            }

        return self.domain_limiters[domain]

    def wait_if_needed(self, url: str) -> float:
        """Wait if necessary to enforce rate limiting.

        Args:
            url: URL being requested

        Returns:
            float: Time actually waited in seconds
        """
        if not self.per_domain_enabled:
            return self._single_limiter.wait_if_needed()

        domain = self._extract_domain(url)
        limiter = self._get_domain_limiter(domain)

        wait_time = limiter.wait_if_needed()

        # Update statistics
        stats = self.domain_statistics[domain]
        stats["total_requests"] += 1
        stats["total_wait_time"] += wait_time
        stats["average_wait_time"] = stats["total_wait_time"] / stats["total_requests"]

        return wait_time

    def reset_domain(self, domain: str) -> None:
        """Reset rate limiter for a specific domain.

        Args:
            domain: Domain name to reset
        """
        if domain in self.domain_limiters:
            self.domain_limiters[domain].reset()

    def reset(self) -> None:
        """Reset all rate limiters."""
        if not self.per_domain_enabled:
            self._single_limiter.reset()
        else:
            for limiter in self.domain_limiters.values():
                limiter.reset()

    def get_domain_statistics(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a domain.

        Args:
            domain: Domain name

        Returns:
            Dict[str, Any]: Domain statistics
        """
        return self.domain_statistics.get(
            domain,
            {"total_requests": 0, "total_wait_time": 0.0, "average_wait_time": 0.0},
        )

    def _validate_backoff_configuration(self) -> None:
        """Validate exponential backoff configuration."""
        if self.base_backoff_delay <= 0:
            raise ValueError("Base backoff delay must be positive")
        if self.max_backoff_delay <= 0:
            raise ValueError("Max backoff delay must be positive")
        if self.backoff_multiplier <= 1:
            raise ValueError("Backoff multiplier must be greater than 1")

    def _calculate_backoff_delay(self, retry_count: int) -> float:
        """Calculate exponential backoff delay for given retry count.

        Args:
            retry_count: Number of retries so far

        Returns:
            float: Backoff delay in seconds
        """
        if not self.exponential_backoff_enabled:
            return 0.0

        delay = self.base_backoff_delay * (self.backoff_multiplier**retry_count)
        return min(delay, self.max_backoff_delay)

    def apply_exponential_backoff(self, domain: str) -> float:
        """Apply exponential backoff for a failed request to a domain.

        Args:
            domain: Domain that failed

        Returns:
            float: Time actually waited in seconds
        """
        if not self.exponential_backoff_enabled:
            return 0.0

        # Get current retry count for domain
        current_retries = self.domain_retry_counts.get(domain, 0)

        # Calculate backoff delay
        backoff_delay = self._calculate_backoff_delay(current_retries)

        # Apply the delay
        start_time = time.time()
        time.sleep(backoff_delay)
        actual_wait = time.time() - start_time

        # Update retry count
        self.domain_retry_counts[domain] = current_retries + 1

        # Update statistics
        if domain not in self.domain_backoff_statistics:
            self.domain_backoff_statistics[domain] = {
                "total_backoff_applications": 0,
                "total_backoff_time": 0.0,
            }

        stats = self.domain_backoff_statistics[domain]
        stats["total_backoff_applications"] += 1
        stats["total_backoff_time"] += actual_wait

        return actual_wait

    def reset_exponential_backoff(self, domain: str) -> None:
        """Reset exponential backoff for a domain (call on successful request).

        Args:
            domain: Domain to reset backoff for
        """
        if domain in self.domain_retry_counts:
            del self.domain_retry_counts[domain]

    def reset_all_exponential_backoffs(self) -> None:
        """Reset all exponential backoff states."""
        self.domain_retry_counts.clear()

    def get_exponential_backoff_statistics(self, domain: str) -> Dict[str, Any]:
        """Get exponential backoff statistics for a domain.

        Args:
            domain: Domain name

        Returns:
            Dict[str, Any]: Backoff statistics
        """
        base_stats = self.domain_backoff_statistics.get(
            domain, {"total_backoff_applications": 0, "total_backoff_time": 0.0}
        )

        # Add current retry count
        base_stats["current_retry_count"] = self.domain_retry_counts.get(domain, 0)

        return base_stats

    def _validate_retry_after_configuration(self) -> None:
        """Validate retry-after configuration."""
        if self.max_retry_after_delay <= 0:
            raise ValueError("Max retry-after delay must be positive")

    def _parse_retry_after_header(self, retry_after_value: str) -> Optional[float]:
        """Parse retry-after header value.

        Args:
            retry_after_value: Value from Retry-After header

        Returns:
            Optional[float]: Delay in seconds, or None if invalid
        """
        if not retry_after_value:
            return None

        # Try parsing as seconds (integer)
        try:
            seconds = int(retry_after_value)
            if seconds < 0:
                return None
            return float(seconds)
        except ValueError:
            pass

        # Try parsing as HTTP date
        try:
            retry_time = parsedate_to_datetime(retry_after_value)
            current_time = datetime.datetime.now(datetime.timezone.utc)

            # If retry_time doesn't have timezone info, assume UTC
            if retry_time.tzinfo is None:
                retry_time = retry_time.replace(tzinfo=datetime.timezone.utc)

            delay = (retry_time - current_time).total_seconds()
            return max(0.0, delay)  # Don't return negative delays
        except (ValueError, TypeError):
            pass

        return None

    def apply_retry_after_delay(self, domain: str, retry_after_delay: float) -> float:
        """Apply retry-after delay for a domain.

        Args:
            domain: Domain to apply delay for
            retry_after_delay: Delay in seconds from retry-after header

        Returns:
            float: Time actually waited in seconds
        """
        if not self.retry_after_enabled:
            return 0.0

        # Cap the delay at maximum allowed
        capped_delay = min(retry_after_delay, self.max_retry_after_delay)

        # Apply the delay
        start_time = time.time()
        time.sleep(capped_delay)
        actual_wait = time.time() - start_time

        # Store the delay for next request
        self.domain_retry_after_delays[domain] = capped_delay

        # Update statistics
        if domain not in self.domain_retry_after_statistics:
            self.domain_retry_after_statistics[domain] = {
                "total_retry_after_applications": 0,
                "total_retry_after_time": 0.0,
            }

        stats = self.domain_retry_after_statistics[domain]
        stats["total_retry_after_applications"] += 1
        stats["total_retry_after_time"] += actual_wait

        return actual_wait

    def wait_if_needed_with_retry_after(self, url: str) -> float:
        """Wait if necessary, checking retry-after delay first.

        Args:
            url: URL being requested

        Returns:
            float: Time actually waited in seconds
        """
        domain = self._extract_domain(url)

        # Check if there's a pending retry-after delay
        if self.retry_after_enabled and domain in self.domain_retry_after_delays:
            retry_after_delay = self.domain_retry_after_delays[domain]

            # Remove the retry-after delay (one-time use)
            del self.domain_retry_after_delays[domain]

            # Apply retry-after delay
            start_time = time.time()
            time.sleep(retry_after_delay)
            actual_wait = time.time() - start_time

            # Update domain limiter timestamp to prevent double-delay
            if self.per_domain_enabled:
                limiter = self._get_domain_limiter(domain)
                limiter.last_request_time = time.time()
            else:
                self._single_limiter.last_request_time = time.time()

            return actual_wait
        else:
            # Fall back to normal rate limiting
            return self.wait_if_needed(url)

    def reset_retry_after_delay(self, domain: str) -> None:
        """Reset retry-after delay for a domain.

        Args:
            domain: Domain to reset retry-after delay for
        """
        if domain in self.domain_retry_after_delays:
            del self.domain_retry_after_delays[domain]

    def reset_all_retry_after_delays(self) -> None:
        """Reset all retry-after delays."""
        self.domain_retry_after_delays.clear()

    def get_retry_after_statistics(self, domain: str) -> Dict[str, Any]:
        """Get retry-after statistics for a domain.

        Args:
            domain: Domain name

        Returns:
            Dict[str, Any]: Retry-after statistics
        """
        base_stats = self.domain_retry_after_statistics.get(
            domain, {"total_retry_after_applications": 0, "total_retry_after_time": 0.0}
        )

        # Add current retry-after delay if any
        base_stats["current_retry_after_delay"] = self.domain_retry_after_delays.get(
            domain, 0.0
        )

        return base_stats
