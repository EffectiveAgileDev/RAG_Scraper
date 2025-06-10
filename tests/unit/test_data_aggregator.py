"""Unit tests for multi-page data aggregation and conflict resolution."""
import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Dict, Any


class TestDataAggregator:
    """Test data aggregation from multiple pages."""
    
    def test_create_data_aggregator(self):
        """Test creation of data aggregator."""
        from src.scraper.data_aggregator import DataAggregator
        
        aggregator = DataAggregator()
        
        assert hasattr(aggregator, 'page_data')
        assert hasattr(aggregator, 'conflict_resolution_rules')
    
    def test_add_page_data(self):
        """Test adding data from individual pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        page_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Tony's Restaurant",
            menu_items={"Appetizers": ["Calamari", "Bruschetta"]},
            source="json-ld"
        )
        
        aggregator.add_page_data(page_data)
        
        assert len(aggregator.page_data) == 1
        assert aggregator.page_data[0].page_type == "menu"
    
    def test_aggregate_restaurant_data_from_multiple_pages(self):
        """Test aggregating restaurant data from multiple pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        from src.scraper.multi_strategy_scraper import RestaurantData
        
        aggregator = DataAggregator()
        
        # Add data from home page
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Tony's Italian Restaurant",
            cuisine="Italian",
            source="heuristic"
        )
        
        # Add data from menu page
        menu_data = PageData(
            url="http://example.com/menu", 
            page_type="menu",
            restaurant_name="Tony's Restaurant",
            menu_items={"Appetizers": ["Calamari"], "Entrees": ["Pasta"]},
            price_range="$15-30",
            source="json-ld"
        )
        
        # Add data from contact page
        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact", 
            restaurant_name="Tony's Italian",
            phone="(503) 555-1234",
            address="123 Main St, Portland, OR",
            hours="Mon-Sun 11am-10pm",
            source="microdata"
        )
        
        aggregator.add_page_data(home_data)
        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(contact_data)
        
        result = aggregator.aggregate()
        
        assert isinstance(result, RestaurantData)
        assert result.name == "Tony's Italian Restaurant"  # From home page
        assert result.cuisine == "Italian"
        assert result.phone == "(503) 555-1234"
        assert result.address == "123 Main St, Portland, OR"
        assert result.hours == "Mon-Sun 11am-10pm"
        assert result.price_range == "$15-30"
        assert "Calamari" in result.menu_items.get("Appetizers", [])
    
    def test_resolve_conflicting_restaurant_names(self):
        """Test resolving conflicting restaurant names across pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        # Different name variations across pages
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Tony's Italian Restaurant",
            source="heuristic"
        )
        
        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu", 
            restaurant_name="Tony's Restaurant",
            source="json-ld"
        )
        
        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            restaurant_name="Tony's Italian",
            source="microdata"
        )
        
        aggregator.add_page_data(home_data)
        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(contact_data)
        
        result = aggregator.aggregate()
        
        # Should prioritize JSON-LD source
        assert result.name == "Tony's Restaurant"
    
    def test_resolve_conflicting_contact_information(self):
        """Test resolving conflicting contact information."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        # Conflicting phone numbers
        home_data = PageData(
            url="http://example.com/",
            page_type="home", 
            phone="(503) 555-0000",
            source="heuristic"
        )
        
        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            phone="(503) 555-1234", 
            address="123 Main St",
            hours="Mon-Sun 11am-10pm",
            source="microdata"
        )
        
        aggregator.add_page_data(home_data)
        aggregator.add_page_data(contact_data)
        
        result = aggregator.aggregate()
        
        # Contact page should have priority for contact fields
        assert result.phone == "(503) 555-1234"
    
    def test_merge_menu_items_from_multiple_pages(self):
        """Test merging menu items from multiple pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        # Menu page with some items
        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items={
                "Appetizers": ["Calamari", "Bruschetta"],
                "Entrees": ["Pasta", "Pizza"]
            },
            source="json-ld"
        )
        
        # About page with additional menu info
        about_data = PageData(
            url="http://example.com/about",
            page_type="about",
            menu_items={
                "Appetizers": ["Antipasto"],  # Additional item
                "Desserts": ["Tiramisu", "Gelato"]  # New section
            },
            source="heuristic"
        )
        
        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(about_data)
        
        result = aggregator.aggregate()
        
        # Should merge all menu items
        assert set(result.menu_items["Appetizers"]) == {"Calamari", "Bruschetta", "Antipasto"}
        assert set(result.menu_items["Entrees"]) == {"Pasta", "Pizza"}
        assert set(result.menu_items["Desserts"]) == {"Tiramisu", "Gelato"}
    
    def test_deduplicate_menu_items(self):
        """Test deduplicating menu items across pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        # Two pages with overlapping menu items
        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items={"Appetizers": ["Calamari", "Bruschetta"]},
            source="json-ld"
        )
        
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            menu_items={"Appetizers": ["Calamari", "Antipasto"]},  # Calamari duplicate
            source="heuristic"
        )
        
        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(home_data)
        
        result = aggregator.aggregate()
        
        # Should not have duplicates
        appetizers = result.menu_items["Appetizers"]
        assert appetizers.count("Calamari") == 1
        assert set(appetizers) == {"Calamari", "Bruschetta", "Antipasto"}
    
    def test_track_data_sources_for_audit(self):
        """Test tracking data sources for audit trail."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Restaurant Name",
            source="heuristic"
        )
        
        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items={"Entrees": ["Pasta"]},
            source="json-ld"
        )
        
        aggregator.add_page_data(home_data)
        aggregator.add_page_data(menu_data)
        
        result = aggregator.aggregate()
        
        # Should track all sources used
        assert "heuristic" in result.sources
        assert "json-ld" in result.sources
        assert len(result.sources) == 2
    
    def test_calculate_confidence_from_multiple_sources(self):
        """Test calculating confidence based on multiple sources."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        # High confidence data from structured sources
        json_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Restaurant",
            source="json-ld",
            confidence="high"
        )
        
        microdata = PageData(
            url="http://example.com/contact",
            page_type="contact",
            phone="(503) 555-1234",
            source="microdata",
            confidence="medium"
        )
        
        aggregator.add_page_data(json_data)
        aggregator.add_page_data(microdata)
        
        result = aggregator.aggregate()
        
        # Should have high confidence due to multiple structured sources
        assert result.confidence == "high"
    
    def test_handle_empty_page_data(self):
        """Test handling case where no useful data is found."""
        from src.scraper.data_aggregator import DataAggregator
        
        aggregator = DataAggregator()
        
        result = aggregator.aggregate()
        
        assert result is None or result.name == ""
    
    def test_prioritize_structured_data_sources(self):
        """Test prioritizing structured data sources over heuristic."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        # Heuristic data (lower priority)
        heuristic_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Heuristic Name",
            phone="(000) 000-0000",
            source="heuristic"
        )
        
        # JSON-LD data (higher priority)
        structured_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Structured Name",
            phone="(503) 555-1234",
            source="json-ld"
        )
        
        aggregator.add_page_data(heuristic_data)
        aggregator.add_page_data(structured_data)
        
        result = aggregator.aggregate()
        
        # Should prioritize structured data
        assert result.name == "Structured Name"
        assert result.phone == "(503) 555-1234"
    
    def test_aggregate_social_media_links(self):
        """Test aggregating social media links from multiple pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            social_media=["https://facebook.com/restaurant"],
            source="heuristic"
        )
        
        contact_data = PageData(
            url="http://example.com/contact", 
            page_type="contact",
            social_media=["https://instagram.com/restaurant", "https://twitter.com/restaurant"],
            source="microdata"
        )
        
        aggregator.add_page_data(home_data)
        aggregator.add_page_data(contact_data)
        
        result = aggregator.aggregate()
        
        # Should combine all unique social media links
        expected_links = {
            "https://facebook.com/restaurant",
            "https://instagram.com/restaurant", 
            "https://twitter.com/restaurant"
        }
        assert set(result.social_media) == expected_links
    
    def test_page_type_priority_for_contact_fields(self):
        """Test that contact page has priority for contact-related fields."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        
        aggregator = DataAggregator()
        
        # Multiple pages with contact info
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            phone="(503) 555-0000",
            address="Wrong Address",
            hours="Wrong Hours",
            source="json-ld"  # Higher source priority
        )
        
        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            phone="(503) 555-1234",
            address="123 Main St",
            hours="Mon-Sun 11am-10pm",
            source="heuristic"  # Lower source priority
        )
        
        aggregator.add_page_data(home_data)
        aggregator.add_page_data(contact_data)
        
        result = aggregator.aggregate()
        
        # Contact page should win for contact fields despite lower source priority
        assert result.phone == "(503) 555-1234"
        assert result.address == "123 Main St"
        assert result.hours == "Mon-Sun 11am-10pm"


class TestPageData:
    """Test PageData dataclass for individual page information."""
    
    def test_create_page_data_with_required_fields(self):
        """Test creating PageData with required fields."""
        from src.scraper.data_aggregator import PageData
        
        page_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            source="json-ld"
        )
        
        assert page_data.url == "http://example.com/menu"
        assert page_data.page_type == "menu"
        assert page_data.source == "json-ld"
    
    def test_page_data_with_restaurant_information(self):
        """Test PageData with restaurant information fields."""
        from src.scraper.data_aggregator import PageData
        
        page_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            restaurant_name="Tony's Restaurant",
            phone="(503) 555-1234",
            address="123 Main St",
            hours="Mon-Sun 11am-10pm",
            source="microdata"
        )
        
        assert page_data.restaurant_name == "Tony's Restaurant"
        assert page_data.phone == "(503) 555-1234"
        assert page_data.address == "123 Main St"
        assert page_data.hours == "Mon-Sun 11am-10pm"
    
    def test_page_data_with_menu_items(self):
        """Test PageData with menu items."""
        from src.scraper.data_aggregator import PageData
        
        menu_items = {
            "Appetizers": ["Calamari", "Bruschetta"],
            "Entrees": ["Pasta", "Pizza"]
        }
        
        page_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items=menu_items,
            source="json-ld"
        )
        
        assert page_data.menu_items == menu_items
        assert "Calamari" in page_data.menu_items["Appetizers"]
    
    def test_page_data_to_dict_conversion(self):
        """Test converting PageData to dictionary."""
        from src.scraper.data_aggregator import PageData
        
        page_data = PageData(
            url="http://example.com/about",
            page_type="about",
            restaurant_name="Restaurant Name",
            cuisine="Italian",
            source="heuristic"
        )
        
        data_dict = page_data.to_dict()
        
        assert data_dict["url"] == "http://example.com/about"
        assert data_dict["page_type"] == "about"
        assert data_dict["restaurant_name"] == "Restaurant Name"
        assert data_dict["cuisine"] == "Italian"
        assert data_dict["source"] == "heuristic"