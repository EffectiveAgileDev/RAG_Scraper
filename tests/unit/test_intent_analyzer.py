"""Unit tests for IntentAnalyzer - customer behavior pattern analysis component."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Import will fail until we implement - expected for RED phase
from src.customer_intent.intent_analyzer import IntentAnalyzer
from src.customer_intent.behavior_pattern import BehaviorPattern


class TestIntentAnalyzer:
    """Test the IntentAnalyzer class for customer behavior analysis."""
    
    def test_intent_analyzer_initialization(self):
        """Test IntentAnalyzer can be initialized."""
        
        analyzer = IntentAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'pattern_cache')
        assert hasattr(analyzer, 'learning_config')
    
    def test_analyze_interaction_patterns(self):
        """Test analysis of customer interaction patterns."""
        
        analyzer = IntentAnalyzer()
        interaction_history = [
            {"query": "vegetarian options", "response_quality": 0.9, "outcome": "positive", "timestamp": datetime.now()},
            {"query": "parking availability", "response_quality": 0.6, "outcome": "abandoned", "timestamp": datetime.now()},
            {"query": "dress code", "response_quality": 0.8, "outcome": "positive", "timestamp": datetime.now()},
            {"query": "vegetarian options", "response_quality": 0.9, "outcome": "positive", "timestamp": datetime.now()},
            {"query": "hours today", "response_quality": 0.4, "outcome": "abandoned", "timestamp": datetime.now()}
        ]
        
        result = analyzer.analyze_interaction_patterns(interaction_history)
        
        assert isinstance(result, dict)
        expected_patterns = ["common_question_gaps", "successful_responses", "abandonment_points"]
        
        for pattern_type in expected_patterns:
            assert pattern_type in result
            pattern = result[pattern_type]
            assert "description" in pattern
            assert "adaptation_action" in pattern
            assert "improvement_suggestions" in pattern
    
    def test_identify_common_question_gaps(self):
        """Test identification of common question gaps."""
        
        analyzer = IntentAnalyzer()
        interaction_data = [
            {"query": "gluten free options", "response_quality": 0.3, "outcome": "abandoned"},
            {"query": "allergen information", "response_quality": 0.2, "outcome": "abandoned"},
            {"query": "nutrition facts", "response_quality": 0.1, "outcome": "abandoned"}
        ]
        
        gaps = analyzer.identify_question_gaps(interaction_data)
        
        assert isinstance(gaps, list)
        assert len(gaps) > 0
        
        for gap in gaps:
            assert "question_category" in gap
            assert "frequency" in gap
            assert "avg_response_quality" in gap
            assert "suggested_improvements" in gap
            assert gap["avg_response_quality"] < 0.5  # Should identify poor responses
    
    def test_analyze_successful_response_patterns(self):
        """Test analysis of successful response patterns."""
        
        analyzer = IntentAnalyzer()
        successful_interactions = [
            {"query": "hours", "response_quality": 0.95, "outcome": "positive", "content_type": "business_hours"},
            {"query": "location", "response_quality": 0.92, "outcome": "positive", "content_type": "address"},
            {"query": "phone number", "response_quality": 0.98, "outcome": "positive", "content_type": "contact"}
        ]
        
        patterns = analyzer.analyze_successful_patterns(successful_interactions)
        
        assert isinstance(patterns, dict)
        assert "high_performing_content_types" in patterns
        assert "successful_query_patterns" in patterns
        assert "response_quality_factors" in patterns
        
        # Should identify content types with high success rates
        high_performing = patterns["high_performing_content_types"]
        assert len(high_performing) > 0
        
        for content_type in high_performing:
            assert "average_quality" in content_type
            assert content_type["average_quality"] > 0.9
    
    def test_detect_abandonment_points(self):
        """Test detection of customer abandonment points."""
        
        analyzer = IntentAnalyzer()
        session_data = [
            {"step": 1, "query": "restaurants near me", "outcome": "continued"},
            {"step": 2, "query": "italian food", "outcome": "continued"},
            {"step": 3, "query": "specific restaurant hours", "outcome": "abandoned"},
            {"step": 1, "query": "best pizza", "outcome": "continued"},
            {"step": 2, "query": "delivery options", "outcome": "abandoned"}
        ]
        
        abandonment_points = analyzer.detect_abandonment_points(session_data)
        
        assert isinstance(abandonment_points, list)
        assert len(abandonment_points) > 0
        
        for point in abandonment_points:
            assert "step_number" in point
            assert "common_queries" in point
            assert "abandonment_rate" in point
            assert "suggested_improvements" in point
            assert 0.0 <= point["abandonment_rate"] <= 1.0
    
    def test_learn_from_feedback(self):
        """Test learning from customer feedback."""
        
        analyzer = IntentAnalyzer()
        feedback_data = [
            {"query": "vegan options", "was_helpful": True, "content_id": "menu_dietary"},
            {"query": "parking info", "was_helpful": False, "content_id": "location_basic"},
            {"query": "vegan options", "was_helpful": True, "content_id": "menu_dietary"},
            {"query": "wifi password", "was_helpful": False, "content_id": "amenities"}
        ]
        
        learning_result = analyzer.learn_from_feedback(feedback_data)
        
        assert isinstance(learning_result, dict)
        assert "content_effectiveness" in learning_result
        assert "query_satisfaction" in learning_result
        assert "improvement_recommendations" in learning_result
        
        # Should track content effectiveness
        effectiveness = learning_result["content_effectiveness"]
        assert "menu_dietary" in effectiveness
        assert effectiveness["menu_dietary"]["helpfulness_rate"] > 0.5
    
    def test_predict_customer_intent(self):
        """Test prediction of customer intent based on patterns."""
        
        analyzer = IntentAnalyzer()
        
        # Train with historical patterns
        training_data = [
            {"query": "best pasta", "actual_intent": "dining_decision", "outcome": "positive"},
            {"query": "good for date night", "actual_intent": "experience_planning", "outcome": "positive"},
            {"query": "hours tonight", "actual_intent": "practical_planning", "outcome": "positive"}
        ]
        
        analyzer.train_intent_prediction(training_data)
        
        # Test prediction
        new_queries = [
            "romantic dinner spot",
            "what time do you close",
            "best dishes here"
        ]
        
        predictions = analyzer.predict_intent(new_queries)
        
        assert isinstance(predictions, list)
        assert len(predictions) == len(new_queries)
        
        for prediction in predictions:
            assert "query" in prediction
            assert "predicted_intent" in prediction
            assert "confidence" in prediction
            assert 0.0 <= prediction["confidence"] <= 1.0
    
    def test_analyze_temporal_patterns(self):
        """Test analysis of temporal customer behavior patterns."""
        
        analyzer = IntentAnalyzer()
        
        # Create temporal interaction data
        base_time = datetime.now()
        temporal_data = [
            {"query": "lunch menu", "timestamp": base_time.replace(hour=11)},
            {"query": "dinner reservations", "timestamp": base_time.replace(hour=18)},
            {"query": "brunch options", "timestamp": base_time.replace(hour=10, weekday=5)},  # Saturday
            {"query": "happy hour", "timestamp": base_time.replace(hour=17)},
            {"query": "late night food", "timestamp": base_time.replace(hour=23)}
        ]
        
        patterns = analyzer.analyze_temporal_patterns(temporal_data)
        
        assert isinstance(patterns, dict)
        assert "hourly_patterns" in patterns
        assert "daily_patterns" in patterns
        assert "seasonal_trends" in patterns
        
        # Should identify time-based query patterns
        hourly = patterns["hourly_patterns"]
        assert len(hourly) > 0
        
        # Should detect lunch vs dinner patterns
        has_meal_patterns = any(
            "lunch" in str(pattern).lower() or "dinner" in str(pattern).lower()
            for pattern in hourly.values()
        )
        assert has_meal_patterns
    
    def test_generate_improvement_recommendations(self):
        """Test generation of improvement recommendations."""
        
        analyzer = IntentAnalyzer()
        analysis_results = {
            "common_question_gaps": [
                {"question_category": "dietary_restrictions", "frequency": 0.3, "avg_response_quality": 0.2}
            ],
            "abandonment_points": [
                {"step_number": 2, "abandonment_rate": 0.6, "common_queries": ["detailed_menu"]}
            ],
            "successful_responses": [
                {"content_type": "hours", "average_quality": 0.95}
            ]
        }
        
        recommendations = analyzer.generate_improvement_recommendations(analysis_results)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert "priority" in recommendation
            assert "category" in recommendation
            assert "description" in recommendation
            assert "implementation_steps" in recommendation
            assert "expected_impact" in recommendation
            
            # Priority should be valid
            assert recommendation["priority"] in ["high", "medium", "low"]
    
    def test_track_intent_evolution(self):
        """Test tracking of how customer intents evolve over time."""
        
        analyzer = IntentAnalyzer()
        
        # Historical intent data over time
        intent_history = [
            {"date": datetime.now() - timedelta(days=30), "intent": "basic_info", "frequency": 0.8},
            {"date": datetime.now() - timedelta(days=15), "intent": "basic_info", "frequency": 0.6},
            {"date": datetime.now() - timedelta(days=15), "intent": "dietary_options", "frequency": 0.3},
            {"date": datetime.now(), "intent": "basic_info", "frequency": 0.4},
            {"date": datetime.now(), "intent": "dietary_options", "frequency": 0.5},
            {"date": datetime.now(), "intent": "sustainability", "frequency": 0.1}
        ]
        
        evolution = analyzer.track_intent_evolution(intent_history)
        
        assert isinstance(evolution, dict)
        assert "trending_intents" in evolution
        assert "declining_intents" in evolution
        assert "emerging_intents" in evolution
        assert "evolution_insights" in evolution
        
        # Should detect trends
        trending = evolution["trending_intents"]
        declining = evolution["declining_intents"]
        
        # Basic info should be declining, dietary options trending up
        dietary_trending = any("dietary" in intent.get("name", "") for intent in trending)
        basic_declining = any("basic" in intent.get("name", "") for intent in declining)
        
        assert dietary_trending or basic_declining  # At least one trend should be detected
    
    def test_calculate_intent_similarity(self):
        """Test calculation of intent similarity between queries."""
        
        analyzer = IntentAnalyzer()
        
        query_pairs = [
            ("what time do you close", "when do you close"),  # High similarity
            ("vegan options", "vegetarian menu"),  # Medium similarity  
            ("parking available", "wine list"),  # Low similarity
        ]
        
        for query1, query2 in query_pairs:
            similarity = analyzer.calculate_intent_similarity(query1, query2)
            
            assert isinstance(similarity, float)
            assert 0.0 <= similarity <= 1.0
        
        # Test that similar queries have higher similarity
        time_similarity = analyzer.calculate_intent_similarity("what time do you close", "when do you close")
        unrelated_similarity = analyzer.calculate_intent_similarity("parking available", "wine list")
        
        assert time_similarity > unrelated_similarity
    
    def test_export_analytics_dashboard_data(self):
        """Test export of data for analytics dashboard."""
        
        analyzer = IntentAnalyzer()
        
        # Mock some analysis results
        analyzer._analysis_cache = {
            "interaction_patterns": {"successful_responses": 0.8},
            "temporal_patterns": {"peak_hours": [11, 12, 18, 19]},
            "intent_evolution": {"trending": ["dietary_options"]}
        }
        
        dashboard_data = analyzer.export_dashboard_data()
        
        assert isinstance(dashboard_data, dict)
        assert "metrics" in dashboard_data
        assert "visualizations" in dashboard_data
        assert "recommendations" in dashboard_data
        assert "last_updated" in dashboard_data
        
        # Should include key metrics
        metrics = dashboard_data["metrics"]
        assert "success_rate" in metrics
        assert "popular_intent_categories" in metrics
        assert "response_quality_avg" in metrics


class TestBehaviorPattern:
    """Test the BehaviorPattern data structure."""
    
    def test_behavior_pattern_creation(self):
        """Test BehaviorPattern can be created."""
        
        pattern = BehaviorPattern(
            pattern_type="abandonment_point",
            description="Customers abandon at menu details",
            frequency=0.3,
            confidence=0.8,
            suggested_actions=["improve_menu_presentation"]
        )
        
        assert pattern.pattern_type == "abandonment_point"
        assert pattern.description == "Customers abandon at menu details"
        assert pattern.frequency == 0.3
        assert pattern.confidence == 0.8
        assert "improve_menu_presentation" in pattern.suggested_actions
    
    def test_behavior_pattern_validation(self):
        """Test BehaviorPattern validates its data."""
        
        # Should validate frequency range
        with pytest.raises((ValueError, TypeError)):
            BehaviorPattern(
                pattern_type="test",
                description="test",
                frequency=1.5,  # Should be <= 1.0
                confidence=0.8,
                suggested_actions=[]
            )
        
        # Should validate confidence range
        with pytest.raises((ValueError, TypeError)):
            BehaviorPattern(
                pattern_type="test",
                description="test",
                frequency=0.5,
                confidence=-0.1,  # Should be >= 0.0
                suggested_actions=[]
            )
    
    def test_behavior_pattern_to_dict(self):
        """Test BehaviorPattern conversion to dictionary."""
        
        pattern = BehaviorPattern(
            pattern_type="successful_response",
            description="High success with hours queries",
            frequency=0.8,
            confidence=0.9,
            suggested_actions=["maintain_current_approach"]
        )
        
        pattern_dict = pattern.to_dict()
        
        assert isinstance(pattern_dict, dict)
        assert "pattern_type" in pattern_dict
        assert "description" in pattern_dict
        assert "frequency" in pattern_dict
        assert "confidence" in pattern_dict
        assert "suggested_actions" in pattern_dict