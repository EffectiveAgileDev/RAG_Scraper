"""Unit tests for AI optional advanced features."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, List, Any


class TestClaudeExtractor:
    """Test Claude AI extractor."""

    @pytest.fixture
    def claude_extractor(self):
        """Create Claude extractor instance."""
        from src.ai.claude_extractor import ClaudeExtractor
        return ClaudeExtractor(api_key="test-key")

    def test_claude_extractor_initialization(self, claude_extractor):
        """Test Claude extractor initialization."""
        assert claude_extractor.api_key == "test-key"
        assert claude_extractor.default_model == "claude-3-opus-20240229"

    @patch('src.ai.claude_extractor.requests.post')
    def test_claude_extraction_success(self, mock_post, claude_extractor):
        """Test successful Claude extraction."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": '{"menu_items": [{"name": "Test Item"}]}'}],
            "usage": {"input_tokens": 100, "output_tokens": 50}
        }
        mock_post.return_value = mock_response

        result = claude_extractor.extract("test content", "Restaurant")

        assert "menu_items" in result
        assert result["provider"] == "claude"
        assert "usage" in result

    def test_claude_api_key_required(self):
        """Test that Claude extraction requires API key."""
        from src.ai.claude_extractor import ClaudeExtractor
        extractor = ClaudeExtractor()
        
        with pytest.raises(ValueError, match="Claude API key not configured"):
            extractor.extract("content", "Restaurant")


class TestOllamaExtractor:
    """Test Ollama local LLM extractor."""

    @pytest.fixture
    def ollama_extractor(self):
        """Create Ollama extractor instance."""
        from src.ai.ollama_extractor import OllamaExtractor
        return OllamaExtractor()

    def test_ollama_extractor_initialization(self, ollama_extractor):
        """Test Ollama extractor initialization."""
        assert ollama_extractor.endpoint == "http://localhost:11434"
        assert ollama_extractor.default_model == "llama2"

    @patch('src.ai.ollama_extractor.requests.get')
    @patch('src.ai.ollama_extractor.requests.post')
    def test_ollama_extraction_success(self, mock_post, mock_get, ollama_extractor):
        """Test successful Ollama extraction."""
        # Mock status check
        mock_get.return_value.status_code = 200
        
        # Mock extraction response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Restaurant: Test Place\nMenu: Pizza $15, Burger $12",
            "model": "llama2",
            "done": True,
            "total_duration": 1000000
        }
        mock_post.return_value = mock_response

        result = ollama_extractor.extract("test content")

        assert result["provider"] == "ollama"
        assert result["local_processing"] is True
        assert "menu_items" in result
        assert len(result["menu_items"]) >= 0

    @patch('src.ai.ollama_extractor.requests.get')
    def test_ollama_service_unavailable(self, mock_get, ollama_extractor):
        """Test Ollama service unavailable."""
        mock_get.side_effect = Exception("Connection refused")

        with pytest.raises(Exception, match="Ollama service not available"):
            ollama_extractor.extract("content")


class TestMultiModalExtractor:
    """Test multi-modal content extractor."""

    @pytest.fixture
    def multimodal_extractor(self):
        """Create multi-modal extractor instance."""
        from src.ai.multimodal_extractor import MultiModalExtractor
        return MultiModalExtractor()

    def test_multimodal_extractor_initialization(self, multimodal_extractor):
        """Test multi-modal extractor initialization."""
        assert multimodal_extractor.vision_model == "gpt-4-vision-preview"

    def test_image_analysis(self, multimodal_extractor):
        """Test image analysis functionality."""
        content = "<div>Restaurant content</div>"
        images = ["menu-board.jpg", "logo.jpg"]

        result = multimodal_extractor.analyze_images(content, images)

        assert "image_extracted_items" in result
        assert "text_correlation" in result
        assert "multimodal_confidence" in result
        assert len(result["image_extracted_items"]) <= len(images)

    def test_menu_image_recognition(self, multimodal_extractor):
        """Test menu image recognition."""
        result = multimodal_extractor._analyze_single_image("menu-board.jpg")

        assert result["image_type"] == "menu"
        assert "items" in result
        assert result["text_detected"] is True

    def test_logo_image_recognition(self, multimodal_extractor):
        """Test logo image recognition."""
        result = multimodal_extractor._analyze_single_image("restaurant-logo.jpg")

        assert result["image_type"] == "branding"
        assert "brand_elements" in result


