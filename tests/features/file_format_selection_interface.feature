Feature: File Format Selection Interface
  As a user of RAG_Scraper
  I want to select my preferred output file format before scraping
  So that I can get files in the format I need (Text, PDF, or Both)

  Background:
    Given the RAG_Scraper web interface is running
    And I am on the main interface page

  Scenario: File format selection options are visible
    Given I am viewing the scraping form
    Then I should see file format selection options
    And the options should include "Text", "PDF", and "Both"
    And "Text" should be selected by default

  Scenario: Select Text format option
    Given I am viewing the scraping form
    When I select "Text" as the file format
    Then the "Text" option should be visually selected
    And the other options should not be selected

  Scenario: Select PDF format option
    Given I am viewing the scraping form
    When I select "PDF" as the file format
    Then the "PDF" option should be visually selected
    And the other options should not be selected

  Scenario: Select Both formats option
    Given I am viewing the scraping form
    When I select "Both" as the file format
    Then the "Both" option should be visually selected
    And the other options should not be selected