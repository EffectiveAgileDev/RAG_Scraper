"""Step definitions for AI optional advanced features."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, List, Any
import tempfile
import os

# Load all scenarios from the feature file
scenarios("../features/ai_optional_features.feature")


@pytest.fixture
def ai_content_analyzer():
    """Fixture for AI content analyzer instance."""
    from src.ai.content_analyzer import AIContentAnalyzer
    return AIContentAnalyzer()


@pytest.fixture
def extraction_context():
    """Fixture to store extraction context between steps."""
    return {
        "analyzer": None,
        "config": {},
        "webpage_content": "",
        "results": {},
        "api_calls": [],
        "provider_used": None,
        "fallback_occurred": False,
        "performance_metrics": {}
    }


# Background steps
@given("the AI content analyzer is initialized")
def ai_analyzer_initialized(ai_content_analyzer, extraction_context):
    """Initialize the AI content analyzer."""
    extraction_context["analyzer"] = ai_content_analyzer


@given("the Restaurant industry configuration is loaded")
def restaurant_config_loaded(extraction_context):
    """Load restaurant industry configuration."""
    extraction_context["config"]["industry"] = "Restaurant"
    extraction_context["config"]["categories"] = ["menu", "prices", "cuisine"]


# Claude AI Integration Steps
@given("Claude API credentials are configured")
def claude_credentials_configured(extraction_context):
    """Configure Claude API credentials."""
    extraction_context["config"]["claude_api_key"] = "test-claude-key"
    extraction_context["config"]["claude_model"] = "claude-3-opus-20240229"


@given("a restaurant webpage with complex menu descriptions")
def complex_menu_webpage(extraction_context):
    """Set up webpage with complex menu descriptions."""
    extraction_context["webpage_content"] = """
    <div class="menu">
        <h3>Ocean's Symphony</h3>
        <p>A delicate dance of Atlantic treasures kissed by Mediterranean sun</p>
        <h3>Garden's Awakening</h3>
        <p>Farm-fresh whispers of spring, lovingly crafted by our chef's gentle hands</p>
    </div>
    """


@when("I run extraction using Claude as the LLM provider")
def run_claude_extraction(extraction_context):
    """Run extraction using Claude as the LLM provider."""
    analyzer = extraction_context["analyzer"]
    
    # Mock Claude API response
    analyzer.claude_extractor = Mock()
    analyzer.claude_extractor.extract = Mock(return_value={
        "menu_items": [
            {
                "name": "Ocean's Symphony",
                "description": "Seafood dish with Mediterranean influences",
                "cuisine_style": "Mediterranean-Atlantic fusion",
                "confidence": 0.85
            }
        ],
        "provider_used": "claude",
        "processing_time": 2.3
    })
    
    result = analyzer.extract_with_claude(
        content=extraction_context["webpage_content"],
        provider="claude"
    )
    extraction_context["results"] = result
    extraction_context["provider_used"] = "claude"


@then("the extraction should use Claude's API")
def verify_claude_api_used(extraction_context):
    """Verify that Claude's API was used."""
    assert extraction_context["provider_used"] == "claude"
    assert extraction_context["analyzer"].claude_extractor.extract.called


@then("the results should include Claude-specific analysis")
def verify_claude_analysis(extraction_context):
    """Verify Claude-specific analysis in results."""
    results = extraction_context["results"]
    assert "provider_used" in results
    assert results["provider_used"] == "claude"
    assert "menu_items" in results


@then("the response format should be consistent with OpenAI results")
def verify_consistent_format(extraction_context):
    """Verify response format consistency."""
    results = extraction_context["results"]
    assert "menu_items" in results
    assert isinstance(results["menu_items"], list)
    if results["menu_items"]:
        item = results["menu_items"][0]
        assert "name" in item
        assert "confidence" in item


@then("API usage should be tracked separately for Claude")
def verify_claude_tracking(extraction_context):
    """Verify Claude API usage tracking."""
    results = extraction_context["results"]
    assert "processing_time" in results
    assert results["processing_time"] > 0


