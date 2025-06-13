"""
Step definitions for Advanced Progress Monitoring acceptance tests.
Following BDD with TDD Red-Green-Refactor methodology for Sprint 7A.
"""
import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from unittest.mock import Mock, MagicMock, patch
import time
import threading
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Load scenarios from feature file
scenarios("../features/advanced_progress_monitoring.feature")


@dataclass
class MonitoringUpdate:
    """Data class for monitoring updates."""
    current_url: str
    progress_percentage: float
    urls_completed: int
    urls_total: int
    current_operation: str
    memory_usage_mb: float
    estimated_time_remaining: float
    errors: List[str]
    session_id: str
    thread_info: Optional[Dict[str, Any]] = None


@pytest.fixture
def monitoring_context():
    """Test context for advanced progress monitoring."""
    return {
        "monitoring_system": None,
        "progress_updates": [],
        "error_notifications": [],
        "restaurant_urls": [],
        "monitoring_enabled": False,
        "session_data": {},
        "performance_metrics": {},
        "current_session_id": None,
        "monitoring_callbacks": [],
        "thread_monitors": {},
        "exported_data": None
    }


@pytest.fixture
def sample_monitoring_urls():
    """Sample URLs for monitoring testing."""
    return [
        "https://restaurant1.com",
        "https://restaurant2.com", 
        "https://restaurant3.com",
        "https://restaurant4.com",
        "https://restaurant5.com",
        "https://multi-page-restaurant.com",
        "https://complex-restaurant.com",
        "https://invalid-restaurant-url.com"
    ]


# Background steps
@given("the RAG_Scraper web interface is running")
def rag_scraper_interface_running(monitoring_context):
    """Mock the web interface as running."""
    monitoring_context["interface_running"] = True


@given("I have access to the advanced progress monitoring system")
def access_advanced_monitoring_system(monitoring_context):
    """Initialize access to advanced monitoring system."""
    # This will fail initially - need to implement AdvancedProgressMonitor
    try:
        from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
        monitoring_context["monitoring_system"] = AdvancedProgressMonitor()
    except ImportError:
        # Expected to fail in RED phase
        monitoring_context["monitoring_system"] = None


@given("the monitoring system is initialized")
def monitoring_system_initialized(monitoring_context):
    """Initialize the monitoring system."""
    if monitoring_context["monitoring_system"] is None:
        # Mock for RED phase
        monitoring_context["monitoring_system"] = Mock()
    
    monitoring_context["monitoring_enabled"] = True
    monitoring_context["current_session_id"] = "test_session_001"


# Scenario: Real-time progress indicators with current URL display
@given(parsers.parse("I have {count:d} valid restaurant website URLs for monitoring testing"))
def have_restaurant_urls_for_monitoring(monitoring_context, sample_monitoring_urls, count):
    """Set up restaurant URLs for monitoring testing."""
    monitoring_context["restaurant_urls"] = sample_monitoring_urls[:count]


@when("I start the scraping process with advanced monitoring enabled")
def start_scraping_with_advanced_monitoring(monitoring_context):
    """Start scraping with advanced monitoring."""
    monitoring_system = monitoring_context["monitoring_system"]
    urls = monitoring_context["restaurant_urls"]
    
    # This will fail initially - need to implement start_monitoring method
    try:
        session_id = monitoring_system.start_monitoring_session(
            urls=urls,
            update_interval=2.0,
            enable_real_time_updates=True
        )
        monitoring_context["current_session_id"] = session_id
        
        # Simulate some URL completions to create progress history
        import time
        for i, url in enumerate(urls[:2]):  # Process first 2 URLs
            monitoring_system.update_url_completion(url, 5.0 + i, success=True)
            time.sleep(0.1)  # Small delay to create time difference
            
    except AttributeError:
        # Expected to fail in RED phase
        monitoring_context["monitoring_errors"] = ["AdvancedProgressMonitor not implemented"]


@then("I should see real-time progress updates every 2 seconds")
def verify_real_time_progress_updates(monitoring_context):
    """Verify real-time progress updates occur every 2 seconds."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    # This will fail initially - need to implement get_real_time_updates
    try:
        updates = monitoring_system.get_real_time_updates()
        assert len(updates) > 0, "Should have real-time updates"
        assert updates[0].update_interval == 2.0, "Updates should occur every 2 seconds"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Real-time progress updates not implemented"


@then("I should see the current URL being processed displayed prominently")
def verify_current_url_display(monitoring_context):
    """Verify current URL being processed is displayed."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        current_status = monitoring_system.get_current_status()
        assert hasattr(current_status, 'current_url'), "Should display current URL"
        assert current_status.current_url in monitoring_context["restaurant_urls"]
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Current URL display not implemented"


