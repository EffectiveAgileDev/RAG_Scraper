Feature: Progress Indication During Scraping
  As a RAG system administrator
  I want to see real-time progress during scraping
  So that I know the system is working and can estimate completion time

  Background:
    Given the RAG_Scraper web interface is running
    And I have access to the localhost application

  Scenario: Progress indication for single URL processing
    Given I have a valid restaurant website URL "http://tonysitalian.com"
    When I submit the URL for scraping
    Then I should see an initial progress message
    And I should see "Processing http://tonysitalian.com" message
    And I should see progress percentage updates
    And I should see a completion message when finished
    And the progress should go from 0% to 100%

  Scenario: Progress indication for multiple URL batch
    Given I have multiple valid restaurant URLs:
      | http://tonysitalian.com    |
      | http://mariascantina.com   |
      | http://joescoffee.com      |
    When I submit the URLs for batch scraping
    Then I should see overall batch progress
    And I should see current URL being processed
    And I should see "Processing 1 of 3: http://tonysitalian.com"
    And I should see "Processing 2 of 3: http://mariascantina.com"
    And I should see "Processing 3 of 3: http://joescoffee.com"
    And I should see overall completion percentage
    And I should see final completion message with statistics

  Scenario: Progress indication during network delays
    Given I have a valid but slow-responding URL "http://slow-restaurant.com"
    When I submit the URL for scraping
    Then I should see "Connecting to http://slow-restaurant.com" message
    And I should see "Waiting for response..." message
    And I should see periodic "Still processing..." updates
    And the progress indicator should remain active during delays

  Scenario: Progress indication during scraping errors
    Given I have a valid but unreachable URL "http://nonexistent-restaurant.com"
    When I submit the URL for scraping
    Then I should see "Processing http://nonexistent-restaurant.com" message
    And I should see "Error connecting to website" message
    And I should see "Skipping http://nonexistent-restaurant.com due to error"
    And the overall progress should continue to next URL if in batch

  Scenario: Progress indication with estimated time remaining
    Given I have multiple restaurant URLs for time estimation:
      | http://restaurant1.com |
      | http://restaurant2.com |
      | http://restaurant3.com |
      | http://restaurant4.com |
      | http://restaurant5.com |
    When I submit the URLs for batch scraping
    Then I should see "Estimated time remaining: calculating..." initially
    And after processing first URL I should see time estimate
    And the time estimate should update as processing continues
    And the estimate should become more accurate over time

  Scenario: Progress indication for multi-page website discovery
    Given I have a restaurant URL with multiple pages "http://multi-page-restaurant.com"
    And the website has menu, contact, and about pages
    When I submit the URL for scraping
    Then I should see "Discovering pages for http://multi-page-restaurant.com"
    And I should see "Found 4 pages to process"
    And I should see "Processing page 1 of 4: Home page"
    And I should see "Processing page 2 of 4: Menu page"
    And I should see "Processing page 3 of 4: Contact page"
    And I should see "Processing page 4 of 4: About page"
    And I should see "Aggregating data from 4 pages"

  Scenario: Progress indication persistence during long operations
    Given I have a large batch of restaurant URLs (20 URLs)
    When I submit the URLs for batch scraping
    Then the progress indicator should remain visible throughout
    And progress updates should appear at least every 5 seconds
    And the interface should remain responsive
    And I should be able to see current operation status
    And the progress should never go backwards