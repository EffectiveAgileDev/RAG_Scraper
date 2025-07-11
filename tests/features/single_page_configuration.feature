Feature: Single Page Configuration Options
  As a user scraping individual pages
  I want to access configuration options in single-page mode
  So that I can configure JavaScript rendering, popup handling, and other options

  Background:
    Given the user is on the main scraping interface
    And the interface is loaded successfully

  Scenario: Single page mode shows configuration options
    When the user selects "Single Page" mode
    Then the single page configuration panel should be visible
    And the single page configuration options should be available

  Scenario: JavaScript rendering available in single page mode
    When the user selects "Single Page" mode
    And the user expands the single page configuration panel
    Then the "Enable JavaScript Rendering" option should be available
    And the "JS Timeout" option should be available

  Scenario: Popup handling available in single page mode
    When the user selects "Single Page" mode
    And the user expands the single page configuration panel
    Then the "Enable Popup Handling" option should be available
    And the popup handling should be enabled by default

  Scenario: Advanced options available in single page mode
    When the user selects "Single Page" mode
    And the user expands the single page configuration panel
    And the user expands the advanced options
    Then the "Request Timeout" option should be available
    And the "Concurrent Requests" option should be available
    But the "Enable Page Discovery" option should not be available

  Scenario: Multi-page specific options not available in single page mode
    When the user selects "Single Page" mode
    And the user expands the single page configuration panel
    Then the "Max Pages Per Site" option should not be available
    And the "Crawl Depth" option should not be available
    And the "Include Patterns" option should not be available
    And the "Exclude Patterns" option should not be available
    And the "Rate Limit" option should not be available

  Scenario: Multi page mode retains all options
    When the user selects "Multi Page" mode
    And the user expands the multi page configuration panel
    Then all multi-page configuration options should be available
    And the "Max Pages Per Site" option should be available
    And the "Crawl Depth" option should be available

  Scenario: Mode switching preserves configuration values
    Given the user selects "Single Page" mode
    And the user sets "Enable JavaScript Rendering" to true
    And the user sets "JS Timeout" to 60 seconds
    When the user switches to "Multi Page" mode
    And the user switches back to "Single Page" mode
    Then the "Enable JavaScript Rendering" should still be true
    And the "JS Timeout" should still be 60 seconds

  Scenario: Configuration panel toggle functionality
    Given the user selects "Single Page" mode
    When the user clicks the single page configuration header
    Then the configuration panel should expand
    And the expand icon should change to indicate expansion
    When the user clicks the header again
    Then the configuration panel should collapse
    And the expand icon should change to indicate collapse

  Scenario: Single page configuration form submission
    Given the user selects "Single Page" mode
    And the user enables JavaScript rendering
    And the user enables popup handling
    And the user sets request timeout to 45 seconds
    When the user submits the scraping request
    Then the configuration should be included in the request
    And the JavaScript rendering should be enabled
    And the popup handling should be enabled
    And the request timeout should be 45 seconds