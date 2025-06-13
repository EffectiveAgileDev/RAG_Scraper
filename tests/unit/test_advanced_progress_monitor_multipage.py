"""
Unit tests for Advanced Progress Monitor multi-page functionality.
Following TDD Red-Green-Refactor methodology for the failing BDD scenario.
"""
import pytest
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# These imports will fail initially (RED phase)
try:
    from src.scraper.advanced_progress_monitor import (
        AdvancedProgressMonitor, 
        PageProgress,
        OperationType
    )
except ImportError:
    # Expected in RED phase
    AdvancedProgressMonitor = Mock
    PageProgress = Mock
    OperationType = Mock


class TestAdvancedProgressMonitorMultiPage(unittest.TestCase):
    """Unit tests for multi-page progress monitoring functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = AdvancedProgressMonitor()
    
    def test_enable_multipage_monitoring_sets_session_flag(self):
        """
        RED TEST: Test that enabling multi-page monitoring sets the session flag.
        This should fail initially.
        """
        # Arrange: Create a monitoring session
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        
        # Act: Enable multi-page monitoring
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        
        # Assert: Session should have multipage_enabled flag set to True
        session = self.monitor.sessions[session_id]
        self.assertTrue(session.get("multipage_enabled", False), 
                       "Multi-page monitoring should be enabled in session")
    
    def test_enable_multipage_monitoring_initializes_page_progress(self):
        """
        RED TEST: Test that enabling multi-page monitoring initializes page progress data.
        This should fail initially.
        """
        # Arrange: Create a monitoring session
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        
        # Act: Enable multi-page monitoring
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        
        # Assert: Session should have page_progress data structure
        session = self.monitor.sessions[session_id]
        self.assertIn("page_progress", session, "Session should contain page progress data")
        
        page_progress = session["page_progress"]
        self.assertEqual(page_progress["current_page"], 1, "Should start at page 1")
        self.assertEqual(page_progress["total_pages"], 4, "Should set total pages to 4")
        self.assertIsInstance(page_progress["page_urls"], list, "Should initialize page URLs list")
        self.assertIsInstance(page_progress["completed_pages"], list, "Should initialize completed pages list")
        self.assertIsInstance(page_progress["failed_pages"], list, "Should initialize failed pages list")
    
    def test_get_page_progress_returns_correct_total_pages_when_multipage_enabled(self):
        """
        RED TEST: Test that get_page_progress returns 4 total pages when multi-page is enabled.
        This is the core failing assertion from the BDD test.
        """
        # Arrange: Create session and enable multi-page monitoring
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        
        # Act: Get page progress
        page_progress = self.monitor.get_page_progress()
        
        # Assert: Should return 4 total pages as configured
        self.assertEqual(page_progress.total_pages, 4, 
                        "Multi-page site should report 4 total pages")
        self.assertEqual(page_progress.current_page, 1, 
                        "Should start at page 1")
    
    def test_get_page_progress_returns_one_page_when_multipage_disabled(self):
        """
        RED TEST: Test that get_page_progress returns 1 page when multi-page is NOT enabled.
        This ensures the logic correctly distinguishes between single and multi-page sites.
        """
        # Arrange: Create session WITHOUT enabling multi-page monitoring
        session_id = self.monitor.start_monitoring_session(["https://single-page-restaurant.com"])
        
        # Act: Get page progress (without enabling multi-page)
        page_progress = self.monitor.get_page_progress()
        
        # Assert: Should return 1 total page for single-page sites
        self.assertEqual(page_progress.total_pages, 1, 
                        "Single-page site should report 1 total page")
        self.assertEqual(page_progress.current_page, 1, 
                        "Should start at page 1")
    
    def test_update_page_progress_updates_current_page_number(self):
        """
        RED TEST: Test that updating page progress changes the current page number.
        """
        # Arrange: Create session and enable multi-page monitoring
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        
        # Act: Update to page 2
        self.monitor.update_page_progress("https://multi-page-restaurant.com/menu", 2, 4)
        
        # Assert: Current page should be updated
        page_progress = self.monitor.get_page_progress()
        self.assertEqual(page_progress.current_page, 2, "Should update to page 2")
        self.assertEqual(page_progress.total_pages, 4, "Total pages should remain 4")
        self.assertEqual(page_progress.current_url, "https://multi-page-restaurant.com/menu", 
                        "Should update current URL")
    
    def test_page_notifications_generated_on_page_start(self):
        """
        RED TEST: Test that page notifications are generated when starting new pages.
        """
        # Arrange: Create session and enable multi-page monitoring
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        
        # Act: Start page 2
        self.monitor.update_page_progress("https://multi-page-restaurant.com/menu", 2, 4)
        
        # Assert: Should generate page start notification
        notifications = self.monitor.get_page_notifications()
        self.assertGreater(len(notifications), 0, "Should have page notifications")
        
        # Check for "Starting page" notifications
        start_notifications = [n for n in notifications if "Starting page" in n["message"]]
        self.assertGreater(len(start_notifications), 0, "Should have page start notifications")
    
    def test_get_current_progress_message_shows_page_format(self):
        """
        RED TEST: Test that progress message shows "Processing page X of Y" format.
        """
        # Arrange: Create session and enable multi-page monitoring
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        self.monitor.update_page_progress("https://multi-page-restaurant.com/menu", 2, 4)
        
        # Act: Get progress message
        progress_message = self.monitor.get_current_progress_message()
        
        # Assert: Should show "Processing page 2 of 4" format
        self.assertIn("page", progress_message.lower(), "Should mention 'page'")
        self.assertIn("2", progress_message, "Should show current page number")
        self.assertIn("4", progress_message, "Should show total page count")
        self.assertIn("of", progress_message, "Should show 'X of Y' format")
    
    def test_page_completion_events_generated(self):
        """
        RED TEST: Test that page completion events are generated.
        """
        # Arrange: Create session and enable multi-page monitoring
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        
        # Act: Complete page 1
        self.monitor.add_completion_event("page_completed", "https://multi-page-restaurant.com", 
                                         {"page_number": 1, "total_pages": 4})
        
        # Assert: Should have page completion event
        completion_events = self.monitor.get_completion_events()
        page_completions = [e for e in completion_events if e["event_type"] == "page_completed"]
        self.assertGreater(len(page_completions), 0, "Should have page completion events")
        
        # Check event details
        event = page_completions[0]
        self.assertEqual(event["event_type"], "page_completed")
        self.assertEqual(event["url"], "https://multi-page-restaurant.com")
        self.assertEqual(event["details"]["page_number"], 1)
        self.assertEqual(event["details"]["total_pages"], 4)
    
    def test_session_persistence_across_multipage_operations(self):
        """
        RED TEST: Test that session data persists correctly during multi-page operations.
        This tests the core issue from the BDD failure - session consistency.
        """
        # Arrange: Create session and enable multi-page monitoring
        session_id = self.monitor.start_monitoring_session(["https://multi-page-restaurant.com"])
        original_session_id = self.monitor.active_session_id
        
        self.monitor.enable_multipage_monitoring(page_tracking=True, page_notifications=True)
        
        # Act: Perform multiple page operations
        self.monitor.update_page_progress("https://multi-page-restaurant.com/menu", 2, 4)
        self.monitor.update_page_progress("https://multi-page-restaurant.com/about", 3, 4)
        
        # Assert: Session should remain consistent
        self.assertEqual(self.monitor.active_session_id, original_session_id, 
                        "Active session ID should not change during multi-page operations")
        
        # Verify session data integrity
        session = self.monitor.sessions[self.monitor.active_session_id]
        self.assertTrue(session.get("multipage_enabled", False), 
                       "Multi-page flag should remain enabled")
        self.assertIn("page_progress", session, 
                     "Page progress data should remain in session")
        
        # Verify page progress works correctly
        page_progress = self.monitor.get_page_progress()
        self.assertEqual(page_progress.total_pages, 4, 
                        "Should still report 4 total pages after operations")
        self.assertEqual(page_progress.current_page, 3, 
                        "Should reflect latest page update")


if __name__ == '__main__':
    unittest.main()