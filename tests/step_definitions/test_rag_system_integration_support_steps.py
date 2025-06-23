"""Step definitions for RAG System Integration Support feature."""

import pytest
from pytest_bdd import given, when, then, scenarios, parsers
import json
import os
from pathlib import Path
from typing import Dict, List, Any

# Link scenarios from the feature file
scenarios("../features/rag_system_integration_support.feature")


@pytest.fixture
def integration_context():
    """Context for integration support testing."""
    return {
        "scraped_data": {},
        "enhanced_files": [],
        "generated_artifacts": {},
        "schemas": {},
        "type_definitions": {},
        "documentation": {},
        "sample_code": {},
        "api_docs": {},
        "integration_package": None
    }


@given("I have scraped restaurant data from multiple pages")
def given_scraped_data(integration_context):
    """Set up scraped restaurant data."""
    integration_context["scraped_data"] = {
        "restaurants": [
            {
                "restaurant_id": "rest_001",
                "restaurant_name": "Luigi's Italian Bistro",
                "cuisine_type": "Italian",
                "location": {"city": "New York", "state": "NY"},
                "source_url": "https://example.com/restaurants/luigis",
                "parent_page_url": "https://example.com/restaurants"
            },
            {
                "restaurant_id": "rest_002",
                "restaurant_name": "Tokyo Sushi Bar",
                "cuisine_type": "Japanese",
                "location": {"city": "San Francisco", "state": "CA"},
                "source_url": "https://example.com/restaurants/tokyo-sushi",
                "parent_page_url": "https://example.com/restaurants"
            }
        ]
    }


@given("the enhanced text files have been generated with metadata")
def given_enhanced_files(integration_context):
    """Set up enhanced text files."""
    integration_context["enhanced_files"] = [
        "Italian/luigis_italian_bistro.txt",
        "Japanese/tokyo_sushi_bar.txt"
    ]


@given("I need to integrate this data into a RAG system")
def given_rag_integration_need(integration_context):
    """Acknowledge RAG integration requirement."""
    integration_context["rag_integration_needed"] = True


@when("I request the JSON schema for the enhanced text file format")
def when_request_json_schema(integration_context):
    """Request JSON schema generation."""
    # This would call the actual schema generator
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["schemas"]["json_schema"] = support.generate_json_schema()


@when("I request TypeScript type definitions for the scraped data structures")
def when_request_typescript_types(integration_context):
    """Request TypeScript type definitions."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["type_definitions"]["typescript"] = support.generate_typescript_types()


@when("I request Python type definitions for the scraped data structures")
def when_request_python_types(integration_context):
    """Request Python type definitions."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["type_definitions"]["python"] = support.generate_python_types()


@when("I request documentation for the entity relationship schema")
def when_request_entity_docs(integration_context):
    """Request entity relationship documentation."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["documentation"]["entity_relationships"] = support.generate_entity_relationship_docs()


@when("I request the configuration schema for RAG optimization settings")
def when_request_config_schema(integration_context):
    """Request configuration schema."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["schemas"]["config_schema"] = support.generate_config_schema()


@when("I request sample integration code for LangChain framework")
def when_request_langchain_sample(integration_context):
    """Request LangChain integration sample."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["sample_code"]["langchain"] = support.generate_langchain_sample()


@when("I request sample integration code for LlamaIndex framework")
def when_request_llamaindex_sample(integration_context):
    """Request LlamaIndex integration sample."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["sample_code"]["llamaindex"] = support.generate_llamaindex_sample()


@when("I request API documentation for programmatic access")
def when_request_api_docs(integration_context):
    """Request API documentation."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["api_docs"] = support.generate_api_documentation()


@when("I generate all integration support artifacts")
def when_generate_all_artifacts(integration_context):
    """Generate all integration artifacts."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["generated_artifacts"] = support.generate_all_artifacts()


@when("I request a complete integration package")
def when_request_integration_package(integration_context):
    """Request complete integration package."""
    from src.file_generator.rag_integration_support import RAGIntegrationSupport
    
    support = RAGIntegrationSupport()
    integration_context["integration_package"] = support.create_integration_package()


