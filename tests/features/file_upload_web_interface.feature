Feature: File Upload Web Interface Integration
    As a user of the RAG Scraper web interface
    I want to be able to upload local PDF files instead of providing URLs
    So that I can extract data from PDFs that are not accessible via URLs

    Background:
        Given the RAG Scraper web application is running
        And I am on the main interface page

    Scenario: User can see input mode toggle
        When I view the main form
        Then I should see an input mode toggle with "URL" and "File Upload" options
        And the "URL" option should be selected by default
        And the TARGET_URLS textarea should be visible

    Scenario: User can switch to file upload mode
        When I click the "File Upload" toggle option
        Then the TARGET_URLS textarea should be hidden
        And I should see a file upload area with drag and drop support
        And the file upload area should accept PDF files
        And there should be a "Browse Files" button

    Scenario: User can switch back to URL mode
        Given I have switched to "File Upload" mode
        When I click the "URL" toggle option
        Then the file upload area should be hidden
        And the TARGET_URLS textarea should be visible and required

    Scenario: User can upload a single PDF file
        Given I am in "File Upload" mode
        When I select a valid PDF file "sample_menu.pdf"
        Then the file should appear in the upload queue
        And I should see the filename "sample_menu.pdf"
        And I should see the file size
        And there should be a remove button for the file

    Scenario: User can upload multiple PDF files
        Given I am in "File Upload" mode
        When I select multiple PDF files "menu1.pdf, menu2.pdf, menu3.pdf"
        Then all files should appear in the upload queue
        And I should see 3 files listed
        And each file should have a remove button

    Scenario: User cannot upload non-PDF files
        Given I am in "File Upload" mode
        When I try to select a file "document.txt"
        Then I should see an error message "Only PDF files are supported"
        And the file should not be added to the upload queue

    Scenario: User can remove files from upload queue
        Given I am in "File Upload" mode
        And I have uploaded "menu1.pdf" and "menu2.pdf"
        When I click the remove button for "menu1.pdf"
        Then "menu1.pdf" should be removed from the queue
        And "menu2.pdf" should still be in the queue

    Scenario: User can drag and drop files
        Given I am in "File Upload" mode
        When I drag and drop "restaurant_menu.pdf" onto the upload area
        Then the file should appear in the upload queue
        And I should see "restaurant_menu.pdf" in the file list

    Scenario: User can process uploaded files
        Given I am in "File Upload" mode
        And I have uploaded "sample_menu.pdf"
        And I have selected an industry
        When I click the "Start Processing" button
        Then the file should be processed for text extraction
        And I should see progress indication
        And the extracted text should be processed with the WTEG schema

    Scenario: File upload shows validation errors
        Given I am in "File Upload" mode
        When I try to upload a file larger than 50MB
        Then I should see an error "File size exceeds maximum limit of 50MB"
        And the file should not be added to the queue

    Scenario: File upload shows security scan results
        Given I am in "File Upload" mode
        When I upload a file that triggers security warnings
        Then I should see a warning message about potential security issues
        And I should have the option to proceed or cancel

    Scenario: Empty file upload queue shows validation
        Given I am in "File Upload" mode
        And the upload queue is empty
        When I try to start processing
        Then I should see an error "Please upload at least one PDF file"
        And processing should not start

    Scenario: File upload progress is tracked
        Given I am in "File Upload" mode
        And I have uploaded multiple PDF files
        When I start processing
        Then I should see individual file processing progress
        And I should see overall progress across all files
        And I should see which file is currently being processed

    Scenario: Processed files show extraction results
        Given I have successfully processed uploaded PDF files
        When processing is complete
        Then I should see extraction results for each file
        And I should see the number of data items extracted from each PDF
        And I should be able to download the generated output files