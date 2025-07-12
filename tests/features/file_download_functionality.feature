Feature: Multiple File Download Functionality
  As a user of the RAG Scraper web interface
  I want to download multiple files after successful extraction
  So that I can access all generated output files

  Background:
    Given the web interface is running
    And the user has performed a successful extraction that generated multiple files

  Scenario: Multiple files are generated and downloadable
    Given the extraction process generated the following files:
      | filename                    | type |
      | restaurant_data.txt        | text |
      | restaurant_data.pdf        | pdf  |
      | restaurant_data.json       | json |
    When the user views the results page
    Then they should see download links for all 3 files
    And each download link should be functional

  Scenario: Download links work for different file types
    Given the extraction generated files of different types
    When the user clicks on a text file download link
    Then the file should download successfully
    When the user clicks on a PDF file download link
    Then the file should download successfully
    When the user clicks on a JSON file download link
    Then the file should download successfully

  Scenario: Download error handling
    Given the extraction generated files
    But one of the files was deleted from the server
    When the user tries to download the missing file
    Then they should see an appropriate error message
    And the other files should still be downloadable

  Scenario: No files generated scenario
    Given the extraction process completed
    But no files were generated due to processing errors
    When the user views the results page
    Then they should see a message indicating no files are available for download
    And no download links should be displayed