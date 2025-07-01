"""Unit tests for LLM extractor functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
import time
from datetime import datetime, timedelta

# Import will fail until we implement the module
try:
    from src.ai.llm_extractor import LLMExtractor, LLMResponse, PromptTemplate
except ImportError:
    # Expected during RED phase
    LLMExtractor = None
    LLMResponse = None
    PromptTemplate = None


class TestLLMExtractor:
    """Test suite for LLM extractor."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "extractions": [
                {
                    "category": "Menu Items",
                    "confidence": 0.85,
                    "extracted_data": {
                        "characteristics": ["locally sourced ingredients", "seasonal menu"]
                    }
                }
            ],
            "source_attribution": "LLM extraction from webpage content"
        })
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    @pytest.fixture
    def llm_extractor(self, mock_openai_client):
        """Create LLM extractor instance for testing."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        with patch('src.ai.llm_extractor.OpenAI', return_value=mock_openai_client):
            return LLMExtractor(
                api_key="test-key",
                model="gpt-3.5-turbo",
                enable_cache=True,
                track_stats=True
            )

    @pytest.fixture
    def sample_industry_config(self):
        """Sample industry configuration."""
        return {
            "industry": "Restaurant",
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food and beverage offerings",
                    "customer_terms": ["food", "menu", "dishes"],
                    "website_terms": ["menu", "food", "dishes", "offerings"]
                },
                {
                    "category": "Dining Options",
                    "description": "Service and seating types",
                    "customer_terms": ["dining", "seating", "service"],
                    "website_terms": ["dining", "seating", "service", "options"]
                }
            ]
        }

    def test_llm_extractor_initialization(self):
        """Test LLM extractor initialization."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        with patch('src.ai.llm_extractor.OpenAI') as mock_openai:
            extractor = LLMExtractor(
                api_key="test-key",
                model="gpt-4",
                enable_cache=False,
                track_stats=True
            )
            
            assert extractor.api_key == "test-key"
            assert extractor.model == "gpt-4"
            assert extractor.enable_cache is False
            assert extractor.track_stats is True
            mock_openai.assert_called_once_with(api_key="test-key")

    def test_prompt_template_generation(self, llm_extractor, sample_industry_config):
        """Test prompt template generation for different industries."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        content = "Farm-to-table dining with seasonal ingredients"
        prompt = llm_extractor._generate_prompt(content, "Restaurant", sample_industry_config)
        
        assert "Restaurant" in prompt
        assert "Menu Items" in prompt
        assert "Dining Options" in prompt
        assert content in prompt
        assert "extract" in prompt.lower()
        assert "confidence" in prompt.lower()

    def test_extract_content_success(self, llm_extractor, sample_industry_config):
        """Test successful content extraction."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        content = "Farm-to-table dining with seasonal ingredients"
        result = llm_extractor.extract(content, "Restaurant", sample_industry_config)
        
        assert "extractions" in result
        assert len(result["extractions"]) > 0
        assert "source_attribution" in result
        
        extraction = result["extractions"][0]
        assert "category" in extraction
        assert "confidence" in extraction
        assert "extracted_data" in extraction
        assert 0.0 <= extraction["confidence"] <= 1.0

    def test_extract_with_confidence_threshold(self, llm_extractor, sample_industry_config):
        """Test extraction with confidence threshold filtering."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        content = "Good food and service"
        result = llm_extractor.extract(
            content, 
            "Restaurant", 
            sample_industry_config,
            confidence_threshold=0.8
        )
        
        # All returned extractions should meet threshold
        for extraction in result["extractions"]:
            assert extraction["confidence"] >= 0.8

    def test_api_failure_handling(self, llm_extractor, sample_industry_config):
        """Test graceful handling of API failures."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        # Mock API failure
        llm_extractor.client.chat.completions.create.side_effect = Exception("API Error")
        
        content = "Test content"
        result = llm_extractor.extract(content, "Restaurant", sample_industry_config)
        
        assert "extractions" in result
        assert len(result["extractions"]) == 0
        assert "error" in result
        assert "fallback_message" in result

    def test_caching_functionality(self, llm_extractor, sample_industry_config):
        """Test that results are cached properly."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        content = "Farm-to-table dining"
        
        # First call
        result1 = llm_extractor.extract(content, "Restaurant", sample_industry_config)
        
        # Second call - should use cache
        result2 = llm_extractor.extract(content, "Restaurant", sample_industry_config)
        
        assert result1 == result2
        
        # Should only have called the API once
        assert llm_extractor.client.chat.completions.create.call_count == 1

    def test_cache_disabled(self, sample_industry_config):
        """Test behavior when caching is disabled."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        with patch('src.ai.llm_extractor.OpenAI') as mock_openai:
            mock_client = mock_openai.return_value
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = '{"extractions": []}'
            mock_client.chat.completions.create.return_value = mock_response
            
            extractor = LLMExtractor(
                api_key="test-key",
                enable_cache=False
            )
            
            content = "Test content"
            
            # Make two identical calls
            extractor.extract(content, "Restaurant", sample_industry_config)
            extractor.extract(content, "Restaurant", sample_industry_config)
            
            # Should call API twice since caching is disabled
            assert mock_client.chat.completions.create.call_count == 2

    def test_usage_statistics_tracking(self, llm_extractor, sample_industry_config):
        """Test usage statistics tracking."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        content1 = "Farm-to-table dining"
        content2 = "Romantic atmosphere"
        
        # Make several extractions
        llm_extractor.extract(content1, "Restaurant", sample_industry_config)
        llm_extractor.extract(content2, "Restaurant", sample_industry_config)
        
        stats = llm_extractor.get_stats()
        
        assert "total_calls" in stats
        assert "successful_extractions" in stats
        assert "failed_extractions" in stats
        assert "average_confidence" in stats
        assert "cache_hit_rate" in stats
        
        assert stats["total_calls"] >= 2
        assert stats["successful_extractions"] >= 2

    def test_malformed_api_response_handling(self, llm_extractor, sample_industry_config):
        """Test handling of malformed API responses."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        # Mock malformed JSON response
        llm_extractor.client.chat.completions.create.return_value.choices[0].message.content = "Invalid JSON"
        
        content = "Test content"
        result = llm_extractor.extract(content, "Restaurant", sample_industry_config)
        
        assert "extractions" in result
        assert len(result["extractions"]) == 0
        assert "error" in result

    def test_empty_content_handling(self, llm_extractor, sample_industry_config):
        """Test handling of empty or whitespace-only content."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        # Test empty string
        result = llm_extractor.extract("", "Restaurant", sample_industry_config)
        assert len(result["extractions"]) == 0
        
        # Test whitespace only
        result = llm_extractor.extract("   \n\t  ", "Restaurant", sample_industry_config)
        assert len(result["extractions"]) == 0

    def test_industry_specific_extraction(self, llm_extractor):
        """Test that extraction adapts to different industries."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        medical_config = {
            "industry": "Medical",
            "categories": [
                {
                    "category": "Services",
                    "description": "Medical procedures and treatments"
                }
            ]
        }
        
        content = "Board-certified specialists providing comprehensive care"
        result = llm_extractor.extract(content, "Medical", medical_config)
        
        # Should adapt prompt and extraction to medical industry
        assert "extractions" in result
        # Verify the prompt generation was called with Medical industry
        call_args = llm_extractor.client.chat.completions.create.call_args
        assert "Medical" in call_args[1]["messages"][1]["content"]  # User message, not system message

    def test_batch_extraction(self, llm_extractor, sample_industry_config):
        """Test batch extraction of multiple content pieces."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        contents = [
            "Farm-to-table dining",
            "Romantic atmosphere",
            "Board-certified doctors"
        ]
        
        results = llm_extractor.extract_batch(contents, "Restaurant", sample_industry_config)
        
        assert len(results) == len(contents)
        for result in results:
            assert "extractions" in result
            assert "source_attribution" in result

    def test_prompt_template_customization(self, llm_extractor):
        """Test custom prompt template functionality."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        custom_template = """
        Extract information from: {content}
        Focus on industry: {industry}
        Categories: {categories}
        Custom instruction: Look for unique features.
        """
        
        llm_extractor.set_custom_template(custom_template)
        
        content = "Unique artisanal coffee"
        config = {"industry": "Restaurant", "categories": []}
        
        result = llm_extractor.extract(content, "Restaurant", config)
        
        # Verify custom template was used
        call_args = llm_extractor.client.chat.completions.create.call_args
        assert "unique features" in call_args[1]["messages"][1]["content"].lower()  # User message, not system message

    def test_response_validation(self, llm_extractor, sample_industry_config):
        """Test validation of LLM responses."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        # Mock response with invalid confidence scores
        invalid_response = json.dumps({
            "extractions": [
                {
                    "category": "Menu Items",
                    "confidence": 1.5,  # Invalid - over 1.0
                    "extracted_data": {}
                },
                {
                    "category": "Services",
                    "confidence": -0.1,  # Invalid - negative
                    "extracted_data": {}
                }
            ]
        })
        
        llm_extractor.client.chat.completions.create.return_value.choices[0].message.content = invalid_response
        
        content = "Test content"
        result = llm_extractor.extract(content, "Restaurant", sample_industry_config)
        
        # Should filter out invalid confidence scores
        valid_extractions = [e for e in result["extractions"] if 0.0 <= e["confidence"] <= 1.0]
        assert len(valid_extractions) == len(result["extractions"])

    def test_rate_limiting_respect(self, llm_extractor, sample_industry_config):
        """Test that rate limiting is respected."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        # Configure rate limiting
        llm_extractor.configure_rate_limiting(calls_per_minute=2)
        
        content = "Test content"
        
        # Make rapid successive calls
        start_time = time.time()
        for i in range(3):
            llm_extractor.extract(f"{content} {i}", "Restaurant", sample_industry_config)
        end_time = time.time()
        
        # Should take at least some time due to rate limiting
        assert end_time - start_time >= 1.0  # At least 1 second delay

    def test_token_usage_tracking(self, llm_extractor, sample_industry_config):
        """Test tracking of token usage for cost monitoring."""
        if not LLMExtractor:
            pytest.skip("LLMExtractor not implemented yet")
        
        # Mock response with usage information
        mock_response = llm_extractor.client.chat.completions.create.return_value
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        
        content = "Farm-to-table dining"
        llm_extractor.extract(content, "Restaurant", sample_industry_config)
        
        usage_stats = llm_extractor.get_token_usage()
        
        assert "total_tokens" in usage_stats
        assert "prompt_tokens" in usage_stats
        assert "completion_tokens" in usage_stats
        assert usage_stats["total_tokens"] >= 150


class TestPromptTemplate:
    """Test suite for prompt template functionality."""

    def test_prompt_template_creation(self):
        """Test prompt template creation."""
        if not PromptTemplate:
            pytest.skip("PromptTemplate not implemented yet")
        
        template = PromptTemplate(
            industry="Restaurant",
            categories=["Menu Items", "Services"],
            custom_instructions="Focus on unique features"
        )
        
        assert template.industry == "Restaurant"
        assert "Menu Items" in template.categories
        assert "unique features" in template.custom_instructions.lower()

    def test_prompt_generation(self):
        """Test prompt generation from template."""
        if not PromptTemplate:
            pytest.skip("PromptTemplate not implemented yet")
        
        template = PromptTemplate(
            industry="Restaurant",
            categories=["Menu Items"],
            custom_instructions="Extract menu information"
        )
        
        content = "Farm-to-table dining"
        prompt = template.generate(content)
        
        assert "Restaurant" in prompt
        assert "Menu Items" in prompt
        assert content in prompt
        assert "extract menu information" in prompt.lower()

    def test_template_validation(self):
        """Test template validation."""
        if not PromptTemplate:
            pytest.skip("PromptTemplate not implemented yet")
        
        # Test invalid industry
        with pytest.raises(ValueError):
            PromptTemplate(industry="", categories=["Menu Items"])
        
        # Test empty categories
        with pytest.raises(ValueError):
            PromptTemplate(industry="Restaurant", categories=[])


class TestLLMResponse:
    """Test suite for LLM response handling."""

    def test_llm_response_creation(self):
        """Test LLM response object creation."""
        if not LLMResponse:
            pytest.skip("LLMResponse not implemented yet")
        
        response_data = {
            "extractions": [
                {
                    "category": "Menu Items",
                    "confidence": 0.85,
                    "extracted_data": {"items": ["pasta", "pizza"]}
                }
            ],
            "source_attribution": "LLM extraction"
        }
        
        response = LLMResponse(response_data)
        
        assert len(response.extractions) == 1
        assert response.extractions[0]["category"] == "Menu Items"
        assert response.source_attribution == "LLM extraction"

    def test_response_validation(self):
        """Test response validation."""
        if not LLMResponse:
            pytest.skip("LLMResponse not implemented yet")
        
        # Test invalid response structure
        with pytest.raises(ValueError):
            LLMResponse({"invalid": "structure"})
        
        # Test invalid confidence scores
        invalid_data = {
            "extractions": [
                {
                    "category": "Menu Items",
                    "confidence": 1.5,  # Invalid
                    "extracted_data": {}
                }
            ]
        }
        
        response = LLMResponse(invalid_data, validate=True)
        assert len(response.extractions) == 0  # Should filter invalid

    def test_response_merging(self):
        """Test merging multiple LLM responses."""
        if not LLMResponse:
            pytest.skip("LLMResponse not implemented yet")
        
        response1_data = {
            "extractions": [
                {"category": "Menu Items", "confidence": 0.8, "extracted_data": {}}
            ]
        }
        
        response2_data = {
            "extractions": [
                {"category": "Services", "confidence": 0.9, "extracted_data": {}}
            ]
        }
        
        response1 = LLMResponse(response1_data)
        response2 = LLMResponse(response2_data)
        
        merged = response1.merge(response2)
        
        assert len(merged.extractions) == 2
        assert any(e["category"] == "Menu Items" for e in merged.extractions)
        assert any(e["category"] == "Services" for e in merged.extractions)