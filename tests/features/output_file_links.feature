Feature: Output File Links in Results Section
  As a user of RAG_Scraper
  I want clickable links to my generated files in the output section
  So that I can easily access and download my scraped data files

  Background:
    Given the RAG_Scraper web interface is running
    And I have completed a successful scraping operation

  Scenario: Display clickable file links for text format
    Given I have selected "Text" as the file format
    And I have scraped restaurant data successfully
    When I view the results section
    Then I should see "Generated files:" section
    And I should see clickable links to the text files
    And the links should have proper file names with .txt extension

  Scenario: Display clickable file links for PDF format
    Given I have selected "PDF" as the file format
    And I have scraped restaurant data successfully
    When I view the results section
    Then I should see "Generated files:" section
    And I should see clickable links to the PDF files
    And the links should have proper file names with .pdf extension

  Scenario: Display clickable file links for both formats
    Given I have selected "Both" as the file format
    And I have scraped restaurant data successfully
    When I view the results section
    Then I should see "Generated files:" section
    And I should see clickable links to both text and PDF files
    And the text links should have .txt extension
    And the PDF links should have .pdf extension

  Scenario: File links should be downloadable
    Given I have generated files from scraping
    When I click on a file link in the results section
    Then the file should be downloadable
    And the file should contain the scraped restaurant data