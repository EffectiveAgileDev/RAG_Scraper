"""
Extended tests for FormatSelectionManager functionality.
"""
import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.file_generator.format_selection_manager import FormatSelectionManager


class TestFormatSelectionManagerExtended:
    """Test extended FormatSelectionManager functionality."""

    def test_format_priority_ordering(self):
        """Test format priority ordering for export."""
        manager = FormatSelectionManager()

        # Set format priorities
        manager.set_format_priority(["json", "pdf", "text"])

        # Select multiple formats
        manager.set_selection_mode("multiple")
        manager.select_format("text")
        manager.select_format("json")
        manager.select_format("pdf")

        # Should return formats in priority order
        ordered_formats = manager.get_ordered_selected_formats()
        assert ordered_formats == ["json", "pdf", "text"]

    def test_format_configuration_persistence(self):
        """Test that format configurations are persisted."""
        manager = FormatSelectionManager()

        # Configure JSON format with field selection
        field_selection = {"core_fields": True, "extended_fields": False}
        manager.select_format("json", field_selection=field_selection)

        # Save configuration
        config_data = manager.save_configuration()
        assert config_data["selected_formats"] == ["json"]
        assert (
            config_data["format_configurations"]["json"]["field_selection"]
            == field_selection
        )

        # Load configuration in new manager
        new_manager = FormatSelectionManager()
        new_manager.load_configuration(config_data)
        assert new_manager.get_selected_formats() == ["json"]
        assert (
            new_manager.get_format_configuration("json")["field_selection"]
            == field_selection
        )

    def test_deselect_format_functionality(self):
        """Test format deselection functionality."""
        manager = FormatSelectionManager()

        manager.set_selection_mode("multiple")
        manager.select_format("json")
        manager.select_format("pdf")

        # Deselect one format
        result = manager.deselect_format("json")
        assert result["success"] is True
        assert "json" not in manager.get_selected_formats()
        assert "pdf" in manager.get_selected_formats()

    def test_clear_all_selections(self):
        """Test clearing all format selections."""
        manager = FormatSelectionManager()

        manager.set_selection_mode("multiple")
        manager.select_format("json")
        manager.select_format("pdf")
        manager.select_format("text")

        manager.clear_all_selections()
        assert manager.get_selected_formats() == []

    def test_get_export_instructions(self):
        """Test getting export instructions for selected formats."""
        manager = FormatSelectionManager()

        manager.select_format("json")

        instructions = manager.get_export_instructions()
        assert instructions["formats"] == ["json"]
        assert "json" in instructions["configurations"]
        assert instructions["total_formats"] == 1

    def test_format_specific_configuration_validation(self):
        """Test validation of format-specific configurations."""
        manager = FormatSelectionManager()

        # Test invalid field selection for JSON
        invalid_field_selection = {
            "invalid_field": True,
            "core_fields": "not_boolean",  # Should be boolean
        }

        result = manager.select_format("json", field_selection=invalid_field_selection)
        assert result["success"] is False
        # Error message should indicate validation failure (either "validation" or "invalid")
        error_msg = result["error"].lower()
        assert "validation" in error_msg or "invalid" in error_msg

    def test_format_selection_callbacks(self):
        """Test format selection event callbacks."""
        manager = FormatSelectionManager()

        callback_called = False
        selected_format = None

        def format_selected_callback(format_name):
            nonlocal callback_called, selected_format
            callback_called = True
            selected_format = format_name

        manager.set_format_selection_callback(format_selected_callback)
        manager.select_format("json")

        assert callback_called is True
        assert selected_format == "json"

    def test_invalid_selection_mode(self):
        """Test handling of invalid selection modes."""
        manager = FormatSelectionManager()

        result = manager.set_selection_mode("invalid_mode")
        assert result["success"] is False
        assert "invalid" in result["error"].lower()

    def test_empty_format_selection(self):
        """Test behavior with empty format selection."""
        manager = FormatSelectionManager()

        instructions = manager.get_export_instructions()
        assert instructions["formats"] == []
        assert instructions["total_formats"] == 0
