Feature: Multi-Strategy Data Extraction
  As a RAG system user
  I want restaurant data extracted using multiple strategies
  So that I get complete information regardless of website structure

  Background:
    Given I have initialized the multi-strategy data extractor
    And I have access to sample restaurant HTML pages

  Scenario: JSON-LD structured data extraction
    Given I have a restaurant website with JSON-LD structured data
    And the JSON-LD contains restaurant schema
    When I extract data using the JSON-LD strategy
    Then I should get the restaurant name from JSON-LD
    And I should get the address from JSON-LD 
    And I should get the phone number from JSON-LD
    And I should get the operating hours from JSON-LD
    And I should get the price range from JSON-LD
    And the extraction confidence should be "high"

  Scenario: Microdata structured data extraction
    Given I have a restaurant website with microdata markup
    And the microdata uses schema.org restaurant vocabulary
    When I extract data using the microdata strategy
    Then I should get the restaurant name from microdata
    And I should get the address from microdata
    And I should get the phone number from microdata
    And I should get the cuisine type from microdata
    And I should get the menu items from microdata
    And the extraction confidence should be "high"

  Scenario: Heuristic pattern extraction fallback
    Given I have a restaurant website with no structured data
    And the website has typical restaurant information patterns
    When I extract data using the heuristic strategy
    Then I should get the restaurant name using text patterns
    And I should get the address using location patterns
    And I should get the phone number using regex patterns
    And I should get the hours using time patterns
    And I should get menu items using section patterns
    And the extraction confidence should be "medium"

  Scenario: Combined multi-strategy extraction
    Given I have a restaurant website with partial structured data
    And some information is only available through heuristic patterns
    When I extract data using all strategies
    Then I should get complete restaurant information
    And structured data should take priority over heuristic data
    And missing structured data should be filled by heuristic patterns
    And the final result should be merged and validated

  Scenario: Strategy priority and conflict resolution
    Given I have a restaurant website with conflicting data sources
    And JSON-LD says the name is "Tony's Italian Restaurant"
    And heuristic patterns find the name as "Tony's Italian"
    When I extract data using all strategies
    Then the JSON-LD data should take highest priority
    And the final restaurant name should be "Tony's Italian Restaurant"
    And confidence scores should reflect data source quality

  Scenario: Menu item extraction across strategies
    Given I have a restaurant website with menu information
    And JSON-LD contains some menu items
    And heuristic patterns find additional menu items
    When I extract menu data using all strategies
    Then I should get menu items from both sources
    And menu items should be categorized by section
    And duplicate menu items should be deduplicated
    And menu formatting should be consistent

  Scenario: Address normalization across strategies
    Given I have a restaurant website with address information
    And different strategies extract address in different formats
    When I extract address data using all strategies
    Then the address should be normalized to standard format
    And the format should be "Street, City, State ZIP"
    And incomplete addresses should be marked as partial
    And confidence should reflect completeness

  Scenario: Phone number extraction and formatting
    Given I have a restaurant website with phone information
    And phone numbers appear in various formats
    When I extract phone data using all strategies
    Then phone numbers should be normalized to standard format
    And the format should be "(XXX) XXX-XXXX" or "XXX-XXX-XXXX"
    And invalid phone numbers should be filtered out
    And multiple phone numbers should be preserved

  Scenario: Hours extraction and standardization
    Given I have a restaurant website with operating hours
    And hours are formatted differently across the site
    When I extract hours data using all strategies
    Then hours should be normalized to consistent format
    And the format should be "Day-Day Time-Time"
    And special hours like "Closed" should be preserved
    And holiday hours should be identified separately

  Scenario: Extraction failure graceful handling
    Given I have a restaurant website with corrupted HTML
    And some extraction strategies fail with errors
    When I extract data using all strategies
    Then successful strategies should still return data
    And failed strategies should not crash the extraction
    And error information should be logged for debugging
    And partial results should be returned with confidence scores

  Scenario: Performance optimization for large pages
    Given I have a restaurant website with large HTML content
    And the page contains many irrelevant sections
    When I extract data using all strategies
    Then extraction should complete within reasonable time
    And memory usage should remain within acceptable limits
    And only relevant sections should be processed intensively
    And progress should be tracked for user feedback

  Scenario: Multi-page website coordination
    Given I have a restaurant website with menu on separate page
    And the main page has contact information
    And the menu page has detailed food items
    When I extract data from multiple pages
    Then information should be aggregated across pages
    And duplicate information should be deduplicated
    And page source should be tracked for each data field
    And the final result should be comprehensive