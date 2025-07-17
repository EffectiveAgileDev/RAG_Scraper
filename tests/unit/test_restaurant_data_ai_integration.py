"""Unit tests for RestaurantData AI analysis integration."""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import Dict, Any, Optional

# We need to import the actual RestaurantData class
from src.scraper.multi_strategy_scraper import RestaurantData


class TestRestaurantDataAIIntegration:
    """Test AI analysis integration in RestaurantData model."""

    def test_restaurant_data_has_ai_analysis_field(self):
        """Test that RestaurantData has an ai_analysis field."""
        restaurant = RestaurantData(
            name="Test Restaurant",
            address="123 Main St",
            ai_analysis={"confidence_score": 0.8}
        )
        
        assert hasattr(restaurant, 'ai_analysis')
        assert restaurant.ai_analysis is not None
        assert restaurant.ai_analysis["confidence_score"] == 0.8

    def test_restaurant_data_ai_analysis_defaults_to_none(self):
        """Test that ai_analysis field defaults to None."""
        restaurant = RestaurantData(name="Test Restaurant")
        
        assert restaurant.ai_analysis is None

    def test_restaurant_data_ai_analysis_can_be_set(self):
        """Test that ai_analysis field can be set with complex data."""
        ai_data = {
            "confidence_score": 0.85,
            "provider_used": "openai",
            "nutritional_context": [
                {"item": "Burger", "calories": 650, "dietary_tags": ["gluten-free option"]}
            ],
            "price_analysis": {
                "price_range": "$15-25",
                "competitive_positioning": "mid-range"
            },
            "cuisine_classification": {
                "primary_cuisine": "American",
                "authenticity_score": 0.9
            },
            "dietary_accommodations": {
                "allergens": ["nuts", "dairy"],
                "dietary_restrictions": ["vegetarian", "gluten-free"]
            }
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis=ai_data
        )
        
        assert restaurant.ai_analysis["confidence_score"] == 0.85
        assert restaurant.ai_analysis["provider_used"] == "openai"
        assert len(restaurant.ai_analysis["nutritional_context"]) == 1
        assert restaurant.ai_analysis["price_analysis"]["price_range"] == "$15-25"
        assert restaurant.ai_analysis["cuisine_classification"]["primary_cuisine"] == "American"
        assert "vegetarian" in restaurant.ai_analysis["dietary_accommodations"]["dietary_restrictions"]

    def test_restaurant_data_ai_analysis_with_error_handling(self):
        """Test that AI analysis can include error information."""
        ai_data = {
            "confidence_score": 0.0,
            "provider_used": "openai",
            "error": "API key invalid",
            "fallback_used": True
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis=ai_data
        )
        
        assert restaurant.ai_analysis["error"] == "API key invalid"
        assert restaurant.ai_analysis["fallback_used"] is True
        assert restaurant.ai_analysis["confidence_score"] == 0.0

    def test_restaurant_data_ai_analysis_with_threshold_information(self):
        """Test that AI analysis includes threshold information."""
        ai_data = {
            "confidence_score": 0.65,
            "confidence_threshold": 0.7,
            "meets_threshold": False,
            "provider_used": "openai"
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis=ai_data
        )
        
        assert restaurant.ai_analysis["confidence_score"] == 0.65
        assert restaurant.ai_analysis["confidence_threshold"] == 0.7
        assert restaurant.ai_analysis["meets_threshold"] is False

    def test_restaurant_data_preserves_existing_fields(self):
        """Test that adding AI analysis doesn't affect existing fields."""
        restaurant = RestaurantData(
            name="Test Restaurant",
            address="123 Main St",
            phone="555-1234",
            cuisine="Italian",
            price_range="$20-30",
            ai_analysis={"confidence_score": 0.9}
        )
        
        # Traditional fields should be preserved
        assert restaurant.name == "Test Restaurant"
        assert restaurant.address == "123 Main St"
        assert restaurant.phone == "555-1234"
        assert restaurant.cuisine == "Italian"
        assert restaurant.price_range == "$20-30"
        
        # AI analysis should be present
        assert restaurant.ai_analysis["confidence_score"] == 0.9

    def test_restaurant_data_ai_analysis_serialization(self):
        """Test that AI analysis data can be serialized."""
        ai_data = {
            "confidence_score": 0.8,
            "provider_used": "openai",
            "nutritional_context": [
                {"item": "Salad", "calories": 350}
            ]
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis=ai_data
        )
        
        # Test that the data can be accessed and is properly structured
        assert isinstance(restaurant.ai_analysis, dict)
        assert isinstance(restaurant.ai_analysis["nutritional_context"], list)
        assert isinstance(restaurant.ai_analysis["nutritional_context"][0], dict)

    def test_restaurant_data_ai_analysis_with_multimodal_data(self):
        """Test AI analysis with multimodal analysis results."""
        ai_data = {
            "confidence_score": 0.75,
            "provider_used": "openai",
            "multimodal_analysis": {
                "images_processed": 3,
                "visual_menu_items": ["Pizza Margherita", "Pasta Carbonara"],
                "ambiance_description": "Cozy Italian restaurant with warm lighting"
            }
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant",
            ai_analysis=ai_data
        )
        
        assert restaurant.ai_analysis["multimodal_analysis"]["images_processed"] == 3
        assert "Pizza Margherita" in restaurant.ai_analysis["multimodal_analysis"]["visual_menu_items"]
        assert "Cozy Italian" in restaurant.ai_analysis["multimodal_analysis"]["ambiance_description"]

    def test_restaurant_data_ai_analysis_with_pattern_learning(self):
        """Test AI analysis with pattern learning results."""
        ai_data = {
            "confidence_score": 0.85,
            "provider_used": "openai",
            "pattern_learning": {
                "site_patterns_identified": ["menu_section_div", "price_span_class"],
                "extraction_confidence": 0.92,
                "patterns_learned": True
            }
        }
        
        restaurant = RestaurantData(
            name="Test Restaurant", 
            ai_analysis=ai_data
        )
        
        assert restaurant.ai_analysis["pattern_learning"]["patterns_learned"] is True
        assert restaurant.ai_analysis["pattern_learning"]["extraction_confidence"] == 0.92
        assert len(restaurant.ai_analysis["pattern_learning"]["site_patterns_identified"]) == 2