"""
Unit tests for JSON file generator integration with file generator service.
Following TDD Red-Green-Refactor process for JSON integration.
"""
import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)
from src.scraper.multi_strategy_scraper import RestaurantData


class TestJSONFileGeneratorIntegration:
    """Test JSON integration with file generator service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = FileGeneratorService()
        self.sample_restaurant_data = [
            RestaurantData(
                name="Test Restaurant 1",
                address="123 Main St, Test City, TC 12345",
                phone="(555) 123-4567",
                hours="Mon-Fri: 9AM-10PM",
                price_range="$$",
                cuisine="Italian",
                social_media=["https://facebook.com/testrestaurant1"],
            ),
            RestaurantData(
                name="Test Restaurant 2",
                address="456 Oak Ave, Test City, TC 12346",
                phone="(555) 987-6543",
                hours="Daily: 11AM-11PM",
                price_range="$",
                cuisine="American",
                social_media=["https://twitter.com/testrestaurant2"],
            ),
        ]

    def test_file_generator_service_supports_json_format(self):
        """Test that file generator service supports JSON format."""
        supported_formats = self.service.get_supported_formats()
        assert "json" in supported_formats
        assert "text" in supported_formats
        assert "pdf" in supported_formats

    def test_validate_json_format_in_file_generation_request(self):
        """Test that FileGenerationRequest validates JSON format."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_restaurant_data, file_format="json"
        )

        validation_errors = request.validate()
        assert (
            len(validation_errors) == 0
        )  # Should have no validation errors for JSON format

    def test_generate_json_file_through_service(self):
        """Test generating JSON file through file generator service."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_restaurant_data,
            file_format="json",
            output_directory="/tmp",
        )

        result = self.service.generate_file(request)

        assert result["success"] is True
        assert result["file_format"] == "json"
        assert result["restaurant_count"] == 2
        assert "file_path" in result
        assert result["file_path"].endswith(".json")

        # Verify JSON file was created and is valid
        assert os.path.exists(result["file_path"])

        with open(result["file_path"], "r") as f:
            json_data = json.load(f)

        assert "restaurants" in json_data
        assert len(json_data["restaurants"]) == 2
        assert "metadata" in json_data

        # Cleanup
        os.remove(result["file_path"])

    def test_generate_json_file_with_field_selection(self):
        """Test generating JSON file with field selection through service."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_restaurant_data,
            file_format="json",
            output_directory="/tmp",
            field_selection={
                "core_fields": True,
                "extended_fields": False,
                "additional_fields": False,
                "contact_fields": True,
                "descriptive_fields": False,
            },
        )

        result = self.service.generate_file(request)

        assert result["success"] is True

        # Verify field selection was applied
        with open(result["file_path"], "r") as f:
            json_data = json.load(f)

        restaurant = json_data["restaurants"][0]

        # Should have core fields
        assert restaurant["basic_info"]["name"] == "Test Restaurant 1"
        assert restaurant["basic_info"]["address"] == "123 Main St, Test City, TC 12345"

        # Should not have extended fields (disabled)
        assert restaurant["additional_details"]["cuisine_types"] == []
        assert restaurant["additional_details"]["special_features"] == []

        # Should have contact fields for restaurant 2
        restaurant_2 = json_data["restaurants"][1]
        # Note: restaurant 1 doesn't have email, so it should be None, restaurant 2 should have it

        # Cleanup
        os.remove(result["file_path"])

    def test_json_file_generation_error_handling(self):
        """Test error handling during JSON file generation."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_restaurant_data,
            file_format="json",
            output_directory="/invalid/nonexistent/directory",
        )

        result = self.service.generate_file(request)

        # Should handle invalid directory gracefully
        assert result["success"] is False
        assert "error" in result
        assert "directory" in result["error"].lower()

    def test_json_file_generation_with_empty_data(self):
        """Test JSON file generation with empty restaurant data."""
        request = FileGenerationRequest(
            restaurant_data=[], file_format="json", output_directory="/tmp"
        )

        result = self.service.generate_file(request)

        assert result["success"] is False
        assert "No restaurant data provided" in result["error"]

    def test_json_configuration_persistence_integration(self):
        """Test that JSON format preferences are saved and restored."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_restaurant_data,
            file_format="json",
            output_directory="/tmp",
            save_preferences=True,
            field_selection={
                "core_fields": True,
                "extended_fields": True,
                "additional_fields": False,
                "contact_fields": False,
                "descriptive_fields": True,
            },
        )

        result = self.service.generate_file(request)
        assert result["success"] is True

        # Verify preferences were saved
        config = self.service.get_current_config()
        assert config["output_directory"] == "/tmp"

        # Create new service instance to test persistence
        new_service = FileGeneratorService()
        new_config = new_service.get_current_config()
        assert new_config["output_directory"] == "/tmp"

        # Cleanup
        os.remove(result["file_path"])


class TestJSONFileGeneratorServiceMethods:
    """Test specific methods for JSON file generation in service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = FileGeneratorService()
        self.sample_data = [
            RestaurantData(
                name="Service Test Restaurant",
                address="789 Service St",
                phone="(555) 555-5555",
                hours="Daily: 9AM-9PM",
                cuisine="Test Cuisine",
            )
        ]

    def test_private_generate_json_file_method_exists(self):
        """Test that private _generate_json_file method exists."""
        assert hasattr(self.service, "_generate_json_file")

        # Test method can be called
        request = FileGenerationRequest(
            restaurant_data=self.sample_data, file_format="json"
        )

        result = self.service._generate_json_file(request, "/tmp")

        assert isinstance(result, dict)
        assert "success" in result

        if result["success"]:
            # Cleanup if file was created
            if "file_path" in result and os.path.exists(result["file_path"]):
                os.remove(result["file_path"])

    def test_json_file_generator_uses_correct_filename_pattern(self):
        """Test that JSON files use appropriate filename pattern."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_data,
            file_format="json",
            output_directory="/tmp",
        )

        result = self.service.generate_file(request)

        if result["success"]:
            filename = os.path.basename(result["file_path"])

            # Should follow pattern: WebScrape_{timestamp}.json
            assert filename.startswith("WebScrape_")
            assert filename.endswith(".json")
            assert len(filename) > len("WebScrape_.json")  # Should have timestamp

            # Cleanup
            os.remove(result["file_path"])

    def test_json_error_handling_in_service_method(self):
        """Test error handling in JSON generation service method."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_data, file_format="json"
        )

        # Test with invalid output directory
        result = self.service._generate_json_file(
            request, "/invalid/path/that/does/not/exist"
        )

        assert result["success"] is False
        assert "error" in result
        assert isinstance(result["error"], str)

    def test_json_field_selection_parameter_passing(self):
        """Test that field selection parameters are correctly passed to JSON generator."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_data,
            file_format="json",
            field_selection={
                "core_fields": True,
                "extended_fields": False,
                "additional_fields": False,
                "contact_fields": False,
                "descriptive_fields": False,
            },
        )

        # Mock the JSON generator to verify parameters
        with patch(
            "src.file_generator.file_generator_service.JSONExportGenerator"
        ) as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_json_file.return_value = {
                "success": True,
                "file_path": "/tmp/test.json",
                "restaurant_count": 1,
            }

            result = self.service._generate_json_file(request, "/tmp")

            # Verify JSON generator was called with field selection
            mock_generator.generate_json_file.assert_called_once()
            call_args = mock_generator.generate_json_file.call_args

            # Check that field_selection was passed
            assert "field_selection" in call_args.kwargs
            assert call_args.kwargs["field_selection"] == request.field_selection

            assert result["success"] is True
