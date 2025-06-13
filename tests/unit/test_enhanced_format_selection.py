"""
Unit tests for Enhanced Format Selection Feature.
Following TDD Red-Green-Refactor process for format selection enhancements.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.file_generator.file_generator_service import FileGeneratorService, FileGenerationRequest
from src.scraper.multi_strategy_scraper import RestaurantData


class TestEnhancedFormatSelection:
    """Test enhanced format selection capabilities."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = FileGeneratorService()
        self.sample_restaurant_data = [
            RestaurantData(
                name="Test Restaurant",
                address="123 Main St",
                phone="(555) 123-4567",
                hours="Mon-Fri: 9AM-10PM",
                price_range="$$",
                cuisine="Italian"
            )
        ]
    
    def test_format_selection_manager_exists(self):
        """Test that FormatSelectionManager class exists."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        assert manager is not None
    
    def test_format_selection_manager_initialization(self):
        """Test FormatSelectionManager initialization with default settings."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        # Should have default format preferences
        assert hasattr(manager, 'format_preferences')
        assert hasattr(manager, 'supported_formats')
        assert hasattr(manager, 'selection_mode')
    
    def test_get_available_formats_includes_json(self):
        """Test that available formats include JSON format."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        available_formats = manager.get_available_formats()
        assert "json" in available_formats
        assert "text" in available_formats
        assert "pdf" in available_formats
    
    def test_single_format_selection_mode(self):
        """Test single format selection mode functionality."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        # Set single format selection mode
        manager.set_selection_mode("single")
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
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        # Set multiple format selection mode
        manager.set_selection_mode("multiple")
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
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        result = manager.select_format("invalid_format")
        assert result["success"] is False
        assert "invalid" in result["error"].lower()
    
    def test_format_field_selection_integration(self):
        """Test integration with field selection for JSON format."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
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
    
    def test_format_priority_ordering(self):
        """Test format priority ordering for export."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
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
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        # Configure JSON format with field selection
        field_selection = {'core_fields': True, 'extended_fields': False}
        manager.select_format("json", field_selection=field_selection)
        
        # Save configuration
        config_data = manager.save_configuration()
        assert config_data["selected_formats"] == ["json"]
        assert config_data["format_configurations"]["json"]["field_selection"] == field_selection
        
        # Load configuration in new manager
        new_manager = FormatSelectionManager()
        new_manager.load_configuration(config_data)
        assert new_manager.get_selected_formats() == ["json"]
        assert new_manager.get_format_configuration("json")["field_selection"] == field_selection


