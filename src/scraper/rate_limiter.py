"""Rate limiting for ethical web scraping."""
import time


class RateLimiter:
    """Simple rate limiter to enforce delays between requests."""
    
    def __init__(self, delay: float = 2.0):
        """Initialize rate limiter with specified delay in seconds."""
        self.delay = delay
        self.last_request_time = None
    
    def wait_if_needed(self):
        """Wait if necessary to enforce rate limiting."""
        current_time = time.time()
        
        if self.last_request_time is not None:
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.delay:
                sleep_time = self.delay - time_since_last
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()