"""Standard extraction pipeline stages."""

from typing import Optional, Dict, Any
from .pipeline import PipelineStage, PipelineResult, ScrapingContext


class RobotsTxtCheckStage(PipelineStage):
    """Check robots.txt compliance before scraping."""
    
    def __init__(self, respect_robots: bool = True):
        super().__init__("robots_check")
        self.respect_robots = respect_robots
    
    def process(self, context: ScrapingContext) -> PipelineResult:
        """Check robots.txt compliance."""
        if not self.respect_robots:
            context.robots_txt_allowed = True
            return PipelineResult.CONTINUE
        
        try:
            # Import here to avoid circular dependencies
            from ..scraper.robots_checker import RobotsChecker
            
            checker = RobotsChecker()
            is_allowed = checker.can_fetch(context.url)
            context.robots_txt_allowed = is_allowed
            
            if not is_allowed:
                context.stop_with_failure("Blocked by robots.txt", self.name)
                return PipelineResult.STOP_FAILURE
            
            return PipelineResult.CONTINUE
            
        except Exception as e:
            # If robots.txt check fails, allow scraping but warn
            context.add_warning(f"Robots.txt check failed: {str(e)}", self.name)
            context.robots_txt_allowed = True
            return PipelineResult.CONTINUE
    
    def is_enabled(self, context: ScrapingContext) -> bool:
        """Only run if robots.txt compliance is required."""
        return self.respect_robots and getattr(context.config, 'respect_robots_txt', True)


class HtmlFetchStage(PipelineStage):
    """Fetch HTML content from URL."""
    
    def __init__(self, timeout: int = 30):
        super().__init__("html_fetch")
        self.timeout = timeout
    
    def process(self, context: ScrapingContext) -> PipelineResult:
        """Fetch HTML content."""
        try:
            # Import here to avoid circular dependencies
            from ..scraper.html_fetcher import HTMLFetcher
            
            fetcher = HTMLFetcher(timeout=self.timeout)
            html_content = fetcher.fetch(context.url)
            
            if not html_content:
                context.stop_with_failure("Failed to fetch HTML content", self.name)
                return PipelineResult.STOP_FAILURE
            
            context.html_content = html_content
            return PipelineResult.CONTINUE
            
        except Exception as e:
            return self.on_error(context, e)
    
    def get_dependencies(self) -> list:
        """Depends on robots.txt check."""
        return ["robots_check"]


class JavaScriptRenderStage(PipelineStage):
    """Render JavaScript if enabled."""
    
    def __init__(self, timeout: int = 30):
        super().__init__("javascript_render")
        self.timeout = timeout
    
    def process(self, context: ScrapingContext) -> PipelineResult:
        """Render JavaScript content."""
        try:
            # Import here to avoid circular dependencies
            from ..scraper.javascript_renderer import JavaScriptRenderer
            
            renderer = JavaScriptRenderer(timeout=self.timeout)
            rendered_content = renderer.render(context.url, context.html_content)
            
            if rendered_content:
                context.rendered_content = rendered_content
                context.javascript_rendered = True
            else:
                # Use original HTML if rendering fails
                context.rendered_content = context.html_content
                context.add_warning("JavaScript rendering failed, using static HTML", self.name)
            
            return PipelineResult.CONTINUE
            
        except Exception as e:
            # Non-critical failure - continue with static HTML
            context.rendered_content = context.html_content
            context.add_warning(f"JavaScript rendering error: {str(e)}", self.name)
            return PipelineResult.CONTINUE
    
    def is_enabled(self, context: ScrapingContext) -> bool:
        """Only run if JavaScript rendering is enabled."""
        if hasattr(context.config, 'javascript'):
            return context.config.javascript.enable_javascript_rendering
        return getattr(context.config, 'enable_javascript_rendering', False)
    
    def get_dependencies(self) -> list:
        """Depends on HTML fetch."""
        return ["html_fetch"]


