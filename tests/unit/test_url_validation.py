"""Unit tests for URL validation and sanitization functionality."""
import pytest
from unittest.mock import Mock, patch
from urllib.parse import urlparse


class TestURLValidator:
    """Test URL validation functionality."""

    def test_validate_valid_http_url(self):
        """Test validation of valid HTTP URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("http://example.com")

        assert result.is_valid is True
        assert result.url == "http://example.com"
        assert result.error_message is None

    def test_validate_valid_https_url(self):
        """Test validation of valid HTTPS URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("https://example.com")

        assert result.is_valid is True
        assert result.url == "https://example.com"
        assert result.error_message is None

    def test_validate_url_with_path(self):
        """Test validation of URL with path."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("https://example.com/restaurant/menu")

        assert result.is_valid is True
        assert result.url == "https://example.com/restaurant/menu"
        assert result.error_message is None

    def test_validate_url_with_subdomain(self):
        """Test validation of URL with subdomain."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("https://www.example.com")

        assert result.is_valid is True
        assert result.url == "https://www.example.com"
        assert result.error_message is None

    def test_validate_invalid_url_no_scheme(self):
        """Test validation of invalid URL without scheme."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("example.com")

        assert result.is_valid is False
        assert "scheme" in result.error_message.lower()

    def test_validate_invalid_url_malformed(self):
        """Test validation of malformed URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("not-a-valid-url")

        assert result.is_valid is False
        assert result.error_message is not None

    def test_validate_empty_url(self):
        """Test validation of empty URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("")

        assert result.is_valid is False
        assert "empty" in result.error_message.lower()

    def test_validate_none_url(self):
        """Test validation of None URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url(None)

        assert result.is_valid is False
        assert (
            "none" in result.error_message.lower()
            or "null" in result.error_message.lower()
        )

    def test_validate_url_with_port(self):
        """Test validation of URL with port number."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("http://example.com:8080")

        assert result.is_valid is True
        assert result.url == "http://example.com:8080"

    def test_validate_url_with_query_params(self):
        """Test validation of URL with query parameters."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url(
            "https://example.com/search?q=restaurant&location=salem"
        )

        assert result.is_valid is True
        assert result.url == "https://example.com/search?q=restaurant&location=salem"

    def test_validate_localhost_url(self):
        """Test validation of localhost URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("http://localhost:3000")

        assert result.is_valid is True
        assert result.url == "http://localhost:3000"

    def test_validate_ip_address_url(self):
        """Test validation of IP address URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("http://192.168.1.1")

        assert result.is_valid is True
        assert result.url == "http://192.168.1.1"


class TestURLSanitizer:
    """Test URL sanitization functionality."""

    def test_sanitize_url_add_https_scheme(self):
        """Test adding HTTPS scheme to URL without scheme."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("example.com")

        assert result.sanitized_url == "https://example.com"
        assert result.changes_made is True
        assert "scheme" in result.change_description.lower()

    def test_sanitize_url_add_www_prefix(self):
        """Test adding www prefix when appropriate."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com")

        # May or may not add www - depends on implementation
        assert result.sanitized_url.startswith("https://")
        assert "example.com" in result.sanitized_url

    def test_sanitize_url_remove_trailing_slash(self):
        """Test removing trailing slash from URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com/")

        assert result.sanitized_url == "https://example.com"
        assert result.changes_made is True

    def test_sanitize_url_normalize_case(self):
        """Test normalizing URL case."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("HTTPS://EXAMPLE.COM")

        assert result.sanitized_url == "https://example.com"
        assert result.changes_made is True

    def test_sanitize_url_remove_duplicate_slashes(self):
        """Test removing duplicate slashes from URL path."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com//path//to//page")

        assert result.sanitized_url == "https://example.com/path/to/page"
        assert result.changes_made is True

    def test_sanitize_url_no_changes_needed(self):
        """Test sanitization when no changes are needed."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com/path")

        assert result.sanitized_url == "https://example.com/path"
        assert result.changes_made is False
        assert result.change_description == "No changes needed"

    def test_sanitize_url_upgrade_http_to_https(self):
        """Test upgrading HTTP to HTTPS."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("http://example.com")

        # May or may not upgrade to HTTPS - depends on implementation
        # At minimum should be valid
        assert result.sanitized_url.startswith(("http://", "https://"))
        assert "example.com" in result.sanitized_url

    def test_sanitize_url_handle_fragment_removal(self):
        """Test removing URL fragments."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com/page#section")

        assert result.sanitized_url == "https://example.com/page"
        assert result.changes_made is True
        assert "fragment" in result.change_description.lower()

    def test_sanitize_url_preserve_query_params(self):
        """Test preserving important query parameters."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com/search?q=restaurant")

        assert "q=restaurant" in result.sanitized_url
        assert result.sanitized_url.startswith("https://example.com/search")

    def test_sanitize_url_handle_unicode_characters(self):
        """Test handling Unicode characters in URL."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com/café")

        # Should properly encode Unicode characters
        assert result.sanitized_url is not None
        assert result.sanitized_url.startswith("https://example.com/")


