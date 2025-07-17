"""Custom OpenAI-compatible extractor for restaurant data."""

import logging
from typing import Dict, Any, Optional, List
import requests
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class CustomExtractor:
    """Custom OpenAI-compatible API extractor."""
    
    def __init__(self, api_key: str, base_url: str, model_name: str = "gpt-3.5-turbo"):
        """Initialize custom extractor.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API endpoint
            model_name: Model name to use
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout = 30
        
        # Ensure base_url ends with the correct path
        if not self.base_url.endswith('/v1'):
            self.base_url = f"{self.base_url}/v1"
    
    def extract_nutritional_info(self, content: str, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract nutritional information using custom API.
        
        Args:
            content: Raw content from restaurant page
            menu_items: List of menu items to analyze
            
        Returns:
            Dictionary with nutritional analysis
        """
        try:
            # Prepare menu items for analysis
            menu_text = ""
            for item in menu_items:
                if isinstance(item, dict):
                    name = item.get('name', '')
                    description = item.get('description', '')
                    price = item.get('price', '')
                    menu_text += f"- {name}: {description} ({price})\n"
            
            # Create prompt for nutritional analysis
            prompt = f"""
            Analyze the following restaurant menu items for nutritional information:
            
            {menu_text}
            
            Please provide:
            1. Dietary accommodations (vegetarian, vegan, gluten-free, etc.)
            2. Healthy options identified
            3. Nutritional highlights or concerns
            4. Overall nutritional assessment
            
            Format your response as JSON with the following structure:
            {{
                "dietary_accommodations": ["vegetarian", "vegan", "gluten-free"],
                "healthy_options": ["item1", "item2"],
                "nutritional_highlights": ["highlight1", "highlight2"],
                "overall_assessment": "brief assessment"
            }}
            """
            
            # Make API call
            response = self._make_api_call(prompt)
            
            # Parse and return results
            return self._parse_nutritional_response(response)
            
        except Exception as e:
            logger.error(f"Error in custom nutritional extraction: {e}")
            return {
                "error": str(e),
                "dietary_accommodations": [],
                "healthy_options": [],
                "nutritional_highlights": [],
                "overall_assessment": "Analysis failed"
            }
    
    def extract_cuisine_classification(self, content: str, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract cuisine classification using custom API.
        
        Args:
            content: Raw content from restaurant page
            menu_items: List of menu items to analyze
            
        Returns:
            Dictionary with cuisine classification
        """
        try:
            # Prepare menu items for analysis
            menu_text = ""
            for item in menu_items:
                if isinstance(item, dict):
                    name = item.get('name', '')
                    description = item.get('description', '')
                    menu_text += f"- {name}: {description}\n"
            
            # Create prompt for cuisine classification
            prompt = f"""
            Analyze the following restaurant menu to classify the cuisine type:
            
            {menu_text}
            
            Please provide:
            1. Primary cuisine type (e.g., Italian, Mexican, Asian, etc.)
            2. Secondary cuisine influences
            3. Cuisine confidence score (0-1)
            4. Reasoning for classification
            
            Format your response as JSON:
            {{
                "primary_cuisine": "cuisine_type",
                "secondary_influences": ["influence1", "influence2"],
                "confidence_score": 0.85,
                "reasoning": "explanation"
            }}
            """
            
            # Make API call
            response = self._make_api_call(prompt)
            
            # Parse and return results
            return self._parse_cuisine_response(response)
            
        except Exception as e:
            logger.error(f"Error in custom cuisine classification: {e}")
            return {
                "error": str(e),
                "primary_cuisine": "Unknown",
                "secondary_influences": [],
                "confidence_score": 0.0,
                "reasoning": "Analysis failed"
            }
    
    def extract_price_analysis(self, content: str, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract price analysis using custom API.
        
        Args:
            content: Raw content from restaurant page
            menu_items: List of menu items to analyze
            
        Returns:
            Dictionary with price analysis
        """
        try:
            # Prepare menu items for analysis
            menu_text = ""
            for item in menu_items:
                if isinstance(item, dict):
                    name = item.get('name', '')
                    price = item.get('price', '')
                    menu_text += f"- {name}: {price}\n"
            
            # Create prompt for price analysis
            prompt = f"""
            Analyze the following restaurant menu prices:
            
            {menu_text}
            
            Please provide:
            1. Price range category (budget, mid-range, upscale, fine-dining)
            2. Average price per item
            3. Value assessment
            4. Price comparison notes
            
            Format your response as JSON:
            {{
                "price_range": "mid-range",
                "average_price": "$15.00",
                "value_assessment": "good value",
                "comparison_notes": "competitive pricing"
            }}
            """
            
            # Make API call
            response = self._make_api_call(prompt)
            
            # Parse and return results
            return self._parse_price_response(response)
            
        except Exception as e:
            logger.error(f"Error in custom price analysis: {e}")
            return {
                "error": str(e),
                "price_range": "Unknown",
                "average_price": "$0.00",
                "value_assessment": "Analysis failed",
                "comparison_notes": "Could not analyze"
            }
    
    def _make_api_call(self, prompt: str) -> str:
        """Make API call to custom endpoint.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            Response text from the API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_nutritional_response(self, response: str) -> Dict[str, Any]:
        """Parse nutritional analysis response.
        
        Args:
            response: Raw response from API
            
        Returns:
            Parsed nutritional data
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)
            return {
                "dietary_accommodations": data.get("dietary_accommodations", []),
                "healthy_options": data.get("healthy_options", []),
                "nutritional_highlights": data.get("nutritional_highlights", []),
                "overall_assessment": data.get("overall_assessment", "")
            }
        except json.JSONDecodeError:
            # Fallback to text parsing
            return {
                "dietary_accommodations": [],
                "healthy_options": [],
                "nutritional_highlights": [],
                "overall_assessment": response[:200]  # First 200 chars
            }
    
    def _parse_cuisine_response(self, response: str) -> Dict[str, Any]:
        """Parse cuisine classification response.
        
        Args:
            response: Raw response from API
            
        Returns:
            Parsed cuisine data
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)
            return {
                "primary_cuisine": data.get("primary_cuisine", "Unknown"),
                "secondary_influences": data.get("secondary_influences", []),
                "confidence_score": data.get("confidence_score", 0.0),
                "reasoning": data.get("reasoning", "")
            }
        except json.JSONDecodeError:
            # Fallback to text parsing
            return {
                "primary_cuisine": "Unknown",
                "secondary_influences": [],
                "confidence_score": 0.0,
                "reasoning": response[:200]  # First 200 chars
            }
    
    def _parse_price_response(self, response: str) -> Dict[str, Any]:
        """Parse price analysis response.
        
        Args:
            response: Raw response from API
            
        Returns:
            Parsed price data
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)
            return {
                "price_range": data.get("price_range", "Unknown"),
                "average_price": data.get("average_price", "$0.00"),
                "value_assessment": data.get("value_assessment", "Unknown"),
                "comparison_notes": data.get("comparison_notes", "")
            }
        except json.JSONDecodeError:
            # Fallback to text parsing
            return {
                "price_range": "Unknown",
                "average_price": "$0.00",
                "value_assessment": "Unknown",
                "comparison_notes": response[:200]  # First 200 chars
            }
    
    def test_connection(self) -> bool:
        """Test connection to custom API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self._make_api_call("Test connection")
            return True
        except Exception as e:
            logger.error(f"Custom API connection test failed: {e}")
            return False