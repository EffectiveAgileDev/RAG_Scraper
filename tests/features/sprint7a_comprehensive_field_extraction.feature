Feature: Comprehensive Field Extraction and Selection System
  As a RAG system administrator
  I want to extract all available restaurant data fields and select which ones to include in exports
  So that I can customize output data to match specific system requirements

  Background:
    Given the RAG_Scraper web interface is running
    And the comprehensive field extraction system is active

  Scenario: Complete field extraction from restaurant website
    Given I have a restaurant website URL with rich data content
    When I execute the scraping process with full field extraction enabled
    Then the system should extract core fields: name, address, phone, hours, website
    And the system should extract extended fields: cuisine types, special features, parking information
    And the system should extract additional fields: reservation information, featured menu items, pricing specials
    And the system should extract contact fields: email addresses, social media links, delivery/takeout options
    And the system should extract descriptive fields: dietary accommodations, ambiance descriptions
    And all extracted fields should be available for export selection

  Scenario: Field extraction with varying data availability
    Given I have restaurant websites with different levels of data completeness
    When I execute batch scraping with comprehensive field extraction
    Then the system should extract all available fields from each website
    And missing fields should be marked as null or empty appropriately
    And the extraction should not fail when optional fields are unavailable
    And each restaurant should have consistent field structure regardless of data availability

  Scenario: Field selection interface for export customization
    Given I have successfully extracted comprehensive restaurant data
    And I am configuring export options
    Then I should see a field selection interface with categorized options
    And I should be able to select/deselect core fields (name, address, phone, hours, website)
    And I should be able to select/deselect extended fields (cuisine, features, parking)
    And I should be able to select/deselect additional fields (reservations, menu, pricing)
    And I should be able to select/deselect contact fields (email, social media, delivery)
    And I should be able to select/deselect descriptive fields (dietary, ambiance)

  Scenario: Custom field selection for text export
    Given I have comprehensive restaurant data extracted
    And I select "Text only" as the export format
    And I configure field selection to include only core and contact fields
    When I generate the export file
    Then the text file should contain only selected fields
    And the text format should properly display: name, address, phone, hours, website, email, social media
    And non-selected fields should not appear in the output
    And the text formatting should remain clean and readable with selected fields

  Scenario: Custom field selection for PDF export
    Given I have comprehensive restaurant data extracted
    And I select "PDF only" as the export format  
    And I configure field selection to include extended and descriptive fields only
    When I generate the export file
    Then the PDF should contain only: cuisine types, special features, parking, dietary accommodations, ambiance
    And the PDF formatting should adapt to the selected field subset
    And non-selected fields should not appear in the PDF layout
    And the PDF should maintain professional formatting with selected fields

  Scenario: Custom field selection for JSON export
    Given I have comprehensive restaurant data extracted
    And I select "JSON only" as the export format
    And I configure field selection to include all field categories
    When I generate the export file
    Then the JSON should contain nested objects for each field category
    And core fields should be in a "basic_info" section
    And extended fields should be in an "additional_details" section
    And contact fields should be in a "contact_info" section
    And descriptive fields should be in a "characteristics" section
    And the JSON structure should be consistent and properly nested

  Scenario: Field selection persistence across sessions
    Given I configure custom field selections including specific categories
    And I save my field selection preferences
    When I restart the application or refresh the interface
    Then my custom field selections should be restored
    And the interface should display my previously selected field combinations
    And the field selection preferences should persist until manually changed

  Scenario: Field extraction error handling and graceful degradation
    Given I have restaurant websites with malformed or incomplete HTML
    When I execute comprehensive field extraction
    Then the system should extract available fields without failing
    And extraction errors should be logged but not stop the process
    And partial field extraction should still allow export generation
    And users should be notified of any extraction limitations or issues

  Scenario: Field extraction performance with large datasets
    Given I have 100 restaurant URLs for batch processing
    And comprehensive field extraction is enabled for all field categories
    When I execute the large batch scraping process
    Then field extraction should complete within acceptable time limits
    And memory usage should remain stable during comprehensive extraction
    And extraction performance should not degrade significantly with additional fields
    And the system should provide progress feedback during field extraction

  Scenario: Field category validation and data integrity
    Given I have extracted comprehensive restaurant data
    When I review the extracted field categories
    Then core fields should contain only essential restaurant information
    And extended fields should contain supplementary business details
    And contact fields should contain only communication-related information
    And descriptive fields should contain only qualitative characteristics
    And there should be no field duplication across categories
    And field categorization should be logical and consistent