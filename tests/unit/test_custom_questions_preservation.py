"""Unit tests for custom questions preservation in AI analysis pipeline."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.ai.content_analyzer import AIContentAnalyzer


class TestCustomQuestionsPreservation:
    """Test that custom questions are preserved throughout AI processing."""
    
    def test_custom_questions_preserved_in_direct_openai_response(self):
        """Test custom questions are preserved when OpenAI returns direct response."""
        # Arrange
        analyzer = AIContentAnalyzer(api_key="test-key")
        
        llm_result = {
            "menu_enhancements": [
                {"item_name": "Burger", "enhanced_description": "Juicy beef burger"}
            ],
            "restaurant_characteristics": {
                "ambiance": "Casual dining"
            },
            "customer_amenities": {
                "parking": "Street parking available"
            },
            "custom_questions": [
                {"question": "Do you have baby highchairs?", "answer": "Yes, we have 5 highchairs"},
                {"question": "Do you serve brunch on weekends?", "answer": "Yes, 10am-2pm"}
            ]
        }
        
        menu_items = [{"name": "Burger", "price": "$15"}]
        
        # Act
        result = analyzer._process_nutritional_result(llm_result, menu_items)
        
        # Assert
        assert "custom_questions" in result
        assert len(result["custom_questions"]) == 2
        assert result["custom_questions"][0]["question"] == "Do you have baby highchairs?"
        assert result["custom_questions"][0]["answer"] == "Yes, we have 5 highchairs"
    
    def test_custom_questions_preserved_in_extraction_format(self):
        """Test custom questions preserved when response is in extraction format."""
        # Arrange
        analyzer = AIContentAnalyzer(api_key="test-key")
        
        inner_content = {
            "menu_enhancements": [{"item_name": "Pizza", "enhanced_description": "Wood-fired pizza"}],
            "restaurant_characteristics": {"ambiance": "Italian bistro"},
            "customer_amenities": {"parking": "Valet parking"},
            "custom_questions": [
                {"question": "Do you serve custom made cocktails?", "answer": "Yes, full bar"}
            ]
        }
        
        llm_result = {
            "extractions": [
                {
                    "category": "AI Analysis",
                    "confidence": 0.9,
                    "extracted_data": inner_content
                }
            ]
        }
        
        menu_items = [{"name": "Pizza", "price": "$18"}]
        
        # Act
        result = analyzer._process_nutritional_result(llm_result, menu_items)
        
        # Assert
        assert "custom_questions" in result
        assert len(result["custom_questions"]) == 1
        assert result["custom_questions"][0]["question"] == "Do you serve custom made cocktails?"
    
    def test_custom_questions_preserved_in_json_string_analysis(self):
        """Test custom questions preserved when response contains JSON string."""
        # Arrange
        analyzer = AIContentAnalyzer(api_key="test-key")
        
        json_content = {
            "menu_enhancements": [],
            "restaurant_characteristics": {"ambiance": "Cozy"},
            "customer_amenities": {"parking": "Free lot"},
            "custom_questions": [
                {"question": "Do you have baby highchairs?", "answer": "No"}
            ]
        }
        
        llm_result = {
            "extractions": [
                {
                    "category": "AI Analysis",
                    "extracted_data": {
                        "analysis": f"```json\n{json.dumps(json_content)}\n```"
                    }
                }
            ]
        }
        
        menu_items = []
        
        # Act
        result = analyzer._process_nutritional_result(llm_result, menu_items)
        
        # Assert
        assert "custom_questions" in result
        assert result["custom_questions"][0]["answer"] == "No"
    
    def test_custom_questions_lost_in_fallback_without_preservation(self):
        """Test that custom questions are lost in fallback if not in content dict."""
        # Arrange
        analyzer = AIContentAnalyzer(api_key="test-key")
        
        # Malformed response that will trigger fallback
        llm_result = {
            "extractions": [
                {
                    "category": "AI Analysis",
                    "extracted_data": {
                        "analysis": "Some non-JSON text response"
                        # Note: no custom_questions in the content dict
                    }
                }
            ]
        }
        
        menu_items = []
        
        # Act
        result = analyzer._process_nutritional_result(llm_result, menu_items)
        
        # Assert - This should FAIL with current implementation
        assert "custom_questions" not in result  # Custom questions are lost!
    
    def test_custom_questions_preserved_in_error_fallback(self):
        """Test custom questions preserved when exception occurs."""
        # Arrange
        analyzer = AIContentAnalyzer(api_key="test-key")
        
        # This will cause an exception during processing
        llm_result = {
            "custom_questions": [
                {"question": "Test question", "answer": "Test answer"}
            ],
            "extractions": "invalid_format"  # This will cause TypeError
        }
        
        menu_items = []
        
        # Act
        result = analyzer._process_nutritional_result(llm_result, menu_items)
        
        # Assert
        assert "custom_questions" in result
        assert len(result["custom_questions"]) == 1
        assert result["custom_questions"][0]["question"] == "Test question"
    
    def test_missing_api_key_preserves_custom_questions(self):
        """Test that missing API key preserves custom questions with fallback answers."""
        # Arrange - Create analyzer with NO API key (this is the real issue)
        analyzer = AIContentAnalyzer(api_key=None)
        analyzer._current_ai_config = {
            'model': 'gpt-4o-mini',
            'custom_questions': [
                "Do you have baby highchairs?",
                "Do you serve brunch on weekends?"
            ]
        }
        
        # Act - This will cause the real "No OpenAI API key available" error
        result = analyzer._analyze_nutritional_content(
            content="Restaurant content",
            menu_items=[{"name": "Burger", "price": "$15"}],
            custom_questions=["Do you have baby highchairs?", "Do you serve brunch on weekends?"],
            ai_config={'model': 'gpt-4o-mini'}
        )
        
        # Assert - Custom questions should be preserved with fallback answers
        assert "custom_questions" in result
        assert len(result["custom_questions"]) == 2
        assert result["custom_questions"][0]["question"] == "Do you have baby highchairs?"
        assert result["custom_questions"][0]["answer"] == "No information found"
        assert result["custom_questions"][1]["question"] == "Do you serve brunch on weekends?"
        assert result["custom_questions"][1]["answer"] == "No information found"
        assert "menu_enhancements" in result
        assert result["menu_enhancements"][0]["enhanced_description"] == "Burger"  # Fallback structure
    
    def test_multi_url_custom_questions_success_case(self):
        """Test the complete flow for multi-URL custom questions when OpenAI succeeds."""
        # Arrange
        analyzer = AIContentAnalyzer(api_key="test-key")
        analyzer._current_ai_config = {
            'model': 'gpt-4o-mini',
            'custom_questions': [
                "Do you have baby highchairs?",
                "Do you serve brunch on weekends?"
            ]
        }
        
        # Mock the direct OpenAI call to succeed
        mock_openai_response = {
            "menu_enhancements": [],
            "restaurant_characteristics": {},
            "customer_amenities": {},
            "custom_questions": [
                {"question": "Do you have baby highchairs?", "answer": "Yes"},
                {"question": "Do you serve brunch on weekends?", "answer": "No"}
            ]
        }
        
        with patch.object(analyzer, '_call_openai_direct', return_value=mock_openai_response):
            # Act
            result = analyzer._analyze_nutritional_content(
                content="Restaurant content",
                menu_items=[{"name": "Pizza", "price": "$18"}],
                custom_questions=["Do you have baby highchairs?", "Do you serve brunch on weekends?"],
                ai_config={'model': 'gpt-4o-mini'}
            )
            
            # Assert
            assert "custom_questions" in result
            assert len(result["custom_questions"]) == 2
            assert result["custom_questions"][0]["answer"] == "Yes"
            assert result["custom_questions"][1]["answer"] == "No"