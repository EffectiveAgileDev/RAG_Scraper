Feature: Index File Generation for Enhanced Text Files
  As a RAG system developer
  I want to generate comprehensive index files
  So that I can efficiently search and navigate generated text files

  Background:
    Given I have restaurant data from multiple pages
    And the data includes entity relationships
    And I have a configured index file generator

  Scenario: Generate master index.json for all entities
    Given I have generated entity-based text files
    When I create a master index file
    Then the master index should be in JSON format
    And it should list all restaurant entities
    And each entity should include basic metadata
    And the index should include generation statistics
    And the file should be named "master_index.json"

  Scenario: Create category-specific index files
    Given I have restaurants from different cuisine categories
    When I generate category indices
    Then each cuisine type should have its own index file
    And category indices should be named "{category}_index.json"
    And each category index should only contain restaurants of that type
    And category indices should include category-specific statistics

  Scenario: Implement entity relationship maps in indices
    Given I have restaurant data with parent-child relationships
    When I generate index files with relationship mapping
    Then the master index should include a relationship section
    And parent-child relationships should be documented
    And sibling relationships should be mapped
    And circular references should be handled properly
    And relationship metadata should be accessible programmatically

  Scenario: Add search metadata to index files
    Given I have restaurant entities with diverse attributes
    When I generate index files with search metadata
    Then each entity should include searchable keywords
    And cuisine types should be indexed for filtering
    And location information should be searchable
    And menu items should be included in search metadata
    And search metadata should support fuzzy matching

  Scenario: Generate JSON format for programmatic access
    Given I have a collection of restaurant text files
    When I create JSON index files
    Then the JSON structure should be well-formed and valid
    And it should include entity IDs for file mapping
    And file paths should be relative to the index location
    And the JSON should include schema version information
    And nested objects should represent entity hierarchies

  Scenario: Create text format indices for human readability
    Given I have generated JSON index files
    When I create human-readable text indices
    Then text indices should be clearly formatted
    And they should include table-of-contents style navigation
    And entity summaries should be human-friendly
    And file paths should be clearly listed
    And the text format should complement the JSON format

  Scenario: Include comprehensive statistics and summaries
    Given I have processed multiple restaurant entities
    When I generate index files with statistics
    Then the index should include total entity counts
    And it should show breakdown by cuisine categories
    And file size statistics should be included
    And generation timestamps should be recorded
    And data quality metrics should be provided

  Scenario: Handle large-scale index generation efficiently
    Given I have data from 50+ restaurant entities
    When I generate comprehensive index files
    Then all entities should be properly indexed
    And index generation should complete within reasonable time
    And memory usage should remain efficient
    And index files should not exceed practical size limits
    And the indexing process should be resumable if interrupted

  Scenario: Validate index file integrity and consistency
    Given I have generated index files and text files
    When I validate the index integrity
    Then all referenced text files should exist
    And entity IDs should be consistent across indices
    And category assignments should be accurate
    And relationship mappings should be bidirectional where appropriate
    And no orphaned references should exist

  Scenario: Support incremental index updates
    Given I have existing index files
    And I have new restaurant entities to add
    When I perform incremental index updates
    Then new entities should be added to appropriate indices
    And existing entities should remain unchanged
    And statistics should be updated accurately
    And index consistency should be maintained
    And the update process should be atomic