Feature: Enhanced Rate Limiting
  As a RAG system administrator
  I want enhanced rate limiting capabilities for multi-page scraping
  So that the system respects server limits and avoids being blocked

  Background:
    Given the RAG_Scraper web interface is running
    And I have access to the enhanced rate limiting system
    And the rate limiting system is initialized

  @rate_limiting @multi_page
  Scenario: Per-domain rate limiting for multi-page scraping
    Given I have restaurant URLs from 3 different domains:
      | domain                | urls | rate_limit |
      | fast-restaurants.com  | 4    | 1.0        |
      | slow-restaurants.com  | 3    | 3.0        |
      | mixed-restaurants.com | 5    | 2.0        |
    And per-domain rate limiting is enabled
    When I start multi-page scraping across all domains
    Then each domain should be rate limited independently
    And fast-restaurants.com requests should be limited to 1 request per second
    And slow-restaurants.com requests should be limited to 1 request per 3 seconds
    And mixed-restaurants.com requests should be limited to 1 request per 2 seconds
    And concurrent processing should respect per-domain limits
    And the total scraping time should reflect domain-specific delays

  @rate_limiting @exponential_backoff
  Scenario: Exponential backoff for failed requests
    Given I have a restaurant website that returns 503 Service Unavailable
    And exponential backoff is enabled with base delay of 1 second
    When I attempt to scrape the website with retry enabled
    Then the first retry should wait 1 second
    And the second retry should wait 2 seconds
    And the third retry should wait 4 seconds
    And the fourth retry should wait 8 seconds
    And the maximum backoff should not exceed 60 seconds
    And failed requests should be logged with retry attempt details

  @rate_limiting @retry_after
  Scenario: Respect retry-after headers from servers
    Given I have a restaurant website that returns 429 Too Many Requests
    And the server includes "Retry-After: 10" header
    When I attempt to scrape the website
    Then the scraper should wait exactly 10 seconds before retrying
    And the retry-after value should override default rate limiting
    And the retry attempt should be logged with the server-specified delay
    And subsequent requests should resume normal rate limiting

  @rate_limiting @domain_throttling
  Scenario: Domain-specific throttling rules configuration
    Given I have configured domain-specific throttling rules:
      | domain_pattern        | delay | max_concurrent | retry_limit |
      | *.example.com         | 2.0   | 2              | 3           |
      | restaurant-chain.*    | 0.5   | 5              | 5           |
      | slow-server.com       | 5.0   | 1              | 2           |
      | default               | 1.5   | 3              | 4           |
    When I scrape URLs matching these domain patterns
    Then each domain should follow its specific throttling rules
    And max concurrent requests should be enforced per domain
    And retry limits should be respected per domain
    And default rules should apply to unmatched domains

  @rate_limiting @concurrent_domains
  Scenario: Concurrent request rate limiting across domains
    Given I have 15 restaurant URLs across 5 different domains
    And concurrent rate limiting is enabled with 3 max concurrent requests per domain
    When I start multi-page scraping with concurrent processing
    Then no more than 3 requests should be active per domain at any time
    And requests should be queued when domain limits are reached
    And different domains should be processed independently
    And total active requests should not exceed system-wide limits
    And domain-specific delays should still be enforced

  @rate_limiting @recovery
  Scenario: Rate limit recovery after temporary blocks
    Given I have a restaurant website that temporarily blocks requests
    And the website returns 429 status for 5 requests
    And then resumes normal operation
    When I continue scraping after the temporary block
    Then the rate limiter should detect the block recovery
    And requests should resume with normal rate limiting
    And the block period should be logged for analysis
    And no requests should be lost during the recovery

  @rate_limiting @adaptive
  Scenario: Adaptive rate limiting based on server response times
    Given I have restaurant websites with varying response times:
      | website        | avg_response_time |
      | fast-site.com  | 200ms            |
      | slow-site.com  | 2000ms           |
      | mixed-site.com | 800ms            |
    And adaptive rate limiting is enabled
    When I scrape these websites over time
    Then rate limits should adapt to server response times
    And fast servers should allow higher request rates
    And slow servers should have increased delays
    And adaptation should happen gradually over multiple requests
    And rate limit adjustments should be logged

  @rate_limiting @multi_page_integration
  Scenario: Rate limiting integration with multi-page navigation
    Given I have a restaurant website with 8 discoverable pages
    And multi-page navigation is enabled
    And rate limiting is configured with 2-second delays
    When I start multi-page scraping with page discovery
    Then rate limiting should apply to all discovered pages
    And page discovery requests should be rate limited
    And data extraction requests should be rate limited
    And the total scraping time should reflect rate limiting delays
    And progress tracking should account for rate limiting delays

  @rate_limiting @configuration
  Scenario: Rate limiting configuration validation and defaults
    Given I have various rate limiting configurations
    When I configure rate limiting with invalid settings:
      | setting           | value | expected_result |
      | negative_delay    | -1.0  | validation_error |
      | zero_max_requests | 0     | validation_error |
      | excessive_delay   | 3600  | capped_to_limit  |
    Then invalid configurations should be rejected with clear error messages
    And excessive values should be capped to safe limits
    And default configurations should be applied for missing settings
    And configuration validation should prevent system instability

  @rate_limiting @monitoring
  Scenario: Rate limiting monitoring and statistics
    Given I have enabled rate limiting monitoring
    And I am processing multiple restaurant websites
    When scraping operations complete
    Then I should see detailed rate limiting statistics:
      | metric                    | tracked |
      | total_requests_made       | yes     |
      | total_delay_time          | yes     |
      | average_delay_per_domain  | yes     |
      | retry_attempts_by_reason  | yes     |
      | rate_limit_violations     | yes     |
    And statistics should be exportable for analysis
    And rate limiting effectiveness should be measurable

  @rate_limiting @emergency_override
  Scenario: Emergency rate limiting override for critical operations
    Given I have enabled emergency rate limiting override
    And I have a critical scraping operation that must complete quickly
    When I enable emergency override mode
    Then rate limiting should be temporarily disabled or reduced
    And override mode should have a maximum duration limit
    And emergency usage should be logged for audit purposes
    And normal rate limiting should resume automatically after override expires
    And emergency overrides should require explicit authorization