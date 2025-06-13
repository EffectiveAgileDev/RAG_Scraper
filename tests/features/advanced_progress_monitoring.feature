# Advanced Progress Monitoring Feature
# Following BDD with TDD Red-Green-Refactor methodology
# Sprint 7A: System Hardening and Production Readiness

Feature: Advanced Progress Monitoring
  As a RAG system administrator
  I want enhanced real-time progress monitoring with detailed feedback
  So that I can track scraping operations and handle issues proactively

  Background:
    Given the RAG_Scraper web interface is running
    And I have access to the advanced progress monitoring system
    And the monitoring system is initialized

  Scenario: Real-time progress indicators with current URL display
    Given I have 5 valid restaurant website URLs for monitoring testing
    When I start the scraping process with advanced monitoring enabled
    Then I should see real-time progress updates every 2 seconds
    And I should see the current URL being processed displayed prominently
    And the progress percentage should update dynamically
    And the progress bar should reflect the current completion status

  Scenario: Multi-page website progress tracking
    Given I have a restaurant website URL with 4 linked pages
    And I enable multi-page scraping with advanced monitoring
    When I start the scraping process
    Then I should see page-by-page progress within the multi-page site
    And I should receive notifications when starting new pages within the same website
    And the progress should show "Processing page 2 of 4" style indicators
    And each page completion should trigger a progress update notification

  Scenario: Dynamic time estimation with real-time updates
    Given I have 10 restaurant URLs for time estimation testing
    And advanced progress monitoring is enabled
    When I start the batch scraping process
    Then I should see an estimated time remaining calculation
    And the time estimate should update dynamically as scraping progresses
    And the estimation should become more accurate after processing 3+ URLs
    And the time remaining should be displayed in minutes and seconds format

  Scenario: Real-time error notifications with continue/stop options
    Given I have a mix of valid and invalid restaurant URLs
    And advanced error monitoring is enabled
    When I start the scraping process and encounter errors
    Then I should receive real-time error notifications for failed URLs
    And each error notification should include the specific error type
    And I should be presented with "Continue" and "Stop" options for error handling
    And choosing "Continue" should proceed with remaining URLs
    And choosing "Stop" should halt the entire scraping process

  Scenario: Memory usage monitoring during large batches
    Given I have 25 restaurant URLs for memory monitoring testing
    And advanced resource monitoring is enabled
    When I start the large batch scraping process
    Then I should see real-time memory usage indicators
    And memory usage should be displayed in MB with updates every 5 seconds
    And I should receive warnings if memory usage exceeds 400MB
    And the system should provide memory optimization suggestions if needed

  Scenario: Current operation status display
    Given I have restaurant URLs with varying complexity
    And detailed operation monitoring is enabled
    When I start the scraping process with operation tracking
    Then I should see the current operation being performed
    And operations should include "Analyzing page structure", "Extracting data", "Processing menu items"
    And each operation should have an estimated duration indicator
    And operation transitions should be clearly indicated in the UI

  Scenario: Batch processing progress with URL queue display
    Given I have 8 restaurant URLs in a batch processing queue
    And batch progress monitoring is enabled
    When I start the batch scraping process
    Then I should see the total queue status "Processing 3 of 8 URLs"
    And completed URLs should be marked with success/failure indicators
    And remaining URLs should be shown in the processing queue
    And I should be able to see which URLs are pending, processing, completed, or failed

  Scenario: Enhanced progress monitoring persistence across sessions
    Given I am running a long batch scraping process
    And advanced monitoring is tracking the session
    When I accidentally close or refresh the browser
    And I return to the scraping interface
    Then the progress monitoring should restore the current session state
    And I should see the current progress, completed URLs, and remaining work
    And the session should continue from where it was interrupted
    And all monitoring data should be preserved

  Scenario: Multi-threaded operation monitoring
    Given I have 15 restaurant URLs for concurrent processing testing
    And multi-threaded scraping with monitoring is enabled
    When I start the concurrent scraping process
    Then I should see monitoring for multiple simultaneous operations
    And each concurrent thread should have its own progress indicator
    And the overall progress should aggregate individual thread progress
    And I should see which URLs are being processed simultaneously

  Scenario: Performance metrics and optimization suggestions
    Given I have completed several scraping sessions with monitoring data
    And performance analysis is enabled
    When I view the advanced monitoring dashboard
    Then I should see average processing time per URL
    And I should see memory usage patterns and optimization opportunities
    And the system should suggest optimal batch sizes for my hardware
    And I should see error rate statistics and common failure patterns

  Scenario: Monitoring data export and session logging
    Given I have completed a scraping session with advanced monitoring
    And monitoring data logging is enabled
    When I access the monitoring session data
    Then I should be able to export monitoring data as JSON
    And the export should include timing data, memory usage, and error logs
    And session logs should be available for troubleshooting
    And historical monitoring data should be accessible for analysis