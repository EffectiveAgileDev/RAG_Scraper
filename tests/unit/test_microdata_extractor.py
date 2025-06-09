"""Unit tests for microdata extraction engine."""
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


class TestMicrodataExtractor:
    """Test microdata structured data extraction functionality."""
    
    def test_extract_restaurant_from_microdata_html(self):
        """Test extraction from HTML with microdata markup."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <h1 itemprop="name">Tony's Italian Restaurant</h1>
            <div itemprop="address" itemscope itemtype="http://schema.org/PostalAddress">
                <span itemprop="streetAddress">1234 Commercial Street</span>
                <span itemprop="addressLocality">Salem</span>
                <span itemprop="addressRegion">OR</span>
                <span itemprop="postalCode">97301</span>
            </div>
            <span itemprop="telephone">(503) 555-0123</span>
            <span itemprop="priceRange">$18-$32</span>
            <span itemprop="servesCuisine">Italian</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        result = results[0]
        assert result.name == "Tony's Italian Restaurant"
        assert result.address == "1234 Commercial Street, Salem, OR 97301"
        assert result.phone == "(503) 555-0123"
        assert result.price_range == "$18-$32"
        assert result.cuisine == "Italian"
        assert result.confidence == "high"
        assert result.source == "microdata"
    
    def test_extract_multiple_restaurants_from_microdata(self):
        """Test extraction of multiple restaurants from microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div>
            <div itemscope itemtype="http://schema.org/Restaurant">
                <h2 itemprop="name">First Restaurant</h2>
                <span itemprop="telephone">503-555-1111</span>
            </div>
            <div itemscope itemtype="http://schema.org/Restaurant">
                <h2 itemprop="name">Second Restaurant</h2>
                <span itemprop="telephone">503-555-2222</span>
            </div>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 2
        assert results[0].name == "First Restaurant"
        assert results[0].phone == "503-555-1111"
        assert results[1].name == "Second Restaurant" 
        assert results[1].phone == "503-555-2222"
    
    def test_extract_foodestablishment_type(self):
        """Test extraction from FoodEstablishment itemtype."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/FoodEstablishment">
            <h1 itemprop="name">Food Place</h1>
            <span itemprop="telephone">503-555-5555</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].name == "Food Place"
        assert results[0].phone == "503-555-5555"
    
    def test_extract_localbusiness_type(self):
        """Test extraction from LocalBusiness itemtype."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/LocalBusiness">
            <span itemprop="name">Local Eatery</span>
            <span itemprop="telephone">503-555-7777</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].name == "Local Eatery"
        assert results[0].phone == "503-555-7777"
    
    def test_ignore_irrelevant_itemtypes(self):
        """Test ignoring of irrelevant schema.org types."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div>
            <div itemscope itemtype="http://schema.org/Person">
                <span itemprop="name">John Doe</span>
            </div>
            <div itemscope itemtype="http://schema.org/Organization">
                <span itemprop="name">Some Company</span>
            </div>
            <div itemscope itemtype="http://schema.org/Restaurant">
                <span itemprop="name">Real Restaurant</span>
            </div>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].name == "Real Restaurant"
    
    def test_extract_opening_hours_microdata(self):
        """Test extraction of opening hours from microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Hours Restaurant</span>
            <span itemprop="openingHours">Mo-Fr 09:00-17:00</span>
            <span itemprop="openingHours">Sa 10:00-16:00</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert "Mo-Fr 09:00-17:00" in results[0].hours
        assert "Sa 10:00-16:00" in results[0].hours
    
    def test_extract_nested_address_microdata(self):
        """Test extraction of nested address microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Address Restaurant</span>
            <div itemprop="address" itemscope itemtype="http://schema.org/PostalAddress">
                <span itemprop="streetAddress">789 Oak Street</span>
                <span itemprop="addressLocality">Portland</span>
                <span itemprop="addressRegion">Oregon</span>
                <span itemprop="postalCode">97205</span>
            </div>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].address == "789 Oak Street, Portland, Oregon 97205"
    
    def test_extract_simple_address_microdata(self):
        """Test extraction of simple address string in microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Simple Address Restaurant</span>
            <span itemprop="address">456 Main St, Eugene, OR 97401</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].address == "456 Main St, Eugene, OR 97401"
    
    def test_extract_menu_microdata(self):
        """Test extraction of menu items from microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Menu Restaurant</span>
            <div itemprop="hasMenu" itemscope itemtype="http://schema.org/Menu">
                <div itemprop="hasMenuSection" itemscope itemtype="http://schema.org/MenuSection">
                    <span itemprop="name">Appetizers</span>
                    <div itemprop="hasMenuItem" itemscope itemtype="http://schema.org/MenuItem">
                        <span itemprop="name">Calamari</span>
                    </div>
                    <div itemprop="hasMenuItem" itemscope itemtype="http://schema.org/MenuItem">
                        <span itemprop="name">Bruschetta</span>
                    </div>
                </div>
            </div>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert "Appetizers" in results[0].menu_items
        assert "Calamari" in results[0].menu_items["Appetizers"]
        assert "Bruschetta" in results[0].menu_items["Appetizers"]
    
    def test_extract_cuisine_types_microdata(self):
        """Test extraction of multiple cuisine types from microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Multi Cuisine Restaurant</span>
            <span itemprop="servesCuisine">Italian</span>
            <span itemprop="servesCuisine">Mediterranean</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert "Italian" in results[0].cuisine
        assert "Mediterranean" in results[0].cuisine
    
    def test_handle_missing_required_fields(self):
        """Test handling of microdata with missing required fields."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="telephone">503-555-9999</span>
            <!-- Missing name field -->
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 0  # Should not extract without name
    
    def test_handle_malformed_microdata_html(self):
        """Test handling of malformed HTML with microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Broken HTML Restaurant
            <!-- Unclosed tags and broken structure -->
            <span itemprop="telephone">503-555-0000
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        # Should handle gracefully and extract what it can
        assert len(results) >= 0  # At minimum should not crash
    
    def test_extract_confidence_scoring(self):
        """Test confidence scoring based on microdata completeness."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        # Complete microdata should have high confidence
        complete_html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Complete Restaurant</span>
            <span itemprop="address">123 Complete St</span>
            <span itemprop="telephone">503-555-1234</span>
            <span itemprop="openingHours">Mo-Fr 09:00-17:00</span>
            <span itemprop="priceRange">$15-$25</span>
        </div>
        """
        
        # Minimal microdata should have lower confidence
        minimal_html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Minimal Restaurant</span>
        </div>
        """
        
        complete_results = extractor.extract_from_html(complete_html)
        minimal_results = extractor.extract_from_html(minimal_html)
        
        assert len(complete_results) == 1
        assert len(minimal_results) == 1
        assert complete_results[0].confidence == "high"
        assert minimal_results[0].confidence in ["medium", "low"]
    
    def test_normalize_phone_numbers(self):
        """Test phone number normalization from microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        phone_formats = [
            "(503) 555-1234",
            "503-555-1234", 
            "503.555.1234",
            "5035551234",
            "+1-503-555-1234"
        ]
        
        for phone in phone_formats:
            html = f"""
            <div itemscope itemtype="http://schema.org/Restaurant">
                <span itemprop="name">Phone Test Restaurant</span>
                <span itemprop="telephone">{phone}</span>
            </div>
            """
            
            results = extractor.extract_from_html(html)
            assert len(results) == 1
            # Should extract some form of the phone number
            assert len(results[0].phone) > 0
    
    def test_extract_social_media_sameas(self):
        """Test extraction of social media links from sameAs microdata."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Social Restaurant</span>
            <link itemprop="sameAs" href="https://www.facebook.com/socialrestaurant">
            <link itemprop="sameAs" href="https://www.instagram.com/socialrestaurant">
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert len(results[0].social_media) == 2
        assert any("facebook" in url for url in results[0].social_media)
        assert any("instagram" in url for url in results[0].social_media)
    
    def test_filter_relevant_itemtypes(self):
        """Test filtering to only relevant schema.org types."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        relevant_types = [
            "http://schema.org/Restaurant",
            "http://schema.org/FoodEstablishment", 
            "http://schema.org/LocalBusiness",
            "https://schema.org/Restaurant"  # HTTPS variant
        ]
        
        irrelevant_types = [
            "http://schema.org/Person",
            "http://schema.org/Organization",
            "http://schema.org/Article"
        ]
        
        for item_type in relevant_types:
            assert extractor.is_relevant_itemtype(item_type) is True
        
        for item_type in irrelevant_types:
            assert extractor.is_relevant_itemtype(item_type) is False
    
    def test_handle_empty_html(self):
        """Test handling of empty HTML."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        results = extractor.extract_from_html("")
        assert results == []
        
        results = extractor.extract_from_html("<html></html>")
        assert results == []
    
    @patch('src.scraper.microdata_extractor.BeautifulSoup')
    def test_handle_html_parsing_errors(self, mock_soup):
        """Test handling of HTML parsing errors."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        # Mock BeautifulSoup to raise an exception
        mock_soup.side_effect = Exception("HTML parsing failed")
        
        extractor = MicrodataExtractor()
        
        results = extractor.extract_from_html("<html>test</html>")
        
        assert results == []  # Should return empty list on parsing errors


