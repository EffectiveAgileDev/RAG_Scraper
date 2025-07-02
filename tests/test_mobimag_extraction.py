"""Acceptance tests for mobimag.co restaurant data extraction."""
import pytest
import requests
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
import json
from urllib.parse import unquote

from src.scraper.multi_strategy_scraper import MultiStrategyScraper
from src.scraper.heuristic_extractor import HeuristicExtractor
from src.scraper.javascript_handler import JavaScriptHandler


class TestMobimagExtractionIssues:
    """Test cases for the specific mobimag.co extraction issues."""

    def test_mobimag_urls_return_different_restaurants(self):
        """Test that different mobimag URLs should return different restaurant data."""
        # This test demonstrates the current issue: both URLs return identical data
        
        # Mock the actual mobimag response with the JavaScript pageData
        mock_html = '''
        <!DOCTYPE html>
        <html>
        <head><title>Portland - Where to Eat Guide - Mobimag</title></head>
        <body>
        <script>
        const pageData = JSON.parse(decodeURIComponent("%5B%7B%22name%22%3A%22Kells%20Irish%20Pub%20Downtown%22%2C%22pageID%22%3A%226%22%7D%2C%7B%22name%22%3A%22Mucca%20Osteria%22%2C%22pageID%22%3A%227%22%7D%5D"));
        </script>
        </body>
        </html>
        '''
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = mock_html
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            scraper = MultiStrategyScraper(enable_ethical_scraping=False)
            
            # Test URL ending with /6 should return "Kells Irish Pub Downtown"
            result_6 = scraper.scrape_url('https://mobimag.co/wteg/portland/6')
            
            # Test URL ending with /7 should return "Mucca Osteria"  
            result_7 = scraper.scrape_url('https://mobimag.co/wteg/portland/7')
            
            # Currently this fails because both return the same data
            # After fix, these should be different restaurants
            if result_6 and result_7:
                # This assertion will initially fail, demonstrating the issue
                assert result_6.name != result_7.name, "Different URLs should return different restaurants"
            else:
                pytest.fail("Scraper should extract restaurant data from mobimag URLs")

    def test_javascript_pagedata_extraction(self):
        """Test extraction of restaurant data from JavaScript pageData."""
        
        # Test data mimicking the actual mobimag.co structure
        test_html = '''
        <script>
        const pageData = JSON.parse(decodeURIComponent("%5B%7B%22name%22%3A%22Miss%20Delta%20BBQ%22%2C%22pageID%22%3A%2222%22%2C%22address%22%3A%22123%20Main%20St%22%2C%22phone%22%3A%22555-1234%22%7D%2C%7B%22name%22%3A%22Portland%20Spirit%22%2C%22pageID%22%3A%224%22%2C%22address%22%3A%22456%20River%20Dr%22%2C%22phone%22%3A%22555-5678%22%7D%5D"));
        </script>
        '''
        
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # This tests the new JavaScript extraction logic we need to implement
        extractor = HeuristicExtractor()
        
        # Currently this would not extract the JavaScript data properly
        results = extractor.extract_from_html(test_html)
        
        # After implementing the fix, this should extract restaurant data
        assert len(results) > 0, "Should extract restaurant data from JavaScript pageData"
        
        # Should extract the first restaurant by default or based on URL context
        restaurant = results[0]
        assert restaurant.name in ["Miss Delta BBQ", "Portland Spirit"], f"Should extract valid restaurant name, got: {restaurant.name}"

    def test_url_based_restaurant_selection(self):
        """Test that restaurant selection is based on URL path."""
        
        # Test HTML with multiple restaurants in pageData
        test_html_with_pagedata = '''
        <script>
        const pageData = JSON.parse(decodeURIComponent("%5B%7B%22name%22%3A%22Restaurant%20One%22%2C%22pageID%22%3A%221%22%7D%2C%7B%22name%22%3A%22Restaurant%20Two%22%2C%22pageID%22%3A%222%22%7D%2C%7B%22name%22%3A%22Restaurant%20Three%22%2C%22pageID%22%3A%223%22%7D%5D"));
        </script>
        '''
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = test_html_with_pagedata
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            scraper = MultiStrategyScraper(enable_ethical_scraping=False)
            
            # Test that different URL endings select different restaurants
            result_1 = scraper.scrape_url('https://mobimag.co/wteg/portland/1')
            result_2 = scraper.scrape_url('https://mobimag.co/wteg/portland/2') 
            result_3 = scraper.scrape_url('https://mobimag.co/wteg/portland/3')
            
            # After implementing the fix, each should return the corresponding restaurant
            if result_1:
                assert result_1.name == "Restaurant One", f"URL /1 should return Restaurant One, got: {result_1.name}"
            if result_2:
                assert result_2.name == "Restaurant Two", f"URL /2 should return Restaurant Two, got: {result_2.name}"
            if result_3:
                assert result_3.name == "Restaurant Three", f"URL /3 should return Restaurant Three, got: {result_3.name}"

    def test_missing_data_fields_extraction(self):
        """Test extraction of complete restaurant data fields."""
        
        # Test HTML with complete restaurant data
        test_html = '''
        <script>
        const pageData = JSON.parse(decodeURIComponent("%5B%7B%22name%22%3A%22Test%20Restaurant%22%2C%22address%22%3A%22123%20Test%20St%2C%20Portland%2C%20OR%2097201%22%2C%22phone%22%3A%22%28503%29%20555-1234%22%2C%22hours%22%3A%22Mon-Fri%2011am-10pm%22%2C%22website%22%3A%22https%3A//testrestaurant.com%22%2C%22menu%22%3A%5B%22Burger%22%2C%22Pizza%22%2C%22Salad%22%5D%7D%5D"));
        </script>
        '''
        
        extractor = HeuristicExtractor()
        results = extractor.extract_from_html(test_html)
        
        # After implementing the fix, all fields should be extracted
        assert len(results) > 0, "Should extract restaurant data"
        
        restaurant = results[0]
        assert restaurant.name == "Test Restaurant", f"Expected 'Test Restaurant', got: {restaurant.name}"
        assert restaurant.address == "123 Test St, Portland, OR 97201", f"Expected full address, got: {restaurant.address}"
        assert restaurant.phone == "(503) 555-1234", f"Expected phone number, got: {restaurant.phone}"
        assert restaurant.hours == "Mon-Fri 11am-10pm", f"Expected hours, got: {restaurant.hours}"
        # Menu items should be extracted and structured properly
        assert len(restaurant.menu_items) > 0, "Should extract menu items"

    def test_enhanced_heuristic_extractor_with_javascript(self):
        """Test that enhanced heuristic extractor correctly handles JavaScript data."""
        
        # This is the actual content that mobimag.co returns
        actual_mobimag_html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Portland - Where to Eat Guide - Mobimag</title>
        </head>
        <body>
            <h1>Subscribe Now</h1>
            <script>
            const pageData = JSON.parse(decodeURIComponent("%5B%7B%22name%22%3A%22Miss%20Delta%20BBQ%22%2C%22pageID%22%3A%2222%22%7D%5D"));
            </script>
        </body>
        </html>
        '''
        
        extractor = HeuristicExtractor()
        results = extractor.extract_from_html(actual_mobimag_html)
        
        # After implementing the fix: should correctly extract restaurant data from JavaScript
        assert len(results) > 0, "Should extract restaurant data from JavaScript pageData"
        
        result = results[0]
        # Should now correctly extract the restaurant name from JavaScript
        assert result.name == "Miss Delta BBQ", f"Should extract correct restaurant name, got: {result.name}"
        
        # Confidence should be high for structured JavaScript data
        assert result.confidence == "high", f"JavaScript extraction should have high confidence, got: {result.confidence}"
        
        # Source should still be heuristic
        assert result.source == "heuristic", f"Source should be heuristic, got: {result.source}"


class TestJavaScriptExtractionUtils:
    """Utility functions for JavaScript data extraction."""
    
    def test_pagedata_parsing(self):
        """Test parsing of pageData from JavaScript."""
        
        js_content = '''
        const pageData = JSON.parse(decodeURIComponent("%5B%7B%22name%22%3A%22Test%20Restaurant%22%7D%5D"));
        '''
        
        # Test the utility function we need to implement
        import re
        pattern = r'pageData = JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)'
        match = re.search(pattern, js_content)
        
        assert match is not None, "Should find pageData pattern"
        
        encoded_data = match.group(1)
        decoded_data = unquote(encoded_data)
        page_data = json.loads(decoded_data)
        
        assert isinstance(page_data, list), "pageData should be a list"
        assert len(page_data) == 1, "Should have one restaurant"
        assert page_data[0]["name"] == "Test Restaurant", "Should extract restaurant name"

    def test_url_id_extraction(self):
        """Test extraction of restaurant ID from URL."""
        
        test_urls = [
            "https://mobimag.co/wteg/portland/6",
            "https://mobimag.co/wteg/portland/7",
            "https://mobimag.co/wteg/portland/22"
        ]
        
        for url in test_urls:
            path_parts = url.split('/')
            restaurant_id = path_parts[-1]
            
            assert restaurant_id.isdigit(), f"URL should end with numeric ID, got: {restaurant_id}"
            assert int(restaurant_id) > 0, f"Restaurant ID should be positive number"