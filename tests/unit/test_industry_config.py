"""Unit tests for industry configuration module."""
import pytest
from unittest.mock import Mock, patch, mock_open
import json


class TestIndustryConfig:
    """Test cases for IndustryConfig class."""

    def test_init_loads_default_industries(self):
        """Test that IndustryConfig initializes with all 12 default industries."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        assert len(config.industries) == 12
        assert "Restaurant" in config.industries
        assert "Real Estate" in config.industries
        assert "Medical" in config.industries
        assert "Dental" in config.industries
        assert "Furniture" in config.industries
        assert "Hardware / Home Improvement" in config.industries
        assert "Vehicle Fuel" in config.industries
        assert "Vehicle Sales" in config.industries
        assert "Vehicle Repair / Towing" in config.industries
        assert "Ride Services" in config.industries
        assert "Shop at Home" in config.industries
        assert "Fast Food" in config.industries

    def test_get_industry_list_returns_sorted_list(self):
        """Test that get_industry_list returns a sorted list of industries."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        industries = config.get_industry_list()
        
        assert isinstance(industries, list)
        assert len(industries) == 12
        assert industries == sorted(industries)

    def test_get_industry_config_returns_config_for_valid_industry(self):
        """Test that get_industry_config returns configuration for a valid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        restaurant_config = config.get_industry_config("Restaurant")
        
        assert restaurant_config is not None
        assert "name" in restaurant_config
        assert restaurant_config["name"] == "Restaurant"
        assert "help_text" in restaurant_config
        assert "extractor_class" in restaurant_config
        assert "categories" in restaurant_config

    def test_get_industry_config_returns_none_for_invalid_industry(self):
        """Test that get_industry_config returns None for an invalid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        invalid_config = config.get_industry_config("InvalidIndustry")
        
        assert invalid_config is None

    def test_get_help_text_returns_text_for_valid_industry(self):
        """Test that get_help_text returns help text for a valid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        
        help_text = config.get_help_text("Restaurant")
        assert help_text == "Extracts menu items, hours, location, ambiance, and dining options"
        
        help_text = config.get_help_text("Real Estate")
        assert help_text == "Extracts property listings, agent info, prices, and features"
        
        help_text = config.get_help_text("Medical")
        assert help_text == "Extracts services, insurance info, doctor profiles, and hours"

    def test_get_help_text_returns_empty_for_invalid_industry(self):
        """Test that get_help_text returns empty string for an invalid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        help_text = config.get_help_text("InvalidIndustry")
        
        assert help_text == ""

    def test_validate_industry_returns_true_for_valid_industry(self):
        """Test that validate_industry returns True for a valid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        
        assert config.validate_industry("Restaurant") is True
        assert config.validate_industry("Real Estate") is True
        assert config.validate_industry("Medical") is True

    def test_validate_industry_returns_false_for_invalid_industry(self):
        """Test that validate_industry returns False for an invalid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        
        assert config.validate_industry("InvalidIndustry") is False
        assert config.validate_industry("") is False
        assert config.validate_industry(None) is False

    def test_get_extractor_class_returns_class_name_for_industry(self):
        """Test that get_extractor_class returns the correct extractor class name."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        
        assert config.get_extractor_class("Restaurant") == "RestaurantScraper"
        assert config.get_extractor_class("Real Estate") == "RealEstateScraper"
        assert config.get_extractor_class("Medical") == "MedicalScraper"

    def test_get_extractor_class_returns_none_for_invalid_industry(self):
        """Test that get_extractor_class returns None for an invalid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        
        assert config.get_extractor_class("InvalidIndustry") is None
        assert config.get_extractor_class("") is None

    def test_load_custom_config_from_file(self):
        """Test loading custom industry configuration from a JSON file."""
        from src.config.industry_config import IndustryConfig
        
        custom_config = {
            "Restaurant": {
                "help_text": "Custom restaurant help text",
                "categories": ["custom_category"]
            }
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(custom_config))):
            config = IndustryConfig(config_file="custom_config.json")
            
            # Should still have all 12 industries
            assert len(config.industries) == 12
            
            # Restaurant should have custom help text
            restaurant_config = config.get_industry_config("Restaurant")
            assert restaurant_config["help_text"] == "Custom restaurant help text"
            assert "custom_category" in restaurant_config["categories"]

    def test_get_industry_categories_returns_categories_list(self):
        """Test that get_industry_categories returns the categories for an industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        
        categories = config.get_industry_categories("Restaurant")
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "menu" in categories
        assert "hours" in categories
        assert "location" in categories

    def test_get_industry_categories_returns_empty_for_invalid_industry(self):
        """Test that get_industry_categories returns empty list for invalid industry."""
        from src.config.industry_config import IndustryConfig
        
        config = IndustryConfig()
        
        categories = config.get_industry_categories("InvalidIndustry")
        assert categories == []