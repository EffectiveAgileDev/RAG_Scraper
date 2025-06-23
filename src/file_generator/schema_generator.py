"""Schema generation for RAG Integration Support."""

from typing import Dict, Any, List, Optional
import json
from abc import ABC, abstractmethod

from .integration_config import (
    SCHEMA_CONFIG, FIELD_PATTERNS, REQUIRED_FIELDS, RelationshipType,
    ChunkingMethod, PreservationStrategy, AggregationMethod,
    DEFAULT_CHUNK_SETTINGS, DEFAULT_EMBEDDING_SETTINGS,
    DEFAULT_CONTEXT_SETTINGS, DEFAULT_MULTIPAGE_SETTINGS,
    VALIDATION_RULES, ERROR_MESSAGES
)


class BaseSchemaGenerator(ABC):
    """Base class for schema generators."""
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate generator configuration."""
        if not self.version:
            raise ValueError("Version must be specified")
    
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """Generate schema."""
        pass
    
    def _create_string_field(
        self, 
        description: str, 
        pattern: Optional[str] = None,
        format_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a string field definition."""
        field = {
            "type": "string",
            "description": description
        }
        if pattern:
            field["pattern"] = pattern
        if format_type:
            field["format"] = format_type
        return field
    
    def _create_object_field(
        self, 
        description: str, 
        properties: Dict[str, Any],
        required: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create an object field definition."""
        field = {
            "type": "object",
            "description": description,
            "properties": properties
        }
        if required:
            field["required"] = required
        return field
    
    def _create_array_field(
        self, 
        description: str, 
        items: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an array field definition."""
        return {
            "type": "array",
            "description": description,
            "items": items
        }


class RestaurantDataSchemaGenerator(BaseSchemaGenerator):
    """Generator for restaurant data JSON Schema."""
    
    def generate(self) -> Dict[str, Any]:
        """Generate JSON Schema for restaurant data."""
        return {
            "$schema": SCHEMA_CONFIG["version"],
            "title": SCHEMA_CONFIG["title"],
            "description": SCHEMA_CONFIG["description"],
            "type": "object",
            "properties": self._create_properties(),
            "required": REQUIRED_FIELDS,
            "additionalProperties": True
        }
    
    def _create_properties(self) -> Dict[str, Any]:
        """Create all property definitions."""
        return {
            "restaurant_id": self._create_string_field(
                "Unique identifier for the restaurant",
                FIELD_PATTERNS["restaurant_id"]
            ),
            "restaurant_name": self._create_string_field(
                "Name of the restaurant"
            ),
            "cuisine_type": self._create_string_field(
                "Type of cuisine served"
            ),
            "location": self._create_location_field(),
            "menu_items": self._create_menu_items_field(),
            "extraction_timestamp": self._create_string_field(
                "ISO 8601 timestamp of when data was extracted",
                format_type="date-time"
            ),
            "source_url": self._create_string_field(
                "Original URL of the scraped page",
                format_type="uri"
            ),
            "parent_page_url": self._create_string_field(
                "URL of the parent page in multi-page scraping",
                format_type="uri"
            ),
            "entity_relationships": self._create_relationships_field(),
            "semantic_chunks": self._create_chunks_field(),
            "cross_references": self._create_cross_references_field(),
            "description": self._create_string_field(
                "Restaurant description"
            )
        }
    
    def _create_location_field(self) -> Dict[str, Any]:
        """Create location field definition."""
        return self._create_object_field(
            "Restaurant location information",
            {
                "address": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "zip": {
                    "type": "string",
                    "pattern": FIELD_PATTERNS["zip_code"]
                },
                "country": {"type": "string"}
            },
            required=["city"]
        )
    
    def _create_menu_items_field(self) -> Dict[str, Any]:
        """Create menu items field definition."""
        return self._create_array_field(
            "Menu items offered by the restaurant",
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "price": {"type": "number"},
                    "category": {"type": "string"}
                },
                "required": ["name"]
            }
        )
    
    def _create_relationships_field(self) -> Dict[str, Any]:
        """Create entity relationships field definition."""
        return self._create_array_field(
            "Relationships to other entities",
            {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [rel.value for rel in RelationshipType],
                        "description": "Type of relationship"
                    },
                    "entity_id": self._create_string_field(
                        "ID of the related entity",
                        FIELD_PATTERNS["entity_id"]
                    ),
                    "entity_type": {"type": "string", "description": "Type of the related entity"},
                    "entity_name": {"type": "string", "description": "Name of the related entity"}
                },
                "required": ["type", "entity_id", "entity_type"]
            }
        )
    
    def _create_chunks_field(self) -> Dict[str, Any]:
        """Create semantic chunks field definition."""
        return self._create_array_field(
            "RAG-optimized content chunks",
            {
                "type": "object",
                "properties": {
                    "chunk_id": {"type": "string", "description": "Unique identifier for the chunk"},
                    "content": {"type": "string", "description": "The actual content of the chunk"},
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata for the chunk",
                        "additionalProperties": True
                    },
                    "embedding_hints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords or phrases for embedding optimization"
                    }
                },
                "required": ["chunk_id", "content"]
            }
        )
    
    def _create_cross_references_field(self) -> Dict[str, Any]:
        """Create cross references field definition."""
        return self._create_array_field(
            "Cross-references to related entities",
            {
                "type": "object",
                "properties": {
                    "ref_id": {"type": "string", "description": "ID of the referenced entity"},
                    "ref_type": {"type": "string", "description": "Type of reference"},
                    "ref_name": {"type": "string", "description": "Name of the referenced entity"},
                    "ref_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL of the referenced entity"
                    }
                },
                "required": ["ref_id", "ref_type"]
            }
        )


