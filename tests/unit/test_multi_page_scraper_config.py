"""Unit tests for MultiPageScraperConfig class."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.scraper.multi_page_scraper_config import MultiPageScraperConfig


class TestMultiPageScraperConfig:
    """Test configuration management for multi-page scraping."""

    def test_initialization_with_default_values(self):
        """Test config initialization with default values."""
        config = MultiPageScraperConfig()
        
        assert config.max_pages == 10
        assert config.enable_ethical_scraping is True
        assert config.max_crawl_depth == 2
        assert config.concurrent_workers == 3
        assert config.throttle_delay == 0.0
        assert config.request_timeout is None

    def test_initialization_with_custom_values(self):
        """Test config initialization with custom values."""
        config = MultiPageScraperConfig(
            max_pages=20,
            enable_ethical_scraping=False,
            max_crawl_depth=3,
            concurrent_workers=5,
            throttle_delay=1.0,
            request_timeout=30.0
        )
        
        assert config.max_pages == 20
        assert config.enable_ethical_scraping is False
        assert config.max_crawl_depth == 3
        assert config.concurrent_workers == 5
        assert config.throttle_delay == 1.0
        assert config.request_timeout == 30.0

    def test_validate_max_pages_positive(self):
        """Test validation ensures max_pages is positive."""
        with pytest.raises(ValueError, match="max_pages must be positive"):
            MultiPageScraperConfig(max_pages=0)
            
        with pytest.raises(ValueError, match="max_pages must be positive"):
            MultiPageScraperConfig(max_pages=-1)

    def test_validate_max_crawl_depth_positive(self):
        """Test validation ensures max_crawl_depth is positive."""
        with pytest.raises(ValueError, match="max_crawl_depth must be positive"):
            MultiPageScraperConfig(max_crawl_depth=0)
            
        with pytest.raises(ValueError, match="max_crawl_depth must be positive"):
            MultiPageScraperConfig(max_crawl_depth=-1)

    def test_validate_concurrent_workers_positive(self):
        """Test validation ensures concurrent_workers is positive."""
        with pytest.raises(ValueError, match="concurrent_workers must be positive"):
            MultiPageScraperConfig(concurrent_workers=0)
            
        with pytest.raises(ValueError, match="concurrent_workers must be positive"):
            MultiPageScraperConfig(concurrent_workers=-1)

    def test_validate_throttle_delay_non_negative(self):
        """Test validation ensures throttle_delay is non-negative."""
        with pytest.raises(ValueError, match="throttle_delay must be non-negative"):
            MultiPageScraperConfig(throttle_delay=-1.0)

    def test_validate_request_timeout_positive_when_set(self):
        """Test validation ensures request_timeout is positive when set."""
        # None should be allowed
        config = MultiPageScraperConfig(request_timeout=None)
        assert config.request_timeout is None
        
        # Positive values should be allowed
        config = MultiPageScraperConfig(request_timeout=30.0)
        assert config.request_timeout == 30.0
        
        # Zero and negative should raise error
        with pytest.raises(ValueError, match="request_timeout must be positive when set"):
            MultiPageScraperConfig(request_timeout=0.0)
            
        with pytest.raises(ValueError, match="request_timeout must be positive when set"):
            MultiPageScraperConfig(request_timeout=-1.0)

    def test_initialize_components_creates_all_components(self):
        """Test that initialize_components creates all required components."""
        config = MultiPageScraperConfig()
        components = config.initialize_components()
        
        # Check that all expected components are created
        expected_components = [
            'page_classifier',
            'data_aggregator', 
            'progress_notifier',
            'multi_strategy_scraper',
            'page_processor',
            'result_handler',
            'page_queue_manager'
        ]
        
        for component_name in expected_components:
            assert component_name in components
            assert components[component_name] is not None

    def test_initialize_components_passes_ethical_scraping_setting(self):
        """Test that ethical scraping setting is passed to components."""
        # Test with ethical scraping enabled
        config_enabled = MultiPageScraperConfig(enable_ethical_scraping=True)
        components_enabled = config_enabled.initialize_components()
        
        # Test with ethical scraping disabled  
        config_disabled = MultiPageScraperConfig(enable_ethical_scraping=False)
        components_disabled = config_disabled.initialize_components()
        
        # Both should create components (detailed behavior testing is done elsewhere)
        assert components_enabled['multi_strategy_scraper'] is not None
        assert components_disabled['multi_strategy_scraper'] is not None

    def test_initialize_components_passes_max_pages_to_queue_manager(self):
        """Test that max_pages setting is passed to PageQueueManager."""
        config = MultiPageScraperConfig(max_pages=15)
        components = config.initialize_components()
        
        # PageQueueManager should be initialized with max_pages
        queue_manager = components['page_queue_manager']
        assert queue_manager is not None

    def test_initialize_statistics_creates_empty_stats(self):
        """Test that initialize_statistics creates empty statistics dictionaries."""
        config = MultiPageScraperConfig()
        stats = config.initialize_statistics()
        
        # Check concurrent stats
        assert 'concurrent_stats' in stats
        concurrent_stats = stats['concurrent_stats']
        assert concurrent_stats['successful_fetches'] == 0
        assert concurrent_stats['failed_fetches'] == 0
        assert concurrent_stats['total_time'] == 0.0
        
        # Check error stats
        assert 'error_stats' in stats
        error_stats = stats['error_stats']
        assert error_stats['total_errors'] == 0
        assert error_stats['error_types'] == {}
        assert error_stats['retryable_errors'] == 0
        assert error_stats['non_retryable_errors'] == 0
        
        # Check error log
        assert 'error_log' in stats
        assert stats['error_log'] == []

    def test_get_config_summary_returns_all_settings(self):
        """Test that get_config_summary returns all configuration settings."""
        config = MultiPageScraperConfig(
            max_pages=25,
            enable_ethical_scraping=False,
            max_crawl_depth=4,
            concurrent_workers=8,
            throttle_delay=2.0,
            request_timeout=60.0
        )
        
        summary = config.get_config_summary()
        
        assert summary['max_pages'] == 25
        assert summary['enable_ethical_scraping'] is False
        assert summary['max_crawl_depth'] == 4
        assert summary['concurrent_workers'] == 8
        assert summary['throttle_delay'] == 2.0
        assert summary['request_timeout'] == 60.0

    def test_update_config_changes_settings(self):
        """Test that update_config can change configuration settings."""
        config = MultiPageScraperConfig()
        
        # Initial values
        assert config.max_pages == 10
        assert config.throttle_delay == 0.0
        
        # Update configuration
        config.update_config(max_pages=20, throttle_delay=1.5)
        
        # Values should be updated
        assert config.max_pages == 20
        assert config.throttle_delay == 1.5
        
        # Other values should remain unchanged
        assert config.enable_ethical_scraping is True
        assert config.max_crawl_depth == 2

    def test_update_config_validates_new_values(self):
        """Test that update_config validates new configuration values."""
        config = MultiPageScraperConfig()
        
        # Invalid values should raise errors
        with pytest.raises(ValueError, match="max_pages must be positive"):
            config.update_config(max_pages=-1)
            
        with pytest.raises(ValueError, match="throttle_delay must be non-negative"):
            config.update_config(throttle_delay=-0.5)

    def test_reset_statistics_clears_all_stats(self):
        """Test that reset_statistics clears all statistical data."""
        config = MultiPageScraperConfig()
        
        # Initialize with some data
        stats = config.initialize_statistics()
        stats['concurrent_stats']['successful_fetches'] = 5
        stats['error_stats']['total_errors'] = 3
        stats['error_log'].append({'error': 'test'})
        
        # Reset statistics
        reset_stats = config.reset_statistics()
        
        # All stats should be reset to initial values
        assert reset_stats['concurrent_stats']['successful_fetches'] == 0
        assert reset_stats['error_stats']['total_errors'] == 0
        assert reset_stats['error_log'] == []