class TestPatternLearner:
    """Test pattern learning system."""

    @pytest.fixture
    def pattern_learner(self):
        """Create pattern learner instance."""
        from src.ai.pattern_learner import PatternLearner
        return PatternLearner()

    def test_pattern_learner_initialization(self, pattern_learner):
        """Test pattern learner initialization."""
        assert pattern_learner.success_threshold == 0.8
        assert pattern_learner.learning_enabled is True

    def test_apply_learned_patterns(self, pattern_learner):
        """Test applying learned patterns."""
        content = '<div class="daily-menu"><h3>Special</h3><p>$25</p></div>'
        historical_patterns = [
            {"patterns": ["menu_class:daily-menu"], "success_rate": 0.95}
        ]

        result = pattern_learner.apply_learned_patterns(content, historical_patterns)

        assert "applied_patterns" in result
        assert "pattern_confidence" in result
        assert "extraction_improved" in result
        assert len(result["applied_patterns"]) > 0

    def test_pattern_matching(self, pattern_learner):
        """Test pattern matching logic."""
        content = '<div class="menu-items">Content</div>'
        pattern = "menu_class:menu-items"

        matches = pattern_learner._pattern_matches_content(pattern, content)
        assert matches is True

    def test_baseline_extraction(self, pattern_learner):
        """Test baseline extraction without patterns."""
        content = '<div class="menu">Item 1 $10</div>'

        result = pattern_learner._baseline_extraction(content)

        assert result["method"] == "baseline_heuristics"
        assert "data" in result
        assert "accuracy" in result

    def test_learning_from_feedback(self, pattern_learner):
        """Test learning from user feedback."""
        content = "test content"
        extracted_data = {"items": ["item1"]}
        corrections = {"missed_items": ["item2"]}

        # Should not raise exception
        pattern_learner.learn_from_feedback(content, extracted_data, corrections)
        
        # Check that learning data was stored
        assert len(pattern_learner.pattern_database) > 0


class TestDynamicPromptAdjuster:
    """Test dynamic prompt adjustment system."""

    @pytest.fixture
    def prompt_adjuster(self):
        """Create dynamic prompt adjuster instance."""
        from src.ai.dynamic_prompt_adjuster import DynamicPromptAdjuster
        return DynamicPromptAdjuster()

    def test_prompt_adjuster_initialization(self, prompt_adjuster):
        """Test prompt adjuster initialization."""
        assert "simple" in prompt_adjuster.complexity_thresholds
        assert "creative_interpretation" in prompt_adjuster.prompt_strategies

    def test_complexity_analysis_simple(self, prompt_adjuster):
        """Test complexity analysis for simple content."""
        simple_content = "<h1>Menu</h1><p>Pizza $10</p>"

        result = prompt_adjuster.analyze_complexity(simple_content)

        assert "complexity_score" in result
        assert "content_type" in result
        assert "recommended_strategy" in result
        assert result["complexity_score"] < 0.7

    def test_complexity_analysis_artistic(self, prompt_adjuster):
        """Test complexity analysis for artistic content."""
        artistic_content = """
        <div>Ocean's symphony dances with moonbeam treasures,
        where gentle whispers of the grove embrace starlight harmony</div>
        """

        result = prompt_adjuster.analyze_complexity(artistic_content)

        assert result["content_type"] == "poetic"
        assert result["recommended_strategy"] == "creative_interpretation"
        assert "artistic_language" in result["complexity_factors"]

    def test_language_complexity_calculation(self, prompt_adjuster):
        """Test language complexity calculation."""
        complex_content = """
        Extraordinary gastronomical establishments frequently demonstrate
        sophisticated culinary methodologies incorporating internationally
        recognized ingredients and traditional preparation techniques.
        """

        complexity = prompt_adjuster._analyze_language_complexity(complex_content)
        assert 0 <= complexity <= 1
        assert complexity > 0.3  # Should be moderately complex

    def test_artistic_language_detection(self, prompt_adjuster):
        """Test artistic language detection."""
        artistic_text = "Symphony of flavors dancing with moonbeam treasures"
        
        artistic_score = prompt_adjuster._detect_artistic_language(artistic_text)
        assert artistic_score > 0

    def test_prompt_optimization_history(self, prompt_adjuster):
        """Test prompt optimization from history."""
        history = [
            {"strategy": "creative_interpretation", "success_rate": 0.9},
            {"strategy": "standard", "success_rate": 0.6},
            {"strategy": "creative_interpretation", "success_rate": 0.85}
        ]

        result = prompt_adjuster.optimize_prompts_from_history(history)

        assert result["recommended_strategy"] == "creative_interpretation"
        assert result["success_count"] == 2


