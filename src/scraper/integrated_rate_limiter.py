"""Integrated rate limiter for ethical and consistent scraping."""

import time
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import threading


@dataclass
class RateLimitStatistics:
    """Statistics for rate limiting operations."""
    total_requests: int = 0
    total_delays: int = 0
    total_delay_time: float = 0.0
    robots_txt_checks: int = 0
    robots_txt_allowed: int = 0
    robots_txt_disallowed: int = 0
    requests_per_domain: Dict[str, int] = field(default_factory=dict)
    unique_domains: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    @property
    def average_delay_time(self) -> float:
        """Get average delay time."""
        return self.total_delay_time / self.total_delays if self.total_delays > 0 else 0.0
    
    @property
    def robots_txt_compliance_rate(self) -> float:
        """Get robots.txt compliance rate."""
        total_checks = self.robots_txt_allowed + self.robots_txt_disallowed
        return self.robots_txt_allowed / total_checks if total_checks > 0 else 0.0
    
    def record_request(self, url: str):
        """Record a request for statistics."""
        self.total_requests += 1
        domain = urlparse(url).netloc
        
        if domain not in self.requests_per_domain:
            self.requests_per_domain[domain] = 0
            self.unique_domains += 1
        
        self.requests_per_domain[domain] += 1
    
    def record_delay(self, url: str, delay_time: float):
        """Record a delay for statistics."""
        self.total_delays += 1
        self.total_delay_time += delay_time
    
    def record_robots_txt_check(self, url: str, allowed: bool):
        """Record a robots.txt check."""
        self.robots_txt_checks += 1
        if allowed:
            self.robots_txt_allowed += 1
        else:
            self.robots_txt_disallowed += 1
    
    def record_performance_metric(self, metric_name: str, value: float):
        """Record a performance metric."""
        self.performance_metrics[metric_name] = value
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics."""
        return self.performance_metrics.copy()
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format."""
        return {
            'total_requests': self.total_requests,
            'total_delays': self.total_delays,
            'total_delay_time': self.total_delay_time,
            'average_delay_time': self.average_delay_time,
            'robots_txt_checks': self.robots_txt_checks,
            'robots_txt_allowed': self.robots_txt_allowed,
            'robots_txt_disallowed': self.robots_txt_disallowed,
            'robots_txt_compliance_rate': self.robots_txt_compliance_rate,
            'unique_domains': self.unique_domains,
            'requests_per_domain': self.requests_per_domain,
            'performance_metrics': self.performance_metrics
        }


class DomainRateLimiter:
    """Rate limiter for individual domains."""
    
    def __init__(self, domain: str, delay: float = 1.0, max_requests_per_minute: int = 60, use_exponential_backoff: bool = False):
        """Initialize domain rate limiter.
        
        Args:
            domain: Domain name
            delay: Delay between requests in seconds
            max_requests_per_minute: Maximum requests per minute
            use_exponential_backoff: Whether to use exponential backoff
        """
        self.domain = domain
        self.delay = delay
        self.max_requests_per_minute = max_requests_per_minute
        self.use_exponential_backoff = use_exponential_backoff
        
        # Request tracking
        self.request_times = []
        self.failure_count = 0
        self.last_request_time = 0
        
        # Thread safety
        self.lock = threading.Lock()
    
    def can_make_request(self) -> bool:
        """Check if a request can be made now."""
        with self.lock:
            current_time = time.time()
            
            # Check if enough time has passed since last request
            if current_time - self.last_request_time < self.delay:
                return False
            
            # Check requests per minute limit
            recent_requests = [t for t in self.request_times if current_time - t < 60]
            if len(recent_requests) >= self.max_requests_per_minute:
                return False
            
            return True
    
    def record_request(self):
        """Record a request."""
        with self.lock:
            current_time = time.time()
            self.request_times.append(current_time)
            self.last_request_time = current_time
            
            # Keep only recent requests
            self.request_times = [t for t in self.request_times if current_time - t < 60]
    
    def record_failure(self):
        """Record a failure (for exponential backoff)."""
        with self.lock:
            self.failure_count += 1
    
    def record_success(self):
        """Record a success (reset failure count)."""
        with self.lock:
            self.failure_count = 0
    
    def get_required_delay(self) -> float:
        """Get the required delay before next request."""
        with self.lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            base_delay = self.delay
            
            # Apply exponential backoff if enabled
            if self.use_exponential_backoff and self.failure_count > 0:
                base_delay = min(base_delay * (2 ** self.failure_count), 60)  # Cap at 60 seconds
            
            required_delay = max(0, base_delay - time_since_last_request)
            return required_delay
    
    def get_request_count(self) -> int:
        """Get total request count."""
        with self.lock:
            return len(self.request_times)
    
    def get_requests_in_last_minute(self) -> int:
        """Get requests in the last minute."""
        with self.lock:
            current_time = time.time()
            recent_requests = [t for t in self.request_times if current_time - t < 60]
            return len(recent_requests)
    
    def can_make_concurrent_request(self) -> bool:
        """Check if concurrent requests are allowed."""
        # Simple implementation - allow concurrent requests if under limit
        return self.get_requests_in_last_minute() < self.max_requests_per_minute


