Feature: Single-Page Multi-Page Feature Integration
  As a RAG system developer
  I want to seamlessly integrate single-page and multi-page scraping capabilities
  So that users can switch between modes with consistent functionality

  Background:
    Given the RAG Scraper web interface is running
    And the scraping configuration is initialized
    And the progress monitoring system is active

  Scenario: JavaScript rendering works in single-page mode
    Given I am on the single-page scraping interface
    And I have a restaurant URL with JavaScript content "https://restaurant-with-js.com"
    And the JavaScript rendering is enabled
    When I submit the URL for single-page processing
    Then the JavaScript content should be rendered properly
    And the extracted data should include JavaScript-loaded content
    And the progress should show JavaScript rendering completion
    And the processing should complete successfully

  Scenario: JavaScript rendering integrates with multi-page mode
    Given I am on the multi-page scraping interface
    And I have multiple restaurant URLs with JavaScript content
    And the JavaScript rendering is enabled in multi-page mode
    When I submit the URLs for multi-page processing
    Then each URL should be processed with JavaScript rendering
    And the batch progress should track JavaScript rendering for each URL
    And all JavaScript-loaded content should be extracted
    And the processing should complete successfully for all URLs

  Scenario: Advanced progress monitoring shows detailed single-page progress
    Given I am on the single-page scraping interface
    And I have a restaurant URL "https://restaurant-example.com"
    And advanced progress monitoring is enabled
    When I submit the URL for processing
    Then the progress should show initialization phase
    And the progress should show page loading phase
    And the progress should show JavaScript rendering phase (if enabled)
    And the progress should show data extraction phase
    And the progress should show completion phase
    And each phase should have accurate time estimates
    And memory usage should be tracked throughout

  Scenario: Advanced progress monitoring works in multi-page batch mode
    Given I am on the multi-page scraping interface
    And I have multiple restaurant URLs for batch processing
    And advanced progress monitoring is enabled
    When I submit the URLs for batch processing
    Then the progress should show overall batch progress
    And the progress should show individual URL progress
    And the progress should show memory usage warnings if applicable
    And the progress should show time estimates for batch completion
    And the progress should track failed URLs separately
    And the progress should show final statistics

  Scenario: Enhanced error handling recovers from JavaScript failures
    Given I am on the single-page scraping interface
    And I have a restaurant URL with problematic JavaScript "https://broken-js-restaurant.com"
    And enhanced error handling is enabled
    When I submit the URL for processing
    And the JavaScript rendering fails
    Then the system should detect the JavaScript failure
    And the system should retry with fallback strategies
    And the system should provide detailed error information
    And the system should still extract available data
    And the user should be notified of the partial failure

  Scenario: Enhanced error handling works across single-page and multi-page modes
    Given I am processing URLs in both single-page and multi-page modes
    And enhanced error handling is enabled
    When various errors occur during processing
    Then the error handling should be consistent across both modes
    And the error recovery strategies should work in both modes
    And the error reporting should be unified
    And the user experience should be consistent

  Scenario: Configurable extraction options work in single-page mode
    Given I am on the single-page scraping interface
    And I have a restaurant URL "https://restaurant-example.com"
    And I configure extraction options for specific fields
    When I submit the URL with custom extraction configuration
    Then only the configured fields should be extracted
    And the extraction should respect the field priorities
    And the processing should be optimized for selected fields
    And the results should match the configured output format

  Scenario: Configurable extraction options integrate with multi-page mode
    Given I am on the multi-page scraping interface
    And I have multiple restaurant URLs
    And I configure extraction options for batch processing
    When I submit the URLs with custom extraction configuration
    Then all URLs should be processed with the same configuration
    And the batch results should be consistent
    And the extraction should respect global and per-URL settings
    And the output format should be applied consistently

  Scenario: Rate limiting and ethics work in single-page mode
    Given I am on the single-page scraping interface
    And I have a restaurant URL "https://restaurant-example.com"
    And rate limiting is configured for ethical scraping
    When I submit the URL for processing
    Then the system should check robots.txt compliance
    And the system should apply appropriate delays
    And the system should use proper user agent headers
    And the system should respect server rate limits
    And the processing should be ethical and compliant

  Scenario: Rate limiting and ethics integrate with multi-page mode
    Given I am on the multi-page scraping interface
    And I have multiple restaurant URLs from different domains
    And rate limiting is configured for ethical scraping
    When I submit the URLs for batch processing
    Then the system should apply per-domain rate limiting
    And the system should check robots.txt for each domain
    And the system should stagger requests appropriately
    And the system should handle rate limit responses gracefully
    And the processing should maintain ethical compliance

  Scenario: Seamless mode switching preserves configuration
    Given I am on the single-page scraping interface
    And I have configured specific extraction options
    And I have set JavaScript rendering preferences
    And I have configured rate limiting settings
    When I switch to multi-page mode
    Then all my configuration should be preserved
    And the settings should work in multi-page mode
    And I should be able to switch back to single-page mode
    And the configuration should remain consistent

  Scenario: Unified progress and error reporting across modes
    Given I am using both single-page and multi-page modes
    And I have processed URLs in both modes
    When I view the processing history
    Then I should see unified progress reports
    And I should see consistent error reporting
    And I should see performance metrics for both modes
    And I should be able to compare results across modes
    And the reporting should be integrated and coherent

  Scenario: Performance optimization works across both modes
    Given I am processing restaurant URLs in both modes
    And performance optimization is enabled
    When I process URLs in single-page mode
    Then the processing should be optimized for single URL
    And memory usage should be minimized
    And JavaScript rendering should be efficient
    When I process URLs in multi-page mode
    Then the processing should be optimized for batch operations
    And memory usage should be managed across URLs
    And JavaScript rendering should be batched efficiently
    And the performance should be consistent across modes