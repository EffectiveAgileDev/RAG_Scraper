"""Unit tests for ContentScorer - scores content relevance for customer intents."""

import pytest
from unittest.mock import Mock, patch

# Import will fail until we implement - expected for RED phase
from src.customer_intent.content_scorer import ContentScorer
from src.customer_intent.relevance_score import RelevanceScore


class TestContentScorer:
    """Test the ContentScorer class for content relevance scoring."""
    
    def test_content_scorer_initialization(self):
        """Test ContentScorer can be initialized."""
        
        scorer = ContentScorer()
        assert scorer is not None
        assert hasattr(scorer, 'scoring_algorithms')
        assert hasattr(scorer, 'intent_weights')
    
    def test_score_content_relevance_basic(self):
        """Test basic content relevance scoring."""
        
        scorer = ContentScorer()
        restaurant_data = {
            "name": "Test Restaurant",
            "menu": {"items": ["Burger - $15"]},
            "hours": {"monday": "9-17"},
            "reviews": {"rating": 4.2},
            "price_range": "$$"
        }
        
        query_patterns = [
            {"query": "what time do you close", "intent_type": "practical_planning"},
            {"query": "is it expensive", "intent_type": "evaluation"},
            {"query": "what food do you serve", "intent_type": "dining_decision"}
        ]
        
        result = scorer.score_content_relevance(restaurant_data, query_patterns)
        
        assert isinstance(result, dict)
        
        for intent_type in ["practical_planning", "evaluation", "dining_decision"]:
            assert intent_type in result
            scores = result[intent_type]
            
            for content_id, score_data in scores.items():
                assert "score" in score_data
                assert "confidence" in score_data
                assert 0.0 <= score_data["score"] <= 1.0
                assert 0.0 <= score_data["confidence"] <= 1.0
    
    def test_score_immediate_decision_intent(self):
        """Test scoring for immediate decision-making intent."""
        
        scorer = ContentScorer()
        restaurant_data = {
            "name": "Quick Bite",
            "rating": 4.5,
            "price_range": "$",
            "cuisine": "American",
            "hours": {"current_status": "open"},
            "location": {"distance": "0.2 miles"}
        }
        
        intent_config = {
            "intent_type": "immediate_decision",
            "scoring_criteria": ["rating", "price_range", "distance", "current_availability"]
        }
        
        score = scorer.score_for_intent(restaurant_data, intent_config)
        
        assert isinstance(score, dict)
        assert "overall_score" in score
        assert "component_scores" in score
        assert "reasoning" in score
        
        # Should score highly for immediate decision factors
        assert score["overall_score"] > 0.7  # Should be high for good rating, cheap, close, open
    
    def test_score_detailed_research_intent(self):
        """Test scoring for detailed research intent."""
        
        scorer = ContentScorer()
        restaurant_data = {
            "name": "Gourmet Bistro",
            "description": "Detailed description of our culinary philosophy and ingredients...",
            "reviews": {
                "count": 150,
                "detailed_reviews": ["Amazing food", "Great service", "Perfect ambiance"]
            },
            "menu": {
                "detailed_descriptions": True,
                "ingredient_lists": True,
                "chef_specials": ["Truffle pasta", "Duck confit"]
            },
            "chef_bio": "Award-winning chef with 20 years experience...",
            "awards": ["Michelin star", "Best restaurant 2023"]
        }
        
        intent_config = {
            "intent_type": "detailed_research",
            "scoring_criteria": ["description_depth", "review_count", "menu_detail", "credentials"]
        }
        
        score = scorer.score_for_intent(restaurant_data, intent_config)
        
        assert isinstance(score, dict)
        assert score["overall_score"] > 0.8  # Should score high for detailed information
        
        # Should have high component scores for research factors
        components = score["component_scores"]
        assert components.get("description_depth", 0) > 0.7
        assert components.get("menu_detail", 0) > 0.7
    
    def test_score_visit_logistics_intent(self):
        """Test scoring for visit logistics planning intent."""
        
        scorer = ContentScorer()
        restaurant_data = {
            "hours": {
                "monday": "11:00-22:00",
                "tuesday": "11:00-22:00",
                "detailed_schedule": True
            },
            "location": {
                "address": "123 Main St",
                "coordinates": {"lat": 40.7128, "lng": -74.0060},
                "directions": "Easy to find"
            },
            "contact": {
                "phone": "555-1234",
                "reservations": "accepted",
                "online_booking": True
            },
            "parking": {
                "availability": "street and garage",
                "cost": "paid",
                "details": "2-hour street parking, garage across street"
            },
            "accessibility": "wheelchair accessible"
        }
        
        intent_config = {
            "intent_type": "visit_logistics",
            "scoring_criteria": ["hours_clarity", "location_detail", "contact_info", "parking_info"]
        }
        
        score = scorer.score_for_intent(restaurant_data, intent_config)
        
        assert isinstance(score, dict)
        assert score["overall_score"] > 0.8  # Should score high for comprehensive logistics info
        
        # Should score highly for logistics factors
        components = score["component_scores"]
        assert components.get("hours_clarity", 0) > 0.8
        assert components.get("contact_info", 0) > 0.8
    
    def test_score_dietary_filtering_intent(self):
        """Test scoring for dietary filtering intent."""
        
        scorer = ContentScorer()
        restaurant_data = {
            "menu": {
                "dietary_options": {
                    "vegetarian": ["Quinoa Bowl", "Veggie Burger", "Caprese Salad"],
                    "vegan": ["Buddha Bowl", "Lentil Soup"],
                    "gluten_free": ["Grilled Fish", "Rice Bowl", "Salad"],
                    "allergen_free": {"nuts": ["marked dishes"], "dairy": ["marked dishes"]}
                },
                "ingredient_lists": True,
                "allergen_info": "detailed"
            },
            "certifications": ["vegetarian_friendly", "allergen_aware"],
            "kitchen_notes": "Separate prep areas for allergen-free dishes"
        }
        
        intent_config = {
            "intent_type": "dietary_filtering",
            "scoring_criteria": ["dietary_variety", "allergen_info", "ingredient_detail", "kitchen_practices"]
        }
        
        score = scorer.score_for_intent(restaurant_data, intent_config)
        
        assert isinstance(score, dict)
        assert score["overall_score"] > 0.9  # Should score very high for comprehensive dietary info
        
        # Should have high scores for dietary factors
        components = score["component_scores"]
        assert components.get("dietary_variety", 0) > 0.8
        assert components.get("allergen_info", 0) > 0.8
    
    def test_calculate_confidence_intervals(self):
        """Test calculation of confidence intervals for scores."""
        
        scorer = ContentScorer()
        
        # Test with varying data quality
        high_quality_data = {
            "name": "Complete Restaurant",
            "description": "Detailed description",
            "menu": {"detailed": True, "complete": True},
            "hours": {"complete": True},
            "contact": {"phone": "yes", "email": "yes"},
            "reviews": {"count": 100, "avg_rating": 4.5}
        }
        
        low_quality_data = {
            "name": "Incomplete Restaurant"
            # Missing most information
        }
        
        high_confidence = scorer.calculate_confidence(high_quality_data)
        low_confidence = scorer.calculate_confidence(low_quality_data)
        
        assert isinstance(high_confidence, float)
        assert isinstance(low_confidence, float)
        assert 0.0 <= high_confidence <= 1.0
        assert 0.0 <= low_confidence <= 1.0
        assert high_confidence > low_confidence
    
    def test_weight_scores_by_intent_importance(self):
        """Test weighting of scores by intent importance."""
        
        scorer = ContentScorer()
        
        # Different restaurant types should have different intent weights
        fine_dining_weights = {
            "atmosphere": 0.3,
            "menu_quality": 0.4,
            "service": 0.2,
            "price": 0.1
        }
        
        fast_food_weights = {
            "speed": 0.4,
            "price": 0.3,
            "convenience": 0.2,
            "menu_quality": 0.1
        }
        
        base_scores = {
            "atmosphere": 0.9,
            "menu_quality": 0.8,
            "service": 0.7,
            "price": 0.6,
            "speed": 0.5,
            "convenience": 0.8
        }
        
        fine_dining_score = scorer.apply_intent_weights(base_scores, fine_dining_weights)
        fast_food_score = scorer.apply_intent_weights(base_scores, fast_food_weights)
        
        # Fine dining should score higher (good atmosphere, menu, service)
        # Fast food should score lower (poor speed, but good convenience)
        assert fine_dining_score > fast_food_score
    
    def test_temporal_relevance_scoring(self):
        """Test temporal relevance scoring for time-sensitive content."""
        
        scorer = ContentScorer()
        
        # Current time-sensitive content
        current_content = {
            "hours_today": "11:00-22:00",
            "daily_special": "Today's special: Fish & Chips",
            "live_wait_time": "15 minutes",
            "current_availability": "accepting walk-ins"
        }
        
        # Static content
        static_content = {
            "general_hours": "Usually open 11-22",
            "sample_menu": "We serve various dishes",
            "general_info": "Family restaurant since 1980"
        }
        
        current_score = scorer.score_temporal_relevance(current_content, time_sensitivity="high")
        static_score = scorer.score_temporal_relevance(static_content, time_sensitivity="high")
        
        assert current_score > static_score
        
        # Low time sensitivity should not penalize static content as much
        static_score_low_sensitivity = scorer.score_temporal_relevance(
            static_content, 
            time_sensitivity="low"
        )
        assert static_score_low_sensitivity > static_score
    
    def test_contextual_relevance_scoring(self):
        """Test contextual relevance based on user location/preferences."""
        
        scorer = ContentScorer()
        
        restaurant_data = {
            "location": {"distance": "0.5 miles"},
            "cuisine": "Italian",
            "price_range": "$$",
            "delivery": True,
            "outdoor_seating": True
        }
        
        # Different user contexts
        nearby_user = {"location_preference": "walking_distance", "max_distance": "1 mile"}
        cuisine_lover = {"preferred_cuisines": ["Italian", "French"], "cuisine_importance": "high"}
        budget_conscious = {"max_price": "$$", "price_importance": "high"}
        delivery_user = {"service_preference": "delivery", "location": "home"}
        
        nearby_score = scorer.score_contextual_relevance(restaurant_data, nearby_user)
        cuisine_score = scorer.score_contextual_relevance(restaurant_data, cuisine_lover)
        budget_score = scorer.score_contextual_relevance(restaurant_data, budget_conscious)
        delivery_score = scorer.score_contextual_relevance(restaurant_data, delivery_user)
        
        # All should score reasonably well given the matching attributes
        assert nearby_score > 0.7  # Close distance
        assert cuisine_score > 0.8  # Matching cuisine preference
        assert budget_score > 0.8   # Matching price range
        assert delivery_score > 0.7 # Has delivery
    
    def test_export_scoring_methodology(self):
        """Test export of scoring methodology for transparency."""
        
        scorer = ContentScorer()
        
        methodology = scorer.export_scoring_methodology()
        
        assert isinstance(methodology, dict)
        assert "intent_types" in methodology
        assert "scoring_criteria" in methodology
        assert "weight_calculations" in methodology
        assert "confidence_factors" in methodology
        
        # Should document each intent type
        intent_types = methodology["intent_types"]
        expected_intents = ["immediate_decision", "detailed_research", "visit_logistics", "dietary_filtering"]
        
        for intent in expected_intents:
            assert intent in intent_types
            intent_info = intent_types[intent]
            assert "description" in intent_info
            assert "key_factors" in intent_info
            assert "weight_distribution" in intent_info
    
    def test_batch_scoring_performance(self):
        """Test batch scoring performance for multiple content pieces."""
        
        scorer = ContentScorer()
        
        # Multiple restaurant data sets
        restaurants = [
            {"name": f"Restaurant {i}", "menu": {"items": ["Item 1"]}, "rating": 4.0 + (i * 0.1)}
            for i in range(10)
        ]
        
        intent_patterns = [
            {"query": "good food", "intent_type": "dining_decision"},
            {"query": "what time close", "intent_type": "practical_planning"}
        ]
        
        # Should handle batch processing
        batch_results = scorer.batch_score_content(restaurants, intent_patterns)
        
        assert isinstance(batch_results, list)
        assert len(batch_results) == len(restaurants)
        
        for i, result in enumerate(batch_results):
            assert "restaurant_id" in result or "restaurant_name" in result
            assert "intent_scores" in result
            assert isinstance(result["intent_scores"], dict)


