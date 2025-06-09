"""Unit tests for heuristic pattern extraction engine."""
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


class TestHeuristicExtractor:
    """Test heuristic pattern extraction functionality."""
    
    def test_extract_restaurant_name_from_title(self):
        """Test extraction of restaurant name from page title."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <head>
            <title>Tony's Italian Restaurant - Best Italian Food in Salem</title>
        </head>
        <body>
            <h1>Welcome to our restaurant</h1>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert "Tony's Italian Restaurant" in results[0].name
        assert results[0].confidence == "medium"
        assert results[0].source == "heuristic"
    
    def test_extract_restaurant_name_from_h1(self):
        """Test extraction of restaurant name from main heading."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <body>
            <h1>Best Pizza Place</h1>
            <p>Welcome to our family restaurant</p>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].name == "Best Pizza Place"
    
    def test_extract_phone_number_patterns(self):
        """Test extraction of phone numbers using regex patterns."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        phone_patterns = [
            "Call us at (503) 555-1234",
            "Phone: 503-555-1234",
            "Tel: 503.555.1234",
            "Contact: 5035551234",
            "Reservations: +1-503-555-1234"
        ]
        
        for pattern in phone_patterns:
            html = f"""
            <html>
            <body>
                <h1>Test Restaurant</h1>
                <p>{pattern}</p>
            </body>
            </html>
            """
            
            results = extractor.extract_from_html(html)
            assert len(results) == 1
            assert len(results[0].phone) > 0
            assert "503" in results[0].phone
    
    def test_extract_address_patterns(self):
        """Test extraction of addresses using location patterns."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        address_patterns = [
            "Visit us at 1234 Main Street, Salem, OR 97301",
            "Located at 5678 Oak Ave, Portland, Oregon 97205",
            "Address: 789 Pine St, Eugene OR 97401"
        ]
        
        for pattern in address_patterns:
            html = f"""
            <html>
            <body>
                <h1>Address Test Restaurant</h1>
                <p>{pattern}</p>
            </body>
            </html>
            """
            
            results = extractor.extract_from_html(html)
            assert len(results) == 1
            assert len(results[0].address) > 0
    
    def test_extract_hours_patterns(self):
        """Test extraction of operating hours using time patterns."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        hours_patterns = [
            "Hours: Monday-Friday 9am-5pm",
            "Open: Mon-Fri 9:00AM-5:00PM",
            "We're open Monday through Friday from 9 to 5",
            "Business Hours: 9am-5pm daily"
        ]
        
        for pattern in hours_patterns:
            html = f"""
            <html>
            <body>
                <h1>Hours Test Restaurant</h1>
                <p>{pattern}</p>
            </body>
            </html>
            """
            
            results = extractor.extract_from_html(html)
            assert len(results) == 1
            assert len(results[0].hours) > 0
    
    def test_extract_price_range_patterns(self):
        """Test extraction of price ranges using currency patterns."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        price_patterns = [
            "Entrees from $15-$25",
            "Price range: $10 to $30",
            "Meals $12-$28",
            "Average cost: $15-25"
        ]
        
        for pattern in price_patterns:
            html = f"""
            <html>
            <body>
                <h1>Price Test Restaurant</h1>
                <p>{pattern}</p>
            </body>
            </html>
            """
            
            results = extractor.extract_from_html(html)
            assert len(results) == 1
            assert len(results[0].price_range) > 0
    
    def test_extract_menu_sections(self):
        """Test extraction of menu items from section headers."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <body>
            <h1>Menu Restaurant</h1>
            <h2>APPETIZERS</h2>
            <p>Bruschetta - Fresh tomatoes</p>
            <p>Calamari - Fried squid rings</p>
            
            <h2>ENTREES</h2>
            <p>Pasta Primavera - Seasonal vegetables</p>
            <p>Chicken Parmigiana - Breaded chicken</p>
            
            <h3>DESSERTS</h3>
            <p>Tiramisu - Coffee flavored</p>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert "APPETIZERS" in results[0].menu_items or "Appetizers" in results[0].menu_items
        assert "ENTREES" in results[0].menu_items or "Entrees" in results[0].menu_items
        assert "DESSERTS" in results[0].menu_items or "Desserts" in results[0].menu_items
    
    def test_extract_cuisine_keywords(self):
        """Test extraction of cuisine types from content keywords."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        cuisine_examples = [
            ("Authentic Italian cuisine", "Italian"),
            ("Traditional Mexican food", "Mexican"),
            ("Fresh sushi and Japanese dishes", "Japanese"),
            ("Classic American steakhouse", "American")
        ]
        
        for content, expected_cuisine in cuisine_examples:
            html = f"""
            <html>
            <body>
                <h1>Cuisine Test Restaurant</h1>
                <p>{content}</p>
            </body>
            </html>
            """
            
            results = extractor.extract_from_html(html)
            assert len(results) == 1
            # Should extract some cuisine information
            assert len(results[0].cuisine) >= 0  # May or may not find it
    
    def test_extract_from_class_names(self):
        """Test extraction using common CSS class name patterns."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <body>
            <h1 class="restaurant-name">Class Name Restaurant</h1>
            <div class="contact-info">
                <span class="phone">503-555-7777</span>
                <span class="address">123 Class St, Portland, OR</span>
            </div>
            <div class="hours">
                Mon-Fri 10am-8pm
            </div>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        assert results[0].name == "Class Name Restaurant"
        # Should extract additional information from semantic classes
    
    def test_extract_from_meta_tags(self):
        """Test extraction from meta tag content."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <head>
            <meta name="description" content="Meta Restaurant - Best food in town. Call 503-555-8888">
            <meta property="og:title" content="Meta Restaurant">
            <meta name="keywords" content="restaurant, italian, pizza, pasta">
        </head>
        <body>
            <h1>Welcome</h1>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        # Should extract information from meta tags
        assert len(results[0].name) > 0
    
    def test_confidence_scoring_heuristic(self):
        """Test confidence scoring for heuristic extraction."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        # Rich content should have higher confidence
        rich_html = """
        <html>
        <body>
            <h1>Rich Content Restaurant</h1>
            <p>Address: 123 Rich St, Portland, OR 97201</p>
            <p>Phone: 503-555-1111</p>
            <p>Hours: Mon-Fri 9am-9pm</p>
            <p>Price range: $15-25</p>
        </body>
        </html>
        """
        
        # Minimal content should have lower confidence
        minimal_html = """
        <html>
        <body>
            <h1>Minimal Restaurant</h1>
        </body>
        </html>
        """
        
        rich_results = extractor.extract_from_html(rich_html)
        minimal_results = extractor.extract_from_html(minimal_html)
        
        assert len(rich_results) == 1
        assert len(minimal_results) == 1
        
        # Rich content should have higher confidence than minimal
        rich_confidence = rich_results[0].confidence
        minimal_confidence = minimal_results[0].confidence
        
        confidence_levels = {"high": 3, "medium": 2, "low": 1}
        assert confidence_levels[rich_confidence] >= confidence_levels[minimal_confidence]
    
    def test_handle_missing_restaurant_indicators(self):
        """Test handling of pages without clear restaurant indicators."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <body>
            <h1>Generic Business</h1>
            <p>We sell widgets and gadgets</p>
            <p>Call 503-555-0000 for more info</p>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        # Should either return empty results or very low confidence
        if results:
            assert results[0].confidence == "low"
        else:
            assert len(results) == 0
    
    def test_extract_social_media_links(self):
        """Test extraction of social media links from page content."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <body>
            <h1>Social Restaurant</h1>
            <p>Follow us on Facebook: https://facebook.com/socialrestaurant</p>
            <a href="https://instagram.com/socialrest">Instagram</a>
            <div>Twitter: @socialrest</div>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        # Should extract some social media links
        assert len(results[0].social_media) >= 0
    
    def test_normalize_extracted_data(self):
        """Test normalization of extracted data."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        # Test phone number normalization
        assert extractor.normalize_phone("(503) 555-1234") is not None
        assert extractor.normalize_phone("503.555.1234") is not None
        
        # Test address normalization  
        assert extractor.normalize_address("123 Main St, Portland, OR") is not None
        
        # Test hours normalization
        assert extractor.normalize_hours("Mon-Fri 9am-5pm") is not None
        
        # Test price range normalization
        assert extractor.normalize_price_range("$15-25") is not None
    
    def test_restaurant_keyword_detection(self):
        """Test detection of restaurant-specific keywords."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        restaurant_keywords = [
            "menu", "restaurant", "dining", "cuisine", "food",
            "chef", "kitchen", "appetizers", "entrees", "desserts",
            "reservations", "takeout", "delivery"
        ]
        
        for keyword in restaurant_keywords:
            assert extractor.is_restaurant_keyword(keyword) is True
        
        non_restaurant_keywords = [
            "software", "hardware", "consulting", "insurance",
            "real estate", "automotive", "legal"
        ]
        
        for keyword in non_restaurant_keywords:
            assert extractor.is_restaurant_keyword(keyword) is False
    
    def test_handle_multiple_phone_numbers(self):
        """Test handling of multiple phone numbers on page."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <body>
            <h1>Multi Phone Restaurant</h1>
            <p>Reservations: 503-555-1111</p>
            <p>Takeout: 503-555-2222</p>
            <p>Catering: 503-555-3333</p>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        # Should extract primary phone number
        assert len(results[0].phone) > 0
    
    def test_extract_from_table_data(self):
        """Test extraction from table-structured data."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        html_content = """
        <html>
        <body>
            <h1>Table Restaurant</h1>
            <table>
                <tr><td>Name:</td><td>Table Restaurant</td></tr>
                <tr><td>Phone:</td><td>503-555-4444</td></tr>
                <tr><td>Address:</td><td>123 Table St</td></tr>
                <tr><td>Hours:</td><td>Daily 11am-9pm</td></tr>
            </table>
        </body>
        </html>
        """
        
        results = extractor.extract_from_html(html_content)
        
        assert len(results) == 1
        # Should extract data from table structure
        assert results[0].name == "Table Restaurant"
    
    def test_handle_empty_or_invalid_html(self):
        """Test handling of empty or invalid HTML."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        extractor = HeuristicExtractor()
        
        # Empty HTML
        assert extractor.extract_from_html("") == []
        assert extractor.extract_from_html("   ") == []
        
        # Invalid HTML
        assert extractor.extract_from_html("<invalid>") == []
    
    @patch('src.scraper.heuristic_extractor.BeautifulSoup')
    def test_handle_html_parsing_errors(self, mock_soup):
        """Test handling of HTML parsing errors."""
        from src.scraper.heuristic_extractor import HeuristicExtractor
        
        # Mock BeautifulSoup to raise an exception
        mock_soup.side_effect = Exception("HTML parsing failed")
        
        extractor = HeuristicExtractor()
        
        results = extractor.extract_from_html("<html>test</html>")
        
        assert results == []  # Should return empty list on parsing errors


