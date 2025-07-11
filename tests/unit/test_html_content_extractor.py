"""Unit tests for HTML content extractor."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

# Import the modules we'll be testing
try:
    from src.processors.html_content_extractor import HTMLContentExtractor
except ImportError:
    HTMLContentExtractor = None


class TestHTMLContentExtractor:
    """Test cases for HTMLContentExtractor."""

    @pytest.fixture
    def sample_html_content(self):
        """Sample HTML content for testing."""
        return """
        <html>
        <head>
            <title>Mario's Italian Restaurant</title>
            <meta name="description" content="Authentic Italian cuisine in downtown Portland">
        </head>
        <body>
            <h1>MARIO'S ITALIAN RESTAURANT</h1>
            <p>123 Main Street, Portland, OR 97201</p>
            <p>Phone: (503) 555-0123</p>
            <p>Email: info@marios.com</p>
            
            <h2>APPETIZERS</h2>
            <ul>
                <li>Bruschetta - $8.99</li>
                <li>Garlic Bread - $5.99</li>
            </ul>
            
            <h2>MAIN COURSES</h2>
            <ul>
                <li>Spaghetti Carbonara - $16.99</li>
                <li>Chicken Parmigiana - $18.99</li>
            </ul>
            
            <h2>HOURS</h2>
            <p>Monday-Thursday: 11:00 AM - 9:00 PM</p>
            <p>Friday-Saturday: 11:00 AM - 10:00 PM</p>
            
            <h2>SERVICES</h2>
            <p>Delivery Available</p>
            <p>Takeout Available</p>
        </body>
        </html>
        """

    @pytest.fixture
    def sample_url(self):
        """Sample URL for testing."""
        return "https://example.com/restaurant"

    @pytest.fixture
    def html_extractor(self):
        """Create HTMLContentExtractor instance."""
        if HTMLContentExtractor is None:
            pytest.skip("HTMLContentExtractor not implemented yet")
        return HTMLContentExtractor()

    def test_html_content_extractor_initialization(self):
        """Test HTMLContentExtractor initializes correctly."""
        if HTMLContentExtractor is None:
            pytest.skip("HTMLContentExtractor not implemented yet")
        
        extractor = HTMLContentExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'extract_content')
        assert hasattr(extractor, 'validate_source')
        assert extractor.timeout == 30
        assert extractor.user_agent is not None

    def test_validate_source_with_url(self, html_extractor):
        """Test validation of URL sources."""
        # Valid URLs
        assert html_extractor.validate_source("https://example.com")
        assert html_extractor.validate_source("http://restaurant.com/menu")
        
        # Invalid URLs
        assert not html_extractor.validate_source("not-a-url")
        assert not html_extractor.validate_source("ftp://example.com")
        assert not html_extractor.validate_source("")

    def test_validate_source_with_html_content(self, html_extractor, sample_html_content):
        """Test validation of HTML content sources."""
        # Valid HTML content
        assert html_extractor.validate_source(sample_html_content)
        assert html_extractor.validate_source("<html><body>test</body></html>")
        
        # Invalid HTML content
        assert not html_extractor.validate_source("plain text without html")
        assert not html_extractor.validate_source("123456")

    def test_validate_source_with_bytes(self, html_extractor, sample_html_content):
        """Test validation of bytes sources."""
        # Valid HTML bytes
        html_bytes = sample_html_content.encode('utf-8')
        assert html_extractor.validate_source(html_bytes)
        
        # Invalid bytes
        assert not html_extractor.validate_source(b"not html content")
        assert not html_extractor.validate_source(b"\x00\x01\x02")

    def test_is_url_detection(self, html_extractor):
        """Test URL detection functionality."""
        # Valid URLs
        assert html_extractor._is_url("https://example.com")
        assert html_extractor._is_url("http://restaurant.com/menu")
        
        # Invalid URLs
        assert not html_extractor._is_url("not-a-url")
        assert not html_extractor._is_url("example.com")  # No scheme
        assert not html_extractor._is_url("")

    def test_contains_html_detection(self, html_extractor):
        """Test HTML content detection."""
        # Valid HTML content
        assert html_extractor._contains_html("<html><body>test</body></html>")
        assert html_extractor._contains_html("Some text <p>with html</p> tags")
        
        # Invalid HTML content
        assert not html_extractor._contains_html("plain text without html")
        assert not html_extractor._contains_html("no tags here")

    @patch('requests.Session.get')
    def test_fetch_html_from_url_success(self, mock_get, html_extractor, sample_html_content):
        """Test successful HTML fetching from URL."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = sample_html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = html_extractor._fetch_html_from_url("https://example.com")
        
        assert result == sample_html_content
        mock_get.assert_called_once_with("https://example.com", timeout=30)

    @patch('requests.Session.get')
    def test_fetch_html_from_url_failure(self, mock_get, html_extractor):
        """Test failed HTML fetching from URL."""
        # Mock failed response
        mock_get.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(requests.RequestException):
            html_extractor._fetch_html_from_url("https://example.com")

    def test_extract_text_from_html(self, html_extractor, sample_html_content):
        """Test text extraction from HTML content."""
        result = html_extractor._extract_text_from_html(sample_html_content)
        
        assert "MARIO'S ITALIAN RESTAURANT" in result
        assert "123 Main Street, Portland, OR 97201" in result
        assert "(503) 555-0123" in result
        assert "Bruschetta - $8.99" in result
        assert "Delivery Available" in result
        
        # Should not contain HTML tags
        assert "<html>" not in result
        assert "<body>" not in result
        assert "<h1>" not in result

    def test_extract_content_from_html_string(self, html_extractor, sample_html_content):
        """Test content extraction from HTML string."""
        result = html_extractor.extract_content(sample_html_content, "test.html")
        
        assert isinstance(result, str)
        assert "MARIO'S ITALIAN RESTAURANT" in result
        assert "123 Main Street" in result
        assert "(503) 555-0123" in result

    @patch('requests.Session.get')
    def test_extract_content_from_url(self, mock_get, html_extractor, sample_html_content):
        """Test content extraction from URL."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = sample_html_content
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = html_extractor.extract_content("https://example.com", "https://example.com")
        
        assert isinstance(result, str)
        assert "MARIO'S ITALIAN RESTAURANT" in result
        assert "123 Main Street" in result

    def test_extract_content_from_bytes(self, html_extractor, sample_html_content):
        """Test content extraction from bytes."""
        html_bytes = sample_html_content.encode('utf-8')
        result = html_extractor.extract_content(html_bytes, "test.html")
        
        assert isinstance(result, str)
        assert "MARIO'S ITALIAN RESTAURANT" in result

    def test_extract_content_invalid_source(self, html_extractor):
        """Test content extraction with invalid source."""
        with pytest.raises(ValueError):
            html_extractor.extract_content("not html or url", "test")

    def test_extract_structured_content(self, html_extractor, sample_html_content):
        """Test structured content extraction."""
        result = html_extractor.extract_structured_content(sample_html_content, "test.html")
        
        assert isinstance(result, dict)
        assert 'title' in result
        assert 'meta_description' in result
        assert 'headers' in result
        assert 'links' in result
        assert 'text_content' in result
        assert 'json_ld' in result
        assert 'microdata' in result
        
        assert result['title'] == "Mario's Italian Restaurant"
        assert "Authentic Italian cuisine" in result['meta_description']
        assert len(result['headers']) > 0
        assert "MARIO'S ITALIAN RESTAURANT" in result['text_content']

    def test_extract_title(self, html_extractor, sample_html_content):
        """Test title extraction."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html_content, 'html.parser')
        result = html_extractor._extract_title(soup)
        
        assert result == "Mario's Italian Restaurant"

    def test_extract_meta_description(self, html_extractor, sample_html_content):
        """Test meta description extraction."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html_content, 'html.parser')
        result = html_extractor._extract_meta_description(soup)
        
        assert "Authentic Italian cuisine" in result

    def test_extract_headers(self, html_extractor, sample_html_content):
        """Test headers extraction."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html_content, 'html.parser')
        result = html_extractor._extract_headers(soup)
        
        assert len(result) > 0
        assert any(header['text'] == "MARIO'S ITALIAN RESTAURANT" for header in result)
        assert any(header['text'] == "APPETIZERS" for header in result)

    def test_extract_links(self, html_extractor):
        """Test links extraction."""
        html_with_links = """
        <html>
        <body>
            <a href="https://example.com">Website</a>
            <a href="/menu">Menu</a>
        </body>
        </html>
        """
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_with_links, 'html.parser')
        result = html_extractor._extract_links(soup)
        
        assert len(result) == 2
        assert any(link['href'] == "https://example.com" for link in result)
        assert any(link['text'] == "Website" for link in result)

    def test_extract_json_ld(self, html_extractor):
        """Test JSON-LD extraction."""
        html_with_json_ld = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Restaurant",
                "name": "Mario's Italian Restaurant"
            }
            </script>
        </head>
        <body></body>
        </html>
        """
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_with_json_ld, 'html.parser')
        result = html_extractor._extract_json_ld(soup)
        
        assert len(result) == 1
        assert result[0]['@type'] == 'Restaurant'
        assert result[0]['name'] == "Mario's Italian Restaurant"

    def test_extract_microdata(self, html_extractor):
        """Test microdata extraction."""
        html_with_microdata = """
        <html>
        <body>
            <div itemscope itemtype="https://schema.org/Restaurant">
                <h1 itemprop="name">Mario's Italian Restaurant</h1>
                <div itemprop="address">123 Main Street</div>
            </div>
        </body>
        </html>
        """
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_with_microdata, 'html.parser')
        result = html_extractor._extract_microdata(soup)
        
        assert len(result) == 1
        assert result[0]['type'] == 'https://schema.org/Restaurant'
        assert result[0]['properties']['name'] == "Mario's Italian Restaurant"
        assert result[0]['properties']['address'] == "123 Main Street"

    def test_custom_timeout_and_user_agent(self):
        """Test custom timeout and user agent initialization."""
        if HTMLContentExtractor is None:
            pytest.skip("HTMLContentExtractor not implemented yet")
        
        custom_user_agent = "Test Agent 1.0"
        extractor = HTMLContentExtractor(timeout=60, user_agent=custom_user_agent)
        
        assert extractor.timeout == 60
        assert extractor.user_agent == custom_user_agent

    def test_session_headers(self, html_extractor):
        """Test session headers are set correctly."""
        assert 'User-Agent' in html_extractor.session.headers
        assert html_extractor.session.headers['User-Agent'] == html_extractor.user_agent