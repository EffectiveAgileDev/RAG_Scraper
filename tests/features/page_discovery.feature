Feature: Page Discovery for Multi-Page Scraping
  As a user of RAG_Scraper
  I want to discover and navigate through multiple pages on a website
  So that I can collect comprehensive restaurant data from directory sites

  Background:
    Given the page discovery system is initialized

  Scenario: Discover links from restaurant directory page
    Given I have a restaurant directory page with multiple restaurant links
    When I extract links from the directory page
    Then I should find all restaurant detail page links
    And the links should be properly formatted URLs
    And duplicate links should be removed

  Scenario: Filter links by pattern
    Given I have a page with mixed types of links
    And I have a pattern to match restaurant pages "/restaurant/*"
    When I filter links using the pattern
    Then I should only get links matching the restaurant pattern
    And non-matching links should be excluded
    And the filtered links should maintain their full URLs

  Scenario: Respect crawl depth limits
    Given I have set a crawl depth limit of 2
    And I start from a directory page at depth 0
    When I discover links at each level
    Then links from the directory page should be at depth 1
    And links from restaurant pages should be at depth 2
    And no links should be followed beyond depth 2
    And the system should track the depth of each discovered link