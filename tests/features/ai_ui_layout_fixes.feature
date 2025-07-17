Feature: AI Settings Panel Layout Fixes
  As a user configuring AI settings
  I want the AI settings panel to have sufficient space
  So that all options and buttons are visible without truncation

  Background:
    Given the RAG Scraper web interface is running
    And I am on the main scraping page

  Scenario: AI Settings Panel has sufficient vertical space
    When I click on "Advanced Options" to expand the advanced settings
    And I enable "AI Enhancement" in the advanced options
    Then the AI settings panel should be fully visible
    And all AI configuration options should be displayed without truncation
    And the save buttons should be visible at the bottom
    And no content should be cut off or require scrolling within the panel

  Scenario: AI Settings Panel maintains proper height in single-page mode
    Given I am in single-page scraping mode
    When I expand the Advanced Options panel
    And I enable AI Enhancement
    Then the AI settings panel should expand to accommodate all content
    And the "Save Settings" button should be visible
    And the "Load Settings" button should be visible
    And the "Clear Settings" button should be visible
    And no vertical scrolling should be required within the AI panel

  Scenario: AI Settings Panel maintains proper height in multi-page mode
    Given I am in multi-page scraping mode
    When I expand the Advanced Options panel
    And I enable AI Enhancement
    Then the AI settings panel should expand to accommodate all content
    And the "Save Multi-Page Settings" button should be visible
    And all AI configuration options should be accessible
    And no content should be hidden due to height constraints