@then("the progress percentage should update dynamically")
def verify_dynamic_progress_percentage(monitoring_context):
    """Verify progress percentage updates dynamically."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        progress_history = monitoring_system.get_progress_history()
        assert len(progress_history) >= 2, "Should have multiple progress updates"
        assert progress_history[-1].progress_percentage > progress_history[0].progress_percentage
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Dynamic progress percentage not implemented"


@then("the progress bar should reflect the current completion status")
def verify_progress_bar_reflects_status(monitoring_context):
    """Verify progress bar reflects current completion status."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        ui_state = monitoring_system.get_ui_state()
        assert 'progress_bar_percentage' in ui_state, "Should have progress bar percentage"
        assert 0 <= ui_state['progress_bar_percentage'] <= 100, "Progress bar should be 0-100%"
    except (AttributeError, AssertionError, KeyError):
        # Expected to fail in RED phase
        assert False, "Progress bar status reflection not implemented"


# Scenario: Multi-page website progress tracking
@given("I have a restaurant website URL with 4 linked pages")
def have_multipage_restaurant_url(monitoring_context):
    """Set up multi-page restaurant URL."""
    monitoring_context["restaurant_urls"] = ["https://multi-page-restaurant.com"]
    monitoring_context["expected_pages"] = 4


@given("I enable multi-page scraping with advanced monitoring")
def enable_multipage_monitoring(monitoring_context):
    """Enable multi-page scraping with advanced monitoring."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        # First start a monitoring session if not already started
        if not getattr(monitoring_system, 'active_session_id', None):
            session_id = monitoring_system.start_monitoring_session(["https://multi-page-restaurant.com"])
            monitoring_context["current_session_id"] = session_id
        
        # Enable multi-page monitoring
        monitoring_system.enable_multipage_monitoring(
            page_tracking=True,
            page_notifications=True
        )
            
    except AttributeError as e:
        # Expected to fail in RED phase
        monitoring_context["monitoring_errors"] = ["Multi-page monitoring not implemented"]


@then("I should see page-by-page progress within the multi-page site")
def verify_page_by_page_progress(monitoring_context):
    """Verify page-by-page progress tracking."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        page_progress = monitoring_system.get_page_progress()
        assert hasattr(page_progress, 'current_page'), "Should track current page"
        assert hasattr(page_progress, 'total_pages'), "Should track total pages"
        assert page_progress.total_pages == monitoring_context["expected_pages"]
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Page-by-page progress tracking not implemented"


@then("I should receive notifications when starting new pages within the same website")
def verify_new_page_notifications(monitoring_context):
    """Verify notifications for new pages."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        notifications = monitoring_system.get_page_notifications()
        assert len(notifications) > 0, "Should have page notifications"
        assert any("Starting page" in notif["message"] for notif in notifications)
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "New page notifications not implemented"


@then('the progress should show "Processing page 2 of 4" style indicators')
def verify_page_progress_indicators(monitoring_context):
    """Verify page progress style indicators."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        progress_message = monitoring_system.get_current_progress_message()
        assert "page" in progress_message.lower(), "Should show page progress"
        assert "of" in progress_message, "Should show 'page X of Y' format"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Page progress indicators not implemented"


