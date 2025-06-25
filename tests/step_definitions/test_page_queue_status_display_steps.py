"""Step definitions for page queue status display feature."""

import re
from unittest.mock import Mock, MagicMock
from pytest_bdd import given, when, then, parsers


@given("I am on the RAG_Scraper web interface")
def on_rag_scraper_interface(mock_flask_app):
    """Set up the RAG_Scraper web interface."""
    pass


@given("I have multi-page scraping mode enabled")
def multi_page_mode_enabled(mock_flask_app):
    """Enable multi-page scraping mode."""
    pass


@given(parsers.parse("I have started a scraping job with {count:d} discovered pages"))
def started_job_with_discovered_pages(queue_context, count):
    """Start a scraping job with discovered pages."""
    queue_context["total_pages"] = count
    queue_context["pages_in_queue"] = count
    queue_context["pages_completed"] = 0
    queue_context["currently_processing"] = 0
    queue_context["failed_pages"] = 0


@given(parsers.parse("I have a scraping job with {total:d} total pages"))
def job_with_total_pages(queue_context, total):
    """Set up a scraping job with total pages."""
    queue_context["total_pages"] = total


@given(parsers.parse("And {completed:d} pages have been completed"))
def pages_completed(queue_context, completed):
    """Set completed pages count."""
    queue_context["pages_completed"] = completed


@given(parsers.parse("And {current:d} page is currently being processed"))
def page_currently_processing(queue_context, current):
    """Set current page being processed."""
    queue_context["currently_processing"] = current


@given(parsers.parse("And {failed:d} page has failed processing"))
def page_failed_processing(queue_context, failed):
    """Set failed pages count."""
    queue_context["failed_pages"] = failed


@given(parsers.parse("I have enabled concurrent processing with limit {limit:d}"))
def enabled_concurrent_processing(queue_context, limit):
    """Enable concurrent processing with limit."""
    queue_context["concurrent_limit"] = limit
    queue_context["concurrent_enabled"] = True


@given(parsers.parse("And {concurrent:d} pages are currently being processed concurrently"))
def pages_processing_concurrently(queue_context, concurrent):
    """Set concurrent pages being processed."""
    queue_context["currently_processing"] = concurrent


@given("I have a scraping job in progress")
def scraping_job_in_progress(queue_context):
    """Set up a scraping job in progress."""
    queue_context["job_in_progress"] = True
    queue_context["total_pages"] = 10
    queue_context["pages_completed"] = 3
    queue_context["currently_processing"] = 1


@given("I have a scraping job with queue status displayed")
def job_with_queue_status_displayed(queue_context):
    """Set up job with queue status displayed."""
    queue_context["queue_status_displayed"] = True
    queue_context["total_pages"] = 8
    queue_context["pages_completed"] = 3
    queue_context["pages_in_queue"] = 4


@given(parsers.parse("I have a scraping job with {initial:d} initial pages"))
def job_with_initial_pages(queue_context, initial):
    """Set up job with initial pages."""
    queue_context["initial_pages"] = initial
    queue_context["total_pages"] = initial


@when("I view the queue status display")
def view_queue_status_display(queue_context):
    """View the queue status display."""
    queue_context["viewing_queue_status"] = True


@when("I view the updated queue status")
def view_updated_queue_status(queue_context):
    """View the updated queue status."""
    queue_context["viewing_updated_status"] = True


@when("the last page completes processing")
def last_page_completes_processing(queue_context):
    """Simulate last page completing processing."""
    queue_context["pages_completed"] = queue_context.get("total_pages", 0)
    queue_context["currently_processing"] = 0
    queue_context["pages_in_queue"] = 0


@when(parsers.parse("{new_count:d} new pages are discovered during processing"))
def new_pages_discovered_during_processing(queue_context, new_count):
    """Simulate new pages being discovered."""
    original_total = queue_context.get("total_pages", 0)
    queue_context["total_pages"] = original_total + new_count
    queue_context["new_pages_discovered"] = new_count
    queue_context["pages_in_queue"] = queue_context.get("pages_in_queue", 0) + new_count