class TestTraditionalFallbackExtractor:
    """Test traditional fallback extractor."""

    @pytest.fixture
    def fallback_extractor(self):
        """Create traditional fallback extractor instance."""
        from src.ai.traditional_fallback_extractor import TraditionalFallbackExtractor
        return TraditionalFallbackExtractor()

    def test_fallback_extractor_initialization(self, fallback_extractor):
        """Test fallback extractor initialization."""
        assert "menu_items" in fallback_extractor.heuristic_patterns
        assert "prices" in fallback_extractor.heuristic_patterns

    def test_traditional_extraction(self, fallback_extractor):
        """Test traditional extraction methods."""
        content = """
        <title>Test Restaurant</title>
        <div class="menu-item">
            <h3>Pizza Special</h3>
            <p>Delicious pizza with fresh ingredients - $15.99</p>
        </div>
        <div class="item">
            <h3>Burger Combo</h3>
            <p>Beef burger with fries - $12.50</p>
        </div>
        """

        result = fallback_extractor.extract_traditional(content)

        assert result["extraction_method"] == "traditional_heuristics"
        assert "menu_items" in result
        assert "restaurant_info" in result
        assert "quality_score" in result
        assert result["quality_score"] >= 0.3

    def test_jsonld_extraction(self, fallback_extractor):
        """Test JSON-LD structured data extraction."""
        content = '''
        <script type="application/ld+json">
        {
            "@type": "Restaurant",
            "hasMenu": {
                "hasMenuSection": {
                    "hasMenuItem": [
                        {
                            "@type": "MenuItem",
                            "name": "Caesar Salad",
                            "description": "Fresh romaine lettuce",
                            "offers": {"price": "12.99"}
                        }
                    ]
                }
            }
        }
        </script>
        '''

        items = fallback_extractor._extract_jsonld_menu_items(content)

        assert len(items) > 0
        assert items[0]["name"] == "Caesar Salad"
        assert items[0]["source"] == "jsonld_extraction"

    def test_menu_item_parsing(self, fallback_extractor):
        """Test menu item parsing from HTML."""
        html_text = "<h3>Grilled Salmon</h3><p>Fresh Atlantic salmon - $24.99</p>"

        item = fallback_extractor._parse_menu_item_text(html_text)

        assert item is not None
        assert "Grilled Salmon" in item["name"]
        assert item["price"] == "$24.99"

    def test_restaurant_info_extraction(self, fallback_extractor):
        """Test restaurant information extraction."""
        content = """
        <title>Mario's Italian Restaurant</title>
        <div>Call us at (555) 123-4567</div>
        <div>123 Main Street, New York</div>
        """

        info = fallback_extractor._extract_restaurant_info(content)

        assert "name" in info
        assert "phone" in info
        assert "address" in info

    def test_minimal_fallback(self, fallback_extractor):
        """Test minimal fallback when extraction fails."""
        result = fallback_extractor._minimal_extraction_result()

        assert result["extraction_method"] == "minimal_fallback"
        assert result["quality_score"] == 0.3
        assert "error" in result


