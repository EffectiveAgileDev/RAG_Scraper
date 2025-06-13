Feature: Enhanced Format Selection User Interface
  As a RAG system administrator  
  I want an updated web interface with enhanced format selection
  So that I can choose between Text, PDF, and JSON formats with a modern single-choice interface

  Background:
    Given the RAG_Scraper web interface is running
    And I am on the main scraping interface

  Scenario: Enhanced format selection interface display
    When I view the format selection section
    Then I should see exactly three format options: "Text", "PDF", "JSON"
    And the format options should be presented as radio buttons
    And there should be no "DUAL", "Both", or multi-format options
    And the "Text" option should be selected by default
    And each format option should have a descriptive subtitle

  Scenario: JSON format option availability
    When I view the format selection options
    Then I should see a "JSON" format option
    And the JSON option should have the title "JSON"
    And the JSON option should have the description "Structured data for system integration"
    And the JSON option should be selectable

  Scenario: Single format selection behavior
    Given I am viewing the format selection interface
    When I select the "PDF" format option
    Then only the "PDF" option should be visually selected
    And the "Text" and "JSON" options should be deselected
    And the form should indicate "PDF" as the selected format

  Scenario: JSON format selection with field customization
    Given I am viewing the format selection interface
    When I select the "JSON" format option
    Then the JSON option should be visually selected
    And I should see field selection options appear
    And the field selection should include "Core Fields", "Extended Fields", "Contact Fields"
    And I should be able to toggle individual field categories

  Scenario: Format selection persistence across page interactions
    Given I have selected the "JSON" format option
    And I have configured custom field selections
    When I enter some restaurant URLs
    And I change other form fields
    Then the "JSON" format should remain selected
    And my field selection preferences should be preserved

  Scenario: Legacy format removal validation
    When I inspect the format selection interface
    Then I should not find any option labeled "DUAL"
    And I should not find any option labeled "Both formats"
    And I should not find any option with value "both"
    And there should be no checkboxes allowing multiple format selection

  Scenario: Enhanced format selection visual design
    When I view the format selection section
    Then each format option should have consistent visual styling
    And the selected format should have a distinct visual indicator
    And hover effects should provide visual feedback
    And the interface should follow the terminal/cyberpunk design theme

  Scenario: Format selection form integration
    Given I have selected the "JSON" format
    And I have entered valid restaurant URLs
    When I submit the scraping form
    Then the request should include format="json"
    And if field selections are configured, they should be included
    And the backend should receive the enhanced format selection data

  Scenario: Format selection accessibility
    When I use keyboard navigation on the format selection
    Then I should be able to navigate between format options using Tab
    And I should be able to select formats using Space or Enter
    And screen readers should announce format option changes
    And the interface should follow accessibility best practices

  Scenario: JSON field selection advanced features
    Given I have selected the "JSON" format option
    When I view the field selection options
    Then I should see grouped field categories
    And I should be able to "Select All" or "Deselect All" fields
    And I should see a preview of which fields will be included
    And field selection changes should update in real-time