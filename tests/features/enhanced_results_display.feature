Feature: Enhanced Results Display
  As a user of the RAG_Scraper web interface
  I want to see detailed results about pages processed per site
  So that I can understand what was scraped and monitor multi-page scraping success

  Background:
    Given the RAG_Scraper web interface is loaded
    And I have successfully completed a scraping operation

  Scenario: Display pages processed for single site
    Given I scraped a restaurant site with 3 pages
    When I view the results section
    Then I should see "Pages Processed: 3"
    And I should see a list of processed pages
    And each page entry should show the URL
    And each page entry should show the processing status

  Scenario: Display pages processed for multiple sites
    Given I scraped 2 restaurant sites
    And the first site had 4 pages processed
    And the second site had 2 pages processed
    When I view the results section
    Then I should see results grouped by site
    And the first site should show "Pages Processed: 4"
    And the second site should show "Pages Processed: 2"

  Scenario: Show page processing details
    Given I scraped a site with successful and failed pages
    When I view the results section
    Then I should see successful pages marked with green status
    And I should see failed pages marked with red status
    And each page should show its URL
    And each page should show its processing time

  Scenario: Expandable page lists for large sites
    Given I scraped a site with 15 pages
    When I view the results section
    Then I should see the first 5 pages displayed
    And I should see "Show all 15 pages" link
    When I click "Show all pages"
    Then I should see all 15 pages listed

  Scenario: Empty results display
    Given no scraping operation has been completed
    When I view the results section
    Then I should see "No results available"
    And I should see "Complete a scraping operation to see detailed results"

  Scenario: Results section visibility based on scraping mode
    Given I am in single-page mode
    When I complete a scraping operation
    Then the results should show individual page processing
    And page relationships should not be displayed
    Given I am in multi-page mode  
    When I complete a scraping operation
    Then the results should show site-based grouping
    And page discovery information should be displayed