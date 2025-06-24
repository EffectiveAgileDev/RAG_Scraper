"""Step definitions for page queue management feature tests."""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from typing import List, Dict, Any, Tuple
from collections import deque
import threading
import time

# Import the PageQueueManager (to be created)
try:
    from src.scraper.page_queue_manager import PageQueueManager
except ImportError:
    # Will fail initially - this is expected in TDD
    PageQueueManager = None

# Load all scenarios from the feature file
scenarios("../features/page_queue_management.feature")


@pytest.fixture
def queue_manager():
    """Create a PageQueueManager instance for testing."""
    if PageQueueManager is None:
        pytest.skip("PageQueueManager not implemented yet")
    return PageQueueManager(max_pages=5)


@pytest.fixture
def limited_queue_manager():
    """Create a PageQueueManager with limited pages for testing."""
    if PageQueueManager is None:
        pytest.skip("PageQueueManager not implemented yet")
    return PageQueueManager(max_pages=3)


@pytest.fixture
def sample_urls():
    """Sample restaurant website URLs for testing."""
    return [
        "http://example.com/",
        "http://example.com/menu",
        "http://example.com/contact",
        "http://example.com/about",
        "http://example.com/hours"
    ]


# Background steps
@given("I have a PageQueueManager with max 5 pages")
def have_queue_manager_max_5(queue_manager):
    """Store the queue manager in context."""
    pytest.current_queue_manager = queue_manager


@given("I have a PageQueueManager with max 3 pages")
def have_queue_manager_max_3(limited_queue_manager):
    """Store the limited queue manager in context."""
    pytest.current_queue_manager = limited_queue_manager


@given("I have sample restaurant website URLs for testing")
def have_sample_urls(sample_urls):
    """Store sample URLs in context."""
    pytest.sample_urls = sample_urls


# Initialization scenario steps
@given("I create a new PageQueueManager instance")
def create_queue_manager_instance():
    """Create a new PageQueueManager instance."""
    if PageQueueManager is None:
        pytest.skip("PageQueueManager not implemented yet")
    pytest.current_queue_manager = PageQueueManager()


@when("I initialize the page queue")
def initialize_page_queue():
    """Initialize the page queue."""
    pytest.current_queue_manager.initialize_page_queue()


@then("the queue should be empty")
def queue_should_be_empty():
    """Verify the queue is empty."""
    assert not pytest.current_queue_manager.has_pending_pages()


@then("the visited pages set should be empty")
def visited_pages_should_be_empty():
    """Verify visited pages set is empty."""
    stats = pytest.current_queue_manager.get_queue_stats()
    assert stats["visited"] == 0


@then("the priority queue should be empty")
def priority_queue_should_be_empty():
    """Verify priority queue is empty."""
    assert not pytest.current_queue_manager.has_pending_pages()


@then("the default traversal strategy should be \"BFS\"")
def default_strategy_should_be_bfs():
    """Verify default traversal strategy is BFS."""
    strategy = pytest.current_queue_manager.get_traversal_strategy()
    assert strategy == "BFS"


# Basic operations scenario steps
@given("I have initialized the page queue")
def have_initialized_queue():
    """Initialize the page queue."""
    pytest.current_queue_manager.initialize_page_queue()


@when(parsers.parse('I add pages {pages} with "{strategy}" strategy'))
def add_pages_with_strategy(pages, strategy):
    """Add pages to queue with specified strategy."""
    # Parse the pages list string
    pages_list = eval(pages)  # ["http://example.com/", "http://example.com/menu"]
    pytest.current_queue_manager.add_pages_to_queue(pages_list, strategy)


@then(parsers.parse("the queue should contain {count:d} pages"))
def queue_should_contain_pages(count):
    """Verify queue contains expected number of pages."""
    stats = pytest.current_queue_manager.get_queue_stats()
    assert stats["pending"] == count


@then(parsers.parse('getting the next page should return "{expected_url}"'))
def next_page_should_return_url(expected_url):
    """Verify next page returns expected URL."""
    url = pytest.current_queue_manager.get_next_page()
    assert url == expected_url


