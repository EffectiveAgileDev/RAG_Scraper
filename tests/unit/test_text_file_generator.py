"""Unit tests for text file generator."""
import os
import tempfile
import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.text_file_generator import TextFileGenerator, TextFileConfig


class TestTextFileGenerator:
    """Test suite for TextFileGenerator."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def text_generator(self, temp_output_dir):
        """Create TextFileGenerator instance."""
        config = TextFileConfig(output_directory=temp_output_dir)
        return TextFileGenerator(config)
    
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
                "appetizers": ["Fresh bruschetta", "calamari rings", "antipasto platter"],
                "entrees": ["Homemade pasta", "wood-fired pizza", "fresh seafood"],
                "desserts": ["Tiramisu", "cannoli", "gelato"]
            },
            cuisine="Italian",
            sources=["json-ld", "heuristic"]
        )
    
    def test_generate_single_restaurant_file(self, text_generator, sample_restaurant):
        """Test generating file for single restaurant."""
        output_file = text_generator.generate_file([sample_restaurant])
        
        # Verify file was created
        assert os.path.exists(output_file)
        
        # Verify filename format
        filename = os.path.basename(output_file)
        assert filename.startswith("WebScrape_")
        assert filename.endswith(".txt")
        
        # Verify content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Tony's Italian Restaurant" in content
        assert "1234 Commercial Street, Salem, OR 97301" in content
        assert "(503) 555-0123" in content
        assert "$18-$32" in content
        assert "Hours: Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm" in content
        assert "APPETIZERS: Fresh bruschetta, calamari rings, antipasto platter" in content
        assert "ENTREES: Homemade pasta, wood-fired pizza, fresh seafood" in content
        assert "DESSERTS: Tiramisu, cannoli, gelato" in content
        assert "CUISINE: Italian" in content
    
    def test_generate_minimal_restaurant_file(self, text_generator):
        """Test generating file for restaurant with minimal data."""
        minimal_restaurant = RestaurantData(
            name="Simple Cafe",
            phone="555-1234",
            sources=["heuristic"]
        )
        
        output_file = text_generator.generate_file([minimal_restaurant])
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        expected_content = "Simple Cafe\n555-1234"
        assert content == expected_content
    
    def test_generate_multiple_restaurants_file(self, text_generator):
        """Test generating file for multiple restaurants."""
        restaurants = [
            RestaurantData(name="Restaurant 1", address="123 Main St", phone="555-0001", sources=["heuristic"]),
            RestaurantData(name="Restaurant 2", address="456 Oak Ave", phone="555-0002", sources=["heuristic"]),
            RestaurantData(name="Restaurant 3", address="789 Pine Rd", phone="555-0003", sources=["heuristic"])
        ]
        
        output_file = text_generator.generate_file(restaurants)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify all restaurants are present
        assert "Restaurant 1" in content
        assert "Restaurant 2" in content  
        assert "Restaurant 3" in content
        
        # Verify restaurants are separated by double carriage returns
        assert content.count("\n\n\n") == 2  # 2 separators for 3 restaurants
    
    def test_filename_timestamp_format(self, text_generator):
        """Test filename timestamp format."""
        with patch('src.file_generator.text_file_generator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30)
            
            restaurant = RestaurantData(name="Test Restaurant", sources=["heuristic"])
            output_file = text_generator.generate_file([restaurant])
            
            filename = os.path.basename(output_file)
            assert filename == "WebScrape_20240315-1430.txt"
    
    def test_utf8_encoding_special_characters(self, text_generator):
        """Test UTF-8 encoding with special characters."""
        restaurant = RestaurantData(
            name="Café España",
            cuisine="Spanish & Latin American",
            menu_items={"desserts": ["crème brûlée", "flan"]},
            sources=["heuristic"]
        )
        
        output_file = text_generator.generate_file([restaurant])
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Café España" in content
        assert "Spanish & Latin American" in content
        assert "crème brûlée" in content
    
    def test_empty_restaurant_list_raises_error(self, text_generator):
        """Test that empty restaurant list raises ValueError."""
        with pytest.raises(ValueError, match="No restaurant data available"):
            text_generator.generate_file([])
    
    def test_file_overwrite_protection(self, text_generator, temp_output_dir):
        """Test file overwrite protection."""
        # Create existing file
        existing_file = os.path.join(temp_output_dir, "WebScrape_20240315-1430.txt")
        with open(existing_file, 'w') as f:
            f.write("Existing content")
        
        # Configure generator to disallow overwrite
        config = TextFileConfig(output_directory=temp_output_dir, allow_overwrite=False)
        generator = TextFileGenerator(config)
        
        with patch('src.file_generator.text_file_generator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2024, 3, 15, 14, 30)
            
            restaurant = RestaurantData(name="Test Restaurant", sources=["heuristic"])
            
            with pytest.raises(FileExistsError):
                generator.generate_file([restaurant])
    
    def test_permission_error_handling(self):
        """Test permission error handling."""
        # Try to write to read-only directory
        config = TextFileConfig(output_directory="/root")
        generator = TextFileGenerator(config)
        
        restaurant = RestaurantData(name="Test Restaurant", sources=["heuristic"])
        
        with pytest.raises(PermissionError):
            generator.generate_file([restaurant])
    
    def test_large_batch_processing(self, text_generator):
        """Test processing large batch of restaurants."""
        restaurants = []
        for i in range(1, 51):  # 50 restaurants
            restaurants.append(RestaurantData(
                name=f"Restaurant {i}",
                address=f"{i*100} Main St",
                phone=f"555-{i:04d}",
                sources=["heuristic"]
            ))
        
        output_file = text_generator.generate_file(restaurants)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify all restaurants are present
        assert content.count("Restaurant ") == 50
        
        # Verify proper separation
        assert content.count("\n\n\n") == 49  # 49 separators for 50 restaurants
        
        # Verify file size is reasonable (under 10MB)
        file_size = os.path.getsize(output_file)
        assert file_size < 10 * 1024 * 1024


class TestTextFileConfig:
    """Test suite for TextFileConfig."""
    
    def test_config_creates_output_directory(self):
        """Test that config creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_subdir")
            assert not os.path.exists(new_dir)
            
            config = TextFileConfig(output_directory=new_dir)
            assert os.path.exists(new_dir)
    
    def test_config_default_values(self):
        """Test config default values."""
        config = TextFileConfig()
        
        assert config.output_directory == "."
        assert config.allow_overwrite is True
        assert config.encoding == "utf-8"
        assert config.filename_pattern == "WebScrape_{timestamp}.txt"


