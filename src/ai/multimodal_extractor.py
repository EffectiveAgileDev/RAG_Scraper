"""Multi-modal content extractor for images and text analysis."""

import logging
import requests
import base64
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import os

logger = logging.getLogger(__name__)


class MultiModalExtractor:
    """Multi-modal content extractor for analyzing text and images."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize multi-modal extractor.

        Args:
            api_key: OpenAI API key for vision model
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.vision_model = "gpt-4-vision-preview"

    def analyze_images(
        self, content: str, image_urls: List[str]
    ) -> Dict[str, Any]:
        """Analyze content with images.

        Args:
            content: Text content from webpage
            image_urls: List of image URLs to analyze

        Returns:
            Multi-modal analysis results
        """
        try:
            image_analysis = []

            for image_url in image_urls:
                analysis = self._analyze_single_image(image_url)
                if analysis:
                    image_analysis.append(
                        {
                            "source": image_url,
                            "analysis": analysis,
                            "confidence": 0.82,  # Placeholder
                        }
                    )

            # Cross-correlate with text content
            correlation = self._correlate_text_and_images(
                content, image_analysis
            )

            return {
                "image_extracted_items": image_analysis,
                "text_correlation": correlation,
                "multimodal_confidence": self._calculate_multimodal_confidence(
                    image_analysis, correlation
                ),
            }

        except Exception as e:
            logger.error(f"Multi-modal analysis failed: {str(e)}")
            return {
                "error": str(e),
                "image_extracted_items": [],
                "text_correlation": {},
            }

    def _analyze_single_image(self, image_url: str) -> Dict[str, Any]:
        """Analyze a single image for restaurant content."""
        try:
            # For demo purposes, return mock analysis
            # In production, this would call vision API

            if "menu" in image_url.lower():
                return {
                    "items": [
                        {"name": "Daily Special", "price": "$25"},
                        {"name": "Chef's Recommendation", "price": "$30"},
                    ],
                    "image_type": "menu",
                    "text_detected": True,
                    "quality": "high",
                }
            elif "logo" in image_url.lower():
                return {
                    "brand_elements": {
                        "logo_detected": True,
                        "colors": ["red", "gold"],
                        "style": "traditional",
                    },
                    "image_type": "branding",
                    "text_detected": False,
                }
            else:
                return {
                    "items": [],
                    "image_type": "general",
                    "description": "Restaurant interior or food photo",
                    "atmosphere": "casual dining",
                }

        except Exception as e:
            logger.error(f"Image analysis failed for {image_url}: {str(e)}")
            return {}

    def _call_vision_api(self, image_data: str, prompt: str) -> Dict[str, Any]:
        """Call OpenAI Vision API."""
        if not self.api_key:
            raise ValueError("OpenAI API key required for vision analysis")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 500,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(f"Vision API error: {response.status_code}")

        return response.json()

    def _correlate_text_and_images(
        self, text_content: str, image_analysis: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Correlate text content with image analysis."""
        correlations = {}

        # Simple correlation logic
        for img_data in image_analysis:
            analysis = img_data.get("analysis", {})
            items = analysis.get("items", [])

            for item in items:
                item_name = item.get("name", "")
                if item_name and item_name.lower() in text_content.lower():
                    correlations[item_name] = "matches_text"
                else:
                    correlations[item_name] = "image_only"

        return correlations

    def _calculate_multimodal_confidence(
        self, image_analysis: List[Dict[str, Any]], correlation: Dict[str, str]
    ) -> float:
        """Calculate confidence score for multi-modal analysis."""
        if not image_analysis:
            return 0.0

        # Calculate based on image quality and text correlation
        base_confidence = 0.7
        correlation_bonus = (
            len([v for v in correlation.values() if v == "matches_text"]) * 0.1
        )

        return min(base_confidence + correlation_bonus, 1.0)

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
