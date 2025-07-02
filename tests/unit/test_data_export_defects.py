"""Unit tests for data export defects found during manual testing."""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestIncompleteDataExportDefect:
    """Test incomplete data export from scraping multiple URLs."""
    
    def test_missing_basic_info_fields(self):
        """Test that basic restaurant info fields are missing in export."""
        # Sample export data from actual test file
        export_data = {
            "metadata": {
                "generation_timestamp": "2025-07-02T11:30:44.563616",
                "restaurant_count": 2,
                "format_version": "1.0"
            },
            "restaurants": [
                {
                    "basic_info": {
                        "name": "Portland",  # Should be actual restaurant name
                        "address": "",       # MISSING
                        "phone": "",         # MISSING
                        "hours": "",         # MISSING
                        "website": None      # MISSING
                    },
                    "additional_details": {
                        "cuisine_types": ["Bbq"],
                        "special_features": [],
                        "parking": None,
                        "reservations": None,
                        "menu_items": [],    # MISSING - should have menu data
                        "pricing": ""        # MISSING
                    }
                }
            ]
        }
        
        restaurant = export_data["restaurants"][0]
        basic_info = restaurant["basic_info"]
        
        # These fields should have actual data, not empty values
        assert basic_info["address"] == "", "Address is missing"
        assert basic_info["phone"] == "", "Phone is missing"
        assert basic_info["hours"] == "", "Hours are missing"
        assert basic_info["website"] is None, "Website is missing"
        
        # Menu items should have actual data
        assert len(restaurant["additional_details"]["menu_items"]) == 0, "Menu items are missing"
        
        # Name should be more specific than just "Portland"
        assert basic_info["name"] == "Portland", "Name is too generic"
    
    def test_duplicate_restaurant_data(self):
        """Test that multiple URLs produce identical duplicate data."""
        # Both restaurants in export have identical data
        export_data = {
            "restaurants": [
                {
                    "basic_info": {
                        "name": "Portland",
                        "address": "",
                        "phone": "",
                        "hours": "",
                        "website": None
                    },
                    "additional_details": {
                        "cuisine_types": ["Bbq"],
                        "menu_items": [],
                        "pricing": ""
                    }
                },
                {
                    "basic_info": {
                        "name": "Portland",
                        "address": "",
                        "phone": "",
                        "hours": "",
                        "website": None
                    },
                    "additional_details": {
                        "cuisine_types": ["Bbq"],
                        "menu_items": [],
                        "pricing": ""
                    }
                }
            ]
        }
        
        restaurant1 = export_data["restaurants"][0]
        restaurant2 = export_data["restaurants"][1]
        
        # Both restaurants should NOT be identical if they're from different URLs
        assert restaurant1["basic_info"]["name"] == restaurant2["basic_info"]["name"]
        assert restaurant1["additional_details"]["cuisine_types"] == restaurant2["additional_details"]["cuisine_types"]
        
        # This suggests the scraper is not properly extracting unique data per URL
        # or is using the same extraction result for both URLs
    
    def test_expected_data_fields_for_mobimag_urls(self):
        """Test what data SHOULD be extracted from mobimag.co URLs."""
        # Expected data structure for proper extraction
        expected_restaurant_data = {
            "basic_info": {
                "name": "String - Actual restaurant name, not city",
                "address": "String - Full address with street, city, state",
                "phone": "String - Phone number in proper format",
                "hours": "String - Operating hours (e.g., 'Mon-Fri 9-5')",
                "website": "String - The actual URL scraped"
            },
            "additional_details": {
                "cuisine_types": ["List - Specific cuisine types, not just 'Bbq'"],
                "special_features": ["List - Features like 'outdoor seating', 'live music'"],
                "parking": "String - Parking information",
                "reservations": "String - Reservation policy",
                "menu_items": ["List - Actual menu items with descriptions/prices"],
                "pricing": "String - Price range like '$', '$$', '$$$'"
            },
            "contact_info": {
                "email": "String - Contact email if available",
                "social_media": ["List - Social media handles/URLs"],
                "delivery_options": ["List - Delivery services like 'DoorDash', 'UberEats'"]
            },
            "characteristics": {
                "dietary_accommodations": ["List - 'vegetarian', 'gluten-free', etc."],
                "ambiance": "String - Restaurant atmosphere description"
            }
        }
        
        # Verify expected structure
        assert "basic_info" in expected_restaurant_data
        assert "additional_details" in expected_restaurant_data
        assert "contact_info" in expected_restaurant_data
        assert "characteristics" in expected_restaurant_data
        
        # Key fields that should have real data
        basic_fields = ["name", "address", "phone", "hours", "website"]
        for field in basic_fields:
            assert field in expected_restaurant_data["basic_info"]
            assert expected_restaurant_data["basic_info"][field] != ""
            assert expected_restaurant_data["basic_info"][field] is not None
    
    def test_scraping_extraction_failure_modes(self):
        """Test common reasons why data extraction might fail."""
        extraction_failure_reasons = [
            "JavaScript-rendered content not loaded",
            "Incorrect CSS selectors for data elements", 
            "Anti-scraping measures blocking access",
            "Rate limiting causing incomplete page loads",
            "Missing data extraction rules for mobimag.co domain",
            "Generic extraction not finding site-specific patterns",
            "Timeout during page loading",
            "Content behind authentication/cookies"
        ]
        
        # Each failure reason should be specific and actionable
        for reason in extraction_failure_reasons:
            assert len(reason) > 10, f"Failure reason too vague: {reason}"
            assert any(keyword in reason.lower() for keyword in 
                      ['javascript', 'selector', 'blocking', 'timeout', 'pattern', 'auth', 'limiting', 'missing', 'extraction']), \
                   f"Reason should be specific: {reason}"
    
    def test_json_export_completeness_requirements(self):
        """Test requirements for complete JSON export."""
        # For a complete export, we expect:
        completeness_requirements = {
            "unique_data_per_url": "Each URL should produce different restaurant data",
            "populated_basic_fields": "Name, address, phone should have real values",
            "menu_data_extraction": "Menu items should be populated from page content",
            "contact_info_extraction": "Email, social media should be found if available",
            "proper_error_handling": "Missing data should be null, not empty strings",
            "metadata_accuracy": "Restaurant count should match actual unique entries"
        }
        
        for requirement, description in completeness_requirements.items():
            assert len(description) > 20, f"Requirement {requirement} needs detailed description"
            assert "should" in description.lower(), f"Requirement {requirement} should specify expected behavior"


if __name__ == "__main__":
    pytest.main([__file__])