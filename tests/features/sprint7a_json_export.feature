Feature: JSON Export Format and Comprehensive Field Selection
  As a RAG system administrator
  I want to export scraped restaurant data in JSON format with comprehensive field selection
  So that I can integrate structured data into various systems and choose specific data fields

  Background:
    Given the RAG_Scraper web interface is running
    And I have access to the export format selection interface

  Scenario: JSON export format selection and generation
    Given I have 3 valid restaurant website URLs with comprehensive data
    And I select "JSON only" as the export format
    When I execute the scraping process
    Then I should receive a JSON file with structured restaurant data
    And the JSON file should contain all extracted restaurant information
    And the JSON structure should be valid and properly formatted
    And the JSON file should be saved to the selected output directory

  Scenario: JSON export with comprehensive field extraction  
    Given I have a restaurant website URL with rich data content
    And I select "JSON only" as the export format
    And all field extraction options are enabled
    When I execute the scraping process
    Then the generated JSON should contain core fields: name, address, phone, hours, website
    And the JSON should contain extended fields: cuisine types, special features, parking information
    And the JSON should contain additional fields: reservation information, featured menu items, pricing specials
    And the JSON should contain contact fields: email addresses, social media links, delivery options
    And the JSON should contain descriptive fields: dietary accommodations, ambiance descriptions

  Scenario: JSON export with field selection customization
    Given I have a restaurant website URL with comprehensive data
    And I select "JSON only" as the export format
    And I configure field selection to include only core and contact fields
    When I execute the scraping process
    Then the generated JSON should contain only: name, address, phone, hours, website, email, social media
    And the JSON should not contain extended or descriptive fields
    And the JSON structure should remain valid with selected fields only

  Scenario: JSON export file structure validation
    Given I have restaurant data ready for JSON export
    When I generate a JSON export file
    Then the JSON should have a structured format with nested objects
    And the JSON should contain a "restaurants" array as the root element
    And each restaurant entry should be a properly structured object
    And field categories should be organized in logical groupings
    And the JSON should pass schema validation checks

  Scenario: JSON export with multiple restaurants
    Given I have 5 restaurant website URLs with varying data completeness
    And I select "JSON only" as the export format
    When I execute batch scraping
    Then I should receive a single JSON file containing all 5 restaurants
    And each restaurant should be represented as a separate object in the array
    And restaurants with missing fields should have null or empty values appropriately
    And the JSON structure should remain consistent across all restaurant entries

  Scenario: JSON export error handling and data integrity
    Given I have restaurant URLs with some incomplete or malformed data
    And I select "JSON only" as the export format
    When I execute the scraping process
    Then the JSON export should handle missing data gracefully
    And invalid data should be sanitized or marked appropriately
    And the JSON file should remain valid even with incomplete source data
    And error information should be logged but not included in the JSON output

  Scenario: JSON export performance and file size optimization
    Given I have 50 restaurant URLs for batch processing
    And I select "JSON only" as the export format
    When I execute large batch scraping
    Then the JSON file should be generated within acceptable time limits
    And the JSON file size should be optimized for the amount of data
    And memory usage should remain within acceptable bounds during JSON generation
    And the JSON structure should remain efficient for parsing by other systems