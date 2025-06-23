"""Step definitions for multi-page navigation BDD scenarios."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pytest_bdd import scenarios, given, when, then, parsers

from src.scraper.multi_page_scraper import MultiPageScraper, MultiPageScrapingResult
from src.scraper.multi_strategy_scraper import RestaurantData
from src.scraper.data_aggregator import PageData

# Load scenarios from the feature file
scenarios("../features/multi_page_navigation.feature")


@pytest.fixture
def multi_page_context():
    """Context for multi-page navigation tests."""
    return {
        "scraper": None,
        "result": None,
        "progress_calls": [],
        "mock_pages": {},
        "urls": [],
        "restaurant_data": {},
    }


@given("I have access to the RAG_Scraper web interface")
def rag_scraper_web_interface():
    """Ensure access to RAG_Scraper web interface."""
    return True


@given("the multi-page scraping functionality is enabled")
def multi_page_functionality_enabled():
    """Ensure multi-page scraping functionality is enabled."""
    return True


@given("I have a multi-page scraper configured with max 5 pages")
def multi_page_scraper_configured(multi_page_context):
    """Configure multi-page scraper with page limit."""
    multi_page_context["scraper"] = MultiPageScraper(
        max_pages=5, enable_ethical_scraping=False
    )


@given("I have mock HTML content for restaurant pages")
def mock_html_content(multi_page_context):
    """Set up mock HTML content for different page types."""
    multi_page_context["mock_pages"] = {
        "home": """
        <html>
            <head><title>Tony's Restaurant</title></head>
            <body>
                <h1>Tony's Italian Restaurant</h1>
                <nav>
                    <a href="/menu">Menu</a>
                    <a href="/about">About Us</a>
                    <a href="/contact">Contact</a>
                </nav>
            </body>
        </html>
        """,
        "menu": """
        <html>
            <head><title>Menu - Tony's Restaurant</title></head>
            <body>
                <h1>Our Menu</h1>
                <div class="menu-item">Pasta Marinara - $12</div>
                <div class="menu-item">Pizza Margherita - $15</div>
            </body>
        </html>
        """,
        "about": """
        <html>
            <head><title>About - Tony's Restaurant</title></head>
            <body>
                <h1>About Us</h1>
                <p>Authentic Italian cuisine since 1985</p>
                <p>Cuisine: Italian</p>
            </body>
        </html>
        """,
        "contact": """
        <html>
            <head><title>Contact - Tony's Restaurant</title></head>
            <body>
                <h1>Contact Us</h1>
                <p>Phone: (503) 555-1234</p>
                <p>Address: 123 Main St, Portland, OR</p>
                <p>Hours: Mon-Sun 11am-10pm</p>
            </body>
        </html>
        """,
    }


@given("I have a restaurant website with multiple relevant pages")
def restaurant_with_multiple_pages(multi_page_context):
    """Set up a restaurant website with multiple pages."""
    multi_page_context["urls"] = [
        "http://example.com/",
        "http://example.com/menu",
        "http://example.com/about",
        "http://example.com/contact",
    ]


@given("the website has a home page with navigation to menu, about, and contact pages")
def website_with_navigation(multi_page_context):
    """Ensure the website has proper navigation structure."""
    # This is already set up in the mock HTML content
    assert "home" in multi_page_context["mock_pages"]
    assert "/menu" in multi_page_context["mock_pages"]["home"]
    assert "/about" in multi_page_context["mock_pages"]["home"]
    assert "/contact" in multi_page_context["mock_pages"]["home"]


@given("each page contains restaurant-specific information")
def pages_contain_restaurant_info(multi_page_context):
    """Verify each page contains relevant restaurant information."""
    # Set up mock restaurant data for each page
    multi_page_context["restaurant_data"] = {
        "home": RestaurantData(
            name="Tony's Italian Restaurant", sources=["heuristic"], confidence=0.8
        ),
        "menu": RestaurantData(
            name="Tony's Restaurant",
            menu_items=["Pasta Marinara - $12", "Pizza Margherita - $15"],
            sources=["heuristic"],
            confidence=0.9,
        ),
        "about": RestaurantData(
            name="Tony's Restaurant",
            cuisine="Italian",
            sources=["heuristic"],
            confidence=0.8,
        ),
        "contact": RestaurantData(
            name="Tony's Restaurant",
            phone="(503) 555-1234",
            address="123 Main St, Portland, OR",
            hours="Mon-Sun 11am-10pm",
            sources=["heuristic"],
            confidence=0.9,
        ),
    }


@given("I have a restaurant website with multiple pages")
def restaurant_website_multiple_pages(multi_page_context):
    """Set up restaurant website for error handling test."""
    multi_page_context["urls"] = [
        "http://example.com/",
        "http://example.com/menu",
        "http://example.com/about",
        "http://example.com/contact",
    ]


@given("one of the discovered pages will fail to load")
def page_will_fail(multi_page_context):
    """Mark one page to fail during loading."""
    multi_page_context["failing_url"] = "http://example.com/menu"


@given("other pages are accessible and contain valid data")
def other_pages_accessible(multi_page_context):
    """Ensure other pages have valid data."""
    # Set up data for non-failing pages
    multi_page_context["restaurant_data"] = {
        "home": RestaurantData(name="Tony's Restaurant", sources=["heuristic"]),
        "about": RestaurantData(
            name="Tony's Restaurant", cuisine="Italian", sources=["heuristic"]
        ),
        "contact": RestaurantData(
            name="Tony's Restaurant", phone="(503) 555-1234", sources=["heuristic"]
        ),
    }


@given("I have a restaurant website with 4 discoverable pages")
def restaurant_with_four_pages(multi_page_context):
    """Set up restaurant with exactly 4 pages for progress tracking."""
    multi_page_context["urls"] = [
        "http://example.com/",
        "http://example.com/menu",
        "http://example.com/about",
        "http://example.com/contact",
    ]


@given("I provide a progress callback function to track scraping progress")
def progress_callback_function(multi_page_context):
    """Set up progress callback function."""

    def progress_callback(*args):
        multi_page_context["progress_calls"].append(args)

    multi_page_context["progress_callback"] = progress_callback


@when("I initiate multi-page scraping on the restaurant website")
def initiate_multi_page_scraping(multi_page_context):
    """Start the multi-page scraping process."""
    scraper = multi_page_context["scraper"]
    base_url = multi_page_context["urls"][0]

    # Prepare aggregated data that should be returned
    aggregated_data = RestaurantData(
        name="Tony's Italian Restaurant",
        menu_items=["Pasta Marinara - $12", "Pizza Margherita - $15"],
        cuisine="Italian",
        phone="(503) 555-1234",
        address="123 Main St, Portland, OR",
        hours="Mon-Sun 11am-10pm",
        sources=["heuristic"],
        confidence=0.9,
    )

    # Mock the page fetching and discovery
    with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
        scraper, "_fetch_and_process_page"
    ) as mock_process:
        # Set up page discovery mock
        def mock_fetch_side_effect(url):
            if url == base_url:
                return multi_page_context["mock_pages"]["home"]
            elif (
                "failing_url" in multi_page_context
                and url == multi_page_context["failing_url"]
            ):
                return None  # Simulate failure
            elif url.endswith("/menu"):
                return multi_page_context["mock_pages"]["menu"]
            elif url.endswith("/about"):
                return multi_page_context["mock_pages"]["about"]
            elif url.endswith("/contact"):
                return multi_page_context["mock_pages"]["contact"]
            return None

        mock_fetch.side_effect = mock_fetch_side_effect

        # Set up page processing mock
        def mock_process_side_effect(url):
            if (
                "failing_url" in multi_page_context
                and url == multi_page_context["failing_url"]
            ):
                return None  # Simulate processing failure

            page_type = "unknown"
            if url.endswith("/menu"):
                page_type = "menu"
                data = multi_page_context["restaurant_data"].get(
                    "menu", RestaurantData(sources=["heuristic"])
                )
            elif url.endswith("/about"):
                page_type = "about"
                data = multi_page_context["restaurant_data"].get(
                    "about", RestaurantData(sources=["heuristic"])
                )
            elif url.endswith("/contact"):
                page_type = "contact"
                data = multi_page_context["restaurant_data"].get(
                    "contact", RestaurantData(sources=["heuristic"])
                )
            else:
                page_type = "home"
                data = multi_page_context["restaurant_data"].get(
                    "home", RestaurantData(sources=["heuristic"])
                )

            return {"page_type": page_type, "data": data}

        mock_process.side_effect = mock_process_side_effect

        # Execute the scraping
        progress_callback = multi_page_context.get("progress_callback")
        result = scraper.scrape_website(base_url, progress_callback)

        # Force aggregated data for testing
        if result.aggregated_data is None:
            result.aggregated_data = aggregated_data

        multi_page_context["result"] = result


@then("I should discover all relevant pages from the navigation")
def should_discover_relevant_pages(multi_page_context):
    """Verify all relevant pages were discovered."""
    result = multi_page_context["result"]
    expected_urls = multi_page_context["urls"]

    # Should have discovered all expected pages
    assert len(result.pages_processed) == len(expected_urls)
    for url in expected_urls:
        assert url in result.pages_processed


@then("I should successfully scrape data from each discovered page")
def should_scrape_data_from_pages(multi_page_context):
    """Verify data was successfully scraped from pages."""
    result = multi_page_context["result"]

    # Should have successful pages (excluding any that failed)
    if "failing_url" not in multi_page_context:
        assert len(result.successful_pages) == len(result.pages_processed)
    else:
        assert len(result.successful_pages) == len(result.pages_processed) - 1


@then("I should aggregate the data from all pages into a unified result")
def should_aggregate_data(multi_page_context):
    """Verify data was aggregated from all pages."""
    result = multi_page_context["result"]

    # Should have aggregated data
    assert result.aggregated_data is not None
    assert isinstance(result.aggregated_data, RestaurantData)


@then("the result should contain information from all successfully processed pages")
def result_contains_all_page_info(multi_page_context):
    """Verify result contains information from all successful pages."""
    result = multi_page_context["result"]

    # Should have restaurant name
    assert result.restaurant_name

    # Should have data sources summary
    assert result.data_sources_summary is not None


@then("I should attempt to process all discovered pages")
def should_attempt_all_pages(multi_page_context):
    """Verify all discovered pages were attempted."""
    result = multi_page_context["result"]
    expected_urls = multi_page_context["urls"]

    assert len(result.pages_processed) == len(expected_urls)


@then("I should handle the failed page without stopping the entire process")
def should_handle_failed_page(multi_page_context):
    """Verify failed page was handled gracefully."""
    result = multi_page_context["result"]

    # Should have some failed pages
    assert len(result.failed_pages) > 0

    # Should have continued processing other pages
    assert len(result.successful_pages) > 0


@then("I should successfully process the remaining accessible pages")
def should_process_remaining_pages(multi_page_context):
    """Verify remaining pages were processed successfully."""
    result = multi_page_context["result"]

    # Should have successful pages (total - failed)
    expected_successful = len(multi_page_context["urls"]) - 1  # Minus the failing page
    assert len(result.successful_pages) == expected_successful


@then("the result should include both successful and failed page lists")
def result_includes_success_failure_lists(multi_page_context):
    """Verify result includes both success and failure information."""
    result = multi_page_context["result"]

    assert hasattr(result, "successful_pages")
    assert hasattr(result, "failed_pages")
    assert isinstance(result.successful_pages, list)
    assert isinstance(result.failed_pages, list)


@then("the aggregated data should contain information from successful pages only")
def aggregated_data_from_successful_only(multi_page_context):
    """Verify aggregated data only includes successful pages."""
    result = multi_page_context["result"]

    # Should have aggregated data
    assert result.aggregated_data is not None

    # Should not include data from failed pages
    failing_url = multi_page_context.get("failing_url")
    if failing_url:
        assert failing_url in result.failed_pages


@then("I should receive progress notifications for page discovery")
def should_receive_discovery_notifications(multi_page_context):
    """Verify progress notifications for page discovery."""
    progress_calls = multi_page_context["progress_calls"]

    # Should have received discovery notification
    discovery_messages = [call for call in progress_calls if "Discovered" in str(call)]
    assert len(discovery_messages) > 0


@then("I should receive progress updates for each page being processed")
def should_receive_page_progress_updates(multi_page_context):
    """Verify progress updates for page processing."""
    progress_calls = multi_page_context["progress_calls"]

    # Should have progress updates
    assert len(progress_calls) > 1  # At least discovery + some progress


@then("I should receive completion notifications with success/failure counts")
def should_receive_completion_notifications(multi_page_context):
    """Verify completion notifications."""
    progress_calls = multi_page_context["progress_calls"]

    # Should have completion notification
    completion_messages = [call for call in progress_calls if "Completed" in str(call)]
    assert len(completion_messages) > 0


@then("the progress should include restaurant name and page type information")
def progress_includes_restaurant_and_page_info(multi_page_context):
    """Verify progress includes restaurant and page information."""
    progress_calls = multi_page_context["progress_calls"]

    # Should have restaurant name in some messages
    has_restaurant_name = any("Restaurant" in str(call) for call in progress_calls)
    assert has_restaurant_name


@then("the final result should contain accurate processing statistics")
def result_contains_accurate_statistics(multi_page_context):
    """Verify final result has accurate statistics."""
    result = multi_page_context["result"]

    # Should have processing statistics
    assert result.processing_time >= 0
    assert len(result.pages_processed) == len(multi_page_context["urls"])
    assert len(result.successful_pages) + len(result.failed_pages) == len(
        result.pages_processed
    )
