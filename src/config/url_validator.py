"""URL validation and sanitization for RAG_Scraper."""
import re
from urllib.parse import urlparse, urlunparse, quote
from typing import List, Optional


class ValidationResult:
    """Result of URL validation."""
    
    def __init__(self, url: str, is_valid: bool, error_message: Optional[str] = None):
        self.url = url
        self.is_valid = is_valid
        self.error_message = error_message
        
        # Parse URL components if valid
        if is_valid and url:
            try:
                parsed = urlparse(url)
                self.scheme = parsed.scheme
                self.domain = parsed.netloc
                self.path = parsed.path
            except Exception:
                self.scheme = None
                self.domain = None
                self.path = None
        else:
            self.scheme = None
            self.domain = None
            self.path = None


class SanitizationResult:
    """Result of URL sanitization."""
    
    def __init__(self, original_url: str, sanitized_url: str, 
                 changes_made: bool, change_description: str):
        self.original_url = original_url
        self.sanitized_url = sanitized_url
        self.changes_made = changes_made
        self.change_description = change_description


class URLValidator:
    """Validates and sanitizes URLs for web scraping."""
    
    ALLOWED_SCHEMES = {'http', 'https'}
    MAX_URL_LENGTH = 2048
    DANGEROUS_CHARS = ['<', '>', '"', "'", '&lt;', '&gt;', '&quot;', '&#']
    
    def validate_url(self, url: str) -> ValidationResult:
        """Validate a single URL."""
        # Handle None or empty URLs
        if url is None:
            return ValidationResult(url, False, "URL cannot be None")
        
        if not url or not url.strip():
            return ValidationResult(url, False, "URL cannot be empty")
        
        url = url.strip()
        
        # Check URL length
        if len(url) > self.MAX_URL_LENGTH:
            return ValidationResult(url, False, f"URL exceeds maximum length of {self.MAX_URL_LENGTH} characters")
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return ValidationResult(url, False, f"Malformed URL: {str(e)}")
        
        # Check scheme
        if not parsed.scheme:
            return ValidationResult(url, False, "URL must include a scheme (http:// or https://)")
        
        if parsed.scheme.lower() not in self.ALLOWED_SCHEMES:
            return ValidationResult(url, False, f"Invalid scheme '{parsed.scheme}'. Only HTTP and HTTPS are allowed")
        
        # Check domain
        if not parsed.netloc:
            return ValidationResult(url, False, "URL must include a domain")
        
        # Check for dangerous characters in path/query
        if any(char in url for char in self.DANGEROUS_CHARS):
            return ValidationResult(url, False, "URL contains potentially dangerous characters")
        
        return ValidationResult(url, True)
    
    def sanitize_url(self, url: str) -> SanitizationResult:
        """Sanitize a URL to make it valid and safe."""
        if not url:
            return SanitizationResult(url, url, False, "Cannot sanitize empty URL")
        
        original_url = url
        changes = []
        
        # Remove leading/trailing whitespace
        url = url.strip()
        if url != original_url:
            changes.append("removed whitespace")
        
        # Convert to lowercase for scheme and domain
        parsed = urlparse(url)
        
        # Add scheme if missing
        if not parsed.scheme:
            url = f"https://{url}"
            changes.append("added HTTPS scheme")
            parsed = urlparse(url)
        
        # Normalize scheme case
        if parsed.scheme != parsed.scheme.lower():
            changes.append("normalized scheme case")
        
        # Normalize domain case
        if parsed.netloc != parsed.netloc.lower():
            changes.append("normalized domain case")
        
        # Remove URL fragment
        if parsed.fragment:
            changes.append("removed fragment")
        
        # Remove duplicate slashes in path
        if "//" in parsed.path and parsed.path != "//":
            changes.append("removed duplicate slashes")
        
        # Remove dangerous characters from path and query
        safe_path = parsed.path
        safe_query = parsed.query
        
        for char in self.DANGEROUS_CHARS:
            if char in safe_path:
                safe_path = safe_path.replace(char, "")
                changes.append("removed dangerous characters")
            if char in safe_query:
                safe_query = safe_query.replace(char, "")
                changes.append("removed dangerous characters")
        
        # Clean up path
        if "//" in safe_path:
            safe_path = safe_path.replace("//", "/")
        
        # Reconstruct URL
        sanitized_parsed = parsed._replace(
            scheme=parsed.scheme.lower(),
            netloc=parsed.netloc.lower(),
            path=safe_path,
            query=safe_query,
            fragment=""  # Remove fragment
        )
        
        sanitized_url = urlunparse(sanitized_parsed)
        
        # Remove trailing slash from root path only
        if sanitized_url.endswith("/") and parsed.path == "/" and not parsed.query and not parsed.fragment:
            sanitized_url = sanitized_url.rstrip("/")
            changes.append("removed trailing slash")
        
        changes_made = len(changes) > 0
        change_description = "; ".join(changes) if changes else "No changes needed"
        
        return SanitizationResult(original_url, sanitized_url, changes_made, change_description)
    
    def validate_urls(self, urls: List[str]) -> List[ValidationResult]:
        """Validate multiple URLs."""
        return [self.validate_url(url) for url in urls]
    
    def sanitize_urls(self, urls: List[str]) -> List[SanitizationResult]:
        """Sanitize multiple URLs."""
        return [self.sanitize_url(url) for url in urls]
    
    def get_duplicate_count(self, urls: List[str]) -> int:
        """Count duplicate URLs in list."""
        return len(urls) - len(set(urls))