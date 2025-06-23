Feature: RAG System Integration Support
  As a developer consuming RAG_Scraper output
  I want well-defined schemas and integration support
  So that I can easily integrate the scraped data into my RAG applications

  Background:
    Given I have scraped restaurant data from multiple pages
    And the enhanced text files have been generated with metadata
    And I need to integrate this data into a RAG system

  Scenario: Generate JSON schema for enhanced text file format
    When I request the JSON schema for the enhanced text file format
    Then a complete JSON schema should be generated
    And the schema should define all metadata fields including:
      | field_type              | description                                    |
      | restaurant_id           | Unique identifier for the restaurant           |
      | restaurant_name         | Name of the restaurant                         |
      | cuisine_type           | Type of cuisine served                         |
      | location               | Restaurant location information                |
      | extraction_timestamp   | When the data was extracted                    |
      | source_url            | Original URL of the scraped page               |
      | parent_page_url       | URL of the parent page if from multi-page      |
      | entity_relationships  | Related entities and their relationships       |
      | semantic_chunks       | RAG-optimized content chunks                   |
      | cross_references      | References to related entities                 |
    And the schema should include validation rules for each field
    And the schema should be compatible with JSON Schema Draft-07

  Scenario: Generate TypeScript type definitions
    When I request TypeScript type definitions for the scraped data structures
    Then TypeScript interfaces should be generated including:
      | interface_name         | purpose                                        |
      | RestaurantData        | Main restaurant data structure                 |
      | EntityRelationship    | Relationship between entities                  |
      | SemanticChunk         | RAG-optimized content chunk                    |
      | ExtractionMetadata    | Metadata about the extraction process          |
      | CrossReference        | Cross-reference information                    |
    And the types should include proper TypeScript annotations
    And the types should support null safety with optional fields
    And the generated types should be exportable as a module

  Scenario: Generate Python type definitions
    When I request Python type definitions for the scraped data structures
    Then Python dataclasses or TypedDict definitions should be generated including:
      | class_name            | purpose                                        |
      | RestaurantData        | Main restaurant data structure                 |
      | EntityRelationship    | Relationship between entities                  |
      | SemanticChunk         | RAG-optimized content chunk                    |
      | ExtractionMetadata    | Metadata about the extraction process          |
      | CrossReference        | Cross-reference information                    |
    And the types should use Python 3.8+ type hints
    And the types should include validation with pydantic if requested
    And the generated types should be importable as a module

  Scenario: Document entity relationship schema
    When I request documentation for the entity relationship schema
    Then comprehensive documentation should be generated including:
      | section                | content                                        |
      | Overview              | High-level description of entity relationships |
      | Relationship Types    | Parent-child, sibling, reference types        |
      | Data Model           | Visual representation of relationships         |
      | Access Patterns      | How to query and traverse relationships        |
      | Examples             | Sample relationship data and queries           |
    And the documentation should include code examples in multiple languages
    And the documentation should explain multi-page relationship handling
    And the documentation should be in Markdown format

  Scenario: Export configuration schema for RAG optimization
    When I request the configuration schema for RAG optimization settings
    Then a JSON schema should be generated for configuration including:
      | setting_category       | settings                                       |
      | chunk_settings        | max_chunk_size, overlap_size, chunking_method |
      | embedding_hints       | keyword_extraction, entity_recognition         |
      | context_settings      | context_window, preservation_strategy          |
      | multi_page_settings   | relationship_depth, aggregation_method         |
    And the schema should include default values for each setting
    And the schema should include validation rules and constraints
    And the schema should be extensible for custom settings

  Scenario: Generate sample integration code for LangChain
    When I request sample integration code for LangChain framework
    Then Python code should be generated that demonstrates:
      | component             | functionality                                  |
      | Document Loader       | Loading enhanced text files with metadata      |
      | Text Splitter        | Using semantic chunks from the files           |
      | Metadata Handler     | Extracting and using metadata in queries       |
      | Vector Store Setup   | Indexing with entity relationships             |
      | Retrieval Chain      | Multi-page aware retrieval                     |
    And the code should include error handling
    And the code should include comments explaining each step
    And the code should be runnable with minimal setup

  Scenario: Generate sample integration code for LlamaIndex
    When I request sample integration code for LlamaIndex framework
    Then Python code should be generated that demonstrates:
      | component             | functionality                                  |
      | Document Loading      | Loading restaurant data with relationships     |
      | Index Creation       | Building indices with metadata                 |
      | Query Engine         | Querying with entity relationship awareness    |
      | Response Synthesis   | Combining data from multiple pages             |
    And the code should follow LlamaIndex best practices
    And the code should include configuration examples
    And the code should handle large-scale data efficiently

  Scenario: Generate API documentation for programmatic access
    When I request API documentation for programmatic access
    Then comprehensive API documentation should be generated including:
      | section               | content                                        |
      | Data Structures      | All output formats and their schemas           |
      | File Organization    | Directory structure and naming conventions     |
      | Access Methods       | How to read and parse generated files          |
      | Integration Points   | Where to hook into the data pipeline           |
      | Code Examples        | Examples in Python, TypeScript, and JavaScript |
    And the documentation should include REST API endpoints if applicable
    And the documentation should explain batch processing results
    And the documentation should be in OpenAPI 3.0 format where applicable

  Scenario: Validate integration artifacts
    When I generate all integration support artifacts
    Then all generated schemas should be valid according to their specifications
    And all code samples should be syntactically correct
    And all documentation should be complete and consistent
    And there should be no conflicting definitions across artifacts
    And all artifacts should be compatible with the latest output format

  Scenario: Export complete integration package
    When I request a complete integration package
    Then a structured package should be created containing:
      | directory             | contents                                       |
      | schemas/              | JSON schemas for all data structures           |
      | types/                | TypeScript and Python type definitions         |
      | docs/                 | All documentation in Markdown format           |
      | examples/             | Integration code for various frameworks        |
      | tests/                | Test data and validation scripts               |
    And the package should include a README with quick start guide
    And the package should be versioned to match the scraper version
    And the package should be distributable as a standalone artifact