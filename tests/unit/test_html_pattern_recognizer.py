"""Unit tests for HTML pattern recognizer."""

import pytest
from unittest.mock import Mock, patch

# Import the modules we'll be testing
try:
    from src.processors.html_pattern_recognizer import HTMLPatternRecognizer, HTMLPatternResult
except ImportError:
    HTMLPatternRecognizer = None
    HTMLPatternResult = None


class TestHTMLPatternRecognizer:
    """Test cases for HTMLPatternRecognizer."""

    @pytest.fixture
    def sample_restaurant_html_text(self):
        """Sample restaurant HTML text for testing."""
        return """
        MARIO'S ITALIAN RESTAURANT
        
        123 Main Street
        Portland, OR 97201
        Phone: (503) 555-0123
        Email: info@marios.com
        Website: www.marios.com
        
        APPETIZERS
        Bruschetta - $8.99
        Garlic Bread - $5.99
        Calamari Rings - $12.99
        
        MAIN COURSES
        Spaghetti Carbonara - $16.99
        Chicken Parmigiana - $18.99
        Lasagna - $15.99
        
        DESSERTS
        Tiramisu - $7.99
        Gelato - $5.99
        
        HOURS
        Monday-Thursday: 11:00 AM - 9:00 PM
        Friday-Saturday: 11:00 AM - 10:00 PM
        Sunday: 12:00 PM - 8:00 PM
        
        SERVICES
        Delivery Available
        Takeout Available
        Catering Available
        Reservations Accepted
        Dine-in Available
        
        Authentic Italian cuisine
        4.5 stars rating
        """

    @pytest.fixture
    def varied_format_html_text(self):
        """HTML text with varied formatting patterns."""
        return """
        Best Pizza Place Ever!
        
        Location: 789 Pine St, Denver, CO 80202
        Call us: 303.555.0789
        Website: www.bestpizza.com
        Email: orders@bestpizza.com
        
        Menu Items:
        * Margherita Pizza $12.00
        * Pepperoni Special $14.50
        * Veggie Delight $13.25
        * Caesar Salad $8.99
        
        We're open every day!
        Mon-Fri: 10am-11pm
        Sat-Sun: 11am-12am
        
        Services:
        Online Ordering Available
        Curbside Pickup
        Outdoor Seating
        Private Dining
        
        Follow us: @bestpizza
        Facebook: facebook.com/bestpizza
        """

    @pytest.fixture
    def html_pattern_recognizer(self):
        """Create HTMLPatternRecognizer instance."""
        if HTMLPatternRecognizer is None:
            pytest.skip("HTMLPatternRecognizer not implemented yet")
        return HTMLPatternRecognizer()

    def test_html_pattern_recognizer_initialization(self):
        """Test HTMLPatternRecognizer initializes correctly."""
        if HTMLPatternRecognizer is None:
            pytest.skip("HTMLPatternRecognizer not implemented yet")
        
        recognizer = HTMLPatternRecognizer()
        assert recognizer is not None
        assert hasattr(recognizer, 'recognize_patterns')
        assert hasattr(recognizer, 'get_supported_patterns')
        assert recognizer.patterns is not None

    def test_get_supported_patterns(self, html_pattern_recognizer):
        """Test getting supported pattern types."""
        patterns = html_pattern_recognizer.get_supported_patterns()
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert 'restaurant_name' in patterns
        assert 'address' in patterns
        assert 'phone' in patterns
        assert 'email' in patterns
        assert 'website' in patterns
        assert 'menu_item' in patterns
        assert 'service' in patterns
        assert 'cuisine' in patterns

    def test_recognize_restaurant_name_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of restaurant name patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'restaurant_name' in result
        assert "MARIO'S ITALIAN RESTAURANT" in result['restaurant_name']

    def test_recognize_address_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of address patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'address' in result
        assert "123 Main Street" in result['address']
        assert "Portland, OR 97201" in result['address']

    def test_recognize_phone_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of phone patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'phone' in result
        assert "(503) 555-0123" in result['phone']

    def test_recognize_email_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of email patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'email' in result
        assert "info@marios.com" in result['email']

    def test_recognize_website_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of website patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'website' in result
        assert "www.marios.com" in result['website']

    def test_recognize_price_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of price patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'prices' in result
        prices = result['prices']
        assert "$8.99" in prices
        assert "$16.99" in prices
        assert "$7.99" in prices

    def test_recognize_menu_item_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of menu item patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'menu_items' in result
        menu_items = result['menu_items']
        assert any("Bruschetta" in item for item in menu_items)
        assert any("Spaghetti Carbonara" in item for item in menu_items)
        assert any("Tiramisu" in item for item in menu_items)

    def test_recognize_hours_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of hours patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'hours' in result
        hours = result['hours']
        assert "Monday-Thursday: 11:00 AM - 9:00 PM" in hours

    def test_recognize_service_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of service patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'services' in result
        services = result['services']
        assert any("Delivery Available" in service for service in services)
        assert any("Takeout Available" in service for service in services)
        assert any("Catering Available" in service for service in services)

    def test_recognize_menu_section_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of menu section patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'menu_sections' in result
        sections = result['menu_sections']
        assert "APPETIZERS" in sections
        assert "MAIN COURSES" in sections
        assert "DESSERTS" in sections

    def test_recognize_cuisine_type_patterns(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test recognition of cuisine type patterns."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'cuisine_type' in result
        cuisine = result['cuisine_type']
        assert "Italian" in cuisine

    def test_recognize_social_media_patterns(self, html_pattern_recognizer, varied_format_html_text):
        """Test recognition of social media patterns."""
        result = html_pattern_recognizer.recognize_patterns(varied_format_html_text)
        
        assert 'social_media' in result
        social_media = result['social_media']
        assert any("@bestpizza" in social for social in social_media)
        assert any("facebook.com/bestpizza" in social for social in social_media)

    def test_recognize_bullet_point_menu_items(self, html_pattern_recognizer, varied_format_html_text):
        """Test recognition of bullet point menu items."""
        result = html_pattern_recognizer.recognize_patterns(varied_format_html_text)
        
        assert 'menu_items' in result
        menu_items = result['menu_items']
        assert any("Margherita Pizza" in item for item in menu_items)
        assert any("Pepperoni Special" in item for item in menu_items)
        assert any("Veggie Delight" in item for item in menu_items)

    def test_recognize_alternative_hours_format(self, html_pattern_recognizer, varied_format_html_text):
        """Test recognition of alternative hours format."""
        result = html_pattern_recognizer.recognize_patterns(varied_format_html_text)
        
        assert 'hours' in result
        # Should extract hours information even if format is different
        assert result['hours'] != ""

    def test_recognize_varied_format_patterns(self, html_pattern_recognizer, varied_format_html_text):
        """Test recognition of varied format patterns."""
        result = html_pattern_recognizer.recognize_patterns(varied_format_html_text)
        
        assert 'restaurant_name' in result
        assert 'address' in result
        assert 'phone' in result
        assert 'website' in result
        
        # Should handle varied formats
        assert "Best Pizza Place Ever" in result['restaurant_name']
        assert "789 Pine St" in result['address']
        assert "303.555.0789" in result['phone']
        assert "www.bestpizza.com" in result['website']

    def test_extract_review_scores(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test extraction of review scores."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'review_scores' in result
        scores = result['review_scores']
        assert "4.5" in scores

    def test_extract_business_hours_context(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test extraction of business hours context."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'business_hours_context' in result
        context = result['business_hours_context']
        assert "HOURS" in context

    def test_extract_contact_context(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test extraction of contact context."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'contact_context' in result
        # Should extract lines with contact-related keywords

    def test_pattern_confidence_scoring(self, html_pattern_recognizer, sample_restaurant_html_text):
        """Test pattern confidence scoring."""
        result = html_pattern_recognizer.recognize_patterns(sample_restaurant_html_text)
        
        assert 'confidence_scores' in result
        scores = result['confidence_scores']
        
        # High confidence patterns should score higher
        assert scores.get('restaurant_name', 0) > 0.8
        assert scores.get('address', 0) > 0.8
        assert scores.get('phone', 0) > 0.8
        assert scores.get('email', 0) > 0.8

    def test_handle_empty_text(self, html_pattern_recognizer):
        """Test handling of empty text input."""
        result = html_pattern_recognizer.recognize_patterns("")
        
        assert isinstance(result, dict)
        # Should return empty results for missing patterns
        assert result.get('restaurant_name', "") == ""
        assert result.get('address', "") == ""
        assert result.get('phone', "") == ""

    def test_handle_malformed_text(self, html_pattern_recognizer):
        """Test handling of malformed text input."""
        malformed_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        result = html_pattern_recognizer.recognize_patterns(malformed_text)
        
        assert isinstance(result, dict)
        # Should handle malformed input gracefully
        assert result.get('restaurant_name', "") == ""
        assert result.get('address', "") == ""

    def test_extract_dietary_info_patterns(self, html_pattern_recognizer):
        """Test extraction of dietary information patterns."""
        text_with_dietary = """
        MARIO'S ITALIAN RESTAURANT
        
        We offer Vegan options
        Gluten-Free pasta available
        Vegetarian friendly menu
        Organic ingredients
        """
        
        result = html_pattern_recognizer.recognize_patterns(text_with_dietary)
        
        assert 'dietary_info' in result
        dietary_info = result['dietary_info']
        assert "Vegan" in dietary_info
        assert "Gluten-Free" in dietary_info or "Gluten" in dietary_info
        assert "Vegetarian" in dietary_info
        assert "Organic" in dietary_info

    def test_extract_location_details(self, html_pattern_recognizer):
        """Test extraction of detailed location information."""
        text_with_location = """
        Downtown Location
        123 Main Street
        Suite 456
        Portland, OR 97201
        Near Pioneer Square
        """
        
        result = html_pattern_recognizer.recognize_patterns(text_with_location)
        
        assert 'location_details' in result
        location = result['location_details']
        assert "Downtown Location" in location
        assert "Suite 456" in location
        assert "Near Pioneer Square" in location

    def test_extract_price_ranges(self, html_pattern_recognizer):
        """Test extraction of price ranges."""
        text_with_price_ranges = """
        MARIO'S ITALIAN RESTAURANT
        
        Appetizers: $5.99 - $12.99
        Main Courses: $15.99 - $24.99
        Desserts: $6.99 - $9.99
        """
        
        result = html_pattern_recognizer.recognize_patterns(text_with_price_ranges)
        
        assert 'price_ranges' in result
        price_ranges = result['price_ranges']
        assert "$5.99 - $12.99" in price_ranges
        assert "$15.99 - $24.99" in price_ranges

    def test_normalize_phone_numbers(self, html_pattern_recognizer):
        """Test normalization of phone numbers."""
        text_with_multiple_phones = """
        Restaurant Phone: (503) 555-0123
        Delivery: 303.555.0789
        Manager: +1-206-555-0456
        """
        
        result = html_pattern_recognizer.recognize_patterns(text_with_multiple_phones)
        
        assert 'phone' in result
        # Should handle multiple phone formats
        phone = result['phone']
        assert "(503) 555-0123" in phone or "303.555.0789" in phone

    def test_html_pattern_result_object(self):
        """Test HTMLPatternResult object structure."""
        if HTMLPatternResult is None:
            pytest.skip("HTMLPatternResult not implemented yet")
        
        result = HTMLPatternResult()
        
        assert hasattr(result, 'restaurant_name')
        assert hasattr(result, 'address')
        assert hasattr(result, 'phone')
        assert hasattr(result, 'email')
        assert hasattr(result, 'website')
        assert hasattr(result, 'prices')
        assert hasattr(result, 'menu_items')
        assert hasattr(result, 'hours')
        assert hasattr(result, 'services')
        assert hasattr(result, 'confidence_scores')
        
        # Test default values
        assert result.restaurant_name == ""
        assert result.address == ""
        assert result.phone == ""
        assert isinstance(result.prices, list)
        assert isinstance(result.menu_items, list)
        assert isinstance(result.services, list)
        assert isinstance(result.confidence_scores, dict)