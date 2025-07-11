"""Factory for creating extraction pipelines with different configurations."""

from typing import List, Dict, Any, Optional
from .pipeline import ExtractionPipeline, PipelineStage
from .stages import (
    RobotsTxtCheckStage,
    HtmlFetchStage,
    JavaScriptRenderStage,
    DataExtractionStage,
    AIExtractionStage
)


class ExtractionPipelineFactory:
    """Factory class for creating extraction pipelines."""
    
    @staticmethod
    def create_standard_pipeline(config: Any = None) -> ExtractionPipeline:
        """Create a standard extraction pipeline with traditional methods.
        
        Args:
            config: Configuration object
            
        Returns:
            Configured ExtractionPipeline
        """
        stages = []
        
        # Robots.txt check stage
        respect_robots = getattr(config, 'respect_robots_txt', True)
        stages.append(RobotsTxtCheckStage(respect_robots=respect_robots))
        
        # HTML fetch stage
        timeout = getattr(config, 'timeout_per_page', 30)
        stages.append(HtmlFetchStage(timeout=timeout))
        
        # JavaScript rendering stage (conditional)
        js_enabled = False
        js_timeout = 30
        
        if hasattr(config, 'javascript'):
            js_enabled = config.javascript.enable_javascript_rendering
            js_timeout = config.javascript.javascript_timeout
        else:
            js_enabled = getattr(config, 'enable_javascript_rendering', False)
            js_timeout = getattr(config, 'javascript_timeout', 30)
        
        if js_enabled:
            stages.append(JavaScriptRenderStage(timeout=js_timeout))
        
        # Data extraction stage
        extraction_strategies = ["json_ld", "microdata", "heuristic"]
        if hasattr(config, 'schema') and hasattr(config.schema, 'extraction_strategies'):
            extraction_strategies = config.schema.extraction_strategies
        
        stages.append(DataExtractionStage(extraction_strategies=extraction_strategies))
        
        return ExtractionPipeline(stages)
    
    @staticmethod
    def create_ai_enabled_pipeline(config: Any = None) -> ExtractionPipeline:
        """Create an AI-enabled extraction pipeline.
        
        Args:
            config: Configuration object with AI settings
            
        Returns:
            Configured ExtractionPipeline with AI stage
        """
        stages = []
        
        # Robots.txt check stage
        respect_robots = getattr(config, 'respect_robots_txt', True)
        stages.append(RobotsTxtCheckStage(respect_robots=respect_robots))
        
        # HTML fetch stage
        timeout = getattr(config, 'timeout_per_page', 30)
        stages.append(HtmlFetchStage(timeout=timeout))
        
        # JavaScript rendering stage (conditional)
        js_enabled = False
        js_timeout = 30
        
        if hasattr(config, 'javascript'):
            js_enabled = config.javascript.enable_javascript_rendering
            js_timeout = config.javascript.javascript_timeout
        else:
            js_enabled = getattr(config, 'enable_javascript_rendering', False)
            js_timeout = getattr(config, 'javascript_timeout', 30)
        
        if js_enabled:
            stages.append(JavaScriptRenderStage(timeout=js_timeout))
        
        # AI extraction stage (first priority)
        ai_config = getattr(config, 'ai_extraction', None)
        fallback_enabled = True
        if ai_config:
            fallback_enabled = getattr(ai_config, 'ai_fallback_enabled', True)
        
        stages.append(AIExtractionStage(
            ai_config=ai_config.__dict__ if ai_config else {},
            fallback_enabled=fallback_enabled
        ))
        
        # Traditional extraction as fallback
        extraction_strategies = ["json_ld", "microdata", "heuristic"]
        if hasattr(config, 'schema') and hasattr(config.schema, 'extraction_strategies'):
            extraction_strategies = config.schema.extraction_strategies
        
        stages.append(DataExtractionStage(extraction_strategies=extraction_strategies))
        
        return ExtractionPipeline(stages)
    
    @staticmethod
    def create_minimal_pipeline() -> ExtractionPipeline:
        """Create a minimal pipeline for testing.
        
        Returns:
            Minimal ExtractionPipeline
        """
        stages = [
            HtmlFetchStage(timeout=10),
            DataExtractionStage(extraction_strategies=["heuristic"])
        ]
        return ExtractionPipeline(stages)
    
    @staticmethod
    def create_custom_pipeline(
        enable_robots_check: bool = True,
        enable_javascript: bool = False,
        enable_ai_extraction: bool = False,
        extraction_strategies: List[str] = None,
        timeouts: Dict[str, int] = None
    ) -> ExtractionPipeline:
        """Create a custom pipeline with specific configuration.
        
        Args:
            enable_robots_check: Whether to check robots.txt
            enable_javascript: Whether to enable JavaScript rendering
            enable_ai_extraction: Whether to enable AI extraction
            extraction_strategies: List of extraction strategies to use
            timeouts: Dictionary of timeout values
            
        Returns:
            Configured ExtractionPipeline
        """
        stages = []
        timeouts = timeouts or {}
        extraction_strategies = extraction_strategies or ["json_ld", "microdata", "heuristic"]
        
        # Robots.txt check
        if enable_robots_check:
            stages.append(RobotsTxtCheckStage(respect_robots=True))
        
        # HTML fetch
        html_timeout = timeouts.get('html_fetch', 30)
        stages.append(HtmlFetchStage(timeout=html_timeout))
        
        # JavaScript rendering
        if enable_javascript:
            js_timeout = timeouts.get('javascript_render', 30)
            stages.append(JavaScriptRenderStage(timeout=js_timeout))
        
        # AI extraction
        if enable_ai_extraction:
            stages.append(AIExtractionStage(fallback_enabled=True))
        
        # Traditional extraction
        stages.append(DataExtractionStage(extraction_strategies=extraction_strategies))
        
        return ExtractionPipeline(stages)
    
    @staticmethod
    def create_pipeline_from_config(config: Any) -> ExtractionPipeline:
        """Create pipeline based on configuration type.
        
        Args:
            config: Configuration object (legacy or unified)
            
        Returns:
            Appropriate ExtractionPipeline
        """
        # Check if this is a unified config with AI support
        if hasattr(config, 'ai_extraction') and config.is_ai_extraction_ready():
            return ExtractionPipelineFactory.create_ai_enabled_pipeline(config)
        else:
            return ExtractionPipelineFactory.create_standard_pipeline(config)
    
    @staticmethod
    def get_available_stages() -> Dict[str, str]:
        """Get information about available pipeline stages.
        
        Returns:
            Dictionary mapping stage names to descriptions
        """
        return {
            "robots_check": "Check robots.txt compliance before scraping",
            "html_fetch": "Fetch HTML content from URL",
            "javascript_render": "Render JavaScript content using browser automation",
            "data_extraction": "Extract data using traditional methods (JSON-LD, microdata, heuristics)",
            "ai_extraction": "Extract data using AI models (future implementation)"
        }
    
    @staticmethod
    def validate_stage_configuration(stages: List[str]) -> List[str]:
        """Validate stage configuration and return any errors.
        
        Args:
            stages: List of stage names to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        available_stages = ExtractionPipelineFactory.get_available_stages()
        errors = []
        
        for stage_name in stages:
            if stage_name not in available_stages:
                errors.append(f"Unknown stage: {stage_name}")
        
        # Check for required dependencies
        if "javascript_render" in stages and "html_fetch" not in stages:
            errors.append("javascript_render stage requires html_fetch stage")
        
        if "data_extraction" in stages and "html_fetch" not in stages:
            errors.append("data_extraction stage requires html_fetch stage")
        
        if "ai_extraction" in stages and "html_fetch" not in stages:
            errors.append("ai_extraction stage requires html_fetch stage")
        
        return errors