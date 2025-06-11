Feature: File Generation System
  As a user of RAG_Scraper
  I want automatic file generation in multiple formats
  So that I can use the extracted data in my RAG systems and documentation

  Background:
    Given the RAG_Scraper web interface is running
    And I have successfully scraped restaurant data

  Scenario: Automatic Text File Generation
    Given I have completed scraping a restaurant URL
    And no specific file format was selected (defaults to text)
    When the scraping process completes
    Then a text file (.txt) should be automatically created
    And the file should contain structured restaurant data
    And the file path should be returned in the API response
    And the file should be accessible in the specified directory

  Scenario: PDF Generation Integration
    Given I have restaurant data ready for file generation
    And I have selected PDF format output
    When I trigger the file generation process
    Then a PDF file (.pdf) should be automatically created
    And the PDF should have professional formatting with headers and sections
    And restaurant data should be properly structured in the PDF
    And the file should be viewable in a PDF reader

  Scenario: Dual Format Generation
    Given I have restaurant data ready for file generation
    And I have selected both text and PDF formats
    When I trigger the file generation process
    Then both .txt and .pdf files should be created
    And both files should contain the same content in their respective formats
    And both file paths should be returned in the response
    And both files should be accessible and properly formatted

  Scenario: File Naming Convention Consistency
    Given I have scraped restaurant data from "https://example-restaurant.com"
    When files are generated
    Then file names should follow the WebScrape_* pattern
    And file names should include timestamp information
    And file extensions should match the selected format (.txt or .pdf)
    And file names should be unique to prevent overwrites

  Scenario: Output Directory Customization
    Given I have specified a custom output directory
    And the directory exists and has write permissions
    When files are generated
    Then files should be created in the specified custom directory
    And the directory should be validated before file creation
    And file permissions should be properly set

  Scenario: File Content Validation for Text Format
    Given I have generated a text file from restaurant data
    When I examine the file contents
    Then the file should contain structured restaurant information
    And sections should be clearly defined (name, address, phone, etc.)
    And the data should be formatted for RAG system consumption
    And the file should be properly encoded (UTF-8)

  Scenario: File Content Validation for PDF Format
    Given I have generated a PDF file from restaurant data
    When I examine the PDF contents
    Then the PDF should have professional document structure
    And headers and sections should be visually distinct
    And restaurant data should be organized logically
    And the PDF should be searchable and properly formatted

  Scenario: Error Handling in File Generation
    Given I have restaurant data ready for processing
    And the output directory is not writable
    When I attempt to generate files
    Then appropriate error messages should be returned
    And the system should not crash or hang
    And alternative solutions should be suggested if possible

  Scenario: Overwrite Protection and Management
    Given I have previously generated files in a directory
    And I am generating new files with the same naming pattern
    When the file generation process runs
    Then existing files should be handled according to overwrite settings
    And users should be protected from accidental data loss
    And file versioning should be considered

  Scenario: Large Dataset File Generation
    Given I have scraped data from multiple restaurants (10+ establishments)
    When I generate files from this large dataset
    Then file generation should complete successfully
    And file size should be reasonable and manageable
    And system performance should remain stable
    And memory usage should be controlled

  Scenario: File Generation Service Independence
    Given I have restaurant data available
    When I call the file generation service directly (not through scraping)
    Then files should be generated successfully
    And the service should work independently of the scraping engine
    And all format options should be available
    And proper error handling should be maintained

  Scenario: Configuration Persistence
    Given I have configured specific file generation preferences
    And I have saved these preferences
    When I perform subsequent file generation operations
    Then my preferences should be remembered and applied
    And configuration should persist across sessions
    And I should be able to modify preferences as needed