class TestMicrodataExtractionResult:
    """Test microdata extraction result data structure."""
    
    def test_create_microdata_extraction_result(self):
        """Test creation of microdata extraction result object."""
        from src.scraper.microdata_extractor import MicrodataExtractionResult
        
        result = MicrodataExtractionResult(
            name="Test Restaurant",
            address="123 Test St, Test City, OR 97000",
            phone="503-555-0000",
            confidence="high",
            source="microdata"
        )
        
        assert result.name == "Test Restaurant"
        assert result.address == "123 Test St, Test City, OR 97000"
        assert result.phone == "503-555-0000"
        assert result.confidence == "high"
        assert result.source == "microdata"
    
    def test_microdata_result_validation(self):
        """Test validation of microdata extraction result."""
        from src.scraper.microdata_extractor import MicrodataExtractionResult
        
        # Valid result
        valid_result = MicrodataExtractionResult(
            name="Valid Restaurant",
            confidence="high",
            source="microdata"
        )
        assert valid_result.is_valid() is True
        
        # Invalid result (no name)
        invalid_result = MicrodataExtractionResult(
            name="",
            confidence="high", 
            source="microdata"
        )
        assert invalid_result.is_valid() is False
    
    def test_microdata_result_to_dict(self):
        """Test conversion of microdata result to dictionary."""
        from src.scraper.microdata_extractor import MicrodataExtractionResult
        
        result = MicrodataExtractionResult(
            name="Dict Restaurant",
            hours="Mo-Fr 09:00-17:00",
            menu_items={"Appetizers": ["Soup", "Salad"]},
            confidence="medium",
            source="microdata"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["name"] == "Dict Restaurant"
        assert result_dict["hours"] == "Mo-Fr 09:00-17:00"
        assert result_dict["menu_items"]["Appetizers"] == ["Soup", "Salad"]
        assert result_dict["confidence"] == "medium"
        assert result_dict["source"] == "microdata"


class TestMicrodataErrorHandling:
    """Test error handling in microdata extraction."""
    
    def test_handle_invalid_itemtype_urls(self):
        """Test handling of invalid itemtype URLs."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="invalid-url">
            <span itemprop="name">Invalid Type Restaurant</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 0  # Should ignore invalid itemtypes
    
    def test_handle_missing_itemscope(self):
        """Test handling of itemprop without itemscope."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div>
            <span itemprop="name">No Itemscope Restaurant</span>
            <span itemprop="telephone">503-555-0000</span>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 0  # Should require itemscope for valid microdata
    
    def test_handle_deeply_nested_microdata(self):
        """Test handling of deeply nested microdata structures."""
        from src.scraper.microdata_extractor import MicrodataExtractor
        
        extractor = MicrodataExtractor()
        
        html_content = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <div>
                <div>
                    <span itemprop="name">Nested Restaurant</span>
                    <div>
                        <span itemprop="telephone">503-555-1111</span>
                    </div>
                </div>
            </div>
        </div>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].name == "Nested Restaurant"
        assert results[0].phone == "503-555-1111"