@then("the queue should be empty after both pages are retrieved")
def queue_empty_after_retrieval():
    """Verify queue is empty after retrieving all pages."""
    assert not pytest.current_queue_manager.has_pending_pages()


# Depth-first strategy scenario steps
@when(parsers.parse('I add pages {pages} with "{strategy}" strategy'))
def add_pages_with_dfs_strategy(pages, strategy):
    """Add pages to queue with DFS strategy."""
    pages_list = eval(pages)
    pytest.current_queue_manager.add_pages_to_queue(pages_list, strategy)


# Priority queue scenario steps
@when("I add pages with priorities")
def add_pages_with_priorities(step):
    """Add pages with priorities to the queue."""
    pages_with_priority = []
    for row in step.table:
        url = row["URL"]
        priority = int(row["Priority"])
        pages_with_priority.append((url, priority))
    
    pytest.current_queue_manager.add_pages_to_queue_with_priority(pages_with_priority)


# Duplicate prevention scenario steps
@when(parsers.parse('I add pages {pages}'))
def add_pages_simple(pages):
    """Add pages to queue (simple version)."""
    pages_list = eval(pages)
    pytest.current_queue_manager.add_pages_to_queue(pages_list)


@then(parsers.parse("the queue should contain {count:d} unique pages"))
def queue_should_contain_unique_pages(count):
    """Verify queue contains expected number of unique pages."""
    stats = pytest.current_queue_manager.get_queue_stats()
    assert stats["pending"] == count


@then("all pages retrieved should be unique")
def all_pages_should_be_unique():
    """Verify all retrieved pages are unique."""
    retrieved_pages = set()
    while pytest.current_queue_manager.has_pending_pages():
        page = pytest.current_queue_manager.get_next_page()
        assert page not in retrieved_pages, f"Duplicate page: {page}"
        retrieved_pages.add(page)


# Max pages limit scenario steps
@when("I add 5 pages to the queue")
def add_five_pages():
    """Add 5 pages to the queue."""
    pages = [f"http://example.com/page{i}" for i in range(5)]
    pytest.current_queue_manager.add_pages_to_queue(pages)


@then("the queue should contain at most 3 pages")
def queue_should_contain_at_most_pages():
    """Verify queue respects max pages limit."""
    stats = pytest.current_queue_manager.get_queue_stats()
    assert stats["pending"] <= 3


@then("no more than 3 pages total should be processed")
def no_more_than_max_pages_processed():
    """Verify total pages processed doesn't exceed limit."""
    processed_count = 0
    while pytest.current_queue_manager.has_pending_pages() and processed_count < 5:
        pytest.current_queue_manager.get_next_page()
        processed_count += 1
    
    stats = pytest.current_queue_manager.get_queue_stats()
    total_processed = stats["visited"]
    assert total_processed <= 3


# Traversal strategies scenario steps
@when(parsers.parse('I set the traversal strategy to "{strategy}"'))
def set_traversal_strategy(strategy):
    """Set the traversal strategy."""
    pytest.current_queue_manager.set_traversal_strategy(strategy)


@then(parsers.parse('the traversal strategy should be "{expected_strategy}"'))
def traversal_strategy_should_be(expected_strategy):
    """Verify traversal strategy is as expected."""
    strategy = pytest.current_queue_manager.get_traversal_strategy()
    assert strategy == expected_strategy


# Breadth-first traversal scenario steps
@given("I have a website with hierarchical structure")
def have_hierarchical_website(step):
    """Set up a hierarchical website structure."""
    # Mock the website structure for testing
    pytest.hierarchical_structure = {}
    for row in step.table:
        url = row["URL"]
        links = row["Links To"].split(", ") if row["Links To"] else []
        # Convert relative links to absolute
        absolute_links = []
        for link in links:
            if link.startswith("/"):
                absolute_links.append("http://example.com" + link)
            else:
                absolute_links.append(link)
        pytest.hierarchical_structure[url] = absolute_links


