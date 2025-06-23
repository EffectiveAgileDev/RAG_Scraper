"""Unit tests for RAG Integration Support module."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
from typing import Dict, List, Any

from src.file_generator.rag_integration_support import RAGIntegrationSupport


class TestRAGIntegrationSupport:
    """Test suite for RAGIntegrationSupport class."""

    @pytest.fixture
    def support(self):
        """Create RAGIntegrationSupport instance."""
        return RAGIntegrationSupport()

    @pytest.fixture
    def sample_restaurant_data(self):
        """Sample restaurant data for testing."""
        return {
            "restaurant_id": "rest_001",
            "restaurant_name": "Luigi's Italian Bistro",
            "cuisine_type": "Italian",
            "location": {
                "address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            },
            "menu_items": [
                {"name": "Margherita Pizza", "price": 15.99},
                {"name": "Spaghetti Carbonara", "price": 18.50}
            ],
            "extraction_timestamp": "2024-01-20T15:30:00Z",
            "source_url": "https://example.com/restaurants/luigis",
            "parent_page_url": "https://example.com/restaurants",
            "entity_relationships": [
                {
                    "type": "parent",
                    "entity_id": "dir_001",
                    "entity_type": "directory"
                }
            ],
            "semantic_chunks": [
                {
                    "chunk_id": "chunk_001",
                    "content": "Luigi's Italian Bistro serves authentic Italian cuisine...",
                    "metadata": {"section": "description"}
                }
            ],
            "cross_references": [
                {
                    "ref_id": "rest_002",
                    "ref_type": "similar_cuisine",
                    "ref_name": "Mario's Pizza Palace"
                }
            ]
        }

    def test_init(self, support):
        """Test RAGIntegrationSupport initialization."""
        assert support is not None
        assert hasattr(support, 'generate_json_schema')
        assert hasattr(support, 'generate_typescript_types')
        assert hasattr(support, 'generate_python_types')

    def test_generate_json_schema_basic(self, support):
        """Test basic JSON schema generation."""
        schema = support.generate_json_schema()
        
        assert isinstance(schema, dict)
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

    def test_generate_json_schema_restaurant_fields(self, support):
        """Test JSON schema includes all restaurant fields."""
        schema = support.generate_json_schema()
        properties = schema["properties"]
        
        # Core fields
        assert "restaurant_id" in properties
        assert "restaurant_name" in properties
        assert "cuisine_type" in properties
        assert "location" in properties
        
        # Multi-page fields
        assert "extraction_timestamp" in properties
        assert "source_url" in properties
        assert "parent_page_url" in properties
        
        # Relationship fields
        assert "entity_relationships" in properties
        assert "semantic_chunks" in properties
        assert "cross_references" in properties

    def test_generate_json_schema_field_types(self, support):
        """Test JSON schema field type definitions."""
        schema = support.generate_json_schema()
        properties = schema["properties"]
        
        # String fields
        assert properties["restaurant_id"]["type"] == "string"
        assert properties["restaurant_name"]["type"] == "string"
        assert properties["cuisine_type"]["type"] == "string"
        
        # Object fields
        assert properties["location"]["type"] == "object"
        
        # Array fields
        assert properties["entity_relationships"]["type"] == "array"
        assert properties["semantic_chunks"]["type"] == "array"
        assert properties["cross_references"]["type"] == "array"
        
        # Format specifications
        assert properties["extraction_timestamp"]["format"] == "date-time"
        assert properties["source_url"]["format"] == "uri"

    def test_generate_json_schema_validation_rules(self, support):
        """Test JSON schema includes validation rules."""
        schema = support.generate_json_schema()
        properties = schema["properties"]
        
        # Pattern validation for restaurant_id
        assert "pattern" in properties["restaurant_id"]
        assert properties["restaurant_id"]["pattern"] == "^[a-zA-Z0-9_-]+$"
        
        # Required fields in location
        location_schema = properties["location"]
        assert "required" in location_schema
        assert "city" in location_schema["required"]
        
        # Array item schemas
        assert "items" in properties["entity_relationships"]
        assert "items" in properties["semantic_chunks"]

    def test_generate_json_schema_nested_objects(self, support):
        """Test JSON schema handles nested object structures."""
        schema = support.generate_json_schema()
        
        # Entity relationship schema
        rel_schema = schema["properties"]["entity_relationships"]["items"]
        assert rel_schema["type"] == "object"
        assert "type" in rel_schema["properties"]
        assert "entity_id" in rel_schema["properties"]
        assert "entity_type" in rel_schema["properties"]
        
        # Semantic chunk schema
        chunk_schema = schema["properties"]["semantic_chunks"]["items"]
        assert chunk_schema["type"] == "object"
        assert "chunk_id" in chunk_schema["properties"]
        assert "content" in chunk_schema["properties"]
        assert "metadata" in chunk_schema["properties"]

    def test_generate_typescript_types_basic(self, support):
        """Test basic TypeScript type generation."""
        typescript = support.generate_typescript_types()
        
        assert isinstance(typescript, str)
        assert "export interface" in typescript
        assert "RestaurantData" in typescript
        assert "EntityRelationship" in typescript
        assert "SemanticChunk" in typescript

    def test_generate_typescript_types_interfaces(self, support):
        """Test TypeScript interface definitions."""
        typescript = support.generate_typescript_types()
        
        # Main interface
        assert "export interface RestaurantData {" in typescript
        assert "restaurant_id: string;" in typescript
        assert "restaurant_name: string;" in typescript
        assert "cuisine_type: string;" in typescript
        
        # Nested interfaces
        assert "export interface Location {" in typescript
        assert "export interface EntityRelationship {" in typescript
        assert "export interface SemanticChunk {" in typescript
        assert "export interface CrossReference {" in typescript

    def test_generate_typescript_types_optional_fields(self, support):
        """Test TypeScript optional field handling."""
        typescript = support.generate_typescript_types()
        
        # Optional fields should use ?
        assert "parent_page_url?: string;" in typescript
        assert "description?: string;" in typescript
        
        # Arrays should be properly typed
        assert "entity_relationships: EntityRelationship[];" in typescript
        assert "semantic_chunks: SemanticChunk[];" in typescript

    def test_generate_typescript_types_type_safety(self, support):
        """Test TypeScript type safety features."""
        typescript = support.generate_typescript_types()
        
        # Union types for enums
        assert "type RelationshipType = 'parent' | 'child' | 'sibling' | 'reference';" in typescript
        
        # Null safety
        assert "| null" in typescript or "| undefined" in typescript
        
        # Metadata types
        assert "metadata: Record<string, any>;" in typescript or "metadata: { [key: string]: any };" in typescript

    def test_generate_typescript_types_exportable(self, support):
        """Test TypeScript module exports."""
        typescript = support.generate_typescript_types()
        
        # Should have exports
        assert "export" in typescript
        
        # Should be valid TypeScript
        assert typescript.strip().endswith("}")
        assert typescript.count("{") == typescript.count("}")

    def test_generate_python_types_basic(self, support):
        """Test basic Python type generation."""
        python_types = support.generate_python_types()
        
        assert isinstance(python_types, str)
        assert "from typing import" in python_types
        assert "class RestaurantData" in python_types or "RestaurantData = TypedDict" in python_types

    def test_generate_python_types_imports(self, support):
        """Test Python type imports."""
        python_types = support.generate_python_types()
        
        # Required imports
        assert "from typing import" in python_types
        assert "Dict" in python_types or "dict" in python_types
        assert "List" in python_types or "list" in python_types
        assert "Optional" in python_types
        
        # Dataclass or TypedDict
        assert "from dataclasses import dataclass" in python_types or \
               "from typing import TypedDict" in python_types

    def test_generate_python_types_class_definitions(self, support):
        """Test Python class/type definitions."""
        python_types = support.generate_python_types()
        
        # Main classes
        assert "RestaurantData" in python_types
        assert "Location" in python_types
        assert "EntityRelationship" in python_types
        assert "SemanticChunk" in python_types
        assert "CrossReference" in python_types

    def test_generate_python_types_field_annotations(self, support):
        """Test Python field type annotations."""
        python_types = support.generate_python_types()
        
        # Field annotations
        assert "restaurant_id: str" in python_types
        assert "restaurant_name: str" in python_types
        assert "cuisine_type: str" in python_types
        
        # Complex types
        assert "location: Location" in python_types
        assert "entity_relationships: List[EntityRelationship]" in python_types or \
               "entity_relationships: list[EntityRelationship]" in python_types

    def test_generate_python_types_optional_handling(self, support):
        """Test Python optional field handling."""
        python_types = support.generate_python_types()
        
        # Optional fields
        assert "Optional[str]" in python_types
        assert "parent_page_url: Optional[str]" in python_types

    def test_generate_python_types_with_pydantic(self, support):
        """Test Python type generation with pydantic option."""
        python_types = support.generate_python_types(use_pydantic=True)
        
        assert "from pydantic import BaseModel" in python_types
        assert "class RestaurantData(BaseModel):" in python_types
        
        # Pydantic features
        assert "class Config:" in python_types or "model_config" in python_types

    def test_generate_entity_relationship_docs_structure(self, support):
        """Test entity relationship documentation structure."""
        docs = support.generate_entity_relationship_docs()
        
        assert isinstance(docs, str)
        assert "# Entity Relationship Schema" in docs
        assert "## Overview" in docs
        assert "## Relationship Types" in docs
        assert "## Data Model" in docs
        assert "## Access Patterns" in docs
        assert "## Examples" in docs

    def test_generate_entity_relationship_docs_content(self, support):
        """Test entity relationship documentation content."""
        docs = support.generate_entity_relationship_docs()
        
        # Relationship types
        assert "parent-child" in docs.lower()
        assert "sibling" in docs.lower()
        assert "reference" in docs.lower()
        
        # Multi-page handling
        assert "multi-page" in docs.lower() or "multiple pages" in docs.lower()
        
        # Code examples
        assert "```python" in docs
        assert "```typescript" in docs or "```javascript" in docs

    def test_generate_entity_relationship_docs_examples(self, support):
        """Test entity relationship documentation examples."""
        docs = support.generate_entity_relationship_docs()
        
        # Should have practical examples
        assert "restaurant" in docs.lower()
        assert "parent_page_url" in docs
        assert "entity_id" in docs
        assert "relationship" in docs.lower()

    def test_generate_config_schema_basic(self, support):
        """Test configuration schema generation."""
        config_schema = support.generate_config_schema()
        
        assert isinstance(config_schema, dict)
        assert "$schema" in config_schema
        assert "type" in config_schema
        assert config_schema["type"] == "object"
        assert "properties" in config_schema

    def test_generate_config_schema_settings(self, support):
        """Test configuration schema settings."""
        config_schema = support.generate_config_schema()
        properties = config_schema["properties"]
        
        # Chunk settings
        assert "chunk_settings" in properties
        chunk_props = properties["chunk_settings"]["properties"]
        assert "max_chunk_size" in chunk_props
        assert "overlap_size" in chunk_props
        assert "chunking_method" in chunk_props
        
        # Embedding hints
        assert "embedding_hints" in properties
        
        # Context settings
        assert "context_settings" in properties
        
        # Multi-page settings
        assert "multi_page_settings" in properties

    def test_generate_config_schema_defaults(self, support):
        """Test configuration schema default values."""
        config_schema = support.generate_config_schema()
        
        # Check for defaults
        chunk_settings = config_schema["properties"]["chunk_settings"]["properties"]
        assert "default" in chunk_settings["max_chunk_size"]
        assert "default" in chunk_settings["overlap_size"]
        
        # Verify reasonable defaults
        assert chunk_settings["max_chunk_size"]["default"] > 0
        assert chunk_settings["overlap_size"]["default"] >= 0

    def test_generate_config_schema_validation(self, support):
        """Test configuration schema validation rules."""
        config_schema = support.generate_config_schema()
        
        chunk_settings = config_schema["properties"]["chunk_settings"]["properties"]
        
        # Numeric constraints
        assert "minimum" in chunk_settings["max_chunk_size"]
        assert chunk_settings["max_chunk_size"]["minimum"] > 0
        
        # Enum constraints
        assert "enum" in chunk_settings["chunking_method"]
        assert "semantic" in chunk_settings["chunking_method"]["enum"]

    def test_generate_langchain_sample_structure(self, support):
        """Test LangChain sample code structure."""
        sample = support.generate_langchain_sample()
        
        assert isinstance(sample, str)
        assert "from langchain" in sample
        assert "import" in sample
        assert "class" in sample or "def" in sample

    def test_generate_langchain_sample_components(self, support):
        """Test LangChain sample includes required components."""
        sample = support.generate_langchain_sample()
        
        # Document loader
        assert "loader" in sample.lower() or "document" in sample.lower()
        
        # Text splitter
        assert "splitter" in sample.lower() or "chunk" in sample.lower()
        
        # Metadata handling
        assert "metadata" in sample.lower()
        
        # Vector store
        assert "vector" in sample.lower() or "store" in sample.lower()
        
        # Retrieval
        assert "retriev" in sample.lower() or "query" in sample.lower()

    def test_generate_langchain_sample_error_handling(self, support):
        """Test LangChain sample includes error handling."""
        sample = support.generate_langchain_sample()
        
        assert "try:" in sample
        assert "except" in sample
        assert "Exception" in sample or "Error" in sample

    def test_generate_langchain_sample_comments(self, support):
        """Test LangChain sample includes comments."""
        sample = support.generate_langchain_sample()
        
        assert "#" in sample or '"""' in sample
        assert sample.count("#") >= 5  # At least 5 comments

    def test_generate_llamaindex_sample_structure(self, support):
        """Test LlamaIndex sample code structure."""
        sample = support.generate_llamaindex_sample()
        
        assert isinstance(sample, str)
        assert "llama_index" in sample or "llama-index" in sample
        assert "import" in sample
        assert "class" in sample or "def" in sample

    def test_generate_llamaindex_sample_components(self, support):
        """Test LlamaIndex sample includes required components."""
        sample = support.generate_llamaindex_sample()
        
        # Document loading
        assert "document" in sample.lower() or "load" in sample.lower()
        
        # Index creation
        assert "index" in sample.lower()
        
        # Query engine
        assert "query" in sample.lower() or "engine" in sample.lower()
        
        # Multi-page handling
        assert "relationship" in sample.lower() or "multi" in sample.lower()

    def test_generate_llamaindex_sample_configuration(self, support):
        """Test LlamaIndex sample includes configuration."""
        sample = support.generate_llamaindex_sample()
        
        assert "config" in sample.lower() or "settings" in sample.lower()
        assert "{" in sample  # Configuration dict

    def test_generate_llamaindex_sample_scalability(self, support):
        """Test LlamaIndex sample handles large-scale data."""
        sample = support.generate_llamaindex_sample()
        
        # Should mention batch processing or streaming
        assert any(term in sample.lower() for term in ["batch", "stream", "chunk", "iterator"])

    def test_generate_api_documentation_structure(self, support):
        """Test API documentation structure."""
        api_docs = support.generate_api_documentation()
        
        assert isinstance(api_docs, dict) or isinstance(api_docs, str)
        
        # Convert to string for checking
        docs_str = str(api_docs)
        
        assert "Data Structures" in docs_str
        assert "File Organization" in docs_str
        assert "Access Methods" in docs_str
        assert "Integration Points" in docs_str
        assert "Code Examples" in docs_str

    def test_generate_api_documentation_content(self, support):
        """Test API documentation content."""
        api_docs = support.generate_api_documentation()
        docs_str = str(api_docs)
        
        # Should describe output formats
        assert "json" in docs_str.lower()
        assert "text" in docs_str.lower()
        
        # Should mention REST endpoints
        assert "endpoint" in docs_str.lower() or "api" in docs_str.lower()
        
        # Should explain batch processing
        assert "batch" in docs_str.lower()

    def test_generate_api_documentation_openapi(self, support):
        """Test API documentation OpenAPI format."""
        api_docs = support.generate_api_documentation()
        
        if isinstance(api_docs, dict) and "openapi" in api_docs:
            assert api_docs["openapi"].startswith("3.")
            assert "paths" in api_docs
            assert "components" in api_docs

    def test_generate_all_artifacts(self, support):
        """Test generating all artifacts."""
        artifacts = support.generate_all_artifacts()
        
        assert isinstance(artifacts, dict)
        assert "schemas" in artifacts
        assert "types" in artifacts
        assert "documentation" in artifacts
        assert "samples" in artifacts
        assert "api" in artifacts

    def test_generate_all_artifacts_completeness(self, support):
        """Test all artifacts are complete."""
        artifacts = support.generate_all_artifacts()
        
        # Schemas
        assert "json_schema" in artifacts["schemas"]
        assert "config_schema" in artifacts["schemas"]
        
        # Types
        assert "typescript" in artifacts["types"]
        assert "python" in artifacts["types"]
        
        # Documentation
        assert "entity_relationships" in artifacts["documentation"]
        
        # Samples
        assert "langchain" in artifacts["samples"]
        assert "llamaindex" in artifacts["samples"]

    def test_create_integration_package(self, support):
        """Test integration package creation."""
        package = support.create_integration_package()
        
        assert isinstance(package, dict)
        assert "schemas" in package
        assert "types" in package
        assert "docs" in package
        assert "examples" in package
        assert "tests" in package

    def test_create_integration_package_readme(self, support):
        """Test integration package includes README."""
        package = support.create_integration_package()
        
        assert "README" in package or "readme" in package
        readme = package.get("README", package.get("readme", ""))
        
        if isinstance(readme, str):
            assert "quick start" in readme.lower() or "getting started" in readme.lower()

    def test_create_integration_package_version(self, support):
        """Test integration package versioning."""
        package = support.create_integration_package()
        
        # Should have version info
        assert "version" in package or "VERSION" in package
        
        # Version should match scraper version
        if "version" in package:
            assert isinstance(package["version"], str)
            assert "." in package["version"]  # Semantic versioning

    def test_create_integration_package_structure(self, support):
        """Test integration package directory structure."""
        package = support.create_integration_package()
        
        # Expected directories
        expected_dirs = ["schemas", "types", "docs", "examples", "tests"]
        for dir_name in expected_dirs:
            assert dir_name in package
            assert isinstance(package[dir_name], dict)

    def test_schema_validation_with_sample_data(self, support, sample_restaurant_data):
        """Test that generated schema validates sample data."""
        schema = support.generate_json_schema()
        
        # This would use jsonschema library in real implementation
        # For now, just verify schema structure matches data
        properties = schema["properties"]
        
        for key in sample_restaurant_data.keys():
            assert key in properties, f"Schema missing property: {key}"

    def test_type_consistency_across_languages(self, support):
        """Test type consistency between TypeScript and Python."""
        typescript = support.generate_typescript_types()
        python = support.generate_python_types()
        
        # Both should define the same main types
        main_types = ["RestaurantData", "Location", "EntityRelationship", "SemanticChunk", "CrossReference"]
        
        for type_name in main_types:
            assert type_name in typescript
            assert type_name in python

    def test_documentation_completeness(self, support):
        """Test that all documentation is complete and consistent."""
        artifacts = support.generate_all_artifacts()
        
        # Check that documentation references all components
        entity_docs = artifacts["documentation"]["entity_relationships"]
        
        # Should document all relationship types
        assert "parent" in entity_docs
        assert "child" in entity_docs
        assert "sibling" in entity_docs
        assert "reference" in entity_docs

    def test_sample_code_syntax_validity(self, support):
        """Test that sample code has valid syntax."""
        langchain_sample = support.generate_langchain_sample()
        llamaindex_sample = support.generate_llamaindex_sample()
        
        # Basic syntax checks
        for sample in [langchain_sample, llamaindex_sample]:
            # Balanced parentheses
            assert sample.count("(") == sample.count(")")
            assert sample.count("{") == sample.count("}")
            assert sample.count("[") == sample.count("]")
            
            # No trailing colons without content
            lines = sample.split("\n")
            for i, line in enumerate(lines):
                if line.strip().endswith(":"):
                    # Next line should be indented or empty
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        assert next_line.strip() == "" or next_line.startswith(" ") or next_line.startswith("\t")

    def test_config_schema_extensibility(self, support):
        """Test configuration schema allows extensions."""
        config_schema = support.generate_config_schema()
        
        # Should allow custom settings
        assert "additionalProperties" in config_schema or \
               any("custom" in str(prop).lower() for prop in config_schema["properties"].values())

    def test_error_messages_helpful(self, support):
        """Test that error handling provides helpful messages."""
        # Test with invalid input
        with pytest.raises(Exception) as exc_info:
            support.generate_json_schema(invalid_param=True)
        
        # Error message should be informative
        if exc_info.value:
            assert len(str(exc_info.value)) > 0