"""Unit tests for PDF generator."""
import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.pdf_generator import PDFGenerator, PDFConfig


class TestPDFConfig:
    """Test suite for PDFConfig data class."""

    def test_pdf_config_creation_with_defaults(self):
        """Test creating PDFConfig with default values."""
        config = PDFConfig()

        assert config.output_directory == "."
        assert config.allow_overwrite is True
        assert config.font_family == "Helvetica"
        assert config.font_size == 12
        assert config.page_orientation == "portrait"
        assert config.margin_size == "standard"
        assert config.filename_pattern == "WebScrape_{timestamp}.pdf"

    def test_pdf_config_creation_with_custom_values(self):
        """Test creating PDFConfig with custom values."""
        config = PDFConfig(
            output_directory="/custom/path",
            allow_overwrite=False,
            font_family="Times-Roman",
            font_size=14,
            page_orientation="landscape",
            margin_size="wide",
            filename_pattern="Custom_{timestamp}.pdf",
        )

        assert config.output_directory == "/custom/path"
        assert config.allow_overwrite is False
        assert config.font_family == "Times-Roman"
        assert config.font_size == 14
        assert config.page_orientation == "landscape"
        assert config.margin_size == "wide"
        assert config.filename_pattern == "Custom_{timestamp}.pdf"

    def test_pdf_config_validation_invalid_orientation(self):
        """Test PDFConfig validation with invalid orientation."""
        config = PDFConfig(page_orientation="invalid")

        # Should revert to default
        assert config.page_orientation == "portrait"

    def test_pdf_config_validation_invalid_margin(self):
        """Test PDFConfig validation with invalid margin size."""
        config = PDFConfig(margin_size="invalid")

        # Should revert to default
        assert config.margin_size == "standard"


