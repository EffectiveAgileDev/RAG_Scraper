"""Unit tests for PDF file generator service integration."""
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)
from src.file_generator.pdf_generator import PDFConfig


class TestFileGeneratorServicePDFIntegration:
    """Test suite for FileGeneratorService PDF integration."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def file_service(self, temp_config_dir):
        """Create FileGeneratorService instance."""
        config_file = os.path.join(temp_config_dir, "pdf_service_config.json")
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
                confidence="high",
                sources=["json-ld", "heuristic"],
            ),
            RestaurantData(
                name="Blue Moon Diner",
                address="5678 State Street, Salem, OR 97302",
                phone="(503) 555-4567",
                cuisine="American",
                confidence="medium",
                sources=["heuristic"],
            ),
        ]

    def test_generate_pdf_file_with_default_config(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test generating PDF file with default configuration."""
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=temp_config_dir,
            file_format="pdf",
        )

        result = file_service.generate_file(request)

        # Verify result
        assert result["success"] is True
        assert "file_path" in result
        assert result["file_path"].endswith(".pdf")
        assert os.path.exists(result["file_path"])
        assert result["file_format"] == "pdf"
        assert result["restaurant_count"] == 2

        # Verify PDF file has content
        file_size = os.path.getsize(result["file_path"])
        assert file_size > 0

    def test_generate_pdf_file_with_custom_directory(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test generating PDF file with custom output directory."""
        custom_dir = os.path.join(temp_config_dir, "custom_pdf_output")
        os.makedirs(custom_dir, exist_ok=True)

        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=custom_dir,
            file_format="pdf",
        )

        result = file_service.generate_file(request)

        # Verify file was created in custom directory
        assert result["success"] is True
        assert result["file_path"].startswith(custom_dir)
        assert os.path.exists(result["file_path"])

    def test_pdf_format_in_supported_formats(self, file_service):
        """Test that PDF format is included in supported formats."""
        formats = file_service.get_supported_formats()

        assert isinstance(formats, list)
        assert "pdf" in formats
        assert "text" in formats  # Should still support text

    def test_generate_pdf_with_preferences_saving(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test PDF generation with preferences saving."""
        custom_dir = os.path.join(temp_config_dir, "custom_pdf_output")
        os.makedirs(custom_dir, exist_ok=True)

        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=custom_dir,
            file_format="pdf",
            save_preferences=True,
        )

        result = file_service.generate_file(request)

        assert result["success"] is True

        # Verify preferences were saved by checking config
        current_config = file_service.get_current_config()
        assert current_config["output_directory"] == custom_dir

    def test_pdf_directory_permission_validation_success(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test successful PDF directory permission validation."""
        # Writable directory should succeed
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=temp_config_dir,
            file_format="pdf",
        )

        result = file_service.generate_file(request)
        assert result["success"] is True

    def test_pdf_directory_permission_validation_failure(
        self, file_service, sample_restaurants
    ):
        """Test PDF directory permission validation failure."""
        # Try to write to read-only directory
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory="/root",
            file_format="pdf",
        )

        result = file_service.generate_file(request)

        assert result["success"] is False
        assert "error" in result
        assert "permission" in result["error"].lower()

    def test_pdf_directory_creation_when_needed(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test automatic PDF directory creation when needed."""
        nested_dir = os.path.join(temp_config_dir, "level1", "level2", "pdf_output")

        # Directory doesn't exist yet
        assert not os.path.exists(nested_dir)

        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=nested_dir,
            file_format="pdf",
        )

        result = file_service.generate_file(request)

        # Verify directory was created and PDF generated
        assert result["success"] is True
        assert os.path.exists(nested_dir)
        assert os.path.exists(result["file_path"])

    def test_pdf_overwrite_handling(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test PDF file overwrite handling."""
        from datetime import datetime

        with patch("src.file_generator.pdf_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30, 45)

            # Generate first PDF
            request1 = FileGenerationRequest(
                restaurant_data=sample_restaurants,
                output_directory=temp_config_dir,
                file_format="pdf",
                allow_overwrite=True,
            )

            result1 = file_service.generate_file(request1)
            assert result1["success"] is True
            first_file = result1["file_path"]

            # Generate second PDF with same timestamp (should overwrite)
            result2 = file_service.generate_file(request1)
            assert result2["success"] is True
            assert result2["file_path"] == first_file

    def test_pdf_overwrite_protection(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test PDF file overwrite protection."""
        # Create existing PDF file
        existing_file = os.path.join(temp_config_dir, "WebScrape_20240315-143045.pdf")
        with open(existing_file, "w") as f:
            f.write("Existing PDF content")

        from datetime import datetime

        with patch("src.file_generator.pdf_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30, 45)

            request = FileGenerationRequest(
                restaurant_data=sample_restaurants,
                output_directory=temp_config_dir,
                file_format="pdf",
                allow_overwrite=False,
            )

            result = file_service.generate_file(request)

            assert result["success"] is False
            assert "exists" in result["error"].lower()

    def test_pdf_empty_restaurant_data_handling(self, file_service, temp_config_dir):
        """Test handling of empty restaurant data for PDF generation."""
        request = FileGenerationRequest(
            restaurant_data=[], output_directory=temp_config_dir, file_format="pdf"
        )

        result = file_service.generate_file(request)

        assert result["success"] is False
        assert "restaurant data" in result["error"].lower()

    def test_pdf_request_validation(
        self, file_service, sample_restaurants, temp_config_dir
    ):
        """Test PDF request validation."""
        # Valid PDF request
        valid_request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=temp_config_dir,
            file_format="pdf",
        )

        errors = valid_request.validate()
        assert len(errors) == 0

        # Invalid PDF request - unsupported format
        invalid_request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory=temp_config_dir,
            file_format="invalid_format",
        )

        errors = invalid_request.validate()
        assert len(errors) > 0
        assert any("format" in error for error in errors)

    def test_pdf_generation_error_handling(self, file_service, sample_restaurants):
        """Test PDF generation error handling."""
        # Test with problematic output directory
        request = FileGenerationRequest(
            restaurant_data=sample_restaurants,
            output_directory="/dev/null/invalid",  # Should cause error
            file_format="pdf",
        )

        result = file_service.generate_file(request)

        assert result["success"] is False
        assert "error" in result

    def test_pdf_generation_with_special_characters(
        self, file_service, temp_config_dir
    ):
        """Test PDF generation with special characters in restaurant data."""
        special_restaurant = RestaurantData(
            name="José's Café & Bistro",
            address="123 Rue de la Paix, Montréal, QC H3G 1A1",
            phone="(514) 555-CAFÉ",
            price_range="€15-€30",
            menu_items={
                "entrées": ["Salade niçoise", "Soupe à l'oignon"],
                "desserts": ["Crème brûlée", "Tarte tatin"],
            },
            cuisine="French",
            sources=["heuristic"],
        )

        request = FileGenerationRequest(
            restaurant_data=[special_restaurant],
            output_directory=temp_config_dir,
            file_format="pdf",
        )

        result = file_service.generate_file(request)

        assert result["success"] is True
        assert os.path.exists(result["file_path"])

        # Verify file has content despite special characters
        file_size = os.path.getsize(result["file_path"])
        assert file_size > 0