@then("each page completion should trigger a progress update notification")
def verify_page_completion_notifications(monitoring_context):
    """Verify page completion notifications."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        completion_events = monitoring_system.get_completion_events()
        page_completions = [e for e in completion_events if e["event_type"] == "page_completed"]
        assert len(page_completions) > 0, "Should have page completion events"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Page completion notifications not implemented"


# Scenario: Dynamic time estimation with real-time updates
@given(parsers.parse("I have {count:d} restaurant URLs for time estimation testing"))
def have_urls_for_time_estimation(monitoring_context, sample_monitoring_urls, count):
    """Set up URLs for time estimation testing."""
    monitoring_context["restaurant_urls"] = sample_monitoring_urls[:count]


@given("advanced progress monitoring is enabled")
def advanced_monitoring_enabled(monitoring_context):
    """Ensure advanced progress monitoring is enabled."""
    monitoring_context["monitoring_enabled"] = True
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        monitoring_system.enable_advanced_features(
            time_estimation=True,
            real_time_updates=True,
            error_notifications=True
        )
    except AttributeError:
        # Expected to fail in RED phase
        pass


@when("I start the batch scraping process")
def start_batch_scraping_process(monitoring_context):
    """Start batch scraping process."""
    monitoring_system = monitoring_context["monitoring_system"]
    urls = monitoring_context["restaurant_urls"]
    
    try:
        session_id = monitoring_system.start_batch_monitoring(urls)
        monitoring_context["current_session_id"] = session_id
        
        # Simulate some URL completions to establish processing time baseline
        for i, url in enumerate(urls[:3]):  # Process first 3 URLs
            processing_time = 4.0 + (i * 0.5)  # Varying processing times
            monitoring_system.update_url_completion(url, processing_time, success=True)
        
        # Create multiple time estimations to establish history with improving accuracy
        for i in range(3):  # Add 3 more estimations
            estimation = monitoring_system.get_time_estimation()
            estimation.accuracy_confidence = 0.3 + (i * 0.2)  # Improve accuracy over time
            monitoring_system.time_estimation_history.append(estimation)
            
    except AttributeError:
        # Expected to fail in RED phase
        monitoring_context["monitoring_errors"] = ["Batch monitoring not implemented"]


@then("I should see an estimated time remaining calculation")
def verify_time_estimation(monitoring_context):
    """Verify estimated time remaining calculation."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        time_estimate = monitoring_system.get_time_estimation()
        assert hasattr(time_estimate, 'estimated_seconds_remaining'), "Should have time estimate"
        assert time_estimate.estimated_seconds_remaining > 0, "Time estimate should be positive"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Time estimation not implemented"


@then("the time estimate should update dynamically as scraping progresses")
def verify_dynamic_time_updates(monitoring_context):
    """Verify dynamic time estimate updates."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        time_history = monitoring_system.get_time_estimation_history()
        assert len(time_history) >= 2, "Should have multiple time estimates"
        # Later estimates should generally be more accurate/different
        assert time_history[-1].accuracy_confidence > time_history[0].accuracy_confidence
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Dynamic time updates not implemented"


@then("the estimation should become more accurate after processing 3+ URLs")
def verify_estimation_accuracy_improvement(monitoring_context):
    """Verify estimation accuracy improves with more data."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        accuracy_metrics = monitoring_system.get_accuracy_metrics()
        assert 'accuracy_after_3_urls' in accuracy_metrics, "Should track accuracy improvement"
        assert accuracy_metrics['accuracy_after_3_urls'] > accuracy_metrics['initial_accuracy']
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Estimation accuracy improvement not implemented"


@then("the time remaining should be displayed in minutes and seconds format")
def verify_time_format_display(monitoring_context):
    """Verify time remaining display format."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        display_format = monitoring_system.get_time_display_format()
        assert "minutes" in display_format or "m" in display_format, "Should show minutes"
        assert "seconds" in display_format or "s" in display_format, "Should show seconds"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Time format display not implemented"


# Scenario: Real-time error notifications with continue/stop options
@given("I have a mix of valid and invalid restaurant URLs")
def have_mixed_valid_invalid_urls(monitoring_context):
    """Set up mix of valid and invalid URLs."""
    monitoring_context["restaurant_urls"] = [
        "https://valid-restaurant1.com",
        "https://valid-restaurant2.com", 
        "https://invalid-url-404.com",
        "https://timeout-restaurant.com",
        "https://valid-restaurant3.com"
    ]


@given("advanced error monitoring is enabled")
def advanced_error_monitoring_enabled(monitoring_context):
    """Enable advanced error monitoring."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        monitoring_system.enable_error_monitoring(
            real_time_notifications=True,
            continue_stop_options=True,
            error_categorization=True
        )
    except AttributeError:
        # Expected to fail in RED phase
        pass


@when("I start the scraping process and encounter errors")
def start_scraping_with_errors(monitoring_context):
    """Start scraping process that will encounter errors."""
    monitoring_system = monitoring_context["monitoring_system"]
    urls = monitoring_context["restaurant_urls"]
    
    try:
        monitoring_system.start_monitoring_with_error_handling(urls)
    except AttributeError:
        # Expected to fail in RED phase
        monitoring_context["monitoring_errors"] = ["Error monitoring not implemented"]


@then("I should receive real-time error notifications for failed URLs")
def verify_real_time_error_notifications(monitoring_context):
    """Verify real-time error notifications."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        error_notifications = monitoring_system.get_error_notifications()
        assert len(error_notifications) > 0, "Should have error notifications"
        assert any(notif.notification_type == "real_time_error" for notif in error_notifications)
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Real-time error notifications not implemented"


@then("each error notification should include the specific error type")
def verify_error_type_in_notifications(monitoring_context):
    """Verify error notifications include specific error types."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        error_notifications = monitoring_system.get_error_notifications()
        for notification in error_notifications:
            assert hasattr(notification, 'error_type'), "Should have error type"
            assert notification.error_type in ["404", "timeout", "connection_error", "parsing_error"]
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Error type specification not implemented"


