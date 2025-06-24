"""
Unit tests for ProgressMonitorUpdater - Update and notification methods.
Tests the extracted update and notification functionality.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.scraper.progress_monitor_updater import ProgressMonitorUpdater
from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
from src.scraper.progress_monitor_models import OperationType


class TestProgressMonitorUpdater:
    """Test the ProgressMonitorUpdater class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = AdvancedProgressMonitor()
        self.updater = ProgressMonitorUpdater(self.monitor)

    def test_updater_can_be_instantiated(self):
        """Test that ProgressMonitorUpdater can be created."""
        updater = ProgressMonitorUpdater(self.monitor)
        assert updater is not None
        assert updater.monitor == self.monitor

    def test_update_url_completion_delegates_to_operations(self):
        """Test that update_url_completion delegates to operations."""
        with patch.object(self.monitor.operations, 'handle_url_completion') as mock_handle:
            self.updater.update_url_completion("http://test.com", 5.0, True)
            mock_handle.assert_called_once_with("http://test.com", 5.0, True)

    def test_update_page_progress_delegates_to_operations(self):
        """Test that update_page_progress delegates to operations."""
        with patch.object(self.monitor.operations, 'update_page_progress_data') as mock_update:
            self.updater.update_page_progress("http://test.com", 2, 5)
            mock_update.assert_called_once_with("http://test.com", 2, 5)

    def test_add_error_notification_delegates_to_operations(self):
        """Test that add_error_notification delegates to operations."""
        with patch.object(self.monitor.operations, 'handle_error') as mock_handle:
            self.updater.add_error_notification("http://test.com", "404", "Not found")
            mock_handle.assert_called_once_with("http://test.com", "404", "Not found")

    def test_add_completion_event_delegates_to_operations(self):
        """Test that add_completion_event delegates to operations."""
        with patch.object(self.monitor.operations, 'add_completion_event_data') as mock_add:
            details = {"key": "value"}
            self.updater.add_completion_event("url_completed", "http://test.com", details)
            mock_add.assert_called_once_with("url_completed", "http://test.com", details)

    def test_add_page_notification_adds_to_page_notifications(self):
        """Test that add_page_notification adds notification to the list."""
        initial_count = len(self.monitor.page_notifications)
        
        self.updater.add_page_notification("Test message", "http://test.com", "info")
        
        assert len(self.monitor.page_notifications) == initial_count + 1
        notification = self.monitor.page_notifications[-1]
        assert notification["message"] == "Test message"
        assert notification["url"] == "http://test.com"
        assert notification["type"] == "info"
        assert "timestamp" in notification

    def test_update_operation_transition_tracks_transitions(self):
        """Test that operation transitions are tracked."""
        operation = OperationType.ANALYZING_PAGE_STRUCTURE
        
        with patch.object(self.monitor.operations, 'set_current_operation_data') as mock_set:
            self.updater.update_operation_transition(operation)
            mock_set.assert_called_once_with(operation)

        # Check that operation transitions are initialized and tracked
        assert hasattr(self.monitor, 'operation_transitions')
        assert len(self.monitor.operation_transitions) > 0
        transition = self.monitor.operation_transitions[-1]
        assert transition["to_operation"] == operation.value
        assert "timestamp" in transition

    def test_add_resource_warning_adds_to_warnings(self):
        """Test that resource warnings are added to active warnings."""
        self.updater.add_resource_warning("memory", "High memory usage", 400.0)
        
        assert hasattr(self.monitor, 'active_warnings')
        assert len(self.monitor.active_warnings) > 0
        warning = self.monitor.active_warnings[-1]
        assert warning["warning_type"] == "memory"
        assert warning["message"] == "High memory usage"
        assert warning["threshold_value"] == 400.0

    def test_update_memory_statistics_updates_memory_stats(self):
        """Test that memory statistics are updated."""
        initial_usage = self.monitor.memory_stats.current_usage_mb
        
        self.updater.update_memory_statistics(300.0, 350.0)
        
        assert self.monitor.memory_stats.current_usage_mb == 300.0
        assert self.monitor.memory_stats.peak_usage_mb == 350.0

    def test_update_memory_statistics_triggers_warning_on_threshold_exceeded(self):
        """Test that memory warnings are triggered when threshold is exceeded."""
        # Set threshold lower than the usage we'll simulate
        self.monitor.memory_warning_threshold = 200.0
        
        self.updater.update_memory_statistics(300.0)
        
        # Should have created a warning
        assert hasattr(self.monitor, 'active_warnings')
        assert len(self.monitor.active_warnings) > 0
        warning = self.monitor.active_warnings[-1]
        assert warning["warning_type"] == "high_memory_usage"

    def test_clear_notifications_clears_all_when_no_types_specified(self):
        """Test that all notifications are cleared when no types specified."""
        # Add some notifications
        self.monitor.error_notifications.append(Mock())
        self.monitor.page_notifications.append(Mock())
        self.monitor.completion_events.append(Mock())
        
        self.updater.clear_notifications()
        
        assert len(self.monitor.error_notifications) == 0
        assert len(self.monitor.page_notifications) == 0
        assert len(self.monitor.completion_events) == 0

    def test_clear_notifications_clears_specific_types(self):
        """Test that only specified notification types are cleared."""
        # Add some notifications
        self.monitor.error_notifications.append(Mock())
        self.monitor.page_notifications.append(Mock())
        self.monitor.completion_events.append(Mock())
        
        self.updater.clear_notifications(["error", "page"])
        
        assert len(self.monitor.error_notifications) == 0
        assert len(self.monitor.page_notifications) == 0
        assert len(self.monitor.completion_events) == 1  # Should remain

    def test_add_thread_notification_adds_to_page_notifications(self):
        """Test that thread notifications are added to page notifications."""
        initial_count = len(self.monitor.page_notifications)
        
        self.updater.add_thread_notification("thread_1", "Thread started", "info")
        
        assert len(self.monitor.page_notifications) == initial_count + 1
        notification = self.monitor.page_notifications[-1]
        assert notification["thread_id"] == "thread_1"
        assert notification["message"] == "Thread started"
        assert notification["level"] == "thread"

    def test_batch_update_url_completions_processes_multiple_urls(self):
        """Test that batch URL completion updates work."""
        url_results = [
            {"url": "http://test1.com", "processing_time": 2.0, "success": True},
            {"url": "http://test2.com", "processing_time": 3.0, "success": False},
            {"url": "http://test3.com", "processing_time": 1.5, "success": True},
        ]
        
        with patch.object(self.updater, 'update_url_completion') as mock_update:
            self.updater.batch_update_url_completions(url_results)
            
            assert mock_update.call_count == 3
            # Check calls were made (using keyword arguments)
            calls = mock_update.call_args_list
            assert len(calls) == 3
            
            # Verify the calls contain expected data
            call_data = [(call.kwargs['url'], call.kwargs['processing_time'], call.kwargs['success']) for call in calls]
            expected_data = [
                ("http://test1.com", 2.0, True),
                ("http://test2.com", 3.0, False),
                ("http://test3.com", 1.5, True),
            ]
            assert call_data == expected_data


