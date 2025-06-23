"""Unit tests for application configuration module."""
import pytest
import os
from unittest.mock import patch, MagicMock


class TestAppConfig:
    """Test application configuration for web server settings."""

    def test_default_port_configuration(self):
        """Test that default port is not 8080 (should be different for multi-page version)."""
        from src.config.app_config import AppConfig

        config = AppConfig()
        assert config.port != 8080
        assert isinstance(config.port, int)
        assert 1024 <= config.port <= 65535  # Valid port range

    def test_default_host_configuration(self):
        """Test default host configuration."""
        from src.config.app_config import AppConfig

        config = AppConfig()
        assert config.host in ["127.0.0.1", "localhost", "0.0.0.0"]

    def test_default_debug_configuration(self):
        """Test default debug mode configuration."""
        from src.config.app_config import AppConfig

        config = AppConfig()
        assert isinstance(config.debug, bool)

    def test_port_from_environment_variable(self):
        """Test port configuration from environment variable."""
        with patch.dict(os.environ, {"RAG_SCRAPER_PORT": "8090"}):
            from src.config.app_config import AppConfig

            config = AppConfig()
            assert config.port == 8090

    def test_invalid_port_from_environment(self):
        """Test handling of invalid port from environment variable."""
        with patch.dict(os.environ, {"RAG_SCRAPER_PORT": "invalid"}):
            from src.config.app_config import AppConfig

            config = AppConfig()
            # Should fall back to default port (not 8080)
            assert config.port != 8080
            assert isinstance(config.port, int)

    def test_port_out_of_range(self):
        """Test handling of port outside valid range."""
        with patch.dict(os.environ, {"RAG_SCRAPER_PORT": "70000"}):
            from src.config.app_config import AppConfig

            with pytest.raises(ValueError, match="Port must be between"):
                config = AppConfig()

    def test_host_from_environment_variable(self):
        """Test host configuration from environment variable."""
        with patch.dict(os.environ, {"RAG_SCRAPER_HOST": "0.0.0.0"}):
            from src.config.app_config import AppConfig

            config = AppConfig()
            assert config.host == "0.0.0.0"

    def test_debug_from_environment_variable(self):
        """Test debug configuration from environment variable."""
        with patch.dict(os.environ, {"RAG_SCRAPER_DEBUG": "true"}):
            from src.config.app_config import AppConfig

            config = AppConfig()
            assert config.debug is True

        with patch.dict(os.environ, {"RAG_SCRAPER_DEBUG": "false"}):
            from src.config.app_config import AppConfig

            config = AppConfig()
            assert config.debug is False

    def test_custom_configuration(self):
        """Test creating configuration with custom values."""
        from src.config.app_config import AppConfig

        config = AppConfig(port=9000, host="0.0.0.0", debug=True)
        assert config.port == 9000
        assert config.host == "0.0.0.0"
        assert config.debug is True

    def test_configuration_to_dict(self):
        """Test converting configuration to dictionary."""
        from src.config.app_config import AppConfig

        config = AppConfig(port=8085, host="localhost", debug=False)
        config_dict = config.to_dict()

        assert config_dict["port"] == 8085
        assert config_dict["host"] == "localhost"
        assert config_dict["debug"] is False

    def test_configuration_string_representation(self):
        """Test string representation of configuration."""
        from src.config.app_config import AppConfig

        config = AppConfig(port=8085, host="localhost", debug=False)
        config_str = str(config)

        assert "8085" in config_str
        assert "localhost" in config_str

    def test_get_server_url(self):
        """Test getting the full server URL."""
        from src.config.app_config import AppConfig

        config = AppConfig(port=8085, host="localhost")
        assert config.get_server_url() == "http://localhost:8085"

        config = AppConfig(port=8090, host="0.0.0.0")
        assert config.get_server_url() == "http://0.0.0.0:8090"

    def test_singleton_pattern(self):
        """Test that AppConfig can be used as a singleton."""
        from src.config.app_config import get_app_config

        config1 = get_app_config()
        config2 = get_app_config()

        assert config1 is config2
        assert config1.port == config2.port

    def test_reset_singleton(self):
        """Test resetting the singleton instance."""
        from src.config.app_config import get_app_config, reset_app_config

        config1 = get_app_config()
        reset_app_config()
        config2 = get_app_config()

        assert config1 is not config2
