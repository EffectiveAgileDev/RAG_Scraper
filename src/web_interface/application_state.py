"""Application state management for Flask web interface."""

from typing import Optional
from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
from src.file_generator.file_generator_service import FileGeneratorService


class ApplicationState:
    """Manages application-wide state for the web interface."""
    
    def __init__(self):
        """Initialize application state."""
        self._advanced_monitor: Optional[AdvancedProgressMonitor] = None
        self._active_scraper = None
        self._file_generator_service: Optional[FileGeneratorService] = None
        self._current_progress = None
    
    @property
    def advanced_monitor(self) -> AdvancedProgressMonitor:
        """Get or create the advanced progress monitor."""
        if self._advanced_monitor is None:
            self._advanced_monitor = AdvancedProgressMonitor()
        return self._advanced_monitor
    
    @property
    def active_scraper(self):
        """Get the active scraper instance."""
        return self._active_scraper
    
    @active_scraper.setter
    def active_scraper(self, scraper):
        """Set the active scraper instance."""
        self._active_scraper = scraper
    
    @property
    def file_generator_service(self) -> Optional[FileGeneratorService]:
        """Get the file generator service."""
        return self._file_generator_service
    
    @file_generator_service.setter
    def file_generator_service(self, service: FileGeneratorService):
        """Set the file generator service."""
        self._file_generator_service = service
    
    @property
    def current_progress(self):
        """Get current progress."""
        return self._current_progress
    
    @current_progress.setter
    def current_progress(self, progress):
        """Set current progress."""
        self._current_progress = progress
    
    def reset(self):
        """Reset application state (useful for testing)."""
        self._advanced_monitor = None
        self._active_scraper = None
        self._file_generator_service = None
        self._current_progress = None


# Global singleton instance
_app_state = ApplicationState()


def get_app_state() -> ApplicationState:
    """Get the global application state instance."""
    return _app_state


def reset_app_state():
    """Reset the global application state (for testing)."""
    global _app_state
    _app_state.reset()