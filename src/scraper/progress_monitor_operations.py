"""
Progress Monitor Operations - Core monitoring operation methods.
Extracted from AdvancedProgressMonitor to separate concerns and improve maintainability.
"""
import time
import threading
import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from collections import deque
from .progress_monitor_models import (
    OperationType,
    URLStatus,
    MonitoringUpdate,
    TimeEstimation,
    ErrorNotification,
)


class ProgressMonitorOperations:
    """
    Core monitoring operations class containing the operational methods
    extracted from AdvancedProgressMonitor.
    """

    def __init__(self, monitor):
        """Initialize operations with reference to the main monitor."""
        self.monitor = monitor
        
    def update_progress(self, session_id: str, completed_urls: int, total_urls: int):
        """Update progress data for a session."""
        if session_id not in self.monitor.sessions:
            return
            
        session = self.monitor.sessions[session_id]
        with self.monitor.lock:
            session["status"].completed_urls = completed_urls
            session["status"].total_urls = total_urls

    def start_monitoring(self, session_id: str):
        """Start monitoring thread for a session."""
        if session_id not in self.monitor.sessions:
            return
            
        self.monitor.monitoring_active = True
        self.monitor.monitoring_thread = threading.Thread(
            target=self.monitoring_loop, args=(session_id,), daemon=True
        )
        self.monitor.monitoring_thread.start()

    def stop_monitoring(self, session_id: str):
        """Stop monitoring for a session."""
        self.monitor.monitoring_active = False
        if self.monitor.monitoring_thread:
            self.monitor.monitoring_thread.join(timeout=5.0)

        if session_id in self.monitor.sessions:
            session = self.monitor.sessions[session_id]
            session["status"].is_running = False
            session["status"].is_stopped = True

    def handle_url_completion(self, url: str, processing_time: float, success: bool = True):
        """Handle URL completion and update statistics."""
        if not self.monitor.active_session_id:
            return

        session = self.monitor.sessions[self.monitor.active_session_id]

        with self.monitor.lock:
            if success:
                session["status"].completed_urls += 1
                session["url_statuses"][url] = URLStatus.COMPLETED
            else:
                session["status"].failed_urls += 1
                session["url_statuses"][url] = URLStatus.FAILED

            self.monitor.url_processing_times.append(processing_time)

            # Move to next URL
            session["current_url_index"] += 1

            # Create progress update and add to history
            progress_update = self.monitor.get_current_status()
            self.monitor.progress_history.append(progress_update)

    def handle_error(self, url: str, error_type: str, error_message: str):
        """Handle error notification and processing."""
        notification = ErrorNotification(
            url=url,
            error_type=error_type,
            error_message=error_message,
            timestamp=datetime.now(),
        )
        self.monitor.error_notifications.append(notification)

    def calculate_time_estimate(self, session_id: str) -> float:
        """Calculate estimated time remaining for a session."""
        if session_id not in self.monitor.sessions or not self.monitor.url_processing_times:
            return 0.0

        session = self.monitor.sessions[session_id]
        remaining_urls = session["status"].total_urls - session["status"].completed_urls

        if remaining_urls <= 0:
            return 0.0

        # Calculate average processing time
        avg_time = sum(self.monitor.url_processing_times) / len(self.monitor.url_processing_times)
        return remaining_urls * avg_time

    def monitoring_loop(self, session_id: str):
        """Main monitoring loop for real-time updates."""
        while self.monitor.monitoring_active and session_id in self.monitor.sessions:
            session = self.monitor.sessions[session_id]
            update_interval = session["update_interval"]

            # Create monitoring update
            update = self.monitor.get_current_status()

            # Add to progress history
            with self.monitor.lock:
                self.monitor.progress_history.append(update)

            # Update time estimation
            if len(self.monitor.url_processing_times) > 0:
                estimation = self.monitor.get_time_estimation()
                self.monitor.time_estimation_history.append(estimation)

            # Sleep for update interval
            time.sleep(update_interval)

    def calculate_accuracy_confidence(self) -> float:
        """Calculate accuracy confidence based on data points."""
        data_points = len(self.monitor.url_processing_times)
        if data_points == 0:
            return 0.1
        elif data_points < 3:
            return 0.3
        elif data_points < 5:
            return 0.6
        else:
            return 0.8

    def get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            memory_info = self.monitor.process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert bytes to MB
        except:
            return 0.0

    def update_page_progress_data(self, url: str, current_page: int, total_pages: int):
        """Update progress data for multi-page website."""
        if not self.monitor.active_session_id:
            return

        session = self.monitor.sessions[self.monitor.active_session_id]
        if "page_progress" not in session:
            session["page_progress"] = {}

        session["page_progress"].update(
            {
                "current_page": current_page,
                "total_pages": total_pages,
                "current_url": url,
            }
        )

        # Add page notification
        notification = {
            "message": f"Starting page {current_page} of {total_pages}",
            "url": url,
            "timestamp": datetime.now(),
            "type": "page_start",
        }
        self.monitor.page_notifications.append(notification)

    def add_completion_event_data(
        self, event_type: str, url: str, details: Dict[str, Any] = None
    ):
        """Add a completion event to the monitor data."""
        event = {
            "event_type": event_type,
            "url": url,
            "timestamp": datetime.now(),
            "details": details or {},
        }
        self.monitor.completion_events.append(event)

    def simulate_memory_usage_change(self, usage_mb: float):
        """Simulate memory usage change for testing and monitoring."""
        self.monitor.memory_stats.current_usage_mb = usage_mb
        # Update peak memory as well
        if usage_mb > self.monitor.memory_stats.peak_usage_mb:
            self.monitor.memory_stats.peak_usage_mb = usage_mb

        if usage_mb > self.monitor.memory_warning_threshold:
            warning = {
                "warning_type": "high_memory_usage",
                "message": f"Memory usage ({usage_mb:.1f} MB) exceeds threshold ({self.monitor.memory_warning_threshold} MB)",
                "timestamp": datetime.now(),
            }
            if not hasattr(self.monitor, "active_warnings"):
                self.monitor.active_warnings = []
            self.monitor.active_warnings.append(warning)

    def set_current_operation_data(self, operation: OperationType):
        """Set the current operation being performed."""
        if self.monitor.active_session_id:
            session = self.monitor.sessions[self.monitor.active_session_id]
            session["current_operation"] = {
                "operation": operation.value,
                "start_time": datetime.now(),
                "estimated_duration": self._get_operation_duration_estimate(operation),
            }

    def _get_operation_duration_estimate(self, operation: OperationType) -> float:
        """Get estimated duration for an operation in seconds."""
        duration_estimates = {
            OperationType.ANALYZING_PAGE_STRUCTURE: 3.0,
            OperationType.EXTRACTING_DATA: 5.0,
            OperationType.PROCESSING_MENU_ITEMS: 8.0,
            OperationType.HANDLING_NAVIGATION: 2.0,
            OperationType.VALIDATING_DATA: 1.0,
            OperationType.GENERATING_OUTPUT: 2.0,
        }
        return duration_estimates.get(operation, 5.0)