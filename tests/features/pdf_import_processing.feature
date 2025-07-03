Feature: PDF Import Processing - Secure Download and Caching
  As a RAG Scraper user
  I want to securely download and cache restaurant guide PDFs
  So that I can extract complete restaurant data from PDF-based guides

  Background:
    Given the RAG Scraper is running
    And the PDF import processing system is enabled
    And I have valid authentication credentials for PDF sources

  Scenario: Successfully download and cache a restaurant guide PDF
    Given I have a valid PDF URL "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
    When I request to download the PDF
    Then the PDF should be downloaded securely with authentication
    And the PDF should be cached locally with expiration policy
    And the cached PDF should pass integrity validation
    And the download should complete within 30 seconds

  Scenario: Retrieve PDF from cache when already downloaded
    Given I have a valid PDF URL "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
    And the PDF is already cached and not expired
    When I request to download the PDF
    Then the PDF should be retrieved from cache
    And no external download should be attempted
    And the response should be instant (< 1 second)

  Scenario: Re-download PDF when cache is expired
    Given I have a valid PDF URL "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
    And the PDF is cached but expired
    When I request to download the PDF
    Then the expired cache should be cleared
    And a fresh PDF should be downloaded with authentication
    And the new PDF should be cached with updated expiration

  Scenario: Handle authentication failure during PDF download
    Given I have a PDF URL requiring authentication
    And my authentication credentials are invalid
    When I request to download the PDF
    Then the download should fail with authentication error
    And no corrupted data should be cached
    And the error should be logged with details

  Scenario: Handle network failure during PDF download
    Given I have a valid PDF URL "https://mobimag.co/wteg/portland/restaurant_guide.pdf"
    And the network connection is unreliable
    When I request to download the PDF
    Then the download should retry with exponential backoff
    And the system should attempt up to 3 retries
    And if all retries fail, appropriate error should be returned

  Scenario: Detect and reject corrupted PDF files
    Given I have a PDF URL that returns corrupted data
    When I request to download the PDF
    Then the PDF integrity validation should fail
    And the corrupted data should not be cached
    And the error should indicate corruption detected

  Scenario: Manage cache storage limits
    Given the PDF cache directory is near storage limit
    When I request to download a new PDF
    Then the oldest cached PDFs should be removed first
    And the cache size should stay within configured limits
    And the new PDF should be cached successfully

  Scenario: Handle concurrent PDF download requests
    Given I have multiple PDF URLs to download simultaneously
    When I request to download all PDFs concurrently
    Then each download should be handled independently
    And authentication should work for each request
    And cache should handle concurrent writes safely
    And all PDFs should be downloaded without conflicts