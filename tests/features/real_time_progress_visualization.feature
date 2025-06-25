Feature: Real-Time Progress Visualization
  As a user running multi-page scraping jobs
  I want to see current page being processed and queue status in real-time
  So that I can monitor progress and understand what the scraper is doing

  Background:
    Given I am on the RAG_Scraper web interface
    And I have multi-page scraping mode enabled
    
  Scenario: Show current page being processed
    Given I have started a multi-page scraping job
    When the scraper begins processing a page
    Then I should see the current page URL being displayed
    And I should see a "Currently Processing:" label
    And the current page should be highlighted in the progress display
    
  Scenario: Real-time progress updates
    Given I have a scraping job with 5 pages in progress
    When the scraper moves from page 1 to page 2
    Then the "Currently Processing" display should update immediately
    And the previous page should show as completed
    And the new current page should be highlighted
    
  Scenario: Display page queue status
    Given I have started a multi-page scraping job with 10 discovered pages
    When I look at the progress visualization
    Then I should see "Pages in Queue: X" display
    And I should see "Pages Completed: Y" display
    And I should see "Pages Remaining: Z" display
    And the numbers should update in real-time as pages are processed
    
  Scenario: Queue status calculations
    Given I have 10 total pages discovered
    And 3 pages have been completed
    And 1 page is currently being processed
    When I view the queue status
    Then I should see "Pages Completed: 3"
    And I should see "Pages in Queue: 6"
    And I should see "Pages Remaining: 6"
    And I should see "Currently Processing: 1"
    
  Scenario: Visual progress indicators
    Given I have a scraping job in progress
    When I view the progress visualization
    Then I should see a progress bar showing overall completion
    And I should see individual page status indicators
    And completed pages should be marked with green checkmarks
    And the current page should have a pulsing animation
    And pending pages should be marked as queued
    
  Scenario: Page processing time estimates
    Given I have processed 3 pages with average time of 2.5 seconds
    And I have 7 pages remaining in the queue
    When I view the progress visualization
    Then I should see "Estimated Time Remaining: ~17.5s"
    And the estimate should update as processing speeds change
    And I should see "Average Processing Time: 2.5s"
    
  Scenario: Error handling in progress display
    Given I have a scraping job in progress
    When a page fails to process
    Then the failed page should be marked with a red X
    And the queue count should adjust accordingly
    And processing should continue with the next page
    And the current page display should update to show the next page
    
  Scenario: Progress visualization during discovery
    Given I have page discovery enabled
    When new pages are discovered during scraping
    Then the "Pages in Queue" count should increase dynamically
    And I should see "New pages discovered: X" notifications
    And the progress bar should adjust to reflect the new total