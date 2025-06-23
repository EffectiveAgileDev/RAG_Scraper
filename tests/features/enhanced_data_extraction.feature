Feature: Enhanced Data Extraction for Multi-Page Context
  As a multi-page scraper
  I want to extract data with awareness of page relationships and context
  So that I can maintain data coherence across related pages

  Background:
    Given the entity relationship tracker is initialized
    And the following page relationships exist:
      | page_url                        | entity_id | parent_id | page_type |
      | /restaurants/directory          | dir_001   | null      | directory |
      | /restaurants/italian-bistro     | rest_001  | dir_001   | detail    |
      | /restaurants/french-cafe        | rest_002  | dir_001   | detail    |
      | /restaurants/italian-bistro/menu| menu_001  | rest_001  | menu      |

  Scenario: Extract JSON-LD data with relationship context
    Given a restaurant detail page with JSON-LD data
    And the page belongs to entity "rest_001" with parent "dir_001"
    When I extract data using the enhanced JSON-LD extractor
    Then the extraction should include entity relationship metadata
    And the extraction should track the source page URL
    And the extraction should include a timestamp
    And the extraction method should be recorded as "json-ld"

  Scenario: Correlate microdata across parent-child pages
    Given a directory page with microdata listing multiple restaurants
    And detail pages for each restaurant with additional microdata
    When I extract data from the directory page for entity "dir_001"
    And I extract data from detail pages for entities "rest_001" and "rest_002"
    Then the extractor should correlate data between parent and child pages
    And child page data should inherit context from the parent
    And duplicate information should be deduplicated with child data taking precedence

  Scenario: Track extraction patterns across multiple pages
    Given multiple restaurant pages from the same directory
    When the heuristic extractor analyzes the first page
    And it identifies successful extraction patterns
    Then those patterns should be prioritized for subsequent pages
    And the confidence score should increase for consistent patterns
    And pattern learning should be stored in the extraction context

  Scenario: Maintain extraction provenance
    Given a restaurant page with mixed data sources
    When I extract data using multiple extractors
    Then each data point should track:
      | metadata_field    | description                          |
      | source_page      | The URL where the data was found    |
      | extraction_time  | When the data was extracted          |
      | extraction_method| Which extractor found the data       |
      | entity_id        | The entity this data belongs to      |
      | confidence       | The confidence level of extraction   |

  Scenario: Handle cross-page data references
    Given a restaurant detail page references a separate menu page
    And the menu page is linked as entity "menu_001"
    When I extract data from the restaurant page
    Then the extractor should identify menu references
    And mark them for follow-up extraction
    And maintain the relationship between restaurant and menu data

  Scenario: Aggregate extraction results by entity
    Given multiple pages have been extracted for entity "rest_001"
    When I request aggregated extraction results
    Then all data points should be grouped by entity
    And newer extractions should update older ones
    And the aggregation should maintain a complete extraction history
    And confidence scores should be recalculated based on multiple sources

  Scenario: Extract with parent context inheritance
    Given a directory page contains common information for all restaurants
    When I extract data from a child restaurant page
    Then the child should inherit applicable context from the parent
    Such as:
      | context_type     | example                              |
      | location_area    | "Downtown dining district"           |
      | price_category   | "Budget-friendly options"            |
      | cuisine_region   | "Authentic Italian restaurants"      |

  Scenario: Detect and utilize consistent page structures
    Given a directory with restaurants using similar page templates
    When the enhanced extractor processes multiple pages
    Then it should detect common structural patterns
    And optimize extraction based on learned patterns
    And report extraction pattern statistics

  Scenario: Handle extraction conflicts across pages
    Given conflicting information across related pages
    When aggregating extraction results
    Then conflicts should be detected and reported
    And resolution should follow these rules:
      | rule_priority | description                                    |
      | 1            | More specific page data overrides general      |
      | 2            | JSON-LD/Microdata overrides heuristic         |
      | 3            | More recent extraction overrides older         |
      | 4            | Higher confidence overrides lower              |

  Scenario: Track extraction coverage
    Given a multi-page scraping session
    When extraction is complete
    Then the system should report:
      | metric                    | description                           |
      | pages_with_structured_data| Count of pages with JSON-LD/Microdata |
      | heuristic_only_pages      | Count of pages using only heuristics  |
      | extraction_success_rate   | Percentage of pages with valid data   |
      | average_confidence        | Mean confidence across all extractions|
      | pattern_effectiveness     | Success rate of identified patterns   |