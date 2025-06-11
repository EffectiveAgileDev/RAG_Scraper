Feature: End-to-End Integration
  As a user of RAG_Scraper
  I want seamless integration between all system components
  So that I can complete the entire workflow from URL input to file generation in one process

  Background:
    Given the RAG_Scraper web interface is running
    And all system components are properly initialized

  Scenario: Complete Workflow Validation
    Given I start with an empty Downloads folder
    And I have a valid restaurant URL "https://example-restaurant.com"
    When I enter the URL and complete the full scraping process
    Then files should appear automatically in the Downloads folder after scraping
    And I should not need a separate file generation step
    And the API response should include actual file paths
    And the files should contain extracted restaurant data

  Scenario: Single API Call Complete Workflow
    Given I have restaurant URLs ready for processing
    When I make a single API call to "/api/scrape" with file format specified
    Then the scraping and file generation should complete in one operation
    And the response should contain both scraping results and generated file paths
    And no additional API calls should be required
    And the workflow should be seamless for the user

  Scenario: Error Handling and Recovery in Complete Workflow
    Given I have a mix of valid and invalid restaurant URLs
    When I start the complete scraping and file generation process
    Then the process should continue with valid URLs
    And failed URLs should be reported separately
    And partial success results should be returned
    And files should be generated for successful extractions only
    And the system should recover gracefully from individual failures

  Scenario: Custom Directory Creation and Usage
    Given I specify a custom output directory path that doesn't exist
    When I start the scraping process with automatic file generation
    Then the system should create the directory if possible
    And directory permissions should be validated
    And files should be created in the custom location
    And the complete workflow should succeed with the custom path

  Scenario: Multi-Format Integration Workflow
    Given I have restaurant data to process
    And I specify "both" for file format (text and PDF)
    When I execute the complete workflow
    Then both text and PDF files should be generated automatically
    And both file paths should be returned in the response
    And both files should contain the same restaurant data
    And the entire process should complete in a single operation

  Scenario: Progress Tracking Through Complete Workflow
    Given I have multiple restaurant URLs for processing
    When I start the complete workflow
    Then progress should be tracked from URL validation through file generation
    And progress indicators should update throughout the entire process
    And users should see current operation status (scraping, file generation, etc.)
    And estimated time should account for both scraping and file generation

  Scenario: Configuration Persistence Across Workflow
    Given I have configured specific preferences for file generation
    And I have set custom output directories and formats
    When I execute the complete workflow multiple times
    Then my configuration should be preserved across operations
    And settings should be applied consistently
    And I should not need to reconfigure for each operation

  Scenario: Workflow Robustness Under Load
    Given I have a large batch of restaurant URLs (15-20 URLs)
    When I execute the complete workflow for the entire batch
    Then all components should work together efficiently
    And memory usage should remain reasonable throughout
    And file generation should succeed for all scraped data
    And the system should not experience performance degradation

  Scenario: API Response Consistency in Complete Workflow
    Given I execute the complete workflow through the web interface
    When the process completes successfully
    Then the API response should contain accurate processing statistics
    And actual file paths should be returned (not descriptions)
    And success/failure counts should be accurate
    And any warnings or errors should be clearly communicated

  Scenario: File System Integration Verification
    Given I complete the full workflow with file generation
    When I check the file system afterwards
    Then all promised files should actually exist
    And file contents should match the scraped data
    And file permissions should be appropriate
    And files should be accessible by the user

  Scenario: Workflow State Management
    Given I start a workflow operation
    When the process is running
    Then the system should maintain proper state throughout
    And concurrent operations should be handled appropriately
    And system resources should be managed efficiently
    And cleanup should occur properly after completion

  Scenario: User Experience Validation
    Given I am using the web interface as an end user
    When I complete the entire workflow from start to finish
    Then the experience should be intuitive and seamless
    And feedback should be provided at each step
    And the final result should meet user expectations
    And no technical knowledge should be required for basic operations