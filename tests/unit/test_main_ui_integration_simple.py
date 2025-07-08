"""Simple unit tests for main UI integration without Flask dependencies."""

import pytest


class TestMainUIIntegrationSimple:
    """Simple tests for main UI integration."""

    def test_file_upload_ui_can_be_imported(self):
        """Test that FileUploadUI can be imported."""
        from src.web_interface.file_upload_ui import FileUploadUI
        ui = FileUploadUI()
        assert ui is not None

    def test_file_upload_ui_renders_html(self):
        """Test that FileUploadUI renders HTML content."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        ui = FileUploadUI()
        html = ui.render()
        
        assert html is not None
        assert len(html) > 0
        assert "file-upload" in html
        assert "input-mode-toggle" in html
        assert "URL Mode" in html
        assert "File Upload Mode" in html

    def test_file_upload_ui_includes_javascript(self):
        """Test that FileUploadUI includes necessary JavaScript."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        ui = FileUploadUI()
        html = ui.render()
        
        assert "toggleInputMode" in html
        assert "handleDragOver" in html
        assert "handleDrop" in html
        assert "processFiles" in html

    def test_file_upload_ui_includes_css(self):
        """Test that FileUploadUI includes necessary CSS."""
        from src.web_interface.file_upload_ui import FileUploadUI
        
        ui = FileUploadUI()
        html = ui.render()
        
        assert ".file-upload-area" in html
        assert "input-mode-toggle" in html  # CSS selector in style block
        assert ".upload-queue" in html

    def test_main_routes_has_file_upload_import(self):
        """Test that main routes imports FileUploadUI."""
        import inspect
        from src.web_interface.routes import main_routes
        
        source = inspect.getsource(main_routes)
        assert "from src.web_interface.file_upload_ui import FileUploadUI" in source

    def test_main_routes_creates_file_upload_ui(self):
        """Test that main routes creates FileUploadUI instance."""
        import inspect
        from src.web_interface.routes import main_routes
        
        source = inspect.getsource(main_routes.index)
        assert "FileUploadUI()" in source
        assert "file_upload_ui =" in source

    def test_main_routes_passes_file_upload_to_template(self):
        """Test that main routes passes file upload UI to template."""
        import inspect
        from src.web_interface.routes import main_routes
        
        source = inspect.getsource(main_routes.index)
        assert "file_upload_ui=" in source or "file_upload_ui =" in source

    def test_app_factory_imports_file_upload_routes(self):
        """Test that app factory imports file upload route registration."""
        import inspect
        from src.web_interface import app_factory
        
        source = inspect.getsource(app_factory)
        assert "from src.web_interface.file_upload_routes import register_file_upload_routes" in source

    def test_app_factory_registers_file_upload_routes(self):
        """Test that app factory calls file upload route registration."""
        import inspect
        from src.web_interface import app_factory
        
        source = inspect.getsource(app_factory.create_app)
        assert "register_file_upload_routes(app)" in source

    def test_file_upload_routes_has_register_function(self):
        """Test that file upload routes has register function."""
        from src.web_interface.file_upload_routes import register_file_upload_routes
        
        assert register_file_upload_routes is not None
        assert callable(register_file_upload_routes)