class TestPDFGenerator:
    """Test suite for PDFGenerator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def pdf_config(self, temp_dir):
        """Create PDFConfig for testing."""
        return PDFConfig(
            output_directory=temp_dir,
            allow_overwrite=True,
            font_family="Helvetica",
            font_size=12,
        )

    @pytest.fixture
    def pdf_generator(self, pdf_config):
        """Create PDFGenerator instance for testing."""
        return PDFGenerator(pdf_config)

    @pytest.fixture
    def sample_restaurant(self):
        """Create sample restaurant data."""
        return RestaurantData(
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
        )

    def test_pdf_generator_initialization_portrait(self, pdf_config):
        """Test PDFGenerator initialization with portrait orientation."""
        generator = PDFGenerator(pdf_config)

        assert generator.config == pdf_config
        assert (
            generator.page_size[0] < generator.page_size[1]
        )  # Width < Height for portrait
        assert generator.margin == 0.75 * 72  # Standard margin in points

    def test_pdf_generator_initialization_landscape(self, temp_dir):
        """Test PDFGenerator initialization with landscape orientation."""
        config = PDFConfig(output_directory=temp_dir, page_orientation="landscape")
        generator = PDFGenerator(config)

        assert (
            generator.page_size[0] > generator.page_size[1]
        )  # Width > Height for landscape

    def test_pdf_generator_initialization_margin_sizes(self, temp_dir):
        """Test PDFGenerator initialization with different margin sizes."""
        narrow_config = PDFConfig(output_directory=temp_dir, margin_size="narrow")
        standard_config = PDFConfig(output_directory=temp_dir, margin_size="standard")
        wide_config = PDFConfig(output_directory=temp_dir, margin_size="wide")

        narrow_gen = PDFGenerator(narrow_config)
        standard_gen = PDFGenerator(standard_config)
        wide_gen = PDFGenerator(wide_config)

        assert narrow_gen.margin < standard_gen.margin < wide_gen.margin

    def test_generate_file_with_single_restaurant(
        self, pdf_generator, sample_restaurant
    ):
        """Test generating PDF file with single restaurant."""
        with patch("src.file_generator.pdf_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30, 45)

            file_path = pdf_generator.generate_file([sample_restaurant])

            # Verify file was created
            assert os.path.exists(file_path)
            assert file_path.endswith(".pdf")
            assert "WebScrape_20240315-143045.pdf" in file_path

            # Verify file has content
            file_size = os.path.getsize(file_path)
            assert file_size > 0

    def test_generate_file_with_multiple_restaurants(self, pdf_generator, temp_dir):
        """Test generating PDF file with multiple restaurants."""
        restaurants = [
            RestaurantData(name="Restaurant 1", sources=["heuristic"]),
            RestaurantData(name="Restaurant 2", sources=["heuristic"]),
            RestaurantData(name="Restaurant 3", sources=["heuristic"]),
        ]

        file_path = pdf_generator.generate_file(restaurants)

        # Verify file was created
        assert os.path.exists(file_path)
        assert file_path.endswith(".pdf")

        # Verify file has content (should be larger for multiple restaurants)
        file_size = os.path.getsize(file_path)
        assert file_size > 0

    def test_generate_file_empty_restaurant_data(self, pdf_generator):
        """Test generating PDF file with empty restaurant data."""
        with pytest.raises(ValueError) as exc_info:
            pdf_generator.generate_file([])

        assert "No restaurant data available" in str(exc_info.value)

    def test_generate_file_none_restaurant_data(self, pdf_generator):
        """Test generating PDF file with None restaurant data."""
        with pytest.raises(ValueError) as exc_info:
            pdf_generator.generate_file(None)

        assert "No restaurant data available" in str(exc_info.value)

    def test_generate_file_permission_error(self, sample_restaurant):
        """Test generating PDF file with permission error."""
        config = PDFConfig(output_directory="/root")  # Should cause permission error
        generator = PDFGenerator(config)

        with pytest.raises(PermissionError) as exc_info:
            generator.generate_file([sample_restaurant])

        assert "No write permission" in str(exc_info.value)

    def test_generate_file_overwrite_disabled(
        self, pdf_generator, sample_restaurant, temp_dir
    ):
        """Test generating PDF file with overwrite disabled."""
        # Create existing file
        existing_file = os.path.join(temp_dir, "WebScrape_20240315-143045.pdf")
        with open(existing_file, "w") as f:
            f.write("existing content")

        # Configure generator to not allow overwrite
        pdf_generator.config.allow_overwrite = False

        with patch("src.file_generator.pdf_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30, 45)

            with pytest.raises(FileExistsError) as exc_info:
                pdf_generator.generate_file([sample_restaurant])

            assert "File already exists" in str(exc_info.value)

    def test_generate_file_overwrite_enabled(
        self, pdf_generator, sample_restaurant, temp_dir
    ):
        """Test generating PDF file with overwrite enabled."""
        # Create existing file
        existing_file = os.path.join(temp_dir, "WebScrape_20240315-143045.pdf")
        with open(existing_file, "w") as f:
            f.write("existing content")

        original_size = os.path.getsize(existing_file)

        with patch("src.file_generator.pdf_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30, 45)

            file_path = pdf_generator.generate_file([sample_restaurant])

            # File should be overwritten with PDF content
            assert os.path.exists(file_path)
            new_size = os.path.getsize(file_path)
            assert new_size != original_size  # Should be different size

    def test_generate_filename_with_timestamp(self, pdf_generator):
        """Test filename generation with timestamp."""
        with patch("src.file_generator.pdf_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30, 45)

            filename = pdf_generator._generate_filename()

            assert filename == "WebScrape_20240315-143045.pdf"

    def test_generate_filename_with_custom_pattern(self, temp_dir):
        """Test filename generation with custom pattern."""
        config = PDFConfig(
            output_directory=temp_dir, filename_pattern="Custom_{timestamp}_Report.pdf"
        )
        generator = PDFGenerator(config)

        with patch("src.file_generator.pdf_generator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 12, 25, 9, 15, 30)

            filename = generator._generate_filename()

            assert filename == "Custom_20241225-091530_Report.pdf"

    def test_format_menu_items_empty(self, pdf_generator):
        """Test formatting empty menu items."""
        result = pdf_generator._format_menu_items({})
        assert result == "No menu items available"

    def test_format_menu_items_none(self, pdf_generator):
        """Test formatting None menu items."""
        result = pdf_generator._format_menu_items(None)
        assert result == "No menu items available"

    def test_format_menu_items_with_data(self, pdf_generator):
        """Test formatting menu items with data."""
        menu_items = {
            "appetizers": ["Bruschetta", "Calamari"],
            "main_courses": ["Pasta", "Pizza"],
            "desserts": ["Tiramisu"],
        }

        result = pdf_generator._format_menu_items(menu_items)

        assert "Appetizers:" in result
        assert "Main Courses:" in result
        assert "Desserts:" in result
        assert "Bruschetta, Calamari" in result
        assert "Pasta, Pizza" in result
        assert "Tiramisu" in result

    def test_format_menu_items_with_empty_categories(self, pdf_generator):
        """Test formatting menu items with some empty categories."""
        menu_items = {
            "appetizers": ["Bruschetta"],
            "main_courses": [],  # Empty category
            "desserts": ["Tiramisu"],
        }

        result = pdf_generator._format_menu_items(menu_items)

        assert "Appetizers:" in result
        assert "Desserts:" in result
        assert "Main Courses:" not in result  # Should not include empty categories

    def test_validate_restaurant_data_valid(self, pdf_generator):
        """Test validation of valid restaurant data."""
        restaurants = [
            RestaurantData(name="Restaurant 1", sources=["heuristic"]),
            RestaurantData(name="Restaurant 2", sources=["json-ld"]),
        ]

        warnings = pdf_generator.validate_restaurant_data(restaurants)
        assert len(warnings) == 0

    def test_validate_restaurant_data_empty(self, pdf_generator):
        """Test validation of empty restaurant data."""
        warnings = pdf_generator.validate_restaurant_data([])

        assert len(warnings) == 1
        assert "No restaurant data provided" in warnings[0]

    def test_validate_restaurant_data_missing_name(self, pdf_generator):
        """Test validation of restaurant data with missing name."""
        restaurants = [
            RestaurantData(name="", sources=["heuristic"]),  # Missing name
            RestaurantData(name="Valid Restaurant", sources=["heuristic"]),
        ]

        warnings = pdf_generator.validate_restaurant_data(restaurants)

        assert len(warnings) == 1
        assert "Restaurant 1: Missing name" in warnings[0]

    def test_validate_restaurant_data_missing_sources(self, pdf_generator):
        """Test validation of restaurant data with missing sources."""
        restaurants = [
            RestaurantData(name="Restaurant 1", sources=[]),  # Missing sources
            RestaurantData(name="Restaurant 2", sources=["heuristic"]),
        ]

        warnings = pdf_generator.validate_restaurant_data(restaurants)

        assert len(warnings) == 1
        assert "Restaurant 1 (Restaurant 1): No data sources specified" in warnings[0]

    def test_validate_restaurant_data_multiple_issues(self, pdf_generator):
        """Test validation of restaurant data with multiple issues."""
        restaurants = [
            RestaurantData(name="", sources=[]),  # Missing name and sources
            RestaurantData(name="Restaurant 2", sources=[]),  # Missing sources
            RestaurantData(name="Valid Restaurant", sources=["heuristic"]),
        ]

        warnings = pdf_generator.validate_restaurant_data(restaurants)

        assert len(warnings) == 3
        assert any("Restaurant 1: Missing name" in warning for warning in warnings)
        assert any(
            "Restaurant 1 (Restaurant 1): No data sources specified" in warning
            for warning in warnings
        )
        assert any(
            "Restaurant 2 (Restaurant 2): No data sources specified" in warning
            for warning in warnings
        )


class TestPDFGeneratorIntegration:
    """Integration tests for PDF generator with realistic scenarios."""

    def test_complex_restaurant_data_integration(self):
        """Test PDF generation with complex restaurant data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PDFConfig(output_directory=temp_dir)
            generator = PDFGenerator(config)

            complex_restaurant = RestaurantData(
                name="José's Café & Bistro",
                address="123 Rue de la Paix, Montréal, QC H3G 1A1",
                phone="(514) 555-CAFÉ",
                price_range="$15-$30",
                hours="Lundi-Dimanche 7h-22h",
                menu_items={
                    "entrées": ["Salade niçoise", "Soupe à l'oignon"],
                    "plats_principaux": ["Coq au vin", "Ratatouille"],
                    "desserts": ["Crème brûlée", "Tarte tatin"],
                },
                cuisine="French",
                confidence="high",
                sources=["json-ld", "heuristic"],
                social_media=["@josescafe", "facebook.com/josescafe"],
            )

            file_path = generator.generate_file([complex_restaurant])

            # Verify file creation and basic properties
            assert os.path.exists(file_path)
            assert file_path.endswith(".pdf")

            # Verify file size is reasonable for complex content
            file_size = os.path.getsize(file_path)
            assert file_size > 1000  # Should be substantial for complex content

    def test_large_dataset_performance(self):
        """Test PDF generation performance with large dataset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PDFConfig(output_directory=temp_dir)
            generator = PDFGenerator(config)

            # Create large dataset
            large_dataset = []
            for i in range(100):
                restaurant = RestaurantData(
                    name=f"Restaurant {i+1}",
                    address=f"{1000+i} Test Street, City, State {97000+i}",
                    phone=f"(555) {1000+i:04d}",
                    price_range="$10-$30",
                    hours="Daily 11am-10pm",
                    menu_items={
                        "appetizers": [f"Appetizer {j}" for j in range(3)],
                        "entrees": [f"Entree {j}" for j in range(5)],
                        "desserts": [f"Dessert {j}" for j in range(2)],
                    },
                    cuisine=f"Cuisine {i%5}",
                    confidence="medium",
                    sources=["heuristic"],
                )
                large_dataset.append(restaurant)

            import time

            start_time = time.time()

            file_path = generator.generate_file(large_dataset)

            end_time = time.time()
            generation_time = end_time - start_time

            # Verify performance requirements
            assert generation_time < 10.0  # Should complete within 10 seconds

            # Verify file was created successfully
            assert os.path.exists(file_path)
            file_size = os.path.getsize(file_path)
            assert file_size > 0

            # Performance check: should not be excessively large
            # Rough estimate: should be less than 5x equivalent text size
            estimated_text_size = len(large_dataset) * 500  # ~500 chars per restaurant
            assert file_size < estimated_text_size * 5

    def test_pdf_generation_with_missing_fields(self):
        """Test PDF generation handles missing fields gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PDFConfig(output_directory=temp_dir)
            generator = PDFGenerator(config)

            incomplete_restaurant = RestaurantData(
                name="Minimal Restaurant",
                sources=["heuristic"]
                # Missing: address, phone, hours, menu_items, etc.
            )

            file_path = generator.generate_file([incomplete_restaurant])

            # Should still generate valid PDF
            assert os.path.exists(file_path)
            file_size = os.path.getsize(file_path)
            assert file_size > 0

    def test_pdf_config_persistence_simulation(self):
        """Test PDF configuration persistence across different generator instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Session 1: Create and use configuration
            config1 = PDFConfig(
                output_directory=temp_dir,
                font_family="Times-Roman",
                page_orientation="landscape",
                margin_size="wide",
            )
            generator1 = PDFGenerator(config1)

            # Session 2: Create new generator with same configuration
            config2 = PDFConfig(
                output_directory=temp_dir,
                font_family="Times-Roman",
                page_orientation="landscape",
                margin_size="wide",
            )
            generator2 = PDFGenerator(config2)

            # Both generators should have same configuration
            assert generator1.config.font_family == generator2.config.font_family
            assert (
                generator1.config.page_orientation == generator2.config.page_orientation
            )
            assert generator1.config.margin_size == generator2.config.margin_size
            assert generator1.page_size == generator2.page_size
            assert generator1.margin == generator2.margin
