Feature: Page Relationships Display
  As a user of the RAG_Scraper web interface
  I want to see parent-child relationships between scraped pages
  So that I can understand the site structure and navigation hierarchy

  Background:
    Given the RAG_Scraper web interface is loaded
    And I am in multi-page mode
    And I have completed a multi-page scraping operation

  Scenario: Display parent-child relationships for discovered pages
    Given I scraped a restaurant site with hierarchical pages
    And the home page discovered 2 child pages
    And one child page discovered 1 additional page
    When I view the results section
    Then I should see the home page marked as "ROOT"
    And I should see the child pages indented under their parent
    And I should see relationship indicators showing the hierarchy
    And each child page should show "↳ from: [parent URL]"

  Scenario: Show relationship depth indicators
    Given I scraped a site with 3 levels of page hierarchy
    When I view the results section
    Then I should see level 0 pages with no indentation
    And I should see level 1 pages with single indentation
    And I should see level 2 pages with double indentation
    And each level should have distinct visual indicators

  Scenario: Display discovery source information
    Given I scraped a site where pages were discovered through links
    When I view the results section
    Then each discovered page should show its discovery source
    And I should see "Discovered from: [parent page]" for child pages
    And I should see "Entry point" for initial URLs
    And I should see the discovery method (link, sitemap, manual)

  Scenario: Show page relationship tree structure
    Given I scraped a site with complex page relationships
    When I view the results section
    Then I should see a tree-like structure with connecting lines
    And parent pages should have expand/collapse indicators
    And expanding a parent should reveal its children
    And collapsing should hide the child pages

  Scenario: Display relationship statistics
    Given I scraped a site with multiple page relationships
    When I view the results section
    Then I should see "Children discovered: X" for parent pages
    And I should see "Depth level: X" for each page
    And I should see total relationship count in the site summary
    And orphaned pages should be clearly marked

  Scenario: Relationship display in single-page mode
    Given I am in single-page mode
    When I complete a scraping operation
    Then I should not see relationship indicators
    And each page should be treated as independent
    And no parent-child hierarchy should be displayed

  Scenario: Interactive relationship exploration
    Given I have results with page relationships
    When I click on a parent page indicator
    Then the child pages should be highlighted
    When I hover over a child page
    Then its parent relationship should be emphasized
    And I should see a tooltip with relationship details

  Scenario: Relationship error handling
    Given I scraped a site with broken relationship links
    When I view the results section
    Then broken relationships should be marked with warning icons
    And I should see "Relationship broken" indicators
    And orphaned pages should be grouped separately