"""Setup validation tests for RAG_Scraper project."""
import sys
import os

def test_python_version():
    """Verify Python version is 3.9+"""
    assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version_info}"

def test_project_structure():
    """Verify project directory structure exists"""
    required_dirs = [
        'src',
        'src/scraper',
        'src/web_interface', 
        'src/file_generator',
        'src/config',
        'tests',
        'tests/features',
        'tests/step_definitions',
        'tests/unit',
        'tests/test_data'
    ]
    
    for directory in required_dirs:
        assert os.path.exists(directory), f"Required directory missing: {directory}"

def test_dependencies_importable():
    """Verify key dependencies can be imported"""
    try:
        import flask
        import pytest
        import requests
        import bs4
        import pytest_bdd
        assert True
    except ImportError as e:
        assert False, f"Failed to import required dependency: {e}"
