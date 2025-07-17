"""Ollama local LLM extractor for restaurant content analysis."""

import logging
import requests
import json
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class OllamaExtractor:
    """Ollama local LLM extractor."""

    def __init__(self, endpoint: str = "http://localhost:11434"):
        """Initialize Ollama extractor.

        Args:
            endpoint: Ollama API endpoint
        """
        self.endpoint = endpoint.rstrip("/")
        self.default_model = "llama2"

    def extract(
        self, content: str, model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract information using Ollama local LLM.

        Args:
            content: Content to analyze
            model: Model to use (defaults to llama2)

        Returns:
            Extraction results
        """
        model = model or self.default_model

        try:
            # Check if Ollama is available
            self._check_ollama_status()

            prompt = self._build_extraction_prompt(content)
            response = self._call_ollama_api(prompt, model)

            return self._process_ollama_response(response)

        except Exception as e:
            logger.error(f"Ollama extraction failed: {str(e)}")
            raise

    def _check_ollama_status(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            raise Exception("Ollama service not available")

    def _build_extraction_prompt(self, content: str) -> str:
        """Build prompt for local LLM extraction."""
        return f"""
        Extract restaurant information from this content. Focus on:
        - Menu items and prices
        - Restaurant name and cuisine type
        - Contact information
        - Special features

        Content: {content[:2000]}

        Respond with structured information in a clear format.
        """

    def _call_ollama_api(self, prompt: str, model: str) -> Dict[str, Any]:
        """Call Ollama API."""
        url = f"{self.endpoint}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9},
        }

        response = requests.post(url, json=payload, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")

        return response.json()

    def _process_ollama_response(
        self, response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Ollama response."""
        try:
            extracted_text = response.get("response", "")

            # Parse the response for structured data
            result = {
                "menu_items": self._extract_menu_items(extracted_text),
                "raw_response": extracted_text,
                "model": response.get("model", "unknown"),
                "provider": "ollama",
                "local_processing": True,
                "done": response.get("done", False),
                "total_duration": response.get("total_duration", 0),
                "load_duration": response.get("load_duration", 0),
                "prompt_eval_count": response.get("prompt_eval_count", 0),
                "eval_count": response.get("eval_count", 0),
            }

            return result

        except Exception as e:
            logger.error(f"Failed to process Ollama response: {str(e)}")
            return {
                "error": f"Response processing failed: {str(e)}",
                "raw_response": response,
                "provider": "ollama",
            }

    def _extract_menu_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract menu items from Ollama response text."""
        # Simple extraction logic - in practice this would be more sophisticated
        lines = text.split("\n")
        items = []

        for line in lines:
            line = line.strip()
            if "$" in line and len(line) > 5:
                # Try to extract item name and price
                parts = line.split("$")
                if len(parts) >= 2:
                    name = parts[0].strip(" -•").strip()
                    price_text = "$" + parts[1].split()[0]

                    if name:
                        items.append(
                            {
                                "name": name,
                                "price": price_text,
                                "source": "ollama_extraction",
                            }
                        )

        return items
