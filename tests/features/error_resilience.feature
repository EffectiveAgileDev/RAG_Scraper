Feature: Error Resilience and Recovery
  As a RAG system user
  I want scraping to continue despite errors
  So that I get partial results even when some sites fail

  Background:
    Given I have initialized the scraping engine
    And I have configured error handling settings
    And I have test websites with various failure scenarios

  Scenario: Network timeout handling
    Given I have a restaurant website that takes 45 seconds to respond
    And the timeout is set to 30 seconds
    When I attempt to scrape the website
    Then the request should timeout after 30 seconds
    And the error should be logged with "timeout" reason
    And other URLs in the batch should continue processing
    And the final report should indicate the timeout failure

  Scenario: HTTP error response handling
    Given I have a restaurant website that returns 404 Not Found
    When I attempt to scrape the website
    Then the 404 error should be handled gracefully
    And the error should be logged with "not found" reason
    And other URLs in the batch should continue processing
    And no partial data should be saved for the failed URL

  Scenario: Malformed HTML recovery
    Given I have a restaurant website with broken HTML structure
    And the HTML has unclosed tags and invalid syntax
    When I attempt to scrape the website
    Then the HTML parser should handle the malformed content
    And extraction should continue with available data
    And partial results should be saved if any data is found
    And warnings should be logged about HTML quality

  Scenario: Missing structured data graceful degradation
    Given I have a restaurant website with no JSON-LD data
    And no microdata is present on the page
    When I extract data using structured strategies
    Then structured extraction should fail gracefully
    And heuristic extraction should be attempted automatically
    And any found data should be returned with appropriate confidence
    And the extraction method should be documented in results

  Scenario: Rate limiting response handling
    Given I have a restaurant website that returns 429 Too Many Requests
    When I attempt to scrape the website
    Then the scraper should respect the rate limiting
    And it should wait before retrying the request
    And it should retry up to 3 times with exponential backoff
    And if all retries fail, it should log the rate limiting issue

  Scenario: Memory management during large batch processing
    Given I have a batch of 100 restaurant URLs to process
    And some websites have very large HTML content
    When I process the entire batch
    Then memory usage should remain within reasonable limits
    And large pages should be processed in chunks if needed
    And memory should be freed after each URL processing
    And the system should not run out of memory

  Scenario: Connection refused handling
    Given I have a restaurant website that refuses connections
    When I attempt to scrape the website
    Then the connection refusal should be handled gracefully
    And the error should be logged with "connection refused" reason
    And other URLs should continue processing normally
    And no retry attempts should be made for connection refusal

  Scenario: SSL certificate error handling
    Given I have a restaurant website with invalid SSL certificate
    When I attempt to scrape the website
    Then the SSL error should be handled appropriately
    And the user should be notified about the security issue
    And the URL should be skipped for security reasons
    And alternative HTTP access should not be attempted automatically

  Scenario: Redirect loop detection and prevention
    Given I have a restaurant website with infinite redirect loops
    When I attempt to scrape the website
    Then the redirect loop should be detected after 5 redirects
    And the scraping should be terminated to prevent infinite loops
    And the error should be logged with "redirect loop" reason
    And other URLs should continue processing

  Scenario: JavaScript-dependent content handling
    Given I have a restaurant website that requires JavaScript to load content
    And the scraper is configured for static HTML only
    When I attempt to scrape the website
    Then static content should be extracted if available
    And missing dynamic content should be noted in the report
    And the limitation should be logged for user awareness
    And partial results should be saved with confidence indicators

  Scenario: Encoding and character set issues
    Given I have a restaurant website with mixed character encodings
    And some text contains special characters and emojis
    When I extract text content from the website
    Then character encoding should be detected automatically
    And special characters should be preserved correctly
    And encoding errors should be handled gracefully
    And the final output should maintain UTF-8 consistency

  Scenario: Partial page load failures
    Given I have a restaurant website where some resources fail to load
    And the main content loads but images and CSS fail
    When I attempt to scrape the website
    Then text content should be extracted successfully
    And missing resources should not prevent data extraction
    And the extraction should focus on textual information
    And warnings about missing resources should be logged

  Scenario: Database and file system error recovery
    Given I am processing a batch of restaurant URLs
    And the output directory becomes read-only during processing
    When I attempt to save extracted data
    Then the file system error should be detected
    And the user should be notified about the permission issue
    And data should be held in memory until the issue is resolved
    And alternative save locations should be suggested

  Scenario: Concurrent processing error isolation
    Given I am processing multiple restaurant URLs simultaneously
    And one URL causes a critical error in its processing thread
    When the error occurs during concurrent processing
    Then the error should be isolated to that specific thread
    And other concurrent processes should continue normally
    And the failed URL should be marked as failed
    And the error details should be captured for debugging

  Scenario: Resource cleanup after errors
    Given I have processed a batch with several failed URLs
    When the batch processing completes with mixed success
    Then all network connections should be properly closed
    And temporary files should be cleaned up
    And memory should be freed from failed processing attempts
    And system resources should be returned to the initial state

  Scenario: Error reporting and user feedback
    Given I have processed a batch with various types of failures
    When the batch processing completes
    Then a comprehensive error report should be generated
    And each failure should include the URL and specific error reason
    And successful extractions should be clearly indicated
    And suggestions for resolving common errors should be provided
    And the report should be saved alongside the extracted data