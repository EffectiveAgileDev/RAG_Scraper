"""Test for toggle functionality fix."""

import pytest


class TestToggleFunctionalityFix:
    """Test that toggle functionality works correctly."""
    
    def test_toggle_javascript_has_unique_function_name(self):
        """Test that toggle function has a unique name to avoid conflicts."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        ui = FileUploadUI()
        html = ui.render()
        
        # Should have a unique function name to avoid conflicts
        assert "function toggleFileUploadMode(" in html or "window.toggleFileUploadMode" in html
        
    def test_toggle_uses_proper_event_handlers(self):
        """Test that toggle uses proper event handlers."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        ui = FileUploadUI()
        html = ui.render()
        
        # Should use onchange with the correct function name
        assert 'onchange="toggleFileUploadMode(' in html or 'onchange="window.toggleFileUploadMode(' in html
        
    def test_toggle_function_is_globally_accessible(self):
        """Test that toggle function is attached to window object."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        ui = FileUploadUI()
        html = ui.render()
        
        # Function should be attached to window for global access
        assert "window.toggleFileUploadMode" in html
        
    def test_toggle_handles_missing_elements_gracefully(self):
        """Test that toggle handles missing elements gracefully."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        ui = FileUploadUI()
        html = ui.render()
        
        # Should check if elements exist before manipulating
        assert "urlContainer && fileContainer" in html
        assert "if (urlsInput)" in html