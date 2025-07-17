"""Unit tests for AI Content Analyzer module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
from typing import Dict, List, Any

from src.ai.content_analyzer import AIContentAnalyzer


class TestAIContentAnalyzer:
    """Test cases for AIContentAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create AIContentAnalyzer instance."""
        return AIContentAnalyzer()

    @pytest.fixture
    def mock_llm_extractor(self):
        """Mock LLM extractor."""
        with patch('src.ai.content_analyzer.LLMExtractor') as mock:
            yield mock

    @pytest.fixture
    def sample_menu_items(self):
        """Sample menu items for testing."""
        return [
            {
                "name": "Caesar Salad",
                "description": "Fresh romaine lettuce with house-made Caesar dressing",
                "price": 12.99
            },
            {
                "name": "Bacon Cheeseburger",
                "description": "1/2 lb beef patty with crispy bacon and melted cheddar",
                "price": 16.99
            }
        ]

    def test_analyzer_initialization(self, analyzer):
        """Test AIContentAnalyzer initialization."""
        assert analyzer is not None
        assert hasattr(analyzer, 'llm_extractor')
        assert hasattr(analyzer, 'confidence_scorer')

    def test_analyze_nutritional_context(self, analyzer, mock_llm_extractor, sample_menu_items):
        """Test nutritional context analysis."""
        # Mock the extract method on the analyzer's llm_extractor instance
        analyzer.llm_extractor.extract = Mock(return_value={
            "nutritional_context": [
                {
                    "name": "Caesar Salad",
                    "tags": ["salad", "vegetarian-option", "lighter-fare"],
                    "calorie_range": {"min": 300, "max": 500},
                    "dietary_flags": ["vegetarian", "gluten-free-available"]
                },
                {
                    "name": "Bacon Cheeseburger",
                    "tags": ["burger", "high-calorie", "meat"],
                    "calorie_range": {"min": 800, "max": 1200},
                    "dietary_flags": ["contains-gluten", "contains-dairy"]
                }
            ],
            "dietary_restrictions": {
                "vegetarian": ["Caesar Salad"],
                "gluten_free": ["Caesar Salad (without croutons)"],
                "vegan": []
            }
        })

        result = analyzer.analyze_content(
            content="<menu content>",
            menu_items=sample_menu_items,
            analysis_type="nutritional"
        )

        assert "nutritional_context" in result
        assert len(result["nutritional_context"]) == 2
        assert "dietary_restrictions" in result

    def test_analyze_menu_with_empty_items(self, analyzer):
        """Test analysis with empty menu items."""
        result = analyzer.analyze_content(
            content="<menu content>",
            menu_items=[],
            analysis_type="nutritional"
        )

        assert "nutritional_context" in result
        assert len(result["nutritional_context"]) == 0

    def test_price_analysis(self, analyzer, mock_llm_extractor):
        """Test price range analysis functionality."""
        price_data = {
            "min": 12,
            "max": 45,
            "items": [
                {"name": "Appetizer", "price": 12},
                {"name": "Steak Dinner", "price": 45}
            ]
        }

        # Mock the extract method on the analyzer's llm_extractor instance
        analyzer.llm_extractor.extract = Mock(return_value={
            "price_tier": "upscale",
            "competitive_positioning": {
                "market_position": "premium",
                "comparison": "Above average for Downtown Manhattan"
            },
            "value_proposition": "High-quality ingredients justify premium pricing",
            "portion_expectations": "Generous portions expected at this price point"
        })

        result = analyzer.analyze_prices(
            prices=price_data,
            location="Downtown Manhattan"
        )

        assert result["price_tier"] == "upscale"
        assert "competitive_positioning" in result
        assert "value_proposition" in result

    def test_price_analysis_with_invalid_location(self, analyzer):
        """Test price analysis with missing location."""
        price_data = {"min": 10, "max": 20, "items": []}
        
        result = analyzer.analyze_prices(
            prices=price_data,
            location=None
        )

        assert "price_tier" in result
        assert result["location_context"] == "Location not specified"

    def test_cuisine_classification(self, analyzer, mock_llm_extractor):
        """Test cuisine classification with cultural context."""
        analyzer.llm_extractor.extract = Mock(return_value={
            "primary_cuisine": "Fusion",
            "cuisine_influences": ["Korean", "Mexican", "Japanese"],
            "cultural_context": "Modern fusion combining Asian and Latin flavors",
            "authenticity_score": 0.7,
            "authenticity_indicators": ["fusion-style", "creative-interpretation"],
            "cuisine_tags": ["fusion", "asian-fusion", "korean-mexican", "modern-cuisine"]
        })

        result = analyzer.classify_cuisine(
            content="<restaurant description>",
            menu_items=[{"name": "Korean BBQ Tacos"}]
        )

        assert result["primary_cuisine"] == "Fusion"
        assert "Korean" in result["cuisine_influences"]
        assert result["authenticity_score"] == 0.7

    def test_handle_ambiguous_descriptions(self, analyzer, mock_llm_extractor):
        """Test handling of ambiguous menu descriptions."""
        ambiguous_items = [
            {"name": "Ocean's Bounty", "description": "Chef's daily selection"},
            {"name": "Garden's Whisper", "description": "Seasonal vegetables"}
        ]

        # Mock the extract method on the analyzer's llm_extractor instance
        analyzer.llm_extractor.extract = Mock(return_value={
            "items": [
                {
                    "name": "Ocean's Bounty",
                    "likely_category": "seafood",
                    "confidence": 0.8,
                    "alternatives": ["fish", "shellfish", "mixed seafood"]
                },
                {
                    "name": "Garden's Whisper",
                    "likely_category": "vegetarian",
                    "confidence": 0.9,
                    "alternatives": ["salad", "vegetable medley"]
                }
            ]
        })

        result = analyzer.analyze_ambiguous_items(ambiguous_items)

        assert len(result["interpreted_items"]) == 2
        assert result["interpreted_items"][0]["likely_category"] == "seafood"

    def test_dietary_accommodation_extraction(self, analyzer, mock_llm_extractor):
        """Test extraction of dietary accommodation information."""
        analyzer.llm_extractor.extract = Mock(return_value={
            "dietary_accommodations": {
                "gluten_free": {
                    "available": True,
                    "items": ["Grilled Chicken", "Salads"],
                    "notes": "GF bread available"
                },
                "vegan": {
                    "available": True,
                    "items": ["Veggie Burger", "Quinoa Bowl"],
                    "notes": "Plant-based options clearly marked"
                }
            },
            "cross_contamination_warnings": ["Shared fryer used"],
            "dietary_friendliness_score": 0.85,
            "missing_info": ["nut allergies not addressed"]
        })

        result = analyzer.extract_dietary_info(
            content="<restaurant page with dietary info>"
        )

        assert "dietary_accommodations" in result
        assert result["dietary_accommodations"]["gluten_free"]["available"]
        assert result["dietary_friendliness_score"] == 0.85

    def test_specialty_analysis(self, analyzer, mock_llm_extractor):
        """Test restaurant specialty analysis."""
        analyzer.llm_extractor.extract = Mock(return_value={
            "signature_dishes": [
                {
                    "name": "Wood-fired Pizza",
                    "rank": 1,
                    "mentions": 5,
                    "description": "Authentic Neapolitan style"
                }
            ],
            "cooking_methods": ["wood-fired", "handmade", "traditional"],
            "unique_selling_points": ["Imported Italian ingredients", "100-year-old starter"],
            "first_timer_recommendations": ["Try the Margherita pizza", "Don't miss the tiramisu"]
        })

        result = analyzer.analyze_specialties(
            content="<page mentioning wood-fired pizza multiple times>"
        )

        assert len(result["signature_dishes"]) > 0
        assert result["signature_dishes"][0]["name"] == "Wood-fired Pizza"

    def test_multilingual_content_processing(self, analyzer, mock_llm_extractor):
        """Test processing of multilingual menu content."""
        multilingual_items = [
            {"name": "Osso Buco", "description": "Braised veal shanks"},
            {"name": "Coq au Vin", "description": "Chicken braised in wine"}
        ]

        analyzer.llm_extractor.extract = Mock(return_value={
            "items_with_translation": [
                {
                    "original": "Osso Buco",
                    "language": "Italian",
                    "translation": "Bone with hole",
                    "pronunciation": "OH-so BOO-ko",
                    "cultural_significance": "Traditional Milanese dish"
                }
            ],
            "authenticity_assessment": "High - proper use of original language",
            "language_consistency": 0.9
        })

        result = analyzer.process_multilingual_content(multilingual_items)

        assert "items_with_translation" in result
        assert result["items_with_translation"][0]["original"] == "Osso Buco"

    def test_structure_unstructured_content(self, analyzer, mock_llm_extractor):
        """Test structuring of unstructured menu content."""
        unstructured_content = """
        We start with appetizers like bruschetta for $8 and calamari at $12.
        Our main courses include pasta dishes from $15-20 and steaks starting at $35.
        Don't forget dessert - tiramisu $8, gelato $6.
        """

        analyzer.llm_extractor.extract = Mock(return_value={
            "structured_menu": {
                "appetizers": [
                    {"name": "Bruschetta", "price": 8},
                    {"name": "Calamari", "price": 12}
                ],
                "main_courses": [
                    {"name": "Pasta dishes", "price_range": [15, 20]},
                    {"name": "Steaks", "starting_price": 35}
                ],
                "desserts": [
                    {"name": "Tiramisu", "price": 8},
                    {"name": "Gelato", "price": 6}
                ]
            },
            "extraction_confidence": 0.95
        })

        result = analyzer.structure_content(unstructured_content)

        assert "structured_menu" in result
        assert "appetizers" in result["structured_menu"]
        assert len(result["structured_menu"]["appetizers"]) == 2

    def test_api_error_handling(self, analyzer, mock_llm_extractor):
        """Test handling of API errors."""
        analyzer.llm_extractor.extract = Mock(side_effect=Exception("API rate limit exceeded"))

        result = analyzer.analyze_content(
            content="<content>",
            menu_items=[],
            analysis_type="nutritional"
        )

        # With empty menu_items, the analyzer returns defaults when LLM fails
        # This tests that the system handles errors gracefully
        assert "nutritional_context" in result
        assert "dietary_restrictions" in result
        assert result["nutritional_context"] == []
        assert result["dietary_restrictions"] == {}

    def test_confidence_score_integration(self, analyzer):
        """Test integration with confidence scoring system."""
        analysis_result = {
            "nutritional_context": [{"name": "Test Item"}],
            "extraction_method": "llm",
            "llm_confidence": 0.85
        }

        confidence = analyzer.calculate_integrated_confidence(
            analysis_result,
            source_reliability=0.9
        )

        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably high with good inputs

    def test_caching_mechanism(self, analyzer, mock_llm_extractor):
        """Test that caching prevents duplicate API calls."""
        content = "Test content"
        menu_items = [{"name": "Test"}]

        # Mock the extract method
        mock_extract = Mock(return_value={
            "nutritional_context": [],
            "dietary_restrictions": {}
        })
        analyzer.llm_extractor.extract = mock_extract

        # First call
        analyzer.analyze_content(content, menu_items, "nutritional")
        
        # Second call with same inputs
        analyzer.analyze_content(content, menu_items, "nutritional")

        # Should only call LLM once due to caching
        assert mock_extract.call_count == 1

    def test_batch_processing(self, analyzer, mock_llm_extractor):
        """Test batch processing of multiple pages."""
        pages = [
            {"url": "page1", "content": "content1"},
            {"url": "page2", "content": "content2"},
            {"url": "page3", "content": "content3"}
        ]

        results = analyzer.batch_analyze(pages)

        assert len(results) == 3
        assert all("url" in result for result in results)

    def test_custom_configuration(self, analyzer):
        """Test using custom configuration."""
        custom_config = {
            "extraction_prompts": {
                "nutritional": "Custom nutritional prompt"
            },
            "confidence_weights": {
                "llm": 0.9,
                "traditional": 0.1
            }
        }

        analyzer.update_configuration(custom_config)
        
        assert analyzer.config["extraction_prompts"]["nutritional"] == "Custom nutritional prompt"
        assert analyzer.config["confidence_weights"]["llm"] == 0.9

    def test_performance_monitoring(self, analyzer, mock_llm_extractor):
        """Test performance monitoring during extraction."""
        mock_llm_extractor.return_value.extract.return_value = {"test": "data"}

        result = analyzer.analyze_content(
            content="x" * 10000,  # Large content
            menu_items=[],
            analysis_type="nutritional",
            monitor_performance=True
        )

        assert "performance_metrics" in result
        assert "processing_time" in result["performance_metrics"]
        assert "memory_usage" in result["performance_metrics"]