Feature: Web Scraping Engine
  As a user of RAG_Scraper
  I want reliable web scraping functionality
  So that I can extract restaurant data from websites

  Background:
    Given the RAG_Scraper web interface is running
    And I have valid restaurant URLs available for testing

  Scenario: Single URL Scraping
    Given I have entered a valid restaurant URL "https://example.com"
    And I have left the output directory empty to use Downloads folder
    And I have set file mode to "Single file for all restaurants"
    When I click "Start Scraping"
    Then a progress bar should appear and update
    And I should see "Scraping Completed Successfully!" message
    And file paths should be listed in the results
    And actual files should be created in the Downloads folder

  Scenario: Multiple URL Batch Processing
    Given I have entered multiple valid restaurant URLs:
      | url                          |
      | https://restaurant1.com      |
      | https://restaurant2.com      |
      | https://restaurant3.com      |
    And I have set a custom output directory
    And I have set file mode to "Separate file per restaurant"
    When I click "Start Scraping"
    Then the progress indicator should show URL count and percentage
    And the current URL being processed should be displayed
    And time estimates should appear after the first URL
    And multiple files should be generated (one per restaurant)

  Scenario: Progress Monitoring During Scraping
    Given I have entered 3 restaurant URLs for scraping
    When I start the scraping process
    Then the progress bar should fill from 0% to 100%
    And the current URL being processed should be shown
    And time estimates should update dynamically
    And memory usage information should be displayed

  Scenario: Single File Mode Data Aggregation
    Given I have multiple restaurant URLs
    And I have selected "Single file for all restaurants" mode
    When I complete the scraping process
    Then all restaurant data should be combined into one file
    And the file should contain data from all successfully scraped URLs
    And failed URLs should not prevent file generation

  Scenario: Individual File Mode Data Separation
    Given I have multiple restaurant URLs
    And I have selected "Separate file per restaurant" mode
    When I complete the scraping process
    Then each successfully scraped restaurant should have its own file
    And file names should identify the source restaurant
    And failed URLs should not affect other restaurant files

  Scenario: Error Handling During Scraping
    Given I have a mix of valid and invalid restaurant URLs:
      | url                          | expected_result |
      | https://valid-restaurant.com | success        |
      | https://invalid-url.fake     | failure        |
      | https://another-valid.com    | success        |
    When I start the scraping process
    Then the process should continue with valid URLs
    And failed URLs should be reported separately
    And partial success results should be returned
    And files should be generated for successful extractions only

  Scenario: Custom Output Directory Configuration
    Given I have specified a custom output directory "/path/to/custom/folder"
    And the directory exists and is writable
    When I complete the scraping process
    Then files should be created in the specified custom location
    And the directory path should be validated before scraping
    And file permissions should be checked

  Scenario: Progress Callback Integration
    Given I have started a scraping process with multiple URLs
    When the scraping is in progress
    Then progress callbacks should fire regularly
    And progress percentage should increase incrementally
    And current operation details should be provided
    And estimated time remaining should be calculated

  Scenario: Memory Management During Large Batches
    Given I have a large batch of restaurant URLs (10+ URLs)
    When I process the entire batch
    Then memory usage should remain within reasonable limits
    And memory usage should be monitored and reported
    And the system should not experience memory leaks
    And performance should remain stable throughout the process