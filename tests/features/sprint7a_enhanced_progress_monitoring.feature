Feature: Enhanced Progress Monitoring and User Feedback System
  As a RAG system administrator
  I want detailed real-time progress monitoring with multi-page notifications
  So that I can track scraping progress and respond to issues promptly

  Background:
    Given the RAG_Scraper web interface is running
    And the enhanced progress monitoring system is active

  Scenario: Real-time progress display for single URL processing
    Given I have a single restaurant website URL
    When I start the scraping process
    Then I should see the current URL being processed displayed
    And I should see real-time status updates during data extraction
    And I should see field extraction progress indicators
    And the progress display should update every 2 seconds or less
    And I should see completion status when processing finishes

  Scenario: Multi-page website progress monitoring with page notifications
    Given I have a restaurant website URL with multiple relevant pages
    When I start the scraping process with multi-page navigation enabled
    Then I should see notification when starting to process the main page
    And I should see notifications when new pages are discovered within the same website
    And I should see "Processing page 2 of [website]" style notifications
    And I should see page-by-page progress within the multi-page site
    And I should see consolidation notification when aggregating data from multiple pages

  Scenario: Batch processing progress monitoring with detailed feedback
    Given I have 10 restaurant website URLs for batch processing
    When I start the batch scraping process
    Then I should see overall batch progress (e.g., "Processing 3 of 10 URLs")
    And I should see current URL being processed
    And I should see individual URL progress status
    And I should see estimated time remaining with dynamic updates
    And progress should continue updating even when individual URLs fail

  Scenario: Progress monitoring with error notifications and continue options
    Given I have restaurant URLs that include some problematic sites
    When I execute batch scraping with progress monitoring
    Then I should see real-time error notifications when issues occur
    And I should be presented with continue/stop options for errors
    And I should see clear error descriptions without technical jargon
    And I should be able to continue processing remaining URLs after errors
    And error notifications should not interfere with progress display

  Scenario: Enhanced progress feedback for field extraction process
    Given I have restaurant URLs with comprehensive data extraction enabled
    When I start scraping with full field extraction
    Then I should see progress indicators for different extraction phases
    And I should see notifications like "Extracting core fields", "Processing extended fields"
    And I should see field category completion indicators
    And I should see total fields extracted count in real-time
    And field extraction progress should be distinct from page loading progress

  Scenario: Multi-page progress with nested progress indicators
    Given I have a restaurant website with 5 discoverable pages
    When I process the multi-page website
    Then I should see overall website progress (e.g., "Website 1 of 3")
    And I should see individual page progress within the website (e.g., "Page 2 of 5")
    And I should see nested progress bars or indicators for both levels
    And I should see page-specific status messages
    And I should see data aggregation progress when combining page results

  Scenario: Progress monitoring performance and responsiveness
    Given I have a large batch of 50 restaurant URLs
    When I execute batch processing with full progress monitoring
    Then progress updates should display within 1 second of processing events
    And the progress interface should remain responsive during heavy processing
    And progress monitoring should not significantly impact scraping performance
    And memory usage for progress tracking should be minimal
    And progress display should not cause UI freezing or delays

  Scenario: Progress monitoring with export format generation feedback
    Given I have completed data extraction for multiple restaurants
    And I have selected JSON export format
    When the system begins generating the export file
    Then I should see export generation progress indicators
    And I should see format-specific generation status messages
    And I should see file size and generation progress updates
    And I should receive notification when export file is ready
    And I should see direct link to the generated file upon completion

  Scenario: Estimated time remaining calculation and accuracy
    Given I start batch processing of 20 restaurant URLs
    When progress monitoring calculates estimated time remaining
    Then the initial estimate should appear within 30 seconds of starting
    And the estimate should become more accurate as processing continues
    And the estimate should update dynamically based on actual processing speed
    And the estimate should account for different processing times per website type
    And the estimate should remain visible and easily readable

  Scenario: Progress monitoring state persistence during interruptions
    Given I have batch processing in progress with progress monitoring active
    When a temporary network interruption occurs
    Then progress monitoring should maintain state information
    And I should see appropriate "Retrying connection" status messages
    And progress should resume correctly after connection restoration
    And previously completed processing should not be lost or repeated
    And I should receive clear feedback about interruption and recovery status