class ConfigurationSchemaGenerator(BaseSchemaGenerator):
    """Generator for RAG configuration JSON Schema."""
    
    def generate(self) -> Dict[str, Any]:
        """Generate configuration schema."""
        return {
            "$schema": SCHEMA_CONFIG["version"],
            "title": "RAG Optimization Configuration",
            "description": "Configuration settings for RAG system optimization",
            "type": "object",
            "properties": self._create_config_properties(),
            "required": ["chunk_settings"],
            "additionalProperties": False
        }
    
    def _create_config_properties(self) -> Dict[str, Any]:
        """Create configuration properties."""
        return {
            "chunk_settings": self._create_chunk_settings(),
            "embedding_hints": self._create_embedding_settings(),
            "context_settings": self._create_context_settings(),
            "multi_page_settings": self._create_multipage_settings(),
            "custom_settings": {
                "type": "object",
                "description": "Custom settings for specific use cases",
                "additionalProperties": True
            }
        }
    
    def _create_chunk_settings(self) -> Dict[str, Any]:
        """Create chunk settings schema."""
        return self._create_object_field(
            "Settings for semantic chunking",
            {
                "max_chunk_size": {
                    "type": "integer",
                    "description": "Maximum size of each chunk in characters",
                    "default": DEFAULT_CHUNK_SETTINGS["max_chunk_size"],
                    "minimum": VALIDATION_RULES["max_chunk_size"]["min"],
                    "maximum": VALIDATION_RULES["max_chunk_size"]["max"]
                },
                "overlap_size": {
                    "type": "integer",
                    "description": "Number of characters to overlap between chunks",
                    "default": DEFAULT_CHUNK_SETTINGS["overlap_size"],
                    "minimum": VALIDATION_RULES["overlap_size"]["min"],
                    "maximum": VALIDATION_RULES["overlap_size"]["max"]
                },
                "chunking_method": {
                    "type": "string",
                    "description": "Method for creating chunks",
                    "enum": [method.value for method in ChunkingMethod],
                    "default": DEFAULT_CHUNK_SETTINGS["chunking_method"]
                },
                "preserve_context": {
                    "type": "boolean",
                    "description": "Whether to preserve context across chunks",
                    "default": DEFAULT_CHUNK_SETTINGS["preserve_context"]
                }
            },
            required=["max_chunk_size", "chunking_method"]
        )
    
    def _create_embedding_settings(self) -> Dict[str, Any]:
        """Create embedding settings schema."""
        return self._create_object_field(
            "Settings for embedding optimization",
            {
                "keyword_extraction": {
                    "type": "boolean",
                    "description": "Extract keywords for embedding hints",
                    "default": DEFAULT_EMBEDDING_SETTINGS["keyword_extraction"]
                },
                "entity_recognition": {
                    "type": "boolean",
                    "description": "Use entity recognition for better embeddings",
                    "default": DEFAULT_EMBEDDING_SETTINGS["entity_recognition"]
                },
                "max_keywords": {
                    "type": "integer",
                    "description": "Maximum keywords per chunk",
                    "default": DEFAULT_EMBEDDING_SETTINGS["max_keywords"],
                    "minimum": 1,
                    "maximum": 50
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include metadata in embeddings",
                    "default": DEFAULT_EMBEDDING_SETTINGS["include_metadata"]
                }
            }
        )
    
    def _create_context_settings(self) -> Dict[str, Any]:
        """Create context settings schema."""
        return self._create_object_field(
            "Settings for context preservation",
            {
                "context_window": {
                    "type": "integer",
                    "description": "Size of context window in characters",
                    "default": DEFAULT_CONTEXT_SETTINGS["context_window"],
                    "minimum": VALIDATION_RULES["context_window"]["min"],
                    "maximum": VALIDATION_RULES["context_window"]["max"]
                },
                "preservation_strategy": {
                    "type": "string",
                    "description": "Strategy for preserving context",
                    "enum": [strategy.value for strategy in PreservationStrategy],
                    "default": DEFAULT_CONTEXT_SETTINGS["preservation_strategy"]
                },
                "include_parent_context": {
                    "type": "boolean",
                    "description": "Include parent page context",
                    "default": DEFAULT_CONTEXT_SETTINGS["include_parent_context"]
                }
            }
        )
    
    def _create_multipage_settings(self) -> Dict[str, Any]:
        """Create multi-page settings schema."""
        return self._create_object_field(
            "Settings for multi-page processing",
            {
                "relationship_depth": {
                    "type": "integer",
                    "description": "Maximum depth for relationship traversal",
                    "default": DEFAULT_MULTIPAGE_SETTINGS["relationship_depth"],
                    "minimum": VALIDATION_RULES["relationship_depth"]["min"],
                    "maximum": VALIDATION_RULES["relationship_depth"]["max"]
                },
                "aggregation_method": {
                    "type": "string",
                    "description": "Method for aggregating multi-page data",
                    "enum": [method.value for method in AggregationMethod],
                    "default": DEFAULT_MULTIPAGE_SETTINGS["aggregation_method"]
                },
                "deduplication": {
                    "type": "boolean",
                    "description": "Enable deduplication across pages",
                    "default": DEFAULT_MULTIPAGE_SETTINGS["deduplication"]
                },
                "cross_reference_limit": {
                    "type": "integer",
                    "description": "Maximum cross-references per entity",
                    "default": DEFAULT_MULTIPAGE_SETTINGS["cross_reference_limit"],
                    "minimum": VALIDATION_RULES["cross_reference_limit"]["min"],
                    "maximum": VALIDATION_RULES["cross_reference_limit"]["max"]
                }
            }
        )


