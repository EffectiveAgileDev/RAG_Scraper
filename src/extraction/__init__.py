"""Pluggable extraction pipeline system."""

from .pipeline import ExtractionPipeline, PipelineStage, ScrapingContext
from .stages import (
    RobotsTxtCheckStage,
    HtmlFetchStage,
    JavaScriptRenderStage,
    DataExtractionStage,
    AIExtractionStage
)
from .pipeline_factory import ExtractionPipelineFactory

__all__ = [
    "ExtractionPipeline",
    "PipelineStage", 
    "ScrapingContext",
    "RobotsTxtCheckStage",
    "HtmlFetchStage",
    "JavaScriptRenderStage", 
    "DataExtractionStage",
    "AIExtractionStage",
    "ExtractionPipelineFactory"
]