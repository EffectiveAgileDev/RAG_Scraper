"""Pytest configuration and shared fixtures for RAG_Scraper tests."""
import sys
import os
from pathlib import Path

# Add the project root directory to Python path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment with proper Python path."""
    # Ensure src module can be imported
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set environment variable for testing
    os.environ["TESTING"] = "1"
    
    yield
    
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def project_root_path():
    """Provide project root path for tests that need it."""
    return project_root


@pytest.fixture
def test_data_dir():
    """Provide test data directory path."""
    return project_root / "tests" / "test_data"


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide temporary directory for test output files."""
    return tmp_path / "output"