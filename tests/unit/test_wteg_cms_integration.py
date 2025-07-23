"""Unit tests for WTEG CMS integration and enhanced menu extraction compatibility."""

import pytest
from unittest.mock import MagicMock
from datetime import datetime

from src.wteg.cms_to_wteg_converter import CMSToWTEGConverter
from src.wteg.wteg_extractor import WTEGExtractor
from src.wteg.wteg_formatters import WTEGRAGFormatter
from src.wteg.wteg_schema import WTEGRestaurantData, WTEGMenuItem, WTEGLocation
from src.scraper.multi_strategy_scraper import RestaurantData


class TestCMSToWTEGConverter:
    """Test the CMS to WTEG converter functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = CMSToWTEGConverter()
    
    def test_convert_enhanced_cms_menu_items(self):
        """Test conversion of enhanced CMS menu items with detailed descriptions."""
        # Create mock CMS restaurant data with enhanced menu items
        cms_data = RestaurantData(
            name="Piattino Restaurant",
            address="1420 SE Stark St, Portland, OR 97214",
            phone="(503) 555-0123",
            cuisine="Italian",
            menu_items={
                "Cheese & Salumi": [
                    "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang",
                    "Gorgonzola: Blue veined buttery Italian cheese",
                    "Pecorino Toscana: strong, salty, intense"
                ],
                "Antipasti": [
                    "Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic",
                    "Carpaccio di Manzo: thin sliced raw beef with arugula, capers, and lemon"
                ]
            },
            confidence="high"
        )
        
        # Convert to WTEG format
        wteg_data = self.converter.convert_restaurant_data(cms_data)
        
        # Verify conversion
        assert isinstance(wteg_data, WTEGRestaurantData)
        assert wteg_data.brief_description == "Piattino Restaurant"
        assert wteg_data.cuisine == "Italian"
        assert len(wteg_data.menu_items) == 5  # Total items across categories
        
        # Check specific menu items with descriptions
        cheese_items = [item for item in wteg_data.menu_items if item.category == "Cheese & Salumi"]
        assert len(cheese_items) == 3
        
        taleggio_item = next((item for item in cheese_items if item.item_name == "Taleggio"), None)
        assert taleggio_item is not None
        assert taleggio_item.description == "cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang"
        assert taleggio_item.category == "Cheese & Salumi"
    
    def test_parse_enhanced_cms_item_formats(self):
        """Test parsing different CMS item formats."""
        # Test colon-separated format (enhanced CMS)
        item1 = self.converter._parse_enhanced_cms_item(
            "Taleggio: cow milk, semi-soft, wash rind", "Cheese"
        )
        assert item1.item_name == "Taleggio"
        assert item1.description == "cow milk, semi-soft, wash rind"
        assert item1.category == "Cheese"
        assert item1.price == ""
        
        # Test price format
        item2 = self.converter._parse_enhanced_cms_item(
            "Caesar Salad - $12.99", "Salads"
        )
        assert item2.item_name == "Caesar Salad"
        assert item2.price == "$12.99"
        assert item2.description == ""
        assert item2.category == "Salads"
        
        # Test simple name format
        item3 = self.converter._parse_enhanced_cms_item(
            "House Bread", "Appetizers"
        )
        assert item3.item_name == "House Bread"
        assert item3.description == ""
        assert item3.price == ""
        assert item3.category == "Appetizers"
    
    def test_location_conversion(self):
        """Test conversion of address string to WTEG location."""
        cms_data = RestaurantData(
            name="Test Restaurant",
            address="1420 SE Stark St, Portland, OR 97214"
        )
        
        wteg_data = self.converter.convert_restaurant_data(cms_data)
        
        assert wteg_data.location.street_address == "1420 SE Stark St"
        assert wteg_data.location.city == "Portland"
        assert wteg_data.location.state == "OR"
        assert wteg_data.location.zip_code == "97214"
    
    def test_contact_info_conversion(self):
        """Test conversion of phone number to WTEG contact format."""
        cms_data = RestaurantData(
            name="Test Restaurant",
            phone="(503) 555-0123"
        )
        
        wteg_data = self.converter.convert_restaurant_data(cms_data)
        
        assert wteg_data.click_to_call.primary_phone == "(503) 555-0123"
        assert wteg_data.click_to_call.formatted_display == "(503) 555-0123"
        assert wteg_data.click_to_call.clickable_link == "tel:5035550123"
    
    def test_confidence_calculation(self):
        """Test confidence score calculation from CMS data."""
        # High confidence with rich data
        rich_cms_data = RestaurantData(
            name="Rich Restaurant",
            address="123 Main St, City, ST 12345",
            phone="(555) 123-4567",
            cuisine="French",
            menu_items={
                "Entrees": [
                    "Coq au Vin: classic French chicken braised in wine with mushrooms and herbs",
                    "Beef Bourguignon: slow-braised beef in red wine with pearl onions and carrots"
                ]
            },
            confidence="high"
        )
        
        confidence = self.converter._calculate_confidence_from_cms(rich_cms_data)
        assert confidence > 0.8  # Should be high confidence
        
        # Low confidence with minimal data
        minimal_cms_data = RestaurantData(
            name="Minimal Restaurant",
            confidence="low"
        )
        
        confidence = self.converter._calculate_confidence_from_cms(minimal_cms_data)
        assert confidence < 0.3  # Should be low confidence
    
    def test_conversion_validation(self):
        """Test validation of conversion quality."""
        cms_data = RestaurantData(
            name="Test Restaurant",
            address="123 Main St",
            phone="555-1234",
            menu_items={
                "Mains": ["Pasta: delicious pasta dish"]
            }
        )
        
        wteg_data = self.converter.convert_restaurant_data(cms_data)
        validation = self.converter.validate_conversion(cms_data, wteg_data)
        
        assert validation["conversion_successful"] is True
        assert validation["data_preserved"]["name"] is True
        assert validation["data_preserved"]["menu_items"] is True
        assert validation["data_preserved"]["contact"] is True
        assert validation["enhancements"]["detailed_menu_descriptions"] == 1


class TestWTEGExtractorEnhancements:
    """Test enhanced WTEG extractor with CMS format support."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = WTEGExtractor()
    
    def test_parse_menu_item_string_enhanced_format(self):
        """Test parsing enhanced CMS format in WTEG extractor."""
        # Test enhanced CMS format
        item1 = self.extractor._parse_menu_item_string(
            "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma"
        )
        assert item1.item_name == "Taleggio"
        assert item1.description == "cow milk, semi-soft, wash rind, strong, bold aroma"
        assert item1.price == ""
        
        # Test traditional price format
        item2 = self.extractor._parse_menu_item_string(
            "Caesar Salad - $12.99"
        )
        assert item2.item_name == "Caesar Salad"
        assert item2.price == "$12.99"
        assert item2.description == ""
        
        # Test simple format
        item3 = self.extractor._parse_menu_item_string("House Bread")
        assert item3.item_name == "House Bread"
        assert item3.description == ""
        assert item3.price == ""
    
    def test_parse_menu_items_mixed_formats(self):
        """Test parsing mixed menu item formats."""
        menu_data = [
            "Taleggio: cow milk, semi-soft, wash rind",
            "Caesar Salad - $12.99",
            "House Bread",
            {"name": "Structured Item", "description": "Dict format", "price": "$15.00"}
        ]
        
        items = self.extractor._parse_menu_items(menu_data)
        
        assert len(items) == 4
        assert items[0].item_name == "Taleggio"
        assert items[0].description == "cow milk, semi-soft, wash rind"
        assert items[1].item_name == "Caesar Salad"
        assert items[1].price == "$12.99"
        assert items[2].item_name == "House Bread"
        assert items[3].item_name == "Structured Item"