class TestAIContentAnalyzerIntegration:
    """Test AI Content Analyzer integration with optional features."""

    @pytest.fixture
    def analyzer(self):
        """Create AI content analyzer instance."""
        from src.ai.content_analyzer import AIContentAnalyzer
        return AIContentAnalyzer()

    def test_analyzer_optional_features_config(self, analyzer):
        """Test that analyzer has optional features configuration."""
        assert "providers" in analyzer.config
        assert "claude" in analyzer.config["providers"]
        assert "ollama" in analyzer.config["providers"]
        assert "multimodal_enabled" in analyzer.config

    def test_claude_extraction_method(self, analyzer):
        """Test Claude extraction method exists."""
        assert hasattr(analyzer, 'extract_with_claude')
        
        # Mock the claude extractor
        analyzer.claude_extractor = Mock()
        analyzer.claude_extractor.extract = Mock(return_value={
            "menu_items": [{"name": "Test Item"}],
            "provider": "claude"
        })

        result = analyzer.extract_with_claude("test content")
        assert result["provider_used"] == "claude"

    def test_ollama_extraction_method(self, analyzer):
        """Test Ollama extraction method exists."""
        assert hasattr(analyzer, 'extract_with_ollama')
        
        # Mock the ollama extractor
        analyzer.ollama_extractor = Mock()
        analyzer.ollama_extractor.extract = Mock(return_value={
            "menu_items": [{"name": "Local Item"}],
            "provider": "ollama"
        })

        result = analyzer.extract_with_ollama("test content")
        assert result["provider_used"] == "ollama"
        assert result["external_calls"] == 0

    def test_multimodal_analysis_method(self, analyzer):
        """Test multi-modal analysis method exists."""
        assert hasattr(analyzer, 'analyze_multimodal_content')
        
        # Mock the multimodal extractor
        analyzer.multimodal_extractor = Mock()
        analyzer.multimodal_extractor.analyze_images = Mock(return_value={
            "image_extracted_items": [{"source": "test.jpg"}]
        })

        result = analyzer.analyze_multimodal_content("content", ["test.jpg"])
        assert result["processing_mode"] == "multimodal"

    def test_pattern_learning_method(self, analyzer):
        """Test pattern learning method exists."""
        assert hasattr(analyzer, 'extract_with_pattern_learning')
        
        # Mock the pattern learner
        analyzer.pattern_learner = Mock()
        analyzer.pattern_learner.apply_learned_patterns = Mock(return_value={
            "applied_patterns": ["test_pattern"]
        })

        result = analyzer.extract_with_pattern_learning("content", [])
        assert "applied_patterns" in result

    def test_dynamic_prompts_method(self, analyzer):
        """Test dynamic prompts method exists."""
        assert hasattr(analyzer, 'extract_with_dynamic_prompts')
        
        # Mock the prompt adjuster
        analyzer.prompt_adjuster = Mock()
        analyzer.prompt_adjuster.analyze_complexity = Mock(return_value={
            "complexity_score": 0.8,
            "content_type": "poetic"
        })

        result = analyzer.extract_with_dynamic_prompts("content")
        assert result["selected_strategy"] == "creative_interpretation"

    def test_graceful_degradation_method(self, analyzer):
        """Test graceful degradation method exists."""
        assert hasattr(analyzer, 'extract_with_graceful_degradation')
        
        # Mock the fallback extractor
        analyzer.fallback_extractor = Mock()
        analyzer.fallback_extractor.extract_traditional = Mock(return_value={
            "extraction_method": "traditional_heuristics",
            "quality_score": 0.75
        })

        result = analyzer.extract_with_graceful_degradation("content")
        assert result["ai_services_status"] == "all_unavailable"
        assert result["fallback_used"] is True