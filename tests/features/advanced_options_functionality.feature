Feature: Advanced Options Functionality
  As a user of the RAG Scraper web interface
  I want to access and configure advanced scraping options
  So that I can customize the extraction behavior

  Background:
    Given the web interface is running
    And the user is on the main extraction page
    And multi-page mode is selected

  Scenario: Advanced Options panel opens when clicked
    Given the Advanced Options panel is collapsed
    When the user clicks on the "Advanced Options" header
    Then the Advanced Options panel should expand
    And the expand icon should change from "▼" to "▲"
    And all advanced option controls should be visible

  Scenario: Advanced Options panel closes when clicked again
    Given the Advanced Options panel is expanded
    When the user clicks on the "Advanced Options" header
    Then the Advanced Options panel should collapse
    And the expand icon should change from "▲" to "▼"
    And advanced option controls should be hidden

  Scenario: Advanced Options toggles properly multiple times
    Given the Advanced Options panel is collapsed
    When the user clicks on the "Advanced Options" header
    Then the panel should expand
    When the user clicks on the "Advanced Options" header again
    Then the panel should collapse
    When the user clicks on the "Advanced Options" header again
    Then the panel should expand

  Scenario: Advanced Options keyboard accessibility
    Given the Advanced Options panel is collapsed
    When the user focuses on the Advanced Options header
    And presses the Enter key
    Then the Advanced Options panel should expand
    When the user presses the Space key
    Then the Advanced Options panel should collapse

  Scenario: Advanced Options content is functional
    Given the Advanced Options panel is expanded
    Then the user should see the "Enable Page Discovery" checkbox
    And the user should see the "Request Timeout" input field
    And the user should see the "Concurrent Requests" slider
    And the user should see the "Follow Redirects" checkbox
    And the user should see the "Respect Robots.txt" checkbox
    And the user should see the "Reset to Defaults" button

  Scenario: Reset to Defaults functionality works
    Given the Advanced Options panel is expanded
    And the user has modified some advanced options
    When the user clicks the "Reset to Defaults" button
    Then all advanced options should return to their default values
    And a success message should be displayed