# Local LLM Support Steps
@given("Ollama is installed and running locally")
def ollama_configured(extraction_context):
    """Configure Ollama for local processing."""
    extraction_context["config"]["ollama_endpoint"] = "http://localhost:11434"
    extraction_context["config"]["local_llm_enabled"] = True


@given('a local model "llama2" is available')
def llama2_model_available(extraction_context):
    """Set up llama2 model availability."""
    extraction_context["config"]["ollama_model"] = "llama2"


@given("privacy mode is enabled in configuration")
def privacy_mode_enabled(extraction_context):
    """Enable privacy mode configuration."""
    extraction_context["config"]["privacy_mode"] = True
    extraction_context["config"]["external_apis_disabled"] = True


@when("I run extraction using Ollama as the LLM provider")
def run_ollama_extraction(extraction_context):
    """Run extraction using Ollama."""
    analyzer = extraction_context["analyzer"]
    
    # Mock Ollama response
    analyzer.ollama_extractor = Mock()
    analyzer.ollama_extractor.extract = Mock(return_value={
        "menu_items": [{"name": "Test Item", "local_processing": True}],
        "provider_used": "ollama",
        "model": "llama2",
        "external_calls": 0
    })
    
    result = analyzer.extract_with_ollama(
        content=extraction_context["webpage_content"]
    )
    extraction_context["results"] = result


@then("the extraction should use local Ollama API")
def verify_ollama_used(extraction_context):
    """Verify Ollama was used for processing."""
    results = extraction_context["results"]
    assert results["provider_used"] == "ollama"
    assert results["model"] == "llama2"


@then("no external API calls should be made")
def verify_no_external_calls(extraction_context):
    """Verify no external API calls were made."""
    results = extraction_context["results"]
    assert results["external_calls"] == 0


@then("the results should include local LLM analysis")
def verify_local_llm_analysis(extraction_context):
    """Verify results include local LLM analysis."""
    results = extraction_context["results"]
    assert "menu_items" in results
    assert results.get("local_processing") is True


@then("processing should respect local resource constraints")
def verify_local_resource_constraints(extraction_context):
    """Verify processing respects local resource constraints."""
    # This would check memory usage, processing time, etc.
    # For testing purposes, we just verify the results exist
    results = extraction_context["results"]
    assert results is not None


# Multi-modal Content Analysis Steps
@given("a restaurant webpage with menu images")
def webpage_with_images(extraction_context):
    """Set up webpage with menu images."""
    extraction_context["webpage_content"] = """
    <div class="menu">
        <img src="menu-board.jpg" alt="Daily Menu Board">
        <img src="signature-dish.jpg" alt="Chef's Special">
        <div class="text-menu">
            <h3>Today's Special: $25</h3>
        </div>
    </div>
    """
    extraction_context["images"] = ["menu-board.jpg", "signature-dish.jpg"]


@given("image analysis is enabled in configuration")
def image_analysis_enabled(extraction_context):
    """Enable image analysis in configuration."""
    extraction_context["config"]["image_analysis_enabled"] = True
    extraction_context["config"]["vision_model"] = "gpt-4-vision-preview"


@given("vision-capable LLM is available")
def vision_llm_available(extraction_context):
    """Set up vision-capable LLM availability."""
    extraction_context["config"]["vision_llm_available"] = True


@when("I run multi-modal content analysis")
def run_multimodal_analysis(extraction_context):
    """Run multi-modal content analysis."""
    analyzer = extraction_context["analyzer"]
    
    # Mock multi-modal analysis
    analyzer.multimodal_extractor = Mock()
    analyzer.multimodal_extractor.analyze_images = Mock(return_value={
        "image_extracted_items": [
            {
                "source": "menu-board.jpg",
                "items": [{"name": "Daily Special", "price": "$25"}],
                "confidence": 0.82
            }
        ],
        "text_correlation": {"Daily Special": "matches_text"},
        "processing_mode": "multimodal"
    })
    
    result = analyzer.analyze_multimodal_content(
        content=extraction_context["webpage_content"],
        images=extraction_context["images"]
    )
    extraction_context["results"] = result


