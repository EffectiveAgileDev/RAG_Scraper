"""Unit tests for industry status configuration functionality."""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from src.config.industry_config import IndustryConfig


class TestIndustryStatusConfig:
    """Test industry status configuration methods."""

    @pytest.fixture
    def sample_status_config(self):
        """Sample industry status configuration for testing."""
        return {
            "available_industries": [
                {
                    "name": "Medical",
                    "status": "available",
                    "description": "Service and provider extraction",
                    "completeness": 85,
                },
                {
                    "name": "Restaurant",
                    "status": "coming_soon",
                    "description": "Menu extraction and dining info",
                    "eta": "Q1 2025",
                },
                {
                    "name": "Real Estate",
                    "status": "coming_soon",
                    "description": "Property listings and agent info",
                    "eta": "Q2 2025",
                },
                {
                    "name": "Dental",
                    "status": "beta",
                    "description": "Dental services with limited features",
                    "completeness": 60,
                },
            ],
            "status_definitions": {
                "available": "Fully functional",
                "beta": "Available with limited features",
                "coming_soon": "In development",
                "planned": "Future roadmap item",
            },
        }

    @pytest.fixture
    def industry_config(self, sample_status_config):
        """Create IndustryConfig with mocked status configuration."""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_status_config))
        ):
            with patch("os.path.exists", return_value=True):
                return IndustryConfig()

    def test_get_all_industries_with_status_returns_list(self, industry_config):
        """Test that get_all_industries_with_status returns a list of industries."""
        # This will fail until we implement the method
        industries = industry_config.get_all_industries_with_status()
        assert isinstance(industries, list)
        assert len(industries) > 0

    def test_get_all_industries_with_status_includes_required_fields(
        self, industry_config
    ):
        """Test that each industry has required status fields."""
        industries = industry_config.get_all_industries_with_status()

        for industry in industries:
            assert "name" in industry, "Industry missing name field"
            assert "status" in industry, "Industry missing status field"
            assert "description" in industry, "Industry missing description field"
            assert industry["name"], "Industry name cannot be empty"
            assert industry["status"], "Industry status cannot be empty"

    def test_get_industries_by_status_returns_dict(self, industry_config):
        """Test that get_industries_by_status returns a dictionary grouped by status."""
        # This will fail until we implement the method
        industries_by_status = industry_config.get_industries_by_status()
        assert isinstance(industries_by_status, dict)

    def test_get_industries_by_status_groups_correctly(self, industry_config):
        """Test that industries are correctly grouped by their status."""
        industries_by_status = industry_config.get_industries_by_status()

        # Should have expected status groups
        assert "available" in industries_by_status
        assert "coming_soon" in industries_by_status
        assert "beta" in industries_by_status

        # Check specific industries are in correct groups
        available_names = [i["name"] for i in industries_by_status["available"]]
        coming_soon_names = [i["name"] for i in industries_by_status["coming_soon"]]
        beta_names = [i["name"] for i in industries_by_status["beta"]]

        assert "Medical" in available_names
        assert "Restaurant" in coming_soon_names
        assert "Real Estate" in coming_soon_names
        assert "Dental" in beta_names

    def test_get_industries_by_status_no_cross_contamination(self, industry_config):
        """Test that industries don't appear in multiple status groups."""
        industries_by_status = industry_config.get_industries_by_status()

        all_names = []
        for status_group in industries_by_status.values():
            group_names = [i["name"] for i in status_group]
            all_names.extend(group_names)

        # No duplicate names across groups
        assert len(all_names) == len(
            set(all_names)
        ), "Industries appear in multiple status groups"

    def test_filter_industries_by_status_available(self, industry_config):
        """Test filtering industries by 'available' status."""
        available_industries = industry_config.filter_industries_by_status("available")

        assert isinstance(available_industries, list)
        for industry in available_industries:
            assert industry["status"] == "available"

    def test_filter_industries_by_status_coming_soon(self, industry_config):
        """Test filtering industries by 'coming_soon' status."""
        coming_soon_industries = industry_config.filter_industries_by_status(
            "coming_soon"
        )

        assert isinstance(coming_soon_industries, list)
        for industry in coming_soon_industries:
            assert industry["status"] == "coming_soon"

    def test_filter_industries_by_status_invalid_status(self, industry_config):
        """Test filtering with invalid status returns empty list."""
        invalid_industries = industry_config.filter_industries_by_status(
            "invalid_status"
        )
        assert isinstance(invalid_industries, list)
        assert len(invalid_industries) == 0

    def test_load_status_config_file_not_found(self):
        """Test behavior when status config file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            config = IndustryConfig()
            # Should fall back to default behavior or create default status config
            industries = config.get_all_industries_with_status()
            assert isinstance(industries, list)

    def test_load_status_config_invalid_json(self):
        """Test behavior with invalid JSON in status config file."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("os.path.exists", return_value=True):
                config = IndustryConfig()
                # Should handle gracefully and provide default configuration
                industries = config.get_all_industries_with_status()
                assert isinstance(industries, list)

    def test_get_status_definitions(self, industry_config):
        """Test retrieving status definitions."""
        definitions = industry_config.get_status_definitions()

        assert isinstance(definitions, dict)
        assert "available" in definitions
        assert "coming_soon" in definitions
        assert "beta" in definitions
        assert definitions["available"] == "Fully functional"

    def test_restaurant_is_coming_soon(self, industry_config):
        """Test that Restaurant is specifically marked as coming_soon."""
        coming_soon_industries = industry_config.filter_industries_by_status(
            "coming_soon"
        )
        restaurant_names = [i["name"] for i in coming_soon_industries]
        assert (
            "Restaurant" in restaurant_names
        ), "Restaurant should be marked as coming_soon"

    def test_medical_is_available(self, industry_config):
        """Test that Medical is specifically marked as available."""
        available_industries = industry_config.filter_industries_by_status("available")
        medical_names = [i["name"] for i in available_industries]
        assert "Medical" in medical_names, "Medical should be marked as available"

    def test_get_industry_status_by_name(self, industry_config):
        """Test getting status for a specific industry by name."""
        # This method will fail until implemented
        restaurant_status = industry_config.get_industry_status("Restaurant")
        assert restaurant_status == "coming_soon"

        medical_status = industry_config.get_industry_status("Medical")
        assert medical_status == "available"

    def test_get_industry_status_invalid_name(self, industry_config):
        """Test getting status for non-existent industry."""
        invalid_status = industry_config.get_industry_status("NonExistent")
        assert invalid_status is None or invalid_status == "unknown"
