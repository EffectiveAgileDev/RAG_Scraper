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


@pytest.fixture
def mock_flask_app():
    """Mock Flask app for web interface tests."""
    from unittest.mock import Mock
    app = Mock()
    app.config = {"TESTING": True}
    return app


@pytest.fixture
def client():
    """Create Flask test client for acceptance tests."""
    from src.web_interface.app import create_app
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def progress_context():
    """Provide progress context for tracking test state."""
    return {}


@pytest.fixture
def queue_context():
    """Provide queue context for tracking test state."""
    return {}


# RestW-specific fixtures
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class MockWebContext:
    """Mock web context for testing."""
    current_page: str = 'main'
    form_data: Dict[str, Any] = None
    extraction_performed: bool = False
    
    def __post_init__(self):
        if self.form_data is None:
            self.form_data = {}


@dataclass
class MockExtractionResult:
    """Mock extraction result for testing."""
    success: bool = True
    schema_type: str = 'RestW'
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {
                'location': {
                    'street_address': '123 Main St',
                    'city': 'Anytown',
                    'state': 'CA',
                    'zip_code': '12345'
                },
                'menu_items': [
                    {'item_name': 'Pizza', 'price': '$10', 'category': 'Main'},
                    {'item_name': 'Salad', 'price': '$8', 'category': 'Appetizer'}
                ],
                'services_offered': {
                    'delivery_available': True,
                    'takeout_available': True,
                    'catering_available': False
                },
                'contact_info': {
                    'primary_phone': '(555) 123-4567',
                    'secondary_phone': ''
                },
                'web_links': {
                    'official_website': 'https://example-restaurant.com',
                    'menu_pdf_url': 'https://example-restaurant.com/menu.pdf'
                }
            }


@pytest.fixture
def mock_web_context():
    """Fixture for mock web context."""
    return MockWebContext()


@pytest.fixture
def mock_extraction_result():
    """Fixture for mock extraction result."""
    return MockExtractionResult()


@pytest.fixture
def mock_wteg_data():
    """Fixture for mock WTEG data."""
    return {
        'location': {
            'street_address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345',
            'neighborhood': 'Downtown'
        },
        'menu_items': [
            {
                'item_name': 'Margherita Pizza',
                'description': 'Fresh mozzarella, tomatoes, basil',
                'price': '$12.99',
                'category': 'Pizza'
            },
            {
                'item_name': 'Caesar Salad',
                'description': 'Romaine lettuce, parmesan, croutons',
                'price': '$8.99',
                'category': 'Salads'
            }
        ],
        'services_offered': {
            'delivery_available': True,
            'takeout_available': True,
            'catering_available': False,
            'reservations_accepted': True,
            'online_ordering': True
        },
        'contact_info': {
            'primary_phone': '(555) 123-4567',
            'secondary_phone': '',
            'formatted_display': '(555) 123-4567',
            'clickable_link': 'tel:5551234567'
        },
        'web_links': {
            'official_website': 'https://example-restaurant.com',
            'menu_pdf_url': 'https://example-restaurant.com/menu.pdf',
            'social_media_links': [
                'https://facebook.com/example-restaurant',
                'https://instagram.com/example-restaurant'
            ]
        }
    }


# Mock classes for testing
class MockRestWProcessor:
    """Mock RestW processor for testing."""
    
    def __init__(self, schema_type='RestW'):
        self.schema_type = schema_type
        self.obfuscate_terminology = True
    
    def process_url(self, url, options=None):
        """Mock URL processing."""
        return {
            'success': True,
            'data': {
                'location': {'street_address': '123 Main St'},
                'menu_items': [{'item_name': 'Pizza'}]
            }
        }
    
    def process_pdf(self, pdf_path, options=None):
        """Mock PDF processing."""
        return {
            'success': True,
            'data': {
                'menu_items': [{'item_name': 'Pizza', 'price': '$10'}]
            }
        }
    
    def uses_wteg_schema(self):
        """Mock WTEG schema check."""
        return True
    
    def validate_restw_output(self, output):
        """Mock output validation."""
        return 'location' in output or 'menu_items' in output


@pytest.fixture
def mock_restw_processor():
    """Fixture for mock RestW processor."""
    return MockRestWProcessor()
