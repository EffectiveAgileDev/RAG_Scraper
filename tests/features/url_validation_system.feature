Feature: URL Validation System
  As a user of RAG_Scraper
  I want reliable URL validation
  So that I can ensure only valid restaurant URLs are processed

  Background:
    Given the RAG_Scraper web interface is running
    And I am on the main interface page

  Scenario: Valid URL Detection
    Given I have entered a valid restaurant URL "https://www.example-restaurant.com"
    When I click the "Validate URLs" button
    Then I should see a green checkmark for the URL
    And I should see "1/1 URLs valid" message
    And no error messages should be displayed

  Scenario: Invalid URL Detection
    Given I have entered an invalid URL "not-a-valid-url"
    When I click the "Validate URLs" button
    Then I should see a red X for the URL
    And I should see "0/1 URLs valid" message
    And I should see a specific error message explaining the issue

  Scenario: Mixed URL Validation
    Given I have entered multiple URLs
    When I click the "Validate URLs" button
    Then I should see "2/3 URLs valid" message
    And I should see individual validation status for each URL
    And I should see clear indication of which URLs failed and why

  Scenario: Real-time URL Validation
    Given I am typing in the URL input field
    When I enter a complete URL and pause typing
    Then validation should occur automatically after a brief delay
    And validation results should update without clicking any button

  Scenario: Empty URL Input Handling
    Given the URL input field is empty
    When I click the "Validate URLs" button
    Then no validation should occur
    And no error messages should be displayed
    And the validation area should remain empty

  Scenario: Whitespace and Formatting Tolerance
    Given I have entered URLs with extra whitespace
    When I click the "Validate URLs" button
    Then whitespace should be properly trimmed
    And empty lines should be ignored
    And I should see "3/4 URLs valid" message