class TestFormatSelectionManagerMethods:
    """Test specific methods of FormatSelectionManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pass
    
    def test_deselect_format_functionality(self):
        """Test format deselection functionality."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
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
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        manager.set_selection_mode("multiple")
        manager.select_format("json")
        manager.select_format("pdf")
        manager.select_format("text")
        
        manager.clear_all_selections()
        assert manager.get_selected_formats() == []
    
    def test_get_export_instructions(self):
        """Test getting export instructions for selected formats."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        manager.select_format("json")
        
        instructions = manager.get_export_instructions()
        assert instructions["formats"] == ["json"]
        assert "json" in instructions["configurations"]
        assert instructions["total_formats"] == 1
    
    def test_format_specific_configuration_validation(self):
        """Test validation of format-specific configurations."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        # Test invalid field selection for JSON
        invalid_field_selection = {
            'invalid_field': True,
            'core_fields': "not_boolean"  # Should be boolean
        }
        
        result = manager.select_format("json", field_selection=invalid_field_selection)
        assert result["success"] is False
        assert "validation" in result["error"].lower()
    
    def test_format_selection_callbacks(self):
        """Test format selection event callbacks."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
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


class TestFileGeneratorServiceIntegration:
    """Test integration with file generator service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = FileGeneratorService()
        self.sample_data = [
            RestaurantData(
                name="Integration Test Restaurant",
                address="456 Integration Ave",
                phone="(555) 555-0001",
                hours="Daily: 10AM-10PM",
                cuisine="Integration"
            )
        ]
    
    def test_enhanced_file_generation_request_with_format_selection(self):
        """Test FileGenerationRequest with format selection manager."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        
        # Create format selection manager
        format_manager = FormatSelectionManager()
        format_manager.select_format("json", field_selection={'core_fields': True})
        
        # Create enhanced file generation request
        request = FileGenerationRequest(
            restaurant_data=self.sample_data,
            file_format="json",
            output_directory="/tmp",
            format_manager=format_manager
        )
        
        # Should use format manager for configuration
        assert request.format_manager is not None
        assert request.format_manager.get_selected_formats() == ["json"]
    
    def test_file_generator_service_uses_format_manager(self):
        """Test that file generator service uses format manager when provided."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        
        format_manager = FormatSelectionManager()
        format_manager.select_format("json")
        
        # Mock the enhanced generation method
        with patch.object(self.service, '_generate_with_format_manager') as mock_method:
            mock_method.return_value = {"success": True, "file_path": "/tmp/test.json"}
            
            request = FileGenerationRequest(
                restaurant_data=self.sample_data,
                file_format="json",
                format_manager=format_manager
            )
            
            result = self.service.generate_file(request)
            
            # Should call enhanced generation method
            mock_method.assert_called_once()
    
    def test_backward_compatibility_without_format_manager(self):
        """Test backward compatibility when format manager is not provided."""
        request = FileGenerationRequest(
            restaurant_data=self.sample_data,
            file_format="json",
            output_directory="/tmp"
        )
        
        # Should work with existing functionality
        result = self.service.generate_file(request)
        assert "success" in result
    
    def test_format_manager_override_field_selection(self):
        """Test that format manager overrides field_selection parameter."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        
        format_manager = FormatSelectionManager()
        format_manager.select_format("json", field_selection={'core_fields': True})
        
        # Create request with both format_manager and field_selection
        request = FileGenerationRequest(
            restaurant_data=self.sample_data,
            file_format="json",
            field_selection={'core_fields': False},  # Should be overridden
            format_manager=format_manager
        )
        
        # Mock JSON generation to verify field selection
        with patch('src.file_generator.file_generator_service.JSONExportGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_json_file.return_value = {
                'success': True,
                'file_path': '/tmp/test.json',
                'restaurant_count': 1
            }
            
            self.service.generate_file(request)
            
            # Should use format manager's field selection, not request's
            call_args = mock_generator.generate_json_file.call_args
            used_field_selection = call_args.kwargs.get('field_selection')
            assert used_field_selection == {'core_fields': True}


class TestEnhancedFormatSelectionEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_concurrent_format_selection_changes(self):
        """Test handling of concurrent format selection changes."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        # Simulate concurrent access
        manager.select_format("json")
        manager.select_format("pdf")
        manager.deselect_format("json")
        
        # Should maintain consistency
        assert manager.get_selected_formats() == ["pdf"]
    
    def test_invalid_selection_mode(self):
        """Test handling of invalid selection modes."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        result = manager.set_selection_mode("invalid_mode")
        assert result["success"] is False
        assert "invalid" in result["error"].lower()
    
    def test_empty_format_selection(self):
        """Test behavior with empty format selection."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        instructions = manager.get_export_instructions()
        assert instructions["formats"] == []
        assert instructions["total_formats"] == 0
    
    def test_format_manager_memory_efficiency(self):
        """Test that format manager is memory efficient with large configurations."""
        from src.file_generator.format_selection_manager import FormatSelectionManager
        manager = FormatSelectionManager()
        
        # Add many format configurations
        for i in range(100):
            field_selection = {f'field_{i}': True for i in range(50)}
            manager.select_format("json", field_selection=field_selection)
            manager.deselect_format("json")
        
        # Should not consume excessive memory
        import sys
        manager_size = sys.getsizeof(manager)
        assert manager_size < 10000  # Reasonable size limit