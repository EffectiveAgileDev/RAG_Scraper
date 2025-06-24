"""
Progress Monitor Updater - Update and notification methods for AdvancedProgressMonitor.
Extracted from AdvancedProgressMonitor to separate update/notification concerns from core monitoring.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from .progress_monitor_models import (
    OperationType,
    ErrorNotification,
)


class ProgressMonitorUpdater:
    """
    Handles all update and notification operations for the progress monitoring system.
    
    This class contains methods for:
    - URL completion updates
    - Page progress updates  
    - Error notifications
    - Completion event tracking
    - Operation transitions
    - Page notifications
    
    The updater works in conjunction with the main AdvancedProgressMonitor,
    ProgressMonitorOperations, and ProgressMonitorStatus classes to provide
    a complete monitoring solution.
    """

    def __init__(self, monitor):
        """
        Initialize the updater with reference to the main monitor.
        
        Args:
            monitor: Reference to the AdvancedProgressMonitor instance
        """
        self.monitor = monitor

    def update_url_completion(
        self, url: str, processing_time: float, success: bool = True
    ):
        """
        Update URL completion status and processing statistics.
        
        Args:
            url: The URL that was processed
            processing_time: Time taken to process the URL in seconds
            success: Whether the URL was processed successfully
        """
        self.monitor.operations.handle_url_completion(url, processing_time, success)

    def update_page_progress(self, url: str, current_page: int, total_pages: int):
        """
        Update progress for multi-page website processing.
        
        Args:
            url: The current URL being processed
            current_page: Current page number
            total_pages: Total number of pages to process
        """
        self.monitor.operations.update_page_progress_data(url, current_page, total_pages)

    def add_error_notification(self, url: str, error_type: str, error_message: str):
        """
        Add an error notification to the monitoring system.
        
        Args:
            url: The URL where the error occurred
            error_type: Type of error (e.g., '404', 'timeout', 'parsing_error')
            error_message: Detailed error message
        """
        self.monitor.operations.handle_error(url, error_type, error_message)

    def add_page_notification(
        self, message: str, url: str, notification_type: str = "info"
    ):
        """
        Add a page-level notification.
        
        Args:
            message: Notification message
            url: URL associated with the notification
            notification_type: Type of notification ('info', 'warning', 'error', 'success')
        """
        notification = {
            "message": message,
            "url": url,
            "timestamp": datetime.now(),
            "type": notification_type,
        }
        self.monitor.page_notifications.append(notification)

    def add_completion_event(
        self, event_type: str, url: str, details: Dict[str, Any] = None
    ):
        """
        Add a completion event to track processing milestones.
        
        Args:
            event_type: Type of completion event (e.g., 'url_completed', 'page_completed', 'batch_completed')
            url: URL associated with the event
            details: Additional event details
        """
        self.monitor.operations.add_completion_event_data(event_type, url, details)

    def update_operation_transition(self, operation: OperationType):
        """
        Update the current operation and track transition.
        
        Args:
            operation: The new operation being performed
        """
        # Add transition to operation history
        if hasattr(self.monitor, 'operation_transitions'):
            transition = {
                "from_operation": getattr(self.monitor, 'current_operation_type', None),
                "to_operation": operation.value,
                "timestamp": datetime.now(),
                "session_id": self.monitor.active_session_id,
            }
            self.monitor.operation_transitions.append(transition)
        else:
            # Initialize operation transitions if not present
            self.monitor.operation_transitions = []
            transition = {
                "from_operation": None,
                "to_operation": operation.value,
                "timestamp": datetime.now(),
                "session_id": self.monitor.active_session_id,
            }
            self.monitor.operation_transitions.append(transition)

        # Update current operation
        self.monitor.operations.set_current_operation_data(operation)
        self.monitor.current_operation_type = operation

    def add_batch_notification(
        self, message: str, batch_size: int, notification_type: str = "info"
    ):
        """
        Add a batch-level notification for batch processing operations.
        
        Args:
            message: Notification message
            batch_size: Size of the batch being processed
            notification_type: Type of notification
        """
        notification = {
            "message": message,
            "batch_size": batch_size,
            "timestamp": datetime.now(),
            "type": notification_type,
            "level": "batch",
        }
        
        # Add to page notifications (they handle both page and batch level)
        self.monitor.page_notifications.append(notification)

    def update_url_status_transition(self, url: str, from_status: str, to_status: str):
        """
        Update URL status and track the transition.
        
        Args:
            url: The URL whose status is changing
            from_status: Previous status
            to_status: New status
        """
        if not self.monitor.active_session_id:
            return

        session = self.monitor.sessions[self.monitor.active_session_id]
        
        with self.monitor.lock:
            # Update URL status
            if url in session["url_statuses"]:
                session["url_statuses"][url] = to_status
            
            # Track transition for monitoring
            transition = {
                "url": url,
                "from_status": from_status,
                "to_status": to_status,
                "timestamp": datetime.now(),
            }
            
            if "url_transitions" not in session:
                session["url_transitions"] = []
            session["url_transitions"].append(transition)

    def add_resource_warning(self, warning_type: str, message: str, threshold_value: float = None):
        """
        Add a resource-related warning notification.
        
        Args:
            warning_type: Type of resource warning (e.g., 'memory', 'cpu', 'disk')
            message: Warning message
            threshold_value: Threshold value that was exceeded (optional)
        """
        warning = {
            "warning_type": warning_type,
            "message": message,
            "threshold_value": threshold_value,
            "timestamp": datetime.now(),
            "level": "resource",
        }
        
        if not hasattr(self.monitor, "active_warnings"):
            self.monitor.active_warnings = []
        self.monitor.active_warnings.append(warning)

    def update_memory_statistics(self, current_usage: float, peak_usage: float = None):
        """
        Update memory usage statistics.
        
        Args:
            current_usage: Current memory usage in MB
            peak_usage: Peak memory usage in MB (optional)
        """
        self.monitor.memory_stats.current_usage_mb = current_usage
        
        if peak_usage is not None:
            self.monitor.memory_stats.peak_usage_mb = peak_usage
        elif current_usage > self.monitor.memory_stats.peak_usage_mb:
            self.monitor.memory_stats.peak_usage_mb = current_usage

        # Check for memory warnings
        if current_usage > self.monitor.memory_warning_threshold:
            self.add_resource_warning(
                "high_memory_usage",
                f"Memory usage ({current_usage:.1f} MB) exceeds threshold ({self.monitor.memory_warning_threshold} MB)",
                self.monitor.memory_warning_threshold
            )

    def add_thread_notification(self, thread_id: str, message: str, notification_type: str = "info"):
        """
        Add a thread-specific notification for multi-threaded operations.
        
        Args:
            thread_id: ID of the thread
            message: Notification message
            notification_type: Type of notification
        """
        notification = {
            "thread_id": thread_id,
            "message": message,
            "timestamp": datetime.now(),
            "type": notification_type,
            "level": "thread",
        }
        
        self.monitor.page_notifications.append(notification)

    def update_time_estimation(self, estimated_seconds: float, confidence: float, method: str = "calculation"):
        """
        Update time estimation with new data.
        
        Args:
            estimated_seconds: Estimated seconds remaining
            confidence: Confidence level (0.0 to 1.0)
            method: Calculation method used
        """
        from .progress_monitor_models import TimeEstimation
        
        estimation = TimeEstimation(
            estimated_seconds_remaining=estimated_seconds,
            accuracy_confidence=confidence,
            calculation_method=method
        )
        
        self.monitor.time_estimation_history.append(estimation)

    def clear_notifications(self, notification_types: List[str] = None):
        """
        Clear notifications of specified types or all notifications.
        
        Args:
            notification_types: List of notification types to clear, or None for all
        """
        if notification_types is None:
            # Clear all notifications
            self.monitor.error_notifications.clear()
            self.monitor.page_notifications.clear()
            self.monitor.completion_events.clear()
            if hasattr(self.monitor, "active_warnings"):
                self.monitor.active_warnings.clear()
        else:
            # Clear specific notification types
            if "error" in notification_types:
                self.monitor.error_notifications.clear()
            if "page" in notification_types:
                self.monitor.page_notifications.clear()
            if "completion" in notification_types:
                self.monitor.completion_events.clear()
            if "warning" in notification_types and hasattr(self.monitor, "active_warnings"):
                self.monitor.active_warnings.clear()

    def batch_update_url_completions(self, url_results: List[Dict[str, Any]]):
        """
        Batch update multiple URL completions for efficiency.
        
        Args:
            url_results: List of dictionaries with keys 'url', 'processing_time', 'success'
        """
        for result in url_results:
            self.update_url_completion(
                url=result["url"],
                processing_time=result["processing_time"],
                success=result.get("success", True)
            )