"""
Format Selection Manager for Enhanced Format Selection Feature.
Manages format selection preferences, validation, and configuration.
"""
from typing import List, Dict, Any, Optional, Callable, Union
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class SelectionMode(Enum):
    """Enumeration for format selection modes."""

    SINGLE = "single"
    MULTIPLE = "multiple"


class FormatSelectionError(Exception):
    """Custom exception for format selection errors."""

    pass


class FormatSelectionManager:
    """
    Manages format selection preferences and configuration.

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
        self._supported_formats = self.SUPPORTED_FORMATS.copy()
        self._selected_formats = []
        self._selection_mode = self._validate_and_convert_mode(initial_mode)
        self._format_configurations = {}
        self._format_priorities = self.DEFAULT_PRIORITIES.copy()
        self._format_selection_callback = None
        self._format_preferences = {
            "text": {"enabled": True, "priority": 1},
            "pdf": {"enabled": True, "priority": 2}, 
            "json": {"enabled": True, "priority": 3}
        }

        logger.debug(
            f"FormatSelectionManager initialized with mode: {self._selection_mode.value}"
        )

    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported formats (read-only)."""
        return self._supported_formats.copy()

    @property
    def selected_formats(self) -> List[str]:
        """Get list of currently selected formats (read-only)."""
        return self._selected_formats.copy()

    @property
    def selection_mode(self) -> SelectionMode:
        """Get current selection mode (read-only)."""
        return self._selection_mode

    @property
    def format_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Get format preferences (read-only)."""
        return self._format_preferences.copy()

    def get_available_formats(self) -> List[str]:
        """Get list of available formats."""
        return self.supported_formats

    def set_selection_mode(self, mode: Union[str, SelectionMode]) -> Dict[str, Any]:
        """
        Set format selection mode.

        Args:
            mode: Selection mode ('single', 'multiple', or SelectionMode enum)

        Returns:
            Dict with success status and optional error message
        """
        try:
            new_mode = self._validate_and_convert_mode(mode)

            # Clear selections when changing from multiple to single mode
            if (
                self._selection_mode == SelectionMode.MULTIPLE
                and new_mode == SelectionMode.SINGLE
            ):
                if len(self._selected_formats) > 1:
                    logger.info(
                        "Switching to single mode, keeping only first selected format"
                    )
                    self._selected_formats = self._selected_formats[:1]
                    # Remove configurations for deselected formats
                    for fmt in self._selected_formats[1:]:
                        self._format_configurations.pop(fmt, None)

            self._selection_mode = new_mode
            logger.debug(f"Selection mode changed to: {new_mode.value}")
            return {"success": True}

        except FormatSelectionError as e:
            logger.error(f"Failed to set selection mode: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_selection_mode(self) -> str:
        """Get current selection mode as string."""
        return self._selection_mode.value

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
        try:
            # Validate format name
            if not self._is_valid_format(format_name):
                raise FormatSelectionError(
                    f"Unsupported format: {format_name}. "
                    f"Supported formats: {', '.join(self._supported_formats)}"
                )

            # Validate format-specific configuration
            self._validate_format_configuration(format_name, field_selection)

            # Handle selection based on mode
            self._apply_format_selection(format_name)

            # Store format configuration
            self._store_format_configuration(format_name, field_selection)

            # Trigger callback
            self._trigger_selection_callback(format_name)

            logger.debug(
                f"Format selected: {format_name} with mode: {self._selection_mode.value}"
            )
            return {"success": True}

        except FormatSelectionError as e:
            logger.error(f"Format selection failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def deselect_format(self, format_name: str) -> Dict[str, Any]:
        """
        Deselect a format.

        Args:
            format_name: Name of the format to deselect

        Returns:
            Dict with success status
        """
        try:
            if format_name in self._selected_formats:
                self._selected_formats.remove(format_name)
                # Remove configuration
                self._format_configurations.pop(format_name, None)
                logger.debug(f"Format deselected: {format_name}")

            return {"success": True}

        except Exception as e:
            logger.error(f"Error deselecting format {format_name}: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_selected_formats(self) -> List[str]:
        """Get list of currently selected formats."""
        return self.selected_formats

    def clear_all_selections(self) -> None:
        """Clear all format selections and configurations."""
        self._selected_formats.clear()
        self._format_configurations.clear()
        logger.debug("All format selections cleared")

    def get_format_configuration(self, format_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific format.

        Args:
            format_name: Name of the format

        Returns:
            Configuration dict for the format (empty if not configured)
        """
        return self._format_configurations.get(format_name, {}).copy()

    def set_format_priority(self, priorities: List[str]) -> Dict[str, Any]:
        """
        Set format priority ordering.

        Args:
            priorities: List of format names in priority order

        Returns:
            Dict with success status
        """
        try:
            # Validate that all priorities are supported formats
            invalid_formats = [
                fmt for fmt in priorities if not self._is_valid_format(fmt)
            ]
            if invalid_formats:
                raise FormatSelectionError(
                    f"Invalid formats in priority list: {', '.join(invalid_formats)}"
                )

            self._format_priorities = priorities.copy()
            logger.debug(f"Format priorities updated: {priorities}")
            return {"success": True}

        except FormatSelectionError as e:
            logger.error(f"Failed to set format priorities: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_ordered_selected_formats(self) -> List[str]:
        """Get selected formats in priority order."""
        ordered = []

        # Add formats in priority order
        for fmt in self._format_priorities:
            if fmt in self._selected_formats:
                ordered.append(fmt)

        # Add any remaining selected formats not in priority list
        for fmt in self._selected_formats:
            if fmt not in ordered:
                ordered.append(fmt)

        return ordered

    def get_export_instructions(self) -> Dict[str, Any]:
        """Get comprehensive export instructions for selected formats."""
        return {
            "formats": self.get_selected_formats(),
            "configurations": {
                fmt: config.copy()
                for fmt, config in self._format_configurations.items()
            },
            "total_formats": len(self._selected_formats),
            "selection_mode": self._selection_mode.value,
            "priority_order": self.get_ordered_selected_formats(),
        }

    def save_configuration(self) -> Dict[str, Any]:
        """Save current configuration to dictionary for persistence."""
        return {
            "selected_formats": self.selected_formats,
            "selection_mode": self._selection_mode.value,
            "format_configurations": {
                fmt: config.copy()
                for fmt, config in self._format_configurations.items()
            },
            "format_priorities": self._format_priorities.copy(),
        }

    def load_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load configuration from dictionary.

        Args:
            config_data: Configuration data dictionary

        Returns:
            Dict with success status
        """
        try:
            # Validate and load selection mode
            mode_str = config_data.get("selection_mode", "single")
            self._selection_mode = self._validate_and_convert_mode(mode_str)

            # Load selected formats (validate each)
            selected = config_data.get("selected_formats", [])
            for fmt in selected:
                if not self._is_valid_format(fmt):
                    raise FormatSelectionError(
                        f"Invalid format in configuration: {fmt}"
                    )
            self._selected_formats = selected.copy()

            # Load configurations
            self._format_configurations = config_data.get(
                "format_configurations", {}
            ).copy()

            # Load priorities
            priorities = config_data.get("format_priorities", self.DEFAULT_PRIORITIES)
            self._format_priorities = priorities.copy()

            logger.debug("Configuration loaded successfully")
            return {"success": True}

        except (FormatSelectionError, KeyError, TypeError) as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return {"success": False, "error": str(e)}

    def set_format_selection_callback(
        self, callback: Optional[Callable[[str], None]]
    ) -> None:
        """
        Set callback for format selection events.

        Args:
            callback: Function to call when format is selected (or None to remove)
        """
        self._format_selection_callback = callback
        logger.debug(f"Format selection callback {'set' if callback else 'removed'}")

    # Private helper methods

    def _validate_and_convert_mode(
        self, mode: Union[str, SelectionMode]
    ) -> SelectionMode:
        """Validate and convert selection mode to enum."""
        if isinstance(mode, SelectionMode):
            return mode

        if isinstance(mode, str):
            try:
                return SelectionMode(mode.lower())
            except ValueError:
                raise FormatSelectionError(
                    f"Invalid selection mode: {mode}. Use 'single' or 'multiple'"
                )

        raise FormatSelectionError(
            f"Selection mode must be string or SelectionMode enum, got: {type(mode)}"
        )

    def _is_valid_format(self, format_name: str) -> bool:
        """Check if format name is valid."""
        return format_name in self._supported_formats

    def _validate_format_configuration(
        self, format_name: str, field_selection: Optional[Dict[str, bool]]
    ) -> None:
        """Validate format-specific configuration."""
        if format_name == "json" and field_selection:
            self._validate_json_field_selection(field_selection)

    def _validate_json_field_selection(self, field_selection: Dict[str, bool]) -> None:
        """Validate JSON field selection configuration."""
        for field_name, value in field_selection.items():
            if field_name not in self.VALID_JSON_FIELDS:
                raise FormatSelectionError(
                    f"JSON field validation failed: {field_name}. "
                    f"Valid fields: {', '.join(self.VALID_JSON_FIELDS)}"
                )

            if not isinstance(value, bool):
                raise FormatSelectionError(
                    f"JSON field value must be boolean: {field_name}"
                )

    def _apply_format_selection(self, format_name: str) -> None:
        """Apply format selection based on current mode."""
        if self._selection_mode == SelectionMode.SINGLE:
            # Clear previous selections and configurations
            old_formats = self._selected_formats.copy()
            self._selected_formats = [format_name]

            # Clean up old configurations
            for fmt in old_formats:
                if fmt != format_name:
                    self._format_configurations.pop(fmt, None)

        elif self._selection_mode == SelectionMode.MULTIPLE:
            if format_name not in self._selected_formats:
                self._selected_formats.append(format_name)

    def _store_format_configuration(
        self, format_name: str, field_selection: Optional[Dict[str, bool]]
    ) -> None:
        """Store format-specific configuration."""
        config = self._format_configurations.get(format_name, {})

        if field_selection:
            config["field_selection"] = field_selection.copy()

        self._format_configurations[format_name] = config

    def _trigger_selection_callback(self, format_name: str) -> None:
        """Trigger format selection callback if set."""
        if self._format_selection_callback:
            try:
                self._format_selection_callback(format_name)
            except Exception as e:
                logger.warning(f"Format selection callback failed: {str(e)}")