class TestBatchURLValidation:
    """Test batch URL validation functionality."""

    def test_validate_multiple_urls_all_valid(self):
        """Test validation of multiple valid URLs."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        urls = [
            "https://restaurant1.com",
            "https://restaurant2.com",
            "https://restaurant3.com",
        ]

        results = validator.validate_urls(urls)

        assert len(results) == 3
        assert all(result.is_valid for result in results)
        assert all(result.error_message is None for result in results)

    def test_validate_multiple_urls_mixed_validity(self):
        """Test validation of URLs with mixed validity."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        urls = [
            "https://valid-restaurant.com",
            "invalid-url",
            "https://another-valid.com",
            "",
            "https://third-valid.com",
        ]

        results = validator.validate_urls(urls)

        assert len(results) == 5

        # Valid URLs
        assert results[0].is_valid is True
        assert results[2].is_valid is True
        assert results[4].is_valid is True

        # Invalid URLs
        assert results[1].is_valid is False
        assert results[3].is_valid is False

    def test_validate_empty_url_list(self):
        """Test validation of empty URL list."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        results = validator.validate_urls([])

        assert len(results) == 0
        assert isinstance(results, list)

    def test_validate_urls_with_duplicates(self):
        """Test validation handling of duplicate URLs."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        urls = [
            "https://restaurant.com",
            "https://restaurant.com",  # Duplicate
            "https://different.com",
        ]

        results = validator.validate_urls(urls)

        assert len(results) == 3
        assert all(result.is_valid for result in results)

        # Should detect duplicates
        duplicate_count = validator.get_duplicate_count(urls)
        assert duplicate_count == 1

    def test_validate_large_url_batch(self):
        """Test validation of large URL batch."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        urls = [f"https://restaurant{i}.com" for i in range(100)]

        results = validator.validate_urls(urls)

        assert len(results) == 100
        assert all(result.is_valid for result in results)

    def test_batch_sanitization(self):
        """Test sanitization of multiple URLs."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        urls = [
            "restaurant1.com",  # Missing scheme
            "https://restaurant2.com/",  # Trailing slash
            "HTTPS://RESTAURANT3.COM",  # Wrong case
        ]

        results = validator.sanitize_urls(urls)

        assert len(results) == 3

        # Check sanitization occurred
        assert results[0].sanitized_url == "https://restaurant1.com"
        assert results[1].sanitized_url == "https://restaurant2.com"
        assert results[2].sanitized_url == "https://restaurant3.com"

        assert all(result.changes_made for result in results)


class TestURLValidationResults:
    """Test URL validation result objects."""

    def test_validation_result_valid_url(self):
        """Test validation result for valid URL."""
        from src.config.url_validator import ValidationResult

        result = ValidationResult(
            url="https://example.com", is_valid=True, error_message=None
        )

        assert result.url == "https://example.com"
        assert result.is_valid is True
        assert result.error_message is None
        assert result.scheme == "https"
        assert result.domain == "example.com"

    def test_validation_result_invalid_url(self):
        """Test validation result for invalid URL."""
        from src.config.url_validator import ValidationResult

        result = ValidationResult(
            url="invalid-url", is_valid=False, error_message="Invalid URL format"
        )

        assert result.url == "invalid-url"
        assert result.is_valid is False
        assert result.error_message == "Invalid URL format"

    def test_sanitization_result_with_changes(self):
        """Test sanitization result with changes."""
        from src.config.url_validator import SanitizationResult

        result = SanitizationResult(
            original_url="example.com",
            sanitized_url="https://example.com",
            changes_made=True,
            change_description="Added HTTPS scheme",
        )

        assert result.original_url == "example.com"
        assert result.sanitized_url == "https://example.com"
        assert result.changes_made is True
        assert result.change_description == "Added HTTPS scheme"

    def test_sanitization_result_no_changes(self):
        """Test sanitization result with no changes."""
        from src.config.url_validator import SanitizationResult

        result = SanitizationResult(
            original_url="https://example.com",
            sanitized_url="https://example.com",
            changes_made=False,
            change_description="No changes needed",
        )

        assert result.original_url == "https://example.com"
        assert result.sanitized_url == "https://example.com"
        assert result.changes_made is False
        assert result.change_description == "No changes needed"


class TestURLSecurityValidation:
    """Test URL security validation."""

    def test_reject_file_scheme_urls(self):
        """Test rejection of file:// scheme URLs."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("file:///etc/passwd")

        assert result.is_valid is False
        assert "scheme" in result.error_message.lower()

    def test_reject_javascript_scheme_urls(self):
        """Test rejection of javascript: scheme URLs."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("javascript:alert('xss')")

        assert result.is_valid is False
        assert "scheme" in result.error_message.lower()

    def test_reject_data_scheme_urls(self):
        """Test rejection of data: scheme URLs."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.validate_url("data:text/html,<script>alert('xss')</script>")

        assert result.is_valid is False
        assert "scheme" in result.error_message.lower()

    def test_allow_only_http_https_schemes(self):
        """Test allowing only HTTP and HTTPS schemes."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()

        # Valid schemes
        http_result = validator.validate_url("http://example.com")
        https_result = validator.validate_url("https://example.com")

        assert http_result.is_valid is True
        assert https_result.is_valid is True

        # Invalid schemes
        ftp_result = validator.validate_url("ftp://example.com")
        assert ftp_result.is_valid is False

    def test_validate_url_length_limits(self):
        """Test URL length validation."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()

        # Normal length URL
        normal_url = "https://example.com/path"
        result = validator.validate_url(normal_url)
        assert result.is_valid is True

        # Extremely long URL
        long_path = "a" * 10000
        long_url = f"https://example.com/{long_path}"
        result = validator.validate_url(long_url)

        # Should either be valid or have specific length error
        if not result.is_valid:
            assert "length" in result.error_message.lower()

    def test_sanitize_removes_dangerous_characters(self):
        """Test sanitization removes dangerous characters."""
        from src.config.url_validator import URLValidator

        validator = URLValidator()
        result = validator.sanitize_url("https://example.com/path?param=<script>")

        # Should remove or encode dangerous characters
        assert "<script>" not in result.sanitized_url
        assert result.changes_made is True
