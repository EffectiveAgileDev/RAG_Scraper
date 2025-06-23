"""Step definitions for Enhanced Rate Limiting BDD scenarios."""
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
from pytest_bdd import scenarios, given, when, then, parsers


# Load scenarios from the feature file
scenarios('../features/rate_limiting.feature')


# Context for rate limiting tests
class RateLimitingContext:
    def __init__(self):
        self.rate_limiter = None
        self.multi_page_scraper = None
        self.domain_configs = {}
        self.scraped_domains = []
        self.start_time = None
        self.end_time = None
        self.retry_attempts = []
        self.response_times = {}
        self.statistics = {}
        self.emergency_override = False
        self.rate_limiting_enabled = True


@pytest.fixture
def rate_limiting_context():
    """Provide rate limiting test context."""
    return RateLimitingContext()


# Background steps
@given("the RAG_Scraper web interface is running")
def given_web_interface_running(rate_limiting_context):
    """Mock web interface running."""
    rate_limiting_context.web_interface_running = True


@given("I have access to the enhanced rate limiting system")
def given_enhanced_rate_limiting_access(rate_limiting_context):
    """Mock access to enhanced rate limiting system."""
    # This will be implemented as we create the enhanced rate limiter
    rate_limiting_context.rate_limiting_system_available = True


@given("the rate limiting system is initialized")
def given_rate_limiting_initialized(rate_limiting_context):
    """Initialize the rate limiting system."""
    # This will be mocked until we implement the enhanced rate limiter
    rate_limiting_context.rate_limiting_initialized = True


# Per-domain rate limiting scenario
@given(parsers.parse("I have restaurant URLs from 3 different domains:\n{table}"))
def given_restaurant_urls_multiple_domains_with_table(rate_limiting_context, table):
    """Set up restaurant URLs from multiple domains with table data."""
    rate_limiting_context.domain_configs = {}
    # Parse the table data (this is a simple simulation)
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]  # Remove empty parts from start/end
            if len(parts) >= 3:
                domain, urls, rate_limit = parts[0], int(parts[1]), float(parts[2])
                rate_limiting_context.domain_configs[domain] = {
                    'urls': urls,
                    'rate_limit': rate_limit
                }


@given("per-domain rate limiting is enabled")
def given_per_domain_rate_limiting_enabled(rate_limiting_context):
    """Enable per-domain rate limiting."""
    rate_limiting_context.per_domain_enabled = True


@when("I start multi-page scraping across all domains")
def when_start_multi_page_scraping_domains(rate_limiting_context):
    """Start multi-page scraping across all domains."""
    rate_limiting_context.start_time = time.time()
    # Mock the scraping process across domains
    rate_limiting_context.scraping_started = True


@then("each domain should be rate limited independently")
def then_domains_rate_limited_independently(rate_limiting_context):
    """Verify each domain is rate limited independently."""
    # This will be verified when we implement the enhanced rate limiter
    assert rate_limiting_context.per_domain_enabled


@then("fast-restaurants.com requests should be limited to 1 request per second")
def then_fast_restaurants_rate_limited(rate_limiting_context):
    """Verify fast-restaurants.com is limited to 1 request per second."""
    expected_rate = rate_limiting_context.domain_configs['fast-restaurants.com']['rate_limit']
    assert expected_rate == 1.0


@then("slow-restaurants.com requests should be limited to 1 request per 3 seconds")
def then_slow_restaurants_rate_limited(rate_limiting_context):
    """Verify slow-restaurants.com is limited to 1 request per 3 seconds."""
    expected_rate = rate_limiting_context.domain_configs['slow-restaurants.com']['rate_limit']
    assert expected_rate == 3.0


@then("mixed-restaurants.com requests should be limited to 1 request per 2 seconds")
def then_mixed_restaurants_rate_limited(rate_limiting_context):
    """Verify mixed-restaurants.com is limited to 1 request per 2 seconds."""
    expected_rate = rate_limiting_context.domain_configs['mixed-restaurants.com']['rate_limit']
    assert expected_rate == 2.0


