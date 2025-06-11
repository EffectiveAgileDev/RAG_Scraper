Feature: End-to-End File Generation Integration
  As a user of RAG_Scraper
  I want scraping to automatically generate output files
  So that I can access scraped data immediately after scraping completes

  @integration @file_generation
  Scenario: Scraping should automatically generate text files
    Given the RAG_Scraper web interface is running
    And I have a valid restaurant website URL
    And I have selected text file output format
    When I execute the scraping process via the web interface
    Then I should receive a success response
    And a text file should be created in the output directory
    And the text file should contain the scraped restaurant data

  @integration @file_generation
  Scenario: Scraping should automatically generate PDF files when selected
    Given the RAG_Scraper web interface is running
    And I have a valid restaurant website URL
    And I have selected PDF file output format
    When I execute the scraping process via the web interface
    Then I should receive a success response
    And a PDF file should be created in the output directory
    And the PDF file should contain the scraped restaurant data

  @integration @file_generation
  Scenario: Scraping should generate both formats when dual format is selected
    Given the RAG_Scraper web interface is running
    And I have a valid restaurant website URL
    And I have selected both text and PDF output formats
    When I execute the scraping process via the web interface
    Then I should receive a success response
    And both text and PDF files should be created in the output directory
    And both files should contain the same restaurant data

  @integration @workflow
  Scenario: Complete workflow from URL input to file generation
    Given the RAG_Scraper web interface is running
    And I have entered a restaurant website URL
    And the URL validation shows the URL is valid
    And I have configured output directory and file format
    When I start the scraping process
    And the scraping process completes successfully
    Then output files should be automatically generated
    And the files should be accessible at the specified output directory
    And the response should include the actual file paths

  @integration @error_detection
  Scenario: Scraping success but missing file generation should be detected
    Given the RAG_Scraper web interface is running
    And I have a valid restaurant website URL
    When I execute the scraping process
    And the scraping reports success
    But no output files are generated
    Then the system should detect this inconsistency
    And return an error indicating file generation failure