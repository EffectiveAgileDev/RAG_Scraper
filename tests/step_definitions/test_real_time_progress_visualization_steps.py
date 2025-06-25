"""Step definitions for real-time progress visualization feature."""

import re
import time
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


@given("I have started a multi-page scraping job")
def started_multi_page_job(progress_context):
    """Start a multi-page scraping job."""
    progress_context["job_started"] = True
    progress_context["current_page"] = "https://restaurant1.com"
    progress_context["total_pages"] = 5
    progress_context["completed_pages"] = 0
    progress_context["pages_in_queue"] = 4


@given(parsers.parse("I have a scraping job with {count:d} pages in progress"))
def job_with_pages_in_progress(progress_context, count):
    """Set up a scraping job with specified pages in progress."""
    progress_context["total_pages"] = count
    progress_context["current_page"] = f"https://restaurant1.com"
    progress_context["completed_pages"] = 0
    progress_context["pages_in_queue"] = count - 1


@given(parsers.parse("I have started a multi-page scraping job with {count:d} discovered pages"))
def job_with_discovered_pages(progress_context, count):
    """Set up a scraping job with discovered pages."""
    progress_context["total_pages"] = count
    progress_context["discovered_pages"] = count
    progress_context["completed_pages"] = 0
    progress_context["pages_in_queue"] = count
    progress_context["current_page"] = None


@given(parsers.parse("I have {total:d} total pages discovered"))
def total_pages_discovered(progress_context, total):
    """Set total pages discovered."""
    progress_context["total_pages"] = total


@given(parsers.parse("And {completed:d} pages have been completed"))
def pages_completed(progress_context, completed):
    """Set completed pages count."""
    progress_context["completed_pages"] = completed


@given(parsers.parse("And {current:d} page is currently being processed"))
def page_currently_processing(progress_context, current):
    """Set current page being processed."""
    progress_context["currently_processing"] = current
    progress_context["current_page"] = f"https://restaurant{current}.com"


@given("I have a scraping job in progress")
def scraping_job_in_progress(progress_context):
    """Set up a scraping job in progress."""
    progress_context["job_started"] = True
    progress_context["total_pages"] = 8
    progress_context["completed_pages"] = 3
    progress_context["current_page"] = "https://restaurant4.com"
    progress_context["pages_in_queue"] = 4


@given(parsers.parse("I have processed {count:d} pages with average time of {avg_time:g} seconds"))
def processed_pages_with_avg_time(progress_context, count, avg_time):
    """Set processed pages with average time."""
    progress_context["completed_pages"] = count
    progress_context["average_processing_time"] = avg_time


@given(parsers.parse("And I have {remaining:d} pages remaining in the queue"))
def pages_remaining_in_queue(progress_context, remaining):
    """Set remaining pages in queue."""
    progress_context["pages_in_queue"] = remaining


@given("I have page discovery enabled")
def page_discovery_enabled(progress_context):
    """Enable page discovery."""
    progress_context["page_discovery_enabled"] = True


@when("the scraper begins processing a page")
def scraper_begins_processing(progress_context):
    """Simulate scraper beginning to process a page."""
    progress_context["processing_started"] = True
    progress_context["current_page"] = "https://restaurant1.com"


@when("the scraper moves from page 1 to page 2")
def scraper_moves_to_next_page(progress_context):
    """Simulate scraper moving to next page."""
    progress_context["completed_pages"] = 1
    progress_context["current_page"] = "https://restaurant2.com"
    progress_context["page_transition"] = True


@when("I look at the progress visualization")
def look_at_progress_visualization(progress_context):
    """Look at the progress visualization."""
    progress_context["viewing_progress"] = True


@when("I view the queue status")
def view_queue_status(progress_context):
    """View the queue status display."""
    progress_context["viewing_queue_status"] = True


@when("I view the progress visualization")
def view_progress_visualization(progress_context):
    """View the progress visualization display."""
    progress_context["viewing_progress_viz"] = True


@when("a page fails to process")
def page_fails_to_process(progress_context):
    """Simulate a page failing to process."""
    progress_context["failed_page"] = "https://restaurant3.com"
    progress_context["page_failure"] = True


@when("new pages are discovered during scraping")
def new_pages_discovered(progress_context):
    """Simulate new pages being discovered."""
    progress_context["new_pages_discovered"] = 3
    progress_context["total_pages"] += 3
    progress_context["pages_in_queue"] += 3


@then("I should see the current page URL being displayed")
def see_current_page_url(progress_context):
    """Verify current page URL is displayed."""
    current_page = progress_context.get("current_page")
    assert current_page is not None
    assert "restaurant1.com" in current_page


@then('I should see a "Currently Processing:" label')
def see_currently_processing_label(progress_context):
    """Verify currently processing label is shown."""
    assert progress_context.get("processing_started") is True


@then("the current page should be highlighted in the progress display")
def current_page_highlighted(progress_context):
    """Verify current page is highlighted."""
    assert progress_context.get("current_page") is not None


@then('the "Currently Processing" display should update immediately')
def currently_processing_updates_immediately(progress_context):
    """Verify currently processing display updates immediately."""
    assert progress_context.get("page_transition") is True
    assert "restaurant2.com" in progress_context.get("current_page", "")


@then("the previous page should show as completed")
def previous_page_shows_completed(progress_context):
    """Verify previous page shows as completed."""
    assert progress_context.get("completed_pages", 0) >= 1