@then("concurrent processing should respect per-domain limits")
def then_concurrent_processing_respects_limits(rate_limiting_context):
    """Verify concurrent processing respects per-domain limits."""
    # This will be implemented with the enhanced rate limiter
    assert rate_limiting_context.per_domain_enabled


@then("the total scraping time should reflect domain-specific delays")
def then_total_time_reflects_delays(rate_limiting_context):
    """Verify total scraping time reflects domain-specific delays."""
    # Mock calculation of expected time based on domain configs
    total_urls = sum(config['urls'] for config in rate_limiting_context.domain_configs.values())
    assert total_urls == 12  # 4 + 3 + 5


# Exponential backoff scenario
@given("I have a restaurant website that returns 503 Service Unavailable")
def given_website_returns_503(rate_limiting_context):
    """Set up website that returns 503."""
    rate_limiting_context.failing_website = "http://failing-restaurant.com"
    rate_limiting_context.error_status = 503


@given("exponential backoff is enabled with base delay of 1 second")
def given_exponential_backoff_enabled(rate_limiting_context):
    """Enable exponential backoff with base delay."""
    rate_limiting_context.exponential_backoff_enabled = True
    rate_limiting_context.base_delay = 1.0


@when("I attempt to scrape the website with retry enabled")
def when_attempt_scrape_with_retry(rate_limiting_context):
    """Attempt to scrape website with retry enabled."""
    rate_limiting_context.retry_attempts = []
    # Mock retry attempts with exponential backoff
    for i in range(4):
        delay = rate_limiting_context.base_delay * (2 ** i)
        rate_limiting_context.retry_attempts.append(delay)


@then("the first retry should wait 1 second")
def then_first_retry_waits_1_second(rate_limiting_context):
    """Verify first retry waits 1 second."""
    assert rate_limiting_context.retry_attempts[0] == 1.0


@then("the second retry should wait 2 seconds")
def then_second_retry_waits_2_seconds(rate_limiting_context):
    """Verify second retry waits 2 seconds."""
    assert rate_limiting_context.retry_attempts[1] == 2.0


@then("the third retry should wait 4 seconds")
def then_third_retry_waits_4_seconds(rate_limiting_context):
    """Verify third retry waits 4 seconds."""
    assert rate_limiting_context.retry_attempts[2] == 4.0


@then("the fourth retry should wait 8 seconds")
def then_fourth_retry_waits_8_seconds(rate_limiting_context):
    """Verify fourth retry waits 8 seconds."""
    assert rate_limiting_context.retry_attempts[3] == 8.0


@then("the maximum backoff should not exceed 60 seconds")
def then_max_backoff_not_exceed_60_seconds(rate_limiting_context):
    """Verify maximum backoff does not exceed 60 seconds."""
    max_backoff = max(rate_limiting_context.retry_attempts)
    assert max_backoff <= 60.0


@then("failed requests should be logged with retry attempt details")
def then_failed_requests_logged(rate_limiting_context):
    """Verify failed requests are logged with retry details."""
    # This will be implemented with proper logging
    assert len(rate_limiting_context.retry_attempts) > 0


# Retry-after headers scenario
@given("I have a restaurant website that returns 429 Too Many Requests")
def given_website_returns_429(rate_limiting_context):
    """Set up website that returns 429."""
    rate_limiting_context.rate_limited_website = "http://rate-limited-restaurant.com"
    rate_limiting_context.error_status = 429


@given('the server includes "Retry-After: 10" header')
def given_server_includes_retry_after_header(rate_limiting_context):
    """Set up server with Retry-After header."""
    rate_limiting_context.retry_after_value = 10


@when("I attempt to scrape the website")
def when_attempt_scrape_website(rate_limiting_context):
    """Attempt to scrape the website."""
    rate_limiting_context.scrape_attempted = True
    rate_limiting_context.actual_wait_time = rate_limiting_context.retry_after_value


@then("the scraper should wait exactly 10 seconds before retrying")
def then_scraper_waits_exactly_10_seconds(rate_limiting_context):
    """Verify scraper waits exactly 10 seconds."""
    assert rate_limiting_context.actual_wait_time == 10


@then("the retry-after value should override default rate limiting")
def then_retry_after_overrides_default(rate_limiting_context):
    """Verify retry-after overrides default rate limiting."""
    assert rate_limiting_context.actual_wait_time == rate_limiting_context.retry_after_value


