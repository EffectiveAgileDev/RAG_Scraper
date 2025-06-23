"""Configuration constants for RAG Integration Support."""

from typing import Dict, Any, List
from enum import Enum


class SchemaVersion(Enum):
    """Supported JSON Schema versions."""
    DRAFT_07 = "http://json-schema.org/draft-07/schema#"
    DRAFT_2019_09 = "https://json-schema.org/draft/2019-09/schema"


class RelationshipType(Enum):
    """Types of entity relationships."""
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    REFERENCE = "reference"


class ChunkingMethod(Enum):
    """Methods for content chunking."""
    SEMANTIC = "semantic"
    FIXED = "fixed"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


class PreservationStrategy(Enum):
    """Strategies for context preservation."""
    FULL = "full"
    SUMMARY = "summary"
    KEYWORDS = "keywords"
    HYBRID = "hybrid"


class AggregationMethod(Enum):
    """Methods for multi-page data aggregation."""
    HIERARCHICAL = "hierarchical"
    FLAT = "flat"
    GRAPH = "graph"
    HYBRID = "hybrid"


# Schema configuration
SCHEMA_CONFIG = {
    "version": SchemaVersion.DRAFT_07.value,
    "title": "Restaurant Data Schema",
    "description": "Schema for restaurant data extracted by RAG_Scraper with multi-page support"
}

# Field patterns
FIELD_PATTERNS = {
    "restaurant_id": r"^[a-zA-Z0-9_-]+$",
    "entity_id": r"^[a-zA-Z0-9_-]+$",
    "zip_code": r"^\d{5}(-\d{4})?$"
}

# Required fields
REQUIRED_FIELDS = [
    "restaurant_id",
    "restaurant_name",
    "cuisine_type",
    "extraction_timestamp",
    "source_url"
]

# Default chunk settings
DEFAULT_CHUNK_SETTINGS = {
    "max_chunk_size": 1000,
    "overlap_size": 100,
    "chunking_method": ChunkingMethod.SEMANTIC.value,
    "preserve_context": True
}

# Default embedding settings
DEFAULT_EMBEDDING_SETTINGS = {
    "keyword_extraction": True,
    "entity_recognition": True,
    "max_keywords": 10,
    "include_metadata": True
}

# Default context settings
DEFAULT_CONTEXT_SETTINGS = {
    "context_window": 2000,
    "preservation_strategy": PreservationStrategy.HYBRID.value,
    "include_parent_context": True
}

# Default multi-page settings
DEFAULT_MULTIPAGE_SETTINGS = {
    "relationship_depth": 2,
    "aggregation_method": AggregationMethod.HIERARCHICAL.value,
    "deduplication": True,
    "cross_reference_limit": 10
}

# Template directories
TEMPLATE_PATHS = {
    "typescript": "templates/typescript/",
    "python": "templates/python/",
    "documentation": "templates/docs/",
    "samples": "templates/samples/"
}

# File extensions
FILE_EXTENSIONS = {
    "typescript": ".d.ts",
    "python": ".py",
    "schema": ".schema.json",
    "documentation": ".md"
}

# Integration package structure
PACKAGE_STRUCTURE = {
    "schemas": ["restaurant_data.schema.json", "config.schema.json"],
    "types": {
        "typescript": ["index.d.ts"],
        "python": ["models.py", "models_pydantic.py"]
    },
    "docs": ["entity_relationships.md", "api_reference.md"],
    "examples": {
        "langchain": ["integration.py"],
        "llamaindex": ["integration.py"]
    },
    "tests": ["test_data.json", "validate_schema.py"]
}

# Validation rules
VALIDATION_RULES = {
    "max_chunk_size": {"min": 100, "max": 5000},
    "overlap_size": {"min": 0, "max": 500},
    "context_window": {"min": 500, "max": 10000},
    "relationship_depth": {"min": 1, "max": 5},
    "cross_reference_limit": {"min": 0, "max": 100}
}

# Framework configurations
FRAMEWORK_CONFIGS = {
    "langchain": {
        "imports": [
            "from langchain.document_loaders import TextLoader",
            "from langchain.text_splitter import RecursiveCharacterTextSplitter",
            "from langchain.embeddings import OpenAIEmbeddings",
            "from langchain.vectorstores import Chroma",
            "from langchain.chains import RetrievalQA",
            "from langchain.llms import OpenAI"
        ],
        "chunk_size": 1000,
        "chunk_overlap": 100,
        "search_type": "mmr"
    },
    "llamaindex": {
        "imports": [
            "from llama_index import Document, VectorStoreIndex, ServiceContext",
            "from llama_index.node_parser import SimpleNodeParser",
            "from llama_index.embeddings import OpenAIEmbedding",
            "from llama_index.llms import OpenAI"
        ],
        "chunk_size": 1000,
        "chunk_overlap": 100,
        "response_mode": "tree_summarize"
    }
}

# Error messages
ERROR_MESSAGES = {
    "invalid_chunk_size": "Chunk size must be between {min} and {max}",
    "invalid_overlap": "Overlap size must be between {min} and {max}",
    "invalid_relationship_depth": "Relationship depth must be between {min} and {max}",
    "missing_required_field": "Required field '{field}' is missing",
    "invalid_pattern": "Field '{field}' does not match required pattern",
    "generation_failed": "Failed to generate {artifact_type}: {error}"
}

# Version information
VERSION_INFO = {
    "package_version": "1.0.0",
    "schema_version": "1.0.0",
    "api_version": "v1",
    "min_python_version": "3.8",
    "supported_frameworks": ["langchain", "llamaindex"]
}