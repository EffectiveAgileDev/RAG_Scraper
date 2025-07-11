Feature: PDF Upload RAG Output Generation
  As a user
  I want to upload PDF files and generate RAG output files
  So that I can process restaurant documents into structured data

  Background:
    Given the RAG scraper application is running
    And the file upload system is configured
    And the scraping pipeline is available

  Scenario: Upload PDF and generate RAG text output
    Given I have a PDF file containing restaurant information
    When I upload the PDF file through the file upload interface
    And I select "text" as the output format
    And I submit the processing request
    Then the system should extract text from the PDF
    And generate a RAG-formatted text file
    And provide download links for the generated files
    And the text file should contain structured restaurant data

  Scenario: Upload PDF and generate RAG PDF output
    Given I have a PDF file containing restaurant menu information
    When I upload the PDF file through the file upload interface
    And I select "pdf" as the output format
    And I submit the processing request
    Then the system should extract text from the PDF
    And generate a new PDF file with RAG formatting
    And provide download links for the generated files
    And the new PDF should contain structured restaurant data

  Scenario: Upload PDF and generate RAG JSON output
    Given I have a PDF file containing restaurant details
    When I upload the PDF file through the file upload interface
    And I select "json" as the output format
    And I submit the processing request
    Then the system should extract text from the PDF
    And generate a JSON file with structured restaurant data
    And provide download links for the generated files
    And the JSON file should contain valid restaurant schema

  Scenario: Upload multiple PDFs and generate batch RAG output
    Given I have multiple PDF files containing restaurant information
    When I upload all PDF files through the file upload interface
    And I select "text" as the output format
    And I submit the processing request
    Then the system should extract text from all PDF files
    And generate individual RAG-formatted text files for each PDF
    And provide download links for all generated files
    And each text file should contain structured restaurant data

  Scenario: Upload PDF with file path and generate RAG output
    Given I have a PDF file accessible via file path
    When I enter the file path in the file path input field
    And I select "text" as the output format
    And I submit the processing request
    Then the system should read the PDF from the specified path
    And extract text from the PDF
    And generate a RAG-formatted text file
    And provide download links for the generated files

  Scenario: PDF upload failure handling
    Given I have a corrupted PDF file
    When I upload the PDF file through the file upload interface
    And I submit the processing request
    Then the system should detect the PDF processing failure
    And display appropriate error messages
    And not generate any output files
    And provide guidance on file requirements

  Scenario: Large PDF upload and processing
    Given I have a large PDF file (>5MB) with restaurant information
    When I upload the PDF file through the file upload interface
    And I select "text" as the output format
    And I submit the processing request
    Then the system should handle the large file upload
    And extract text from the large PDF
    And generate a RAG-formatted text file
    And provide download links for the generated files
    And display processing progress during extraction