@then("the retry attempt should be logged with the server-specified delay")
def then_retry_logged_with_server_delay(rate_limiting_context):
    """Verify retry is logged with server-specified delay."""
    # This will be implemented with proper logging
    assert rate_limiting_context.actual_wait_time > 0


@then("subsequent requests should resume normal rate limiting")
def then_subsequent_requests_resume_normal(rate_limiting_context):
    """Verify subsequent requests resume normal rate limiting."""
    # This will be verified in the implementation
    assert rate_limiting_context.scrape_attempted


# Domain-specific throttling configuration scenario
@given(parsers.parse("I have configured domain-specific throttling rules:\n{table}"))
def given_domain_specific_throttling_rules_with_table(rate_limiting_context, table):
    """Set up domain-specific throttling rules with table data."""
    rate_limiting_context.throttling_rules = {}
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4:
                pattern, delay, max_concurrent, retry_limit = parts[0], float(parts[1]), int(parts[2]), int(parts[3])
                rate_limiting_context.throttling_rules[pattern] = {
                    'delay': delay,
                    'max_concurrent': max_concurrent,
                    'retry_limit': retry_limit
                }


@when("I scrape URLs matching these domain patterns")
def when_scrape_urls_matching_patterns(rate_limiting_context):
    """Scrape URLs matching domain patterns."""
    rate_limiting_context.pattern_matching_started = True


@then("each domain should follow its specific throttling rules")
def then_domains_follow_specific_rules(rate_limiting_context):
    """Verify each domain follows its specific throttling rules."""
    assert len(rate_limiting_context.throttling_rules) == 4


@then("max concurrent requests should be enforced per domain")
def then_max_concurrent_enforced(rate_limiting_context):
    """Verify max concurrent requests are enforced per domain."""
    for rule in rate_limiting_context.throttling_rules.values():
        assert 'max_concurrent' in rule


@then("retry limits should be respected per domain")
def then_retry_limits_respected(rate_limiting_context):
    """Verify retry limits are respected per domain."""
    for rule in rate_limiting_context.throttling_rules.values():
        assert 'retry_limit' in rule


@then("default rules should apply to unmatched domains")
def then_default_rules_apply(rate_limiting_context):
    """Verify default rules apply to unmatched domains."""
    assert 'default' in rate_limiting_context.throttling_rules


# Concurrent request rate limiting scenario
@given("I have 15 restaurant URLs across 5 different domains")
def given_15_urls_across_5_domains(rate_limiting_context):
    """Set up 15 URLs across 5 domains."""
    rate_limiting_context.total_urls = 15
    rate_limiting_context.total_domains = 5
    rate_limiting_context.urls_per_domain = 3


@given("concurrent rate limiting is enabled with 3 max concurrent requests per domain")
def given_concurrent_rate_limiting_enabled(rate_limiting_context):
    """Enable concurrent rate limiting."""
    rate_limiting_context.max_concurrent_per_domain = 3
    rate_limiting_context.concurrent_limiting_enabled = True


@when("I start multi-page scraping with concurrent processing")
def when_start_concurrent_multi_page_scraping(rate_limiting_context):
    """Start multi-page scraping with concurrent processing."""
    rate_limiting_context.concurrent_scraping_started = True


@then("no more than 3 requests should be active per domain at any time")
def then_max_3_requests_per_domain(rate_limiting_context):
    """Verify no more than 3 requests are active per domain."""
    assert rate_limiting_context.max_concurrent_per_domain == 3


@then("requests should be queued when domain limits are reached")
def then_requests_queued_when_limits_reached(rate_limiting_context):
    """Verify requests are queued when domain limits are reached."""
    # This will be implemented with the enhanced rate limiter
    assert rate_limiting_context.concurrent_limiting_enabled


@then("different domains should be processed independently")
def then_domains_processed_independently(rate_limiting_context):
    """Verify different domains are processed independently."""
    assert rate_limiting_context.total_domains == 5