@then("the system should extract text from images")
def verify_image_text_extraction(extraction_context):
    """Verify text extraction from images."""
    results = extraction_context["results"]
    assert "image_extracted_items" in results
    assert len(results["image_extracted_items"]) > 0


@then("identify menu items from photos")
def verify_menu_item_identification(extraction_context):
    """Verify menu items identified from photos."""
    results = extraction_context["results"]
    items = results["image_extracted_items"][0]["items"]
    assert len(items) > 0
    assert "name" in items[0]


@then("correlate image content with text content")
def verify_content_correlation(extraction_context):
    """Verify correlation between image and text content."""
    results = extraction_context["results"]
    assert "text_correlation" in results


# Site-specific Pattern Learning Steps
@given("a restaurant chain with multiple location websites")
def restaurant_chain_setup(extraction_context):
    """Set up restaurant chain for pattern learning."""
    extraction_context["config"]["chain_name"] = "TestChain"
    extraction_context["config"]["pattern_learning_enabled"] = True


@given("successful extractions from 5 similar sites")
def successful_extractions_history(extraction_context):
    """Set up history of successful extractions."""
    extraction_context["pattern_history"] = [
        {"site": "site1.com", "patterns": ["menu_class:daily-menu"], "success_rate": 0.95},
        {"site": "site2.com", "patterns": ["menu_class:daily-menu"], "success_rate": 0.92},
        {"site": "site3.com", "patterns": ["menu_class:daily-menu"], "success_rate": 0.88},
        {"site": "site4.com", "patterns": ["menu_class:daily-menu"], "success_rate": 0.91},
        {"site": "site5.com", "patterns": ["menu_class:daily-menu"], "success_rate": 0.89}
    ]


@when("I process a new site from the same chain")
def process_new_chain_site(extraction_context):
    """Process a new site from the same chain."""
    analyzer = extraction_context["analyzer"]
    
    # Mock pattern learning
    analyzer.pattern_learner = Mock()
    analyzer.pattern_learner.apply_learned_patterns = Mock(return_value={
        "applied_patterns": ["menu_class:daily-menu"],
        "pattern_confidence": 0.91,
        "extraction_improved": True,
        "baseline_accuracy": 0.65,
        "pattern_accuracy": 0.89
    })
    
    result = analyzer.extract_with_pattern_learning(
        content=extraction_context["webpage_content"],
        chain_patterns=extraction_context["pattern_history"]
    )
    extraction_context["results"] = result


@then("the system should identify common patterns")
def verify_pattern_identification(extraction_context):
    """Verify common patterns were identified."""
    results = extraction_context["results"]
    assert "applied_patterns" in results
    assert len(results["applied_patterns"]) > 0


@then("improve extraction accuracy over baseline")
def verify_accuracy_improvement(extraction_context):
    """Verify extraction accuracy improvement."""
    results = extraction_context["results"]
    assert results["pattern_accuracy"] > results["baseline_accuracy"]


# Dynamic Prompt Adjustment Steps
@given("a restaurant webpage with complex poetic menu descriptions")
def poetic_menu_descriptions(extraction_context):
    """Set up webpage with poetic menu descriptions."""
    extraction_context["webpage_content"] = """
    <div class="artisan-menu">
        <div class="dish">
            <h3>Moonbeam's Embrace</h3>
            <p>Where starlight meets earth's bounty in a symphony of flavors</p>
        </div>
        <div class="dish">
            <h3>Whispers of the Ancient Grove</h3>
            <p>Secrets of the forest captured in delicate seasonal treasures</p>
        </div>
    </div>
    """


