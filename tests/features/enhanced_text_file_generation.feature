Feature: Enhanced Text File Generation
  As a user of the RAG scraper
  I want to generate enhanced text files with hierarchical structure
  So that I can use them effectively in RAG systems

  Background:
    Given I have restaurant data from multiple pages
    And the data includes entity relationships
    And I have a configured text file generator

  Scenario: Generate hierarchical document structure
    Given I have restaurant data with parent-child relationships
    When I generate text files with hierarchical structure
    Then the output should maintain entity hierarchy
    And each document should include relationship metadata
    And the structure should be optimized for RAG consumption

  Scenario: Generate entity-based file organization
    Given I have multiple restaurant entities with different types
    When I generate files using entity-based organization
    Then each entity should have its own dedicated file
    And files should be organized by entity type
    And related entities should be cross-referenced

  Scenario: Include cross-reference sections in generated files
    Given I have restaurant data with entity relationships
    When I generate text files with cross-references
    Then each file should include a cross-reference section
    And references should link to related entities
    And circular references should be handled properly

  Scenario: Add RAG-optimized metadata headers
    Given I have restaurant extraction results
    When I generate text files with RAG metadata
    Then each file should include structured metadata headers
    And metadata should contain entity information
    And headers should include extraction provenance
    And the format should be optimized for embedding models

  Scenario: Create category-based output directory structure
    Given I have restaurant data from different categories
    When I generate organized output directories
    Then files should be organized by category
    And each category should have its own directory
    And the structure should include index files

  Scenario: Generate comprehensive index files
    Given I have generated entity-based text files
    When I create index files
    Then a master index should list all entities
    And category indices should organize by type
    And indices should include entity metadata
    And search metadata should be embedded

  Scenario: Handle large-scale multi-page data sets
    Given I have data from 50+ restaurant pages
    When I generate text files for the complete data set
    Then all entities should be processed
    And relationships should be maintained across files
    And the output should be efficiently organized
    And memory usage should remain reasonable

  Scenario: Preserve extraction context in output
    Given I have extraction results with detailed context
    When I generate text files preserving context
    Then each file should include extraction timestamps
    And source page information should be maintained
    And extraction methods should be documented
    And confidence scores should be preserved

  Scenario: Generate RAG-friendly chunk boundaries
    Given I have long restaurant descriptions
    When I generate text files with semantic chunking
    Then content should be divided at natural boundaries
    And chunk markers should be RAG-friendly
    And context should be preserved across chunks
    And overlapping information should be handled

  Scenario: Validate output file integrity
    Given I have generated text files
    When I validate the output structure
    Then all required files should be present
    And cross-references should be valid
    And metadata should be complete
    And file structure should follow conventions