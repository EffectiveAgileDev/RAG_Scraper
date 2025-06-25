Feature: Page Queue Status and Remaining Count Display
  As a user monitoring multi-page scraping jobs
  I want to see detailed page queue status and remaining count information
  So that I can understand the progress and plan accordingly

  Background:
    Given I am on the RAG_Scraper web interface
    And I have multi-page scraping mode enabled
    
  Scenario: Display initial queue status
    Given I have started a scraping job with 10 discovered pages
    When I view the queue status display
    Then I should see "Pages in Queue: 10" 
    And I should see "Pages Remaining: 10"
    And I should see "Pages Completed: 0"
    And I should see "Currently Processing: 0"
    
  Scenario: Queue status updates as pages are processed
    Given I have a scraping job with 8 total pages
    And 3 pages have been completed
    And 1 page is currently being processed
    When I view the updated queue status
    Then I should see "Pages in Queue: 4"
    And I should see "Pages Remaining: 5"
    And I should see "Pages Completed: 3"
    And I should see "Currently Processing: 1"
    
  Scenario: Queue empties as job completes
    Given I have a scraping job with 5 total pages
    And 4 pages have been completed
    And 1 page is currently being processed
    When the last page completes processing
    Then I should see "Pages in Queue: 0"
    And I should see "Pages Remaining: 0"
    And I should see "Pages Completed: 5"
    And I should see "Currently Processing: 0"
    
  Scenario: Queue grows with page discovery
    Given I have a scraping job with 5 initial pages
    And 2 pages have been completed
    When 3 new pages are discovered during processing
    Then I should see "Pages in Queue: 6" 
    And I should see "Pages Remaining: 6"
    And I should see total pages increased to 8
    And I should see a "New pages discovered: 3" notification
    
  Scenario: Failed pages impact queue calculations
    Given I have a scraping job with 6 total pages
    And 2 pages have been completed
    And 1 page has failed processing
    When I view the queue status
    Then I should see "Pages in Queue: 3"
    And I should see "Pages Remaining: 3"
    And I should see "Pages Completed: 2"
    And I should see failed page excluded from processing queue
    
  Scenario: Queue status with concurrent processing
    Given I have enabled concurrent processing with limit 3
    And I have a scraping job with 12 total pages
    And 4 pages have been completed
    And 3 pages are currently being processed concurrently
    When I view the queue status
    Then I should see "Pages in Queue: 5"
    And I should see "Pages Remaining: 8"
    And I should see "Currently Processing: 3"
    And I should see concurrent processing indicator
    
  Scenario: Visual queue progress indicators
    Given I have a scraping job in progress
    When I view the queue status display
    Then I should see a visual progress bar for overall completion
    And I should see color-coded status indicators
    And completed pages should show green indicators
    And queued pages should show amber indicators
    And failed pages should show red indicators
    
  Scenario: Queue status persistence across page refreshes
    Given I have a scraping job with queue status displayed
    When I refresh the page during active scraping
    Then the queue status should be restored accurately
    And all counters should reflect the current state
    And no data should be lost from the refresh