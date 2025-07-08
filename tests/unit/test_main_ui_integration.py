"""Unit tests for main UI integration with file upload components."""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestMainUIIntegration:
    """Test integration of file upload components into main web interface."""

    @pytest.fixture
    def mock_app(self):
        """Create mock Flask app for testing."""
        app = Mock()
        app.config = {"TESTING": True}
        app.url_map = Mock()
        app.url_map.iter_rules.return_value = [
            Mock(rule="/"),
            Mock(rule="/api/upload"),
            Mock(rule="/api/process-files")
        ]
        return app

    @pytest.fixture
    def mock_client(self):
        """Create mock test client."""
        client = Mock()
        response = Mock()
        response.status_code = 200
        response.get_data.return_value = b"<html><body>Original template content</body></html>"
        client.get.return_value = response
        return client

    def test_main_routes_imports_file_upload_ui(self):
        """Test that main routes can import FileUploadUI component."""
        try:
            from src.web_interface.file_upload_ui import FileUploadUI
            ui = FileUploadUI()
            assert ui is not None
            # This test should fail initially because FileUploadUI is not imported in main_routes
        except ImportError:
            pytest.fail("FileUploadUI should be importable for main route integration")

    def test_main_routes_renders_file_upload_component(self):
        """Test that main routes can render file upload component."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        # Create component and render
        ui = FileUploadUI()
        html = ui.render()
        
        # Should generate HTML
        assert html is not None
        assert len(html) > 0
        assert "file-upload" in html

    @patch('src.web_interface.routes.main_routes.render_template')
    def test_main_route_passes_file_upload_to_template(self, mock_render_template):
        """Test that main route passes file upload UI to template."""
        # Mock render_template to capture arguments
        mock_render_template.return_value = "<html>Mock template</html>"
        
        # Import and call the index route function
        from src.web_interface.routes.main_routes import index
        
        result = index()
        
        # Should have called render_template
        mock_render_template.assert_called_once()
        
        # Check if file upload UI was passed to template
        args, kwargs = mock_render_template.call_args
        
        # This test should fail because file upload UI is not yet integrated
        assert 'file_upload_ui' in kwargs, "file_upload_ui should be passed to template"

    def test_main_route_integrates_file_upload_routes(self):
        """Test that file upload routes are registered in app factory."""
        try:
            from src.web_interface.file_upload_routes import register_file_upload_routes
            # This should exist for proper integration
            assert register_file_upload_routes is not None
            # This test should fail because integration is not yet complete
        except ImportError:
            pytest.fail("File upload route registration should be available")

    def test_app_factory_includes_file_upload_routes(self):
        """Test that app factory registers file upload routes."""
        # Check if app_factory imports file upload routes
        import inspect
        from src.web_interface import app_factory
        
        source = inspect.getsource(app_factory.create_app)
        
        # Should include file upload route registration
        # This test should fail because integration is not complete
        assert "file_upload" in source.lower(), "App factory should register file upload routes"

    def test_index_template_supports_file_upload_variables(self):
        """Test that index.html template can accept file upload UI variables."""
        # This test checks template integration capability
        from src.web_interface.routes.main_routes import render_template
        
        # Try to render with file upload UI variable
        try:
            result = render_template('index.html', file_upload_ui="<div>Test UI</div>")
            # If this doesn't fail, template supports the variable
            assert result is not None
        except Exception as e:
            # This should fail because template doesn't expect file_upload_ui yet
            pytest.fail(f"Template should support file_upload_ui variable: {e}")

    def test_main_route_creates_file_upload_ui_instance(self):
        """Test that main route creates FileUploadUI instance."""
        import inspect
        from src.web_interface.routes import main_routes
        
        # Check if main route imports and uses FileUploadUI
        source = inspect.getsource(main_routes.index)
        
        # Should create FileUploadUI instance
        # This test should fail because integration is not complete
        assert "FileUploadUI" in source, "Main route should create FileUploadUI instance"