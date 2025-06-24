"""
Data Exporter for Advanced Progress Monitor.
Handles exporting monitoring data, session logs, and historical data for analysis.
"""
from datetime import datetime
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .advanced_progress_monitor import AdvancedProgressMonitor


class DataExporter:
    """Exporter for monitoring data and session logs."""

    def __init__(self, monitor: "AdvancedProgressMonitor"):
        self.monitor = monitor

    def export_monitoring_data_as_json(self) -> Dict[str, Any]:
        """Export monitoring data as JSON."""
        if not self.monitor.active_session_id:
            return {}

        session = self.monitor.sessions[self.monitor.active_session_id]

        export_data = {
            "session_id": self.monitor.active_session_id,
            "start_time": session["start_time"].isoformat(),
            "timing_data": {
                "url_processing_times": self.monitor.url_processing_times,
                "average_time": sum(self.monitor.url_processing_times)
                / len(self.monitor.url_processing_times)
                if self.monitor.url_processing_times
                else 0,
            },
            "memory_usage": {
                "current_mb": self.monitor.memory_stats.current_usage_mb,
                "peak_mb": self.monitor.memory_stats.peak_usage_mb,
            },
            "error_logs": [
                {
                    "url": notif.url,
                    "error_type": notif.error_type,
                    "message": notif.error_message,
                    "timestamp": notif.timestamp.isoformat(),
                }
                for notif in self.monitor.error_notifications
            ],
            "progress_history": [
                {
                    "current_url": update.current_url,
                    "progress_percentage": update.progress_percentage,
                    "timestamp": update.timestamp.isoformat(),
                }
                for update in self.monitor.progress_history
            ],
        }

        return export_data

    def get_session_logs(self) -> List[Dict[str, Any]]:
        """Get session logs for troubleshooting."""
        logs = []

        # Add progress updates as log entries
        for update in self.monitor.progress_history:
            logs.append(
                {
                    "timestamp": update.timestamp.isoformat(),
                    "level": "INFO",
                    "message": f"Processing {update.current_url} - {update.progress_percentage:.1f}% complete",
                    "data": {
                        "url": update.current_url,
                        "progress": update.progress_percentage,
                        "memory_mb": update.memory_usage_mb,
                    },
                }
            )

        # Add error notifications as log entries
        for error in self.monitor.error_notifications:
            logs.append(
                {
                    "timestamp": error.timestamp.isoformat(),
                    "level": "ERROR",
                    "message": f"Error processing {error.url}: {error.error_message}",
                    "data": {
                        "url": error.url,
                        "error_type": error.error_type,
                        "error_message": error.error_message,
                    },
                }
            )

        return sorted(logs, key=lambda x: x["timestamp"])

    def get_historical_data(self) -> Dict[str, Any]:
        """Get historical monitoring data for analysis."""
        return {
            "total_sessions": len(self.monitor.sessions),
            "session_summaries": [
                {
                    "session_id": session_id,
                    "start_time": session_data["start_time"].isoformat(),
                    "total_urls": session_data["status"].total_urls,
                    "completed_urls": session_data["status"].completed_urls,
                }
                for session_id, session_data in self.monitor.sessions.items()
            ],
        }