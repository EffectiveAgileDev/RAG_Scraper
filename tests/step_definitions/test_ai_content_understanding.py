"""Step definitions for AI-powered content understanding features."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, List, Any

# Load all scenarios from the feature file
scenarios("../features/ai_content_understanding.feature")


@pytest.fixture
def ai_content_analyzer():
    """Fixture for AI content analyzer instance."""
    from src.ai.content_analyzer import AIContentAnalyzer
    return AIContentAnalyzer()


@pytest.fixture
def mock_openai_response():
    """Fixture for mocked OpenAI API responses."""
    return Mock()


@pytest.fixture
def extraction_context():
    """Fixture to store extraction context between steps."""
    return {
        "webpage_content": "",
        "menu_items": [],
        "prices": [],
        "location": "",
        "results": {},
        "api_configured": False,
        "existing_data": {}
    }


# Background steps
@given("the AI content understanding module is initialized")
def ai_module_initialized(ai_content_analyzer, extraction_context):
    """Initialize the AI content understanding module."""
    assert ai_content_analyzer is not None
    extraction_context["analyzer"] = ai_content_analyzer


@given("the OpenAI API is configured")
def openai_configured(extraction_context, mock_openai_response):
    """Configure OpenAI API with mock."""
    extraction_context["api_configured"] = True
    extraction_context["mock_api"] = mock_openai_response


@given("the Restaurant industry configuration is loaded")
def restaurant_config_loaded(extraction_context):
    """Load restaurant industry configuration."""
    extraction_context["industry"] = "Restaurant"
    extraction_context["config"] = {
        "categories": ["menu", "prices", "cuisine", "dietary"],
        "extraction_prompts": {}
    }


# Scenario: Enhance menu items with nutritional context
@given("a restaurant webpage with menu items")
def webpage_with_menu(extraction_context):
    """Set up a webpage with menu items."""
    extraction_context["webpage_content"] = """
    <h2>Our Menu</h2>
    <div class="menu-item">
        <h3>Caesar Salad</h3>
        <p>Fresh romaine lettuce with our house-made Caesar dressing</p>
    </div>
    <div class="menu-item">
        <h3>Bacon Cheeseburger</h3>
        <p>1/2 lb beef patty with crispy bacon and melted cheddar</p>
    </div>
    """


@given('the menu contains items like "Caesar Salad" and "Bacon Cheeseburger"')
def menu_contains_items(extraction_context):
    """Verify menu contains specific items."""
    extraction_context["menu_items"] = [
        {"name": "Caesar Salad", "description": "Fresh romaine lettuce with our house-made Caesar dressing"},
        {"name": "Bacon Cheeseburger", "description": "1/2 lb beef patty with crispy bacon and melted cheddar"}
    ]


@when("I run the AI content understanding analysis")
def run_ai_analysis(extraction_context):
    """Run AI content understanding analysis."""
    analyzer = extraction_context["analyzer"]
    results = analyzer.analyze_content(
        content=extraction_context["webpage_content"],
        menu_items=extraction_context.get("menu_items", []),
        analysis_type="nutritional"
    )
    extraction_context["results"] = results


@then("the result should include nutritional context for each menu item")
def check_nutritional_context(extraction_context):
    """Verify nutritional context is included."""
    results = extraction_context["results"]
    assert "nutritional_context" in results
    assert len(results["nutritional_context"]) == len(extraction_context["menu_items"])


@then(parsers.parse('"{item}" should have tags like {tags}'))
def check_item_tags(extraction_context, item: str, tags: str):
    """Verify specific item has expected tags."""
    tags_list = json.loads(tags)
    results = extraction_context["results"]
    item_data = next((i for i in results["nutritional_context"] if i["name"] == item), None)
    assert item_data is not None
    assert all(tag in item_data["tags"] for tag in tags_list)


@then("each item should have estimated calorie ranges")
def check_calorie_ranges(extraction_context):
    """Verify calorie ranges are provided."""
    results = extraction_context["results"]
    for item in results["nutritional_context"]:
        assert "calorie_range" in item
        assert "min" in item["calorie_range"]
        assert "max" in item["calorie_range"]


@then("dietary restrictions should be identified (gluten-free, vegan, etc.)")
def check_dietary_restrictions(extraction_context):
    """Verify dietary restrictions are identified."""
    results = extraction_context["results"]
    assert "dietary_restrictions" in results
    

# Scenario: Analyze price ranges
@given("a restaurant webpage with menu prices")
def webpage_with_prices(extraction_context):
    """Set up webpage with menu prices."""
    extraction_context["webpage_content"] = """
    <div class="menu">
        <div class="item">Appetizer - $12</div>
        <div class="item">Steak Dinner - $45</div>
        <div class="item">Pasta - $18</div>
    </div>
    """


@given(parsers.parse('the menu shows entrees ranging from ${min_price} to ${max_price}'))
def menu_price_range(extraction_context, min_price: str, max_price: str):
    """Set menu price range."""
    extraction_context["prices"] = {
        "min": float(min_price),
        "max": float(max_price),
        "items": [
            {"name": "Appetizer", "price": 12},
            {"name": "Steak Dinner", "price": 45},
            {"name": "Pasta", "price": 18}
        ]
    }


@given(parsers.parse('the restaurant is located in "{location}"'))
def restaurant_location(extraction_context, location: str):
    """Set restaurant location."""
    extraction_context["location"] = location


@when("I run the AI price analysis")
def run_price_analysis(extraction_context):
    """Run AI price analysis."""
    analyzer = extraction_context["analyzer"]
    results = analyzer.analyze_prices(
        prices=extraction_context["prices"],
        location=extraction_context["location"]
    )
    extraction_context["results"] = results


@then("the result should include overall price tier classification")
def check_price_tier(extraction_context):
    """Verify price tier classification."""
    results = extraction_context["results"]
    assert "price_tier" in results
    assert results["price_tier"] in ["budget", "moderate", "upscale", "fine-dining"]


@then(parsers.parse('the price tier should be "{tier}" based on location and prices'))
def verify_price_tier(extraction_context, tier: str):
    """Verify specific price tier."""
    results = extraction_context["results"]
    assert results["price_tier"] == tier


@then("competitive positioning analysis should be provided")
def check_competitive_analysis(extraction_context):
    """Verify competitive positioning analysis."""
    results = extraction_context["results"]
    assert "competitive_positioning" in results
    assert "market_position" in results["competitive_positioning"]


@then("value proposition insights should be generated")
def check_value_proposition(extraction_context):
    """Verify value proposition insights."""
    results = extraction_context["results"]
    assert "value_proposition" in results


@then("price-to-portion expectations should be estimated")
def check_portion_expectations(extraction_context):
    """Verify price-to-portion expectations."""
    results = extraction_context["results"]
    assert "portion_expectations" in results


# Scenario: Classify cuisine with cultural context
@given(parsers.parse('a restaurant webpage describing "{cuisine_description}"'))
def webpage_with_cuisine(extraction_context, cuisine_description: str):
    """Set up webpage with cuisine description."""
    extraction_context["webpage_content"] = f"""
    <div class="about">
        <h2>About Us</h2>
        <p>We specialize in {cuisine_description}</p>
    </div>
    """
    extraction_context["cuisine_description"] = cuisine_description


@given('the menu contains items like "Korean BBQ Tacos" and "Miso Ramen"')
def menu_with_fusion_items(extraction_context):
    """Set menu with fusion items."""
    extraction_context["menu_items"] = [
        {"name": "Korean BBQ Tacos", "description": "Marinated bulgogi beef in soft corn tortillas"},
        {"name": "Miso Ramen", "description": "Rich miso broth with handmade noodles"}
    ]


@when("I run the AI cuisine classification")
def run_cuisine_classification(extraction_context):
    """Run AI cuisine classification."""
    analyzer = extraction_context["analyzer"]
    results = analyzer.classify_cuisine(
        content=extraction_context["webpage_content"],
        menu_items=extraction_context.get("menu_items", [])
    )
    extraction_context["results"] = results


@then(parsers.parse('the primary cuisine should be identified as "{cuisine}"'))
def check_primary_cuisine(extraction_context, cuisine: str):
    """Verify primary cuisine identification."""
    results = extraction_context["results"]
    assert "primary_cuisine" in results
    assert results["primary_cuisine"] == cuisine


@then(parsers.parse('cuisine influences should include {influences}'))
def check_cuisine_influences(extraction_context, influences: str):
    """Verify cuisine influences."""
    influences_list = json.loads(influences)
    results = extraction_context["results"]
    assert "cuisine_influences" in results
    assert all(inf in results["cuisine_influences"] for inf in influences_list)


@then("cultural context should explain fusion elements")
def check_cultural_context(extraction_context):
    """Verify cultural context explanation."""
    results = extraction_context["results"]
    assert "cultural_context" in results
    assert len(results["cultural_context"]) > 0


@then("authenticity indicators should be provided")
def check_authenticity(extraction_context):
    """Verify authenticity indicators."""
    results = extraction_context["results"]
    assert "authenticity_score" in results
    assert "authenticity_indicators" in results


@then("related cuisine tags should be suggested for search optimization")
def check_cuisine_tags(extraction_context):
    """Verify cuisine tags for SEO."""
    results = extraction_context["results"]
    assert "cuisine_tags" in results
    assert len(results["cuisine_tags"]) > 0


# Additional scenario steps would continue here...
# Implementing remaining scenarios following the same pattern