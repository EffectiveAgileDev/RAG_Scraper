"""RAG Integration Support module for generating schemas and integration artifacts."""

from typing import Dict, Any
from .rag_integration_support_refactored import (
    RAGIntegrationSupport as RefactoredRAGIntegrationSupport,
    GenerationConfig,
    GenerationResult,
    RAGIntegrationError
)

# For backward compatibility, expose the refactored class as the main class
class RAGIntegrationSupport(RefactoredRAGIntegrationSupport):
    """Generates schemas, type definitions, and integration support for RAG systems."""

    def __init__(self):
        """Initialize RAG Integration Support."""
        config = GenerationConfig(version="1.0.0")
        super().__init__(config)


# Export public classes for easier imports
__all__ = [
    'RAGIntegrationSupport',
    'GenerationConfig', 
    'GenerationResult',
    'RAGIntegrationError'
]