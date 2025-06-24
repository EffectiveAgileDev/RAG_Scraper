"""Refactored RAG Integration Support with improved architecture and error handling."""

import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from .integration_config import (
    VERSION_INFO, PACKAGE_STRUCTURE, ERROR_MESSAGES, 
    SchemaVersion, RelationshipType
)
from .schema_generator import (
    RestaurantDataSchemaGenerator, ConfigurationSchemaGenerator, SchemaValidator
)
from .type_generator import TypeScriptGenerator, PythonDataclassGenerator, PydanticGenerator
from .documentation_generator import (
    EntityRelationshipDocGenerator, APIDocumentationGenerator, ReadmeGenerator
)
from .validation_script_generator import ValidationScriptGenerator
from .langchain_sample_generator import LangChainSampleGenerator
from .llamaindex_sample_generator import LlamaIndexSampleGenerator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for artifact generation."""
    version: str = VERSION_INFO["package_version"]
    include_validation: bool = True
    include_examples: bool = True
    include_documentation: bool = True
    output_directory: Optional[Path] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class GenerationResult:
    """Result of artifact generation."""
    success: bool
    artifacts: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    generation_time: Optional[float] = None


class RAGIntegrationError(Exception):
    """Custom exception for RAG integration errors."""
    
    def __init__(self, message: str, error_type: str = "general", details: Optional[Dict] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}


class ArtifactGenerator(ABC):
    """Base class for artifact generators."""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    @abstractmethod
    def generate(self) -> Tuple[bool, Any]:
        """Generate artifact. Returns (success, artifact)."""
        pass
    
    def _add_error(self, message: str, error_type: str = "generation"):
        """Add error message."""
        error_msg = ERROR_MESSAGES.get(error_type, "Error: {error}").format(error=message)
        self.errors.append(error_msg)
        logger.error(f"{self.__class__.__name__}: {error_msg}")
    
    def _add_warning(self, message: str):
        """Add warning message."""
        self.warnings.append(message)
        logger.warning(f"{self.__class__.__name__}: {message}")
    
    def _validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        return True


class SchemaArtifactGenerator(ArtifactGenerator):
    """Generator for JSON schemas."""
    
    def generate(self) -> Tuple[bool, Dict[str, Any]]:
        """Generate JSON schemas."""
        try:
            schemas = {}
            
            # Generate restaurant data schema
            restaurant_generator = RestaurantDataSchemaGenerator(self.config.version)
            restaurant_schema = restaurant_generator.generate()
            
            if self.config.include_validation:
                validator = SchemaValidator()
                if not validator.validate_restaurant_schema(restaurant_schema):
                    for error in validator.get_errors():
                        self._add_error(f"Restaurant schema validation: {error}")
                    return False, {}
            
            schemas["restaurant_data"] = restaurant_schema
            
            # Generate configuration schema
            config_generator = ConfigurationSchemaGenerator(self.config.version)
            config_schema = config_generator.generate()
            
            if self.config.include_validation:
                if not validator.validate_config_schema(config_schema):
                    for error in validator.get_errors():
                        self._add_error(f"Config schema validation: {error}")
                    return False, {}
            
            schemas["configuration"] = config_schema
            
            logger.info(f"Generated {len(schemas)} schemas successfully")
            return True, schemas
            
        except Exception as e:
            self._add_error(f"Schema generation failed: {e}", "generation_failed")
            return False, {}


class TypeDefinitionArtifactGenerator(ArtifactGenerator):
    """Generator for type definitions."""
    
    def generate(self) -> Tuple[bool, Dict[str, Any]]:
        """Generate type definitions."""
        try:
            types = {}
            
            # Generate TypeScript types
            ts_generator = TypeScriptGenerator(self.config.version)
            typescript = ts_generator.generate()
            types["typescript"] = typescript
            
            # Generate Python dataclass types
            py_generator = PythonDataclassGenerator(self.config.version)
            python_dataclass = py_generator.generate()
            types["python_dataclass"] = python_dataclass
            
            # Generate Pydantic types
            pydantic_generator = PydanticGenerator(self.config.version)
            python_pydantic = pydantic_generator.generate()
            types["python_pydantic"] = python_pydantic
            
            logger.info(f"Generated {len(types)} type definition sets")
            return True, types
            
        except Exception as e:
            self._add_error(f"Type definition generation failed: {e}", "generation_failed")
            return False, {}


class DocumentationArtifactGenerator(ArtifactGenerator):
    """Generator for documentation."""
    
    def generate(self) -> Tuple[bool, Dict[str, Any]]:
        """Generate documentation."""
        try:
            docs = {}
            
            if self.config.include_documentation:
                # Generate entity relationship documentation
                entity_generator = EntityRelationshipDocGenerator(self.config.version)
                entity_docs = entity_generator.generate()
                docs["entity_relationships"] = entity_docs
                
                # Generate API documentation
                api_generator = APIDocumentationGenerator(self.config.version)
                api_docs = api_generator.generate()
                docs["api_reference"] = api_docs
                
                # Generate README
                readme_generator = ReadmeGenerator(self.config.version)
                readme = readme_generator.generate({
                    "version": self.config.version,
                    "schema_version": self.config.version,
                    "scraper_version": self.config.version
                })
                docs["readme"] = readme
            
            logger.info(f"Generated {len(docs)} documentation files")
            return True, docs
            
        except Exception as e:
            self._add_error(f"Documentation generation failed: {e}", "generation_failed")
            return False, {}


class SampleCodeArtifactGenerator(ArtifactGenerator):
    """Generator for sample integration code."""
    
    def generate(self) -> Tuple[bool, Dict[str, Any]]:
        """Generate sample code."""
        try:
            samples = {}
            
            if self.config.include_examples:
                # Generate LangChain sample
                langchain_generator = LangChainSampleGenerator(self.config.version)
                langchain_code = langchain_generator.generate()
                samples["langchain"] = langchain_code
                
                # Generate LlamaIndex sample
                llamaindex_generator = LlamaIndexSampleGenerator(self.config.version)
                llamaindex_code = llamaindex_generator.generate()
                samples["llamaindex"] = llamaindex_code
                
                # Generate validation script
                validation_generator = ValidationScriptGenerator(self.config.version)
                validation_script = validation_generator.generate()
                samples["validation_script"] = validation_script
            
            logger.info(f"Generated {len(samples)} sample code files")
            return True, samples
            
        except Exception as e:
            self._add_error(f"Sample code generation failed: {e}", "generation_failed")
            return False, {}


class IntegrationPackageGenerator:
    """Generates complete integration packages."""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.generators = {
            "schemas": SchemaArtifactGenerator(config),
            "types": TypeDefinitionArtifactGenerator(config),
            "documentation": DocumentationArtifactGenerator(config),
            "samples": SampleCodeArtifactGenerator(config)
        }
    
    def generate_package(self) -> GenerationResult:
        """Generate complete integration package."""
        start_time = datetime.now(timezone.utc)
        result = GenerationResult(success=True)
        
        try:
            logger.info("Starting integration package generation...")
            
            # Generate all artifacts
            for artifact_type, generator in self.generators.items():
                logger.info(f"Generating {artifact_type}...")
                success, artifacts = generator.generate()
                
                if success:
                    result.artifacts[artifact_type] = artifacts
                else:
                    result.success = False
                    result.errors.extend(generator.errors)
                
                result.warnings.extend(generator.warnings)
            
            # Create package structure
            if result.success:
                package = self._create_package_structure(result.artifacts)
                result.artifacts["package"] = package
            
            # Calculate generation time
            end_time = datetime.now(timezone.utc)
            result.generation_time = (end_time - start_time).total_seconds()
            
            if result.success:
                logger.info(f"Package generation completed successfully in {result.generation_time:.2f}s")
            else:
                logger.error(f"Package generation failed with {len(result.errors)} errors")
            
            return result
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Package generation failed: {e}")
            logger.error(f"Package generation failed: {e}")
            return result
    
    def _create_package_structure(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured integration package."""
        package = {
            "version": self.config.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "package_info": {
                "name": "RAG_Scraper Integration Support",
                "version": self.config.version,
                "description": "Complete integration support for RAG_Scraper output",
                "supported_frameworks": VERSION_INFO["supported_frameworks"],
                "min_python_version": VERSION_INFO["min_python_version"]
            }
        }
        
        # Add schemas
        if "schemas" in artifacts:
            package["schemas"] = {
                "restaurant_data.schema.json": artifacts["schemas"]["restaurant_data"],
                "config.schema.json": artifacts["schemas"]["configuration"]
            }
        
        # Add type definitions
        if "types" in artifacts:
            package["types"] = {
                "typescript": {
                    "index.d.ts": artifacts["types"]["typescript"]
                },
                "python": {
                    "models.py": artifacts["types"]["python_dataclass"],
                    "models_pydantic.py": artifacts["types"]["python_pydantic"]
                }
            }
        
        # Add documentation
        if "documentation" in artifacts:
            package["docs"] = {
                "entity_relationships.md": artifacts["documentation"]["entity_relationships"],
                "api_reference.md": artifacts["documentation"]["api_reference"],
                "README.md": artifacts["documentation"]["readme"]
            }
        
        # Add examples
        if "samples" in artifacts:
            package["examples"] = {
                "langchain": {
                    "integration.py": artifacts["samples"]["langchain"]
                },
                "llamaindex": {
                    "integration.py": artifacts["samples"]["llamaindex"]
                }
            }
            
            package["tests"] = {
                "validate_schema.py": artifacts["samples"]["validation_script"],
                "test_data.json": self._generate_test_data()
            }
        
        return package
    
    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate sample test data."""
        return {
            "test_restaurant": {
                "restaurant_id": "test_001",
                "restaurant_name": "Test Restaurant",
                "cuisine_type": "Italian",
                "location": {
                    "city": "Test City",
                    "state": "TS"
                },
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                "source_url": "https://example.com/test",
                "entity_relationships": [],
                "semantic_chunks": [
                    {
                        "chunk_id": "chunk_test_001",
                        "content": "Test restaurant content for validation",
                        "metadata": {"test": True}
                    }
                ],
                "cross_references": []
            }
        }


class RAGIntegrationSupport:
    """Refactored RAG Integration Support with improved error handling and modularity."""
    
    def __init__(self, config: Optional[GenerationConfig] = None):
        """Initialize RAG Integration Support.
        
        Args:
            config: Generation configuration. If None, uses default config.
        """
        self.config = config or GenerationConfig()
        self.package_generator = IntegrationPackageGenerator(self.config)
        self._cache = {}  # Simple caching for expensive operations
    
    def generate_json_schema(self) -> Dict[str, Any]:
        """Generate JSON Schema for enhanced text file format.
        
        Returns:
            Dict containing JSON Schema Draft-07 compliant schema
            
        Raises:
            RAGIntegrationError: If schema generation fails
        """
        cache_key = "json_schema"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            generator = RestaurantDataSchemaGenerator(self.config.version)
            schema = generator.generate()
            
            if self.config.include_validation:
                validator = SchemaValidator()
                if not validator.validate_restaurant_schema(schema):
                    errors = validator.get_errors()
                    raise RAGIntegrationError(
                        "Schema validation failed",
                        error_type="validation_failed", 
                        details={"errors": errors}
                    )
            
            self._cache[cache_key] = schema
            return schema
            
        except Exception as e:
            if isinstance(e, RAGIntegrationError):
                raise
            raise RAGIntegrationError(
                f"JSON schema generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_typescript_types(self) -> str:
        """Generate TypeScript type definitions.
        
        Returns:
            String containing TypeScript interface definitions
            
        Raises:
            RAGIntegrationError: If type generation fails
        """
        cache_key = "typescript_types"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            generator = TypeScriptGenerator(self.config.version)
            types = generator.generate()
            self._cache[cache_key] = types
            return types
            
        except Exception as e:
            raise RAGIntegrationError(
                f"TypeScript type generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_python_types(self, use_pydantic: bool = False) -> str:
        """Generate Python type definitions.
        
        Args:
            use_pydantic: Whether to use Pydantic BaseModel instead of dataclasses
            
        Returns:
            String containing Python type definitions
            
        Raises:
            RAGIntegrationError: If type generation fails
        """
        cache_key = f"python_types_{'pydantic' if use_pydantic else 'dataclass'}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            if use_pydantic:
                generator = PydanticGenerator(self.config.version)
            else:
                generator = PythonDataclassGenerator(self.config.version)
            
            types = generator.generate()
            self._cache[cache_key] = types
            return types
            
        except Exception as e:
            raise RAGIntegrationError(
                f"Python type generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_entity_relationship_docs(self) -> str:
        """Generate documentation for entity relationship schema.
        
        Returns:
            Markdown documentation explaining entity relationships
            
        Raises:
            RAGIntegrationError: If documentation generation fails
        """
        cache_key = "entity_docs"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            generator = EntityRelationshipDocGenerator(self.config.version)
            docs = generator.generate()
            self._cache[cache_key] = docs
            return docs
            
        except Exception as e:
            raise RAGIntegrationError(
                f"Entity relationship documentation generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_config_schema(self) -> Dict[str, Any]:
        """Generate configuration schema for RAG optimization settings.
        
        Returns:
            Dict containing configuration JSON Schema
            
        Raises:
            RAGIntegrationError: If schema generation fails
        """
        cache_key = "config_schema"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            generator = ConfigurationSchemaGenerator(self.config.version)
            schema = generator.generate()
            
            if self.config.include_validation:
                validator = SchemaValidator()
                if not validator.validate_config_schema(schema):
                    errors = validator.get_errors()
                    raise RAGIntegrationError(
                        "Config schema validation failed",
                        error_type="validation_failed",
                        details={"errors": errors}
                    )
            
            self._cache[cache_key] = schema
            return schema
            
        except Exception as e:
            if isinstance(e, RAGIntegrationError):
                raise
            raise RAGIntegrationError(
                f"Configuration schema generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_langchain_sample(self) -> str:
        """Generate sample integration code for LangChain.
        
        Returns:
            String containing LangChain integration example
            
        Raises:
            RAGIntegrationError: If sample generation fails
        """
        try:
            generator = LangChainSampleGenerator(self.config.version)
            return generator.generate()
            
        except Exception as e:
            raise RAGIntegrationError(
                f"LangChain sample generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_llamaindex_sample(self) -> str:
        """Generate sample integration code for LlamaIndex.
        
        Returns:
            String containing LlamaIndex integration example
            
        Raises:
            RAGIntegrationError: If sample generation fails
        """
        try:
            generator = LlamaIndexSampleGenerator(self.config.version)
            return generator.generate()
            
        except Exception as e:
            raise RAGIntegrationError(
                f"LlamaIndex sample generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_api_documentation(self) -> Dict[str, Any]:
        """Generate API documentation for programmatic access.
        
        Returns:
            Dict containing API documentation
            
        Raises:
            RAGIntegrationError: If documentation generation fails
        """
        cache_key = "api_docs"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            generator = APIDocumentationGenerator(self.config.version)
            docs = generator.generate()
            self._cache[cache_key] = docs
            return docs
            
        except Exception as e:
            raise RAGIntegrationError(
                f"API documentation generation failed: {e}",
                error_type="generation_failed"
            )
    
    def generate_all_artifacts(self) -> Dict[str, Any]:
        """Generate all integration support artifacts.
        
        Returns:
            Dict containing all generated artifacts
            
        Raises:
            RAGIntegrationError: If artifact generation fails
        """
        try:
            result = self.package_generator.generate_package()
            
            if not result.success:
                raise RAGIntegrationError(
                    "Artifact generation failed",
                    error_type="generation_failed",
                    details={
                        "errors": result.errors,
                        "warnings": result.warnings
                    }
                )
            
            return result.artifacts
            
        except Exception as e:
            if isinstance(e, RAGIntegrationError):
                raise
            raise RAGIntegrationError(
                f"All artifacts generation failed: {e}",
                error_type="generation_failed"
            )
    
    def create_integration_package(self) -> Dict[str, Any]:
        """Create a complete integration package.
        
        Returns:
            Dict representing the integration package structure
            
        Raises:
            RAGIntegrationError: If package creation fails
        """
        try:
            result = self.package_generator.generate_package()
            
            if not result.success:
                raise RAGIntegrationError(
                    "Integration package creation failed",
                    error_type="generation_failed",
                    details={
                        "errors": result.errors,
                        "warnings": result.warnings
                    }
                )
            
            return result.artifacts.get("package", {})
            
        except Exception as e:
            if isinstance(e, RAGIntegrationError):
                raise
            raise RAGIntegrationError(
                f"Integration package creation failed: {e}",
                error_type="generation_failed"
            )
    
    def validate_generated_artifacts(self, artifacts: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate generated artifacts for consistency and correctness.
        
        Args:
            artifacts: Generated artifacts to validate
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        try:
            # Validate schemas
            if "schemas" in artifacts:
                validator = SchemaValidator()
                for schema_name, schema in artifacts["schemas"].items():
                    if "restaurant" in schema_name.lower():
                        if not validator.validate_restaurant_schema(schema):
                            errors.extend([f"Restaurant schema: {e}" for e in validator.get_errors()])
                    elif "config" in schema_name.lower():
                        if not validator.validate_config_schema(schema):
                            errors.extend([f"Config schema: {e}" for e in validator.get_errors()])
            
            # Validate type definitions
            if "types" in artifacts:
                type_artifacts = artifacts["types"]
                
                # Check TypeScript syntax (basic)
                if "typescript" in type_artifacts:
                    ts_code = type_artifacts["typescript"]
                    if not self._validate_typescript_syntax(ts_code):
                        errors.append("TypeScript type definitions have syntax errors")
                
                # Check Python syntax (basic)
                if "python_dataclass" in type_artifacts:
                    py_code = type_artifacts["python_dataclass"]
                    if not self._validate_python_syntax(py_code):
                        errors.append("Python dataclass definitions have syntax errors")
            
            # Validate documentation
            if "documentation" in artifacts:
                doc_artifacts = artifacts["documentation"]
                for doc_name, doc_content in doc_artifacts.items():
                    if not isinstance(doc_content, str) or len(doc_content) < 100:
                        errors.append(f"Documentation '{doc_name}' is too short or invalid")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation failed: {e}")
            return False, errors
    
    def _validate_typescript_syntax(self, typescript_code: str) -> bool:
        """Basic validation of TypeScript syntax."""
        try:
            # Basic checks
            if typescript_code.count("{") != typescript_code.count("}"):
                return False
            if typescript_code.count("(") != typescript_code.count(")"):
                return False
            if typescript_code.count("[") != typescript_code.count("]"):
                return False
            
            # Check for required elements
            required_elements = ["export interface", "RestaurantData", "EntityRelationship"]
            for element in required_elements:
                if element not in typescript_code:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_python_syntax(self, python_code: str) -> bool:
        """Basic validation of Python syntax."""
        try:
            # Try to compile the code
            compile(python_code, "<string>", "exec")
            
            # Check for required elements
            required_elements = ["class RestaurantData", "from typing import", "__all__"]
            for element in required_elements:
                if element not in python_code:
                    return False
            
            return True
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def clear_cache(self):
        """Clear internal cache."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached items."""
        return {
            "cached_items": list(self._cache.keys()),
            "cache_size": len(self._cache)
        }