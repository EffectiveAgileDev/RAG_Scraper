Feature: PDF Generation System with Professional Formatting
  As a restaurant data analyst
  I want to generate professional PDF documents from scraped restaurant data
  So that I can create presentation-ready documentation alongside RAG text files

  Background:
    Given the RAG_Scraper system is initialized
    And I have sample restaurant data with multiple sources

  Scenario: Generate basic PDF document from restaurant data
    Given I have restaurant data for "Tony's Italian Restaurant" with complete information
    When I request PDF generation with format "pdf"
    Then a PDF file should be created successfully
    And the PDF should contain the restaurant name "Tony's Italian Restaurant"
    And the PDF should contain the restaurant address
    And the PDF should contain the restaurant phone number
    And the PDF should have proper document structure with headers

  Scenario: Generate PDF with professional formatting and layout
    Given I have restaurant data for multiple restaurants
    When I request PDF generation with professional formatting
    Then the PDF should have a document title and timestamp header
    And the PDF should have proper visual hierarchy with sections
    And each restaurant should be clearly separated on the page
    And the PDF should include source indicators for each data point
    And font formatting should be consistent throughout the document

  Scenario: Generate PDF with configurable formatting options
    Given I have restaurant data ready for PDF generation
    When I configure PDF settings with custom fonts and layout
    And I request PDF generation with custom configuration
    Then the PDF should use the specified font family
    And the PDF should apply the configured layout settings
    And the formatting preferences should be saved for future use

  Scenario: Dual format generation - text and PDF simultaneously
    Given I have restaurant data for "Blue Moon Diner"
    When I request dual format generation for both text and PDF
    Then both a text file and PDF file should be created
    And the content in both files should match exactly
    And both files should be saved in the specified output directory
    And the generation result should indicate both formats were created

  Scenario: PDF generation with large dataset performance
    Given I have restaurant data for 50 restaurants
    When I request PDF generation for the large dataset
    Then the PDF should be generated within acceptable time limits
    And the PDF file size should be optimized and under 5x equivalent text size
    And all 50 restaurants should be included in the PDF
    And the PDF should have proper page breaks and navigation

  Scenario: PDF configuration persistence across sessions
    Given I configure PDF settings with custom output directory and formatting
    When I save the PDF preferences
    And I restart the application session
    Then the saved PDF configuration should be restored
    And subsequent PDF generation should use the saved preferences
    And the output directory setting should persist

  Scenario: PDF content validation and integrity
    Given I have restaurant data with special characters and formatting
    When I generate a PDF document
    Then all special characters should be properly encoded in the PDF
    And the PDF should be valid and openable in standard PDF viewers
    And the content should match the source data exactly
    And metadata should include generation timestamp and source information

  Scenario: PDF generation error handling and validation
    Given I have invalid restaurant data or missing required fields
    When I attempt PDF generation
    Then appropriate error messages should be provided
    And the system should handle missing data gracefully
    And partial data should still generate a valid PDF with warnings
    And error details should specify which data fields are problematic

  Scenario: Multi-page PDF with headers and footers
    Given I have restaurant data that requires multiple pages
    When I generate a PDF document
    Then the PDF should have consistent headers on each page
    And page numbers should be included in footers
    And restaurant information should not be split across pages inappropriately
    And the document should maintain professional formatting throughout

  Scenario: PDF file organization and naming
    Given I configure a specific output directory for PDF files
    When I generate PDF documents for different restaurant datasets
    Then PDF files should be named with timestamps and identifiers
    And files should be organized in the specified directory structure
    And duplicate filename conflicts should be handled appropriately
    And file permissions should allow standard access and sharing