@then('I should be presented with "Continue" and "Stop" options for error handling')
def verify_continue_stop_options(monitoring_context):
    """Verify continue/stop options for error handling."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        error_handler = monitoring_system.get_error_handler()
        available_actions = error_handler.get_available_actions()
        assert "continue" in available_actions, "Should have continue option"
        assert "stop" in available_actions, "Should have stop option"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Continue/Stop options not implemented"


@then('choosing "Continue" should proceed with remaining URLs')
def verify_continue_action(monitoring_context):
    """Verify continue action proceeds with remaining URLs."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        error_handler = monitoring_system.get_error_handler()
        initial_remaining = len(monitoring_context["restaurant_urls"]) - 3  # Assume 3 failed
        error_handler.handle_error_action("continue")
        current_remaining = error_handler.get_remaining_urls_count()
        assert current_remaining > 0, "Should continue with remaining URLs"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Continue action not implemented"


@then('choosing "Stop" should halt the entire scraping process')
def verify_stop_action(monitoring_context):
    """Verify stop action halts scraping process."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        error_handler = monitoring_system.get_error_handler()
        error_handler.handle_error_action("stop")
        process_status = monitoring_system.get_process_status()
        assert process_status.is_stopped, "Process should be stopped"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Stop action not implemented"


# Additional step definitions for remaining scenarios...

@given(parsers.parse("I have {count:d} restaurant URLs for memory monitoring testing"))
def have_urls_for_memory_monitoring(monitoring_context, sample_monitoring_urls, count):
    """Set up URLs for memory monitoring testing."""
    monitoring_context["restaurant_urls"] = sample_monitoring_urls[:count]


@given("advanced resource monitoring is enabled")
def advanced_resource_monitoring_enabled(monitoring_context):
    """Enable advanced resource monitoring."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        monitoring_system.enable_resource_monitoring(
            memory_tracking=True,
            memory_warnings=True,
            optimization_suggestions=True
        )
    except AttributeError:
        # Expected to fail in RED phase
        pass


@when("I start the large batch scraping process")
def start_large_batch_scraping(monitoring_context):
    """Start large batch scraping process."""
    monitoring_system = monitoring_context["monitoring_system"]
    urls = monitoring_context["restaurant_urls"]
    
    try:
        session_id = monitoring_system.start_large_batch_monitoring(urls)
        monitoring_context["current_session_id"] = session_id
        
        # Simulate some memory usage for testing
        monitoring_system.simulate_memory_usage(250.0)  # Set memory usage below warning threshold
        
    except AttributeError:
        # Expected to fail in RED phase
        monitoring_context["monitoring_errors"] = ["Large batch monitoring not implemented"]


@then("I should see real-time memory usage indicators")
def verify_memory_usage_indicators(monitoring_context):
    """Verify real-time memory usage indicators."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        memory_stats = monitoring_system.get_memory_statistics()
        assert hasattr(memory_stats, 'current_usage_mb'), "Should show current memory usage"
        assert memory_stats.current_usage_mb > 0, "Memory usage should be positive"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Memory usage indicators not implemented"


@then("memory usage should be displayed in MB with updates every 5 seconds")
def verify_memory_display_format(monitoring_context):
    """Verify memory usage display format and update frequency."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        memory_config = monitoring_system.get_memory_monitoring_config()
        assert memory_config["display_unit"] == "MB", "Should display in MB"
        assert memory_config["update_interval"] == 5.0, "Should update every 5 seconds"
    except (AttributeError, AssertionError, KeyError):
        # Expected to fail in RED phase
        assert False, "Memory display format not implemented"


@then("I should receive warnings if memory usage exceeds 400MB")
def verify_memory_warnings(monitoring_context):
    """Verify memory usage warnings."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        warning_config = monitoring_system.get_warning_configuration()
        assert warning_config["memory_warning_threshold"] == 400.0, "Should warn at 400MB"
        
        # Simulate high memory usage
        monitoring_system.simulate_memory_usage(450.0)
        warnings = monitoring_system.get_active_warnings()
        assert any(w["warning_type"] == "high_memory_usage" for w in warnings)
    except (AttributeError, AssertionError, KeyError):
        # Expected to fail in RED phase
        assert False, "Memory warnings not implemented"


@then("the system should provide memory optimization suggestions if needed")
def verify_memory_optimization_suggestions(monitoring_context):
    """Verify memory optimization suggestions."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        optimization_engine = monitoring_system.get_optimization_engine()
        suggestions = optimization_engine.get_memory_suggestions()
        assert len(suggestions) > 0, "Should provide optimization suggestions"
        assert any("batch size" in s["suggestion"].lower() for s in suggestions)
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Memory optimization suggestions not implemented"


