Feature: Results Display Layout Fixes
  As a user viewing scraping results
  I want the results to be properly positioned and organized
  So that I can easily view the output and navigate the interface

  Background:
    Given the RAG Scraper web interface is running
    And I am on the main scraping page
    And I have completed a scraping operation

  Scenario: Scraping results are positioned under the correct section
    When I view the scraping results
    Then the results output should be positioned under the "Scraping Results" section
    And the results should be clearly visible and accessible
    And the results should not interfere with other UI elements

  Scenario: Advanced Options header is properly positioned
    When I view the advanced options section
    Then the "Advanced Options" header should be positioned to the left
    And the header should be directly above the advanced options controls
    And the header alignment should be consistent with the interface design

  Scenario: Results display does not overlap with advanced options
    Given I have expanded the Advanced Options panel
    When I view the scraping results
    Then the results display should not overlap with the advanced options
    And both sections should be clearly separated visually
    And the layout should remain functional on different screen sizes