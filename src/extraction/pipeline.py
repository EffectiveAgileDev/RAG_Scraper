"""Core extraction pipeline architecture."""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
from enum import Enum


class PipelineResult(Enum):
    """Results that can be returned by pipeline stages."""
    CONTINUE = "continue"
    STOP_SUCCESS = "stop_success"
    STOP_FAILURE = "stop_failure"
    RETRY = "retry"


@dataclass
class ScrapingContext:
    """Context object passed through the extraction pipeline."""
    
    # Input data
    url: str
    config: Any = None  # ScrapingConfig or UnifiedScrapingConfig
    
    # Processing state
    html_content: str = ""
    rendered_content: str = ""
    robots_txt_allowed: bool = True
    javascript_rendered: bool = False
    
    # Extraction results
    extraction_results: Dict[str, Any] = field(default_factory=dict)
    final_result: Any = None
    
    # Control flags
    should_stop: bool = False
    should_retry: bool = False
    retry_count: int = 0
    max_retries: int = 3
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Performance tracking
    processing_time: float = 0.0
    stage_times: Dict[str, float] = field(default_factory=dict)
    
    def add_error(self, error: str, stage_name: str = "unknown") -> None:
        """Add an error to the context."""
        self.errors.append(f"[{stage_name}] {error}")
    
    def add_warning(self, warning: str, stage_name: str = "unknown") -> None:
        """Add a warning to the context."""
        self.warnings.append(f"[{stage_name}] {warning}")
    
    def has_errors(self) -> bool:
        """Check if context has any errors."""
        return len(self.errors) > 0
    
    def can_retry(self) -> bool:
        """Check if retry is possible."""
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment retry counter."""
        self.retry_count += 1
        self.should_retry = False
    
    def stop_with_success(self) -> None:
        """Mark pipeline to stop with success."""
        self.should_stop = True
    
    def stop_with_failure(self, error: str, stage_name: str = "unknown") -> None:
        """Mark pipeline to stop with failure."""
        self.should_stop = True
        self.add_error(error, stage_name)
    
    def request_retry(self) -> None:
        """Request a retry if possible."""
        if self.can_retry():
            self.should_retry = True
        else:
            self.stop_with_failure("Maximum retries exceeded")


class PipelineStage(ABC):
    """Abstract base class for extraction pipeline stages."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.enabled = True
    
    @abstractmethod
    def process(self, context: ScrapingContext) -> PipelineResult:
        """Process the scraping context.
        
        Args:
            context: The scraping context to process
            
        Returns:
            PipelineResult indicating how to proceed
        """
        pass
    
    def is_enabled(self, context: ScrapingContext) -> bool:
        """Check if this stage should be executed."""
        return self.enabled
    
    def on_error(self, context: ScrapingContext, error: Exception) -> PipelineResult:
        """Handle errors during stage processing.
        
        Args:
            context: The scraping context
            error: The exception that occurred
            
        Returns:
            PipelineResult indicating how to proceed
        """
        context.add_error(str(error), self.name)
        return PipelineResult.STOP_FAILURE
    
    def get_dependencies(self) -> List[str]:
        """Get list of stage names this stage depends on."""
        return []
    
    def cleanup(self, context: ScrapingContext) -> None:
        """Cleanup resources after stage processing."""
        pass


class ExtractionPipeline:
    """Main extraction pipeline that orchestrates processing stages."""
    
    def __init__(self, stages: List[PipelineStage] = None):
        self.stages = stages or []
        self._stage_lookup = {stage.name: stage for stage in self.stages}
    
    def add_stage(self, stage: PipelineStage, position: int = None) -> None:
        """Add a stage to the pipeline.
        
        Args:
            stage: The stage to add
            position: Position to insert stage (None = append)
        """
        if position is None:
            self.stages.append(stage)
        else:
            self.stages.insert(position, stage)
        
        self._stage_lookup[stage.name] = stage
    
    def remove_stage(self, stage_name: str) -> bool:
        """Remove a stage from the pipeline.
        
        Args:
            stage_name: Name of stage to remove
            
        Returns:
            True if stage was removed, False if not found
        """
        if stage_name in self._stage_lookup:
            stage = self._stage_lookup[stage_name]
            self.stages.remove(stage)
            del self._stage_lookup[stage_name]
            return True
        return False
    
    def get_stage(self, stage_name: str) -> Optional[PipelineStage]:
        """Get a stage by name."""
        return self._stage_lookup.get(stage_name)
    
    def process(self, url: str, config: Any = None) -> ScrapingContext:
        """Process a URL through the extraction pipeline.
        
        Args:
            url: URL to process
            config: Configuration object
            
        Returns:
            ScrapingContext with results
        """
        import time
        
        # Create initial context
        context = ScrapingContext(url=url, config=config)
        start_time = time.time()
        
        try:
            # Process through each stage
            for stage in self.stages:
                if not stage.is_enabled(context):
                    continue
                
                # Check if we should stop
                if context.should_stop:
                    break
                
                # Record stage timing
                stage_start = time.time()
                
                try:
                    # Process stage
                    result = stage.process(context)
                    
                    # Record timing
                    stage_duration = time.time() - stage_start
                    context.stage_times[stage.name] = stage_duration
                    
                    # Handle stage result
                    if result == PipelineResult.STOP_SUCCESS:
                        context.stop_with_success()
                        break
                    elif result == PipelineResult.STOP_FAILURE:
                        context.stop_with_failure(f"Stage {stage.name} failed")
                        break
                    elif result == PipelineResult.RETRY:
                        context.request_retry()
                        if context.should_retry:
                            # Restart pipeline from beginning
                            context.increment_retry()
                            return self.process(url, config)
                        break
                    # CONTINUE - proceed to next stage
                    
                except Exception as e:
                    # Handle stage error
                    stage_duration = time.time() - stage_start
                    context.stage_times[stage.name] = stage_duration
                    
                    error_result = stage.on_error(context, e)
                    if error_result == PipelineResult.STOP_FAILURE:
                        context.stop_with_failure(f"Stage {stage.name} error: {str(e)}")
                        break
                    elif error_result == PipelineResult.RETRY:
                        context.request_retry()
                        if context.should_retry:
                            context.increment_retry()
                            return self.process(url, config)
                        break
                    # Continue processing other stages
                
                finally:
                    # Cleanup stage resources
                    try:
                        stage.cleanup(context)
                    except Exception:
                        pass  # Don't fail pipeline on cleanup errors
        
        finally:
            # Record total processing time
            context.processing_time = time.time() - start_time
        
        return context
    
    def validate_dependencies(self) -> List[str]:
        """Validate that all stage dependencies are met.
        
        Returns:
            List of dependency errors (empty if valid)
        """
        errors = []
        stage_names = {stage.name for stage in self.stages}
        
        for stage in self.stages:
            for dependency in stage.get_dependencies():
                if dependency not in stage_names:
                    errors.append(f"Stage '{stage.name}' depends on missing stage '{dependency}'")
        
        return errors
    
    def get_stage_info(self) -> Dict[str, Any]:
        """Get information about pipeline stages."""
        return {
            "total_stages": len(self.stages),
            "enabled_stages": len([s for s in self.stages if s.enabled]),
            "stage_names": [s.name for s in self.stages],
            "dependencies": {s.name: s.get_dependencies() for s in self.stages}
        }