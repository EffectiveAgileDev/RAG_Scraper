"""Unit tests for QueryMapper - maps content chunks to customer query templates."""

import pytest
from unittest.mock import Mock, patch

# Import will fail until we implement - expected for RED phase
from src.customer_intent.query_mapper import QueryMapper
from src.customer_intent.query_template import QueryTemplate


class TestQueryMapper:
    """Test the QueryMapper class for content-to-query mapping."""
    
    def test_query_mapper_initialization(self):
        """Test QueryMapper can be initialized."""
        
        mapper = QueryMapper()
        assert mapper is not None
        assert hasattr(mapper, 'template_cache')
        assert hasattr(mapper, 'query_patterns')
    
    def test_map_chunks_to_queries(self):
        """Test mapping of semantic chunks to customer queries."""
        
        mapper = QueryMapper()
        semantic_chunks = [
            {
                "id": "chunk_1",
                "type": "menu_item",
                "content": "Coq au Vin - $28 - Braised chicken in red wine",
                "metadata": {"chunk_type": "menu", "item_category": "main_course"}
            },
            {
                "id": "chunk_2", 
                "type": "business_hours",
                "content": "Open Monday-Thursday 11:00-22:00, Friday-Saturday 11:00-23:00",
                "metadata": {"chunk_type": "hours", "temporal_type": "recurring_schedule"}
            },
            {
                "id": "chunk_3",
                "type": "location_info", 
                "content": "Located at 123 Main St, Downtown. Valet parking available.",
                "metadata": {"chunk_type": "location", "has_parking": True}
            }
        ]
        
        result = mapper.map_chunks_to_queries(semantic_chunks)
        
        assert isinstance(result, dict)
        
        expected_chunk_types = ["menu_item", "business_hours", "location_info"]
        for chunk_type in expected_chunk_types:
            assert chunk_type in result
            queries = result[chunk_type]
            assert len(queries) >= 3  # Should have multiple query variations
            
            # Verify query structure
            for query in queries:
                assert isinstance(query, str)
                assert len(query) > 0
    
    def test_generate_query_templates(self):
        """Test generation of query templates for different content types."""
        
        mapper = QueryMapper()
        restaurant_data = {
            "hours": {"monday": "11:00-22:00"},
            "menu": {"appetizers": ["Salad - $12"]},
            "location": {"address": "123 Main St"},
            "contact": {"phone": "555-1234"}
        }
        
        result = mapper.generate_query_templates(restaurant_data)
        
        assert isinstance(result, dict)
        
        for content_type in ["hours", "menu", "location", "contact"]:
            assert content_type in result
            templates = result[content_type]
            assert len(templates) >= 3
            
            # Should include question words
            question_words = ["what", "when", "where", "how", "do", "are", "is"]
            has_questions = any(
                any(word in template.lower() for word in question_words)
                for template in templates
            )
            assert has_questions
    
    def test_generate_natural_language_variations(self):
        """Test generation of natural language query variations."""
        
        mapper = QueryMapper()
        base_queries = [
            "What time do you close?",
            "Do you have vegetarian options?",
            "Where are you located?"
        ]
        
        variations = mapper.generate_variations(base_queries)
        
        assert isinstance(variations, dict)
        
        for base_query in base_queries:
            assert base_query in variations
            query_variations = variations[base_query]
            assert len(query_variations) >= 3
            
            # Should have different phrasings
            unique_variations = set(query_variations)
            assert len(unique_variations) == len(query_variations)  # No duplicates
    
    def test_map_menu_items_to_queries(self):
        """Test specific mapping of menu items to customer queries."""
        
        mapper = QueryMapper()
        menu_chunk = {
            "id": "menu_1",
            "type": "menu_item",
            "content": "Caesar Salad - $12 - Fresh romaine, parmesan, croutons",
            "metadata": {
                "item_name": "Caesar Salad",
                "price": "$12",
                "category": "appetizer",
                "ingredients": ["romaine", "parmesan", "croutons"]
            }
        }
        
        queries = mapper.map_menu_item_to_queries(menu_chunk)
        
        assert isinstance(queries, list)
        assert len(queries) > 0
        
        # Should generate different types of menu queries
        expected_patterns = [
            "do you have",  # availability
            "how much",     # price
            "what's in",    # ingredients
            "caesar salad"  # specific item
        ]
        
        query_text = " ".join(queries).lower()
        found_patterns = sum(1 for pattern in expected_patterns if pattern in query_text)
        assert found_patterns >= 2  # Should match at least 2 patterns
    
    def test_map_hours_to_queries(self):
        """Test specific mapping of business hours to customer queries."""
        
        mapper = QueryMapper()
        hours_chunk = {
            "id": "hours_1",
            "type": "business_hours",
            "content": "Open Monday-Friday 11:00-22:00, Saturday-Sunday 10:00-23:00",
            "metadata": {
                "temporal_type": "recurring_schedule",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            }
        }
        
        queries = mapper.map_hours_to_queries(hours_chunk)
        
        assert isinstance(queries, list)
        assert len(queries) > 0
        
        # Should generate time-related queries
        time_patterns = [
            "time",
            "open",
            "close",
            "hours"
        ]
        
        query_text = " ".join(queries).lower()
        found_patterns = sum(1 for pattern in time_patterns if pattern in query_text)
        assert found_patterns >= 2
    
    def test_map_location_to_queries(self):
        """Test specific mapping of location info to customer queries."""
        
        mapper = QueryMapper()
        location_chunk = {
            "id": "location_1",
            "type": "location_info",
            "content": "Located at 123 Main St, Downtown. Free parking available.",
            "metadata": {
                "address": "123 Main St",
                "neighborhood": "Downtown",
                "parking": True
            }
        }
        
        queries = mapper.map_location_to_queries(location_chunk)
        
        assert isinstance(queries, list)
        assert len(queries) > 0
        
        # Should generate location-related queries
        location_patterns = [
            "where",
            "address",
            "located",
            "parking"
        ]
        
        query_text = " ".join(queries).lower()
        found_patterns = sum(1 for pattern in location_patterns if pattern in query_text)
        assert found_patterns >= 2
    
    def test_handle_parameterized_queries(self):
        """Test handling of parameterized query templates."""
        
        mapper = QueryMapper()
        menu_data = {
            "appetizers": ["Caesar Salad", "French Onion Soup"],
            "main_courses": ["Coq au Vin", "Salmon Teriyaki"]
        }
        
        parameterized_queries = mapper.generate_parameterized_queries(menu_data)
        
        assert isinstance(parameterized_queries, list)
        assert len(parameterized_queries) > 0
        
        # Should include parameter placeholders
        has_parameters = any(
            "[" in query and "]" in query
            for query in parameterized_queries
        )
        assert has_parameters
        
        # Should generate specific instantiated queries
        instantiated_queries = mapper.instantiate_parameterized_queries(
            parameterized_queries, menu_data
        )
        
        assert len(instantiated_queries) > len(parameterized_queries)
        
        # Should include actual dish names
        query_text = " ".join(instantiated_queries).lower()
        assert "caesar salad" in query_text or "coq au vin" in query_text
    
    def test_query_template_scoring(self):
        """Test scoring of query templates by relevance and naturalness."""
        
        mapper = QueryMapper()
        query_candidates = [
            "What time do you close?",  # Natural, relevant
            "At what temporal point does your establishment cease operations?",  # Unnatural
            "Do you have pasta?",  # Natural, relevant
            "Query menu items database",  # Technical, unnatural
        ]
        
        chunk_context = {
            "type": "business_hours",
            "content": "Open Monday-Friday 11:00-22:00"
        }
        
        scored_queries = mapper.score_query_templates(query_candidates, chunk_context)
        
        assert isinstance(scored_queries, list)
        assert len(scored_queries) == len(query_candidates)
        
        for scored_query in scored_queries:
            assert "query" in scored_query
            assert "relevance_score" in scored_query
            assert "naturalness_score" in scored_query
            assert "overall_score" in scored_query
            
            # Scores should be in valid range
            assert 0.0 <= scored_query["relevance_score"] <= 1.0
            assert 0.0 <= scored_query["naturalness_score"] <= 1.0
            assert 0.0 <= scored_query["overall_score"] <= 1.0
        
        # Natural, relevant queries should score higher
        natural_query = next(sq for sq in scored_queries if "What time do you close" in sq["query"])
        technical_query = next(sq for sq in scored_queries if "Query menu items" in sq["query"])
        
        assert natural_query["overall_score"] > technical_query["overall_score"]
    
    def test_context_aware_query_generation(self):
        """Test context-aware query generation based on restaurant type."""
        
        mapper = QueryMapper()
        
        # Fine dining context
        fine_dining_context = {
            "restaurant_type": "fine_dining",
            "price_range": "$$$",
            "atmosphere": "upscale"
        }
        
        # Fast food context
        fast_food_context = {
            "restaurant_type": "fast_food",
            "price_range": "$",
            "service": "quick_service"
        }
        
        fine_dining_queries = mapper.generate_context_aware_queries(fine_dining_context)
        fast_food_queries = mapper.generate_context_aware_queries(fast_food_context)
        
        # Fine dining should include different query patterns
        fine_dining_text = " ".join(fine_dining_queries).lower()
        fine_dining_patterns = ["reservation", "dress code", "wine", "tasting"]
        fine_dining_matches = sum(1 for pattern in fine_dining_patterns if pattern in fine_dining_text)
        
        # Fast food should include different patterns
        fast_food_text = " ".join(fast_food_queries).lower()
        fast_food_patterns = ["drive through", "delivery", "quick", "value"]
        fast_food_matches = sum(1 for pattern in fast_food_patterns if pattern in fast_food_text)
        
        # Should have context-appropriate patterns
        assert fine_dining_matches > 0 or fast_food_matches > 0
    
    def test_temporal_query_mapping(self):
        """Test mapping of temporal content to time-based queries."""
        
        mapper = QueryMapper()
        temporal_chunks = [
            {
                "id": "daily_hours",
                "content": "Open today 11:00-22:00",
                "metadata": {"temporal_type": "real_time"}
            },
            {
                "id": "weekly_schedule", 
                "content": "Weekend hours: Saturday-Sunday 10:00-23:00",
                "metadata": {"temporal_type": "weekly"}
            },
            {
                "id": "special_event",
                "content": "Valentine's Day special menu February 14th",
                "metadata": {"temporal_type": "specific_date"}
            }
        ]
        
        temporal_queries = mapper.map_temporal_content_to_queries(temporal_chunks)
        
        assert isinstance(temporal_queries, dict)
        
        for chunk in temporal_chunks:
            chunk_id = chunk["id"]
            assert chunk_id in temporal_queries
            
            queries = temporal_queries[chunk_id]
            temporal_type = chunk["metadata"]["temporal_type"]
            
            # Should generate appropriate temporal queries
            query_text = " ".join(queries).lower()
            
            if temporal_type == "real_time":
                assert "now" in query_text or "today" in query_text
            elif temporal_type == "weekly":
                assert "weekend" in query_text or "saturday" in query_text or "sunday" in query_text
            elif temporal_type == "specific_date":
                assert "valentine" in query_text or "february" in query_text
    
    def test_export_query_mappings(self):
        """Test export of query mappings for RAG system integration."""
        
        mapper = QueryMapper()
        
        # Mock some query mappings
        mapper._mapping_cache = {
            "menu_items": ["What food do you serve?", "Do you have pasta?"],
            "hours": ["What time do you close?", "Are you open now?"],
            "location": ["Where are you located?", "What's your address?"]
        }
        
        export_result = mapper.export_query_mappings()
        
        assert isinstance(export_result, dict)
        assert "query_templates" in export_result
        assert "content_mappings" in export_result
        assert "metadata" in export_result
        
        # Should be in RAG-friendly format
        templates = export_result["query_templates"]
        assert isinstance(templates, dict)
        
        for content_type, queries in templates.items():
            assert isinstance(queries, list)
            assert len(queries) > 0