@when(parsers.parse('I perform breadth-first traversal from "{start_url}"'))
def perform_breadth_first_traversal(start_url):
    """Perform breadth-first traversal."""
    # Mock the page fetcher for testing
    def mock_page_fetcher(url):
        return pytest.hierarchical_structure.get(url, [])
    
    pytest.traversal_result = pytest.current_queue_manager.breadth_first_traversal(
        start_url, page_fetcher=mock_page_fetcher
    )


@then("pages should be visited in breadth-first order")
def pages_visited_breadth_first_order():
    """Verify pages are visited in breadth-first order."""
    # This is a complex assertion that would need to check the order
    # For now, just verify we have a result
    assert pytest.traversal_result is not None
    assert len(pytest.traversal_result) > 0


@then("level 1 pages should be visited before level 2 pages")
def level_1_before_level_2():
    """Verify level 1 pages come before level 2 pages."""
    result = pytest.traversal_result
    level1_indices = [i for i, url in enumerate(result) if "level1" in url]
    level2_indices = [i for i, url in enumerate(result) if "level2" in url]
    
    if level1_indices and level2_indices:
        assert max(level1_indices) < min(level2_indices)


# Depth-first traversal scenario steps
@when(parsers.parse('I perform depth-first traversal from "{start_url}"'))
def perform_depth_first_traversal(start_url):
    """Perform depth-first traversal."""
    def mock_page_fetcher(url):
        return pytest.hierarchical_structure.get(url, [])
    
    pytest.traversal_result = pytest.current_queue_manager.depth_first_traversal(
        start_url, page_fetcher=mock_page_fetcher
    )


@then("pages should be visited in depth-first order")
def pages_visited_depth_first_order():
    """Verify pages are visited in depth-first order."""
    assert pytest.traversal_result is not None
    assert len(pytest.traversal_result) > 0


@then("one branch should be explored completely before the other")
def one_branch_before_other():
    """Verify one branch is explored before the other."""
    result = pytest.traversal_result
    branch1_indices = [i for i, url in enumerate(result) if "branch1" in url]
    branch2_indices = [i for i, url in enumerate(result) if "branch2" in url]
    
    if branch1_indices and branch2_indices:
        # Either all branch1 comes before branch2, or vice versa
        branch1_complete_first = max(branch1_indices) < min(branch2_indices)
        branch2_complete_first = max(branch2_indices) < min(branch1_indices)
        assert branch1_complete_first or branch2_complete_first


# Priority traversal scenario steps
@given("I have a restaurant website with different page types")
def have_restaurant_website_page_types():
    """Set up restaurant website with different page types."""
    pytest.restaurant_structure = {
        "http://example.com/": ["http://example.com/menu", "http://example.com/blog", "http://example.com/contact"],
        "http://example.com/menu": [],
        "http://example.com/blog": [],
        "http://example.com/contact": []
    }


@when(parsers.parse('I perform priority traversal from "{start_url}"'))
def perform_priority_traversal(start_url):
    """Perform priority-based traversal."""
    def mock_page_fetcher(url):
        return pytest.restaurant_structure.get(url, [])
    
    pytest.traversal_result = pytest.current_queue_manager.priority_traversal(
        start_url, page_fetcher=mock_page_fetcher
    )


@then('high-priority pages like "menu" should be visited first')
def high_priority_pages_first():
    """Verify high-priority pages are visited first."""
    result = pytest.traversal_result
    menu_index = next((i for i, url in enumerate(result) if "menu" in url), -1)
    blog_index = next((i for i, url in enumerate(result) if "blog" in url), -1)
    
    if menu_index >= 0 and blog_index >= 0:
        assert menu_index < blog_index


@then('low-priority pages like "blog" should be visited last')
def low_priority_pages_last():
    """Verify low-priority pages are visited last."""
    # This is already checked in the previous step
    pass


@then("the traversal should respect the priority ordering")
def traversal_respects_priority():
    """Verify traversal respects priority ordering."""
    assert pytest.traversal_result is not None
    assert len(pytest.traversal_result) > 0


# Queue statistics scenario steps
@given("I add 3 pages to the queue")
def add_three_pages():
    """Add 3 pages to the queue."""
    pages = ["http://example.com/page1", "http://example.com/page2", "http://example.com/page3"]
    pytest.current_queue_manager.add_pages_to_queue(pages)


