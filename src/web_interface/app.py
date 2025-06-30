"""Flask web application for RAG_Scraper."""

from src.web_interface.app_factory import create_app
from src.web_interface.application_state import get_app_state


def get_current_progress():
    """Get current progress for testing."""
    app_state = get_app_state()
    return app_state.current_progress


if __name__ == "__main__":
    from src.config.app_config import get_app_config

    app = create_app()
    config = get_app_config()
    config.host = "0.0.0.0"  # Override default for direct app.py execution

    app.run(host=config.host, port=config.port, debug=config.debug)
