Feature: Comprehensive RAG Scraper Feature Showcase
  As a user of the RAG Scraper application
  I want to demonstrate all current features including progress visualization and multi-page scraping
  So that I can validate the complete functionality of the system

  Background:
    Given the RAG Scraper web interface is running
    And I have access to test restaurant URLs

  Scenario: Single-page scraping with basic progress tracking
    Given I am on the RAG Scraper home page
    When I enter "https://mettavern.com/" in the URL input field
    And I select "Single Page" scraping mode
    And I select "Text" as the output format
    And I click the "Start Scraping" button
    Then I should see progress updates in real-time
    And I should see "Processing" status messages
    And I should see a progress percentage indicator
    And I should eventually see "EXTRACTION_COMPLETE" status
    And I should see successful extraction results
    And I should see the generated text file available for download

  Scenario: Multi-page scraping with enhanced progress visualization
    Given I am on the RAG Scraper home page
    When I enter "https://mettavern.com/" in the URL input field
    And I select "Multi Page" scraping mode
    And I configure multi-page settings:
      | Setting | Value |
      | Max Pages | 10 |
      | Crawl Depth | 2 |
      | Rate Limit | 1000ms |
    And I select "Text" as the output format
    And I click the "Start Scraping" button
    Then I should see enhanced progress visualization features:
      | Feature | Description |
      | Current Page Display | Shows the page currently being processed |
      | Page Queue Status | Displays remaining pages in queue |
      | Real-time Progress | Updates progress percentage as pages complete |
      | Processing Time | Shows time taken for each page |
      | Page Discovery Status | Shows when new pages are discovered |
    And I should see multiple pages being processed
    And I should see page relationship information
    And I should see aggregated data from multiple pages
    And I should eventually see "EXTRACTION_COMPLETE" with multiple targets processed
    And I should see detailed results showing all processed pages

  Scenario: Batch processing multiple URLs with progress tracking
    Given I am on the RAG Scraper home page
    When I enter multiple URLs:
      | URL |
      | https://mettavern.com/ |
      | https://example-restaurant.com/ |
    And I select "Single Page" scraping mode
    And I select "Text" as the output format
    And I click the "Start Scraping" button
    Then I should see batch processing progress
    And I should see individual URL processing status
    And I should see overall progress across all URLs
    And I should see results for each successfully processed URL
    And I should see any failed URLs clearly marked

  Scenario: Advanced options configuration and testing
    Given I am on the RAG Scraper home page
    When I expand the "Advanced Options" section
    Then I should see configuration options for:
      | Option | Type |
      | Page Discovery | Toggle |
      | Custom Timeout | Input Field |
      | Concurrent Requests | Slider |
      | Rate Limiting | Input Field |
    When I configure advanced options:
      | Option | Value |
      | Page Discovery | Enabled |
      | Custom Timeout | 45 seconds |
      | Concurrent Requests | 2 |
      | Rate Limiting | 2000ms |
    And I enter "https://mettavern.com/" in the URL input field
    And I select "Multi Page" scraping mode
    And I click the "Start Scraping" button
    Then I should see the custom configuration being applied
    And I should see slower processing due to increased rate limiting
    And I should see reduced concurrent processing

  Scenario: Real-time progress visualization features
    Given I am on the RAG Scraper home page
    When I start a multi-page scraping operation on "https://mettavern.com/"
    Then I should see real-time progress elements:
      | Element | Behavior |
      | Progress Bar | Updates smoothly as pages complete |
      | Current Page Indicator | Shows exact page being processed |
      | Queue Counter | Shows remaining pages to process |
      | Time Estimates | Shows estimated completion time |
      | Page Processing Status | Shows success/failure per page |
      | Memory Usage | Shows current memory consumption |
    And the progress visualization should update without page refresh
    And the progress should be accurate and reflect actual processing

  Scenario: Enhanced results display with page relationships
    Given I have completed a multi-page scraping operation
    When I view the results section
    Then I should see enhanced results display showing:
      | Information | Details |
      | Pages Processed | Total count and list of URLs |
      | Success/Failure Status | Per-page status indicators |
      | Processing Time | Time taken for each page |
      | Page Relationships | Parent-child page relationships |
      | Discovery Method | How each page was found |
      | Data Aggregation | Combined data from all pages |
    And I should be able to expand/collapse page details
    And I should see clear visual indicators for page status
    And I should see the relationship hierarchy between pages

  Scenario: File generation with multiple formats
    Given I have successfully scraped restaurant data
    When I configure file generation options:
      | Format | Output |
      | Text | Single text file |
      | PDF | PDF document |
      | Both | Text and PDF |
    And I generate files for each format
    Then I should see files generated successfully
    And I should be able to download each file format
    And the files should contain properly formatted restaurant data
    And PDF files should have proper formatting and layout

  Scenario: Error handling and recovery
    Given I am testing error scenarios
    When I enter an invalid URL "https://nonexistent-restaurant-site.invalid/"
    And I start scraping
    Then I should see appropriate error messages
    And I should see the URL marked as failed
    And I should see specific error details
    And the system should continue processing other valid URLs
    And I should see error recovery suggestions

  Scenario: Memory management during large operations
    Given I am processing multiple URLs with multi-page scraping
    When I monitor system resources during processing
    Then I should see memory usage tracking
    And I should see memory usage stay within reasonable limits
    And I should see memory cleanup after processing completion
    And I should not see memory leaks or excessive usage

  Scenario: Complete workflow demonstration
    Given I want to demonstrate the complete RAG Scraper workflow
    When I perform a complete scraping session:
      | Step | Action |
      | 1 | Configure URLs and scraping mode |
      | 2 | Set advanced options |
      | 3 | Start scraping with progress monitoring |
      | 4 | Monitor real-time progress updates |
      | 5 | View detailed results |
      | 6 | Generate output files |
      | 7 | Download generated files |
    Then each step should complete successfully
    And I should have a complete audit trail of the operation
    And I should have usable output files with restaurant data
    And the entire process should demonstrate professional-grade functionality