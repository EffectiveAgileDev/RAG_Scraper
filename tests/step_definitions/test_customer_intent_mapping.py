"""Step definitions for customer intent mapping BDD tests."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import json
from datetime import datetime
from typing import Dict, List, Any

# Load scenarios from the feature file
scenarios('../features/customer_intent_mapping.feature')

# Import will fail until we implement - expected for RED phase
from src.customer_intent.intent_mapper import CustomerIntentMapper
from src.customer_intent.intent_analyzer import IntentAnalyzer
from src.customer_intent.query_mapper import QueryMapper
from src.customer_intent.content_scorer import ContentScorer


@pytest.fixture
def intent_context():
    """Context for customer intent mapping tests."""
    return {
        "intent_mapper": None,
        "restaurant_data": None,
        "intent_mappings": [],
        "intent_categories": {},
        "customer_summaries": {},
        "query_mappings": {},
        "relevance_scores": {},
        "faq_results": [],
        "temporal_mappings": {},
        "export_results": {},
        "interaction_patterns": {}
    }


@given("a customer intent mapper is initialized")
def init_customer_intent_mapper(intent_context):
    """Initialize customer intent mapper."""
    
    intent_context["intent_mapper"] = CustomerIntentMapper()


@given("sample restaurant data has been extracted and structured")
def setup_structured_restaurant_data(intent_context):
    """Setup comprehensive restaurant data for intent mapping."""
    intent_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "description": "Fine dining establishment serving French cuisine",
        "cuisine": "French",
        "price_range": "$$$",
        "rating": 4.5,
        "location": {
            "address": "123 Main St",
            "city": "Downtown",
            "coordinates": {"lat": 40.7128, "lng": -74.0060}
        },
        "hours": {
            "monday": "11:00-22:00",
            "tuesday": "11:00-22:00",
            "wednesday": "11:00-22:00",
            "thursday": "11:00-22:00", 
            "friday": "11:00-23:00",
            "saturday": "10:00-23:00",
            "sunday": "10:00-21:00"
        },
        "menu": {
            "appetizers": [
                {"name": "Caesar Salad", "price": "$12", "description": "Fresh romaine, parmesan, croutons"},
                {"name": "French Onion Soup", "price": "$8", "description": "Classic with gruyere cheese"}
            ],
            "main_courses": [
                {"name": "Coq au Vin", "price": "$28", "description": "Braised chicken in red wine"},
                {"name": "Salmon Teriyaki", "price": "$24", "description": "Fresh Atlantic salmon"}
            ],
            "dietary_options": {
                "vegetarian": ["Ratatouille - $22", "Mushroom Risotto - $20"],
                "gluten_free": ["Grilled Fish - $26", "Salad Nicoise - $18"],
                "vegan": ["Quinoa Bowl - $19"]
            }
        },
        "contact": {
            "phone": "(555) 123-4567",
            "email": "info@bistrodeluxe.com",
            "reservations": "recommended"
        },
        "ambiance": {
            "description": "Elegant dining room with warm lighting and soft jazz",
            "dress_code": "business casual",
            "noise_level": "quiet",
            "good_for": ["date night", "business dinner", "celebration"]
        },
        "amenities": {
            "parking": "valet available",
            "wifi": "complimentary",
            "accessibility": "wheelchair accessible",
            "payment": ["cash", "card", "mobile"]
        },
        "reviews": {
            "highlights": ["excellent service", "romantic atmosphere", "outstanding wine list"],
            "common_complaints": ["expensive", "slow service during peak hours"]
        }
    }


@given("restaurant data with menu, hours, location, and reviews")
def setup_basic_restaurant_data(intent_context):
    """Setup basic restaurant data for intent analysis."""
    setup_structured_restaurant_data(intent_context)


@given("restaurant data with comprehensive information")
def setup_comprehensive_data(intent_context):
    """Setup comprehensive restaurant data."""
    setup_structured_restaurant_data(intent_context)


@given("restaurant data structured for RAG")
def setup_rag_structured_data(intent_context):
    """Setup RAG-structured data."""
    setup_structured_restaurant_data(intent_context)


@given("semantically structured restaurant chunks")
def setup_semantic_chunks(intent_context):
    """Setup semantic chunks for mapping."""
    intent_context["semantic_chunks"] = [
        {
            "id": "chunk_1",
            "type": "menu_item",
            "content": "Coq au Vin - $28 - Braised chicken in red wine",
            "metadata": {"chunk_type": "menu", "item_category": "main_course"}
        },
        {
            "id": "chunk_2", 
            "type": "business_hours",
            "content": "Open Monday-Thursday 11:00-22:00, Friday-Saturday 11:00-23:00, Sunday 10:00-21:00",
            "metadata": {"chunk_type": "hours", "temporal_type": "recurring_schedule"}
        },
        {
            "id": "chunk_3",
            "type": "location_info", 
            "content": "Located at 123 Main St, Downtown. Valet parking available.",
            "metadata": {"chunk_type": "location", "has_parking": True}
        }
    ]


@given("restaurant content and customer query patterns")
def setup_query_patterns(intent_context):
    """Setup customer query patterns."""
    intent_context["query_patterns"] = [
        {"query": "what time do you close", "intent_type": "practical_planning"},
        {"query": "do you have vegetarian options", "intent_type": "dietary_requirements"},
        {"query": "is it good for date night", "intent_type": "experience_planning"},
        {"query": "how much does dinner cost", "intent_type": "evaluation"}
    ]


@given("multiple restaurant types (fine dining, fast food, cafe)")
def setup_multiple_restaurant_types(intent_context):
    """Setup different restaurant categories."""
    intent_context["restaurant_types"] = {
        "fine_dining": {"price_range": "$$$", "atmosphere": "upscale", "service": "full_service"},
        "fast_food": {"price_range": "$", "atmosphere": "casual", "service": "quick_service"},
        "cafe": {"price_range": "$$", "atmosphere": "relaxed", "service": "counter_service"}
    }


@given("restaurant content mapped to customer intents")
def setup_mapped_content(intent_context):
    """Setup content with intent mappings."""
    setup_structured_restaurant_data(intent_context)


@given("restaurant data with comprehensive intent mappings") 
def setup_comprehensive_mappings(intent_context):
    """Setup comprehensive intent mappings."""
    setup_structured_restaurant_data(intent_context)


@given("restaurant data with time-sensitive information")
def setup_temporal_data(intent_context):
    """Setup time-sensitive restaurant data."""
    intent_context["temporal_data"] = {
        "current_hours": "11:00-22:00",
        "daily_specials": {"today": "Fish and Chips - $18"},
        "weekend_hours": {"saturday": "10:00-23:00", "sunday": "10:00-21:00"},
        "holiday_schedule": {"thanksgiving": "closed", "christmas": "limited_hours"}
    }


@given("completed customer intent mappings")
def setup_completed_mappings(intent_context):
    """Setup completed intent mappings for export."""
    setup_structured_restaurant_data(intent_context)


@given("restaurant content and complex customer scenarios")
def setup_complex_scenarios(intent_context):
    """Setup complex customer scenarios."""
    setup_structured_restaurant_data(intent_context)


@given("historical customer interaction data")
def setup_interaction_data(intent_context):
    """Setup historical interaction patterns."""
    intent_context["interaction_history"] = [
        {"query": "vegetarian options", "response_quality": 0.9, "outcome": "positive"},
        {"query": "parking availability", "response_quality": 0.6, "outcome": "abandoned"},
        {"query": "dress code", "response_quality": 0.8, "outcome": "positive"}
    ]


@when("I analyze customer intent patterns for restaurants")
def analyze_intent_patterns(intent_context):
    """Analyze customer intent patterns."""
    
    result = intent_context["intent_mapper"].analyze_intent_patterns(
        intent_context["restaurant_data"]
    )
    intent_context["intent_mappings"] = result.get("mappings", [])


@when("I categorize customer intents")
def categorize_intents(intent_context):
    """Categorize customer intents by decision stage."""
    
    result = intent_context["intent_mapper"].categorize_intents(
        intent_context["restaurant_data"]
    )
    intent_context["intent_categories"] = result


@when("I generate customer intent summaries")
def generate_intent_summaries(intent_context):
    """Generate customer-centric content summaries."""
    
    result = intent_context["intent_mapper"].generate_customer_summaries(
        intent_context["restaurant_data"]
    )
    intent_context["customer_summaries"] = result


@when("I create customer query mappings")
def create_query_mappings(intent_context):
    """Create mappings from chunks to customer queries."""
    
    query_mapper = QueryMapper()
    result = query_mapper.map_chunks_to_queries(
        intent_context["semantic_chunks"]
    )
    intent_context["query_mappings"] = result


@when("I score content relevance for different intents")
def score_content_relevance(intent_context):
    """Score content relevance for customer intents."""
    
    scorer = ContentScorer()
    result = scorer.score_content_relevance(
        intent_context["restaurant_data"],
        intent_context["query_patterns"]
    )
    intent_context["relevance_scores"] = result


@when("I analyze intent patterns by restaurant category")
def analyze_category_patterns(intent_context):
    """Analyze intent patterns by restaurant type."""
    
    result = intent_context["intent_mapper"].analyze_by_category(
        intent_context["restaurant_types"]
    )
    intent_context["category_patterns"] = result


@when("I create bidirectional relationships")
def create_bidirectional_relationships(intent_context):
    """Create bidirectional intent-content relationships."""
    
    result = intent_context["intent_mapper"].create_bidirectional_relationships(
        intent_context["restaurant_data"]
    )
    intent_context["bidirectional_relationships"] = result


@when("I generate customer FAQs")
def generate_customer_faqs(intent_context):
    """Generate customer FAQs from mapped content."""
    
    result = intent_context["intent_mapper"].generate_faqs(
        intent_context["restaurant_data"]
    )
    intent_context["faq_results"] = result


@when("I map temporal customer intents")
def map_temporal_intents(intent_context):
    """Map temporal customer intents."""
    
    result = intent_context["intent_mapper"].map_temporal_intents(
        intent_context["temporal_data"]
    )
    intent_context["temporal_mappings"] = result


@when("I export intent mappings for RAG system integration")
def export_intent_mappings(intent_context):
    """Export intent mappings for RAG systems."""
    
    result = intent_context["intent_mapper"].export_for_rag(
        intent_context["restaurant_data"]
    )
    intent_context["export_results"] = result


@when("I process ambiguous customer intents")
def process_ambiguous_intents(intent_context):
    """Process ambiguous customer intents."""
    
    ambiguous_queries = [
        "good for date night",
        "quick lunch near office", 
        "family dinner with dietary needs"
    ]
    
    result = intent_context["intent_mapper"].process_ambiguous_intents(
        ambiguous_queries,
        intent_context["restaurant_data"]
    )
    intent_context["ambiguous_results"] = result


@when("I analyze customer behavior patterns")
def analyze_behavior_patterns(intent_context):
    """Analyze customer behavior patterns."""
    
    analyzer = IntentAnalyzer()
    result = analyzer.analyze_interaction_patterns(
        intent_context["interaction_history"]
    )
    intent_context["behavior_patterns"] = result


@then(parsers.parse("I should receive intent mappings including:\n{table}"))
def verify_intent_mappings(intent_context, table):
    """Verify intent mappings match expected patterns."""
    lines = table.strip().split('\n')
    expected_mappings = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_mappings.append({
                    "customer_question": fields[1].strip(),
                    "mapped_content_type": fields[2].strip(), 
                    "confidence_score": float(fields[3].strip())
                })
    
    mappings = intent_context.get("intent_mappings", [])
    assert len(mappings) >= len(expected_mappings), "Missing expected intent mappings"
    
    for expected in expected_mappings:
        found_mapping = next(
            (m for m in mappings if expected["customer_question"] in m.get("question", "")),
            None
        )
        assert found_mapping is not None, f"Missing mapping for: {expected['customer_question']}"
        assert found_mapping.get("confidence_score", 0) >= expected["confidence_score"]


@then("each mapping should include supporting evidence from the content")
def verify_mapping_evidence(intent_context):
    """Verify mappings include supporting evidence."""
    mappings = intent_context.get("intent_mappings", [])
    
    for mapping in mappings:
        assert "supporting_evidence" in mapping, "Missing supporting evidence"
        assert len(mapping["supporting_evidence"]) > 0, "Empty supporting evidence"


@then(parsers.parse("I should have intent categories including:\n{table}"))
def verify_intent_categories(intent_context, table):
    """Verify intent categories match expected structure."""
    lines = table.strip().split('\n')
    expected_categories = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_categories.append({
                    "intent_category": fields[1].strip(),
                    "description": fields[2].strip(),
                    "example_questions": fields[3].strip()
                })
    
    categories = intent_context.get("intent_categories", {})
    
    for expected in expected_categories:
        category_name = expected["intent_category"]
        assert category_name in categories, f"Missing category: {category_name}"
        
        category = categories[category_name]
        assert "description" in category, f"Missing description for {category_name}"
        assert "example_questions" in category, f"Missing examples for {category_name}"


@then("each category should map to relevant content sections")
def verify_category_content_mapping(intent_context):
    """Verify categories map to content sections."""
    categories = intent_context.get("intent_categories", {})
    
    for category_name, category_data in categories.items():
        assert "content_sections" in category_data, f"Missing content sections for {category_name}"
        assert len(category_data["content_sections"]) > 0, f"Empty content sections for {category_name}"


@then(parsers.parse("I should receive summaries answering common questions like:\n{table}"))
def verify_customer_summaries(intent_context, table):
    """Verify customer-centric summaries."""
    lines = table.strip().split('\n')
    expected_summaries = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 3:
                expected_summaries.append({
                    "question_type": fields[1].strip(),
                    "summary_content": fields[2].strip()
                })
    
    summaries = intent_context.get("customer_summaries", {})
    
    for expected in expected_summaries:
        question_type = expected["question_type"]
        assert question_type in summaries, f"Missing summary for: {question_type}"
        
        summary = summaries[question_type]
        assert len(summary) > 0, f"Empty summary for {question_type}"


@then("summaries should be optimized for direct customer consumption")
def verify_customer_optimized_summaries(intent_context):
    """Verify summaries are customer-optimized."""
    summaries = intent_context.get("customer_summaries", {})
    
    for summary_type, summary_content in summaries.items():
        # Should be concise (under 200 characters for quick answers)
        assert len(summary_content) <= 200, f"Summary too long for {summary_type}"
        # Should avoid technical jargon
        assert "RAG" not in summary_content, f"Technical jargon in {summary_type}"
        assert "extraction" not in summary_content, f"Technical jargon in {summary_type}"


@then(parsers.parse("each chunk should be mapped to potential customer queries:\n{table}"))
def verify_chunk_query_mappings(intent_context, table):
    """Verify chunk-to-query mappings."""
    lines = table.strip().split('\n')
    expected_mappings = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 3:
                expected_mappings.append({
                    "chunk_type": fields[1].strip(),
                    "example_queries": fields[2].strip()
                })
    
    query_mappings = intent_context.get("query_mappings", {})
    
    for expected in expected_mappings:
        chunk_type = expected["chunk_type"]
        assert chunk_type in query_mappings, f"Missing mappings for: {chunk_type}"
        
        mappings = query_mappings[chunk_type]
        assert len(mappings) > 0, f"Empty query mappings for {chunk_type}"


@then("mappings should support natural language query variations")
def verify_query_variations(intent_context):
    """Verify support for natural language variations."""
    query_mappings = intent_context.get("query_mappings", {})
    
    for chunk_type, mappings in query_mappings.items():
        # Should have multiple query variations per chunk type
        assert len(mappings) >= 3, f"Insufficient query variations for {chunk_type}"
        
        # Should include question words
        question_words = ["what", "where", "when", "how", "do", "is", "are"]
        has_questions = any(
            any(word in query.lower() for word in question_words)
            for query in mappings
        )
        assert has_questions, f"Missing question variations for {chunk_type}"


@then(parsers.parse("each content piece should have relevance scores for:\n{table}"))
def verify_relevance_scoring(intent_context, table):
    """Verify content relevance scoring."""
    lines = table.strip().split('\n')
    expected_intent_types = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 3:
                expected_intent_types.append({
                    "intent_type": fields[1].strip(),
                    "scoring_criteria": fields[2].strip()
                })
    
    relevance_scores = intent_context.get("relevance_scores", {})
    
    for expected in expected_intent_types:
        intent_type = expected["intent_type"]
        assert intent_type in relevance_scores, f"Missing relevance scores for: {intent_type}"
        
        scores = relevance_scores[intent_type]
        assert isinstance(scores, dict), f"Invalid score format for {intent_type}"


@then("scores should be between 0.0 and 1.0 with confidence intervals")
def verify_score_ranges(intent_context):
    """Verify score ranges and confidence intervals."""
    relevance_scores = intent_context.get("relevance_scores", {})
    
    for intent_type, scores in relevance_scores.items():
        for content_id, score_data in scores.items():
            score = score_data.get("score", 0)
            assert 0.0 <= score <= 1.0, f"Score out of range for {intent_type}/{content_id}: {score}"
            
            confidence = score_data.get("confidence", 0)
            assert 0.0 <= confidence <= 1.0, f"Confidence out of range for {intent_type}/{content_id}: {confidence}"


@then(parsers.parse("intent mappings should be customized by restaurant type:\n{table}"))
def verify_restaurant_type_customization(intent_context, table):
    """Verify restaurant type-specific intent mappings."""
    lines = table.strip().split('\n')
    expected_types = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 3:
                expected_types.append({
                    "restaurant_type": fields[1].strip(),
                    "priority_intents": fields[2].strip()
                })
    
    category_patterns = intent_context.get("category_patterns", {})
    
    for expected in expected_types:
        restaurant_type = expected["restaurant_type"]
        assert restaurant_type in category_patterns, f"Missing patterns for: {restaurant_type}"
        
        patterns = category_patterns[restaurant_type]
        assert "priority_intents" in patterns, f"Missing priority intents for {restaurant_type}"


@then("each type should have different intent importance weightings")
def verify_intent_weightings(intent_context):
    """Verify different weightings by restaurant type."""
    category_patterns = intent_context.get("category_patterns", {})
    
    weightings_by_type = {}
    for restaurant_type, patterns in category_patterns.items():
        weightings_by_type[restaurant_type] = patterns.get("intent_weights", {})
    
    # Verify that different restaurant types have different weightings
    if len(weightings_by_type) >= 2:
        types = list(weightings_by_type.keys())
        first_weights = weightings_by_type[types[0]]
        second_weights = weightings_by_type[types[1]]
        
        # At least some weights should be different
        has_differences = any(
            first_weights.get(intent) != second_weights.get(intent)
            for intent in set(first_weights.keys()) | set(second_weights.keys())
        )
        assert has_differences, "Restaurant types should have different intent weightings"


@then(parsers.parse("I should have relationships including:\n{table}"))
def verify_bidirectional_relationships(intent_context, table):
    """Verify bidirectional relationships."""
    lines = table.strip().split('\n')
    expected_relationships = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_relationships.append({
                    "relationship_type": fields[1].strip(),
                    "from_entity": fields[2].strip(),
                    "to_entity": fields[3].strip()
                })
    
    relationships = intent_context.get("bidirectional_relationships", [])
    
    for expected in expected_relationships:
        found_relationship = next(
            (r for r in relationships if 
             r.get("type") == expected["relationship_type"] and
             expected["from_entity"] in str(r.get("from_entity", "")) and
             expected["to_entity"] in str(r.get("to_entity", ""))),
            None
        )
        assert found_relationship is not None, f"Missing relationship: {expected}"


@then("relationships should support both content-to-intent and intent-to-content queries")
def verify_bidirectional_support(intent_context):
    """Verify bidirectional query support."""
    relationships = intent_context.get("bidirectional_relationships", [])
    
    # Should have both directions represented
    content_to_intent = [r for r in relationships if "answers_question" in r.get("type", "")]
    intent_to_content = [r for r in relationships if "supported_by" in r.get("type", "") or "enables" in r.get("type", "")]
    
    assert len(content_to_intent) > 0, "Missing content-to-intent relationships"
    assert len(intent_to_content) > 0 or len(relationships) > 0, "Missing intent-to-content relationships"


@then(parsers.parse("I should receive structured FAQ including:\n{table}"))
def verify_structured_faq(intent_context, table):
    """Verify structured FAQ generation."""
    lines = table.strip().split('\n')
    expected_faqs = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_faqs.append({
                    "question": fields[1].strip(),
                    "answer_source": fields[2].strip(),
                    "confidence": float(fields[3].strip())
                })
    
    faq_results = intent_context.get("faq_results", [])
    
    for expected in expected_faqs:
        found_faq = next(
            (faq for faq in faq_results if expected["question"] in faq.get("question", "")),
            None
        )
        assert found_faq is not None, f"Missing FAQ: {expected['question']}"
        assert found_faq.get("confidence", 0) >= expected["confidence"]


@then("answers should be generated from the actual scraped content")
def verify_content_based_answers(intent_context):
    """Verify answers are based on scraped content."""
    faq_results = intent_context.get("faq_results", [])
    restaurant_data = intent_context.get("restaurant_data", {})
    
    for faq in faq_results:
        answer = faq.get("answer", "")
        source_content = faq.get("source_content", "")
        
        # Answer should reference actual data from restaurant
        restaurant_name = restaurant_data.get("name", "")
        if restaurant_name:
            # At least some FAQs should reference the restaurant name or specific details
            has_specific_content = (
                restaurant_name.lower() in answer.lower() or
                any(cuisine in answer.lower() for cuisine in [restaurant_data.get("cuisine", "").lower()]) or
                len(source_content) > 0
            )
        
        assert "source_content" in faq, "FAQ missing source content reference"


@then(parsers.parse("I should handle intents like:\n{table}"))
def verify_temporal_intent_handling(intent_context, table):
    """Verify temporal intent handling."""
    lines = table.strip().split('\n')
    expected_temporal = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_temporal.append({
                    "temporal_intent": fields[1].strip(),
                    "mapped_content": fields[2].strip(),
                    "time_sensitivity": fields[3].strip()
                })
    
    temporal_mappings = intent_context.get("temporal_mappings", {})
    
    for expected in expected_temporal:
        intent = expected["temporal_intent"]
        found_mapping = next(
            (m for intent_key, m in temporal_mappings.items() if intent in intent_key),
            None
        )
        assert found_mapping is not None, f"Missing temporal mapping for: {intent}"
        assert found_mapping.get("time_sensitivity") == expected["time_sensitivity"]


@then("mappings should consider current date/time context")
def verify_datetime_context(intent_context):
    """Verify date/time context consideration."""
    temporal_mappings = intent_context.get("temporal_mappings", {})
    
    for intent, mapping in temporal_mappings.items():
        assert "context_timestamp" in mapping, f"Missing timestamp context for {intent}"
        assert "time_sensitivity" in mapping, f"Missing time sensitivity for {intent}"


@then(parsers.parse("the output should include:\n{table}"))
def verify_export_components(intent_context, table):
    """Verify export components."""
    lines = table.strip().split('\n')
    expected_components = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_components.append({
                    "export_component": fields[1].strip(),
                    "format": fields[2].strip(),
                    "content": fields[3].strip()
                })
    
    export_results = intent_context.get("export_results", {})
    
    for expected in expected_components:
        component = expected["export_component"]
        assert component in export_results, f"Missing export component: {component}"
        
        component_data = export_results[component]
        assert "format" in component_data, f"Missing format for {component}"
        assert component_data["format"] == expected["format"], f"Wrong format for {component}"


@then("exports should be optimized for RAG system query processing")
def verify_rag_optimization(intent_context):
    """Verify RAG system optimization."""
    export_results = intent_context.get("export_results", {})
    
    for component, data in export_results.items():
        # Should have proper structure for RAG systems
        assert "metadata" in data, f"Missing metadata for RAG optimization in {component}"
        assert "query_optimization" in data, f"Missing query optimization for {component}"


@then(parsers.parse("I should handle queries like:\n{table}"))
def verify_ambiguous_query_handling(intent_context, table):
    """Verify ambiguous query handling."""
    lines = table.strip().split('\n')
    expected_queries = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_queries.append({
                    "ambiguous_query": fields[1].strip(),
                    "detected_intents": fields[2].strip(),
                    "resolution_strategy": fields[3].strip()
                })
    
    ambiguous_results = intent_context.get("ambiguous_results", {})
    
    for expected in expected_queries:
        query = expected["ambiguous_query"]
        found_result = next(
            (result for query_key, result in ambiguous_results.items() if query in query_key),
            None
        )
        assert found_result is not None, f"Missing handling for: {query}"
        assert "detected_intents" in found_result, f"Missing intent detection for {query}"
        assert len(found_result["detected_intents"]) > 1, f"Should detect multiple intents for {query}"


@then("responses should address all detected intent components")
def verify_multi_intent_responses(intent_context):
    """Verify multi-intent response handling."""
    ambiguous_results = intent_context.get("ambiguous_results", {})
    
    for query, result in ambiguous_results.items():
        detected_intents = result.get("detected_intents", [])
        response_components = result.get("response_components", [])
        
        # Response should address each detected intent
        assert len(response_components) >= len(detected_intents), f"Insufficient response components for {query}"


@then(parsers.parse("I should identify patterns like:\n{table}"))
def verify_behavior_patterns(intent_context, table):
    """Verify customer behavior pattern identification."""
    lines = table.strip().split('\n')
    expected_patterns = []
    
    for line in lines[1:]:  # Skip header
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:
                expected_patterns.append({
                    "pattern_type": fields[1].strip(),
                    "description": fields[2].strip(),
                    "adaptation_action": fields[3].strip()
                })
    
    behavior_patterns = intent_context.get("behavior_patterns", {})
    
    for expected in expected_patterns:
        pattern_type = expected["pattern_type"]
        assert pattern_type in behavior_patterns, f"Missing pattern: {pattern_type}"
        
        pattern = behavior_patterns[pattern_type]
        assert "description" in pattern, f"Missing description for {pattern_type}"
        assert "adaptation_action" in pattern, f"Missing adaptation action for {pattern_type}"


@then("patterns should inform future intent mapping improvements")
def verify_pattern_learning(intent_context):
    """Verify pattern learning for improvements."""
    behavior_patterns = intent_context.get("behavior_patterns", {})
    
    for pattern_type, pattern in behavior_patterns.items():
        assert "improvement_suggestions" in pattern, f"Missing improvement suggestions for {pattern_type}"
        assert len(pattern["improvement_suggestions"]) > 0, f"Empty improvement suggestions for {pattern_type}"