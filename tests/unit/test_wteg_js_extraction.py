"""Unit tests for WTEG JavaScript data extraction from mobimag.co.

Following TDD approach: Write failing tests first for WTEG-specific extraction.
"""
import pytest
from unittest.mock import patch, Mock
import json
from urllib.parse import quote


class TestWTEGJavaScriptExtraction:
    """Test WTEG-specific JavaScript data extraction for mobimag.co."""
    
    def test_wteg_extractor_exists(self):
        """Test that WTEGExtractor class exists."""
        try:
            from src.wteg.wteg_extractor import WTEGExtractor
            
            extractor = WTEGExtractor()
            assert extractor is not None, "WTEGExtractor should be instantiable"
            
        except ImportError:
            pytest.fail("WTEGExtractor class not implemented yet")
    
    def test_extract_from_mobimag_pagedata(self):
        """Test extraction from mobimag.co pageData JavaScript."""
        try:
            from src.wteg.wteg_extractor import WTEGExtractor
            from src.wteg.wteg_schema import WTEGRestaurantData
            
            extractor = WTEGExtractor()
            
            # Mock HTML with embedded pageData (like actual mobimag.co)
            sample_pagedata = [
                {
                    "name": "Canard",
                    "pageID": "21",
                    "location": "1420 SE Stark St, Portland, OR 97214",
                    "cuisine": "French Bistro",
                    "description": "Authentic French bistro featuring house-made charcuterie and seasonal menu",
                    "phone": "(503) 555-0121",
                    "website": "https://canardpdx.com",
                    "menu": ["Duck Confit - $28", "Escargot - $14", "French Onion Soup - $12"]
                },
                {
                    "name": "Mamma Khouri's", 
                    "pageID": "16",
                    "location": "4500 SE Hawthorne Blvd, Portland, OR 97215",
                    "cuisine": "Lebanese",
                    "description": "Family-owned Lebanese restaurant serving traditional Middle Eastern cuisine",
                    "phone": "(503) 555-0116",
                    "website": "https://mammakhouri.com",
                    "menu": ["Hummus Plate - $12", "Lamb Shawarma - $18", "Baklava - $6"]
                }
            ]
            
            encoded_data = quote(json.dumps(sample_pagedata))
            mock_html = f'''
            <html>
            <head><title>Portland - Where to Eat Guide</title></head>
            <body>
            <script>
            const pageData = JSON.parse(decodeURIComponent("{encoded_data}"));
            </script>
            </body>
            </html>
            '''
            
            # Test extraction for page 21 (Canard)
            result = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/21")
            
            assert result is not None, "Should extract WTEG data"
            assert isinstance(result, WTEGRestaurantData), "Should return WTEGRestaurantData instance"
            assert result.brief_description == "Authentic French bistro featuring house-made charcuterie and seasonal menu"
            assert result.cuisine == "French Bistro"
            assert result.click_to_call.primary_phone == "(503) 555-0121"
            
        except ImportError:
            pytest.fail("WTEG extraction not implemented yet")
    
    def test_url_based_restaurant_selection(self):
        """Test that correct restaurant is selected based on URL."""
        try:
            from src.wteg.wteg_extractor import WTEGExtractor
            
            extractor = WTEGExtractor()
            
            # Sample data with multiple restaurants
            sample_pagedata = [
                {"name": "Restaurant A", "pageID": "1"},
                {"name": "Restaurant B", "pageID": "2"}, 
                {"name": "Restaurant C", "pageID": "3"}
            ]
            
            encoded_data = quote(json.dumps(sample_pagedata))
            mock_html = f'''
            <script>
            const pageData = JSON.parse(decodeURIComponent("{encoded_data}"));
            </script>
            '''
            
            # Test URL-based selection
            result_1 = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/1")
            result_2 = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/2")
            result_3 = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/3")
            
            # Should extract different restaurants based on URL
            assert result_1.brief_description != result_2.brief_description, "Should extract different restaurants"
            assert result_2.brief_description != result_3.brief_description, "Should extract different restaurants"
            
            # Should match expected restaurants by pageID
            restaurant_1_name = self._extract_name_from_description(result_1.brief_description)
            restaurant_2_name = self._extract_name_from_description(result_2.brief_description)
            
            assert "Restaurant A" in restaurant_1_name or result_1.brief_description == "Restaurant A"
            assert "Restaurant B" in restaurant_2_name or result_2.brief_description == "Restaurant B"
            
        except ImportError:
            pytest.fail("URL-based restaurant selection not implemented yet")
    
    def test_complete_wteg_field_mapping(self):
        """Test mapping of all WTEG fields from JavaScript data."""
        try:
            from src.wteg.wteg_extractor import WTEGExtractor
            
            extractor = WTEGExtractor()
            
            # Complete restaurant data
            complete_restaurant = {
                "name": "Test Restaurant",
                "pageID": "1",
                "location": "123 Test St, Portland, OR 97201",
                "cuisine": "Test Cuisine",
                "description": "Test restaurant description",
                "phone": "(503) 555-0100",
                "website": "https://testrestaurant.com",
                "menu": ["Item 1 - $10", "Item 2 - $15"],
                "services": {
                    "delivery": True,
                    "takeout": True,
                    "catering": False,
                    "reservations": True
                },
                "onlineOrdering": [
                    {
                        "platform": "DoorDash",
                        "url": "https://doordash.com/restaurant/test",
                        "fee": "$2.99"
                    }
                ],
                "social": ["https://facebook.com/testrestaurant"],
                "mapUrl": "https://maps.google.com/test"
            }
            
            encoded_data = quote(json.dumps([complete_restaurant]))
            mock_html = f'''
            <script>
            const pageData = JSON.parse(decodeURIComponent("{encoded_data}"));
            </script>
            '''
            
            result = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/1")
            
            # Verify all WTEG fields are mapped
            assert result.brief_description == "Test restaurant description"
            assert result.cuisine == "Test Cuisine"
            assert result.location.street_address == "123 Test St"
            assert result.location.city == "Portland"
            assert result.location.state == "OR"
            assert result.click_to_call.primary_phone == "(503) 555-0100"
            assert result.click_for_website.official_website == "https://testrestaurant.com"
            assert result.services_offered.delivery_available == True
            assert result.services_offered.takeout_available == True
            assert result.services_offered.reservations_accepted == True
            assert len(result.click_to_link) == 1
            assert result.click_to_link[0].platform_name == "DoorDash"
            
        except ImportError:
            pytest.fail("Complete field mapping not implemented yet")
    
    def test_raw_data_preservation(self):
        """Test that raw data is preserved without AI interpretation."""
        try:
            from src.wteg.wteg_extractor import WTEGExtractor
            
            extractor = WTEGExtractor()
            
            # Raw data with specific wording
            raw_restaurant = {
                "name": "Raw Data Restaurant",
                "description": "Exactly this text should be preserved without modification",
                "menu": ["Specific Menu Item Name - $19.99"],
                "phone": "(503) 555-1234",
                "pageID": "1"
            }
            
            encoded_data = quote(json.dumps([raw_restaurant]))
            mock_html = f'''
            <script>
            const pageData = JSON.parse(decodeURIComponent("{encoded_data}"));
            </script>
            '''
            
            result = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/1")
            
            # Verify exact text preservation
            assert result.brief_description == "Exactly this text should be preserved without modification"
            assert result.click_to_call.primary_phone == "(503) 555-1234"
            assert len(result.menu_items) >= 1
            
            # Should not have AI-enhanced fields
            assert not hasattr(result, 'ai_enhanced_description')
            assert not hasattr(result, 'ai_sentiment_score')
            assert result.extraction_method == "wteg_specific"
            
        except ImportError:
            pytest.fail("Raw data preservation not implemented yet")
    
    def test_client_critical_urls_extraction(self):
        """Test extraction from client's critical URLs (21 and 16)."""
        try:
            from src.wteg.wteg_extractor import WTEGExtractor
            
            extractor = WTEGExtractor()
            
            # Simulate the exact scenario from client's failing test
            client_pagedata = [
                {
                    "name": "Canard", 
                    "pageID": "21",
                    "location": "Southeast Portland",
                    "cuisine": "French",
                    "description": "French restaurant specializing in charcuterie",
                    "phone": "(503) 555-0021",
                    "menu": ["Duck Confit", "Pâté", "French Bread"]
                },
                {
                    "name": "Mamma Khouri's",
                    "pageID": "16", 
                    "location": "Hawthorne District",
                    "cuisine": "Lebanese",
                    "description": "Authentic Lebanese family restaurant",
                    "phone": "(503) 555-0016",
                    "menu": ["Hummus", "Falafel", "Shawarma"]
                }
            ]
            
            encoded_data = quote(json.dumps(client_pagedata))
            mock_html = f'''
            <script>
            const pageData = JSON.parse(decodeURIComponent("{encoded_data}"));
            </script>
            '''
            
            # Test both critical URLs
            result_21 = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/21")
            result_16 = extractor.extract_wteg_data(mock_html, "https://mobimag.co/wteg/portland/16")
            
            # These should NOT be empty like in the failing export
            assert result_21.brief_description != "", "Description should not be empty"
            assert result_21.click_to_call.primary_phone != "", "Phone should not be empty"
            assert len(result_21.menu_items) > 0, "Menu items should not be empty"
            
            assert result_16.brief_description != "", "Description should not be empty"
            assert result_16.click_to_call.primary_phone != "", "Phone should not be empty"
            assert len(result_16.menu_items) > 0, "Menu items should not be empty"
            
            # Should be different restaurants
            assert result_21.brief_description != result_16.brief_description
            assert result_21.cuisine != result_16.cuisine
            
        except ImportError:
            pytest.fail("Client critical URL extraction not implemented yet")
    
    def test_extraction_confidence_scoring(self):
        """Test confidence scoring for WTEG extraction."""
        try:
            from src.wteg.wteg_extractor import WTEGExtractor
            
            extractor = WTEGExtractor()
            
            # Complete data should have high confidence
            complete_data = {
                "name": "Complete Restaurant",
                "pageID": "1",
                "location": "Full address",
                "cuisine": "Known cuisine",
                "description": "Complete description",
                "phone": "(503) 555-0100",
                "website": "https://example.com",
                "menu": ["Item 1", "Item 2"]
            }
            
            # Minimal data should have lower confidence
            minimal_data = {
                "name": "Minimal Restaurant",
                "pageID": "2"
            }
            
            for restaurant_data in [complete_data, minimal_data]:
                encoded_data = quote(json.dumps([restaurant_data]))
                mock_html = f'''
                <script>
                const pageData = JSON.parse(decodeURIComponent("{encoded_data}"));
                </script>
                '''
                
                result = extractor.extract_wteg_data(mock_html, f"https://mobimag.co/wteg/portland/{restaurant_data['pageID']}")
                
                # Should have confidence score
                assert hasattr(result, 'confidence_score'), "Should have confidence score"
                assert 0.0 <= result.confidence_score <= 1.0, "Confidence should be between 0 and 1"
            
            # Complete data should have higher confidence than minimal
            complete_result = extractor.extract_wteg_data(
                f'<script>const pageData = JSON.parse(decodeURIComponent("{quote(json.dumps([complete_data]))}"));</script>',
                "https://mobimag.co/wteg/portland/1"
            )
            minimal_result = extractor.extract_wteg_data(
                f'<script>const pageData = JSON.parse(decodeURIComponent("{quote(json.dumps([minimal_data]))}"));</script>',
                "https://mobimag.co/wteg/portland/2"
            )
            
            assert complete_result.confidence_score > minimal_result.confidence_score, "Complete data should have higher confidence"
            
        except ImportError:
            pytest.fail("Confidence scoring not implemented yet")
    
    def _extract_name_from_description(self, description: str) -> str:
        """Helper method to extract restaurant name from description."""
        # Simple extraction for testing
        return description.split(' ')[0] if description else ""


if __name__ == "__main__":
    pytest.main([__file__])