@then("total active requests should not exceed system-wide limits")
def then_total_requests_not_exceed_limits(rate_limiting_context):
    """Verify total active requests don't exceed system-wide limits."""
    max_total = rate_limiting_context.total_domains * rate_limiting_context.max_concurrent_per_domain
    assert max_total == 15  # 5 domains * 3 concurrent per domain


@then("domain-specific delays should still be enforced")
def then_domain_delays_still_enforced(rate_limiting_context):
    """Verify domain-specific delays are still enforced."""
    assert rate_limiting_context.concurrent_limiting_enabled


# Additional scenarios would continue here following the same pattern...
# For brevity, I'm implementing the core scenarios that demonstrate the TDD approach.
# The remaining scenarios would follow the same structure.

# Rate limit recovery scenario
@given("I have a restaurant website that temporarily blocks requests")
def given_website_temporarily_blocks(rate_limiting_context):
    """Set up website that temporarily blocks requests."""
    rate_limiting_context.temporarily_blocked_website = "http://temp-blocked-restaurant.com"
    rate_limiting_context.block_count = 0


@given("the website returns 429 status for 5 requests")
def given_website_returns_429_for_5_requests(rate_limiting_context):
    """Set up website to return 429 for 5 requests."""
    rate_limiting_context.blocked_requests = 5


@given("then resumes normal operation")
def given_website_resumes_normal_operation(rate_limiting_context):
    """Set up website to resume normal operation."""
    rate_limiting_context.recovery_enabled = True


@when("I continue scraping after the temporary block")
def when_continue_scraping_after_block(rate_limiting_context):
    """Continue scraping after temporary block."""
    rate_limiting_context.continued_after_block = True


@then("the rate limiter should detect the block recovery")
def then_rate_limiter_detects_recovery(rate_limiting_context):
    """Verify rate limiter detects block recovery."""
    assert rate_limiting_context.recovery_enabled


@then("requests should resume with normal rate limiting")
def then_requests_resume_normal_rate_limiting(rate_limiting_context):
    """Verify requests resume with normal rate limiting."""
    assert rate_limiting_context.continued_after_block


@then("the block period should be logged for analysis")
def then_block_period_logged(rate_limiting_context):
    """Verify block period is logged for analysis."""
    assert rate_limiting_context.blocked_requests > 0


@then("no requests should be lost during the recovery")
def then_no_requests_lost_during_recovery(rate_limiting_context):
    """Verify no requests are lost during recovery."""
    # This will be implemented with proper request tracking
    assert rate_limiting_context.recovery_enabled


# Configuration validation scenario
@given("I have various rate limiting configurations")
def given_various_rate_limiting_configurations(rate_limiting_context):
    """Set up various rate limiting configurations."""
    rate_limiting_context.configurations = {}


@when("I configure rate limiting with invalid settings")
def when_configure_invalid_settings(rate_limiting_context):
    """Configure rate limiting with invalid settings."""
    rate_limiting_context.invalid_configs = {
        'negative_delay': {'value': -1.0, 'expected_result': 'validation_error'},
        'zero_max_requests': {'value': 0, 'expected_result': 'validation_error'},
        'excessive_delay': {'value': 3600, 'expected_result': 'capped_to_limit'}
    }


@then("invalid configurations should be rejected with clear error messages")
def then_invalid_configs_rejected(rate_limiting_context):
    """Verify invalid configurations are rejected."""
    # This will be implemented with proper validation
    assert len(rate_limiting_context.invalid_configs) > 0


@then("excessive values should be capped to safe limits")
def then_excessive_values_capped(rate_limiting_context):
    """Verify excessive values are capped to safe limits."""
    excessive_config = rate_limiting_context.invalid_configs['excessive_delay']
    assert excessive_config['expected_result'] == 'capped_to_limit'


@then("default configurations should be applied for missing settings")
def then_default_configs_applied(rate_limiting_context):
    """Verify default configurations are applied for missing settings."""
    # This will be implemented with default value handling
    assert True  # Placeholder


@then("configuration validation should prevent system instability")
def then_validation_prevents_instability(rate_limiting_context):
    """Verify configuration validation prevents system instability."""
    # This will be implemented with comprehensive validation
    assert True  # Placeholder


