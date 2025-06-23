"""
Unit tests for JSON export generator functionality.
Following TDD Red-Green-Refactor process for Sprint 7A JSON export feature.
"""
import pytest
import json
import os
from unittest.mock import Mock, patch
from src.file_generator.json_export_generator import JSONExportGenerator


class TestJSONExportGeneratorCore:
    """Test core JSON export functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = JSONExportGenerator()
        self.sample_restaurant_data = {
            "name": "Test Restaurant",
            "address": "123 Main St, Test City, TC 12345",
            "phone": "(555) 123-4567",
            "hours": "Mon-Fri: 9AM-10PM",
            "website": "https://testrestaurant.com",
            "cuisine_types": ["Italian", "Pizza"],
            "special_features": ["Outdoor Seating", "WiFi"],
            "parking": "Street parking available",
            "email": "info@testrestaurant.com",
            "social_media": ["https://facebook.com/testrestaurant"],
            "delivery_options": ["DoorDash", "Uber Eats"],
            "dietary_accommodations": ["Vegetarian", "Gluten-free options"],
            "ambiance": "Casual dining, family-friendly",
        }

    def test_json_generator_initialization(self):
        """Test that JSON generator initializes correctly."""
        generator = JSONExportGenerator()
        assert generator is not None
        assert hasattr(generator, "generate_json_file")
        assert hasattr(generator, "format_restaurant_data")

    def test_format_single_restaurant_data_to_json_structure(self):
        """Test formatting single restaurant data into JSON structure."""
        formatted_data = self.generator.format_restaurant_data(
            self.sample_restaurant_data
        )

        # Should return properly structured data
        assert isinstance(formatted_data, dict)
        assert "basic_info" in formatted_data
        assert "additional_details" in formatted_data
        assert "contact_info" in formatted_data
        assert "characteristics" in formatted_data

        # Verify basic_info contains core fields
        basic_info = formatted_data["basic_info"]
        assert basic_info["name"] == "Test Restaurant"
        assert basic_info["address"] == "123 Main St, Test City, TC 12345"
        assert basic_info["phone"] == "(555) 123-4567"
        assert basic_info["hours"] == "Mon-Fri: 9AM-10PM"
        assert basic_info["website"] == "https://testrestaurant.com"

    def test_format_restaurant_data_with_missing_fields(self):
        """Test formatting restaurant data when some fields are missing."""
        incomplete_data = {
            "name": "Incomplete Restaurant",
            "address": "456 Incomplete Ave",
            "phone": "(555) 999-0000"
            # Missing hours, website, and all optional fields
        }

        formatted_data = self.generator.format_restaurant_data(incomplete_data)

        # Should handle missing fields gracefully
        assert formatted_data["basic_info"]["name"] == "Incomplete Restaurant"
        assert formatted_data["basic_info"]["hours"] is None
        assert formatted_data["basic_info"]["website"] is None
        assert formatted_data["additional_details"]["cuisine_types"] == []
        assert formatted_data["contact_info"]["email"] is None

    def test_generate_json_file_for_single_restaurant(self):
        """Test generating JSON file for single restaurant."""
        output_path = "/tmp/test_single_restaurant.json"
        restaurant_list = [self.sample_restaurant_data]

        result = self.generator.generate_json_file(restaurant_list, output_path)

        # Should return success status
        assert result["success"] is True
        assert result["file_path"] == output_path
        assert result["restaurant_count"] == 1

        # Should create valid JSON file
        assert os.path.exists(output_path)

        with open(output_path, "r") as f:
            json_data = json.load(f)

        assert "restaurants" in json_data
        assert len(json_data["restaurants"]) == 1
        assert json_data["restaurants"][0]["basic_info"]["name"] == "Test Restaurant"

        # Cleanup
        os.remove(output_path)

    def test_generate_json_file_for_multiple_restaurants(self):
        """Test generating JSON file for multiple restaurants."""
        output_path = "/tmp/test_multiple_restaurants.json"

        restaurant_2 = {
            "name": "Second Restaurant",
            "address": "789 Second St",
            "phone": "(555) 987-6543",
            "hours": "Daily: 11AM-11PM",
            "website": "https://secondrestaurant.com",
        }

        restaurant_list = [self.sample_restaurant_data, restaurant_2]

        result = self.generator.generate_json_file(restaurant_list, output_path)

        assert result["success"] is True
        assert result["restaurant_count"] == 2

        with open(output_path, "r") as f:
            json_data = json.load(f)

        assert len(json_data["restaurants"]) == 2
        assert json_data["restaurants"][0]["basic_info"]["name"] == "Test Restaurant"
        assert json_data["restaurants"][1]["basic_info"]["name"] == "Second Restaurant"

        # Cleanup
        os.remove(output_path)

    def test_json_file_structure_validation(self):
        """Test that generated JSON follows expected schema structure."""
        output_path = "/tmp/test_json_structure.json"
        restaurant_list = [self.sample_restaurant_data]

        self.generator.generate_json_file(restaurant_list, output_path)

        with open(output_path, "r") as f:
            json_data = json.load(f)

        # Validate top-level structure
        assert "metadata" in json_data
        assert "restaurants" in json_data

        # Validate metadata
        metadata = json_data["metadata"]
        assert "generation_timestamp" in metadata
        assert "restaurant_count" in metadata
        assert "format_version" in metadata

        # Validate restaurant structure
        restaurant = json_data["restaurants"][0]
        assert "basic_info" in restaurant
        assert "additional_details" in restaurant
        assert "contact_info" in restaurant
        assert "characteristics" in restaurant

        # Cleanup
        os.remove(output_path)

    def test_json_export_error_handling_invalid_path(self):
        """Test error handling when invalid output path is provided."""
        invalid_path = "/invalid/nonexistent/directory/output.json"
        restaurant_list = [self.sample_restaurant_data]

        result = self.generator.generate_json_file(restaurant_list, invalid_path)

        assert result["success"] is False
        assert "error" in result
        assert (
            "Invalid output path" in result["error"]
            or "Permission denied" in result["error"]
        )

    def test_json_export_empty_restaurant_list(self):
        """Test handling of empty restaurant list."""
        output_path = "/tmp/test_empty_restaurants.json"
        empty_list = []

        result = self.generator.generate_json_file(empty_list, output_path)

        assert result["success"] is True
        assert result["restaurant_count"] == 0

        with open(output_path, "r") as f:
            json_data = json.load(f)

        assert json_data["restaurants"] == []
        assert json_data["metadata"]["restaurant_count"] == 0

        # Cleanup
        os.remove(output_path)


class TestJSONExportGeneratorFieldSelection:
    """Test field selection functionality for JSON export."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = JSONExportGenerator()
        self.full_restaurant_data = {
            "name": "Full Data Restaurant",
            "address": "123 Full St",
            "phone": "(555) 111-2222",
            "hours": "Daily: 8AM-9PM",
            "website": "https://fulldata.com",
            "cuisine_types": ["American", "Burgers"],
            "special_features": ["Drive-through", "Kids menu"],
            "parking": "Free parking lot",
            "reservations": "Accepts reservations",
            "menu_items": ["Burger Special", "Fish and Chips"],
            "pricing": "$ (Affordable)",
            "email": "contact@fulldata.com",
            "social_media": ["https://twitter.com/fulldata"],
            "delivery_options": ["GrubHub"],
            "dietary_accommodations": ["Vegan options"],
            "ambiance": "Casual, sports bar atmosphere",
        }

    def test_generate_json_with_core_fields_only(self):
        """Test JSON generation with only core fields selected."""
        output_path = "/tmp/test_core_fields_only.json"
        restaurant_list = [self.full_restaurant_data]

        field_selection = {
            "core_fields": True,
            "extended_fields": False,
            "additional_fields": False,
            "contact_fields": False,
            "descriptive_fields": False,
        }

        result = self.generator.generate_json_file(
            restaurant_list, output_path, field_selection=field_selection
        )

        assert result["success"] is True

        with open(output_path, "r") as f:
            json_data = json.load(f)

        restaurant = json_data["restaurants"][0]

        # Should contain core fields
        assert restaurant["basic_info"]["name"] == "Full Data Restaurant"
        assert restaurant["basic_info"]["address"] == "123 Full St"

        # Should not contain non-core fields
        assert restaurant["additional_details"]["cuisine_types"] == []
        assert restaurant["contact_info"]["email"] is None
        assert restaurant["characteristics"]["dietary_accommodations"] == []

        # Cleanup
        os.remove(output_path)

    def test_generate_json_with_custom_field_selection(self):
        """Test JSON generation with custom field selection."""
        output_path = "/tmp/test_custom_fields.json"
        restaurant_list = [self.full_restaurant_data]

        field_selection = {
            "core_fields": True,
            "extended_fields": True,
            "additional_fields": False,
            "contact_fields": True,
            "descriptive_fields": False,
        }

        result = self.generator.generate_json_file(
            restaurant_list, output_path, field_selection=field_selection
        )

        assert result["success"] is True

        with open(output_path, "r") as f:
            json_data = json.load(f)

        restaurant = json_data["restaurants"][0]

        # Should contain selected fields
        assert restaurant["basic_info"]["name"] == "Full Data Restaurant"
        assert restaurant["additional_details"]["cuisine_types"] == [
            "American",
            "Burgers",
        ]
        assert restaurant["contact_info"]["email"] == "contact@fulldata.com"

        # Should not contain non-selected fields
        assert restaurant["additional_details"]["reservations"] is None
        assert restaurant["characteristics"]["ambiance"] is None

        # Cleanup
        os.remove(output_path)

    def test_validate_field_selection_configuration(self):
        """Test validation of field selection configuration."""
        # Valid configuration should pass
        valid_config = {
            "core_fields": True,
            "extended_fields": False,
            "additional_fields": True,
            "contact_fields": False,
            "descriptive_fields": True,
        }

        is_valid = self.generator.validate_field_selection(valid_config)
        assert is_valid is True

        # Invalid configuration should fail
        invalid_config = {
            "core_fields": True,
            "invalid_field": True,  # This field doesn't exist
        }

        is_valid = self.generator.validate_field_selection(invalid_config)
        assert is_valid is False