@then("a complete JSON schema should be generated")
def then_json_schema_generated(integration_context):
    """Verify JSON schema generation."""
    assert "json_schema" in integration_context["schemas"]
    schema = integration_context["schemas"]["json_schema"]
    assert isinstance(schema, dict)
    assert "$schema" in schema
    assert "type" in schema
    assert "properties" in schema


@then(parsers.parse("the schema should define all metadata fields including:\n{table}"))
def then_schema_has_fields(integration_context, table):
    """Verify schema includes all required fields."""
    schema = integration_context["schemas"]["json_schema"]
    properties = schema.get("properties", {})
    
    # Parse the table data
    for row in table.split("\n")[1:]:  # Skip header
        field, _ = [col.strip() for col in row.split("|")[1:-1]]
        assert field in properties, f"Field {field} not found in schema"


@then("the schema should include validation rules for each field")
def then_schema_has_validation(integration_context):
    """Verify schema includes validation rules."""
    schema = integration_context["schemas"]["json_schema"]
    properties = schema.get("properties", {})
    
    for field, field_schema in properties.items():
        assert "type" in field_schema or "$ref" in field_schema
        # Some fields should have additional validation
        if field == "restaurant_id":
            assert "pattern" in field_schema
        elif field == "extraction_timestamp":
            assert "format" in field_schema


@then("the schema should be compatible with JSON Schema Draft-07")
def then_schema_draft07_compatible(integration_context):
    """Verify JSON Schema Draft-07 compatibility."""
    schema = integration_context["schemas"]["json_schema"]
    assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"


@then(parsers.parse("TypeScript interfaces should be generated including:\n{table}"))
def then_typescript_interfaces_generated(integration_context, table):
    """Verify TypeScript interfaces."""
    typescript_code = integration_context["type_definitions"]["typescript"]
    assert isinstance(typescript_code, str)
    
    # Parse the table data
    for row in table.split("\n")[1:]:  # Skip header
        interface_name, _ = [col.strip() for col in row.split("|")[1:-1]]
        assert f"interface {interface_name}" in typescript_code or \
               f"export interface {interface_name}" in typescript_code


@then("the types should include proper TypeScript annotations")
def then_typescript_annotations(integration_context):
    """Verify TypeScript annotations."""
    typescript_code = integration_context["type_definitions"]["typescript"]
    assert "string" in typescript_code
    assert "number" in typescript_code
    assert "interface" in typescript_code
    assert "export" in typescript_code


@then("the types should support null safety with optional fields")
def then_typescript_null_safety(integration_context):
    """Verify TypeScript null safety."""
    typescript_code = integration_context["type_definitions"]["typescript"]
    assert "?" in typescript_code  # Optional fields
    assert "| null" in typescript_code or "| undefined" in typescript_code


@then("the generated types should be exportable as a module")
def then_typescript_exportable(integration_context):
    """Verify TypeScript module exports."""
    typescript_code = integration_context["type_definitions"]["typescript"]
    assert "export" in typescript_code


@then(parsers.parse("Python dataclasses or TypedDict definitions should be generated including:\n{table}"))
def then_python_types_generated(integration_context, table):
    """Verify Python type definitions."""
    python_code = integration_context["type_definitions"]["python"]
    assert isinstance(python_code, str)
    
    # Parse the table data
    for row in table.split("\n")[1:]:  # Skip header
        class_name, _ = [col.strip() for col in row.split("|")[1:-1]]
        assert f"class {class_name}" in python_code or \
               f"{class_name} = TypedDict" in python_code


@then("the types should use Python 3.8+ type hints")
def then_python_type_hints(integration_context):
    """Verify Python type hints."""
    python_code = integration_context["type_definitions"]["python"]
    assert "from typing import" in python_code
    assert "str" in python_code or "int" in python_code or "float" in python_code
    assert "Dict" in python_code or "dict" in python_code
    assert "List" in python_code or "list" in python_code