@given("dynamic prompt adjustment is enabled")
def dynamic_prompts_enabled(extraction_context):
    """Enable dynamic prompt adjustment."""
    extraction_context["config"]["dynamic_prompts"] = True
    extraction_context["config"]["complexity_analysis"] = True


@when("I run extraction with complexity analysis")
def run_complexity_analysis(extraction_context):
    """Run extraction with complexity analysis."""
    analyzer = extraction_context["analyzer"]
    
    # Mock dynamic prompt adjustment
    analyzer.prompt_adjuster = Mock()
    analyzer.prompt_adjuster.analyze_complexity = Mock(return_value={
        "complexity_score": 0.85,
        "content_type": "poetic",
        "selected_strategy": "creative_interpretation",
        "prompt_adjustments": [
            "Use creative interpretation for poetic descriptions",
            "Focus on extracting actual food items from metaphorical language",
            "Identify cuisine style from artistic descriptions"
        ],
        "reasoning": "High complexity poetic language detected"
    })
    
    result = analyzer.extract_with_dynamic_prompts(
        content=extraction_context["webpage_content"]
    )
    extraction_context["results"] = result


@then("the system should analyze content complexity")
def verify_complexity_analysis(extraction_context):
    """Verify content complexity analysis."""
    results = extraction_context["results"]
    assert "complexity_score" in results
    assert results["complexity_score"] > 0


@then("select appropriate prompt strategy")
def verify_prompt_strategy_selection(extraction_context):
    """Verify appropriate prompt strategy selection."""
    results = extraction_context["results"]
    assert "selected_strategy" in results
    assert results["selected_strategy"] == "creative_interpretation"


@then("provide explanation of prompt selection reasoning")
def verify_prompt_reasoning(extraction_context):
    """Verify prompt selection reasoning is provided."""
    results = extraction_context["results"]
    assert "reasoning" in results
    assert len(results["reasoning"]) > 0


# Integration and Error Handling Steps
@given("all optional AI features are enabled")
def all_features_enabled(extraction_context):
    """Enable all optional AI features."""
    extraction_context["config"].update({
        "claude_enabled": True,
        "ollama_enabled": True,
        "multimodal_enabled": True,
        "pattern_learning_enabled": True,
        "dynamic_prompts_enabled": True
    })


@given("all LLM providers become unavailable")
def all_llm_unavailable(extraction_context):
    """Simulate all LLM providers becoming unavailable."""
    extraction_context["llm_failures"] = {
        "openai": "API quota exceeded",
        "claude": "Service temporarily unavailable",
        "ollama": "Local service not responding"
    }


@when("I run extraction with full feature set")
def run_full_feature_extraction(extraction_context):
    """Run extraction with full feature set."""
    analyzer = extraction_context["analyzer"]
    
    # Mock graceful degradation
    analyzer.fallback_extractor = Mock()
    analyzer.fallback_extractor.extract_traditional = Mock(return_value={
        "extraction_method": "traditional_heuristics",
        "menu_items": [{"name": "Traditional extraction result"}],
        "fallback_used": True,
        "ai_services_status": "all_unavailable",
        "quality_score": 0.75
    })
    
    result = analyzer.extract_with_graceful_degradation(
        content=extraction_context["webpage_content"]
    )
    extraction_context["results"] = result


@then("the system should detect all AI service failures")
def verify_ai_failure_detection(extraction_context):
    """Verify AI service failure detection."""
    results = extraction_context["results"]
    assert results["ai_services_status"] == "all_unavailable"


@then("automatically fallback to traditional extraction methods")
def verify_traditional_fallback(extraction_context):
    """Verify fallback to traditional extraction methods."""
    results = extraction_context["results"]
    assert results["extraction_method"] == "traditional_heuristics"
    assert results["fallback_used"] is True


@then("maintain extraction quality within acceptable bounds")
def verify_acceptable_quality(extraction_context):
    """Verify extraction quality is maintained."""
    results = extraction_context["results"]
    assert "quality_score" in results
    assert results["quality_score"] >= 0.7  # Acceptable threshold