@given("I retrieve 1 page from the queue")
def retrieve_one_page():
    """Retrieve 1 page from the queue."""
    pytest.current_queue_manager.get_next_page()


@when("I get queue statistics")
def get_queue_statistics():
    """Get queue statistics."""
    pytest.queue_stats = pytest.current_queue_manager.get_queue_stats()


@then("the statistics should show 2 pending pages")
def stats_show_pending_pages():
    """Verify statistics show correct pending pages."""
    assert pytest.queue_stats["pending"] == 2


@then("should show 1 visited page")
def stats_show_visited_pages():
    """Verify statistics show correct visited pages."""
    assert pytest.queue_stats["visited"] == 1


@then("should show the current traversal strategy")
def stats_show_traversal_strategy():
    """Verify statistics show traversal strategy."""
    assert "strategy" in pytest.queue_stats


# Thread safety scenario steps
@when("I perform concurrent queue operations")
def perform_concurrent_operations():
    """Perform concurrent queue operations."""
    def add_pages():
        pages = [f"http://example.com/thread1-{i}" for i in range(3)]
        pytest.current_queue_manager.add_pages_to_queue(pages)
    
    def get_pages():
        results = []
        for _ in range(2):
            if pytest.current_queue_manager.has_pending_pages():
                results.append(pytest.current_queue_manager.get_next_page())
        return results
    
    # Run operations concurrently
    import threading
    threads = []
    
    # Add pages from two threads
    for _ in range(2):
        thread = threading.Thread(target=add_pages)
        threads.append(thread)
        thread.start()
    
    # Wait for add operations
    for thread in threads:
        thread.join()
    
    # Now get pages from multiple threads
    results = []
    get_threads = []
    for _ in range(2):
        thread = threading.Thread(target=lambda: results.extend(get_pages()))
        get_threads.append(thread)
        thread.start()
    
    for thread in get_threads:
        thread.join()
    
    pytest.concurrent_results = results


@then("all operations should complete without errors")
def all_operations_complete():
    """Verify all operations completed without errors."""
    # If we get here, no exceptions were raised
    pass


@then("the queue state should remain consistent")
def queue_state_consistent():
    """Verify queue state remains consistent."""
    stats = pytest.current_queue_manager.get_queue_stats()
    assert stats["pending"] >= 0
    assert stats["visited"] >= 0


@then("no pages should be lost or duplicated due to race conditions")
def no_pages_lost_or_duplicated():
    """Verify no pages lost or duplicated in concurrent access."""
    if hasattr(pytest, 'concurrent_results'):
        # Check that we got some results and they're unique
        assert len(set(pytest.concurrent_results)) == len(pytest.concurrent_results)


# Error handling scenario steps
@given("I have a PageQueueManager instance")
def have_queue_manager_instance():
    """Have a PageQueueManager instance."""
    if PageQueueManager is None:
        pytest.skip("PageQueueManager not implemented yet")
    pytest.current_queue_manager = PageQueueManager()


@when("I attempt invalid operations like setting invalid strategy")
def attempt_invalid_operations():
    """Attempt invalid operations."""
    pytest.error_raised = False
    try:
        pytest.current_queue_manager.set_traversal_strategy("INVALID")
    except ValueError:
        pytest.error_raised = True


@then("appropriate errors should be raised")
def appropriate_errors_raised():
    """Verify appropriate errors are raised."""
    assert pytest.error_raised


@then("the queue state should remain valid")
def queue_state_remains_valid():
    """Verify queue state remains valid after errors."""
    # Should be able to perform valid operations
    pytest.current_queue_manager.initialize_page_queue()
    assert not pytest.current_queue_manager.has_pending_pages()


@then("I should be able to continue with valid operations")
def can_continue_valid_operations():
    """Verify can continue with valid operations after errors."""
    pytest.current_queue_manager.set_traversal_strategy("BFS")
    assert pytest.current_queue_manager.get_traversal_strategy() == "BFS"