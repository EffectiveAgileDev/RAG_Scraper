Feature: Advanced Options Toggle Section
  As a user configuring multi-page scraping
  I want access to advanced options for fine-tuning the scraping behavior
  So that I can optimize the scraping process for different scenarios

  Background:
    Given I am on the RAG_Scraper web interface
    And I have multi-page scraping mode enabled
    
  Scenario: Show/hide advanced options toggle
    Given I am viewing the multi-page configuration panel
    When I look for the advanced options section
    Then I should see an "Advanced Options" toggle button
    And the advanced options section should be collapsed by default
    When I click the "Advanced Options" toggle
    Then the advanced options section should expand
    And I should see additional configuration controls

  Scenario: Page discovery enable/disable toggle
    Given I have expanded the advanced options section
    When I look at the page discovery controls
    Then I should see a "Enable Page Discovery" toggle switch
    And the toggle should be enabled by default
    And I should see explanatory text about page discovery
    When I disable the page discovery toggle
    Then the scraper should only process explicitly provided URLs
    And I should see a warning about reduced functionality

  Scenario: Custom timeout settings input
    Given I have expanded the advanced options section
    When I look at the timeout controls
    Then I should see a "Request Timeout" input field
    And the field should show the current timeout value in seconds
    And I should see min/max value indicators
    When I change the timeout value to 45
    Then the configuration should be updated
    And I should see validation feedback

  Scenario: Concurrent request limit slider
    Given I have expanded the advanced options section
    When I look at the concurrency controls
    Then I should see a "Concurrent Requests" slider
    And the slider should show the current limit value
    And I should see min/max labels (1-10)
    When I adjust the slider to 3
    Then the concurrent request limit should be updated
    And I should see the new value displayed

  Scenario: Advanced options validation
    Given I have expanded the advanced options section
    When I set an invalid timeout value of 0
    Then I should see a validation error message
    And the apply button should be disabled
    When I correct the timeout to a valid value
    Then the validation error should disappear
    And the apply button should be enabled

  Scenario: Advanced options persistence
    Given I have configured advanced options
    When I set custom timeout to 30 seconds
    And I set concurrent requests to 2
    And I disable page discovery
    And I refresh the page
    Then my advanced option settings should be preserved
    And the advanced options section should remember its expanded state

  Scenario: Advanced options reset to defaults
    Given I have configured custom advanced options
    When I click the "Reset to Defaults" button
    Then all advanced options should return to default values
    And I should see a confirmation message
    And the changes should be applied immediately

  Scenario: Advanced options impact on scraping
    Given I have disabled page discovery
    When I start a scraping job with multiple URLs
    Then only the explicitly provided URLs should be processed
    And no additional pages should be discovered
    Given I have set a custom timeout of 10 seconds
    When I scrape a slow-loading page
    Then the request should timeout after 10 seconds
    And I should see appropriate timeout status in results