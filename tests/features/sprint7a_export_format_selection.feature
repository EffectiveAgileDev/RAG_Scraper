Feature: Single-Choice Export Format Selection Interface
  As a RAG system administrator
  I want to select exactly one export format (Text, PDF, or JSON)
  So that I can generate files in my preferred format without multi-format complexity

  Background:
    Given the RAG_Scraper web interface is running
    And I have access to the export format selection interface

  Scenario: Export format selection interface display
    Given I am on the main scraping interface
    Then I should see export format selection options
    And the options should be "Text only", "PDF only", "JSON only"
    And the format selection should be presented as radio buttons or dropdown
    And only one format option should be selectable at a time
    And there should be no "All formats" or "Both" option available

  Scenario: Text only export format selection
    Given I have valid restaurant website URLs
    And I select "Text only" as the export format
    When I execute the scraping process
    Then I should receive only a text file output
    And no PDF or JSON files should be generated
    And the text file should contain properly formatted restaurant data
    And the format selection should be visually indicated as active

  Scenario: PDF only export format selection
    Given I have valid restaurant website URLs  
    And I select "PDF only" as the export format
    When I execute the scraping process
    Then I should receive only a PDF file output
    And no text or JSON files should be generated
    And the PDF file should contain professionally formatted restaurant data
    And the format selection should be visually indicated as active

  Scenario: JSON only export format selection
    Given I have valid restaurant website URLs
    And I select "JSON only" as the export format
    When I execute the scraping process
    Then I should receive only a JSON file output
    And no text or PDF files should be generated
    And the JSON file should contain structured restaurant data
    And the format selection should be visually indicated as active

  Scenario: Export format preference persistence
    Given I select "JSON only" as the export format
    And I complete a scraping session
    When I refresh the web interface or restart the application
    Then the export format selection should default to "JSON only"
    And my previous format choice should be remembered
    And the interface should display my saved preference

  Scenario: Export format selection validation
    Given I am on the scraping interface
    When I attempt to start scraping without selecting an export format
    Then I should receive a validation error message
    And the scraping process should not start
    And I should be prompted to select exactly one export format
    And the error message should be clear and user-friendly

  Scenario: Export format selection change during session
    Given I have selected "Text only" as the export format
    When I change the selection to "PDF only" before scraping
    Then the interface should update to show "PDF only" as selected
    And the previous "Text only" selection should be deselected
    And only the new format choice should be active
    And the change should be reflected in the UI immediately

  Scenario: Export format selection with field customization
    Given I select "JSON only" as the export format
    And I customize field selections to include only core fields
    When I execute the scraping process
    Then the JSON output should respect both format and field selections
    And only the chosen fields should appear in the JSON file
    And the format-specific customization should work correctly

  Scenario: Legacy multi-format selection removal validation
    Given I am using the updated export interface
    Then I should not see any "Both", "All formats", or multiple selection options
    And there should be no checkboxes allowing multiple format selection
    And the interface should clearly indicate single-choice selection only
    And any legacy multi-format selection code should be inactive