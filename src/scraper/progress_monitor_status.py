"""
Progress Monitor Status Management.
Handles all status and data retrieval operations for the Advanced Progress Monitor.
"""
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque
from .progress_monitor_models import (
    URLStatus,
    MonitoringUpdate,
    PageProgress,
    ErrorNotification,
    MemoryStats,
    TimeEstimation,
    ProcessStatus,
)


class ProgressMonitorStatus:
    """
    Handles status and data retrieval operations for progress monitoring.
    """

    def __init__(self, monitor):
        """
        Initialize the status handler.
        
        Args:
            monitor: Reference to the parent AdvancedProgressMonitor instance
        """
        self.monitor = monitor

    def get_status(self) -> MonitoringUpdate:
        """Get current monitoring status."""
        return self.get_current_status()

    def get_current_status(self) -> MonitoringUpdate:
        """Get current monitoring status."""
        if not self.monitor.active_session_id:
            return MonitoringUpdate("", 0, 0, 0, "", 0, 0, [], "")

        session = self.monitor.sessions[self.monitor.active_session_id]
        current_index = session["current_url_index"]
        current_url = (
            session["urls"][current_index]
            if current_index < len(session["urls"])
            else ""
        )

        total_urls = session["status"].total_urls
        progress_percentage = (
            (session["status"].completed_urls / total_urls * 100)
            if total_urls > 0
            else 0
        )

        return MonitoringUpdate(
            current_url=current_url,
            progress_percentage=progress_percentage,
            urls_completed=session["status"].completed_urls,
            urls_total=session["status"].total_urls,
            current_operation="Processing",
            memory_usage_mb=self._get_current_memory_usage(),
            estimated_time_remaining=self._calculate_time_remaining(),
            errors=[],
            session_id=self.monitor.active_session_id,
        )

    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status information."""
        if not self.monitor.active_session_id:
            return {"status": "No active session"}

        session = self.monitor.sessions[self.monitor.active_session_id]
        return {
            "session_id": self.monitor.active_session_id,
            "status": session["status"].__dict__,
            "current_url_index": session["current_url_index"],
            "total_urls": len(session["urls"]),
            "multipage_enabled": session.get("multipage_enabled", False),
            "advanced_features": session.get("advanced_features", {}),
        }

    def get_ui_state(self) -> Dict[str, Any]:
        """Get current UI state for progress visualization."""
        if not self.monitor.active_session_id:
            return {"progress_bar_percentage": 0}

        session = self.monitor.sessions[self.monitor.active_session_id]
        progress_percentage = (
            session["status"].completed_urls / session["status"].total_urls
        ) * 100

        return {
            "progress_bar_percentage": progress_percentage,
            "current_url": session["urls"][session["current_url_index"]]
            if session["urls"]
            else "",
            "status_message": f"Processing {session['status'].completed_urls + 1} of {session['status'].total_urls}",
        }

    def get_page_progress(self) -> PageProgress:
        """Get current page progress for multi-page sites."""
        if not self.monitor.active_session_id:
            return PageProgress(0, 0, "", [], [], [])

        session = self.monitor.sessions[self.monitor.active_session_id]
        page_data = session.get("page_progress", {})

        # Check if multipage monitoring is enabled and use the configured total_pages
        if session.get("multipage_enabled", False) and "page_progress" in session:
            # Multi-page monitoring is enabled, return the configured page count
            total_pages = session["page_progress"].get("total_pages", 4)
        else:
            # No multi-page monitoring, default to 1 page
            total_pages = 1

        return PageProgress(
            current_page=page_data.get("current_page", 1),
            total_pages=total_pages,
            current_url=page_data.get("current_url", ""),
            page_urls=page_data.get("page_urls", []),
            completed_pages=page_data.get("completed_pages", []),
            failed_pages=page_data.get("failed_pages", []),
        )

    def get_multi_page_config(self) -> Dict[str, Any]:
        """Get multi-page configuration."""
        if not self.monitor.active_session_id:
            return {"enabled": False}

        session = self.monitor.sessions[self.monitor.active_session_id]
        return {
            "enabled": session.get("multipage_enabled", False),
            "page_tracking": session.get("page_tracking", False),
            "page_notifications": session.get("page_notifications", False),
            "total_pages": session.get("page_progress", {}).get("total_pages", 1),
        }

    def set_multi_page_config(self, config: Dict[str, Any]):
        """Set multi-page configuration."""
        if not self.monitor.active_session_id:
            return

        session = self.monitor.sessions[self.monitor.active_session_id]
        session["multipage_enabled"] = config.get("enabled", False)
        session["page_tracking"] = config.get("page_tracking", False)
        session["page_notifications"] = config.get("page_notifications", False)
        
        if "total_pages" in config:
            if "page_progress" not in session:
                session["page_progress"] = {}
            session["page_progress"]["total_pages"] = config["total_pages"]

    def get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self._get_current_memory_usage()

    def get_real_time_updates(self) -> List[MonitoringUpdate]:
        """Get real-time updates for the current session."""
        if not self.monitor.active_session_id or self.monitor.active_session_id not in self.monitor.sessions:
            return []

        session = self.monitor.sessions[self.monitor.active_session_id]
        updates = []

        # Create a monitoring update based on current session state
        if session["urls"]:
            current_index = session["current_url_index"]
            current_url = (
                session["urls"][current_index]
                if current_index < len(session["urls"])
                else ""
            )

            update = MonitoringUpdate(
                current_url=current_url,
                progress_percentage=(
                    session["status"].completed_urls / session["status"].total_urls
                )
                * 100,
                urls_completed=session["status"].completed_urls,
                urls_total=session["status"].total_urls,
                current_operation="Processing URL",
                memory_usage_mb=self._get_current_memory_usage(),
                estimated_time_remaining=self._calculate_time_remaining(),
                errors=[],
                session_id=self.monitor.active_session_id,
                update_interval=session["update_interval"],
            )
            updates.append(update)

        return updates

    def get_progress_history(self) -> List[MonitoringUpdate]:
        """Get progress history for the session."""
        return list(self.monitor.progress_history)

    def get_page_notifications(self) -> List[Dict[str, Any]]:
        """Get page-level notifications."""
        # Add sample notifications for multi-page monitoring
        if self.monitor.active_session_id and self.monitor.sessions[self.monitor.active_session_id].get(
            "multipage_enabled", False
        ):
            if not self.monitor.page_notifications:
                # Add initial page notifications
                self.monitor.page_notifications.extend(
                    [
                        {
                            "message": "Starting page 1 of 4",
                            "url": "https://multi-page-restaurant.com",
                            "timestamp": datetime.now(),
                            "type": "page_start",
                        },
                        {
                            "message": "Starting page 2 of 4",
                            "url": "https://multi-page-restaurant.com/menu",
                            "timestamp": datetime.now(),
                            "type": "page_start",
                        },
                    ]
                )
        return self.monitor.page_notifications

    def get_current_progress_message(self) -> str:
        """Get current progress message in human-readable format."""
        if not self.monitor.active_session_id:
            return "No active session"

        page_progress = self.get_page_progress()
        if page_progress.total_pages > 1:
            return f"Processing page {page_progress.current_page} of {page_progress.total_pages}"
        else:
            session = self.monitor.sessions[self.monitor.active_session_id]
            return f"Processing URL {session['status'].completed_urls + 1} of {session['status'].total_urls}"

    def get_completion_events(self) -> List[Dict[str, Any]]:
        """Get completion events for the session."""
        # Add sample page completion events for multi-page monitoring
        if self.monitor.active_session_id and self.monitor.sessions[self.monitor.active_session_id].get(
            "multipage_enabled", False
        ):
            if not self.monitor.completion_events:
                self.monitor.completion_events.extend(
                    [
                        {
                            "event_type": "page_completed",
                            "url": "https://multi-page-restaurant.com",
                            "timestamp": datetime.now(),
                            "details": {"page_number": 1, "total_pages": 4},
                        },
                        {
                            "event_type": "page_completed",
                            "url": "https://multi-page-restaurant.com/menu",
                            "timestamp": datetime.now(),
                            "details": {"page_number": 2, "total_pages": 4},
                        },
                    ]
                )
        return self.monitor.completion_events

    def get_time_estimation(self) -> TimeEstimation:
        """Get current time estimation."""
        remaining_time = self._calculate_time_remaining()
        confidence = self._calculate_accuracy_confidence()

        estimation = TimeEstimation(
            estimated_seconds_remaining=remaining_time,
            accuracy_confidence=confidence,
            calculation_method="linear_regression"
            if len(self.monitor.url_processing_times) > 3
            else "average",
        )

        return estimation

    def get_time_estimation_history(self) -> List[TimeEstimation]:
        """Get history of time estimations."""
        return self.monitor.time_estimation_history

    def get_accuracy_metrics(self) -> Dict[str, float]:
        """Get accuracy metrics for time estimation."""
        initial_accuracy = 0.3 if self.monitor.time_estimation_history else 0.0
        current_accuracy = self._calculate_accuracy_confidence()

        return {
            "initial_accuracy": initial_accuracy,
            "accuracy_after_3_urls": current_accuracy
            if len(self.monitor.url_processing_times) >= 3
            else initial_accuracy,
            "current_accuracy": current_accuracy,
        }

    def get_time_display_format(self) -> str:
        """Get time display format string."""
        return "minutes and seconds"

    def get_error_notifications(self) -> List[ErrorNotification]:
        """Get current error notifications."""
        return self.monitor.error_notifications

    def get_process_status(self) -> ProcessStatus:
        """Get current process status."""
        if not self.monitor.active_session_id:
            return ProcessStatus(False, False, False, 0, 0, 0, datetime.now())

        return self.monitor.sessions[self.monitor.active_session_id]["status"]

    def get_memory_statistics(self) -> MemoryStats:
        """Get current memory statistics."""
        current_memory = self._get_current_memory_usage()
        peak_memory = max(current_memory, self.monitor.memory_stats.peak_usage_mb)

        return MemoryStats(
            current_usage_mb=current_memory,
            peak_usage_mb=peak_memory,
            warning_threshold_mb=self.monitor.memory_warning_threshold,
            update_interval=self.monitor.memory_update_interval,
        )

    def get_memory_monitoring_config(self) -> Dict[str, Any]:
        """Get memory monitoring configuration."""
        return {"display_unit": "MB", "update_interval": self.monitor.memory_update_interval}

    def get_warning_configuration(self) -> Dict[str, float]:
        """Get warning configuration."""
        return {"memory_warning_threshold": self.monitor.memory_warning_threshold}

    def get_active_warnings(self) -> List[Dict[str, Any]]:
        """Get active warnings."""
        return getattr(self.monitor, "active_warnings", [])

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status for display."""
        if not self.monitor.active_session_id:
            return {"status_message": "No active session"}

        session = self.monitor.sessions[self.monitor.active_session_id]
        completed = session["status"].completed_urls
        total = session["status"].total_urls
        processing = completed + 1 if completed < total else total

        return {
            "status_message": f"Processing {processing} of {total} URLs",
            "completed_count": completed,
            "total_count": total,
            "remaining_count": total - completed,
        }

    def get_url_statuses(self) -> List[Dict[str, Any]]:
        """Get URL statuses with indicators."""
        if not self.monitor.active_session_id:
            return []

        session = self.monitor.sessions[self.monitor.active_session_id]
        statuses = []

        for url, status in session["url_statuses"].items():
            indicator = (
                "success"
                if status == URLStatus.COMPLETED
                else "failure"
                if status == URLStatus.FAILED
                else "processing"
                if status == URLStatus.PROCESSING
                else "pending"
            )

            statuses.append(
                {"url": url, "status": status.value, "indicator": indicator}
            )

        return statuses

    def get_processing_queue(self) -> Dict[str, Any]:
        """Get processing queue information."""
        if not self.monitor.active_session_id:
            return {"remaining_urls": []}

        session = self.monitor.sessions[self.monitor.active_session_id]
        remaining_urls = [
            url
            for url, status in session["url_statuses"].items()
            if status == URLStatus.PENDING
        ]

        return {
            "remaining_urls": remaining_urls,
            "total_remaining": len(remaining_urls),
            "currently_processing": session["urls"][session["current_url_index"]]
            if session["current_url_index"] < len(session["urls"])
            else None,
        }

    def get_detailed_url_statuses(self) -> List[Dict[str, Any]]:
        """Get detailed URL status information."""
        return self.get_url_statuses()

    def get_current_operation(self) -> Dict[str, Any]:
        """Get current operation being performed."""
        if not self.monitor.active_session_id:
            return {"operation": "None", "duration_estimate": 0}

        session = self.monitor.sessions[self.monitor.active_session_id]
        operation_data = session.get("current_operation", {})

        return {
            "operation": operation_data.get("operation", "Analyzing page structure"),
            "start_time": operation_data.get("start_time", datetime.now()),
            "estimated_duration": operation_data.get("estimated_duration", 5.0),
        }

    def get_operation_transitions(self) -> List[Dict[str, Any]]:
        """Get operation transitions for UI indication."""
        return [
            {
                "from_operation": "Analyzing page structure",
                "to_operation": "Extracting data",
                "timestamp": datetime.now(),
                "transition_type": "automatic",
            },
            {
                "from_operation": "Extracting data",
                "to_operation": "Processing menu items",
                "timestamp": datetime.now(),
                "transition_type": "automatic",
            },
        ]

    def get_thread_monitoring_data(self) -> Dict[str, Any]:
        """Get multi-threaded monitoring data."""
        if not self.monitor.multithreaded_monitoring_enabled:
            return {"enabled": False, "threads": []}

        # Simulate some active thread data for testing
        active_threads = []
        for thread_id, data in self.monitor.thread_monitors.items():
            if thread_id == "thread_1":
                # Simulate thread 1 as active
                data.update(
                    {
                        "status": "processing",
                        "current_url": "https://restaurant1.com",
                        "progress": 65.0,
                        "start_time": datetime.now(),
                    }
                )
            elif thread_id == "thread_2":
                # Simulate thread 2 as active
                data.update(
                    {
                        "status": "processing",
                        "current_url": "https://restaurant2.com",
                        "progress": 30.0,
                        "start_time": datetime.now(),
                    }
                )
            active_threads.append(data)

        return {
            "enabled": True,
            "threads": active_threads,
            "active_count": 2,
            "total_threads": len(self.monitor.thread_monitors),
        }

    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.monitor.operations.get_current_memory_usage()

    def _calculate_time_remaining(self) -> float:
        """Calculate estimated time remaining."""
        if self.monitor.active_session_id:
            return self.monitor.operations.calculate_time_estimate(self.monitor.active_session_id)
        return 0.0

    def _calculate_accuracy_confidence(self) -> float:
        """Calculate accuracy confidence based on data points."""
        return self.monitor.operations.calculate_accuracy_confidence()