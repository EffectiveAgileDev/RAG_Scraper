"""Claude AI extractor for restaurant content analysis."""

import logging
import requests
import json
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ClaudeExtractor:
    """Claude AI-powered content extractor."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude extractor.

        Args:
            api_key: Claude API key
        """
        self.api_key = api_key or ""
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.default_model = "claude-3-opus-20240229"

    def extract(
        self,
        content: str,
        industry: str = "Restaurant",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract information using Claude AI.

        Args:
            content: Content to analyze
            industry: Industry context
            model: Claude model to use

        Returns:
            Extraction results
        """
        if not self.api_key:
            raise ValueError("Claude API key not configured")

        model = model or self.default_model

        prompt = self._build_restaurant_prompt(content, industry)

        try:
            response = self._call_claude_api(prompt, model)
            return self._process_claude_response(response)
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            raise

    def _build_restaurant_prompt(self, content: str, industry: str) -> str:
        """Build prompt for restaurant content extraction."""
        return f"""
        Analyze this {industry.lower()} website content and extract structured information:

        Content:
        {content[:3000]}

        Please extract and return a JSON object with:
        1. menu_items: Array of menu items with names, descriptions, prices if available
        2. restaurant_info: Basic restaurant information
        3. cuisine_type: Type of cuisine
        4. price_range: Overall price range
        5. special_features: Any special features or offerings
        6. confidence: Your confidence in the extraction (0-1)

        Respond with only valid JSON.
        """

    def _call_claude_api(self, prompt: str, model: str) -> Dict[str, Any]:
        """Call Claude API with the prompt."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        payload = {
            "model": model,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post(
            self.base_url, headers=headers, json=payload, timeout=30
        )

        if response.status_code != 200:
            raise Exception(
                f"Claude API error: {response.status_code} - {response.text}"
            )

        return response.json()

    def _process_claude_response(
        self, response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Claude API response."""
        try:
            content = response["content"][0]["text"]

            # Try to parse as JSON
            if content.startswith("{"):
                extracted_data = json.loads(content)
            else:
                # Fallback parsing if not pure JSON
                extracted_data = {
                    "menu_items": [],
                    "raw_response": content,
                    "parsing_note": "Response was not in JSON format",
                }

            # Add Claude-specific metadata
            extracted_data.update(
                {
                    "provider": "claude",
                    "model": response.get("model", "unknown"),
                    "usage": response.get("usage", {}),
                    "processing_time": 0,  # Would be calculated in real implementation
                }
            )

            return extracted_data

        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to process Claude response: {str(e)}")
            return {
                "error": f"Response processing failed: {str(e)}",
                "raw_response": response,
                "provider": "claude",
            }