class EthicalComplianceChecker:
    """Checks ethical compliance for web scraping."""
    
    def __init__(self, user_agent: str = None):
        """Initialize ethical compliance checker.
        
        Args:
            user_agent: User agent string to use
        """
        self.user_agent = user_agent or "RAGScraper/1.0 (+https://example.com/bot-info)"
        self.robots_txt_cache = {}
        self.request_history = defaultdict(list)
    
    def check_robots_txt(self, url: str) -> Dict[str, Any]:
        """Check robots.txt compliance for a URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with compliance information
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check cache first
        if domain in self.robots_txt_cache:
            robots_txt = self.robots_txt_cache[domain]
        else:
            robots_txt = self.fetch_robots_txt(urljoin(f"{parsed_url.scheme}://{domain}", "/robots.txt"))
            self.robots_txt_cache[domain] = robots_txt
        
        # Parse robots.txt
        if robots_txt:
            return self._parse_robots_txt(robots_txt, url)
        else:
            # If no robots.txt, assume allowed
            return {
                'allowed': True,
                'crawl_delay': None,
                'user_agent_allowed': True
            }
    
    def fetch_robots_txt(self, robots_url: str) -> Optional[str]:
        """Fetch robots.txt content.
        
        Args:
            robots_url: URL to robots.txt file
            
        Returns:
            Robots.txt content or None if not found
        """
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            pass
        return None
    
    def _parse_robots_txt(self, robots_txt: str, url: str) -> Dict[str, Any]:
        """Parse robots.txt content.
        
        Args:
            robots_txt: Robots.txt content
            url: URL being checked
            
        Returns:
            Dictionary with parsed information
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        lines = robots_txt.strip().split('\n')
        current_user_agent = None
        crawl_delay = None
        disallowed_paths = []
        allowed_paths = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.lower().startswith('user-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            elif line.lower().startswith('disallow:') and current_user_agent == '*':
                disallowed_path = line.split(':', 1)[1].strip()
                if disallowed_path:
                    disallowed_paths.append(disallowed_path)
            elif line.lower().startswith('allow:') and current_user_agent == '*':
                allowed_path = line.split(':', 1)[1].strip()
                if allowed_path:
                    allowed_paths.append(allowed_path)
            elif line.lower().startswith('crawl-delay:') and current_user_agent == '*':
                try:
                    crawl_delay = float(line.split(':', 1)[1].strip())
                except ValueError:
                    crawl_delay = None
        
        # Check if path is disallowed
        for disallowed_path in disallowed_paths:
            if path.startswith(disallowed_path):
                return {
                    'allowed': False,
                    'crawl_delay': crawl_delay,
                    'user_agent_allowed': False,
                    'disallow_reason': "Path explicitly disallowed"
                }
        
        # Check if path is explicitly allowed
        for allowed_path in allowed_paths:
            if path.startswith(allowed_path):
                return {
                    'allowed': True,
                    'crawl_delay': crawl_delay,
                    'user_agent_allowed': True
                }
        
        # Default to allowed if not explicitly disallowed
        return {
            'allowed': True,
            'crawl_delay': crawl_delay,
            'user_agent_allowed': True
        }
    
    def is_user_agent_appropriate(self, user_agent: str) -> bool:
        """Check if user agent is appropriate for ethical scraping.
        
        Args:
            user_agent: User agent string to check
            
        Returns:
            True if user agent is appropriate
        """
        # Check for bot identification and contact info
        if "bot" in user_agent.lower() or "scraper" in user_agent.lower():
            return True
        
        # Check for contact information
        if "+" in user_agent and ("http" in user_agent or "mailto" in user_agent):
            return True
        
        # Reject fake browser user agents
        if user_agent.startswith("Mozilla/5.0") and "fake" in user_agent.lower():
            return False
        
        return False
    
    def are_request_headers_appropriate(self, headers: Dict[str, str]) -> bool:
        """Check if request headers are appropriate.
        
        Args:
            headers: Request headers dictionary
            
        Returns:
            True if headers are appropriate
        """
        # Must have User-Agent header
        if 'User-Agent' not in headers:
            return False
        
        # Check if user agent is appropriate
        if not self.is_user_agent_appropriate(headers['User-Agent']):
            return False
        
        # Should have common headers
        expected_headers = ['Accept', 'Accept-Language', 'Accept-Encoding']
        for header in expected_headers:
            if header not in headers:
                return False
        
        return True
    
    def record_request(self, url: str, timestamp: float):
        """Record a request for frequency checking.
        
        Args:
            url: URL that was requested
            timestamp: Time of the request
        """
        domain = urlparse(url).netloc
        self.request_history[domain].append(timestamp)
        
        # Keep only recent requests
        current_time = time.time()
        self.request_history[domain] = [
            t for t in self.request_history[domain] 
            if current_time - t < 300  # Keep 5 minutes of history
        ]
    
    def is_request_frequency_appropriate(self, url: str, min_delay: float) -> bool:
        """Check if request frequency is appropriate.
        
        Args:
            url: URL being requested
            min_delay: Minimum delay between requests in seconds
            
        Returns:
            True if frequency is appropriate
        """
        domain = urlparse(url).netloc
        current_time = time.time()
        
        if domain not in self.request_history:
            return True
        
        recent_requests = self.request_history[domain]
        if not recent_requests:
            return True
        
        # Check if enough time has passed since last request
        time_since_last = current_time - recent_requests[-1]
        return time_since_last >= min_delay
    
    def check_ethical_compliance(self, url: str) -> Dict[str, Any]:
        """Check overall ethical compliance for a URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with compliance information
        """
        # Check robots.txt
        robots_result = self.check_robots_txt(url)
        
        # Check user agent
        user_agent_appropriate = self.is_user_agent_appropriate(self.user_agent)
        
        # Check request headers
        headers = {'User-Agent': self.user_agent}
        headers_appropriate = self.are_request_headers_appropriate(headers)
        
        # Check request frequency
        frequency_appropriate = self.is_request_frequency_appropriate(url, 2.0)
        
        is_compliant = (
            robots_result['allowed'] and
            user_agent_appropriate and
            headers_appropriate and
            frequency_appropriate
        )
        
        return {
            'is_compliant': is_compliant,
            'user_agent_appropriate': user_agent_appropriate,
            'request_headers_appropriate': headers_appropriate,
            'request_frequency_appropriate': frequency_appropriate,
            'robots_txt_compliant': robots_result['allowed']
        }


class IntegratedRateLimiter:
    """Integrated rate limiter with ethical compliance."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize integrated rate limiter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.default_delay = self.config.get('default_delay', 1.0)
        self.max_requests_per_minute = self.config.get('max_requests_per_minute', 60)
        self.respect_robots_txt = self.config.get('respect_robots_txt', True)
        self.ethical_compliance = self.config.get('ethical_compliance', True)
        
        # Initialize components
        self.domain_limiters = self._initialize_domain_limiters()
        self.ethical_checker = EthicalComplianceChecker()
        self.rate_limit_statistics = RateLimitStatistics()
        
        # Server response tracking
        self.server_response_history = defaultdict(list)
        
        # Thread safety
        self.lock = threading.Lock()
    
    def _initialize_domain_limiters(self) -> Dict[str, DomainRateLimiter]:
        """Initialize domain limiters."""
        limiters = {}
        
        # Add per-domain limits from config
        per_domain_limits = self.config.get('per_domain_limits', {})
        for domain, settings in per_domain_limits.items():
            limiters[domain] = DomainRateLimiter(
                domain=domain,
                delay=settings.get('delay', self.default_delay),
                max_requests_per_minute=settings.get('max_requests', self.max_requests_per_minute)
            )
        
        return limiters
    
    def get_limiter(self, domain: str) -> DomainRateLimiter:
        """Get or create domain limiter for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            DomainRateLimiter instance
        """
        with self.lock:
            if domain not in self.domain_limiters:
                self.domain_limiters[domain] = DomainRateLimiter(
                    domain=domain,
                    delay=self.default_delay,
                    max_requests_per_minute=self.max_requests_per_minute
                )
            
            return self.domain_limiters[domain]
    
    def check_rate_limit(self, url: str) -> Dict[str, Any]:
        """Check if a request can be made to the URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with rate limit information
        """
        domain = urlparse(url).netloc
        limiter = self.get_limiter(domain)
        
        can_proceed = limiter.can_make_request()
        required_delay = limiter.get_required_delay() if not can_proceed else 0
        
        return {
            'can_proceed': can_proceed,
            'required_delay': required_delay,
            'domain': domain
        }
    
    def apply_rate_limit(self, url: str, mode: str = 'single_page') -> Dict[str, Any]:
        """Apply rate limiting to a URL.
        
        Args:
            url: URL to rate limit
            mode: Processing mode
            
        Returns:
            Dictionary with rate limiting results
        """
        rate_limit_result = self.check_rate_limit(url)
        
        if not rate_limit_result['can_proceed']:
            delay_duration = rate_limit_result['required_delay']
            time.sleep(delay_duration)
            
            # Record statistics
            self.rate_limit_statistics.record_delay(url, delay_duration)
            
            return {
                'delay_applied': True,
                'delay_duration': delay_duration,
                'mode': mode
            }
        else:
            return {
                'delay_applied': False,
                'delay_duration': 0,
                'mode': mode
            }
    
    def apply_rate_limit_batch(self, urls: List[str], mode: str = 'multi_page') -> Dict[str, Any]:
        """Apply rate limiting to a batch of URLs.
        
        Args:
            urls: List of URLs to rate limit
            mode: Processing mode
            
        Returns:
            Dictionary with batch rate limiting results
        """
        total_delays = 0
        total_delay_time = 0.0
        
        for url in urls:
            result = self.apply_rate_limit(url, mode)
            if result['delay_applied']:
                total_delays += 1
                total_delay_time += result['delay_duration']
        
        return {
            'total_delays': total_delays,
            'total_delay_time': total_delay_time
        }
    
    def check_robots_txt_compliance(self, url: str) -> Dict[str, Any]:
        """Check robots.txt compliance for a URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with compliance information
        """
        return self.ethical_checker.check_robots_txt(url)
    
    def check_ethical_compliance(self, url: str) -> Dict[str, Any]:
        """Check overall ethical compliance for a URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with compliance information
        """
        return self.ethical_checker.check_ethical_compliance(url)
    
    def handle_server_rate_limit(self, url: str, response) -> Dict[str, Any]:
        """Handle server rate limit response.
        
        Args:
            url: URL that was rate limited
            response: HTTP response object
            
        Returns:
            Dictionary with rate limit handling information
        """
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                retry_after = int(retry_after)
            except ValueError:
                retry_after = None
        
        return {
            'is_rate_limited': True,
            'retry_after': retry_after,
            'should_retry': True,
            'default_delay': self.default_delay * 5 if not retry_after else None
        }
    
    def record_request(self, url: str):
        """Record a request for statistics.
        
        Args:
            url: URL that was requested
        """
        domain = urlparse(url).netloc
        limiter = self.get_limiter(domain)
        limiter.record_request()
        
        self.rate_limit_statistics.record_request(url)
    
    def record_robots_txt_check(self, url: str, allowed: bool):
        """Record a robots.txt check.
        
        Args:
            url: URL that was checked
            allowed: Whether the request was allowed
        """
        self.rate_limit_statistics.record_robots_txt_check(url, allowed)
    
    def record_server_response(self, url: str, status_code: int, response_time: Optional[float]):
        """Record a server response for adaptive rate limiting.
        
        Args:
            url: URL that was requested
            status_code: HTTP status code
            response_time: Response time in seconds
        """
        domain = urlparse(url).netloc
        timestamp = time.time()
        
        self.server_response_history[domain].append({
            'timestamp': timestamp,
            'status_code': status_code,
            'response_time': response_time
        })
        
        # Keep only recent responses
        cutoff_time = timestamp - 300  # 5 minutes
        self.server_response_history[domain] = [
            r for r in self.server_response_history[domain] 
            if r['timestamp'] > cutoff_time
        ]
        
        # Update domain limiter based on response
        limiter = self.get_limiter(domain)
        if status_code == 200:
            limiter.record_success()
        elif status_code == 429:
            limiter.record_failure()
    
    def get_adaptive_delay(self, url: str) -> float:
        """Get adaptive delay based on server responses.
        
        Args:
            url: URL to get delay for
            
        Returns:
            Adaptive delay in seconds
        """
        domain = urlparse(url).netloc
        
        if domain not in self.server_response_history:
            return self.default_delay
        
        recent_responses = self.server_response_history[domain]
        if not recent_responses:
            return self.default_delay
        
        # Count recent rate limit responses
        rate_limited_count = sum(1 for r in recent_responses if r['status_code'] == 429)
        
        # Increase delay if we've been rate limited
        if rate_limited_count > 0:
            return self.default_delay * (1 + rate_limited_count)
        
        return self.default_delay
    
    def check_concurrent_requests(self, urls: List[str]) -> Dict[str, Any]:
        """Check if concurrent requests can be made to URLs.
        
        Args:
            urls: List of URLs to check
            
        Returns:
            Dictionary with concurrent request information
        """
        concurrent_allowed = 0
        
        for url in urls:
            domain = urlparse(url).netloc
            limiter = self.get_limiter(domain)
            
            if limiter.can_make_concurrent_request():
                concurrent_allowed += 1
        
        return {
            'can_proceed': concurrent_allowed > 0,
            'concurrent_requests_allowed': concurrent_allowed
        }
    
    def get_rate_limit_statistics(self) -> RateLimitStatistics:
        """Get rate limit statistics.
        
        Returns:
            RateLimitStatistics object
        """
        return self.rate_limit_statistics