Feature: Separate Save Settings for Single and Multi-Page Modes
  As a user of the RAG Scraper web interface
  I want separate save settings for single-page and multi-page modes
  So that my preferences are preserved independently for each mode

  Background:
    Given the web interface is running
    And the user is on the main extraction page

  Scenario: Single-page save settings independent from multi-page
    Given the user selects single-page mode
    When the user configures single-page settings:
      | setting              | value    |
      | requestTimeout       | 45       |
      | enableJavaScript     | true     |
      | followRedirects      | false    |
    And the user enables single-page save settings
    And the user switches to multi-page mode
    Then the multi-page settings should have default values
    And the single-page save settings toggle should be independent

  Scenario: Multi-page save settings independent from single-page
    Given the user selects multi-page mode
    When the user configures multi-page settings:
      | setting              | value    |
      | maxPages            | 100      |
      | crawlDepth          | 3        |
      | rateLimit           | 2000     |
      | enableJavaScript    | true     |
    And the user enables multi-page save settings
    And the user switches to single-page mode
    Then the single-page settings should have default values
    And the multi-page save settings toggle should be independent

  Scenario: Both modes can have save settings enabled simultaneously
    Given the user selects single-page mode
    And the user enables single-page save settings
    When the user switches to multi-page mode
    And the user enables multi-page save settings
    Then both save settings should be active independently
    And switching between modes should preserve respective settings

  Scenario: Save settings are located within respective config panels
    Given the user selects single-page mode
    When the user expands the single-page configuration panel
    Then the single-page save settings toggle should be visible within the panel
    When the user switches to multi-page mode
    And the user expands the multi-page configuration panel
    Then the multi-page save settings toggle should be visible within the panel

  Scenario: Settings persistence works independently
    Given the user has configured and saved single-page settings
    And the user has configured and saved multi-page settings
    When the user refreshes the page
    Then the single-page saved settings should be restored when in single-page mode
    And the multi-page saved settings should be restored when in multi-page mode
    And the settings should not interfere with each other