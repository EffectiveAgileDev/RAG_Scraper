Feature: Industry Knowledge Database
  As a user of the RAG Scraper
  I want industry-specific knowledge databases to map customer terms to website terms
  So that I can extract more relevant data based on industry-specific vocabulary and concepts

  Background:
    Given the system has industry knowledge databases configured
    And I am on the RAG Scraper homepage

  Scenario: Load restaurant industry categories and terms
    Given I have selected "Restaurant" as my industry
    When the system loads the restaurant knowledge database
    Then I should see the following restaurant categories available:
      | Category        | Description                    |
      | Menu Items      | Food and beverage offerings    |
      | Cuisine Type    | Style of cooking               |
      | Dining Options  | Service and seating types      |
      | Amenities       | Restaurant facilities          |
      | Hours           | Operating times                |
      | Location        | Address and contact info       |
    And each category should have associated website terms
    And each category should have customer query synonyms

  Scenario: Map customer terms to website terms for restaurants
    Given I have selected "Restaurant" as my industry
    And the restaurant knowledge database is loaded
    When I search for customer term "vegetarian options"
    Then the system should map it to website terms:
      | Website Term    | Confidence |
      | vegan           | 0.9        |
      | vegetarian      | 1.0        |
      | plant-based     | 0.8        |
      | meat-free       | 0.7        |
    And the system should categorize it under "Menu Items"
    And the confidence scores should reflect term relevance

  Scenario: Handle unknown terms gracefully
    Given I have selected "Restaurant" as my industry
    And the restaurant knowledge database is loaded
    When I search for an unknown term "quantum dining"
    Then the system should return an empty mapping result
    And the system should log the unknown term for future analysis
    And the system should suggest fallback to generic extraction
    And no error should be thrown

  Scenario: Support custom term additions to knowledge database
    Given I have selected "Restaurant" as my industry
    And the restaurant knowledge database is loaded
    When I add a custom mapping from "gluten-free" to category "Menu Items"
    And I specify the website terms: "gluten-free, celiac-friendly, wheat-free"
    Then the new mapping should be stored in the database
    And future searches for "gluten-free" should return the custom mapping
    And the mapping should persist across sessions
    And the confidence score should be marked as user-defined

  Scenario: Load medical industry categories and terms
    Given I have selected "Medical" as my industry
    When the system loads the medical knowledge database
    Then I should see the following medical categories available:
      | Category        | Description                      |
      | Services        | Medical procedures and treatments|
      | Specialties     | Medical specialization areas     |
      | Insurance       | Accepted insurance providers     |
      | Staff           | Doctor and staff information     |
      | Facilities      | Medical equipment and amenities  |
      | Appointments    | Scheduling and availability      |
    And each category should have medical-specific website terms
    And each category should have patient query synonyms

  Scenario: Cross-industry term validation
    Given I have selected "Real Estate" as my industry
    And the real estate knowledge database is loaded
    When I search for a restaurant term "menu items"
    Then the system should return an empty mapping result
    And the system should suggest checking the correct industry selection
    And no cross-contamination between industry databases should occur

  Scenario: Database schema validation and integrity
    Given I have selected "Restaurant" as my industry
    When the system validates the knowledge database schema
    Then all required fields should be present:
      | Field           | Type   | Required |
      | category        | string | yes      |
      | customer_terms  | array  | yes      |
      | website_terms   | array  | yes      |
      | confidence      | float  | yes      |
      | synonyms        | array  | no       |
    And all confidence scores should be between 0.0 and 1.0
    And all arrays should contain at least one term
    And no duplicate entries should exist within a category

  Scenario: Fuzzy matching for similar terms
    Given I have selected "Restaurant" as my industry
    And the restaurant knowledge database is loaded
    When I search for a slightly misspelled term "vegitarian options"
    Then the system should use fuzzy matching to find "vegetarian options"
    And the confidence score should be adjusted for the fuzzy match
    And the system should suggest the correct spelling
    And the mapping should still return relevant website terms

  Scenario: Synonym handling and expansion
    Given I have selected "Restaurant" as my industry
    And the restaurant knowledge database is loaded
    When I search for customer term "parking"
    Then the system should expand to include synonyms:
      | Customer Term   | Synonyms                        |
      | parking         | parking lot, valet, garage      |
    And all synonyms should map to the same website terms
    And the system should return the highest confidence mapping
    And synonym relationships should be bidirectional

  Scenario: Database performance with large term sets
    Given I have selected "Restaurant" as my industry
    And the restaurant knowledge database contains 1000+ term mappings
    When I perform 50 consecutive term lookups
    Then each lookup should complete in under 100ms
    And memory usage should remain stable
    And the system should use efficient indexing
    And cache frequently accessed terms