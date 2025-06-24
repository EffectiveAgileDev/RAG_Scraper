"""Integration tests to verify PageProcessor and MultiPageScraper work together."""
import pytest
from unittest.mock import Mock, patch

from src.scraper.multi_page_scraper import MultiPageScraper
from src.scraper.page_processor import PageProcessor
from src.scraper.multi_strategy_scraper import RestaurantData


class TestPageProcessorIntegration:
    """Integration tests for PageProcessor with MultiPageScraper."""

    def test_page_processor_can_be_used_independently(self):
        """Test that PageProcessor can be used standalone."""
        processor = PageProcessor(enable_ethical_scraping=False)
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><head><title>Test Restaurant</title></head></html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            html_content = processor._fetch_page("http://example.com")
            assert html_content is not None
            assert "Test Restaurant" in html_content
            
            restaurant_name = processor._extract_restaurant_name(html_content)
            assert restaurant_name == "Test Restaurant"

    def test_multi_page_scraper_integration_with_page_processor(self):
        """Test that MultiPageScraper properly integrates with PageProcessor."""
        scraper = MultiPageScraper(max_pages=3, enable_ethical_scraping=False)
        
        # Verify PageProcessor is properly initialized
        assert hasattr(scraper, 'page_processor')
        assert isinstance(scraper.page_processor, PageProcessor)
        assert scraper.page_processor.enable_ethical_scraping == scraper.enable_ethical_scraping
        
        # Test that methods are properly delegated
        with patch.object(scraper.page_processor, '_fetch_page') as mock_fetch:
            mock_fetch.return_value = "<html>content</html>"
            
            result = scraper._fetch_page("http://example.com")
            assert result == "<html>content</html>"
            mock_fetch.assert_called_once_with("http://example.com")

    def test_page_processor_configuration_consistency(self):
        """Test that PageProcessor configuration matches MultiPageScraper."""
        # Test with ethical scraping enabled
        scraper1 = MultiPageScraper(enable_ethical_scraping=True)
        assert scraper1.page_processor.enable_ethical_scraping is True
        
        # Test with ethical scraping disabled
        scraper2 = MultiPageScraper(enable_ethical_scraping=False)
        assert scraper2.page_processor.enable_ethical_scraping is False

    def test_page_processor_error_handling_integration(self):
        """Test that error handling works correctly through the integration."""
        scraper = MultiPageScraper(enable_ethical_scraping=False)
        
        with patch.object(scraper.page_processor, '_fetch_page') as mock_fetch:
            # Simulate network error
            mock_fetch.return_value = None
            
            result = scraper._fetch_and_process_page("http://example.com")
            assert result is None
            mock_fetch.assert_called_once_with("http://example.com")

    def test_multi_page_scraper_coordination_methods_still_work(self):
        """Test that coordination methods in MultiPageScraper are unaffected."""
        scraper = MultiPageScraper(max_pages=5)
        
        # These should still exist and be callable
        assert callable(scraper.scrape_website)
        assert callable(scraper.process_discovered_pages)
        assert callable(scraper.get_current_progress)
        
        # Test queue management methods still work
        assert callable(scraper._initialize_page_queue)
        assert callable(scraper._add_pages_to_queue)
        assert callable(scraper._get_next_page)
        
        # Test error handling methods still work
        assert callable(scraper._handle_page_error)
        assert callable(scraper._retry_failed_page)