class TestAdvancedProgressMonitorUpdaterIntegration:
    """Test integration between AdvancedProgressMonitor and ProgressMonitorUpdater."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = AdvancedProgressMonitor()

    def test_monitor_has_updater_instance(self):
        """Test that AdvancedProgressMonitor has an updater instance."""
        assert hasattr(self.monitor, 'updater')
        assert self.monitor.updater is not None
        assert isinstance(self.monitor.updater, ProgressMonitorUpdater)

    def test_monitor_delegates_update_methods_to_updater(self):
        """Test that monitor methods delegate to updater."""
        with patch.object(self.monitor.updater, 'update_url_completion') as mock_update:
            self.monitor.update_url_completion("http://test.com", 5.0, True)
            mock_update.assert_called_once_with("http://test.com", 5.0, True)

        with patch.object(self.monitor.updater, 'add_error_notification') as mock_error:
            self.monitor.add_error_notification("http://test.com", "404", "Not found")
            mock_error.assert_called_once_with("http://test.com", "404", "Not found")

    def test_monitor_has_additional_updater_methods(self):
        """Test that monitor exposes additional updater methods."""
        # These should exist as delegation methods
        assert hasattr(self.monitor, 'add_page_notification')
        assert hasattr(self.monitor, 'update_operation_transition')
        assert hasattr(self.monitor, 'add_resource_warning')
        assert hasattr(self.monitor, 'update_memory_statistics')
        assert hasattr(self.monitor, 'clear_notifications')

    def test_monitor_updater_methods_work_end_to_end(self):
        """Test that monitor updater methods work end-to-end."""
        # Test page notification
        self.monitor.add_page_notification("Test message", "http://test.com")
        assert len(self.monitor.page_notifications) > 0
        
        # Test resource warning
        self.monitor.add_resource_warning("memory", "Test warning")
        assert len(self.monitor.active_warnings) > 0
        
        # Test clear notifications
        self.monitor.clear_notifications()
        assert len(self.monitor.page_notifications) == 0
        assert len(self.monitor.active_warnings) == 0