class TestDualFormatGeneration:
    """Test suite for dual format generation (text and PDF)."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def file_service(self, temp_config_dir):
        """Create FileGeneratorService instance."""
        config_file = os.path.join(temp_config_dir, "dual_format_config.json")
        return FileGeneratorService(config_file)

    @pytest.fixture
    def sample_restaurant(self):
        """Create sample restaurant data."""
        return RestaurantData(
            name="Dual Format Restaurant",
            address="123 Test Street",
            phone="555-TEST",
            cuisine="Test Cuisine",
            sources=["test"],
        )

    def test_generate_both_text_and_pdf_formats(
        self, file_service, sample_restaurant, temp_config_dir
    ):
        """Test generating both text and PDF formats."""
        # Generate text file
        text_request = FileGenerationRequest(
            restaurant_data=[sample_restaurant],
            output_directory=temp_config_dir,
            file_format="text",
        )
        text_result = file_service.generate_file(text_request)

        # Generate PDF file
        pdf_request = FileGenerationRequest(
            restaurant_data=[sample_restaurant],
            output_directory=temp_config_dir,
            file_format="pdf",
        )
        pdf_result = file_service.generate_file(pdf_request)

        # Verify both files were created successfully
        assert text_result["success"] is True
        assert pdf_result["success"] is True

        assert os.path.exists(text_result["file_path"])
        assert os.path.exists(pdf_result["file_path"])

        assert text_result["file_path"].endswith(".txt")
        assert pdf_result["file_path"].endswith(".pdf")

        # Verify both have same restaurant count
        assert text_result["restaurant_count"] == pdf_result["restaurant_count"]

    def test_dual_format_content_consistency(
        self, file_service, sample_restaurant, temp_config_dir
    ):
        """Test content consistency between text and PDF formats."""
        # Use same restaurant data for both formats
        restaurant_data = [sample_restaurant]

        # Generate text file
        text_request = FileGenerationRequest(
            restaurant_data=restaurant_data,
            output_directory=temp_config_dir,
            file_format="text",
        )
        text_result = file_service.generate_file(text_request)

        # Generate PDF file
        pdf_request = FileGenerationRequest(
            restaurant_data=restaurant_data,
            output_directory=temp_config_dir,
            file_format="pdf",
        )
        pdf_result = file_service.generate_file(pdf_request)

        # Verify both formats contain the same data
        assert text_result["success"] is True
        assert pdf_result["success"] is True
        assert text_result["restaurant_count"] == pdf_result["restaurant_count"]

        # Read text file content for basic validation
        with open(text_result["file_path"], "r", encoding="utf-8") as f:
            text_content = f.read()

        # Verify text content contains expected restaurant information
        assert sample_restaurant.name in text_content
        assert sample_restaurant.address in text_content
        assert sample_restaurant.phone in text_content

    def test_dual_format_with_large_dataset(self, file_service, temp_config_dir):
        """Test dual format generation with large dataset."""
        # Create large dataset
        large_dataset = []
        for i in range(20):
            restaurant = RestaurantData(
                name=f"Large Dataset Restaurant {i+1}",
                address=f"{1000+i} Dataset Street",
                phone=f"555-{1000+i:04d}",
                cuisine=f"Cuisine {i%3}",
                sources=["heuristic"],
            )
            large_dataset.append(restaurant)

        # Generate both formats
        text_request = FileGenerationRequest(
            restaurant_data=large_dataset,
            output_directory=temp_config_dir,
            file_format="text",
        )
        text_result = file_service.generate_file(text_request)

        pdf_request = FileGenerationRequest(
            restaurant_data=large_dataset,
            output_directory=temp_config_dir,
            file_format="pdf",
        )
        pdf_result = file_service.generate_file(pdf_request)

        # Verify both formats handle large dataset
        assert text_result["success"] is True
        assert pdf_result["success"] is True
        assert text_result["restaurant_count"] == 20
        assert pdf_result["restaurant_count"] == 20

        # Verify files exist and have content
        text_size = os.path.getsize(text_result["file_path"])
        pdf_size = os.path.getsize(pdf_result["file_path"])

        assert text_size > 0
        assert pdf_size > 0

        # PDF should be larger but not excessively so
        assert pdf_size > text_size  # PDF typically larger due to formatting
        assert pdf_size < text_size * 10  # But not more than 10x larger
