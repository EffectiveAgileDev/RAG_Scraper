Feature: Local File Upload for PDF Processing
  As a RAG Scraper user
  I want to upload local PDF files for processing
  So that I can extract restaurant data from PDF files that are not accessible via URL

  Background:
    Given the RAG Scraper web interface is running
    And I am on the main scraping page
    And the local file upload system is enabled

  Scenario: Switch from URL mode to File Upload mode
    Given the interface is in "URL Mode" by default
    When I click the "File Upload Mode" toggle
    Then the URL input area should be hidden
    And the file upload area should be displayed
    And the upload area should show "Drag and drop PDF files here or click to browse"
    And the mode indicator should show "FILE UPLOAD MODE"

  Scenario: Upload a single PDF file via drag and drop
    Given the interface is in "File Upload Mode"
    And I have a valid PDF file "restaurant_menu.pdf" on my local system
    When I drag and drop the PDF file onto the upload area
    Then the file should be validated as a PDF format
    And the file size should be checked (must be under 50MB)
    And the file should appear in the upload queue with status "Ready for processing"
    And the file name should be displayed as "restaurant_menu.pdf"
    And a remove button should be available for each file

  Scenario: Upload a single PDF file via browse button
    Given the interface is in "File Upload Mode"
    And I have a valid PDF file "restaurant_guide.pdf" on my local system
    When I click the "Browse Files" button
    And I select the PDF file from the file dialog
    Then the file should be validated and added to the upload queue
    And the file should show status "Ready for processing"
    And the total file count should display "1 file selected"

  Scenario: Upload multiple PDF files for batch processing
    Given the interface is in "File Upload Mode"
    And I have multiple PDF files: "menu1.pdf", "menu2.pdf", "guide.pdf"
    When I select all three files through the file browser
    Then all files should be validated and added to the upload queue
    And each file should show individual status "Ready for processing"
    And the total file count should display "3 files selected"
    And I should be able to remove individual files from the queue

  Scenario: Reject invalid file types with user feedback
    Given the interface is in "File Upload Mode"
    When I try to upload a file "document.txt" that is not a PDF
    Then the file should be rejected with error message
    And the error should state "Only PDF, DOC, and DOCX files are supported"
    And the file should not appear in the upload queue
    And the interface should highlight the supported file types

  Scenario: Reject oversized files with user feedback
    Given the interface is in "File Upload Mode"
    When I try to upload a PDF file larger than 50MB
    Then the file should be rejected with error message
    And the error should state "File size exceeds 50MB limit"
    And the file should not appear in the upload queue
    And the interface should show the current file size and limit

  Scenario: Process uploaded PDF files and extract restaurant data
    Given the interface is in "File Upload Mode"
    And I have uploaded a PDF file "restaurant_menu.pdf"
    And the file is in the upload queue with status "Ready for processing"
    When I click the "Process Files" button
    Then the file should be uploaded to the server
    And the server should extract text from the PDF using OCR/PDF parsing
    And the extracted text should be processed through WTEG schema mapping
    And restaurant data should be identified (name, address, phone, menu items)
    And the results should be displayed in the same format as URL scraping
    And I should be able to export the results to Text/PDF/JSON formats

  Scenario: Show upload progress for large files
    Given the interface is in "File Upload Mode"
    And I have uploaded a large PDF file (> 10MB)
    When I click the "Process Files" button
    Then a progress bar should appear showing upload progress
    And the progress should update in real-time (0% to 100%)
    And the status should change from "Uploading..." to "Processing..." to "Complete"
    And estimated time remaining should be displayed during upload

  Scenario: Handle file upload errors gracefully
    Given the interface is in "File Upload Mode"
    And I have uploaded a PDF file "corrupted_menu.pdf"
    When I click the "Process Files" button
    And the file upload fails due to network error
    Then an error message should be displayed
    And the error should state "Upload failed: Network error. Please try again."
    And I should have the option to retry the upload
    And the file should remain in the queue for retry

  Scenario: Handle PDF processing errors gracefully
    Given the interface is in "File Upload Mode"
    And I have uploaded a PDF file "encrypted_menu.pdf" that is password-protected
    When I click the "Process Files" button
    And the PDF cannot be processed due to encryption
    Then an error message should be displayed
    And the error should state "Cannot process password-protected PDF. Please provide an unlocked version."
    And the file should be marked as "Failed" in the queue
    And I should be able to remove the failed file and try again

  Scenario: Clear upload queue and start over
    Given the interface is in "File Upload Mode"
    And I have multiple files in the upload queue
    When I click the "Clear All" button
    Then all files should be removed from the upload queue
    And the queue should show "No files selected"
    And the total file count should reset to 0

  Scenario: Switch back to URL mode without losing progress
    Given the interface is in "File Upload Mode"
    And I have processed files with extracted data displayed
    When I click the "URL Mode" toggle
    Then the file upload area should be hidden
    And the URL input area should be displayed
    And the previously extracted data should remain visible
    And I should be able to export the existing results

  Scenario: Validate file security before processing
    Given the interface is in "File Upload Mode"
    And I have uploaded a PDF file "suspicious_menu.pdf"
    When I click the "Process Files" button
    Then the file should be scanned for malware (if security scanning is enabled)
    And only clean files should proceed to text extraction
    And if malware is detected, the file should be rejected with appropriate error
    And the infected file should be safely removed from temporary storage