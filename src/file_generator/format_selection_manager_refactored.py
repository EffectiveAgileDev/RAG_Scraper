"""
Refactored Format Selection Logic with separated concerns.

This refactored version addresses the brittleness issues by:
- Separating validation, configuration management, and selection logic
- Using dependency injection for better testability  
- Reducing coupling between components
- Enabling better unit testing of individual concerns
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


class FormatValidator:
    """Pure validation service for format names and configurations."""
    
    def __init__(self, supported_formats: List[str] = None):
        """Initialize format validator.
        
        Args:
            supported_formats: List of supported format names
        """
        self.supported_formats = supported_formats or ["text", "pdf", "json"]
        self.valid_json_fields = [
            "core_fields", "extended_fields", "additional_fields", 
            "contact_fields", "descriptive_fields"
        ]
    
    def validate_format(self, format_name: str) -> Dict[str, Any]:
        """Validate format name.
        
        Args:
            format_name: Format name to validate
            
        Returns:
            Dict with validation result
        """
        if not isinstance(format_name, str):
            return {
                "valid": False, 
                "error": f"Format name must be string, got: {type(format_name)}"
            }
            
        if not format_name or not format_name.strip():
            return {"valid": False, "error": "Format name cannot be empty"}
            
        if format_name not in self.supported_formats:
            return {
                "valid": False,
                "error": f"Unsupported format: {format_name}. Supported formats: {', '.join(self.supported_formats)}"
            }
            
        return {"valid": True}
    
    def validate_selection_mode(self, mode: Union[str, SelectionMode]) -> Dict[str, Any]:
        """Validate selection mode.
        
        Args:
            mode: Selection mode to validate
            
        Returns:
            Dict with validation result
        """
        if isinstance(mode, SelectionMode):
            return {"valid": True, "mode": mode}
            
        if isinstance(mode, str):
            try:
                converted_mode = SelectionMode(mode.lower())
                return {"valid": True, "mode": converted_mode}
            except ValueError:
                return {
                    "valid": False,
                    "error": f"Invalid selection mode: {mode}. Use 'single' or 'multiple'"
                }
        
        return {
            "valid": False,
            "error": f"Selection mode must be string or SelectionMode enum, got: {type(mode)}"
        }
    
    def validate_json_configuration(self, field_selection: Dict[str, bool]) -> Dict[str, Any]:
        """Validate JSON field selection configuration.
        
        Args:
            field_selection: JSON field selection configuration
            
        Returns:
            Dict with validation result
        """
        if not isinstance(field_selection, dict):
            return {"valid": False, "error": "Field selection must be a dictionary"}
            
        for field_name, value in field_selection.items():
            if field_name not in self.valid_json_fields:
                return {
                    "valid": False,
                    "error": f"JSON field validation failed: {field_name}. Valid fields: {', '.join(self.valid_json_fields)}"
                }
            
            if not isinstance(value, bool):
                return {
                    "valid": False,
                    "error": f"JSON field validation failed: {field_name} value must be boolean"
                }
                
        return {"valid": True}


class FormatConfigurationManager:
    """Service for managing format-specific configurations."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self._configurations = {}
        self._priorities = ["text", "pdf", "json"]
        self._preferences = {
            "text": {"enabled": True, "priority": 1},
            "pdf": {"enabled": True, "priority": 2}, 
            "json": {"enabled": True, "priority": 3}
        }
    
    def store_configuration(self, format_name: str, configuration: Dict[str, Any]) -> None:
        """Store configuration for a format.
        
        Args:
            format_name: Format name
            configuration: Configuration data
        """
        self._configurations[format_name] = configuration.copy() if configuration else {}
    
    def get_configuration(self, format_name: str) -> Dict[str, Any]:
        """Get configuration for a format.
        
        Args:
            format_name: Format name
            
        Returns:
            Configuration dict (empty if not found)
        """
        return self._configurations.get(format_name, {}).copy()
    
    def remove_configuration(self, format_name: str) -> None:
        """Remove configuration for a format.
        
        Args:
            format_name: Format name
        """
        self._configurations.pop(format_name, None)
    
    def clear_all_configurations(self) -> None:
        """Clear all configurations."""
        self._configurations.clear()
    
    def set_priorities(self, priorities: List[str]) -> None:
        """Set format priority ordering.
        
        Args:
            priorities: List of format names in priority order
        """
        self._priorities = priorities.copy()
    
    def get_priorities(self) -> List[str]:
        """Get format priority ordering."""
        return self._priorities.copy()
    
    def save_state(self) -> Dict[str, Any]:
        """Save configuration state to dictionary.
        
        Returns:
            Configuration state
        """
        return {
            "configurations": {
                fmt: config.copy() for fmt, config in self._configurations.items()
            },
            "priorities": self._priorities.copy(),
            "preferences": {
                fmt: pref.copy() for fmt, pref in self._preferences.items()
            }
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """Load configuration state from dictionary.
        
        Args:
            state: Configuration state
        """
        self._configurations = state.get("configurations", {}).copy()
        self._priorities = state.get("priorities", ["text", "pdf", "json"]).copy()
        self._preferences = state.get("preferences", {}).copy()


class FormatSelectionService:
    """Service for managing format selection logic."""
    
    def __init__(self, selection_mode: SelectionMode = SelectionMode.SINGLE):
        """Initialize selection service.
        
        Args:
            selection_mode: Initial selection mode
        """
        self._selection_mode = selection_mode
        self._selected_formats = []
        self._callback = None
    
    def get_selection_mode(self) -> SelectionMode:
        """Get current selection mode."""
        return self._selection_mode
    
    def set_selection_mode(self, mode: SelectionMode) -> None:
        """Set selection mode.
        
        Args:
            mode: New selection mode
        """
        # Handle mode transition logic
        if self._selection_mode == SelectionMode.MULTIPLE and mode == SelectionMode.SINGLE:
            # Keep only first format when switching to single mode
            if len(self._selected_formats) > 1:
                self._selected_formats = self._selected_formats[:1]
                logger.info("Switched to single mode, keeping only first selected format")
        
        self._selection_mode = mode
    
    def select_format(self, format_name: str) -> None:
        """Select a format based on current mode.
        
        Args:
            format_name: Format name to select
        """
        if self._selection_mode == SelectionMode.SINGLE:
            # Replace current selection
            self._selected_formats = [format_name]
        elif self._selection_mode == SelectionMode.MULTIPLE:
            # Add to selection if not already present
            if format_name not in self._selected_formats:
                self._selected_formats.append(format_name)
        
        # Trigger callback
        if self._callback:
            try:
                self._callback(format_name)
            except Exception as e:
                logger.warning(f"Selection callback failed: {str(e)}")
    
    def deselect_format(self, format_name: str) -> None:
        """Deselect a format.
        
        Args:
            format_name: Format name to deselect
        """
        if format_name in self._selected_formats:
            self._selected_formats.remove(format_name)
    
    def get_selected_formats(self) -> List[str]:
        """Get list of selected formats."""
        return self._selected_formats.copy()
    
    def clear_selections(self) -> None:
        """Clear all format selections."""
        self._selected_formats.clear()
    
    def set_callback(self, callback: Optional[Callable[[str], None]]) -> None:
        """Set selection callback.
        
        Args:
            callback: Callback function or None to remove
        """
        self._callback = callback
    
    def get_ordered_formats(self, priorities: List[str]) -> List[str]:
        """Get selected formats in priority order.
        
        Args:
            priorities: Priority ordering
            
        Returns:
            Selected formats in priority order
        """
        ordered = []
        
        # Add formats in priority order
        for fmt in priorities:
            if fmt in self._selected_formats:
                ordered.append(fmt)
        
        # Add any remaining selected formats not in priority list
        for fmt in self._selected_formats:
            if fmt not in ordered:
                ordered.append(fmt)
        
        return ordered


class RefactoredFormatSelectionManager:
    """
    Refactored format selection manager using separation of concerns.
    
    This manager separates concerns into dedicated services:
    - Format validation
    - Configuration management  
    - Selection logic
    """
    
    # Class constants for supported formats
    SUPPORTED_FORMATS = ["text", "pdf", "json"]
    DEFAULT_PRIORITIES = ["text", "pdf", "json"]
    
    def __init__(self, 
                 initial_mode: Union[str, SelectionMode] = SelectionMode.SINGLE,
                 validator: Optional[FormatValidator] = None,
                 config_manager: Optional[FormatConfigurationManager] = None,
                 selection_service: Optional[FormatSelectionService] = None):
        """Initialize refactored format selection manager.
        
        Args:
            initial_mode: Initial selection mode
            validator: Injectable format validator
            config_manager: Injectable configuration manager
            selection_service: Injectable selection service
        """
        # Validate initial mode
        self.validator = validator or FormatValidator(self.SUPPORTED_FORMATS)
        mode_validation = self.validator.validate_selection_mode(initial_mode)
        if not mode_validation["valid"]:
            raise FormatSelectionError(mode_validation["error"])
        
        # Initialize services
        self.config_manager = config_manager or FormatConfigurationManager()
        self.selection_service = selection_service or FormatSelectionService(mode_validation["mode"])
        
        logger.debug(f"RefactoredFormatSelectionManager initialized with mode: {self.selection_service.get_selection_mode().value}")
    
    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported formats (read-only)."""
        return self.SUPPORTED_FORMATS.copy()
    
    @property
    def selected_formats(self) -> List[str]:
        """Get list of currently selected formats (read-only)."""
        return self.selection_service.get_selected_formats()
    
    @property
    def selection_mode(self) -> SelectionMode:
        """Get current selection mode (read-only)."""
        return self.selection_service.get_selection_mode()
    
    @property
    def format_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Get format preferences (read-only)."""
        state = self.config_manager.save_state()
        return state.get("preferences", {}).copy()
    
    def get_available_formats(self) -> List[str]:
        """Get list of available formats."""
        return self.supported_formats
    
    def set_selection_mode(self, mode: Union[str, SelectionMode]) -> Dict[str, Any]:
        """Set format selection mode.
        
        Args:
            mode: Selection mode to set
            
        Returns:
            Dict with success status
        """
        # Validate mode
        validation = self.validator.validate_selection_mode(mode)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}
        
        # Apply mode change
        old_formats = self.selection_service.get_selected_formats()
        self.selection_service.set_selection_mode(validation["mode"])
        
        # Clean up configurations for deselected formats
        new_formats = self.selection_service.get_selected_formats()
        for fmt in old_formats:
            if fmt not in new_formats:
                self.config_manager.remove_configuration(fmt)
        
        return {"success": True}
    
    def get_selection_mode(self) -> str:
        """Get current selection mode as string."""
        return self.selection_service.get_selection_mode().value
    
    def select_format(self, format_name: str, field_selection: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """Select a format with optional configuration.
        
        Args:
            format_name: Name of the format to select
            field_selection: Optional field selection configuration
            
        Returns:
            Dict with success status
        """
        # Validate format
        format_validation = self.validator.validate_format(format_name)
        if not format_validation["valid"]:
            return {"success": False, "error": format_validation["error"]}
        
        # Validate format-specific configuration
        if format_name == "json" and field_selection:
            config_validation = self.validator.validate_json_configuration(field_selection)
            if not config_validation["valid"]:
                return {"success": False, "error": config_validation["error"]}
        
        # Apply selection
        old_formats = self.selection_service.get_selected_formats()
        self.selection_service.select_format(format_name)
        
        # Clean up configurations for deselected formats (in single mode)
        if self.selection_service.get_selection_mode() == SelectionMode.SINGLE:
            for fmt in old_formats:
                if fmt != format_name:
                    self.config_manager.remove_configuration(fmt)
        
        # Store configuration
        config = {}
        if field_selection:
            config["field_selection"] = field_selection
        self.config_manager.store_configuration(format_name, config)
        
        logger.debug(f"Format selected: {format_name} with mode: {self.get_selection_mode()}")
        return {"success": True}
    
    def deselect_format(self, format_name: str) -> Dict[str, Any]:
        """Deselect a format.
        
        Args:
            format_name: Format name to deselect
            
        Returns:
            Dict with success status
        """
        self.selection_service.deselect_format(format_name)
        self.config_manager.remove_configuration(format_name)
        logger.debug(f"Format deselected: {format_name}")
        return {"success": True}
    
    def get_selected_formats(self) -> List[str]:
        """Get list of currently selected formats."""
        return self.selected_formats
    
    def clear_all_selections(self) -> None:
        """Clear all format selections and configurations."""
        self.selection_service.clear_selections()
        self.config_manager.clear_all_configurations()
        logger.debug("All format selections cleared")
    
    def get_format_configuration(self, format_name: str) -> Dict[str, Any]:
        """Get configuration for a specific format.
        
        Args:
            format_name: Format name
            
        Returns:
            Configuration dict
        """
        return self.config_manager.get_configuration(format_name)
    
    def set_format_priority(self, priorities: List[str]) -> Dict[str, Any]:
        """Set format priority ordering.
        
        Args:
            priorities: List of format names in priority order
            
        Returns:
            Dict with success status
        """
        # Validate all priorities
        for fmt in priorities:
            validation = self.validator.validate_format(fmt)
            if not validation["valid"]:
                return {"success": False, "error": f"Invalid format in priority list: {fmt}"}
        
        self.config_manager.set_priorities(priorities)
        logger.debug(f"Format priorities updated: {priorities}")
        return {"success": True}
    
    def get_ordered_selected_formats(self) -> List[str]:
        """Get selected formats in priority order."""
        priorities = self.config_manager.get_priorities()
        return self.selection_service.get_ordered_formats(priorities)
    
    def get_export_instructions(self) -> Dict[str, Any]:
        """Get comprehensive export instructions for selected formats."""
        return {
            "formats": self.get_selected_formats(),
            "configurations": {
                fmt: self.config_manager.get_configuration(fmt)
                for fmt in self.get_selected_formats()
            },
            "total_formats": len(self.get_selected_formats()),
            "selection_mode": self.get_selection_mode(),
            "priority_order": self.get_ordered_selected_formats(),
        }
    
    def save_configuration(self) -> Dict[str, Any]:
        """Save current configuration to dictionary for persistence."""
        config_state = self.config_manager.save_state()
        return {
            "selected_formats": self.get_selected_formats(),
            "selection_mode": self.get_selection_mode(),
            "format_configurations": config_state["configurations"],
            "format_priorities": config_state["priorities"],
        }
    
    def load_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration from dictionary.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            Dict with success status
        """
        try:
            # Validate and load selection mode
            mode_str = config_data.get("selection_mode", "single")
            mode_validation = self.validator.validate_selection_mode(mode_str)
            if not mode_validation["valid"]:
                return {"success": False, "error": mode_validation["error"]}
            
            # Validate selected formats
            selected = config_data.get("selected_formats", [])
            for fmt in selected:
                validation = self.validator.validate_format(fmt)
                if not validation["valid"]:
                    return {"success": False, "error": f"Invalid format in configuration: {fmt}"}
            
            # Load configuration state
            config_state = {
                "configurations": config_data.get("format_configurations", {}),
                "priorities": config_data.get("format_priorities", self.DEFAULT_PRIORITIES),
                "preferences": {}
            }
            self.config_manager.load_state(config_state)
            
            # Apply selection mode and formats
            self.selection_service.set_selection_mode(mode_validation["mode"])
            self.selection_service.clear_selections()
            for fmt in selected:
                self.selection_service.select_format(fmt)
            
            logger.debug("Configuration loaded successfully")
            return {"success": True}
            
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def set_format_selection_callback(self, callback: Optional[Callable[[str], None]]) -> None:
        """Set callback for format selection events.
        
        Args:
            callback: Function to call when format is selected (or None to remove)
        """
        self.selection_service.set_callback(callback)
        logger.debug(f"Format selection callback {'set' if callback else 'removed'}")


# Backward compatibility - Create factory function
def create_refactored_format_selection_manager(initial_mode: Union[str, SelectionMode] = SelectionMode.SINGLE):
    """Create refactored format selection manager with default components."""
    return RefactoredFormatSelectionManager(initial_mode=initial_mode)