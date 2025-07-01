Feature: Semantic Structuring for RAG Systems
  As a RAG system integrator
  I want extracted restaurant data to be semantically structured
  So that it can be efficiently imported and queried by RAG systems

  Background:
    Given a semantic structurer is initialized
    And sample restaurant data has been extracted

  Scenario: Structure restaurant data into semantic chunks
    Given restaurant data with name "Bistro Deluxe" and description "Fine dining establishment serving French cuisine"
    When I structure the data for RAG
    Then I should receive semantic chunks optimized for embedding
    And each chunk should have a maximum size of 512 tokens
    And each chunk should maintain semantic coherence
    And chunks should not break mid-sentence

  Scenario: Add rich metadata to semantic chunks
    Given restaurant data with multiple attributes including cuisine, price range, and location
    When I structure the data with metadata enrichment
    Then each chunk should have metadata including:
      | metadata_field   | example_value        |
      | source_type      | restaurant           |
      | entity_name      | Bistro Deluxe        |
      | chunk_type       | description          |
      | confidence_score | 0.95                 |
      | extraction_method| json_ld              |
      | timestamp        | 2024-01-07T10:00:00Z |
    And metadata should support filtering and retrieval

  Scenario: Create relationship mappings between chunks
    Given restaurant data with menu items, hours, and contact information
    When I create semantic relationships
    Then I should have a relationship graph including:
      | from_chunk        | relationship | to_chunk          |
      | restaurant_info   | has_menu     | menu_items        |
      | restaurant_info   | has_hours    | business_hours    |
      | menu_items        | priced_in    | price_range       |
      | restaurant_info   | located_at   | address_chunk     |
    And relationships should be bidirectional where appropriate

  Scenario: Generate embedding hints for optimal vectorization
    Given restaurant data with ambiance descriptions and menu items
    When I generate embedding hints
    Then each chunk should have embedding hints including:
      | hint_type          | purpose                           |
      | semantic_context   | Improve embedding quality         |
      | domain_keywords    | Restaurant-specific terms         |
      | importance_weight  | Prioritize key information        |
      | query_templates    | Common search patterns            |

  Scenario: Export structured data in JSON format
    Given semantically structured restaurant data
    When I export to JSON format
    Then the output should be valid JSON
    And it should include all chunks, metadata, and relationships
    And it should follow the RAG-ready schema

  Scenario: Export structured data in JSONL format
    Given semantically structured restaurant data
    When I export to JSONL format
    Then each line should be a valid JSON object
    And each line should represent one semantic chunk
    And metadata should be embedded in each line

  Scenario: Export structured data in Parquet format
    Given semantically structured restaurant data
    When I export to Parquet format
    Then the output should be a valid Parquet file
    And it should have optimized columnar storage
    And it should preserve all data types correctly

  Scenario: Handle multi-modal content in semantic structure
    Given restaurant data with text, images, and PDF content
    When I structure multi-modal data
    Then text content should be in standard chunks
    And image descriptions should be separate chunks with image metadata
    And PDF content should maintain document structure
    And all chunks should be linked via relationships

  Scenario: Optimize chunk boundaries for semantic coherence
    Given a long restaurant description that exceeds chunk size limits
    When I apply intelligent chunking
    Then chunks should break at natural boundaries like paragraphs
    And related information should be kept together
    And no chunk should exceed the token limit
    And overlapping context should be provided between chunks

  Scenario: Generate summary chunks for quick retrieval
    Given complete restaurant data
    When I generate summary chunks
    Then I should have a primary summary chunk with key information
    And the summary should include name, cuisine, price range, and location
    And the summary chunk should be marked with "summary" type
    And it should link to detailed chunks

  Scenario: Support configurable chunk sizes
    Given restaurant data and a custom chunk size of 256 tokens
    When I structure data with custom configuration
    Then all chunks should respect the 256 token limit
    And the configuration should be stored in metadata
    And chunk boundaries should still maintain semantic coherence

  Scenario: Add temporal metadata for time-sensitive information
    Given restaurant hours and special event information
    When I structure temporal data
    Then business hours should have "recurring_schedule" temporal type
    And special events should have "specific_date" temporal type
    And temporal metadata should enable time-based queries

  Scenario: Create hierarchical chunk organization
    Given restaurant data with nested information
    When I create hierarchical structure
    Then I should have parent chunks for main categories
    And child chunks for detailed information
    And the hierarchy should be navigable via relationships
    And hierarchy depth should not exceed 3 levels

  Scenario: Support multiple export profiles
    Given semantically structured data
    When I export with "chatbot" profile
    Then chunks should be optimized for conversational retrieval
    When I export with "search" profile  
    Then chunks should be optimized for keyword search
    When I export with "analytics" profile
    Then data should be structured for aggregation queries

  Scenario: Handle missing or incomplete data gracefully
    Given restaurant data with missing phone numbers and incomplete addresses
    When I structure incomplete data
    Then missing fields should be marked in metadata
    And chunks should still be created for available data
    And confidence scores should reflect data completeness
    And relationships should only include verified data