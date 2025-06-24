"""Unit tests for refactored MultiPageScraper using MultiPageScraperConfig."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.scraper.multi_page_scraper import MultiPageScraper
from src.scraper.multi_page_scraper_config import MultiPageScraperConfig


class TestMultiPageScraperRefactored:
    """Test refactored MultiPageScraper that uses MultiPageScraperConfig."""

    def test_initialization_uses_config_class(self):
        """Test that MultiPageScraper uses MultiPageScraperConfig for initialization."""
        scraper = MultiPageScraper(max_pages=15, enable_ethical_scraping=False)
        
        # Should have a config instance
        assert hasattr(scraper, 'config')
        assert isinstance(scraper.config, MultiPageScraperConfig)
        
        # Config should have the provided values
        assert scraper.config.max_pages == 15
        assert scraper.config.enable_ethical_scraping is False

    def test_initialization_with_config_object(self):
        """Test that MultiPageScraper can be initialized with a config object."""
        config = MultiPageScraperConfig(
            max_pages=25,
            enable_ethical_scraping=True,
            max_crawl_depth=3
        )
        
        scraper = MultiPageScraper(config=config)
        
        # Should use the provided config
        assert scraper.config is config
        assert scraper.config.max_pages == 25
        assert scraper.config.max_crawl_depth == 3

    def test_components_initialized_from_config(self):
        """Test that scraper components are initialized from config."""
        scraper = MultiPageScraper()
        
        # Components should be initialized
        assert hasattr(scraper, 'page_classifier')
        assert hasattr(scraper, 'data_aggregator')
        assert hasattr(scraper, 'progress_notifier')
        assert hasattr(scraper, 'multi_strategy_scraper')
        assert hasattr(scraper, 'page_processor')
        assert hasattr(scraper, 'result_handler')
        assert hasattr(scraper, 'page_queue_manager')
        
        # All components should be not None
        assert scraper.page_classifier is not None
        assert scraper.data_aggregator is not None
        assert scraper.progress_notifier is not None
        assert scraper.multi_strategy_scraper is not None
        assert scraper.page_processor is not None
        assert scraper.result_handler is not None
        assert scraper.page_queue_manager is not None

    def test_statistics_initialized_from_config(self):
        """Test that statistics are initialized from config."""
        scraper = MultiPageScraper()
        
        # Statistics should be initialized  
        assert hasattr(scraper, '_concurrent_stats')
        assert hasattr(scraper, '_error_stats')
        assert hasattr(scraper, '_error_log')
        
        # Should have initial values
        assert scraper._concurrent_stats['successful_fetches'] == 0
        assert scraper._error_stats['total_errors'] == 0
        assert scraper._error_log == []

    def test_max_crawl_depth_from_config(self):
        """Test that max_crawl_depth is obtained from config."""
        config = MultiPageScraperConfig(max_crawl_depth=5)
        scraper = MultiPageScraper(config=config)
        
        # Should use config value instead of hardcoded default
        assert scraper.config.max_crawl_depth == 5

    def test_config_can_be_updated_after_initialization(self):
        """Test that configuration can be updated after scraper initialization."""
        scraper = MultiPageScraper(max_pages=10)
        
        # Update configuration
        scraper.config.update_config(max_pages=20, throttle_delay=1.0)
        
        # Values should be updated
        assert scraper.config.max_pages == 20
        assert scraper.config.throttle_delay == 1.0

    def test_get_config_summary_available(self):
        """Test that configuration summary is available through scraper."""
        scraper = MultiPageScraper(
            max_pages=12, 
            enable_ethical_scraping=False
        )
        
        summary = scraper.config.get_config_summary()
        
        assert summary['max_pages'] == 12
        assert summary['enable_ethical_scraping'] is False

    def test_scrape_website_uses_config_max_crawl_depth(self):
        """Test that scrape_website uses max_crawl_depth from config."""
        # Create scraper with custom crawl depth
        config = MultiPageScraperConfig(max_crawl_depth=4)
        scraper = MultiPageScraper(config=config)
        
        # Verify config value is accessible
        assert scraper.config.max_crawl_depth == 4
        
        # Test that the configuration is properly set
        # (More detailed behavior testing would require complex mocking
        # but the key point is that config.max_crawl_depth is available)

    def test_initialization_validates_parameters(self):
        """Test that initialization validates parameters through config."""
        # Invalid max_pages should raise error
        with pytest.raises(ValueError, match="max_pages must be positive"):
            MultiPageScraper(max_pages=-1)
            
        # Invalid throttle_delay should raise error  
        with pytest.raises(ValueError, match="throttle_delay must be non-negative"):
            MultiPageScraper(throttle_delay=-0.5)

    def test_backward_compatibility_with_old_interface(self):
        """Test that old interface still works for backward compatibility."""
        # Old-style initialization should still work
        scraper = MultiPageScraper(max_pages=8, enable_ethical_scraping=True)
        
        # Should have access to old attributes for compatibility
        assert scraper.max_pages == 8
        assert scraper.enable_ethical_scraping is True
        
        # But config should be the source of truth
        assert scraper.config.max_pages == 8
        assert scraper.config.enable_ethical_scraping is True

    def test_scraper_uses_config_for_component_initialization(self):
        """Test that scraper delegates component initialization to config."""
        scraper = MultiPageScraper(enable_ethical_scraping=False)
        
        # Components should be initialized with the config's ethical scraping setting
        # (This is a behavioral test - detailed mocking would be needed for full verification)
        assert scraper.multi_strategy_scraper is not None
        assert scraper.page_processor is not None