class DataExtractionStage(PipelineStage):
    """Extract data using traditional methods (JSON-LD, microdata, heuristics)."""
    
    def __init__(self, extraction_strategies: list = None):
        super().__init__("data_extraction")
        self.extraction_strategies = extraction_strategies or ["json_ld", "microdata", "heuristic"]
    
    def process(self, context: ScrapingContext) -> PipelineResult:
        """Extract data using configured strategies."""
        try:
            # Import here to avoid circular dependencies
            from ..scraper.multi_strategy_scraper import MultiStrategyScraper
            
            scraper = MultiStrategyScraper()
            
            # Use rendered content if available, otherwise use static HTML
            content = context.rendered_content or context.html_content
            
            # Extract using each strategy
            for strategy in self.extraction_strategies:
                try:
                    if strategy == "json_ld":
                        result = scraper.json_ld_extractor.extract_restaurant_data(content)
                        if result:
                            context.extraction_results["json_ld"] = result
                    elif strategy == "microdata":
                        result = scraper.microdata_extractor.extract_restaurant_data(content)
                        if result:
                            context.extraction_results["microdata"] = result
                    elif strategy == "heuristic":
                        result = scraper.heuristic_extractor.extract_restaurant_data(content)
                        if result:
                            context.extraction_results["heuristic"] = result
                            
                except Exception as e:
                    context.add_warning(f"Strategy {strategy} failed: {str(e)}", self.name)
            
            # Merge results
            if context.extraction_results:
                merged_result = scraper._merge_extraction_results(
                    context.extraction_results.get("json_ld"),
                    context.extraction_results.get("microdata"),
                    context.extraction_results.get("heuristic")
                )
                context.final_result = merged_result
                return PipelineResult.STOP_SUCCESS
            else:
                context.stop_with_failure("No data extracted by any strategy", self.name)
                return PipelineResult.STOP_FAILURE
                
        except Exception as e:
            return self.on_error(context, e)
    
    def get_dependencies(self) -> list:
        """Depends on HTML content (and optionally JavaScript rendering)."""
        return ["html_fetch"]


class AIExtractionStage(PipelineStage):
    """AI-powered data extraction stage (prepared for future implementation)."""
    
    def __init__(self, ai_config: Dict[str, Any] = None, fallback_enabled: bool = True):
        super().__init__("ai_extraction")
        self.ai_config = ai_config or {}
        self.fallback_enabled = fallback_enabled
    
    def process(self, context: ScrapingContext) -> PipelineResult:
        """Extract data using AI models."""
        try:
            # Check if AI extraction is enabled
            ai_config = getattr(context.config, 'ai_extraction', None)
            if not ai_config or not getattr(ai_config, 'enable_ai_extraction', False):
                return PipelineResult.CONTINUE
            
            # AI extraction logic will be implemented here
            # For now, this is a placeholder that demonstrates the architecture
            
            context.add_warning("AI extraction not yet implemented", self.name)
            
            # If fallback is enabled, continue to traditional extraction
            if self.fallback_enabled:
                return PipelineResult.CONTINUE
            else:
                context.stop_with_failure("AI extraction failed and fallback disabled", self.name)
                return PipelineResult.STOP_FAILURE
                
        except Exception as e:
            if self.fallback_enabled:
                context.add_warning(f"AI extraction error, using fallback: {str(e)}", self.name)
                return PipelineResult.CONTINUE
            else:
                return self.on_error(context, e)
    
    def is_enabled(self, context: ScrapingContext) -> bool:
        """Only run if AI extraction is configured."""
        ai_config = getattr(context.config, 'ai_extraction', None)
        return ai_config and getattr(ai_config, 'enable_ai_extraction', False)
    
    def get_dependencies(self) -> list:
        """Depends on HTML content."""
        return ["html_fetch"]
    
    def _extract_with_ai_model(self, content: str, extraction_type: str = "restaurant") -> Optional[Dict[str, Any]]:
        """Extract data using AI model (placeholder for future implementation).
        
        Args:
            content: HTML content to extract from
            extraction_type: Type of extraction to perform
            
        Returns:
            Extracted data dictionary or None if extraction fails
        """
        # This will be implemented when AI integration is added
        # Will use models like OpenAI GPT, Claude, or local models
        # to extract structured restaurant data from HTML content
        
        # Example structure for future implementation:
        # 1. Prepare prompt based on extraction_type
        # 2. Send content + prompt to AI model
        # 3. Parse AI response into structured data
        # 4. Validate and clean extracted data
        # 5. Return structured result
        
        return None