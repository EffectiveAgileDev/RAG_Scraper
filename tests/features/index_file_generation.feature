Feature: Index File Generation for Multi-Page Import Systems
  As a RAG system developer
  I want to generate comprehensive index files from multi-page scraped data
  So that I can efficiently search and navigate generated text files with full provenance tracking

  Background:
    Given I have restaurant data extracted from multiple related pages
    And the multi-page data includes parent-child page relationships
    And the data includes cross-page entity correlations
    And each entity has extraction provenance from source pages
    And I have a configured index file generator for multi-page context

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

  Scenario: Generate indices with multi-page provenance tracking
    Given I have restaurant data extracted from directory and detail pages
    And each entity has provenance metadata from source pages
    When I generate index files with provenance tracking
    Then each index entry should include source page URLs
    And extraction timestamps should be preserved per entity
    And extraction methods should be tracked per data point
    And parent-child page relationships should be documented
    And cross-page data correlation should be maintained

  Scenario: Index generation from cross-page entity relationships
    Given I have a restaurant directory page with entity "dir_001"
    And detail pages for restaurants "rest_001" and "rest_002" 
    And a menu page "menu_001" linked to "rest_001"
    When I generate indices with cross-page relationships
    Then the master index should map directory to restaurant relationships
    Then restaurant indices should reference their menu pages
    And relationship provenance should include source page context
    And bidirectional relationship mapping should be maintained

  Scenario: Aggregate multi-page data into unified indices
    Given restaurant "rest_001" has data from multiple pages:
      | page_type | url                    | data_extracted           |
      | directory | /restaurants           | name, cuisine, basic_info |
      | detail    | /restaurants/bistro    | full_details, hours       |
      | menu      | /restaurants/bistro/menu | menu_items, prices      |
    When I generate unified index entries
    Then each entity should aggregate data from all source pages
    And data conflicts should be resolved using page hierarchy rules
    And the most specific page data should take precedence
    And aggregation metadata should track data source contributions

  Scenario: Handle multi-page extraction timeline in indices
    Given restaurant data extracted across multiple scraping sessions
    And some pages were scraped at different times
    When I generate index files with temporal awareness
    Then indices should include extraction timeline metadata
    And stale data should be identified and flagged
    And the most recent extraction should be prioritized
    And historical extraction data should be preserved for auditing

  Scenario: Index multi-page context inheritance patterns
    Given directory pages with common context for all child restaurants
    And child restaurant pages that inherit parent context
    When I generate indices with context inheritance tracking
    Then inherited context should be explicitly documented
    And context inheritance rules should be preserved
    And child-specific overrides should be clearly marked
    And context provenance should trace back to parent pages