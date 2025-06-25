Feature: Enhanced Page Status Display
  As a user scraping restaurant websites
  I want to see detailed success/failure status for each page
  So that I can understand what happened during the scraping process

  Background:
    Given I am on the RAG_Scraper web interface
    And I have multi-page scraping enabled

  Scenario: Display success status with details for successful pages
    Given I have successfully scraped a multi-page restaurant site
    When I view the results
    Then I should see success indicators for successful pages
    And each successful page should show "✓ SUCCESS" status
    And each successful page should display the HTTP status code
    And each successful page should show data extracted count
    And each successful page should display content size information

  Scenario: Display failure status with details for failed pages
    Given I have attempted to scrape a site with some failed pages
    When I view the results
    Then I should see failure indicators for failed pages
    And each failed page should show "✗ FAILED" status
    And each failed page should display the error message
    And each failed page should show the HTTP status code if available
    And each failed page should indicate the failure reason

  Scenario: Display timeout status for pages that timed out
    Given I have attempted to scrape pages that timed out
    When I view the results
    Then I should see timeout indicators for timed out pages
    And each timed out page should show "⏰ TIMEOUT" status
    And each timed out page should display the timeout duration
    And each timed out page should show partial data if any was extracted

  Scenario: Display redirect status for redirected pages
    Given I have scraped pages that were redirected
    When I view the results
    Then I should see redirect indicators for redirected pages
    And each redirected page should show "↪ REDIRECTED" status
    And each redirected page should display the final URL
    And each redirected page should show the redirect chain if multiple

  Scenario: Show detailed status tooltips on hover
    Given I have results with various page statuses
    When I hover over a page status indicator
    Then I should see a tooltip with detailed information
    And the tooltip should include timestamp information
    And the tooltip should show extraction method used
    And the tooltip should display response headers if available

  Scenario: Filter results by page status
    Given I have results with mixed success and failure statuses
    When I use the status filter controls
    Then I should be able to show only successful pages
    And I should be able to show only failed pages
    And I should be able to show all pages regardless of status

  Scenario: Export status report for failed pages
    Given I have results with some failed pages
    When I click the "Export Failed Pages Report" button
    Then I should receive a detailed report of all failures
    And the report should include URLs, error messages, and timestamps
    And the report should be downloadable as a text file

  Scenario: Retry failed pages functionality
    Given I have results with some failed pages
    When I click the "Retry Failed Pages" button
    Then the system should attempt to re-scrape only the failed pages
    And I should see updated progress for the retry attempts
    And successful retries should update the status display