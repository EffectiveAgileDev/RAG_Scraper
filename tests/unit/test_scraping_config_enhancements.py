"""Unit tests for enhanced scraping configuration with multi-page support."""
import json
import os
import tempfile
from typing import Dict, Any

import pytest

from src.config.scraping_config import ScrapingConfig


class TestScrapingConfigEnhancements:
    """Test enhanced configuration features for multi-page scraping."""

    def test_create_config_with_multi_page_properties(self):
        """Test creating configuration with multi-page properties."""
        config = ScrapingConfig(
            urls=["https://example.com"],
            max_pages_per_site=25,
            page_discovery_enabled=True,
            follow_pagination=True,
            max_crawl_depth=3
        )
        
        assert config.max_pages_per_site == 25
        assert config.page_discovery_enabled is True
        assert config.follow_pagination is True
        assert config.max_crawl_depth == 3

    def test_link_pattern_configuration(self):
        """Test link pattern configuration structure."""
        link_patterns = {
            "include": ["/restaurants/.*", "/menu/.*"],
            "exclude": [".*(login|signup).*", ".*\\.(jpg|png|gif|pdf)$"]
        }
        
        config = ScrapingConfig(
            urls=["https://example.com"],
            link_patterns=link_patterns
        )
        
        assert hasattr(config, 'link_patterns')
        assert config.link_patterns["include"] == ["/restaurants/.*", "/menu/.*"]
        assert config.link_patterns["exclude"] == [".*(login|signup).*", ".*\\.(jpg|png|gif|pdf)$"]

    def test_crawl_settings_configuration(self):
        """Test crawl settings configuration."""
        crawl_settings = {
            "max_crawl_depth": 3,
            "follow_pagination": True,
            "respect_robots_txt": True
        }
        
        config = ScrapingConfig(
            urls=["https://example.com"],
            crawl_settings=crawl_settings
        )
        
        assert hasattr(config, 'crawl_settings')
        assert config.crawl_settings["max_crawl_depth"] == 3
        assert config.crawl_settings["follow_pagination"] is True
        assert config.crawl_settings["respect_robots_txt"] is True

    def test_per_domain_settings(self):
        """Test per-domain configuration settings."""
        per_domain_settings = {
            "restaurant1.com": {
                "rate_limit": 1.0,
                "max_pages": 50,
                "user_agent": "RAG_Scraper/1.0 Polite"
            },
            "restaurant2.com": {
                "rate_limit": 3.0,
                "max_pages": 20,
                "user_agent": "RAG_Scraper/1.0 Fast"
            },
            "default": {
                "rate_limit": 2.0,
                "max_pages": 10,
                "user_agent": "RAG_Scraper/1.0"
            }
        }
        
        config = ScrapingConfig(
            urls=["https://example.com"],
            per_domain_settings=per_domain_settings
        )
        
        assert hasattr(config, 'per_domain_settings')
        assert config.per_domain_settings["restaurant1.com"]["rate_limit"] == 1.0
        assert config.per_domain_settings["restaurant1.com"]["max_pages"] == 50
        assert config.per_domain_settings["default"]["rate_limit"] == 2.0

    def test_configuration_validation_positive_values(self):
        """Test validation ensures positive values for certain parameters."""
        # max_pages_per_site must be positive
        with pytest.raises(ValueError, match="must be positive"):
            ScrapingConfig(
                urls=["https://example.com"],
                max_pages_per_site=-5
            )
        
        # max_crawl_depth must be at least 1
        with pytest.raises(ValueError, match="must be at least 1"):
            ScrapingConfig(
                urls=["https://example.com"],
                max_crawl_depth=0
            )
        
        # page_timeout must be positive
        with pytest.raises(ValueError, match="must be positive"):
            ScrapingConfig(
                urls=["https://example.com"],
                page_timeout=-30
            )

    def test_configuration_validation_link_patterns(self):
        """Test validation of link pattern configuration."""
        # Invalid regex patterns should raise error
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            ScrapingConfig(
                urls=["https://example.com"],
                link_patterns={
                    "include": ["[invalid regex"],  # Missing closing bracket
                    "exclude": []
                }
            )

    def test_configuration_validation_per_domain(self):
        """Test validation of per-domain settings."""
        # Invalid rate limit should raise error
        with pytest.raises(ValueError, match="Rate limit must be positive"):
            ScrapingConfig(
                urls=["https://example.com"],
                per_domain_settings={
                    "example.com": {
                        "rate_limit": -1.0,
                        "max_pages": 10
                    }
                }
            )

    def test_default_multi_page_configuration_values(self):
        """Test default values for multi-page configuration."""
        config = ScrapingConfig(urls=["https://example.com"])
        
        # Check defaults
        assert config.max_pages_per_site == 10
        assert config.page_discovery_enabled is True
        assert config.max_crawl_depth == 2
        assert config.follow_pagination is False
        assert config.respect_robots_txt is True
        assert config.concurrent_requests == 3

    def test_configuration_to_dict_with_new_properties(self):
        """Test converting enhanced configuration to dictionary."""
        config = ScrapingConfig(
            urls=["https://example.com"],
            max_crawl_depth=3,
            follow_pagination=True,
            link_patterns={
                "include": ["/restaurants/.*"],
                "exclude": [".*(login|signup).*"]
            }
        )
        
        config_dict = config.to_dict()
        
        assert "max_crawl_depth" in config_dict
        assert config_dict["max_crawl_depth"] == 3
        assert "follow_pagination" in config_dict
        assert config_dict["follow_pagination"] is True
        assert "link_patterns" in config_dict
        assert config_dict["link_patterns"]["include"] == ["/restaurants/.*"]

    def test_configuration_from_dict_with_new_properties(self):
        """Test creating configuration from dictionary with new properties."""
        data = {
            "urls": ["https://example.com"],
            "max_pages_per_site": 30,
            "max_crawl_depth": 4,
            "follow_pagination": True,
            "link_patterns": {
                "include": ["/menu/.*"],
                "exclude": [".*\\.pdf$"]
            }
        }
        
        config = ScrapingConfig.from_dict(data)
        
        assert config.max_pages_per_site == 30
        assert config.max_crawl_depth == 4
        assert config.follow_pagination is True
        assert config.link_patterns["include"] == ["/menu/.*"]

    def test_save_and_load_enhanced_configuration(self):
        """Test saving and loading enhanced configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Create config with new properties
            original_config = ScrapingConfig(
                urls=["https://example.com"],
                max_crawl_depth=5,
                follow_pagination=True,
                link_patterns={
                    "include": ["/reviews/.*"],
                    "exclude": [".*\\.jpg$"]
                },
                per_domain_settings={
                    "example.com": {
                        "rate_limit": 1.5,
                        "max_pages": 25
                    }
                }
            )
            
            # Save to file
            original_config.save_to_file(temp_file)
            
            # Load from file
            loaded_config = ScrapingConfig.load_from_file(temp_file)
            
            # Verify loaded values
            assert loaded_config.max_crawl_depth == 5
            assert loaded_config.follow_pagination is True
            assert loaded_config.link_patterns["include"] == ["/reviews/.*"]
            assert loaded_config.per_domain_settings["example.com"]["rate_limit"] == 1.5
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_max_total_pages_configuration(self):
        """Test max total pages configuration."""
        config = ScrapingConfig(
            urls=["https://example1.com", "https://example2.com"],
            max_total_pages=100
        )
        
        assert config.max_total_pages == 100

    def test_should_follow_link_method(self):
        """Test method to check if a link should be followed."""
        config = ScrapingConfig(
            urls=["https://example.com"],
            link_patterns={
                "include": ["/restaurants/.*", "/menu/.*"],
                "exclude": [".*(login|signup).*", ".*\\.(jpg|png|gif|pdf)$"]
            }
        )
        
        # Should follow matching include patterns
        assert config.should_follow_link("/restaurants/italian") is True
        assert config.should_follow_link("/menu/lunch") is True
        
        # Should not follow excluded patterns
        assert config.should_follow_link("/user/login") is False
        assert config.should_follow_link("/images/food.jpg") is False
        
        # Should not follow non-matching patterns
        assert config.should_follow_link("/about-us") is False

    def test_get_domain_settings_method(self):
        """Test method to get settings for a specific domain."""
        config = ScrapingConfig(
            urls=["https://example.com"],
            per_domain_settings={
                "restaurant1.com": {
                    "rate_limit": 1.0,
                    "max_pages": 50
                },
                "default": {
                    "rate_limit": 2.0,
                    "max_pages": 10
                }
            }
        )
        
        # Get specific domain settings
        settings = config.get_domain_settings("restaurant1.com")
        assert settings["rate_limit"] == 1.0
        assert settings["max_pages"] == 50
        
        # Get default settings for unknown domain
        default_settings = config.get_domain_settings("unknown.com")
        assert default_settings["rate_limit"] == 2.0
        assert default_settings["max_pages"] == 10

    def test_crawl_timeout_configuration(self):
        """Test crawl timeout configuration."""
        config = ScrapingConfig(
            urls=["https://example.com"],
            page_timeout=45,
            crawl_timeout=600  # 10 minutes for entire crawl
        )
        
        assert config.page_timeout == 45
        assert config.crawl_timeout == 600

    def test_concurrent_requests_configuration(self):
        """Test concurrent requests configuration."""
        config = ScrapingConfig(
            urls=["https://example.com"],
            concurrent_requests=5
        )
        
        assert config.concurrent_requests == 5
        
        # Test validation
        with pytest.raises(ValueError, match="must be at least 1"):
            ScrapingConfig(
                urls=["https://example.com"],
                concurrent_requests=0
            )

    def test_respect_robots_txt_configuration(self):
        """Test robots.txt respect configuration."""
        config = ScrapingConfig(
            urls=["https://example.com"],
            respect_robots_txt=False
        )
        
        assert config.respect_robots_txt is False
        
        # Default should be True
        default_config = ScrapingConfig(urls=["https://example.com"])
        assert default_config.respect_robots_txt is True