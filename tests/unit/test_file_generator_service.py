"""Unit tests for file generator service integration."""
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)
from src.file_generator.text_file_generator import TextFileConfig


class TestFileGeneratorService:
    """Test suite for FileGeneratorService."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def file_service(self, temp_config_dir):
        """Create FileGeneratorService instance."""
        config_file = os.path.join(temp_config_dir, "file_service_config.json")
        return FileGeneratorService(config_file)

    @pytest.fixture
    def sample_restaurants(self):
        """Create sample restaurant data."""
        return [
            RestaurantData(
                name="Tony's Italian Restaurant",
                address="1234 Commercial Street, Salem, OR 97301",
                phone="(503) 555-0123",
                price_range="$18-$32",
                hours="Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm",
                menu_items={
                    "appetizers": ["Fresh bruschetta", "calamari rings"],
                    "entrees": ["Homemade pasta", "wood-fired pizza"],
                    "desserts": ["Tiramisu", "cannoli"],
                },
                cuisine="Italian",
                sources=["json-ld", "heuristic"],
            ),
            RestaurantData(
                name="Blue Moon Diner",
                address="5678 State Street",
                phone="(503) 555-4567",
                cuisine="American",
                sources=["heuristic"],
            ),
        ]

    def test_generate_text_file_with_default_config(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test generating text file with default configuration."""
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=temp_config_dir,
            file_format="text",
        )

        result = file_service.generate_file(request)

        # Verify result
        assert result["success"] is True
        assert "file_path" in result
        assert result["file_path"].endswith(".txt")
        assert os.path.exists(result["file_path"])

        # Verify content
        with open(result["file_path"], "r", encoding="utf-8") as f:
            content = f.read()

        assert "Tony's Italian Restaurant" in content
        assert "Blue Moon Diner" in content
        assert content.count("\n\n\n") == 1  # One separator between restaurants

    def test_generate_text_file_with_custom_directory(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test generating text file with custom output directory."""
        custom_dir = os.path.join(temp_config_dir, "custom_output")
        os.makedirs(custom_dir, exist_ok=True)

        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=custom_dir,
            file_format="text",
        )

        result = file_service.generate_file(request)

        # Verify file was created in custom directory
        assert result["success"] is True
        assert result["file_path"].startswith(custom_dir)
        assert os.path.exists(result["file_path"])

    def test_directory_permission_validation_success(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test successful directory permission validation."""
        # Writable directory should succeed
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=temp_config_dir,
            file_format="text",
        )

        result = file_service.generate_file(request)
        assert result["success"] is True

    def test_directory_permission_validation_failure(
        self, file_service, sample_restaurants
    ):
        """Test directory permission validation failure."""
        # Try to write to read-only directory
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory="/root",
            file_format="text",
        )

        result = file_service.generate_file(request)

        assert result["success"] is False
        assert "error" in result
        assert "permission" in result["error"].lower()

    def test_directory_creation_when_needed(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test automatic directory creation when needed."""
        nested_dir = os.path.join(temp_config_dir, "level1", "level2", "output")

        # Directory doesn't exist yet
        assert not os.path.exists(nested_dir)

        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=nested_dir,
            file_format="text",
        )

        result = file_service.generate_file(request)

        # Debug output
        if not result["success"]:
            print(f"Error: {result['error']}")

        # Verify directory was created and file generated
        assert result["success"] is True
        assert os.path.exists(nested_dir)
        assert os.path.exists(result["file_path"])

    def test_persistent_directory_configuration(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test that directory preferences are saved and restored."""
        custom_dir = os.path.join(temp_config_dir, "persistent_output")
        os.makedirs(custom_dir, exist_ok=True)

        # First request with custom directory
        request1 = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=custom_dir,
            file_format="text",
            save_preferences=True,
        )

        result1 = file_service.generate_file(request1)
        assert result1["success"] is True

        # Get current config (should show custom directory)
        current_config = file_service.get_current_config()
        assert current_config["output_directory"] == custom_dir

        # Second request without specifying directory (should use saved preference)
        request2 = FileGenerationRequest(
            restaurant_data=sample_restaurants, file_format="text"
        )

        result2 = file_service.generate_file(request2)
        assert result2["success"] is True
        assert result2["file_path"].startswith(custom_dir)

    def test_file_overwrite_handling(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test file overwrite handling."""
        from datetime import datetime

        with patch("src.file_generator.text_file_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30)

            # Generate first file
            request1 = FileGenerationRequest(
                restaurant_data=sample_restaurants,
                output_directory=temp_config_dir,
                file_format="text",
                allow_overwrite=True,
            )

            result1 = file_service.generate_file(request1)
            assert result1["success"] is True
            first_file = result1["file_path"]

            # Generate second file with same timestamp (should overwrite)
            result2 = file_service.generate_file(request1)
            assert result2["success"] is True
            assert result2["file_path"] == first_file

    def test_file_overwrite_protection(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test file overwrite protection."""
        # Create existing file
        existing_file = os.path.join(temp_config_dir, "WebScrape_20240315-1430.txt")
        with open(existing_file, "w") as f:
            f.write("Existing content")

        from datetime import datetime

        with patch("src.file_generator.text_file_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30)

            request = FileGenerationRequest(
                restaurant_data=sample_restaurants,
                output_directory=temp_config_dir,
                file_format="text",
                allow_overwrite=False,
            )

            result = file_service.generate_file(request)

            assert result["success"] is False
            assert "exists" in result["error"].lower()

    def test_empty_restaurant_data_handling(self, file_service, temp_config_dir):
        """Test handling of empty restaurant data."""
        request = FileGenerationRequest(
            restaurant_data=[], output_directory=temp_config_dir, file_format="text"
        )

        result = file_service.generate_file(request)

        assert result["success"] is False
        assert "restaurant data" in result["error"].lower()

    def test_invalid_file_format_handling(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test handling of invalid file format."""
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=temp_config_dir,
            file_format="invalid_format",
        )

        result = file_service.generate_file(request)

        assert result["success"] is False
        assert "format" in result["error"].lower()

    def test_get_supported_formats(self, file_service):
        """Test getting supported file formats."""
        formats = file_service.get_supported_formats()

        assert isinstance(formats, list)
        assert "text" in formats
        # Future formats would be added here (pdf, etc.)

    def test_get_current_config(self, file_service, temp_config_dir):
        """Test getting current configuration."""
        config = file_service.get_current_config()

        assert isinstance(config, dict)
        assert "output_directory" in config
        assert "allow_overwrite" in config
        assert "encoding" in config
        assert "filename_pattern" in config

    def test_update_config(self, file_service, temp_config_dir):
        """Test updating configuration."""
        custom_dir = os.path.join(temp_config_dir, "updated_output")
        os.makedirs(custom_dir, exist_ok=True)

        new_config = {
            "output_directory": custom_dir,
            "allow_overwrite": False,
            "encoding": "utf-8",
            "filename_pattern": "Custom_{timestamp}.txt",
        }

        result = file_service.update_config(new_config)

        assert result["success"] is True

        # Verify config was updated
        current_config = file_service.get_current_config()
        assert current_config["output_directory"] == custom_dir
        assert current_config["allow_overwrite"] is False
        assert current_config["filename_pattern"] == "Custom_{timestamp}.txt"

    def test_validate_directory_permissions(self, file_service, temp_config_dir):
        """Test directory permission validation method."""
        # Valid directory
        result = file_service.validate_directory_permissions(temp_config_dir)
        assert result["valid"] is True

        # Invalid directory
        result = file_service.validate_directory_permissions("/root")
        assert result["valid"] is False
        assert "error" in result


class TestFileGenerationRequest:
    """Test suite for FileGenerationRequest data class."""

    def test_request_creation_with_required_fields(self):
        """Test creating request with required fields only."""
        restaurants = [RestaurantData(name="Test", sources=["heuristic"])]

        request = FileGenerationRequest(restaurant_data=restaurants, file_format="text")

        assert request.restaurant_data == restaurants
        assert request.file_format == "text"
        assert request.output_directory is None  # Should use default
        assert request.allow_overwrite is True  # Default
        assert request.save_preferences is False  # Default

    def test_request_creation_with_all_fields(self, tmp_path):
        """Test creating request with all fields specified."""
        restaurants = [RestaurantData(name="Test", sources=["heuristic"])]

        request = FileGenerationRequest(
            restaurant_data=restaurants,
            output_directory=str(tmp_path),
            file_format="text",
            allow_overwrite=False,
            save_preferences=True,
        )

        assert request.restaurant_data == restaurants
        assert request.output_directory == str(tmp_path)
        assert request.file_format == "text"
        assert request.allow_overwrite is False
        assert request.save_preferences is True

    def test_request_validation(self):
        """Test request validation."""
        # Valid request
        restaurants = [RestaurantData(name="Test", sources=["heuristic"])]
        request = FileGenerationRequest(restaurant_data=restaurants, file_format="text")

        errors = request.validate()
        assert len(errors) == 0

        # Invalid request - empty data
        invalid_request = FileGenerationRequest(restaurant_data=[], file_format="text")

        errors = invalid_request.validate()
        assert len(errors) > 0
        assert any("restaurant data" in error for error in errors)

        # Invalid request - unsupported format
        invalid_format_request = FileGenerationRequest(
            restaurant_data=restaurants, file_format="unsupported"
        )

        errors = invalid_format_request.validate()
        assert len(errors) > 0
        assert any("format" in error for error in errors)


class TestFileServiceIntegration:
    """Integration tests for file service with real file operations."""

    def test_full_workflow_with_persistence(self):
        """Test complete workflow with configuration persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "service_config.json")
            output_dir = os.path.join(temp_dir, "output")

            # Session 1: Generate file and save preferences
            service1 = FileGeneratorService(config_file)

            restaurants = [
                RestaurantData(
                    name="Restaurant 1", phone="555-0001", sources=["heuristic"]
                ),
                RestaurantData(
                    name="Restaurant 2", phone="555-0002", sources=["heuristic"]
                ),
            ]

            request = FileGenerationRequest(
                restaurant_data=restaurants,
                output_directory=output_dir,
                file_format="text",
                save_preferences=True,
            )

            result1 = service1.generate_file(request)
            assert result1["success"] is True
            assert os.path.exists(result1["file_path"])

            # Session 2: New service instance should load saved preferences
            service2 = FileGeneratorService(config_file)
            config = service2.get_current_config()
            assert config["output_directory"] == output_dir

            # Generate another file (should use saved directory)
            request2 = FileGenerationRequest(
                restaurant_data=restaurants, file_format="text"
            )

            result2 = service2.generate_file(request2)
            assert result2["success"] is True
            assert result2["file_path"].startswith(output_dir)