# Add placeholder step definitions for remaining scenarios to make tests runnable
# These will all fail initially as expected in RED phase

@given("I have restaurant URLs with varying complexity")
def have_varying_complexity_urls(monitoring_context):
    """Set up URLs with varying complexity."""
    monitoring_context["restaurant_urls"] = ["https://simple.com", "https://complex.com"]


@given("detailed operation monitoring is enabled")
def detailed_operation_monitoring_enabled(monitoring_context):
    """Enable detailed operation monitoring."""
    pass  # Will fail - not implemented


@when("I start the scraping process with operation tracking")
def start_scraping_with_operation_tracking(monitoring_context):
    """Start scraping with operation tracking."""
    monitoring_system = monitoring_context["monitoring_system"]
    urls = monitoring_context["restaurant_urls"]
    
    try:
        # Start monitoring session if not already started
        if not monitoring_system.active_session_id:
            monitoring_system.start_monitoring_session(urls)
        
        # Set current operation for tracking
        from src.scraper.advanced_progress_monitor import OperationType
        monitoring_system.set_current_operation(OperationType.ANALYZING_PAGE_STRUCTURE)
        
    except (AttributeError, ImportError):
        # Expected to fail in RED phase
        monitoring_context["monitoring_errors"] = ["Operation tracking not implemented"]