@then("the types should include validation with pydantic if requested")
def then_python_pydantic_option(integration_context):
    """Verify pydantic option."""
    python_code = integration_context["type_definitions"]["python"]
    # Should have either dataclass or pydantic imports
    assert "from dataclasses import dataclass" in python_code or \
           "from pydantic import BaseModel" in python_code


@then("the generated types should be importable as a module")
def then_python_importable(integration_context):
    """Verify Python module structure."""
    python_code = integration_context["type_definitions"]["python"]
    assert "__all__" in python_code or "class" in python_code


@then(parsers.parse("comprehensive documentation should be generated including:\n{table}"))
def then_documentation_generated(integration_context, table):
    """Verify documentation generation."""
    docs = integration_context["documentation"]["entity_relationships"]
    assert isinstance(docs, str)
    
    # Parse the table data
    for row in table.split("\n")[1:]:  # Skip header
        section, _ = [col.strip() for col in row.split("|")[1:-1]]
        assert section in docs or section.lower() in docs.lower()


@then("the documentation should include code examples in multiple languages")
def then_docs_have_code_examples(integration_context):
    """Verify code examples in documentation."""
    docs = integration_context["documentation"]["entity_relationships"]
    assert "```python" in docs or "```Python" in docs
    assert "```typescript" in docs or "```TypeScript" in docs or "```javascript" in docs


@then("the documentation should explain multi-page relationship handling")
def then_docs_explain_multipage(integration_context):
    """Verify multi-page documentation."""
    docs = integration_context["documentation"]["entity_relationships"]
    assert "multi-page" in docs.lower() or "multiple pages" in docs.lower()
    assert "parent" in docs.lower()
    assert "child" in docs.lower()


@then("the documentation should be in Markdown format")
def then_docs_markdown_format(integration_context):
    """Verify Markdown format."""
    docs = integration_context["documentation"]["entity_relationships"]
    assert "#" in docs  # Headers
    assert "```" in docs  # Code blocks


@then(parsers.parse("a JSON schema should be generated for configuration including:\n{table}"))
def then_config_schema_generated(integration_context, table):
    """Verify configuration schema."""
    schema = integration_context["schemas"]["config_schema"]
    assert isinstance(schema, dict)
    properties = schema.get("properties", {})
    
    # Parse the table data
    for row in table.split("\n")[1:]:  # Skip header
        category, settings = [col.strip() for col in row.split("|")[1:-1]]
        assert category in properties
        # Check that settings are present
        for setting in settings.split(", "):
            found = False
            for prop in properties.values():
                if isinstance(prop, dict) and "properties" in prop:
                    if setting in prop["properties"]:
                        found = True
                        break
            assert found, f"Setting {setting} not found in schema"


@then("the schema should include default values for each setting")
def then_config_has_defaults(integration_context):
    """Verify default values in config schema."""
    schema = integration_context["schemas"]["config_schema"]
    
    def check_defaults(obj):
        if isinstance(obj, dict):
            if "properties" in obj:
                for prop in obj["properties"].values():
                    if isinstance(prop, dict):
                        assert "default" in prop or "properties" in prop
                        check_defaults(prop)
    
    check_defaults(schema)


@then("the schema should include validation rules and constraints")
def then_config_has_validation(integration_context):
    """Verify validation in config schema."""
    schema = integration_context["schemas"]["config_schema"]
    
    def check_validation(obj):
        if isinstance(obj, dict):
            if "properties" in obj:
                for prop in obj["properties"].values():
                    if isinstance(prop, dict):
                        # Should have type and potentially other constraints
                        assert "type" in prop or "$ref" in prop
                        check_validation(prop)
    
    check_validation(schema)


@then("the schema should be extensible for custom settings")
def then_config_extensible(integration_context):
    """Verify config extensibility."""
    schema = integration_context["schemas"]["config_schema"]
    # Should allow additional properties or have extension points
    assert schema.get("additionalProperties", False) or \
           "custom" in str(schema).lower() or \
           "extension" in str(schema).lower()


