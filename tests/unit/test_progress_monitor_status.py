"""
Unit tests for ProgressMonitorStatus class.
Tests the extracted status and data retrieval functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
from src.scraper.progress_monitor_status import ProgressMonitorStatus
from src.scraper.progress_monitor_models import (
    MonitoringUpdate,
    PageProgress,
    MemoryStats,
    TimeEstimation,
    ProcessStatus,
    URLStatus,
)


class TestProgressMonitorStatus:
    """Test cases for ProgressMonitorStatus class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = AdvancedProgressMonitor()
        self.status_handler = self.monitor.status
        
        # Start a test session
        self.session_id = self.monitor.start_monitoring_session(
            ["https://test1.com", "https://test2.com"]
        )

    def test_status_handler_initialization(self):
        """Test that status handler is properly initialized."""
        assert isinstance(self.status_handler, ProgressMonitorStatus)
        assert self.status_handler.monitor is self.monitor

    def test_get_status_delegates_to_get_current_status(self):
        """Test that get_status delegates to get_current_status."""
        status = self.status_handler.get_status()
        current_status = self.status_handler.get_current_status()
        
        assert isinstance(status, MonitoringUpdate)
        assert isinstance(current_status, MonitoringUpdate)
        assert status.session_id == current_status.session_id

    def test_get_current_status_returns_monitoring_update(self):
        """Test that get_current_status returns proper MonitoringUpdate."""
        status = self.status_handler.get_current_status()
        
        assert isinstance(status, MonitoringUpdate)
        assert status.session_id == self.session_id
        assert status.urls_total == 2
        assert status.urls_completed == 0

    def test_get_detailed_status_returns_session_info(self):
        """Test that get_detailed_status returns detailed session information."""
        detailed_status = self.status_handler.get_detailed_status()
        
        assert isinstance(detailed_status, dict)
        assert detailed_status["session_id"] == self.session_id
        assert detailed_status["total_urls"] == 2
        assert "status" in detailed_status
        assert "multipage_enabled" in detailed_status

    def test_get_ui_state_returns_progress_info(self):
        """Test that get_ui_state returns UI-relevant progress information."""
        ui_state = self.status_handler.get_ui_state()
        
        assert isinstance(ui_state, dict)
        assert "progress_bar_percentage" in ui_state
        assert "current_url" in ui_state
        assert "status_message" in ui_state
        assert ui_state["progress_bar_percentage"] == 0  # No completed URLs yet

    def test_get_page_progress_returns_page_progress_object(self):
        """Test that get_page_progress returns PageProgress object."""
        page_progress = self.status_handler.get_page_progress()
        
        assert isinstance(page_progress, PageProgress)
        assert page_progress.current_page == 1
        assert page_progress.total_pages == 1  # Default when multipage is disabled

    def test_get_multi_page_config_returns_configuration(self):
        """Test that get_multi_page_config returns multipage configuration."""
        config = self.status_handler.get_multi_page_config()
        
        assert isinstance(config, dict)
        assert "enabled" in config
        assert "page_tracking" in config
        assert "page_notifications" in config
        assert config["enabled"] is False  # Default

    def test_set_multi_page_config_updates_configuration(self):
        """Test that set_multi_page_config updates the multipage configuration."""
        new_config = {
            "enabled": True,
            "page_tracking": True,
            "page_notifications": True,
            "total_pages": 5
        }
        
        self.status_handler.set_multi_page_config(new_config)
        updated_config = self.status_handler.get_multi_page_config()
        
        assert updated_config["enabled"] is True
        assert updated_config["page_tracking"] is True
        assert updated_config["page_notifications"] is True
        assert updated_config["total_pages"] == 5

    def test_get_page_progress_with_multipage_enabled(self):
        """Test get_page_progress when multipage is enabled."""
        # Enable multipage monitoring
        self.monitor.enable_multipage_monitoring()
        
        page_progress = self.status_handler.get_page_progress()
        
        assert isinstance(page_progress, PageProgress)
        assert page_progress.total_pages == 4  # Default multipage total

    def test_get_real_time_updates_returns_monitoring_updates(self):
        """Test that get_real_time_updates returns list of MonitoringUpdate objects."""
        updates = self.status_handler.get_real_time_updates()
        
        assert isinstance(updates, list)
        if updates:  # If session is active
            assert isinstance(updates[0], MonitoringUpdate)
            assert updates[0].session_id == self.session_id

    def test_get_progress_history_returns_list(self):
        """Test that get_progress_history returns list of updates."""
        history = self.status_handler.get_progress_history()
        
        assert isinstance(history, list)

    def test_get_current_progress_message_returns_readable_string(self):
        """Test that get_current_progress_message returns human-readable string."""
        message = self.status_handler.get_current_progress_message()
        
        assert isinstance(message, str)
        assert "Processing URL" in message or "Processing page" in message

    def test_get_time_estimation_returns_time_estimation_object(self):
        """Test that get_time_estimation returns TimeEstimation object."""
        estimation = self.status_handler.get_time_estimation()
        
        assert isinstance(estimation, TimeEstimation)
        assert hasattr(estimation, "estimated_seconds_remaining")
        assert hasattr(estimation, "accuracy_confidence")

    def test_get_process_status_returns_process_status_object(self):
        """Test that get_process_status returns ProcessStatus object."""
        process_status = self.status_handler.get_process_status()
        
        assert isinstance(process_status, ProcessStatus)
        assert hasattr(process_status, "is_running")
        assert hasattr(process_status, "total_urls")

    @patch('psutil.Process')
    def test_get_memory_statistics_returns_memory_stats(self, mock_process):
        """Test that get_memory_statistics returns MemoryStats object."""
        # Mock memory info
        mock_process.return_value.memory_info.return_value.rss = 100 * 1024 * 1024  # 100MB
        
        memory_stats = self.status_handler.get_memory_statistics()
        
        assert isinstance(memory_stats, MemoryStats)
        assert hasattr(memory_stats, "current_usage_mb")
        assert hasattr(memory_stats, "peak_usage_mb")

    def test_get_queue_status_returns_queue_information(self):
        """Test that get_queue_status returns queue status information."""
        queue_status = self.status_handler.get_queue_status()
        
        assert isinstance(queue_status, dict)
        assert "status_message" in queue_status
        assert "completed_count" in queue_status
        assert "total_count" in queue_status

    def test_get_url_statuses_returns_url_status_list(self):
        """Test that get_url_statuses returns list of URL status information."""
        url_statuses = self.status_handler.get_url_statuses()
        
        assert isinstance(url_statuses, list)
        if url_statuses:  # If there are URLs
            assert "url" in url_statuses[0]
            assert "status" in url_statuses[0]
            assert "indicator" in url_statuses[0]

    def test_get_processing_queue_returns_queue_information(self):
        """Test that get_processing_queue returns processing queue information."""
        queue_info = self.status_handler.get_processing_queue()
        
        assert isinstance(queue_info, dict)
        assert "remaining_urls" in queue_info
        assert "total_remaining" in queue_info

    def test_get_current_operation_returns_operation_info(self):
        """Test that get_current_operation returns current operation information."""
        operation_info = self.status_handler.get_current_operation()
        
        assert isinstance(operation_info, dict)
        assert "operation" in operation_info

    def test_get_thread_monitoring_data_returns_thread_info(self):
        """Test that get_thread_monitoring_data returns thread monitoring information."""
        thread_data = self.status_handler.get_thread_monitoring_data()
        
        assert isinstance(thread_data, dict)
        assert "enabled" in thread_data
        assert "threads" in thread_data

    def test_status_methods_work_without_active_session(self):
        """Test that status methods handle no active session gracefully."""
        # Create a new monitor without active session
        empty_monitor = AdvancedProgressMonitor()
        empty_status = empty_monitor.status
        
        # These should not raise exceptions
        status = empty_status.get_current_status()
        ui_state = empty_status.get_ui_state()
        page_progress = empty_status.get_page_progress()
        
        assert isinstance(status, MonitoringUpdate)
        assert isinstance(ui_state, dict)
        assert isinstance(page_progress, PageProgress)

    def test_monitor_delegates_status_methods_correctly(self):
        """Test that the main monitor correctly delegates to status handler."""
        # Test a few key methods to ensure delegation is working
        monitor_status = self.monitor.get_status()
        status_handler_status = self.status_handler.get_status()
        
        assert monitor_status.session_id == status_handler_status.session_id
        
        monitor_ui_state = self.monitor.get_ui_state()
        status_handler_ui_state = self.status_handler.get_ui_state()
        
        assert monitor_ui_state == status_handler_ui_state


class TestProgressMonitorStatusIntegration:
    """Integration tests for ProgressMonitorStatus with AdvancedProgressMonitor."""

    def test_status_handler_maintains_consistency_with_monitor(self):
        """Test that status handler maintains consistency with monitor state."""
        monitor = AdvancedProgressMonitor()
        session_id = monitor.start_monitoring_session(["https://test.com"])
        
        # Update monitor state
        monitor.enable_multipage_monitoring()
        
        # Check that status handler reflects the changes
        config = monitor.status.get_multi_page_config()
        assert config["enabled"] is True
        
        # Check that both direct and delegated calls return same result
        direct_status = monitor.status.get_current_status()
        delegated_status = monitor.get_status()
        
        assert direct_status.session_id == delegated_status.session_id
        assert direct_status.urls_total == delegated_status.urls_total

    def test_status_handler_preserves_monitor_reference(self):
        """Test that status handler maintains proper reference to monitor."""
        monitor = AdvancedProgressMonitor()
        
        assert monitor.status.monitor is monitor
        assert id(monitor.status.monitor) == id(monitor)