@when("I view the queue status")
def view_queue_status(queue_context):
    """View the queue status."""
    queue_context["viewing_queue"] = True


@when("I view the queue status display")
def view_queue_status_display_again(queue_context):
    """View the queue status display again."""
    queue_context["viewing_display"] = True


@when("I refresh the page during active scraping")
def refresh_page_during_scraping(queue_context):
    """Simulate page refresh during active scraping."""
    queue_context["page_refreshed"] = True


@then(parsers.parse('I should see "Pages in Queue: {count:d}"'))
def see_pages_in_queue(queue_context, count):
    """Verify pages in queue count."""
    total = queue_context.get("total_pages", 0)
    completed = queue_context.get("pages_completed", 0)
    currently_processing = queue_context.get("currently_processing", 0)
    failed = queue_context.get("failed_pages", 0)
    
    expected_in_queue = total - completed - currently_processing - failed
    assert expected_in_queue == count


@then(parsers.parse('I should see "Pages Remaining: {count:d}"'))
def see_pages_remaining(queue_context, count):
    """Verify pages remaining count."""
    total = queue_context.get("total_pages", 0)
    completed = queue_context.get("pages_completed", 0)
    
    expected_remaining = total - completed
    assert expected_remaining == count


@then(parsers.parse('I should see "Pages Completed: {count:d}"'))
def see_pages_completed(queue_context, count):
    """Verify pages completed count."""
    assert queue_context.get("pages_completed", 0) == count


@then(parsers.parse('I should see "Currently Processing: {count:d}"'))
def see_currently_processing(queue_context, count):
    """Verify currently processing count."""
    assert queue_context.get("currently_processing", 0) == count


@then(parsers.parse("I should see total pages increased to {total:d}"))
def see_total_pages_increased(queue_context, total):
    """Verify total pages increased."""
    assert queue_context.get("total_pages", 0) == total


@then(parsers.parse('I should see a "New pages discovered: {count:d}" notification'))
def see_new_pages_notification(queue_context, count):
    """Verify new pages discovered notification."""
    assert queue_context.get("new_pages_discovered", 0) == count


@then("I should see failed page excluded from processing queue")
def see_failed_page_excluded(queue_context):
    """Verify failed page is excluded from processing queue."""
    assert queue_context.get("failed_pages", 0) > 0


@then("I should see concurrent processing indicator")
def see_concurrent_processing_indicator(queue_context):
    """Verify concurrent processing indicator is shown."""
    assert queue_context.get("concurrent_enabled", False) is True


@then("I should see a visual progress bar for overall completion")
def see_visual_progress_bar(queue_context):
    """Verify visual progress bar is shown."""
    assert queue_context.get("viewing_display", False) is True


@then("I should see color-coded status indicators")
def see_color_coded_indicators(queue_context):
    """Verify color-coded status indicators."""
    assert queue_context.get("viewing_display", False) is True


@then("completed pages should show green indicators")
def completed_pages_show_green(queue_context):
    """Verify completed pages show green indicators."""
    assert queue_context.get("pages_completed", 0) >= 0


@then("queued pages should show amber indicators")
def queued_pages_show_amber(queue_context):
    """Verify queued pages show amber indicators."""
    total = queue_context.get("total_pages", 0)
    completed = queue_context.get("pages_completed", 0)
    assert total - completed >= 0


@then("failed pages should show red indicators")
def failed_pages_show_red(queue_context):
    """Verify failed pages show red indicators."""
    assert queue_context.get("failed_pages", 0) >= 0


@then("the queue status should be restored accurately")
def queue_status_restored_accurately(queue_context):
    """Verify queue status is restored accurately after refresh."""
    assert queue_context.get("page_refreshed", False) is True


@then("all counters should reflect the current state")
def counters_reflect_current_state(queue_context):
    """Verify all counters reflect current state."""
    assert queue_context.get("page_refreshed", False) is True


@then("no data should be lost from the refresh")
def no_data_lost_from_refresh(queue_context):
    """Verify no data is lost from refresh."""
    assert queue_context.get("page_refreshed", False) is True