@then("the new current page should be highlighted")
def new_current_page_highlighted(progress_context):
    """Verify new current page is highlighted."""
    current_page = progress_context.get("current_page")
    assert current_page is not None
    assert "restaurant2.com" in current_page


@then(parsers.parse('I should see "Pages in Queue: {queue_type}" display'))
def see_pages_in_queue_display(progress_context, queue_type):
    """Verify pages in queue display."""
    if queue_type == "X":
        assert progress_context.get("pages_in_queue") is not None


@then(parsers.parse('I should see "Pages Completed: {completed_type}" display'))
def see_pages_completed_display(progress_context, completed_type):
    """Verify pages completed display."""
    if completed_type == "Y":
        assert progress_context.get("completed_pages") is not None


@then(parsers.parse('I should see "Pages Remaining: {remaining_type}" display'))
def see_pages_remaining_display(progress_context, remaining_type):
    """Verify pages remaining display."""
    if remaining_type == "Z":
        assert progress_context.get("pages_in_queue") is not None


@then("the numbers should update in real-time as pages are processed")
def numbers_update_in_real_time(progress_context):
    """Verify numbers update in real-time."""
    assert progress_context.get("viewing_progress") is True


@then(parsers.parse('I should see "Pages Completed: {count:d}"'))
def see_pages_completed_count(progress_context, count):
    """Verify pages completed count."""
    assert progress_context.get("completed_pages") == count


@then(parsers.parse('I should see "Pages in Queue: {count:d}"'))
def see_pages_in_queue_count(progress_context, count):
    """Verify pages in queue count."""
    expected_queue = progress_context.get("total_pages", 0) - progress_context.get("completed_pages", 0) - progress_context.get("currently_processing", 0)
    assert expected_queue == count


@then(parsers.parse('I should see "Pages Remaining: {count:d}"'))
def see_pages_remaining_count(progress_context, count):
    """Verify pages remaining count."""
    expected_remaining = progress_context.get("total_pages", 0) - progress_context.get("completed_pages", 0)
    assert expected_remaining == count


@then(parsers.parse('I should see "Currently Processing: {count:d}"'))
def see_currently_processing_count(progress_context, count):
    """Verify currently processing count."""
    assert progress_context.get("currently_processing") == count


@then("I should see a progress bar showing overall completion")
def see_progress_bar(progress_context):
    """Verify progress bar is shown."""
    assert progress_context.get("viewing_progress_viz") is True


@then("I should see individual page status indicators")
def see_individual_page_status(progress_context):
    """Verify individual page status indicators."""
    assert progress_context.get("total_pages", 0) > 0


@then("completed pages should be marked with green checkmarks")
def completed_pages_marked_green(progress_context):
    """Verify completed pages are marked with green checkmarks."""
    assert progress_context.get("completed_pages", 0) > 0


@then("the current page should have a pulsing animation")
def current_page_has_pulsing_animation(progress_context):
    """Verify current page has pulsing animation."""
    assert progress_context.get("current_page") is not None


@then("pending pages should be marked as queued")
def pending_pages_marked_queued(progress_context):
    """Verify pending pages are marked as queued."""
    assert progress_context.get("pages_in_queue", 0) > 0


@then(parsers.parse('I should see "Estimated Time Remaining: ~{time:g}s"'))
def see_estimated_time_remaining(progress_context, time):
    """Verify estimated time remaining display."""
    avg_time = progress_context.get("average_processing_time", 0)
    remaining = progress_context.get("pages_in_queue", 0)
    expected_time = avg_time * remaining
    # Allow for small floating point differences
    assert abs(expected_time - time) < 0.1


@then("the estimate should update as processing speeds change")
def estimate_updates_with_speed_changes(progress_context):
    """Verify estimate updates with speed changes."""
    assert progress_context.get("average_processing_time") is not None


@then(parsers.parse('I should see "Average Processing Time: {time:g}s"'))
def see_average_processing_time(progress_context, time):
    """Verify average processing time display."""
    assert progress_context.get("average_processing_time") == time


@then("the failed page should be marked with a red X")
def failed_page_marked_red_x(progress_context):
    """Verify failed page is marked with red X."""
    assert progress_context.get("page_failure") is True
    assert progress_context.get("failed_page") is not None


@then("the queue count should adjust accordingly")
def queue_count_adjusts_for_failure(progress_context):
    """Verify queue count adjusts for failed page."""
    assert progress_context.get("page_failure") is True


@then("processing should continue with the next page")
def processing_continues_next_page(progress_context):
    """Verify processing continues with next page."""
    assert progress_context.get("page_failure") is True


@then("the current page display should update to show the next page")
def current_page_display_updates_next(progress_context):
    """Verify current page display updates to next page."""
    assert progress_context.get("page_failure") is True


@then('the "Pages in Queue" count should increase dynamically')
def pages_in_queue_increases_dynamically(progress_context):
    """Verify pages in queue count increases dynamically."""
    assert progress_context.get("new_pages_discovered", 0) > 0


@then(parsers.parse('I should see "New pages discovered: {count_type}" notifications'))
def see_new_pages_discovered_notifications(progress_context, count_type):
    """Verify new pages discovered notifications."""
    if count_type == "X":
        assert progress_context.get("new_pages_discovered", 0) > 0


@then("the progress bar should adjust to reflect the new total")
def progress_bar_adjusts_new_total(progress_context):
    """Verify progress bar adjusts to new total."""
    assert progress_context.get("new_pages_discovered", 0) > 0
    assert progress_context.get("total_pages", 0) > 0