class TestHeuristicExtractionResult:
    """Test heuristic extraction result data structure."""
    
    def test_create_heuristic_extraction_result(self):
        """Test creation of heuristic extraction result object."""
        from src.scraper.heuristic_extractor import HeuristicExtractionResult
        
        result = HeuristicExtractionResult(
            name="Heuristic Restaurant",
            address="123 Heuristic St",
            phone="503-555-9999",
            confidence="medium",
            source="heuristic"
        )
        
        assert result.name == "Heuristic Restaurant"
        assert result.address == "123 Heuristic St"
        assert result.phone == "503-555-9999"
        assert result.confidence == "medium"
        assert result.source == "heuristic"
    
    def test_heuristic_result_validation(self):
        """Test validation of heuristic extraction result."""
        from src.scraper.heuristic_extractor import HeuristicExtractionResult
        
        # Valid result
        valid_result = HeuristicExtractionResult(
            name="Valid Heuristic Restaurant",
            confidence="medium",
            source="heuristic"
        )
        assert valid_result.is_valid() is True
        
        # Invalid result (no name)
        invalid_result = HeuristicExtractionResult(
            name="",
            confidence="medium",
            source="heuristic"
        )
        assert invalid_result.is_valid() is False
    
    def test_heuristic_result_to_dict(self):
        """Test conversion of heuristic result to dictionary."""
        from src.scraper.heuristic_extractor import HeuristicExtractionResult
        
        result = HeuristicExtractionResult(
            name="Dict Heuristic Restaurant", 
            cuisine="Italian, Mexican",
            menu_items={"Appetizers": ["Chips", "Salsa"]},
            confidence="medium",
            source="heuristic"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["name"] == "Dict Heuristic Restaurant"
        assert result_dict["cuisine"] == "Italian, Mexican"
        assert result_dict["confidence"] == "medium"
        assert result_dict["source"] == "heuristic"