class SchemaValidator:
    """Validator for generated schemas."""
    
    def __init__(self):
        self.errors: List[str] = []
    
    def validate_restaurant_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate restaurant data schema."""
        self.errors.clear()
        
        # Check basic structure
        if not self._check_basic_structure(schema):
            return False
        
        # Check required fields
        if not self._check_required_fields(schema):
            return False
        
        # Check field types
        if not self._check_field_types(schema):
            return False
        
        return len(self.errors) == 0
    
    def validate_config_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate configuration schema."""
        self.errors.clear()
        
        # Check basic structure
        if not self._check_basic_structure(schema):
            return False
        
        # Check settings sections
        if not self._check_settings_sections(schema):
            return False
        
        return len(self.errors) == 0
    
    def _check_basic_structure(self, schema: Dict[str, Any]) -> bool:
        """Check basic schema structure."""
        required_keys = ["$schema", "type", "properties"]
        for key in required_keys:
            if key not in schema:
                self.errors.append(f"Missing required key: {key}")
                return False
        return True
    
    def _check_required_fields(self, schema: Dict[str, Any]) -> bool:
        """Check that all required fields are present."""
        properties = schema.get("properties", {})
        for field in REQUIRED_FIELDS:
            if field not in properties:
                self.errors.append(f"Missing required field: {field}")
                return False
        return True
    
    def _check_field_types(self, schema: Dict[str, Any]) -> bool:
        """Check field type definitions."""
        properties = schema.get("properties", {})
        
        # Check string fields have type
        string_fields = ["restaurant_id", "restaurant_name", "cuisine_type"]
        for field in string_fields:
            if field in properties:
                if properties[field].get("type") != "string":
                    self.errors.append(f"Field {field} should be string type")
                    return False
        
        return True
    
    def _check_settings_sections(self, schema: Dict[str, Any]) -> bool:
        """Check configuration settings sections."""
        properties = schema.get("properties", {})
        required_sections = ["chunk_settings"]
        
        for section in required_sections:
            if section not in properties:
                self.errors.append(f"Missing required settings section: {section}")
                return False
        
        return True
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()