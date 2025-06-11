Feature: Sprint 6-A Integration - File Format Selection with Clickable Output Links
  As a user of RAG_Scraper
  I want to select my file format and get clickable links to my files
  So that I can have complete control over my output and easy access to results

  Background:
    Given the RAG_Scraper web interface is running
    And I am on the main interface page

  Scenario: Complete workflow with text format selection and file links
    Given I have entered valid restaurant URLs
    And I select "Text" as the file format
    When I complete the scraping process
    Then I should see "Scraping Completed Successfully!" message
    And I should see clickable links to text files
    And the links should work for downloading files
    And the downloaded files should contain restaurant data

  Scenario: Complete workflow with PDF format selection and file links
    Given I have entered valid restaurant URLs
    And I select "PDF" as the file format
    When I complete the scraping process
    Then I should see "Scraping Completed Successfully!" message
    And I should see clickable links to PDF files
    And the links should work for downloading files
    And the downloaded files should contain restaurant data

  Scenario: Complete workflow with both formats and multiple file links
    Given I have entered valid restaurant URLs
    And I select "Both" as the file format
    When I complete the scraping process
    Then I should see "Scraping Completed Successfully!" message
    And I should see clickable links to both text and PDF files
    And all links should work for downloading files
    And all downloaded files should contain restaurant data