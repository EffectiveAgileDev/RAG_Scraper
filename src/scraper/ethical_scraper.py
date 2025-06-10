"""Ethical web scraper with rate limiting and robots.txt compliance."""
import requests
import time
import re
from urllib.parse import urljoin, urlparse
from typing import Optional, Dict, Any
from .rate_limiter import RateLimiter


class RobotsTxtParser:
    """Parser for robots.txt files."""
    
    def __init__(self, robots_content: str):
        """Initialize with robots.txt content."""
        self.rules = self._parse_robots_txt(robots_content)
    
    def _parse_robots_txt(self, content: str) -> Dict[str, Dict[str, list]]:
        """Parse robots.txt content into rules."""
        rules = {'*': {'allow': [], 'disallow': []}}
        current_user_agent = '*'
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ':' not in line:
                continue
                
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == 'user-agent':
                current_user_agent = value.lower()
                if current_user_agent not in rules:
                    rules[current_user_agent] = {'allow': [], 'disallow': []}
            elif key == 'allow':
                if current_user_agent not in rules:
                    rules[current_user_agent] = {'allow': [], 'disallow': []}
                rules[current_user_agent]['allow'].append(value)
            elif key == 'disallow':
                if current_user_agent not in rules:
                    rules[current_user_agent] = {'allow': [], 'disallow': []}
                # Only add non-empty disallow rules (empty disallow means allow all)
                if value.strip():
                    rules[current_user_agent]['disallow'].append(value)
        
        return rules
    
    def is_allowed(self, path: str, user_agent: str) -> bool:
        """Check if path is allowed for user agent."""
        user_agent = user_agent.lower()
        
        # Check specific user agent rules first
        if user_agent in self.rules:
            rules = self.rules[user_agent]
        else:
            rules = self.rules.get('*', {'allow': [], 'disallow': []})
        
        # Find the most specific matching rule (longest path match)
        best_allow_match = ""
        best_disallow_match = ""
        
        # Check allow rules
        for allow_path in rules.get('allow', []):
            if allow_path and path.startswith(allow_path):
                if len(allow_path) > len(best_allow_match):
                    best_allow_match = allow_path
        
        # Check disallow rules
        for disallow_path in rules.get('disallow', []):
            if disallow_path and path.startswith(disallow_path):
                if len(disallow_path) > len(best_disallow_match):
                    best_disallow_match = disallow_path
        
        # If we have both matches, the more specific (longer) one wins
        if best_allow_match and best_disallow_match:
            return len(best_allow_match) >= len(best_disallow_match)
        elif best_disallow_match:
            return False  # Disallowed
        else:
            return True  # No disallow rule or explicit allow


class EthicalScraper:
    """Ethical web scraper with rate limiting and robots.txt compliance."""
    
    def __init__(self, delay: float = 2.0, timeout: int = 30, 
                 user_agent: str = "RAG_Scraper/1.0 (Ethical Restaurant Data Scraper)"):
        """Initialize ethical scraper."""
        if delay < 0:
            raise ValueError("Delay cannot be negative")
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        if not user_agent.strip():
            raise ValueError("User agent cannot be empty")
        
        self.delay = delay
        self.timeout = timeout
        self.user_agent = user_agent
        self.rate_limiter = RateLimiter(delay)
        self.robots_cache = {}
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = urljoin(base_url, '/robots.txt')
            
            # Check cache first
            if robots_url in self.robots_cache:
                parser = self.robots_cache[robots_url]
            else:
                # Fetch robots.txt
                try:
                    response = requests.get(robots_url, timeout=self.timeout)
                    if response.status_code == 200:
                        parser = RobotsTxtParser(response.text)
                    else:
                        parser = RobotsTxtParser("")  # Empty = allow all
                except:
                    parser = RobotsTxtParser("")  # Error = allow all
                
                self.robots_cache[robots_url] = parser
            
            return parser.is_allowed(parsed_url.path, self.user_agent)
            
        except Exception:
            return True  # Default to allowing if error
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page with rate limiting."""
        try:
            self.rate_limiter.wait_if_needed()
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
            
        except Exception:
            return None
    
    def fetch_page_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch page with retry logic for rate limiting and errors."""
        for attempt in range(max_retries):
            try:
                self.rate_limiter.wait_if_needed()
                
                headers = {
                    'User-Agent': self.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                response = requests.get(url, headers=headers, timeout=self.timeout)
                
                if response.status_code == 429:  # Too Many Requests
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        time.sleep(int(retry_after))
                        continue
                
                response.raise_for_status()
                return response.text
                
            except Exception:
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None