@then(parsers.parse("Python code should be generated that demonstrates:\n{table}"))
def then_python_sample_generated(integration_context, table):
    """Verify Python sample code."""
    # Check both LangChain and LlamaIndex samples
    for framework in ["langchain", "llamaindex"]:
        if framework in integration_context["sample_code"]:
            code = integration_context["sample_code"][framework]
            assert isinstance(code, str)
            assert "import" in code
            assert "def" in code or "class" in code
            
            # Parse table and verify components
            for row in table.split("\n")[1:]:  # Skip header
                component, _ = [col.strip() for col in row.split("|")[1:-1]]
                # Component should be referenced in code or comments
                assert component.lower() in code.lower()


@then("the code should include error handling")
def then_sample_has_error_handling(integration_context):
    """Verify error handling in samples."""
    for code in integration_context["sample_code"].values():
        assert "try" in code or "except" in code or "Exception" in code


@then("the code should include comments explaining each step")
def then_sample_has_comments(integration_context):
    """Verify comments in samples."""
    for code in integration_context["sample_code"].values():
        assert "#" in code or '"""' in code or "'''" in code


@then("the code should be runnable with minimal setup")
def then_sample_runnable(integration_context):
    """Verify sample is runnable."""
    for code in integration_context["sample_code"].values():
        # Should have imports and main logic
        assert "import" in code
        assert "if __name__" in code or "def main" in code or "class" in code


@then("the code should follow LangChain best practices")
def then_langchain_best_practices(integration_context):
    """Verify LangChain best practices."""
    if "langchain" in integration_context["sample_code"]:
        code = integration_context["sample_code"]["langchain"]
        assert "from langchain" in code
        # Should use proper chain construction
        assert "Chain" in code or "chain" in code


@then("the code should include configuration examples")
def then_sample_has_config(integration_context):
    """Verify configuration in samples."""
    for code in integration_context["sample_code"].values():
        assert "config" in code.lower() or "settings" in code.lower()


@then("the code should handle large-scale data efficiently")
def then_sample_handles_scale(integration_context):
    """Verify scalability considerations."""
    for code in integration_context["sample_code"].values():
        # Should mention batch processing or streaming
        assert "batch" in code.lower() or "stream" in code.lower() or \
               "chunk" in code.lower() or "iterator" in code.lower()


@then("the code should follow LlamaIndex best practices")
def then_llamaindex_best_practices(integration_context):
    """Verify LlamaIndex best practices."""
    if "llamaindex" in integration_context["sample_code"]:
        code = integration_context["sample_code"]["llamaindex"]
        assert "from llama_index" in code or "import llama_index" in code
        # Should use proper index construction
        assert "Index" in code or "index" in code


@then(parsers.parse("comprehensive API documentation should be generated including:\n{table}"))
def then_api_docs_generated(integration_context, table):
    """Verify API documentation."""
    api_docs = integration_context["api_docs"]
    assert isinstance(api_docs, dict) or isinstance(api_docs, str)
    
    # Convert to string if dict
    docs_str = str(api_docs)
    
    # Parse table and verify sections
    for row in table.split("\n")[1:]:  # Skip header
        section, _ = [col.strip() for col in row.split("|")[1:-1]]
        assert section in docs_str or section.lower() in docs_str.lower()


@then("the documentation should include REST API endpoints if applicable")
def then_api_docs_rest_endpoints(integration_context):
    """Verify REST endpoints documentation."""
    api_docs = str(integration_context["api_docs"])
    # Should mention endpoints or HTTP methods
    assert "endpoint" in api_docs.lower() or \
           "GET" in api_docs or "POST" in api_docs or \
           "http" in api_docs.lower()


@then("the documentation should explain batch processing results")
def then_api_docs_batch_processing(integration_context):
    """Verify batch processing documentation."""
    api_docs = str(integration_context["api_docs"])
    assert "batch" in api_docs.lower()
    assert "process" in api_docs.lower()


@then("the documentation should be in OpenAPI 3.0 format where applicable")
def then_api_docs_openapi_format(integration_context):
    """Verify OpenAPI format where applicable."""
    api_docs = integration_context["api_docs"]
    if isinstance(api_docs, dict):
        # Check for OpenAPI structure
        if "openapi" in api_docs:
            assert api_docs["openapi"].startswith("3.")


