"""
Error Handler for Advanced Progress Monitor.
Provides error management and user interaction capabilities for the scraping process.
"""
from typing import List, TYPE_CHECKING
from .progress_monitor_models import URLStatus

if TYPE_CHECKING:
    from .advanced_progress_monitor import AdvancedProgressMonitor


class ErrorHandler:
    """Handler for error management and user interaction."""

    def __init__(self, monitor: "AdvancedProgressMonitor"):
        self.monitor = monitor
        self.available_actions = ["continue", "stop"]
        self.remaining_urls_count = 0

    def get_available_actions(self) -> List[str]:
        """Get available error handling actions."""
        return self.available_actions

    def handle_error_action(self, action: str):
        """Handle user's error action choice."""
        if action == "stop":
            self.monitor.stop_monitoring()
        elif action == "continue":
            # Continue processing - update remaining count
            if self.monitor.active_session_id:
                session = self.monitor.sessions[self.monitor.active_session_id]
                pending_urls = [
                    url
                    for url, status in session["url_statuses"].items()
                    if status == URLStatus.PENDING
                ]
                self.remaining_urls_count = len(pending_urls)

    def get_remaining_urls_count(self) -> int:
        """Get count of remaining URLs to process."""
        return self.remaining_urls_count