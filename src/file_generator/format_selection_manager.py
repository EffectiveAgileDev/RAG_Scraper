"""
Format Selection Manager for Enhanced Format Selection Feature.

This module now uses the refactored implementation internally while maintaining
backward compatibility with existing code.
"""
from typing import List, Dict, Any, Optional, Callable, Union
from enum import Enum
import logging

# Import the refactored implementation
from .format_selection_manager_refactored import (
    RefactoredFormatSelectionManager,
    SelectionMode,
    FormatSelectionError,
    FormatValidator,
    FormatConfigurationManager,
    FormatSelectionService
)

logger = logging.getLogger(__name__)


class FormatSelectionManager:
    """
    Manages format selection preferences and configuration.
    
    This class now uses the refactored implementation internally while maintaining
    backward compatibility with existing code.

    Provides functionality for:
    - Single or multiple format selection modes
    - Format-specific configuration (e.g., field selection for JSON)
    - Format priority ordering
    - Configuration persistence
    - Event callbacks
    """

    # Class constants for supported formats
    SUPPORTED_FORMATS = ["text", "pdf", "json"]
    DEFAULT_PRIORITIES = ["text", "pdf", "json"]
    VALID_JSON_FIELDS = [
        "core_fields",
        "extended_fields",
        "additional_fields",
        "contact_fields",
        "descriptive_fields",
    ]

    def __init__(self, initial_mode: Union[str, SelectionMode] = SelectionMode.SINGLE):
        """
        Initialize format selection manager with default settings.

        Args:
            initial_mode: Initial selection mode (single or multiple)
        """
        # Initialize the refactored implementation
        self._refactored_manager = RefactoredFormatSelectionManager(initial_mode=initial_mode)
        
        # Store backward compatibility attributes
        self._supported_formats = self.SUPPORTED_FORMATS.copy()
        self._format_preferences = {
            "text": {"enabled": True, "priority": 1},
            "pdf": {"enabled": True, "priority": 2}, 
            "json": {"enabled": True, "priority": 3}
        }
        
        # Backward compatibility: Expose delegated internal state
        self._selected_formats = self._refactored_manager.selected_formats
        self._format_configurations = {}
        self._format_priorities = self.DEFAULT_PRIORITIES.copy()
        self._selection_mode = self._refactored_manager.selection_mode
        self._format_selection_callback = None

        logger.debug(
            f"FormatSelectionManager initialized with mode: {self._refactored_manager.get_selection_mode()}"
        )

    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported formats (read-only)."""
        return self._refactored_manager.supported_formats

    @property
    def selected_formats(self) -> List[str]:
        """Get list of currently selected formats (read-only)."""
        return self._refactored_manager.selected_formats

    @property
    def selection_mode(self) -> SelectionMode:
        """Get current selection mode (read-only)."""
        return self._refactored_manager.selection_mode

    @property
    def format_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Get format preferences (read-only)."""
        return self._format_preferences.copy()

    def get_available_formats(self) -> List[str]:
        """Get list of available formats."""
        return self._refactored_manager.get_available_formats()

    def set_selection_mode(self, mode: Union[str, SelectionMode]) -> Dict[str, Any]:
        """
        Set format selection mode.

        Args:
            mode: Selection mode ('single', 'multiple', or SelectionMode enum)

        Returns:
            Dict with success status and optional error message
        """
        return self._refactored_manager.set_selection_mode(mode)

    def get_selection_mode(self) -> str:
        """Get current selection mode as string."""
        return self._refactored_manager.get_selection_mode()

    def select_format(
        self, format_name: str, field_selection: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Select a format with optional configuration.

        Args:
            format_name: Name of the format to select
            field_selection: Optional field selection configuration (for JSON format)

        Returns:
            Dict with success status and optional error message
        """
        return self._refactored_manager.select_format(format_name, field_selection)

    def deselect_format(self, format_name: str) -> Dict[str, Any]:
        """
        Deselect a format.

        Args:
            format_name: Name of the format to deselect

        Returns:
            Dict with success status
        """
        return self._refactored_manager.deselect_format(format_name)

    def get_selected_formats(self) -> List[str]:
        """Get list of currently selected formats."""
        return self._refactored_manager.get_selected_formats()

    def clear_all_selections(self) -> None:
        """Clear all format selections and configurations."""
        self._refactored_manager.clear_all_selections()

    def get_format_configuration(self, format_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific format.

        Args:
            format_name: Name of the format

        Returns:
            Configuration dict for the format (empty if not configured)
        """
        return self._refactored_manager.get_format_configuration(format_name)

    def set_format_priority(self, priorities: List[str]) -> Dict[str, Any]:
        """
        Set format priority ordering.

        Args:
            priorities: List of format names in priority order

        Returns:
            Dict with success status
        """
        return self._refactored_manager.set_format_priority(priorities)

    def get_ordered_selected_formats(self) -> List[str]:
        """Get selected formats in priority order."""
        return self._refactored_manager.get_ordered_selected_formats()

    def get_export_instructions(self) -> Dict[str, Any]:
        """Get comprehensive export instructions for selected formats."""
        return self._refactored_manager.get_export_instructions()

    def save_configuration(self) -> Dict[str, Any]:
        """Save current configuration to dictionary for persistence."""
        return self._refactored_manager.save_configuration()

    def load_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load configuration from dictionary.

        Args:
            config_data: Configuration data dictionary

        Returns:
            Dict with success status
        """
        return self._refactored_manager.load_configuration(config_data)

    def set_format_selection_callback(
        self, callback: Optional[Callable[[str], None]]
    ) -> None:
        """
        Set callback for format selection events.

        Args:
            callback: Function to call when format is selected (or None to remove)
        """
        self._refactored_manager.set_format_selection_callback(callback)

    # Backward compatibility: Expose some private methods that tests expect
    def _validate_and_convert_mode(self, mode):
        """Backward compatibility: delegate to refactored validator."""
        validation = self._refactored_manager.validator.validate_selection_mode(mode)
        if not validation["valid"]:
            raise FormatSelectionError(validation["error"])
        return validation["mode"]
    
    def _is_valid_format(self, format_name):
        """Backward compatibility: delegate to refactored validator."""
        return self._refactored_manager.validator.validate_format(format_name)["valid"]
