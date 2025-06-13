"""
Core tests for FormatSelectionManager without service dependencies.
"""
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.file_generator.format_selection_manager import FormatSelectionManager


class TestFormatSelectionManagerCore:
    """Test core FormatSelectionManager functionality."""
    
    def test_format_selection_manager_exists(self):
        """Test that FormatSelectionManager class exists."""
        manager = FormatSelectionManager()
        assert manager is not None
    
    def test_format_selection_manager_initialization(self):
        """Test FormatSelectionManager initialization with default settings."""
        manager = FormatSelectionManager()
        
        assert hasattr(manager, 'supported_formats')
        assert hasattr(manager, 'selected_formats')
        assert hasattr(manager, 'selection_mode')
        # Check private attributes exist
        assert hasattr(manager, '_format_configurations')
        assert hasattr(manager, '_supported_formats')
        assert hasattr(manager, '_selected_formats')
    
    def test_get_available_formats_includes_json(self):
        """Test that available formats include JSON format."""
        manager = FormatSelectionManager()
        
        available_formats = manager.get_available_formats()
        assert "json" in available_formats
        assert "text" in available_formats
        assert "pdf" in available_formats
    
    def test_single_format_selection_mode(self):
        """Test single format selection mode functionality."""
        manager = FormatSelectionManager()
        
        # Set single format selection mode
        result = manager.set_selection_mode("single")
        assert result["success"] is True
        assert manager.get_selection_mode() == "single"
        
        # Should only allow one format to be selected
        result = manager.select_format("json")
        assert result["success"] is True
        assert manager.get_selected_formats() == ["json"]
        
        # Selecting another format should replace the previous one
        result = manager.select_format("pdf")
        assert result["success"] is True
        assert manager.get_selected_formats() == ["pdf"]
    
    def test_multiple_format_selection_mode(self):
        """Test multiple format selection mode functionality."""
        manager = FormatSelectionManager()
        
        # Set multiple format selection mode
        result = manager.set_selection_mode("multiple")
        assert result["success"] is True
        assert manager.get_selection_mode() == "multiple"
        
        # Should allow multiple formats to be selected
        result = manager.select_format("json")
        assert result["success"] is True
        assert "json" in manager.get_selected_formats()
        
        # Adding another format should keep both
        result = manager.select_format("pdf")
        assert result["success"] is True
        assert "json" in manager.get_selected_formats()
        assert "pdf" in manager.get_selected_formats()
    
    def test_format_validation_rejects_invalid_formats(self):
        """Test that invalid formats are rejected."""
        manager = FormatSelectionManager()
        
        result = manager.select_format("invalid_format")
        assert result["success"] is False
        assert "invalid" in result["error"].lower()
    
    def test_format_field_selection_integration(self):
        """Test integration with field selection for JSON format."""
        manager = FormatSelectionManager()
        
        # Select JSON format with field selection
        field_selection = {
            'core_fields': True,
            'extended_fields': False,
            'additional_fields': True,
            'contact_fields': False,
            'descriptive_fields': True
        }
        
        result = manager.select_format("json", field_selection=field_selection)
        assert result["success"] is True
        
        # Should store field selection for JSON format
        json_config = manager.get_format_configuration("json")
        assert json_config["field_selection"] == field_selection