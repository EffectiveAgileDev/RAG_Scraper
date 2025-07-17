"""Unit tests for JSON export generator AI integration."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.json_export_generator import JSONExportGenerator


class TestJSONExportAIIntegration:
    """Test AI analysis integration in JSON export generator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = JSONExportGenerator()
        self.mock_config = Mock()
        self.mock_config.include_ai_analysis = True

    def test_json_export_includes_ai_analysis(self):
        """Test that JSON export includes AI analysis data."""
        ai_data = {
            "confidence_score": 0.85,
            "provider_used": "openai",
            "nutritional_context": [
                {"item": "Burger", "calories": 650}
            ]
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            address="123 Main St",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        assert "ai_analysis" in result
        assert result["ai_analysis"]["confidence_score"] == 0.85
        assert result["ai_analysis"]["provider_used"] == "openai"
        assert len(result["ai_analysis"]["nutritional_context"]) == 1

    def test_json_export_without_ai_analysis(self):
        """Test that JSON export works without AI analysis."""
        restaurant = RestaurantData(
            name="Test Restaurant",
            address="123 Main St"
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        assert "ai_analysis" not in result
        assert result["name"] == "Test Restaurant"
        assert result["address"] == "123 Main St"

    def test_json_export_with_empty_ai_analysis(self):
        """Test that JSON export handles empty AI analysis."""
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis={}
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        assert "ai_analysis" in result
        assert result["ai_analysis"] == {}

    def test_json_export_with_ai_nutritional_analysis(self):
        """Test JSON export with AI nutritional analysis."""
        ai_data = {
            "confidence_score": 0.9,
            "provider_used": "openai",
            "nutritional_context": [
                {
                    "item": "Caesar Salad",
                    "calories": 470,
                    "dietary_tags": ["vegetarian", "gluten-free option"],
                    "allergens": ["dairy", "eggs"]
                },
                {
                    "item": "Grilled Chicken",
                    "calories": 350,
                    "dietary_tags": ["high-protein", "keto-friendly"],
                    "allergens": []
                }
            ]
        }
        
        restaurant = RestaurantData(
            name="Health Bistro",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        assert result["ai_analysis"]["nutritional_context"][0]["item"] == "Caesar Salad"
        assert result["ai_analysis"]["nutritional_context"][0]["calories"] == 470
        assert "vegetarian" in result["ai_analysis"]["nutritional_context"][0]["dietary_tags"]
        assert "dairy" in result["ai_analysis"]["nutritional_context"][0]["allergens"]

    def test_json_export_with_ai_price_analysis(self):
        """Test JSON export with AI price analysis."""
        ai_data = {
            "confidence_score": 0.8,
            "provider_used": "openai",
            "price_analysis": {
                "price_range": "$15-25",
                "competitive_positioning": "mid-range",
                "value_assessment": "good value for quality",
                "price_trends": {
                    "appetizers": "$8-12",
                    "mains": "$18-28",
                    "desserts": "$6-9"
                }
            }
        }
        
        restaurant = RestaurantData(
            name="Bistro Example",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        price_analysis = result["ai_analysis"]["price_analysis"]
        assert price_analysis["price_range"] == "$15-25"
        assert price_analysis["competitive_positioning"] == "mid-range"
        assert price_analysis["value_assessment"] == "good value for quality"
        assert price_analysis["price_trends"]["mains"] == "$18-28"

    def test_json_export_with_ai_cuisine_classification(self):
        """Test JSON export with AI cuisine classification."""
        ai_data = {
            "confidence_score": 0.92,
            "provider_used": "openai",
            "cuisine_classification": {
                "primary_cuisine": "Italian",
                "secondary_cuisines": ["Mediterranean", "American"],
                "authenticity_score": 0.85,
                "fusion_elements": ["truffle oil", "modern presentation"],
                "regional_specialties": ["Northern Italian", "Tuscan"]
            }
        }
        
        restaurant = RestaurantData(
            name="Authentic Italian",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        cuisine_class = result["ai_analysis"]["cuisine_classification"]
        assert cuisine_class["primary_cuisine"] == "Italian"
        assert "Mediterranean" in cuisine_class["secondary_cuisines"]
        assert cuisine_class["authenticity_score"] == 0.85
        assert "truffle oil" in cuisine_class["fusion_elements"]
        assert "Northern Italian" in cuisine_class["regional_specialties"]

    def test_json_export_with_ai_dietary_accommodations(self):
        """Test JSON export with AI dietary accommodations."""
        ai_data = {
            "confidence_score": 0.88,
            "provider_used": "openai",
            "dietary_accommodations": {
                "allergens": ["nuts", "dairy", "gluten"],
                "dietary_restrictions": ["vegetarian", "vegan", "gluten-free", "keto"],
                "accommodation_quality": "excellent",
                "special_menu_available": True,
                "staff_knowledge": "well-trained"
            }
        }
        
        restaurant = RestaurantData(
            name="Inclusive Eatery",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        dietary = result["ai_analysis"]["dietary_accommodations"]
        assert "nuts" in dietary["allergens"]
        assert "vegan" in dietary["dietary_restrictions"]
        assert dietary["accommodation_quality"] == "excellent"
        assert dietary["special_menu_available"] is True
        assert dietary["staff_knowledge"] == "well-trained"

    def test_json_export_with_ai_confidence_and_threshold(self):
        """Test JSON export with AI confidence and threshold information."""
        ai_data = {
            "confidence_score": 0.65,
            "confidence_threshold": 0.7,
            "meets_threshold": False,
            "provider_used": "openai",
            "analysis_timestamp": "2025-01-15T10:30:00Z"
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        ai_analysis = result["ai_analysis"]
        assert ai_analysis["confidence_score"] == 0.65
        assert ai_analysis["confidence_threshold"] == 0.7
        assert ai_analysis["meets_threshold"] is False
        assert ai_analysis["analysis_timestamp"] == "2025-01-15T10:30:00Z"

    def test_json_export_with_ai_error_handling(self):
        """Test JSON export with AI analysis error information."""
        ai_data = {
            "confidence_score": 0.0,
            "provider_used": "openai",
            "error": "API key invalid",
            "fallback_used": True,
            "error_details": {
                "error_type": "authentication",
                "timestamp": "2025-01-15T10:30:00Z",
                "retry_possible": True
            }
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        ai_analysis = result["ai_analysis"]
        assert ai_analysis["error"] == "API key invalid"
        assert ai_analysis["fallback_used"] is True
        assert ai_analysis["error_details"]["error_type"] == "authentication"
        assert ai_analysis["error_details"]["retry_possible"] is True

    def test_json_export_with_multimodal_ai_analysis(self):
        """Test JSON export with multimodal AI analysis."""
        ai_data = {
            "confidence_score": 0.82,
            "provider_used": "openai",
            "multimodal_analysis": {
                "images_processed": 5,
                "visual_menu_items": ["Pasta Carbonara", "Margherita Pizza"],
                "ambiance_description": "Modern Italian with warm lighting",
                "visual_confidence": 0.78
            }
        }
        
        restaurant = RestaurantData(
            name="Visual Test Restaurant",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        multimodal = result["ai_analysis"]["multimodal_analysis"]
        assert multimodal["images_processed"] == 5
        assert "Pasta Carbonara" in multimodal["visual_menu_items"]
        assert "Modern Italian" in multimodal["ambiance_description"]
        assert multimodal["visual_confidence"] == 0.78

    def test_json_export_with_pattern_learning_ai_analysis(self):
        """Test JSON export with pattern learning AI analysis."""
        ai_data = {
            "confidence_score": 0.91,
            "provider_used": "openai",
            "pattern_learning": {
                "site_patterns_identified": ["menu-item-class", "price-span"],
                "extraction_confidence": 0.89,
                "patterns_learned": True,
                "site_type": "restaurant_chain",
                "extraction_strategy": "structured_data_preferred"
            }
        }
        
        restaurant = RestaurantData(
            name="Pattern Test Restaurant",
            ai_analysis=ai_data
        )
        
        result = self.generator._convert_single_restaurant_to_dict(restaurant)
        
        pattern_learning = result["ai_analysis"]["pattern_learning"]
        assert pattern_learning["patterns_learned"] is True
        assert "menu-item-class" in pattern_learning["site_patterns_identified"]
        assert pattern_learning["extraction_confidence"] == 0.89
        assert pattern_learning["site_type"] == "restaurant_chain"

    def test_json_export_batch_with_mixed_ai_analysis(self):
        """Test JSON export with batch of restaurants with mixed AI analysis."""
        restaurant1 = RestaurantData(
            name="AI Restaurant",
            ai_analysis={"confidence_score": 0.9, "provider_used": "openai"}
        )
        
        restaurant2 = RestaurantData(
            name="Traditional Restaurant"
        )
        
        restaurant3 = RestaurantData(
            name="Error Restaurant",
            ai_analysis={"error": "API timeout", "fallback_used": True}
        )
        
        restaurants = [restaurant1, restaurant2, restaurant3]
        
        # Test batch conversion
        results = []
        for restaurant in restaurants:
            results.append(self.generator._convert_single_restaurant_to_dict(restaurant))
        
        # Check first restaurant has AI analysis
        assert "ai_analysis" in results[0]
        assert results[0]["ai_analysis"]["confidence_score"] == 0.9
        
        # Check second restaurant has no AI analysis
        assert "ai_analysis" not in results[1]
        
        # Check third restaurant has error AI analysis
        assert "ai_analysis" in results[2]
        assert results[2]["ai_analysis"]["error"] == "API timeout"
        assert results[2]["ai_analysis"]["fallback_used"] is True