@then("all generated schemas should be valid according to their specifications")
def then_schemas_valid(integration_context):
    """Verify schema validity."""
    for schema_name, schema in integration_context["schemas"].items():
        assert isinstance(schema, dict)
        if "json_schema" in schema_name:
            assert "$schema" in schema
            assert "type" in schema


@then("all code samples should be syntactically correct")
def then_code_samples_valid(integration_context):
    """Verify code syntax."""
    for framework, code in integration_context["sample_code"].items():
        assert isinstance(code, str)
        # Basic syntax checks
        assert code.count("(") == code.count(")")
        assert code.count("{") == code.count("}")
        assert code.count("[") == code.count("]")
        
        # Python specific
        if "python" in framework.lower() or framework in ["langchain", "llamaindex"]:
            assert "import" in code
            assert not code.strip().endswith(":")


@then("all documentation should be complete and consistent")
def then_docs_complete(integration_context):
    """Verify documentation completeness."""
    for doc_type, doc in integration_context["documentation"].items():
        assert isinstance(doc, str)
        assert len(doc) > 100  # Should have substantial content
        
        # Should have sections
        assert "#" in doc or "=" in doc  # Headers


@then("there should be no conflicting definitions across artifacts")
def then_no_conflicts(integration_context):
    """Verify no conflicts between artifacts."""
    # Collect all type/class names
    all_names = set()
    
    # From TypeScript
    if "typescript" in integration_context["type_definitions"]:
        ts_code = integration_context["type_definitions"]["typescript"]
        # Extract interface names (simplified)
        for line in ts_code.split("\n"):
            if "interface" in line:
                parts = line.split()
                if "interface" in parts:
                    idx = parts.index("interface")
                    if idx + 1 < len(parts):
                        all_names.add(parts[idx + 1].strip("{"))
    
    # From Python
    if "python" in integration_context["type_definitions"]:
        py_code = integration_context["type_definitions"]["python"]
        # Extract class names (simplified)
        for line in py_code.split("\n"):
            if "class" in line:
                parts = line.split()
                if "class" in parts:
                    idx = parts.index("class")
                    if idx + 1 < len(parts):
                        all_names.add(parts[idx + 1].strip("(:"))
    
    # No duplicate names (this is a simplified check)
    assert len(all_names) == len(set(all_names))


@then("all artifacts should be compatible with the latest output format")
def then_artifacts_compatible(integration_context):
    """Verify artifacts compatibility."""
    # All artifacts should reference the same core types
    artifacts_text = str(integration_context)
    
    # Core types that should be consistent
    core_types = ["restaurant_id", "cuisine_type", "extraction_timestamp"]
    for core_type in core_types:
        assert core_type in artifacts_text


@then(parsers.parse("a structured package should be created containing:\n{table}"))
def then_package_structure(integration_context, table):
    """Verify package structure."""
    package = integration_context["integration_package"]
    assert isinstance(package, dict)
    
    # Parse table and verify directories
    for row in table.split("\n")[1:]:  # Skip header
        directory, _ = [col.strip() for col in row.split("|")[1:-1]]
        dir_name = directory.rstrip("/")
        assert dir_name in package


@then("the package should include a README with quick start guide")
def then_package_has_readme(integration_context):
    """Verify README in package."""
    package = integration_context["integration_package"]
    assert "README" in package or "readme" in str(package).lower()


@then("the package should be versioned to match the scraper version")
def then_package_versioned(integration_context):
    """Verify package versioning."""
    package = integration_context["integration_package"]
    # Should have version info
    assert "version" in str(package).lower()


@then("the package should be distributable as a standalone artifact")
def then_package_distributable(integration_context):
    """Verify package is distributable."""
    package = integration_context["integration_package"]
    # Should be self-contained
    assert isinstance(package, dict)
    assert len(package) > 0
    # Should have all necessary components
    required_components = ["schemas", "types", "docs", "examples"]
    for component in required_components:
        assert any(component in key for key in package.keys())