class TestWTEGRAGFormatterEnhancements:
    """Test enhanced WTEG RAG formatter with description support."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create test restaurant with enhanced menu items
        self.restaurant = WTEGRestaurantData(
            brief_description="Test Restaurant",
            cuisine="Italian",
            menu_items=[
                WTEGMenuItem(
                    item_name="Taleggio",
                    description="cow milk, semi-soft, wash rind, strong, bold aroma",
                    category="Cheese"
                ),
                WTEGMenuItem(
                    item_name="Gorgonzola",
                    description="Blue veined buttery Italian cheese",
                    category="Cheese"
                ),
                WTEGMenuItem(
                    item_name="Caesar Salad",
                    price="$12.99",
                    category="Salads"
                )
            ]
        )
        self.formatter = WTEGRAGFormatter(self.restaurant)
    
    def test_format_menu_with_descriptions(self):
        """Test that menu formatting includes descriptions."""
        menu_summary = self.formatter._format_menu()
        
        # Should include descriptions for items that have them
        assert "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma" in menu_summary
        assert "Gorgonzola: Blue veined buttery Italian cheese" in menu_summary
        
        # Should include price for items without descriptions
        assert "Caesar Salad ($12.99)" in menu_summary
        
        # Should group by category
        assert "Cheese:" in menu_summary
        assert "Salads:" in menu_summary
    
    def test_rag_format_includes_descriptions(self):
        """Test that RAG format preserves detailed descriptions."""
        rag_format = self.formatter.format()
        
        menu_summary = rag_format["menu_summary"]
        
        # Verify descriptions are preserved in RAG output
        assert "cow milk, semi-soft, wash rind" in menu_summary
        assert "Blue veined buttery Italian cheese" in menu_summary
        
        # Verify searchable content includes descriptions
        searchable = rag_format["searchable_content"]
        assert "cow milk, semi-soft, wash rind" in searchable
    
    def test_searchable_text_includes_menu_descriptions(self):
        """Test that searchable text includes detailed menu descriptions."""
        searchable_text = self.formatter._create_searchable_text()
        
        # Should include all detailed descriptions for RAG embedding
        assert "cow milk, semi-soft, wash rind, strong, bold aroma" in searchable_text
        assert "Blue veined buttery Italian cheese" in searchable_text
        assert "Taleggio" in searchable_text
        assert "Gorgonzola" in searchable_text


class TestEndToEndWTEGIntegration:
    """Test end-to-end integration of enhanced CMS extraction with WTEG."""
    
    def test_cms_to_wteg_to_rag_pipeline(self):
        """Test complete pipeline from CMS extraction to RAG output."""
        # Step 1: Create enhanced CMS extraction result
        cms_data = RestaurantData(
            name="Piattino Portland",
            address="1420 SE Stark St, Portland, OR 97214",
            phone="(503) 555-0123",
            cuisine="Italian",
            menu_items={
                "Cheese & Salumi": [
                    "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang",
                    "Gorgonzola: Blue veined buttery Italian cheese"
                ],
                "Antipasti": [
                    "Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic"
                ]
            },
            confidence="high"
        )
        
        # Step 2: Convert to WTEG format
        converter = CMSToWTEGConverter()
        wteg_data = converter.convert_restaurant_data(cms_data)
        
        # Step 3: Format for RAG
        formatter = WTEGRAGFormatter(wteg_data)
        rag_output = formatter.format()
        
        # Step 4: Verify end-to-end preservation of detailed descriptions
        menu_summary = rag_output["menu_summary"]
        
        # Critical test: detailed descriptions should be preserved throughout the pipeline
        assert "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang" in menu_summary
        assert "Gorgonzola: Blue veined buttery Italian cheese" in menu_summary
        assert "Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic" in menu_summary
        
        # Verify searchable content includes descriptions for RAG embedding
        searchable = rag_output["searchable_content"]
        assert "cow milk, semi-soft, wash rind" in searchable
        assert "Blue veined buttery" in searchable
        assert "grilled bread with fresh tomatoes" in searchable
        
        # Verify restaurant metadata is preserved
        assert rag_output["restaurant_name"] == "Piattino Portland"
        assert rag_output["cuisine_type"] == "Italian"
        assert rag_output["location_summary"] == "1420 SE Stark St, Portland, OR 97214"
    
    def test_backward_compatibility_with_existing_formats(self):
        """Test that enhancements don't break existing WTEG functionality."""
        # Test with traditional WTEG format (no descriptions)
        traditional_wteg = WTEGRestaurantData(
            brief_description="Traditional Restaurant",
            cuisine="American",
            menu_items=[
                WTEGMenuItem(item_name="Burger", price="$15.00", category="Mains"),
                WTEGMenuItem(item_name="Fries", price="$8.00", category="Sides")
            ]
        )
        
        formatter = WTEGRAGFormatter(traditional_wteg)
        rag_output = formatter.format()
        
        # Should still work correctly
        assert "Burger ($15.00)" in rag_output["menu_summary"]
        assert "Fries ($8.00)" in rag_output["menu_summary"]
        assert rag_output["restaurant_name"] == "Traditional Restaurant"
    
    def test_validation_reports_conversion_quality(self):
        """Test that validation correctly reports conversion quality."""
        # High-quality CMS data
        rich_cms_data = RestaurantData(
            name="Excellent Restaurant",
            address="123 Perfect St, Great City, ST 12345",
            phone="555-GREAT",
            cuisine="Fine Dining",
            menu_items={
                "Signature Dishes": [
                    "Wagyu Beef: premium Japanese beef with truffle sauce and seasonal vegetables",
                    "Lobster Thermidor: fresh Maine lobster with cognac cream sauce"
                ]
            },
            confidence="high"
        )
        
        converter = CMSToWTEGConverter()
        wteg_data = converter.convert_restaurant_data(rich_cms_data)
        validation = converter.validate_conversion(rich_cms_data, wteg_data)
        
        assert validation["conversion_successful"] is True
        assert validation["data_preserved"]["name"] is True
        assert validation["data_preserved"]["menu_items"] is True
        assert validation["data_preserved"]["contact"] is True
        assert validation["data_preserved"]["location"] is True
        assert validation["enhancements"]["detailed_menu_descriptions"] == 2
        assert validation["enhancements"]["confidence_score"] > 0.8
        assert len(validation["issues"]) == 0