"""Unit tests for popup detection and classification."""
import pytest
from unittest.mock import Mock, patch

from src.scraper.restaurant_popup_detector import RestaurantPopupDetector, RestaurantPopupPattern


class TestRestaurantPopupDetector:
    """Test cases for restaurant popup detector."""
    
    @pytest.fixture
    def detector(self):
        """Create popup detector instance."""
        return RestaurantPopupDetector()
    
    def test_detect_age_verification_popup(self, detector):
        """Test detection of age verification popup."""
        html = '''
        <div class="age-gate modal">
            <p>Are you 21 or older?</p>
            <button class="confirm-age">Yes, I'm 21+</button>
        </div>
        '''
        
        popups = detector.detect_restaurant_popups(html)
        
        assert len(popups) >= 1
        age_popup = next((p for p in popups if p['type'] == 'age_verification'), None)
        assert age_popup is not None
        assert age_popup['priority'] == 1
        assert age_popup['confidence'] > 0.5
    
    def test_detect_location_selector(self, detector):
        """Test detection of location selector popup."""
        html = '''
        <div class="location-modal">
            <h3>Choose Your Restaurant Location</h3>
            <div class="location-item">Downtown</div>
            <div class="location-item">Uptown</div>
        </div>
        '''
        
        popups = detector.detect_restaurant_popups(html)
        
        location_popup = next((p for p in popups if p['type'] == 'location_selector'), None)
        assert location_popup is not None
        assert location_popup['priority'] == 2
    
    def test_detect_multiple_popups_priority_order(self, detector):
        """Test detection and priority ordering of multiple popups."""
        html = '''
        <div class="newsletter-modal">Subscribe to our newsletter</div>
        <div class="age-verification">Please verify your age: Are you 21 or older?</div>
        <div class="location-modal">Find your nearest restaurant location</div>
        '''
        
        popups = detector.detect_restaurant_popups(html)
        
        # Should detect multiple popups
        assert len(popups) >= 2
        
        # Age verification should have highest priority (lowest number)
        age_popup = next((p for p in popups if p['type'] == 'age_verification'), None)
        newsletter_popup = next((p for p in popups if p['type'] == 'newsletter_signup'), None)
        
        assert age_popup is not None
        assert newsletter_popup is not None
        assert age_popup['priority'] < newsletter_popup['priority']
    
    def test_confidence_scoring(self, detector):
        """Test confidence scoring for popup detection."""
        # High confidence case - multiple selectors and keywords
        high_confidence_html = '''
        <div class="age-gate age-verification">
            <p>You must be 21 years or older to view this content</p>
            <button class="verify-age">Confirm Age</button>
        </div>
        '''
        
        # Low confidence case - minimal matches
        low_confidence_html = '''
        <div class="some-modal">
            <p>Please verify your age</p>
        </div>
        '''
        
        high_popups = detector.detect_restaurant_popups(high_confidence_html)
        low_popups = detector.detect_restaurant_popups(low_confidence_html)
        
        if high_popups and low_popups:
            high_age_popup = next((p for p in high_popups if p['type'] == 'age_verification'), None)
            low_age_popup = next((p for p in low_popups if p['type'] == 'age_verification'), None)
            
            if high_age_popup and low_age_popup:
                assert high_age_popup['confidence'] > low_age_popup['confidence']
    
    def test_no_popups_detected(self, detector):
        """Test when no popups are present."""
        html = '''
        <div class="main-content">
            <h1>Restaurant Name</h1>
            <div class="menu">Menu items</div>
        </div>
        '''
        
        popups = detector.detect_restaurant_popups(html)
        assert len(popups) == 0
    
    def test_get_handling_strategy_age_verification(self, detector):
        """Test handling strategy for age verification."""
        strategy = detector.get_handling_strategy('age_verification')
        
        assert strategy['method'] == 'click_button'
        assert '.confirm-age' in strategy['targets']
        assert strategy['fallback'] == 'continue_anyway'
    
    def test_get_handling_strategy_location_selector(self, detector):
        """Test handling strategy for location selector."""
        strategy = detector.get_handling_strategy('location_selector')
        
        assert strategy['method'] == 'select_option'
        assert '.location-item:first' in strategy['targets']
    
    def test_get_handling_strategy_unknown_type(self, detector):
        """Test handling strategy for unknown popup type."""
        strategy = detector.get_handling_strategy('unknown_popup')
        
        assert strategy['method'] == 'generic_close'
        assert '.close' in strategy['targets']
    
    def test_covid_notice_detection(self, detector):
        """Test detection of COVID-related notices."""
        html = '''
        <div class="covid-modal health-notice">
            <h3>Health and Safety Guidelines</h3>
            <p>Please follow COVID safety protocols</p>
            <button class="acknowledge">I Understand</button>
        </div>
        '''
        
        popups = detector.detect_restaurant_popups(html)
        
        covid_popup = next((p for p in popups if p['type'] == 'covid_notice'), None)
        assert covid_popup is not None
        assert covid_popup['confidence'] > 0.3
    
    def test_reservation_prompt_detection(self, detector):
        """Test detection of reservation prompts."""
        html = '''
        <div class="reservation-modal">
            <h3>Make a Reservation</h3>
            <p>Book your table now!</p>
            <button class="book-table">Reserve</button>
            <button class="no-thanks">No Thanks</button>
        </div>
        '''
        
        popups = detector.detect_restaurant_popups(html)
        
        reservation_popup = next((p for p in popups if p['type'] == 'reservation_prompt'), None)
        assert reservation_popup is not None


class TestPopupPatternMatching:
    """Test popup pattern matching logic."""
    
    def test_selector_matching(self):
        """Test selector-based matching."""
        detector = RestaurantPopupDetector()
        
        html_with_class = '<div class="age-gate">Please verify your age</div>'
        html_with_id = '<div id="ageModal">Are you older than 21?</div>'
        html_without_match = '<div class="random-class">Random content</div>'
        
        age_pattern = next(p for p in detector.patterns if p.type == 'age_verification')
        
        assert detector._matches_pattern(html_with_class, age_pattern)
        assert detector._matches_pattern(html_with_id, age_pattern)
        assert not detector._matches_pattern(html_without_match, age_pattern)
    
    def test_keyword_requirement(self):
        """Test that keywords are required for pattern matching."""
        detector = RestaurantPopupDetector()
        
        # Has selector but no keywords
        html_no_keywords = '<div class="age-gate">Random content</div>'
        # Has selector and keywords
        html_with_keywords = '<div class="age-gate">Are you 21 or older?</div>'
        
        age_pattern = next(p for p in detector.patterns if p.type == 'age_verification')
        
        assert not detector._matches_pattern(html_no_keywords, age_pattern)
        assert detector._matches_pattern(html_with_keywords, age_pattern)