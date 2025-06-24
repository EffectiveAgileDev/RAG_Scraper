"""Unit tests for PageProcessor class - Test-Driven Development."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from src.scraper.page_processor import PageProcessor
from src.scraper.multi_strategy_scraper import RestaurantData


class TestPageProcessor:
    """Test suite for PageProcessor class."""

    def test_page_processor_initialization(self):
        """Test PageProcessor can be initialized with required components."""
        processor = PageProcessor(enable_ethical_scraping=True)
        assert processor is not None
        assert processor.enable_ethical_scraping is True

    def test_fetch_page_with_ethical_scraping(self):
        """Test _fetch_page method with ethical scraping enabled."""
        processor = PageProcessor(enable_ethical_scraping=True)
        
        with patch.object(processor, 'multi_strategy_scraper') as mock_scraper:
            mock_scraper.ethical_scraper = Mock()
            mock_scraper.ethical_scraper.fetch_page_with_retry.return_value = "<html>content</html>"
            
            result = processor._fetch_page("http://example.com")
            assert result == "<html>content</html>"
            mock_scraper.ethical_scraper.fetch_page_with_retry.assert_called_once_with("http://example.com")

    def test_fetch_page_without_ethical_scraping(self):
        """Test _fetch_page method without ethical scraping."""
        processor = PageProcessor(enable_ethical_scraping=False)
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>content</html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = processor._fetch_page("http://example.com")
            assert result == "<html>content</html>"
            mock_get.assert_called_once_with("http://example.com", timeout=30)

    def test_fetch_page_handles_errors(self):
        """Test _fetch_page method handles network errors gracefully."""
        processor = PageProcessor(enable_ethical_scraping=False)
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = processor._fetch_page("http://example.com")
            assert result is None

    def test_fetch_and_process_page_success(self):
        """Test _fetch_and_process_page method with successful processing."""
        processor = PageProcessor(enable_ethical_scraping=True)
        
        with patch.object(processor, '_fetch_page') as mock_fetch, \
             patch.object(processor, 'page_classifier') as mock_classifier, \
             patch.object(processor, 'multi_strategy_scraper') as mock_scraper:
            
            mock_fetch.return_value = "<html>restaurant content</html>"
            mock_classifier.classify_page.return_value = "menu"
            mock_restaurant_data = RestaurantData(
                name="Test Restaurant",
                sources=["json-ld"]
            )
            mock_scraper.scrape_url.return_value = mock_restaurant_data
            
            result = processor._fetch_and_process_page("http://example.com/menu")
            
            assert result is not None
            assert result["page_type"] == "menu"
            assert result["data"] == mock_restaurant_data

    def test_fetch_and_process_page_fetch_failure(self):
        """Test _fetch_and_process_page method when page fetch fails."""
        processor = PageProcessor(enable_ethical_scraping=True)
        
        with patch.object(processor, '_fetch_page') as mock_fetch:
            mock_fetch.return_value = None
            
            result = processor._fetch_and_process_page("http://example.com/menu")
            assert result is None

    def test_fetch_and_process_page_scraping_failure(self):
        """Test _fetch_and_process_page method when scraping fails."""
        processor = PageProcessor(enable_ethical_scraping=True)
        
        with patch.object(processor, '_fetch_page') as mock_fetch, \
             patch.object(processor, 'page_classifier') as mock_classifier, \
             patch.object(processor, 'multi_strategy_scraper') as mock_scraper:
            
            mock_fetch.return_value = "<html>restaurant content</html>"
            mock_classifier.classify_page.return_value = "menu"
            mock_scraper.scrape_url.return_value = None
            
            result = processor._fetch_and_process_page("http://example.com/menu")
            
            assert result is not None
            assert result["page_type"] == "menu"
            assert result["data"].sources == ["heuristic"]

    def test_extract_restaurant_name_from_title(self):
        """Test _extract_restaurant_name method extracts from page title."""
        processor = PageProcessor()
        
        html_content = "<html><head><title>Pizza Palace | Best Pizza in Town</title></head></html>"
        
        result = processor._extract_restaurant_name(html_content)
        assert result == "Pizza Palace"

    def test_extract_restaurant_name_from_h1(self):
        """Test _extract_restaurant_name method extracts from h1 tag."""
        processor = PageProcessor()
        
        html_content = "<html><body><h1>Burger Heaven</h1></body></html>"
        
        result = processor._extract_restaurant_name(html_content)
        assert result == "Burger Heaven"

    def test_extract_restaurant_name_default_fallback(self):
        """Test _extract_restaurant_name method returns default when extraction fails."""
        processor = PageProcessor()
        
        html_content = "<html><body><p>No title or h1</p></body></html>"
        
        result = processor._extract_restaurant_name(html_content)
        assert result == "Restaurant"

    def test_extract_restaurant_name_handles_malformed_html(self):
        """Test _extract_restaurant_name method handles malformed HTML."""
        processor = PageProcessor()
        
        html_content = "<html><title>Broken HTML"
        
        result = processor._extract_restaurant_name(html_content)
        # BeautifulSoup is lenient and will parse this as "Broken HTML"
        assert result == "Broken HTML"

    def test_extract_restaurant_name_handles_parsing_exceptions(self):
        """Test _extract_restaurant_name method handles parsing exceptions."""
        processor = PageProcessor()
        
        # Mock BeautifulSoup to raise an exception
        with patch('src.scraper.page_processor.BeautifulSoup') as mock_soup:
            mock_soup.side_effect = Exception("Parsing error")
            
            result = processor._extract_restaurant_name("<html>content</html>")
            assert result == "Restaurant"  # Should return default on exception

    def test_page_processor_has_required_dependencies(self):
        """Test PageProcessor initializes with required dependencies."""
        processor = PageProcessor(enable_ethical_scraping=True)
        
        # Should have these attributes after initialization
        assert hasattr(processor, 'page_classifier')
        assert hasattr(processor, 'multi_strategy_scraper')
        assert hasattr(processor, 'enable_ethical_scraping')
        assert processor.enable_ethical_scraping is True