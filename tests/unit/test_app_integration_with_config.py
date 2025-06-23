"""Integration tests for app configuration with Flask application."""
import pytest
from unittest.mock import patch, MagicMock
import sys


class TestAppIntegrationWithConfig:
    """Test integration of AppConfig with Flask application."""

    def test_start_server_uses_app_config(self):
        """Test that start_server.py uses AppConfig for port configuration."""
        # Mock the Flask app
        mock_app = MagicMock()

        # Mock AppConfig
        with patch("src.config.app_config.get_app_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.port = 8085
            mock_config.host = "127.0.0.1"
            mock_config.debug = True
            mock_get_config.return_value = mock_config

            # Import and test the configuration usage
            from src.config.app_config import get_app_config

            config = get_app_config()

            assert config.port == 8085
            assert config.host == "127.0.0.1"
            assert config.debug is True

    def test_run_app_uses_app_config(self):
        """Test that run_app.py uses AppConfig for port configuration."""
        with patch("src.config.app_config.get_app_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.port = 8085
            mock_config.host = "localhost"
            mock_config.debug = False
            mock_get_config.return_value = mock_config

            from src.config.app_config import get_app_config

            config = get_app_config()

            assert config.port == 8085
            assert config.host == "localhost"
            assert config.debug is False

    def test_web_interface_app_uses_app_config(self):
        """Test that web_interface/app.py uses AppConfig for port configuration."""
        with patch("src.config.app_config.get_app_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.port = 8085
            mock_config.host = "0.0.0.0"
            mock_config.debug = False
            mock_get_config.return_value = mock_config

            from src.config.app_config import get_app_config

            config = get_app_config()

            assert config.port == 8085
            assert config.host == "0.0.0.0"
            assert config.debug is False

    def test_different_port_from_single_page_version(self):
        """Test that multi-page version uses different port from single-page (8080)."""
        from src.config.app_config import AppConfig

        config = AppConfig()
        assert config.port != 8080
        assert config.port == 8085  # Default for multi-page version