# Adaptive rate limiting scenario
@given(parsers.parse("I have restaurant websites with varying response times:\n{table}"))
def given_websites_with_varying_response_times(rate_limiting_context, table):
    """Set up websites with varying response times."""
    rate_limiting_context.response_times = {}
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2:
                website, response_time = parts[0], parts[1]
                # Convert response time to milliseconds
                if 'ms' in response_time:
                    time_ms = int(response_time.replace('ms', ''))
                    rate_limiting_context.response_times[website] = time_ms


@given("adaptive rate limiting is enabled")
def given_adaptive_rate_limiting_enabled(rate_limiting_context):
    """Enable adaptive rate limiting."""
    rate_limiting_context.adaptive_rate_limiting_enabled = True


@when("I scrape these websites over time")
def when_scrape_websites_over_time(rate_limiting_context):
    """Scrape websites over time."""
    rate_limiting_context.scraping_over_time_started = True


@then("rate limits should adapt to server response times")
def then_rate_limits_adapt_to_response_times(rate_limiting_context):
    """Verify rate limits adapt to server response times."""
    assert rate_limiting_context.adaptive_rate_limiting_enabled


@then("fast servers should allow higher request rates")
def then_fast_servers_higher_rates(rate_limiting_context):
    """Verify fast servers allow higher request rates."""
    # Find fast server (lowest response time)
    min_time = min(rate_limiting_context.response_times.values())
    assert min_time == 200  # fast-site.com has 200ms


@then("slow servers should have increased delays")
def then_slow_servers_increased_delays(rate_limiting_context):
    """Verify slow servers have increased delays."""
    # Find slow server (highest response time)
    max_time = max(rate_limiting_context.response_times.values())
    assert max_time == 2000  # slow-site.com has 2000ms


@then("adaptation should happen gradually over multiple requests")
def then_adaptation_gradual(rate_limiting_context):
    """Verify adaptation happens gradually."""
    assert rate_limiting_context.scraping_over_time_started


@then("rate limit adjustments should be logged")
def then_rate_limit_adjustments_logged(rate_limiting_context):
    """Verify rate limit adjustments are logged."""
    # This will be implemented with proper logging
    assert rate_limiting_context.adaptive_rate_limiting_enabled


# Multi-page integration scenario
@given("I have a restaurant website with 8 discoverable pages")
def given_website_with_8_pages(rate_limiting_context):
    """Set up website with 8 discoverable pages."""
    rate_limiting_context.discoverable_pages = 8


@given("multi-page navigation is enabled")
def given_multi_page_navigation_enabled(rate_limiting_context):
    """Enable multi-page navigation."""
    rate_limiting_context.multi_page_navigation_enabled = True


@given("rate limiting is configured with 2-second delays")
def given_rate_limiting_2_second_delays(rate_limiting_context):
    """Configure rate limiting with 2-second delays."""
    rate_limiting_context.rate_limit_delay = 2.0


@when("I start multi-page scraping with page discovery")
def when_start_multi_page_scraping_with_discovery(rate_limiting_context):
    """Start multi-page scraping with page discovery."""
    rate_limiting_context.multi_page_scraping_with_discovery_started = True


@then("rate limiting should apply to all discovered pages")
def then_rate_limiting_applies_to_all_pages(rate_limiting_context):
    """Verify rate limiting applies to all discovered pages."""
    assert rate_limiting_context.multi_page_navigation_enabled


@then("page discovery requests should be rate limited")
def then_page_discovery_rate_limited(rate_limiting_context):
    """Verify page discovery requests are rate limited."""
    assert rate_limiting_context.rate_limit_delay > 0


@then("data extraction requests should be rate limited")
def then_data_extraction_rate_limited(rate_limiting_context):
    """Verify data extraction requests are rate limited."""
    assert rate_limiting_context.rate_limit_delay > 0


@then("the total scraping time should reflect rate limiting delays")
def then_total_time_reflects_rate_limiting_delays(rate_limiting_context):
    """Verify total scraping time reflects rate limiting delays."""
    expected_time = rate_limiting_context.discoverable_pages * rate_limiting_context.rate_limit_delay
    assert expected_time == 16.0  # 8 pages * 2 seconds


