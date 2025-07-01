"""Unit tests for CustomerIntentMapper - the main customer intent mapping component."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import will fail until we implement - expected for RED phase
from src.customer_intent.intent_mapper import CustomerIntentMapper
from src.customer_intent.intent_result import IntentMappingResult


class TestCustomerIntentMapper:
    """Test the main CustomerIntentMapper class."""
    
    def test_intent_mapper_initialization(self):
        """Test CustomerIntentMapper can be initialized with default config."""
        mapper = CustomerIntentMapper()
        assert mapper is not None
        assert hasattr(mapper, 'industry_config')
        assert hasattr(mapper, 'intent_patterns')
    
    def test_intent_mapper_with_industry_config(self):
        """Test CustomerIntentMapper with industry-specific configuration."""
        
        config = {
            'industry': 'restaurant',
            'intent_patterns': {
                'dining_decision': ['what is good', 'best dishes', 'recommendations'],
                'practical_info': ['hours', 'location', 'parking']
            }
        }
        
        mapper = CustomerIntentMapper(config=config)
        assert mapper.industry == 'restaurant'
        assert 'dining_decision' in mapper.intent_patterns
        assert 'practical_info' in mapper.intent_patterns
    
    def test_analyze_intent_patterns_basic(self):
        """Test basic intent pattern analysis."""
        
        mapper = CustomerIntentMapper()
        restaurant_data = {
            "name": "Test Restaurant",
            "menu": {"appetizers": ["Salad - $12"]},
            "hours": {"monday": "9-17"},
            "description": "Great food and atmosphere"
        }
        
        result = mapper.analyze_intent_patterns(restaurant_data)
        
        assert isinstance(result, dict)
        assert "mappings" in result
        assert len(result["mappings"]) > 0
        
        # Verify mapping structure
        first_mapping = result["mappings"][0]
        assert "customer_question" in first_mapping
        assert "mapped_content_type" in first_mapping
        assert "confidence_score" in first_mapping
        assert "supporting_evidence" in first_mapping
    
    def test_categorize_intents_by_decision_stage(self):
        """Test intent categorization by customer decision stage."""
        
        mapper = CustomerIntentMapper()
        restaurant_data = {
            "name": "Bistro Deluxe",
            "cuisine": "French",
            "price_range": "$$$",
            "location": {"address": "123 Main St"},
            "reviews": {"rating": 4.5}
        }
        
        result = mapper.categorize_intents(restaurant_data)
        
        assert isinstance(result, dict)
        expected_categories = ["discovery", "evaluation", "practical_planning", "dietary_requirements", "experience_planning"]
        
        for category in expected_categories:
            assert category in result
            assert "description" in result[category]
            assert "example_questions" in result[category]
            assert "content_sections" in result[category]
    
    def test_generate_customer_summaries(self):
        """Test generation of customer-centric summaries."""
        
        mapper = CustomerIntentMapper()
        restaurant_data = {
            "name": "Bistro Deluxe",
            "cuisine": "French",
            "price_range": "$$$",
            "rating": 4.5,
            "location": {"city": "Downtown"},
            "menu": {"vegetarian_options": ["Ratatouille", "Salad"]},
            "hours": {"monday": "11:00-22:00"}
        }
        
        result = mapper.generate_customer_summaries(restaurant_data)
        
        assert isinstance(result, dict)
        expected_summary_types = ["quick_decision", "dietary_friendly", "visit_planning", "experience_preview"]
        
        for summary_type in expected_summary_types:
            assert summary_type in result
            summary = result[summary_type]
            
            # Should be concise for customer consumption
            assert len(summary) <= 200
            # Should not contain technical jargon
            assert "RAG" not in summary
            assert "extraction" not in summary
    
    def test_create_bidirectional_relationships(self):
        """Test creation of bidirectional intent-content relationships."""
        
        mapper = CustomerIntentMapper()
        restaurant_data = {
            "name": "Test Restaurant",
            "menu": {"appetizers": ["Salad"]},
            "hours": {"monday": "9-17"},
            "contact": {"phone": "555-1234"}
        }
        
        result = mapper.create_bidirectional_relationships(restaurant_data)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check for expected relationship types
        relationship_types = {rel["type"] for rel in result}
        expected_types = {"answers_question", "supports_decision", "enables_planning", "addresses_concern"}
        assert any(rt in relationship_types for rt in expected_types)
        
        # Verify bidirectional structure
        for relationship in result:
            assert "type" in relationship
            assert "from_entity" in relationship
            assert "to_entity" in relationship
            assert "confidence" in relationship
    
    def test_generate_faqs_from_content(self):
        """Test FAQ generation from restaurant content."""
        
        mapper = CustomerIntentMapper()
        restaurant_data = {
            "name": "Bistro Deluxe",
            "cuisine": "French",
            "price_range": "$$$",
            "contact": {"reservations": "recommended"},
            "ambiance": {"good_for": ["date night"]}
        }
        
        result = mapper.generate_faqs(restaurant_data)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        for faq in result:
            assert "question" in faq
            assert "answer" in faq
            assert "answer_source" in faq
            assert "confidence" in faq
            assert "source_content" in faq
            
            # Confidence should be in valid range
            assert 0.0 <= faq["confidence"] <= 1.0
    
    def test_map_temporal_intents(self):
        """Test mapping of temporal customer intents."""
        
        mapper = CustomerIntentMapper()
        temporal_data = {
            "current_hours": "11:00-22:00",
            "daily_specials": {"today": "Fish Special - $18"},
            "weekend_hours": {"saturday": "10:00-23:00"},
            "holiday_schedule": {"thanksgiving": "closed"}
        }
        
        result = mapper.map_temporal_intents(temporal_data)
        
        assert isinstance(result, dict)
        
        # Should handle different temporal contexts
        temporal_types = {"real_time", "daily", "weekly", "seasonal"}
        found_types = set()
        
        for intent, mapping in result.items():
            assert "time_sensitivity" in mapping
            assert "context_timestamp" in mapping
            found_types.add(mapping["time_sensitivity"])
        
        assert len(found_types) > 0
    
    def test_export_for_rag_systems(self):
        """Test export functionality for RAG system integration."""
        
        mapper = CustomerIntentMapper()
        restaurant_data = {
            "name": "Test Restaurant",
            "menu": {"items": ["Burger - $15"]},
            "hours": {"monday": "9-17"}
        }
        
        result = mapper.export_for_rag(restaurant_data)
        
        assert isinstance(result, dict)
        expected_components = ["intent_taxonomy", "content_mappings", "query_templates", "relevance_scores"]
        
        for component in expected_components:
            assert component in result
            component_data = result[component]
            assert "format" in component_data
            assert "metadata" in component_data
            assert "query_optimization" in component_data
    
    def test_process_ambiguous_intents(self):
        """Test processing of ambiguous customer intents."""
        
        mapper = CustomerIntentMapper()
        ambiguous_queries = [
            "good for date night",
            "quick lunch near office",
            "family dinner with dietary needs"
        ]
        restaurant_data = {
            "name": "Test Restaurant",
            "atmosphere": "romantic",
            "speed": "moderate",
            "location": {"address": "Downtown"},
            "menu": {"dietary_options": {"vegetarian": ["Salad"], "kids": ["Chicken Fingers"]}}
        }
        
        result = mapper.process_ambiguous_intents(ambiguous_queries, restaurant_data)
        
        assert isinstance(result, dict)
        
        for query in ambiguous_queries:
            found_result = next(
                (r for query_key, r in result.items() if query in query_key),
                None
            )
            assert found_result is not None
            assert "detected_intents" in found_result
            assert len(found_result["detected_intents"]) > 1  # Should detect multiple intents
            assert "response_components" in found_result
    
    def test_analyze_by_restaurant_category(self):
        """Test analysis by restaurant category/type."""
        
        mapper = CustomerIntentMapper()
        restaurant_types = {
            "fine_dining": {"price_range": "$$$", "atmosphere": "upscale"},
            "fast_food": {"price_range": "$", "service": "quick"},
            "cafe": {"price_range": "$$", "atmosphere": "casual"}
        }
        
        result = mapper.analyze_by_category(restaurant_types)
        
        assert isinstance(result, dict)
        
        for restaurant_type in restaurant_types.keys():
            assert restaurant_type in result
            category_data = result[restaurant_type]
            assert "priority_intents" in category_data
            assert "intent_weights" in category_data
            
            # Different types should have different weightings
            weights = category_data["intent_weights"]
            assert len(weights) > 0
    
    def test_intent_confidence_scoring(self):
        """Test confidence scoring for intent mappings."""
        
        mapper = CustomerIntentMapper()
        
        # Test with high-confidence data
        high_confidence_data = {
            "name": "Bistro Deluxe",
            "menu": {"appetizers": ["Caesar Salad - $12"], "mains": ["Steak - $28"]},
            "hours": {"monday": "11:00-22:00"},
            "contact": {"phone": "555-1234", "email": "info@bistro.com"}
        }
        
        # Test with low-confidence data
        low_confidence_data = {
            "name": "Unknown Restaurant"
            # Missing most information
        }
        
        high_result = mapper.analyze_intent_patterns(high_confidence_data)
        low_result = mapper.analyze_intent_patterns(low_confidence_data)
        
        # High confidence data should have higher scores
        high_scores = [m["confidence_score"] for m in high_result["mappings"]]
        low_scores = [m["confidence_score"] for m in low_result["mappings"]]
        
        assert max(high_scores) > max(low_scores) if low_scores else 0.0
        
        # All scores should be in valid range
        for score in high_scores + low_scores:
            assert 0.0 <= score <= 1.0
    
    def test_industry_specific_patterns(self):
        """Test industry-specific intent patterns."""
        
        # Test restaurant-specific patterns
        restaurant_mapper = CustomerIntentMapper(config={'industry': 'restaurant'})
        
        restaurant_data = {
            "name": "Test Restaurant",
            "cuisine": "Italian", 
            "menu": {"pasta": ["Carbonara - $18"]},
            "wine_list": {"reds": ["Chianti"], "whites": ["Pinot Grigio"]}
        }
        
        result = restaurant_mapper.analyze_intent_patterns(restaurant_data)
        
        # Should detect restaurant-specific intents
        restaurant_intents = [m["customer_question"] for m in result["mappings"]]
        restaurant_specific = any(
            "wine" in intent.lower() or "menu" in intent.lower() or "cuisine" in intent.lower()
            for intent in restaurant_intents
        )
        assert restaurant_specific
    
    def test_content_relevance_scoring(self):
        """Test content relevance scoring for different intent types."""
        
        mapper = CustomerIntentMapper()
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
        
        # Mock ContentScorer since we're testing integration
        with patch('src.customer_intent.content_scorer.ContentScorer') as mock_scorer:
            mock_instance = Mock()
            mock_instance.score_content_relevance.return_value = {
                "practical_planning": {"hours": {"score": 0.95, "confidence": 0.9}},
                "evaluation": {"price_range": {"score": 0.88, "confidence": 0.8}},
                "dining_decision": {"menu": {"score": 0.92, "confidence": 0.85}}
            }
            mock_scorer.return_value = mock_instance
            
            result = mapper.score_content_relevance(restaurant_data, query_patterns)
            
            assert isinstance(result, dict)
            
            for intent_type in ["practical_planning", "evaluation", "dining_decision"]:
                assert intent_type in result
                scores = result[intent_type]
                
                for content_id, score_data in scores.items():
                    assert "score" in score_data
                    assert "confidence" in score_data
                    assert 0.0 <= score_data["score"] <= 1.0
                    assert 0.0 <= score_data["confidence"] <= 1.0
    
    def test_handle_missing_restaurant_data(self):
        """Test handling of incomplete restaurant data."""
        
        mapper = CustomerIntentMapper()
        incomplete_data = {
            "name": "Incomplete Restaurant"
            # Missing menu, hours, location, etc.
        }
        
        result = mapper.analyze_intent_patterns(incomplete_data)
        
        # Should still create some mappings, but with lower confidence
        assert len(result["mappings"]) > 0
        
        # Confidence scores should reflect data completeness
        confidence_scores = [m["confidence_score"] for m in result["mappings"]]
        assert all(score < 0.8 for score in confidence_scores)  # Lower confidence due to missing data
    
    def test_query_template_generation(self):
        """Test generation of query templates for natural language variations."""
        
        mapper = CustomerIntentMapper()
        restaurant_data = {
            "hours": {"monday": "11:00-22:00"},
            "menu": {"appetizers": ["Salad - $12"]},
            "location": {"address": "123 Main St"}
        }
        
        # Mock QueryMapper since we're testing integration
        with patch('src.customer_intent.query_mapper.QueryMapper') as mock_query_mapper:
            mock_instance = Mock()
            mock_instance.generate_query_templates.return_value = {
                "hours": [
                    "What time do you close?",
                    "Are you open now?",
                    "What are your hours?",
                    "When do you close today?"
                ],
                "menu": [
                    "What food do you serve?",
                    "Do you have [dish]?",
                    "What's on the menu?",
                    "How much is [item]?"
                ]
            }
            mock_query_mapper.return_value = mock_instance
            
            result = mapper.generate_query_templates(restaurant_data)
            
            assert isinstance(result, dict)
            
            for content_type, templates in result.items():
                assert len(templates) >= 3  # Should have multiple variations
                
                # Should include question words
                question_words = ["what", "when", "where", "how", "do", "are", "is"]
                has_questions = any(
                    any(word in template.lower() for word in question_words)
                    for template in templates
                )
                assert has_questions


class TestIntentMappingResult:
    """Test the IntentMappingResult data structure."""
    
    def test_intent_result_creation(self):
        """Test IntentMappingResult can be created."""
        
        result = IntentMappingResult(
            mappings=[],
            categories={},
            confidence_score=0.8,
            processing_time=0.1
        )
        
        assert result.mappings == []
        assert result.categories == {}
        assert result.confidence_score == 0.8
        assert result.processing_time == 0.1
    
    def test_intent_result_validation(self):
        """Test IntentMappingResult validates its data."""
        
        # Should validate that mappings is a list
        with pytest.raises((ValueError, TypeError)):
            IntentMappingResult(
                mappings="not a list",  # Should be list
                categories={},
                confidence_score=0.8,
                processing_time=0.1
            )
        
        # Should validate confidence score range
        with pytest.raises((ValueError, TypeError)):
            IntentMappingResult(
                mappings=[],
                categories={},
                confidence_score=1.5,  # Should be <= 1.0
                processing_time=0.1
            )
    
    def test_intent_result_to_dict(self):
        """Test IntentMappingResult conversion to dictionary."""
        
        result = IntentMappingResult(
            mappings=[{"question": "test", "content": "test"}],
            categories={"discovery": {"description": "finding restaurants"}},
            confidence_score=0.9,
            processing_time=0.2
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "mappings" in result_dict
        assert "categories" in result_dict
        assert "confidence_score" in result_dict
        assert "processing_time" in result_dict