class TestMenuItemFormatting:
    """Test suite for menu item formatting."""
    
    @pytest.fixture
    def text_generator(self):
        """Create TextFileGenerator instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = TextFileConfig(output_directory=temp_dir)
            yield TextFileGenerator(config)
    
    def test_standard_menu_sections(self, text_generator):
        """Test formatting of standard menu sections."""
        restaurant = RestaurantData(
            name="Test Restaurant",
            menu_items={
                "appetizers": ["Soup", "Salad"],
                "entrees": ["Steak", "Fish"],
                "desserts": ["Cake", "Ice cream"]
            },
            sources=["heuristic"]
        )
        
        output_file = text_generator.generate_file([restaurant])
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "APPETIZERS: Soup, Salad" in content
        assert "ENTREES: Steak, Fish" in content
        assert "DESSERTS: Cake, Ice cream" in content
    
    def test_menu_section_mapping(self, text_generator):
        """Test that menu sections are mapped correctly."""
        restaurant = RestaurantData(
            name="Test Restaurant",
            menu_items={
                "mains": ["Burger", "Pizza"],  # Should map to ENTREES
                "beverages": ["Coffee", "Tea"]  # Should map to DRINKS
            },
            sources=["heuristic"]
        )
        
        output_file = text_generator.generate_file([restaurant])
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "ENTREES: Burger, Pizza" in content
        assert "DRINKS: Coffee, Tea" in content
    
    def test_custom_menu_sections(self, text_generator):
        """Test formatting of custom menu sections."""
        restaurant = RestaurantData(
            name="Test Restaurant",
            menu_items={
                "special_items": ["Today's Special", "Chef's Choice"]
            },
            sources=["heuristic"]
        )
        
        output_file = text_generator.generate_file([restaurant])
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "SPECIAL ITEMS: Today's Special, Chef's Choice" in content