class TestQueryTemplate:
    """Test the QueryTemplate data structure."""
    
    def test_query_template_creation(self):
        """Test QueryTemplate can be created."""
        
        template = QueryTemplate(
            template="What time do you {action}?",
            parameters=["open", "close"],
            content_type="business_hours",
            naturalness_score=0.9
        )
        
        assert template.template == "What time do you {action}?"
        assert "open" in template.parameters
        assert "close" in template.parameters
        assert template.content_type == "business_hours"
        assert template.naturalness_score == 0.9
    
    def test_query_template_instantiation(self):
        """Test QueryTemplate instantiation with parameters."""
        
        template = QueryTemplate(
            template="Do you have {item}?",
            parameters=["pasta", "pizza", "salad"],
            content_type="menu_items",
            naturalness_score=0.8
        )
        
        instantiated_queries = template.instantiate()
        
        assert isinstance(instantiated_queries, list)
        assert len(instantiated_queries) == len(template.parameters)
        
        # Should replace placeholders with actual parameters
        assert "Do you have pasta?" in instantiated_queries
        assert "Do you have pizza?" in instantiated_queries
        assert "Do you have salad?" in instantiated_queries
    
    def test_query_template_validation(self):
        """Test QueryTemplate validates its data."""
        
        # Should validate naturalness score range
        with pytest.raises((ValueError, TypeError)):
            QueryTemplate(
                template="test {param}",
                parameters=["test"],
                content_type="test",
                naturalness_score=1.5  # Should be <= 1.0
            )
        
        # Should validate template has placeholders if parameters provided
        with pytest.raises((ValueError, TypeError)):
            QueryTemplate(
                template="static template",  # No placeholders
                parameters=["param1", "param2"],  # But has parameters
                content_type="test",
                naturalness_score=0.8
            )
    
    def test_query_template_to_dict(self):
        """Test QueryTemplate conversion to dictionary."""
        
        template = QueryTemplate(
            template="Where is {location}?",
            parameters=["restaurant", "parking", "entrance"],
            content_type="location",
            naturalness_score=0.85
        )
        
        template_dict = template.to_dict()
        
        assert isinstance(template_dict, dict)
        assert "template" in template_dict
        assert "parameters" in template_dict
        assert "content_type" in template_dict
        assert "naturalness_score" in template_dict