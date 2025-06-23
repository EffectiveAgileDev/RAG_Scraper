Feature: Scraping Mode Selector
  As a user of the RAG_Scraper web interface
  I want to choose between single-page and multi-page scraping modes
  So that I can control how URLs are processed and scraped

  Background:
    Given the RAG_Scraper web interface is loaded
    And I can see the scraping mode selector

  Scenario: Default scraping mode is single-page
    When I load the web interface
    Then the single-page mode should be selected by default
    And the multi-page configuration panel should be hidden
    And the status bar should show "SINGLE_PAGE_MODE // DIRECT_URL_PROCESSING"

  Scenario: Switch to multi-page mode
    Given the single-page mode is selected
    When I click on the multi-page mode option
    Then the multi-page mode should become selected
    And the single-page mode should become unselected
    And the multi-page configuration panel header should be visible
    And the status bar should show "MULTI_PAGE_MODE // ADVANCED_CRAWLING_ENABLED"

  Scenario: Multi-page configuration panel visibility
    Given I am in multi-page mode
    When I click on the multi-page configuration header
    Then the configuration panel should expand
    And I should see max pages per site setting
    And I should see crawl depth slider
    And I should see include patterns input
    And I should see exclude patterns input
    And I should see rate limit slider
    And the status bar should show "MULTI_PAGE_CONFIG // PANEL_EXPANDED"

  Scenario: Switch back to single-page mode
    Given I am in multi-page mode
    And the multi-page configuration panel is expanded
    When I click on the single-page mode option
    Then the single-page mode should become selected
    And the multi-page mode should become unselected
    And the multi-page configuration panel should be hidden
    And the configuration panel should be collapsed
    And the status bar should show "SINGLE_PAGE_MODE // DIRECT_URL_PROCESSING"

  Scenario: Multi-page configuration slider updates
    Given I am in multi-page mode
    And the configuration panel is expanded
    When I move the crawl depth slider to value 3
    Then the depth value display should show "Depth: 3"
    And the status bar should show "CRAWL_DEPTH_SET // LEVEL_3"
    When I move the rate limit slider to 2000
    Then the rate limit value display should show "Delay: 2000ms"
    And the status bar should show "RATE_LIMIT_SET // 2000MS_DELAY"

  Scenario: Multi-page configuration input updates
    Given I am in multi-page mode
    And the configuration panel is expanded
    When I change the max pages input to "100"
    Then the status bar should show "MAX_PAGES_SET // LIMIT_100_PAGES"
    When I change the include patterns to "menu,food,dining"
    Then the status bar should show "INCLUDE_PATTERNS_SET // 3_FILTERS_ACTIVE"
    When I change the exclude patterns to "admin,login,cart,checkout"
    Then the status bar should show "EXCLUDE_PATTERNS_SET // 4_FILTERS_ACTIVE"

  Scenario: Submit form with single-page mode
    Given I am in single-page mode
    And I have entered valid URLs
    When I submit the scraping form
    Then the request should include scraping_mode as "single"
    And the request should not include multi_page_config
    And the status should show "INITIATING_EXTRACTION // SINGLE_MODE"

  Scenario: Submit form with multi-page mode
    Given I am in multi-page mode
    And I have configured max pages as 75
    And I have configured crawl depth as 3
    And I have configured include patterns as "menu,food"
    And I have configured exclude patterns as "admin,login"
    And I have configured rate limit as 1500
    And I have entered valid URLs
    When I submit the scraping form
    Then the request should include scraping_mode as "multi"
    And the request should include multi_page_config with:
      | maxPages        | 75         |
      | crawlDepth      | 3          |
      | includePatterns | menu,food  |
      | excludePatterns | admin,login|
      | rateLimit       | 1500       |
    And the status should show "INITIATING_EXTRACTION // MULTI_MODE"

  Scenario: Multi-page configuration persistence
    Given I am in multi-page mode
    And I have configured the multi-page settings
    When I switch to single-page mode
    And I switch back to multi-page mode
    Then the previous multi-page configuration should be preserved
    And all input values should remain unchanged

  Scenario: Visual feedback for mode selection
    Given I can see both mode options
    When I hover over the single-page mode option
    Then it should show hover effects with cyan border
    When I hover over the multi-page mode option
    Then it should show hover effects with cyan border
    When I select the multi-page mode
    Then it should show active state with green border and glow
    And the single-page mode should show inactive state