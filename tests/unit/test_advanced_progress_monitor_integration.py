"""
Unit tests for AdvancedProgressMonitor integration with ProgressMonitorConfig.
Following TDD Red-Green-Refactor methodology for configuration extraction refactoring.
"""
import pytest
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# These imports should work after refactoring
try:
    from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
    from src.scraper.progress_monitor_config import ProgressMonitorConfig
except ImportError:
    # Expected during refactoring
    AdvancedProgressMonitor = Mock
    ProgressMonitorConfig = Mock


class TestAdvancedProgressMonitorIntegration(unittest.TestCase):
    """Unit tests for AdvancedProgressMonitor integration with ProgressMonitorConfig."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = AdvancedProgressMonitor()

    def test_monitor_has_config_property(self):
        """
        RED TEST: Test that AdvancedProgressMonitor has a config property.
        This should fail initially.
        """
        # Assert: Monitor should have config property
        self.assertIsInstance(
            self.monitor.config,
            ProgressMonitorConfig,
            "Monitor should have ProgressMonitorConfig instance"
        )

    def test_enable_detailed_logging_delegates_to_config(self):
        """
        RED TEST: Test that enable_detailed_logging delegates to config.
        This should fail initially.
        """
        # Act: Enable detailed logging
        self.monitor.enable_detailed_logging(True)

        # Assert: Config should be updated
        self.assertTrue(
            self.monitor.config.detailed_logging_enabled,
            "Config should have detailed logging enabled"
        )

    def test_enable_memory_monitoring_delegates_to_config(self):
        """
        RED TEST: Test that enable_memory_monitoring delegates to config.
        This should fail initially.
        """
        # Act: Enable memory monitoring
        memory_config = {"update_interval": 2.0, "warning_threshold": 300.0}
        self.monitor.enable_memory_monitoring(True, memory_config)

        # Assert: Config should be updated
        self.assertTrue(
            self.monitor.config.memory_monitoring_enabled,
            "Config should have memory monitoring enabled"
        )
        self.assertEqual(
            self.monitor.config.memory_monitoring_config,
            memory_config,
            "Config should have memory monitoring config set"
        )

    def test_enable_page_notifications_delegates_to_config(self):
        """
        RED TEST: Test that enable_page_notifications delegates to config.
        This should fail initially.
        """
        # Act: Enable page notifications
        self.monitor.enable_page_notifications(True)

        # Assert: Config should be updated
        self.assertTrue(
            self.monitor.config.page_notifications_enabled,
            "Config should have page notifications enabled"
        )

    def test_enable_time_estimation_delegates_to_config(self):
        """
        RED TEST: Test that enable_time_estimation delegates to config.
        This should fail initially.
        """
        # Act: Enable time estimation
        self.monitor.enable_time_estimation(True)

        # Assert: Config should be updated
        self.assertTrue(
            self.monitor.config.time_estimation_enabled,
            "Config should have time estimation enabled"
        )

    def test_set_time_display_format_delegates_to_config(self):
        """
        RED TEST: Test that set_time_display_format delegates to config.
        This should fail initially.
        """
        # Act: Set time display format
        self.monitor.set_time_display_format("iso_8601")

        # Assert: Config should be updated
        self.assertEqual(
            self.monitor.config.time_display_format,
            "iso_8601",
            "Config should have time display format set"
        )

    def test_enable_accuracy_tracking_delegates_to_config(self):
        """
        RED TEST: Test that enable_accuracy_tracking delegates to config.
        This should fail initially.
        """
        # Act: Enable accuracy tracking
        self.monitor.enable_accuracy_tracking(True)

        # Assert: Config should be updated
        self.assertTrue(
            self.monitor.config.accuracy_tracking_enabled,
            "Config should have accuracy tracking enabled"
        )

    def test_set_memory_monitoring_config_delegates_to_config(self):
        """
        RED TEST: Test that set_memory_monitoring_config delegates to config.
        This should fail initially.
        """
        # Act: Set memory monitoring config
        config = {"update_interval": 1.5, "warning_threshold": 200.0}
        self.monitor.set_memory_monitoring_config(config)

        # Assert: Config should be updated
        self.assertEqual(
            self.monitor.config.memory_monitoring_config,
            config,
            "Config should have memory monitoring config set"
        )

    def test_set_warning_configuration_delegates_to_config(self):
        """
        RED TEST: Test that set_warning_configuration delegates to config.
        This should fail initially.
        """
        # Act: Set warning configuration
        warning_config = {"memory_threshold": 350.0, "time_threshold": 180.0}
        self.monitor.set_warning_configuration(warning_config)

        # Assert: Config should be updated
        self.assertEqual(
            self.monitor.config.warning_configuration,
            warning_config,
            "Config should have warning configuration set"
        )

    def test_enable_thread_monitoring_delegates_to_config(self):
        """
        RED TEST: Test that enable_thread_monitoring delegates to config.
        This should fail initially.
        """
        # Act: Enable thread monitoring
        self.monitor.enable_thread_monitoring(True, max_threads=8)

        # Assert: Config should be updated
        self.assertTrue(
            self.monitor.config.thread_monitoring_enabled,
            "Config should have thread monitoring enabled"
        )
        self.assertEqual(
            self.monitor.config.thread_monitoring_config["max_threads"],
            8,
            "Config should have max threads set"
        )

    def test_get_configuration_returns_config_dict(self):
        """
        RED TEST: Test that get_configuration returns config dictionary.
        This should fail initially.
        """
        # Arrange: Set some configuration
        self.monitor.enable_detailed_logging(True)
        self.monitor.enable_memory_monitoring(True)

        # Act: Get configuration
        config_dict = self.monitor.get_configuration()

        # Assert: Should return configuration dictionary
        self.assertIsInstance(config_dict, dict)
        self.assertTrue(config_dict["detailed_logging_enabled"])
        self.assertTrue(config_dict["memory_monitoring_enabled"])

    def test_apply_configuration_updates_config(self):
        """
        RED TEST: Test that apply_configuration updates config.
        This should fail initially.
        """
        # Arrange: Configuration dictionary
        config_dict = {
            "detailed_logging_enabled": True,
            "time_estimation_enabled": True,
            "time_display_format": "verbose"
        }

        # Act: Apply configuration
        self.monitor.apply_configuration(config_dict)

        # Assert: Config should be updated
        self.assertTrue(self.monitor.config.detailed_logging_enabled)
        self.assertTrue(self.monitor.config.time_estimation_enabled)
        self.assertEqual(self.monitor.config.time_display_format, "verbose")

    def test_validate_configuration_returns_validation_result(self):
        """
        RED TEST: Test that validate_configuration returns validation result.
        This should fail initially.
        """
        # Act: Validate configuration
        validation_result = self.monitor.validate_configuration()

        # Assert: Should return validation result
        self.assertIsInstance(validation_result, dict)
        self.assertIn("valid", validation_result)
        self.assertIn("errors", validation_result)

    def test_old_configuration_methods_still_work_for_backward_compatibility(self):
        """
        RED TEST: Test that existing monitor methods still work after refactoring.
        This ensures backward compatibility.
        """
        # These methods should still exist in AdvancedProgressMonitor
        # even after extracting configuration logic
        
        # Test existing monitoring methods
        urls = ["https://test.com"]
        session_id = self.monitor.start_monitoring_session(urls)
        
        # These should work
        self.monitor.enable_multipage_monitoring()
        self.monitor.enable_advanced_features(time_estimation=True)
        self.monitor.enable_error_monitoring()
        self.monitor.enable_resource_monitoring()
        
        # Assert session was created
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.monitor.sessions)


if __name__ == "__main__":
    unittest.main()