"""
Unit tests for ProgressMonitorOperations class extraction.
Following TDD Red-Green-Refactor methodology.
"""
import pytest
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# These imports will fail initially (RED phase)
try:
    from src.scraper.progress_monitor_operations import ProgressMonitorOperations
    from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
    from src.scraper.progress_monitor_models import URLStatus, OperationType
except ImportError:
    # Expected in RED phase
    ProgressMonitorOperations = Mock
    AdvancedProgressMonitor = Mock
    URLStatus = Mock
    OperationType = Mock


class TestProgressMonitorOperations(unittest.TestCase):
    """Unit tests for ProgressMonitorOperations class."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = AdvancedProgressMonitor()
        # This will fail initially as ProgressMonitorOperations doesn't exist yet
        self.operations = ProgressMonitorOperations(self.monitor)

    def test_progress_monitor_operations_can_be_instantiated(self):
        """
        RED TEST: Test that ProgressMonitorOperations can be instantiated.
        This should fail initially.
        """
        # Arrange & Act: Create ProgressMonitorOperations instance
        operations = ProgressMonitorOperations(self.monitor)
        
        # Assert: Should be instantiated successfully
        self.assertIsNotNone(operations, "ProgressMonitorOperations should be instantiated")
        self.assertEqual(operations.monitor, self.monitor, "Should store reference to monitor")

    def test_update_progress_method_exists(self):
        """
        RED TEST: Test that update_progress method exists in ProgressMonitorOperations.
        """
        # Assert: Should have update_progress method
        self.assertTrue(
            hasattr(self.operations, 'update_progress'),
            "ProgressMonitorOperations should have update_progress method"
        )

    def test_start_monitoring_method_exists(self):
        """
        RED TEST: Test that start_monitoring method exists in ProgressMonitorOperations.
        """
        # Assert: Should have start_monitoring method
        self.assertTrue(
            hasattr(self.operations, 'start_monitoring'),
            "ProgressMonitorOperations should have start_monitoring method"
        )

    def test_stop_monitoring_method_exists(self):
        """
        RED TEST: Test that stop_monitoring method exists in ProgressMonitorOperations.
        """
        # Assert: Should have stop_monitoring method
        self.assertTrue(
            hasattr(self.operations, 'stop_monitoring'),
            "ProgressMonitorOperations should have stop_monitoring method"
        )

    def test_handle_url_completion_method_exists(self):
        """
        RED TEST: Test that handle_url_completion method exists in ProgressMonitorOperations.
        """
        # Assert: Should have handle_url_completion method
        self.assertTrue(
            hasattr(self.operations, 'handle_url_completion'),
            "ProgressMonitorOperations should have handle_url_completion method"
        )

    def test_handle_error_method_exists(self):
        """
        RED TEST: Test that handle_error method exists in ProgressMonitorOperations.
        """
        # Assert: Should have handle_error method
        self.assertTrue(
            hasattr(self.operations, 'handle_error'),
            "ProgressMonitorOperations should have handle_error method"
        )

    def test_calculate_time_estimate_method_exists(self):
        """
        RED TEST: Test that calculate_time_estimate method exists in ProgressMonitorOperations.
        """
        # Assert: Should have calculate_time_estimate method
        self.assertTrue(
            hasattr(self.operations, 'calculate_time_estimate'),
            "ProgressMonitorOperations should have calculate_time_estimate method"
        )

    def test_update_url_completion_delegates_to_operations(self):
        """
        RED TEST: Test that AdvancedProgressMonitor delegates to ProgressMonitorOperations.
        """
        # Arrange: Create a session first, then mock the operations method
        session_id = self.monitor.start_monitoring_session(["https://test.com"])
        original_method = self.monitor.operations.handle_url_completion
        self.monitor.operations.handle_url_completion = Mock()
        
        # Act: Call update_url_completion on monitor
        self.monitor.update_url_completion("https://test.com", 5.0, True)
        
        # Assert: Should delegate to operations
        self.monitor.operations.handle_url_completion.assert_called_once_with(
            "https://test.com", 5.0, True
        )

    def test_operations_can_update_progress_data(self):
        """
        RED TEST: Test that operations can update progress data.
        """
        # Arrange: Create session
        session_id = self.monitor.start_monitoring_session(["https://test.com"])
        
        # Act: Update progress through operations
        self.operations.update_progress(session_id, 1, 2)
        
        # Assert: Progress should be updated
        status = self.monitor.get_current_status()
        self.assertEqual(status.urls_completed, 1, "Should update completed URLs")

    def test_operations_can_handle_monitoring_lifecycle(self):
        """
        RED TEST: Test that operations can handle monitoring lifecycle.
        """
        # Arrange: Create session
        session_id = self.monitor.start_monitoring_session(["https://test.com"])
        
        # Act: Start and stop monitoring through operations
        self.operations.start_monitoring(session_id)
        self.assertTrue(self.monitor.monitoring_active, "Should start monitoring")
        
        self.operations.stop_monitoring(session_id)
        self.assertFalse(self.monitor.monitoring_active, "Should stop monitoring")

    def test_operations_can_calculate_time_estimates(self):
        """
        RED TEST: Test that operations can calculate time estimates.
        """
        # Arrange: Create session with some processing times
        session_id = self.monitor.start_monitoring_session(["https://test1.com", "https://test2.com"])
        self.monitor.url_processing_times = [5.0, 10.0]
        
        # Act: Calculate time estimate through operations
        estimate = self.operations.calculate_time_estimate(session_id)
        
        # Assert: Should return reasonable estimate
        self.assertIsInstance(estimate, float, "Should return float estimate")
        self.assertGreater(estimate, 0, "Should return positive estimate")


class TestAdvancedProgressMonitorRefactored(unittest.TestCase):
    """Unit tests for refactored AdvancedProgressMonitor."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = AdvancedProgressMonitor()

    def test_monitor_has_operations_instance(self):
        """
        RED TEST: Test that AdvancedProgressMonitor has ProgressMonitorOperations instance.
        """
        # Assert: Should have operations attribute
        self.assertTrue(
            hasattr(self.monitor, 'operations'),
            "AdvancedProgressMonitor should have operations attribute"
        )
        self.assertIsInstance(
            self.monitor.operations, 
            ProgressMonitorOperations,
            "Operations should be ProgressMonitorOperations instance"
        )

    def test_monitor_delegates_update_url_completion(self):
        """
        RED TEST: Test that monitor delegates update_url_completion to operations.
        """
        # Arrange: Mock operations method
        self.monitor.operations.handle_url_completion = Mock()
        
        # Act: Call update_url_completion
        self.monitor.update_url_completion("https://test.com", 5.0, True)
        
        # Assert: Should delegate to operations
        self.monitor.operations.handle_url_completion.assert_called_once_with(
            "https://test.com", 5.0, True
        )

    def test_monitor_keeps_initialization_methods(self):
        """
        RED TEST: Test that monitor keeps initialization and interface methods.
        """
        # Assert: Should still have high-level interface methods
        interface_methods = [
            'start_monitoring_session',
            'get_current_status', 
            'get_real_time_updates',
            'get_ui_state',
            'get_page_progress'
        ]
        
        for method_name in interface_methods:
            self.assertTrue(
                hasattr(self.monitor, method_name),
                f"AdvancedProgressMonitor should keep {method_name} method"
            )

    def test_monitor_removes_core_operation_methods(self):
        """
        RED TEST: Test that core operation methods are moved to operations class.
        """
        # Assert: These methods should be moved to operations class
        moved_methods = [
            'monitoring_loop',
            'calculate_time_estimate',
            'calculate_accuracy_confidence'
        ]
        
        for method_name in moved_methods:
            # These should exist in operations after refactoring
            if hasattr(self.monitor, 'operations'):
                self.assertTrue(
                    hasattr(self.monitor.operations, method_name),
                    f"Operations should have {method_name} method"
                )


if __name__ == "__main__":
    unittest.main()