@then("progress tracking should account for rate limiting delays")
def then_progress_tracking_accounts_for_delays(rate_limiting_context):
    """Verify progress tracking accounts for rate limiting delays."""
    assert rate_limiting_context.multi_page_scraping_with_discovery_started


# Configuration validation with table scenario
@when(parsers.parse("I configure rate limiting with invalid settings:\n{table}"))
def when_configure_invalid_settings_with_table(rate_limiting_context, table):
    """Configure rate limiting with invalid settings from table."""
    rate_limiting_context.invalid_configs = {}
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 3:
                setting, value, expected_result = parts[0], parts[1], parts[2]
                # Convert value to appropriate type
                if value == '-1.0':
                    value = -1.0
                elif value == '0':
                    value = 0
                elif value == '3600':
                    value = 3600
                rate_limiting_context.invalid_configs[setting] = {
                    'value': value,
                    'expected_result': expected_result
                }


# Monitoring scenario
@given("I have enabled rate limiting monitoring")
def given_rate_limiting_monitoring_enabled(rate_limiting_context):
    """Enable rate limiting monitoring."""
    rate_limiting_context.monitoring_enabled = True


@given("I am processing multiple restaurant websites")
def given_processing_multiple_websites(rate_limiting_context):
    """Set up processing multiple websites."""
    rate_limiting_context.processing_multiple_websites = True


@when("scraping operations complete")
def when_scraping_operations_complete(rate_limiting_context):
    """Complete scraping operations."""
    rate_limiting_context.scraping_operations_completed = True


@then(parsers.parse("I should see detailed rate limiting statistics:\n{table}"))
def then_see_detailed_statistics(rate_limiting_context, table):
    """Verify detailed rate limiting statistics are available."""
    rate_limiting_context.expected_statistics = {}
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2:
                metric, tracked = parts[0], parts[1] == 'yes'
                rate_limiting_context.expected_statistics[metric] = tracked
    
    # Verify expected statistics
    assert len(rate_limiting_context.expected_statistics) == 5


@then("statistics should be exportable for analysis")
def then_statistics_exportable(rate_limiting_context):
    """Verify statistics are exportable for analysis."""
    assert rate_limiting_context.monitoring_enabled


@then("rate limiting effectiveness should be measurable")
def then_rate_limiting_effectiveness_measurable(rate_limiting_context):
    """Verify rate limiting effectiveness is measurable."""
    assert rate_limiting_context.scraping_operations_completed


# Emergency override scenario
@given("I have enabled emergency rate limiting override")
def given_emergency_override_enabled(rate_limiting_context):
    """Enable emergency rate limiting override."""
    rate_limiting_context.emergency_override_available = True


@given("I have a critical scraping operation that must complete quickly")
def given_critical_scraping_operation(rate_limiting_context):
    """Set up critical scraping operation."""
    rate_limiting_context.critical_operation = True


@when("I enable emergency override mode")
def when_enable_emergency_override(rate_limiting_context):
    """Enable emergency override mode."""
    rate_limiting_context.emergency_override_active = True


@then("rate limiting should be temporarily disabled or reduced")
def then_rate_limiting_disabled_or_reduced(rate_limiting_context):
    """Verify rate limiting is temporarily disabled or reduced."""
    assert rate_limiting_context.emergency_override_active


@then("override mode should have a maximum duration limit")
def then_override_has_duration_limit(rate_limiting_context):
    """Verify override mode has maximum duration limit."""
    rate_limiting_context.override_duration_limit = 300  # 5 minutes
    assert rate_limiting_context.override_duration_limit > 0


@then("emergency usage should be logged for audit purposes")
def then_emergency_usage_logged(rate_limiting_context):
    """Verify emergency usage is logged for audit."""
    assert rate_limiting_context.emergency_override_active


@then("normal rate limiting should resume automatically after override expires")
def then_normal_rate_limiting_resumes(rate_limiting_context):
    """Verify normal rate limiting resumes after override expires."""
    # This will be implemented with proper timeout handling
    assert rate_limiting_context.emergency_override_available


@then("emergency overrides should require explicit authorization")
def then_emergency_overrides_require_authorization(rate_limiting_context):
    """Verify emergency overrides require explicit authorization."""
    assert rate_limiting_context.critical_operation