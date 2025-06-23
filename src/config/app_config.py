"""Application configuration for RAG_Scraper web server."""
import os
from typing import Optional, Dict, Any


class AppConfig:
    """Configuration for the Flask web application."""

    def __init__(
        self, 
        port: Optional[int] = None, 
        host: Optional[str] = None, 
        debug: Optional[bool] = None
    ):
        """Initialize application configuration.
        
        Args:
            port: Server port number (defaults to 8085 for multi-page version)
            host: Server host address (defaults to localhost)
            debug: Debug mode flag (defaults to False)
        """
        # Set port - default to 8085 for multi-page version to avoid conflict with 8080
        if port is not None:
            self.port = port
        else:
            env_port = os.environ.get("RAG_SCRAPER_PORT", "8085")
            try:
                self.port = int(env_port)
            except ValueError:
                self.port = 8085  # Default for multi-page version
        
        # Validate port range
        if not (1024 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1024 and 65535, got {self.port}")
        
        # Set host
        if host is not None:
            self.host = host
        else:
            self.host = os.environ.get("RAG_SCRAPER_HOST", "localhost")
        
        # Set debug mode
        if debug is not None:
            self.debug = debug
        else:
            debug_env = os.environ.get("RAG_SCRAPER_DEBUG", "false").lower()
            self.debug = debug_env in ["true", "1", "yes", "on"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "port": self.port,
            "host": self.host,
            "debug": self.debug
        }

    def get_server_url(self) -> str:
        """Get the full server URL."""
        return f"http://{self.host}:{self.port}"

    def __str__(self) -> str:
        """String representation of configuration."""
        return f"AppConfig(port={self.port}, host={self.host}, debug={self.debug})"

    def __repr__(self) -> str:
        """Detailed representation of configuration."""
        return self.__str__()


# Singleton instance
_app_config: Optional[AppConfig] = None


def get_app_config() -> AppConfig:
    """Get the singleton application configuration instance."""
    global _app_config
    if _app_config is None:
        _app_config = AppConfig()
    return _app_config


def reset_app_config() -> None:
    """Reset the singleton instance (mainly for testing)."""
    global _app_config
    _app_config = None