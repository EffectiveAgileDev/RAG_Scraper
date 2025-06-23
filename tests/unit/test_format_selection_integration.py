"""
Integration tests for FormatSelectionManager with file generator service.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.file_generator.format_selection_manager import FormatSelectionManager
from src.scraper.multi_strategy_scraper import RestaurantData


class TestFormatSelectionIntegration:
    """Test integration functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_data = [
            RestaurantData(
                name="Integration Test Restaurant",
                address="456 Integration Ave",
                phone="(555) 555-0001",
                hours="Daily: 10AM-10PM",
                cuisine="Integration",
            )
        ]

    def test_file_generation_request_with_format_manager(self):
        """Test FileGenerationRequest can accept format manager."""
        # Mock the import to avoid reportlab dependency
        with patch.dict(
            "sys.modules",
            {
                "src.file_generator.pdf_generator": Mock(),
                "reportlab": Mock(),
                "reportlab.lib": Mock(),
                "reportlab.lib.pagesizes": Mock(),
                "reportlab.platypus": Mock(),
                "reportlab.lib.styles": Mock(),
                "reportlab.lib.units": Mock(),
            },
        ):
            from src.file_generator.file_generator_service import FileGenerationRequest

            # Create format selection manager
            format_manager = FormatSelectionManager()
            format_manager.select_format("json", field_selection={"core_fields": True})

            # Create enhanced file generation request
            request = FileGenerationRequest(
                restaurant_data=self.sample_data,
                file_format="json",
                output_directory="/tmp",
                format_manager=format_manager,
            )

            # Should use format manager for configuration
            assert request.format_manager is not None
            assert request.format_manager.get_selected_formats() == ["json"]

    def test_format_manager_field_selection_override(self):
        """Test that format manager overrides field_selection parameter."""
        with patch.dict(
            "sys.modules",
            {
                "src.file_generator.pdf_generator": Mock(),
                "reportlab": Mock(),
                "reportlab.lib": Mock(),
                "reportlab.lib.pagesizes": Mock(),
                "reportlab.platypus": Mock(),
                "reportlab.lib.styles": Mock(),
                "reportlab.lib.units": Mock(),
            },
        ):
            from src.file_generator.file_generator_service import (
                FileGenerationRequest,
                FileGeneratorService,
            )

            format_manager = FormatSelectionManager()
            format_manager.select_format("json", field_selection={"core_fields": True})

            # Create request with both format_manager and field_selection
            request = FileGenerationRequest(
                restaurant_data=self.sample_data,
                file_format="json",
                field_selection={"core_fields": False},  # Should be overridden
                format_manager=format_manager,
            )

            # Mock the file generator service
            service = FileGeneratorService()

            # Mock the _generate_json_file method
            with patch.object(service, "_generate_json_file") as mock_json_gen:
                mock_json_gen.return_value = {
                    "success": True,
                    "file_path": "/tmp/test.json",
                    "restaurant_count": 1,
                }

                # Mock the _generate_with_format_manager method call
                with patch.object(
                    service, "_generate_with_format_manager"
                ) as mock_format_gen:
                    mock_format_gen.return_value = {
                        "success": True,
                        "file_path": "/tmp/test.json",
                        "restaurant_count": 1,
                    }

                    result = service.generate_file(request)

                    # Should call format manager method
                    mock_format_gen.assert_called_once()
                    assert result["success"] is True

    def test_backward_compatibility_without_format_manager(self):
        """Test backward compatibility when format manager is not provided."""
        with patch.dict(
            "sys.modules",
            {
                "src.file_generator.pdf_generator": Mock(),
                "reportlab": Mock(),
                "reportlab.lib": Mock(),
                "reportlab.lib.pagesizes": Mock(),
                "reportlab.platypus": Mock(),
                "reportlab.lib.styles": Mock(),
                "reportlab.lib.units": Mock(),
            },
        ):
            from src.file_generator.file_generator_service import (
                FileGenerationRequest,
                FileGeneratorService,
            )

            request = FileGenerationRequest(
                restaurant_data=self.sample_data,
                file_format="json",
                output_directory="/tmp",
            )

            service = FileGeneratorService()

            # Mock the _generate_json_file method
            with patch.object(service, "_generate_json_file") as mock_json_gen:
                mock_json_gen.return_value = {
                    "success": True,
                    "file_path": "/tmp/test.json",
                    "restaurant_count": 1,
                }

                result = service.generate_file(request)

                # Should work with existing functionality
                assert "success" in result
                mock_json_gen.assert_called_once()

    def test_generate_with_format_manager_method_exists(self):
        """Test that _generate_with_format_manager method exists and works."""
        with patch.dict(
            "sys.modules",
            {
                "src.file_generator.pdf_generator": Mock(),
                "reportlab": Mock(),
                "reportlab.lib": Mock(),
                "reportlab.lib.pagesizes": Mock(),
                "reportlab.platypus": Mock(),
                "reportlab.lib.styles": Mock(),
                "reportlab.lib.units": Mock(),
            },
        ):
            from src.file_generator.file_generator_service import (
                FileGeneratorService,
                FileGenerationRequest,
            )

            service = FileGeneratorService()

            # Should have the method
            assert hasattr(service, "_generate_with_format_manager")

            # Create format manager and request
            format_manager = FormatSelectionManager()
            format_manager.select_format("json", field_selection={"core_fields": True})

            request = FileGenerationRequest(
                restaurant_data=self.sample_data,
                file_format="json",
                format_manager=format_manager,
            )

            # Mock the underlying generation method
            with patch.object(service, "_generate_json_file") as mock_json_gen:
                mock_json_gen.return_value = {
                    "success": True,
                    "file_path": "/tmp/test.json",
                    "restaurant_count": 1,
                }

                result = service._generate_with_format_manager(request, "/tmp")

                assert result["success"] is True
                mock_json_gen.assert_called_once()

                # Verify that field selection was properly passed
                call_args = mock_json_gen.call_args
                enhanced_request = call_args[0][
                    0
                ]  # First argument is the enhanced request
                assert enhanced_request.field_selection == {"core_fields": True}