class TestRelevanceScore:
    """Test the RelevanceScore data structure."""
    
    def test_relevance_score_creation(self):
        """Test RelevanceScore can be created."""
        
        score = RelevanceScore(
            content_id="menu_1",
            intent_type="dining_decision",
            score=0.85,
            confidence=0.9,
            factors={"menu_quality": 0.8, "price_appeal": 0.9}
        )
        
        assert score.content_id == "menu_1"
        assert score.intent_type == "dining_decision"
        assert score.score == 0.85
        assert score.confidence == 0.9
        assert score.factors["menu_quality"] == 0.8
    
    def test_relevance_score_validation(self):
        """Test RelevanceScore validates its data."""
        
        # Should validate score range
        with pytest.raises((ValueError, TypeError)):
            RelevanceScore(
                content_id="test",
                intent_type="test",
                score=1.5,  # Should be <= 1.0
                confidence=0.8,
                factors={}
            )
        
        # Should validate confidence range
        with pytest.raises((ValueError, TypeError)):
            RelevanceScore(
                content_id="test",
                intent_type="test",
                score=0.8,
                confidence=-0.1,  # Should be >= 0.0
                factors={}
            )
    
    def test_relevance_score_to_dict(self):
        """Test RelevanceScore conversion to dictionary."""
        
        score = RelevanceScore(
            content_id="hours_1",
            intent_type="practical_planning",
            score=0.92,
            confidence=0.95,
            factors={"clarity": 0.9, "completeness": 0.95, "timeliness": 0.9}
        )
        
        score_dict = score.to_dict()
        
        assert isinstance(score_dict, dict)
        assert "content_id" in score_dict
        assert "intent_type" in score_dict
        assert "score" in score_dict
        assert "confidence" in score_dict
        assert "factors" in score_dict