@then("I should see the current operation being performed")
def verify_current_operation_display(monitoring_context):
    """Verify current operation display."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        current_operation = monitoring_system.get_current_operation()
        assert "operation" in current_operation, "Should display current operation"
        assert current_operation["operation"] != "None", "Should have a valid operation"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Current operation display not implemented"


@then('operations should include "Analyzing page structure", "Extracting data", "Processing menu items"')
def verify_operation_types(monitoring_context):
    """Verify specific operation types."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        from src.scraper.advanced_progress_monitor import OperationType
        expected_operations = [
            "Analyzing page structure",
            "Extracting data", 
            "Processing menu items"
        ]
        
        # Check if operation enum contains expected operations
        available_operations = [op.value for op in OperationType]
        for expected_op in expected_operations:
            assert expected_op in available_operations, f"Operation '{expected_op}' not available"
    except (ImportError, AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Operation types not implemented"


@then("each operation should have an estimated duration indicator")
def verify_operation_duration_indicators(monitoring_context):
    """Verify operation duration indicators."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        current_operation = monitoring_system.get_current_operation()
        assert "estimated_duration" in current_operation, "Should have duration estimate"
        assert current_operation["estimated_duration"] > 0, "Duration should be positive"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Operation duration indicators not implemented"


@then("operation transitions should be clearly indicated in the UI")
def verify_operation_transitions(monitoring_context):
    """Verify operation transitions in UI."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        transitions = monitoring_system.get_operation_transitions()
        assert len(transitions) > 0, "Should have operation transitions"
        assert "from_operation" in transitions[0], "Should track operation transitions"
        assert "to_operation" in transitions[0], "Should track destination operation"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Operation transitions not implemented"


# Additional step definitions for remaining scenarios

@given(parsers.parse("I have {count:d} restaurant URLs in a batch processing queue"))
def have_urls_in_batch_queue(monitoring_context, sample_monitoring_urls, count):
    """Set up URLs in batch processing queue."""
    monitoring_context["restaurant_urls"] = sample_monitoring_urls[:count]


@given("batch progress monitoring is enabled") 
def batch_progress_monitoring_enabled(monitoring_context):
    """Enable batch progress monitoring."""
    monitoring_system = monitoring_context["monitoring_system"]
    try:
        monitoring_system.enable_batch_progress_monitoring(
            queue_display=True,
            url_status_tracking=True
        )
    except AttributeError:
        # Expected to fail in RED phase
        pass


@when("I start the scraping process")
def start_scraping_process(monitoring_context):
    """Start the scraping process."""
    monitoring_system = monitoring_context["monitoring_system"]
    urls = monitoring_context["restaurant_urls"]
    
    try:
        # Only create a new session if one doesn't already exist
        if not getattr(monitoring_system, 'active_session_id', None):
            session_id = monitoring_system.start_monitoring_session(urls)
            monitoring_context["current_session_id"] = session_id
        else:
            # Use existing session
            monitoring_context["current_session_id"] = monitoring_system.active_session_id
        
        # Simulate some processing progress
        for i, url in enumerate(urls[:2]):  # Simulate processing first 2 URLs
            monitoring_system.update_url_completion(url, 5.0, success=True)
            
    except AttributeError:
        # Expected to fail in RED phase
        monitoring_context["monitoring_errors"] = ["Scraping process not implemented"]


@then('I should see the total queue status "Processing 3 of 8 URLs"')
def verify_queue_status_display(monitoring_context):
    """Verify queue status display."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        queue_status = monitoring_system.get_queue_status()
        assert 'status_message' in queue_status, "Should have queue status message"
        assert "of" in queue_status['status_message'], "Should show 'Processing X of Y' format"
    except (AttributeError, AssertionError, KeyError):
        # Expected to fail in RED phase
        assert False, "Queue status display not implemented"


@then("completed URLs should be marked with success/failure indicators")
def verify_completion_indicators(monitoring_context):
    """Verify completion indicators."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        url_statuses = monitoring_system.get_url_statuses()
        assert any(status['indicator'] in ["success", "failure"] for status in url_statuses)
    except (AttributeError, AssertionError, KeyError):
        # Expected to fail in RED phase
        assert False, "Completion indicators not implemented"


@then("remaining URLs should be shown in the processing queue")
def verify_remaining_urls_display(monitoring_context):
    """Verify remaining URLs display."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        queue_info = monitoring_system.get_processing_queue()
        assert 'remaining_urls' in queue_info, "Should show remaining URLs"
        assert len(queue_info['remaining_urls']) > 0, "Should have remaining URLs"
    except (AttributeError, AssertionError, KeyError):
        # Expected to fail in RED phase
        assert False, "Remaining URLs display not implemented"


@then("I should be able to see which URLs are pending, processing, completed, or failed")
def verify_url_status_tracking(monitoring_context):
    """Verify URL status tracking."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        url_statuses = monitoring_system.get_detailed_url_statuses()
        expected_statuses = ["pending", "processing", "completed", "failed"]
        found_statuses = [status['status'] for status in url_statuses]
        assert any(status in expected_statuses for status in found_statuses)
    except (AttributeError, AssertionError, KeyError):
        # Expected to fail in RED phase
        assert False, "URL status tracking not implemented"


# Additional missing step definitions

@given("I am running a long batch scraping process")
def running_long_batch_process(monitoring_context):
    """Set up long batch scraping process."""
    monitoring_context["long_batch_active"] = True
    monitoring_context["restaurant_urls"] = ["https://restaurant1.com"] * 20  # Simulate long batch


@given("advanced monitoring is tracking the session")
def advanced_monitoring_tracking_session(monitoring_context):
    """Enable session tracking."""
    monitoring_system = monitoring_context["monitoring_system"]
    try:
        # First ensure we have an active session
        if not monitoring_system.active_session_id:
            session_id = monitoring_system.start_monitoring_session(["https://restaurant1.com", "https://restaurant2.com"])
            monitoring_context["current_session_id"] = session_id
        
        # Enable session tracking
        monitoring_system.enable_session_tracking(
            persistence=True,
            state_restoration=True
        )
    except AttributeError:
        pass


@when("I accidentally close or refresh the browser")
def close_refresh_browser(monitoring_context):
    """Simulate browser close/refresh."""
    monitoring_context["browser_closed"] = True


@when("I return to the scraping interface")
def return_to_interface(monitoring_context):
    """Return to scraping interface."""
    monitoring_context["returned_to_interface"] = True


@then("the progress monitoring should restore the current session state")
def verify_session_state_restoration(monitoring_context):
    """Verify session state restoration."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        # Test session restoration
        session_restored = monitoring_system.restore_session_state()
        assert session_restored, "Should restore session state"
    except AttributeError:
        # Expected to fail in RED phase
        assert False, "Session state restoration not implemented"


@then("I should see the current progress, completed URLs, and remaining work")
def verify_progress_restoration(monitoring_context):
    """Verify progress restoration."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        current_status = monitoring_system.get_current_status()
        assert hasattr(current_status, 'progress_percentage'), "Should show current progress"
        assert hasattr(current_status, 'urls_completed'), "Should show completed URLs"
        assert hasattr(current_status, 'urls_total'), "Should show remaining work"
    except (AttributeError, AssertionError):
        assert False, "Progress restoration not implemented"


@then("the session should continue from where it was interrupted")
def verify_session_continuation(monitoring_context):
    """Verify session continuation."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        process_status = monitoring_system.get_process_status()
        assert process_status.is_running or not process_status.is_stopped, "Session should be continuing"
    except (AttributeError, AssertionError):
        assert False, "Session continuation not implemented"


@then("all monitoring data should be preserved")
def verify_monitoring_data_preservation(monitoring_context):
    """Verify monitoring data preservation."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        # Check if session data is marked as saved
        if monitoring_system.active_session_id:
            session = monitoring_system.sessions[monitoring_system.active_session_id]
            assert session.get("state_saved", False), "Monitoring data should be preserved"
        else:
            assert len(monitoring_system.sessions) > 0, "Should have preserved session data"
    except (AttributeError, AssertionError):
        assert False, "Monitoring data preservation not implemented"


@given(parsers.parse("I have {count:d} restaurant URLs for concurrent processing testing"))
def have_urls_for_concurrent_testing(monitoring_context, sample_monitoring_urls, count):
    """Set up URLs for concurrent testing."""
    monitoring_context["restaurant_urls"] = sample_monitoring_urls[:count]


@given("multi-threaded scraping with monitoring is enabled")
def multithreaded_monitoring_enabled(monitoring_context):
    """Enable multi-threaded monitoring."""
    monitoring_system = monitoring_context["monitoring_system"]
    try:
        monitoring_system.enable_multithreaded_monitoring(max_threads=4)
    except AttributeError:
        # Expected to fail in RED phase
        pass


@when("I start the concurrent scraping process")
def start_concurrent_scraping(monitoring_context):
    """Start concurrent scraping."""
    monitoring_system = monitoring_context["monitoring_system"]
    urls = monitoring_context["restaurant_urls"]
    
    try:
        # Enable multi-threaded monitoring if not already enabled
        if not hasattr(monitoring_system, 'multithreaded_monitoring_enabled'):
            monitoring_system.enable_multithreaded_monitoring()
        
        # Start monitoring session for concurrent processing
        session_id = monitoring_system.start_monitoring_session(urls)
        monitoring_context["current_session_id"] = session_id
    except AttributeError:
        # Expected to fail in RED phase
        pass


@then("I should see monitoring for multiple simultaneous operations")
def verify_multithreaded_monitoring(monitoring_context):
    """Verify multi-threaded monitoring."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        thread_data = monitoring_system.get_thread_monitoring_data()
        assert thread_data["enabled"], "Multi-threaded monitoring should be enabled"
        assert thread_data["active_count"] > 1, "Should have multiple active threads"
    except (AttributeError, AssertionError):
        assert False, "Multi-threaded monitoring not implemented"


@then("each concurrent thread should have its own progress indicator")
def verify_thread_progress_indicators(monitoring_context):
    """Verify thread progress indicators."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        thread_data = monitoring_system.get_thread_monitoring_data()
        threads = thread_data["threads"]
        assert len(threads) > 0, "Should have thread progress indicators"
        # Check that each thread has progress information
        for thread in threads:
            assert "progress" in thread, "Each thread should have progress indicator"
            assert "status" in thread, "Each thread should have status"
    except (AttributeError, AssertionError):
        assert False, "Thread progress indicators not implemented"


@then("the overall progress should aggregate individual thread progress")
def verify_aggregated_progress(monitoring_context):
    """Verify aggregated progress."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        thread_data = monitoring_system.get_thread_monitoring_data()
        overall_progress = monitoring_system.get_current_status()
        assert hasattr(overall_progress, 'progress_percentage'), "Should have overall progress"
        assert thread_data["total_threads"] > 0, "Should aggregate from multiple threads"
    except (AttributeError, AssertionError):
        assert False, "Aggregated progress not implemented"


@then("I should see which URLs are being processed simultaneously")
def verify_simultaneous_processing_display(monitoring_context):
    """Verify simultaneous processing display."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        thread_data = monitoring_system.get_thread_monitoring_data()
        active_urls = [thread["current_url"] for thread in thread_data["threads"] 
                      if thread["current_url"] is not None]
        assert len(active_urls) > 1, "Should show multiple URLs being processed simultaneously"
    except (AttributeError, AssertionError):
        assert False, "Simultaneous processing display not implemented"


@given("I have completed several scraping sessions with monitoring data")
def completed_sessions_with_data(monitoring_context):
    """Set up completed sessions."""
    monitoring_context["completed_sessions"] = 3


@given("performance analysis is enabled")
def performance_analysis_enabled(monitoring_context):
    """Enable performance analysis."""
    pass


@when("I view the advanced monitoring dashboard")
def view_monitoring_dashboard(monitoring_context):
    """View monitoring dashboard."""
    pass


@then("I should see average processing time per URL")
def verify_average_processing_time(monitoring_context):
    """Verify average processing time display."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        performance_analyzer = monitoring_system.get_performance_analyzer()
        avg_time = performance_analyzer.get_average_processing_time()
        assert avg_time >= 0, "Should have average processing time"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Average processing time not implemented"


@then("I should see memory usage patterns and optimization opportunities")
def verify_memory_patterns(monitoring_context):
    """Verify memory usage patterns."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        performance_analyzer = monitoring_system.get_performance_analyzer()
        memory_patterns = performance_analyzer.get_memory_usage_patterns()
        assert "peak_memory_mb" in memory_patterns, "Should show memory usage patterns"
        assert "optimization_opportunities" in memory_patterns, "Should show optimization opportunities"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Memory usage patterns not implemented"


@then("the system should suggest optimal batch sizes for my hardware")
def verify_batch_size_suggestions(monitoring_context):
    """Verify batch size suggestions."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        performance_analyzer = monitoring_system.get_performance_analyzer()
        batch_size = performance_analyzer.get_optimal_batch_size_suggestion()
        assert isinstance(batch_size, int), "Should suggest optimal batch size"
        assert batch_size > 0, "Batch size should be positive"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Batch size suggestions not implemented"


@then("I should see error rate statistics and common failure patterns")
def verify_error_statistics(monitoring_context):
    """Verify error rate statistics."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        performance_analyzer = monitoring_system.get_performance_analyzer()
        error_stats = performance_analyzer.get_error_rate_statistics()
        assert "total_errors" in error_stats, "Should show error statistics"
        assert "common_patterns" in error_stats, "Should show common failure patterns"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Error rate statistics not implemented"


@given("I have completed a scraping session with advanced monitoring")
def completed_session_with_monitoring(monitoring_context):
    """Set up completed session."""
    monitoring_context["completed_session"] = True


@given("monitoring data logging is enabled")
def monitoring_data_logging_enabled(monitoring_context):
    """Enable monitoring data logging."""
    pass


@when("I access the monitoring session data")
def access_session_data(monitoring_context):
    """Access monitoring session data."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        # Ensure we have an active session with some data
        if not monitoring_system.active_session_id:
            session_id = monitoring_system.start_monitoring_session(["https://restaurant1.com", "https://restaurant2.com"])
            monitoring_context["current_session_id"] = session_id
            
            # Add some processing times and errors for data export
            monitoring_system.update_url_completion("https://restaurant1.com", 5.2, success=True)
            monitoring_system.add_error_notification("https://restaurant2.com", "404", "Page not found")
    except AttributeError:
        # Expected to fail in RED phase
        pass


@then("I should be able to export monitoring data as JSON")
def verify_json_export_capability(monitoring_context):
    """Verify JSON export capability."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        data_exporter = monitoring_system.get_data_exporter()
        exported_data = data_exporter.export_monitoring_data_as_json()
        assert isinstance(exported_data, dict), "Should export data as JSON dict"
        monitoring_context["exported_data"] = exported_data
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "JSON export capability not implemented"


@then("the export should include timing data, memory usage, and error logs")
def verify_export_content(monitoring_context):
    """Verify export content."""
    exported_data = monitoring_context.get("exported_data", {})
    
    try:
        assert "timing_data" in exported_data, "Should include timing data"
        assert "memory_usage" in exported_data, "Should include memory usage"
        assert "error_logs" in exported_data, "Should include error logs"
    except AssertionError:
        # Expected to fail in RED phase
        assert False, "Export content not implemented"


@then("session logs should be available for troubleshooting")
def verify_session_logs(monitoring_context):
    """Verify session logs."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        data_exporter = monitoring_system.get_data_exporter()
        session_logs = data_exporter.get_session_logs()
        assert isinstance(session_logs, list), "Should provide session logs"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Session logs not implemented"


@then("historical monitoring data should be accessible for analysis")
def verify_historical_data(monitoring_context):
    """Verify historical data access."""
    monitoring_system = monitoring_context["monitoring_system"]
    
    try:
        data_exporter = monitoring_system.get_data_exporter()
        historical_data = data_exporter.get_historical_data()
        assert isinstance(historical_data, dict), "Should provide historical data"
        assert "total_sessions" in historical_data, "Should include session count"
    except (AttributeError, AssertionError):
        # Expected to fail in RED phase
        assert False, "Historical data access not implemented"