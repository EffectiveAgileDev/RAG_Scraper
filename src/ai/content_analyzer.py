"""AI-powered content analyzer for advanced restaurant data extraction."""

import logging
from typing import Dict, List, Any, Optional, Union
import hashlib
import json
from datetime import datetime, timedelta
import requests
import base64
import os

from src.ai.llm_extractor import LLMExtractor
from src.ai.confidence_scorer import ConfidenceScorer
from src.ai.claude_extractor import ClaudeExtractor
from src.ai.ollama_extractor import OllamaExtractor
from src.ai.custom_extractor import CustomExtractor
from src.ai.multimodal_extractor import MultiModalExtractor
from src.ai.pattern_learner import PatternLearner
from src.ai.dynamic_prompt_adjuster import DynamicPromptAdjuster
from src.ai.traditional_fallback_extractor import TraditionalFallbackExtractor

logger = logging.getLogger(__name__)


class AIContentAnalyzer:
    """Analyzes restaurant content using AI for enhanced extraction."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI Content Analyzer.

        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        # Store for backward compatibility
        self.api_key = api_key
        
        self.llm_extractor = LLMExtractor(api_key=api_key)
        self.confidence_scorer = ConfidenceScorer()
        self._cache = {}
        self._cache_ttl = timedelta(minutes=15)
        self.config = {
            "extraction_prompts": {},
            "confidence_weights": {"llm": 0.8, "traditional": 0.2},
            "providers": {
                "openai": {"enabled": True, "api_key": api_key},
                "claude": {"enabled": False, "api_key": None},
                "ollama": {
                    "enabled": False,
                    "endpoint": "http://localhost:11434",
                },
                "llama_cpp": {"enabled": False, "model_path": None},
                "custom": {
                    "enabled": False,
                    "api_key": None,
                    "base_url": None,
                    "model_name": None,
                    "provider_name": "Custom Provider"
                },
            },
            "default_provider": "openai",
            "fallback_enabled": True,
            "multimodal_enabled": False,
            "pattern_learning_enabled": False,
            "dynamic_prompts_enabled": False,
        }

        # Initialize additional extractors
        self.claude_extractor = None
        self.ollama_extractor = None
        self.custom_extractor = None
        self.multimodal_extractor = None
        self.pattern_learner = None
        self.prompt_adjuster = None
        self.fallback_extractor = None

    def _get_restaurant_industry_config(
        self, categories: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get restaurant industry configuration."""
        if categories is None:
            categories = [
                {
                    "category": "Restaurant Info",
                    "fields": ["name", "cuisine", "location", "hours"],
                },
                {
                    "category": "Menu Items",
                    "fields": ["name", "description", "price", "dietary_info"],
                },
                {
                    "category": "Amenities",
                    "fields": ["parking", "wifi", "accessibility"],
                },
            ]

        return {
            "industry": "Restaurant",
            "categories": categories,
            "confidence_weights": self.config["confidence_weights"],
        }

    def analyze_content(
        self,
        content: str,
        menu_items: List[Dict[str, Any]],
        analysis_type: str,
        monitor_performance: bool = False,
        custom_questions: List[str] = None,
    ) -> Dict[str, Any]:
        """Analyze content for nutritional and other insights.

        Args:
            content: Raw webpage content
            menu_items: List of menu items to analyze
            analysis_type: Type of analysis (e.g., "nutritional")
            monitor_performance: Whether to track performance metrics
            custom_questions: Optional list of custom questions to include in analysis

        Returns:
            Analysis results with nutritional context
        """
        try:
            # Check cache
            cache_key = self._get_cache_key(content, menu_items, analysis_type)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

            start_time = datetime.now() if monitor_performance else None

            if analysis_type == "nutritional":
                # Pass the AI config for model selection
                ai_config = getattr(self, '_current_ai_config', {})
                result = self._analyze_nutritional_content(content, menu_items, custom_questions, ai_config)
            else:
                result = {"error": f"Unknown analysis type: {analysis_type}"}

            if monitor_performance:
                result["performance_metrics"] = {
                    "processing_time": (
                        datetime.now() - start_time
                    ).total_seconds(),
                    "memory_usage": "Not implemented",  # Placeholder
                }

            # Cache result
            self._add_to_cache(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "nutritional_context": [],
                "dietary_restrictions": {},
            }

    def _analyze_nutritional_content(
        self, content: str, menu_items: List[Dict[str, Any]], custom_questions: List[str] = None, ai_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze nutritional content of menu items."""
        print(f"DEBUG: _analyze_nutritional_content called with custom_questions: {custom_questions}")
        if not menu_items:
            return {"nutritional_context": [], "dietary_restrictions": {}}

        # Check which provider to use
        provider = self.config.get("default_provider", "openai")
        
        # Use custom provider if configured
        if (provider == "custom" and 
            self.config["providers"]["custom"]["enabled"] and 
            self.config["providers"]["custom"]["api_key"]):
            try:
                return self.extract_with_custom(content, menu_items, "nutritional", custom_questions)
            except Exception as e:
                logger.error(f"Custom provider failed, falling back to OpenAI: {e}")
                provider = "openai"
        
        # Use Claude if configured
        elif (provider == "claude" and 
              self.config["providers"]["claude"]["enabled"] and 
              self.config["providers"]["claude"]["api_key"]):
            try:
                return self.extract_with_claude(content, provider, custom_questions)
            except Exception as e:
                logger.error(f"Claude provider failed, falling back to OpenAI: {e}")
                provider = "openai"
        
        # Use Ollama if configured
        elif (provider == "ollama" and 
              self.config["providers"]["ollama"]["enabled"]):
            try:
                return self.extract_with_ollama(content, custom_questions)
            except Exception as e:
                logger.error(f"Ollama provider failed, falling back to OpenAI: {e}")
                provider = "openai"

        # Build enhanced prompt with custom questions support
        print(f"DEBUG: Building prompt with custom_questions: {custom_questions}")
        if custom_questions and len(custom_questions) > 0:
            print(f"DEBUG: Adding {len(custom_questions)} custom questions to prompt")
        else:
            print("DEBUG: No custom questions to add to prompt")
        
        prompt = self._build_enhanced_prompt(content, menu_items, custom_questions)

        # Create industry configuration for Restaurant
        industry_config = {
            "industry": "Restaurant",
            "categories": [
                {
                    "category": "Menu Items",
                    "fields": ["name", "description", "price", "dietary_info"],
                },
                {
                    "category": "Restaurant Info",
                    "fields": ["hours", "location", "contact", "cuisine_type"],
                },
                {
                    "category": "Amenities",
                    "fields": [
                        "parking",
                        "wifi",
                        "accessibility",
                        "payment_methods",
                    ],
                },
            ],
            "confidence_weights": {"llm": 0.8, "traditional": 0.2},
        }

        # Use direct OpenAI call with our custom prompt when custom questions are present
        if custom_questions and len(custom_questions) > 0:
            print("DEBUG: Using direct OpenAI call for custom questions")
            # Get the model name from AI config (passed from UI)
            model_name = (ai_config or {}).get('model', 'gpt-3.5-turbo')
            print(f"DEBUG: Using model: {model_name}")
            llm_result = self._call_openai_direct(prompt, model_name)
        else:
            print("DEBUG: Using standard LLMExtractor")
            # Extract categories from industry_config for LLMExtractor
            categories = [cat["category"] for cat in industry_config.get("categories", [])]
            llm_result = self.llm_extractor.extract(
                content=content,
                industry="restaurant",
                categories=categories,
                custom_instructions="Extract restaurant data including menu items, amenities, and contact information."
            )

        # Process LLM result into expected format
        return self._process_nutritional_result(llm_result, menu_items, custom_questions)

    def _process_nutritional_result(
        self, llm_result: Dict[str, Any], menu_items: List[Dict[str, Any]], custom_questions: List[str] = None
    ) -> Dict[str, Any]:
        """Process LLM result into enhanced RAG context format."""
        print(f"DEBUG: _process_nutritional_result called with llm_result keys: {list(llm_result.keys()) if llm_result else 'None'}")
        
        # Helper function to create default structure with custom_questions preserved
        def create_default_structure(preserve_custom_questions=None):
            default = {
                "menu_enhancements": [
                    {
                        "item_name": item.get("name", "Unknown"),
                        "enhanced_description": item.get("name", "Unknown"),
                        "dietary_tags": [],
                        "meal_category": "unknown",
                        "price_category": "unknown"
                    }
                    for item in menu_items
                ],
                "restaurant_characteristics": {
                    "ambiance": "Unknown",
                    "dining_style": "unknown", 
                    "specialties": [],
                    "target_demographic": "unknown"
                },
                "customer_amenities": {
                    "parking": "unknown",
                    "family_friendly": False,
                    "accessibility": "unknown", 
                    "payment_methods": [],
                    "reservations": "unknown"
                }
            }
            # Preserve custom_questions if they were provided
            if preserve_custom_questions:
                # Convert to expected format with "No information found" answers
                default["custom_questions"] = [
                    {"question": q, "answer": "No information found"}
                    for q in preserve_custom_questions
                ]
                print(f"DEBUG: Preserved {len(preserve_custom_questions)} custom questions in default structure")
            return default
        
        # Default structure if LLM fails - preserve custom questions!
        if not llm_result or "error" in llm_result:
            print("DEBUG: LLM result is empty or has error, returning default structure with preserved custom questions")
            return create_default_structure(custom_questions)
        
        # Try to parse LLM result if it contains JSON
        try:
            # Check if this is direct OpenAI response with the expected structure
            if "menu_enhancements" in llm_result:
                print("DEBUG: Found menu_enhancements in llm_result, returning as-is")
                # Ensure custom_questions are preserved if present
                if "custom_questions" in llm_result:
                    print(f"DEBUG: Preserving {len(llm_result['custom_questions'])} custom questions in result")
                else:
                    print("DEBUG: No custom_questions found in llm_result")
                return llm_result
            
            # Check if this is the LLMExtractor format with extractions
            if "extractions" in llm_result:
                print("DEBUG: Found extractions in llm_result, processing...")
                extractions = llm_result.get("extractions", [])
                if extractions and isinstance(extractions, list) and len(extractions) > 0:
                    # Look for JSON content in the extractions
                    for extraction in extractions:
                        if "extracted_data" in extraction:
                            content = extraction["extracted_data"]
                            print(f"DEBUG: Found extracted_data: {content}")
                            if isinstance(content, dict):
                                # Check if it has our expected structure
                                if "menu_enhancements" in content or "restaurant_characteristics" in content:
                                    print("DEBUG: Extracted data has expected structure, returning it")
                                    # Check for custom_questions preservation
                                    if "custom_questions" in content:
                                        print(f"DEBUG: Preserving {len(content['custom_questions'])} custom questions from extracted data")
                                    else:
                                        print("DEBUG: No custom_questions found in extracted data")
                                    return content
                                # Check if the content has an "analysis" field with JSON string
                                elif "analysis" in content and isinstance(content["analysis"], str):
                                    try:
                                        # Try to parse the analysis field as JSON
                                        analysis_str = content["analysis"]
                                        # Remove markdown code block if present
                                        if analysis_str.startswith("```json"):
                                            analysis_str = analysis_str[7:]  # Remove ```json
                                        if analysis_str.endswith("```"):
                                            analysis_str = analysis_str[:-3]  # Remove ```
                                        parsed_analysis = json.loads(analysis_str.strip())
                                        print("DEBUG: Successfully parsed analysis JSON string")
                                        # Check for custom_questions preservation
                                        if "custom_questions" in parsed_analysis:
                                            print(f"DEBUG: Preserving {len(parsed_analysis['custom_questions'])} custom questions from parsed analysis")
                                        else:
                                            print("DEBUG: No custom_questions found in parsed analysis")
                                        return parsed_analysis
                                    except:
                                        # If parsing fails, wrap in structure
                                        print("DEBUG: Failed to parse analysis JSON, wrapping in structure")
                                        # Check if there were custom_questions in the original content
                                        custom_questions = content.get("custom_questions", None)
                                        fallback = create_default_structure(custom_questions)
                                        fallback["restaurant_characteristics"]["analysis"] = content.get("analysis", str(content))
                                        return fallback
                                else:
                                    # If it's just analysis text, wrap it in our structure
                                    print("DEBUG: Extracted data is analysis text, wrapping in structure")
                                    # Check if there were custom_questions in the original content
                                    custom_questions = content.get("custom_questions", None)
                                    fallback = create_default_structure(custom_questions)
                                    fallback["restaurant_characteristics"]["analysis"] = content.get("analysis", str(content))
                                    return fallback
            
            # If it's some other format, try to extract useful information
            print(f"DEBUG: Unrecognized format, returning whole result: {llm_result}")
            return llm_result
            
        except Exception as e:
            logger.error(f"Error processing LLM result: {e}")
            print(f"DEBUG: Error processing LLM result: {e}")
            # Check if custom_questions exist in the original llm_result before error
            custom_questions = None
            if llm_result and isinstance(llm_result, dict):
                custom_questions = llm_result.get("custom_questions", None)
            fallback = create_default_structure(custom_questions)
            fallback["restaurant_characteristics"]["ambiance"] = "AI processing error"
            return fallback

    def analyze_prices(
        self, prices: Dict[str, Any], location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze price ranges and competitive positioning.

        Args:
            prices: Price data including min, max, and items
            location: Restaurant location for context

        Returns:
            Price analysis results
        """
        try:
            if not location:
                location_context = "Location not specified"
            else:
                location_context = location

            prompt = f"""
            Analyze restaurant pricing:
            - Price range: ${prices.get('min', 0)} - ${prices.get('max', 0)}
            - Location: {location_context}
            - Items: {json.dumps(prices.get('items', []), indent=2)}
            
            Provide:
            1. Price tier classification (budget/moderate/upscale/fine-dining)
            2. Competitive positioning analysis
            3. Value proposition insights
            4. Portion expectations based on pricing
            """

            # Create industry configuration for Restaurant
            industry_config = {
                "industry": "Restaurant",
                "categories": [
                    {
                        "category": "Pricing",
                        "fields": ["menu_prices", "price_range", "value"],
                    },
                    {
                        "category": "Location",
                        "fields": [
                            "address",
                            "neighborhood",
                            "market_context",
                        ],
                    },
                ],
            }

            result = self.llm_extractor.extract(
                content="",
                industry="Restaurant",
                industry_config=industry_config,
                custom_prompt=prompt,
            )

            # Ensure required fields
            if "price_tier" not in result:
                result["price_tier"] = self._determine_price_tier(prices)

            result["location_context"] = location_context
            return result

        except Exception as e:
            logger.error(f"Error in price analysis: {str(e)}")
            return {
                "price_tier": "unknown",
                "location_context": location_context,
                "error": str(e),
            }

    def _determine_price_tier(self, prices: Dict[str, Any]) -> str:
        """Determine price tier based on price ranges."""
        max_price = prices.get("max", 0)
        if max_price < 15:
            return "budget"
        elif max_price < 30:
            return "moderate"
        elif max_price < 50:
            return "upscale"
        else:
            return "fine-dining"

    def classify_cuisine(
        self, content: str, menu_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Classify cuisine type with cultural context.

        Args:
            content: Restaurant webpage content
            menu_items: Menu items for analysis

        Returns:
            Cuisine classification results
        """
        prompt = f"""
        Analyze the restaurant's cuisine based on:
        Content: {content[:1000]}...
        Menu items: {json.dumps(menu_items, indent=2)}
        
        Provide:
        1. Primary cuisine type
        2. Cuisine influences (list)
        3. Cultural context explanation
        4. Authenticity score (0-1)
        5. Authenticity indicators
        6. Cuisine tags for search optimization
        """

        cuisine_categories = [
            {
                "category": "Cuisine",
                "fields": ["cuisine_type", "cultural_context", "authenticity"],
            },
            {
                "category": "Menu Items",
                "fields": ["dishes", "ingredients", "cultural_significance"],
            },
        ]
        industry_config = self._get_restaurant_industry_config(
            cuisine_categories
        )

        result = self.llm_extractor.extract(
            content=content,
            industry="Restaurant",
            industry_config=industry_config,
            custom_prompt=prompt,
        )
        return result

    def analyze_ambiguous_items(
        self, menu_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze ambiguous menu descriptions."""
        prompt = f"""
        Interpret these ambiguous menu items:
        {json.dumps(menu_items, indent=2)}
        
        For each item, provide:
        1. Likely category (seafood, meat, vegetarian, etc.)
        2. Confidence score (0-1)
        3. Alternative interpretations
        """

        result = self.llm_extractor.extract(
            content="", industry="Restaurant", custom_prompt=prompt
        )
        return {"interpreted_items": result.get("items", [])}

    def extract_dietary_info(self, content: str) -> Dict[str, Any]:
        """Extract dietary accommodation information."""
        prompt = """
        Extract dietary accommodation information:
        1. Available dietary options (gluten-free, vegan, etc.)
        2. Specific menu items for each dietary need
        3. Cross-contamination warnings
        4. Overall dietary friendliness score (0-1)
        5. Missing dietary information
        """

        result = self.llm_extractor.extract(
            content=content, industry="Restaurant", custom_prompt=prompt
        )
        return result

    def analyze_specialties(self, content: str) -> Dict[str, Any]:
        """Analyze restaurant specialties and signature dishes."""
        prompt = """
        Identify restaurant specialties:
        1. Signature dishes (ranked by prominence)
        2. Special cooking methods
        3. Unique selling points
        4. Recommendations for first-time visitors
        """

        result = self.llm_extractor.extract(
            content=content, industry="Restaurant", custom_prompt=prompt
        )
        return result

    def process_multilingual_content(
        self, menu_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process multilingual menu content."""
        prompt = f"""
        Process multilingual menu items:
        {json.dumps(menu_items, indent=2)}
        
        For each non-English item:
        1. Identify original language
        2. Provide translation
        3. Add pronunciation guide
        4. Explain cultural significance
        """

        result = self.llm_extractor.extract(
            content="", industry="Restaurant", custom_prompt=prompt
        )
        return result

    def structure_content(self, unstructured_content: str) -> Dict[str, Any]:
        """Convert unstructured content to structured menu."""
        prompt = f"""
        Structure this unstructured menu content into categories:
        {unstructured_content}
        
        Create structured menu with:
        1. Appetizers
        2. Main courses
        3. Desserts
        4. Beverages
        
        Include prices and portion info where mentioned.
        """

        result = self.llm_extractor.extract(
            unstructured_content, custom_prompt=prompt
        )
        return result

    def calculate_integrated_confidence(
        self, analysis_result: Dict[str, Any], source_reliability: float = 0.8
    ) -> float:
        """Calculate integrated confidence score."""
        factors = {
            "source_reliability": source_reliability,
            "extraction_method": analysis_result.get(
                "extraction_method", "llm"
            ),
            "llm_confidence": analysis_result.get("llm_confidence", 0.7),
        }

        # Simple weighted average for now
        weights = self.config["confidence_weights"]
        llm_weight = weights.get("llm", 0.8)

        confidence = (
            factors["source_reliability"] * 0.3
            + factors["llm_confidence"] * llm_weight
        )

        return min(max(confidence, 0.0), 1.0)

    def batch_analyze(
        self, pages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Batch analyze multiple pages."""
        results = []
        for page in pages:
            result = self.analyze_content(
                content=page.get("content", ""),
                menu_items=page.get("menu_items", []),
                analysis_type="nutritional",
            )
            result["url"] = page.get("url", "")
            results.append(result)
        return results

    def update_configuration(self, custom_config: Dict[str, Any]) -> None:
        """Update analyzer configuration."""
        self.config.update(custom_config)

    def _get_cache_key(
        self, content: str, menu_items: List, analysis_type: str
    ) -> str:
        """Generate cache key for content."""
        data = f"{content[:1000]}{str(menu_items)}{analysis_type}"
        return hashlib.md5(data.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache if valid."""
        if key in self._cache:
            cached_data = self._cache[key]
            if datetime.now() - cached_data["timestamp"] < self._cache_ttl:
                return cached_data["result"]
            else:
                del self._cache[key]
        return None

    def _add_to_cache(self, key: str, result: Dict[str, Any]) -> None:
        """Add result to cache."""
        self._cache[key] = {"result": result, "timestamp": datetime.now()}

    # =================================================================
    # OPTIONAL ADVANCED AI FEATURES
    # =================================================================

    def extract_with_claude(
        self, content: str, provider: str = "claude", custom_questions: List[str] = None
    ) -> Dict[str, Any]:
        """Extract content using Claude AI."""
        if not self.claude_extractor:
            self.claude_extractor = ClaudeExtractor(
                api_key=self.config["providers"]["claude"]["api_key"]
            )

        try:
            # Use enhanced prompt if custom questions are present
            if custom_questions and len(custom_questions) > 0:
                prompt = self._build_enhanced_prompt(content, [], custom_questions)
                # TODO: Implement direct Claude API call with custom prompt
                # For now, fall back to traditional extraction
                result = self.claude_extractor.extract(
                    content=content,
                    industry="Restaurant",
                    model=self.config["providers"]["claude"].get(
                        "model", "claude-3-opus-20240229"
                    ),
                )
                # Add custom questions note
                result["custom_questions_note"] = "Custom questions not yet implemented for Claude provider"
            else:
                result = self.claude_extractor.extract(
                    content=content,
                    industry="Restaurant",
                    model=self.config["providers"]["claude"].get(
                        "model", "claude-3-opus-20240229"
                    ),
                )
            result["provider_used"] = "claude"
            return result
        except Exception as e:
            logger.error(f"Claude extraction failed: {str(e)}")
            if self.config["fallback_enabled"]:
                return self._fallback_to_openai(content)
            raise

    def extract_with_ollama(self, content: str, custom_questions: List[str] = None) -> Dict[str, Any]:
        """Extract content using Ollama local LLM."""
        if not self.ollama_extractor:
            self.ollama_extractor = OllamaExtractor(
                endpoint=self.config["providers"]["ollama"]["endpoint"]
            )

        # Use enhanced prompt if custom questions are present
        if custom_questions and len(custom_questions) > 0:
            prompt = self._build_enhanced_prompt(content, [], custom_questions)
            # TODO: Implement direct Ollama API call with custom prompt
            # For now, fall back to traditional extraction
            result = self.ollama_extractor.extract(content=content)
            result["custom_questions_note"] = "Custom questions not yet implemented for Ollama provider"
        else:
            result = self.ollama_extractor.extract(content=content)
        
        result["provider_used"] = "ollama"
        result["external_calls"] = 0
        return result

    def extract_with_custom(
        self, content: str, menu_items: List[Dict[str, Any]], analysis_type: str = "nutritional", custom_questions: List[str] = None
    ) -> Dict[str, Any]:
        """Extract content using custom OpenAI-compatible API."""
        if not self.custom_extractor:
            custom_config = self.config["providers"]["custom"]
            self.custom_extractor = CustomExtractor(
                api_key=custom_config["api_key"],
                base_url=custom_config["base_url"],
                model_name=custom_config.get("model_name", "gpt-3.5-turbo")
            )

        try:
            result = {}
            
            # Use enhanced prompt if custom questions are present
            if custom_questions and len(custom_questions) > 0:
                prompt = self._build_enhanced_prompt(content, menu_items, custom_questions)
                # TODO: Implement direct custom provider API call with custom prompt
                # For now, fall back to traditional extraction
                if analysis_type == "nutritional":
                    result = self.custom_extractor.extract_nutritional_info(content, menu_items)
                elif analysis_type == "cuisine":
                    result = self.custom_extractor.extract_cuisine_classification(content, menu_items)
                elif analysis_type == "price":
                    result = self.custom_extractor.extract_price_analysis(content, menu_items)
                else:
                    result = self.custom_extractor.extract_nutritional_info(content, menu_items)
                result["custom_questions_note"] = "Custom questions not yet implemented for custom provider"
            else:
                # Perform analysis based on type
                if analysis_type == "nutritional":
                    result = self.custom_extractor.extract_nutritional_info(content, menu_items)
                elif analysis_type == "cuisine":
                    result = self.custom_extractor.extract_cuisine_classification(content, menu_items)
                elif analysis_type == "price":
                    result = self.custom_extractor.extract_price_analysis(content, menu_items)
                else:
                    # Default to nutritional analysis
                    result = self.custom_extractor.extract_nutritional_info(content, menu_items)
            
            result["provider_used"] = "custom"
            result["external_calls"] = 1
            return result
            
        except Exception as e:
            logger.error(f"Custom extraction failed: {str(e)}")
            if self.config["fallback_enabled"]:
                return self._fallback_to_openai(content)
            raise

    def analyze_multimodal_content(
        self, content: str, images: List[str]
    ) -> Dict[str, Any]:
        """Analyze content with images using multi-modal AI."""
        if not self.multimodal_extractor:
            self.multimodal_extractor = MultiModalExtractor()

        result = self.multimodal_extractor.analyze_images(
            content=content, image_urls=images
        )
        result["processing_mode"] = "multimodal"
        return result

    def extract_with_pattern_learning(
        self, content: str, chain_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract content using learned patterns."""
        if not self.pattern_learner:
            self.pattern_learner = PatternLearner()

        result = self.pattern_learner.apply_learned_patterns(
            content=content, historical_patterns=chain_patterns
        )
        return result

    def extract_with_dynamic_prompts(self, content: str) -> Dict[str, Any]:
        """Extract content with dynamically adjusted prompts."""
        if not self.prompt_adjuster:
            self.prompt_adjuster = DynamicPromptAdjuster()

        complexity_analysis = self.prompt_adjuster.analyze_complexity(content)

        # Apply dynamic prompt based on complexity
        if complexity_analysis["complexity_score"] > 0.7:
            strategy = "creative_interpretation"
        else:
            strategy = "standard_extraction"

        result = complexity_analysis
        result["selected_strategy"] = strategy
        return result

    def extract_with_graceful_degradation(
        self, content: str
    ) -> Dict[str, Any]:
        """Extract content with graceful degradation to traditional methods."""
        if not self.fallback_extractor:
            self.fallback_extractor = TraditionalFallbackExtractor()

        # Simulate all AI services failing
        result = self.fallback_extractor.extract_traditional(content=content)
        result["ai_services_status"] = "all_unavailable"
        result["fallback_used"] = True
        return result

    def _fallback_to_openai(self, content: str) -> Dict[str, Any]:
        """Fallback to OpenAI when other providers fail."""
        logger.info("Falling back to OpenAI due to primary provider failure")
        return self.analyze_content(
            content=content, menu_items=[], analysis_type="nutritional"
        )

    def _build_enhanced_prompt(self, content: str, menu_items: List[Dict[str, Any]], custom_questions: List[str] = None) -> str:
        """Build enhanced prompt with custom questions for any provider."""
        # Build custom questions section
        custom_questions_section = ""
        if custom_questions and len(custom_questions) > 0:
            custom_questions_section = f"""

4. CUSTOM QUESTIONS:
Please answer these specific questions if information is available in the content:
{chr(10).join([f"- {q}" for q in custom_questions])}
"""

        # Build the enhanced prompt
        prompt = f"""
        Analyze this restaurant content for enhanced RAG system input:
        
        RESTAURANT CONTENT:
        {content}
        
        MENU ITEMS:
        {json.dumps(menu_items, indent=2)}
        
        Please provide enriched information that would be valuable for a chatbot to answer customer questions:
        
        1. MENU ENHANCEMENTS:
        - Infer ingredients and preparation methods for each menu item
        - Identify dietary accommodations (vegetarian, vegan, gluten-free, etc.)
        - Categorize items by meal type (appetizers, entrees, desserts, beverages)
        - Estimate price range category (budget/mid-range/upscale)
        
        2. RESTAURANT CHARACTERISTICS:
        - Describe the likely ambiance and atmosphere
        - Identify unique features or specialties
        - Infer target customer demographic
        - Categorize the dining experience type (casual, fine dining, fast-casual, etc.)
        
        3. CUSTOMER SERVICE INFO:
        - Extract or infer parking availability
        - Identify family-friendly features
        - Note accessibility information
        - Payment methods and reservation policies{custom_questions_section}
        
        Return JSON with this structure:
        {{
            "menu_enhancements": [
                {{
                    "item_name": "name",
                    "enhanced_description": "detailed description with ingredients",
                    "dietary_tags": ["vegetarian", "gluten-free"],
                    "meal_category": "entree",
                    "price_category": "mid-range"
                }}
            ],
            "restaurant_characteristics": {{
                "ambiance": "description of atmosphere",
                "dining_style": "casual/fine/fast-casual",
                "specialties": ["list of signature items or features"],
                "target_demographic": "families/young professionals/etc"
            }},
            "customer_amenities": {{
                "parking": "available/limited/street only",
                "family_friendly": true/false,
                "accessibility": "wheelchair accessible/limited",
                "payment_methods": ["cash", "card", "mobile"],
                "reservations": "required/recommended/not needed"
            }}{f''',
            "custom_questions": [
                {{
                    "question": "question text",
                    "answer": "answer or 'No information found'"
                }}
            ]''' if custom_questions and len(custom_questions) > 0 else ''}
        }}
        """
        return prompt

    def _call_openai_direct(self, prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Call OpenAI API directly with custom prompt for custom questions."""
        try:
            # Import OpenAI
            from openai import OpenAI
            
            # Use the API key passed to AIContentAnalyzer constructor
            # This should always be available since we validate it in the scraping handler
            api_key = self.api_key
            if not api_key:
                logger.error("No OpenAI API key available for custom questions - AIContentAnalyzer was not properly initialized")
                return {"error": "No API key available"}
            
            # Create OpenAI client
            client = OpenAI(api_key=api_key)
            
            print(f"DEBUG: Calling OpenAI with custom prompt: {prompt[:200]}...")
            
            # Make the API call with higher token limit for comprehensive analysis
            response = client.chat.completions.create(
                model=model,  # Use the model specified in UI settings
                messages=[
                    {"role": "system", "content": "You are an expert restaurant data analyzer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,  # Increased from 1500 to allow comprehensive analysis
                temperature=0.3
            )
            
            # Extract the response content
            result_text = response.choices[0].message.content
            print(f"DEBUG: OpenAI response: {result_text[:200]}...")
            
            # Try to parse as JSON
            try:
                result_json = json.loads(result_text)
                return result_json
            except json.JSONDecodeError:
                # If not valid JSON, wrap in extractions format
                return {
                    "extractions": [
                        {
                            "category": "AI Analysis",
                            "confidence": 0.8,
                            "extracted_data": {"analysis": result_text}
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Direct OpenAI call failed: {e}")
            return {"error": str(e)}
