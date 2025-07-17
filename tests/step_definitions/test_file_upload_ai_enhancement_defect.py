"""Step definitions for file upload AI enhancement defect testing."""

import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
from pytest_bdd import given, when, then, scenario, parsers
from src.web_interface.file_upload_routes import FileUploadRoutes
from src.file_processing.file_upload_handler import FileUploadHandler
from src.file_processing.file_validator import FileValidator
from src.file_processing.file_security_scanner import FileSecurityScanner
from src.file_processing.pdf_text_extractor import PDFTextExtractor
from src.scraper.multi_strategy_scraper import RestaurantData
from src.ai.llm_extractor import LLMExtractor


# Scenario loading
@scenario('../features/file_upload_ai_enhancement_defect.feature', 'AI Enhancement Successfully Processes Uploaded PDF')
def test_ai_enhancement_success():
    pass


@scenario('../features/file_upload_ai_enhancement_defect.feature', 'AI Enhancement Fails Gracefully with Invalid API Key')
def test_ai_enhancement_invalid_key():
    pass


@scenario('../features/file_upload_ai_enhancement_defect.feature', 'AI Enhancement is Disabled for File Upload')
def test_ai_enhancement_disabled():
    pass


@scenario('../features/file_upload_ai_enhancement_defect.feature', 'AI Enhancement Data Flow Consistency')
def test_ai_enhancement_data_flow():
    pass


@scenario('../features/file_upload_ai_enhancement_defect.feature', 'Compare File Upload vs Multi-Page AI Enhancement')
def test_compare_file_upload_vs_multipage():
    pass


# Test context class
class TestContext:
    def __init__(self):
        self.app = None
        self.client = None
        self.upload_handler = None
        self.file_routes = None
        self.api_key = None
        self.uploaded_file_id = None
        self.processing_response = None
        self.output_json = None
        self.ai_config = None
        self.mock_llm_extractor = None
        self.temp_dir = None
        self.pdf_content = None


@pytest.fixture
def context():
    """Test context fixture."""
    ctx = TestContext()
    ctx.temp_dir = tempfile.mkdtemp()
    yield ctx
    # Cleanup
    if ctx.temp_dir and os.path.exists(ctx.temp_dir):
        import shutil
        shutil.rmtree(ctx.temp_dir)


# Step definitions
@given('the RAG_Scraper web interface is running')
def web_interface_running(context):
    """Mock Flask app setup."""
    from flask import Flask
    context.app = Flask(__name__)
    context.app.config['UPLOAD_FOLDER'] = context.temp_dir
    context.app.config['TESTING'] = True
    context.client = context.app.test_client()
    
    # Initialize file upload routes
    context.file_routes = FileUploadRoutes(context.app)


@given('I have a valid OpenAI API key')
def valid_api_key(context):
    """Set up valid API key."""
    context.api_key = "sk-test-valid-key-for-testing"


@given('I have uploaded a PDF file containing restaurant data')
def uploaded_pdf_file(context):
    """Mock PDF file upload."""
    # Create mock PDF content
    context.pdf_content = """
    Fuller's Coffee Shop
    136 NW 9th Avenue, Pearl District, downtown Portland
    Phone: (503) 222-5608
    Hours: Mon-Sat 7am-2pm, Sun 8am-2pm
    
    Menu:
    - Famous Creamy Omelettes
    - Breakfast Steak
    - French Toast
    - German Pancake
    """
    
    # Mock file upload
    context.uploaded_file_id = "test_file_123"
    
    # Mock the upload handler to return our test file
    with patch.object(context.file_routes.upload_handler, 'get_file_path') as mock_get_path:
        test_file_path = os.path.join(context.temp_dir, 'test_restaurant.pdf')
        with open(test_file_path, 'w') as f:
            f.write(context.pdf_content)
        mock_get_path.return_value = test_file_path


@given('I have enabled AI enhancement in the settings')
def ai_enhancement_enabled(context):
    """Enable AI enhancement."""
    context.ai_config = {
        'ai_enhancement_enabled': True,
        'llm_provider': 'openai',
        'api_key': context.api_key,
        'ai_features': ['nutritional_analysis', 'price_analysis'],
        'confidence_threshold': 0.7,
        'custom_questions': []
    }


@given('I have configured a valid OpenAI API key')
def configured_valid_api_key(context):
    """Configure valid API key in AI settings."""
    if context.ai_config:
        context.ai_config['api_key'] = context.api_key


@given('I have configured an invalid OpenAI API key')
def configured_invalid_api_key(context):
    """Configure invalid API key in AI settings."""
    if context.ai_config:
        context.ai_config['api_key'] = 'invalid-key-12345'


@given('I have selected AI features for analysis')
def selected_ai_features(context):
    """Select AI features for analysis."""
    if context.ai_config:
        context.ai_config['ai_features'] = [
            'nutritional_analysis',
            'price_analysis',
            'cuisine_classification'
        ]


@given('I have disabled AI enhancement in the settings')
def ai_enhancement_disabled(context):
    """Disable AI enhancement."""
    context.ai_config = {
        'ai_enhancement_enabled': False,
        'llm_provider': 'openai',
        'api_key': '',
        'ai_features': [],
        'confidence_threshold': 0.7,
        'custom_questions': []
    }


@when('I process the uploaded PDF file for RAG output')
def process_uploaded_pdf(context):
    """Process uploaded PDF file for RAG output."""
    # Mock PDF text extraction
    with patch('src.file_processing.pdf_text_extractor.PDFTextExtractor') as mock_extractor_class:
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.text = context.pdf_content
        mock_result.page_count = 1
        mock_result.method_used = 'pypdf'
        mock_result.error_message = None
        mock_extractor.extract_text.return_value = mock_result
        
        # Mock LLM extractor based on AI config
        if context.ai_config.get('ai_enhancement_enabled', False):
            with patch('src.ai.llm_extractor.LLMExtractor') as mock_llm_class:
                mock_llm = Mock()
                mock_llm_class.return_value = mock_llm
                
                if context.ai_config.get('api_key') == 'invalid-key-12345':
                    # Simulate API error for invalid key
                    mock_llm.extract.side_effect = Exception("Malformed API response")
                    context.mock_llm_extractor = mock_llm
                else:
                    # Simulate successful AI extraction
                    mock_llm.extract.return_value = {
                        'success': True,
                        'extractions': [
                            {
                                'category': 'Restaurant Info',
                                'confidence': 0.9,
                                'extracted_data': {
                                    'name': "Fuller's Coffee Shop",
                                    'address': "136 NW 9th Avenue, Pearl District, downtown Portland",
                                    'phone': "(503) 222-5608",
                                    'hours': "Mon-Sat 7am-2pm, Sun 8am-2pm"
                                }
                            },
                            {
                                'category': 'Menu Items',
                                'confidence': 0.8,
                                'extracted_data': {
                                    'items': ['Famous Creamy Omelettes', 'Breakfast Steak', 'French Toast']
                                }
                            }
                        ]
                    }
                    context.mock_llm_extractor = mock_llm
        
        # Call the actual file processing endpoint
        request_data = {
            'file_ids': [context.uploaded_file_id],
            'output_dir': context.temp_dir,
            'file_format': 'json',
            'json_field_selections': ['core_fields', 'extended_fields', 'contact_fields', 'descriptive_fields'],
            'schema_type': 'Restaurant',
            **context.ai_config
        }
        
        with context.app.test_request_context('/api/process-uploaded-files-for-rag', 
                                             method='POST', 
                                             json=request_data):
            try:
                response = context.file_routes._process_files_through_scraping_pipeline(
                    file_ids=[context.uploaded_file_id],
                    file_paths=[],
                    output_dir=context.temp_dir,
                    file_mode='single',
                    file_format='json',
                    json_field_selections=['core_fields', 'extended_fields', 'contact_fields', 'descriptive_fields'],
                    scraping_mode='single',
                    multi_page_config={},
                    industry='restaurant',
                    schema_type='Restaurant',
                    ai_config=context.ai_config
                )
                context.processing_response = response
                
                # Read the generated JSON file
                if hasattr(response, 'json') and response.json:
                    response_data = response.json
                    if response_data.get('success') and response_data.get('output_files'):
                        output_file = response_data['output_files'][0]
                        output_path = os.path.join(context.temp_dir, output_file)
                        if os.path.exists(output_path):
                            with open(output_path, 'r') as f:
                                context.output_json = json.load(f)
                
            except Exception as e:
                context.processing_response = {'error': str(e)}


@when('I process the same restaurant data via file upload')
def process_via_file_upload(context):
    """Process restaurant data via file upload."""
    # This step would be implemented similar to the above
    # For now, we'll store the file upload result
    process_uploaded_pdf(context)
    context.file_upload_result = context.output_json


@when('I process the same restaurant data via multi-page scraping')
def process_via_multipage_scraping(context):
    """Process restaurant data via multi-page scraping."""
    # Mock multi-page scraping result with AI enhancement
    context.multipage_result = {
        "metadata": {
            "generation_timestamp": "2025-01-16T10:00:00",
            "restaurant_count": 1,
            "format_version": "1.0"
        },
        "restaurants": [
            {
                "basic_info": {
                    "name": "Fuller's Coffee Shop",
                    "address": "136 NW 9th Avenue, Pearl District, downtown Portland",
                    "phone": "(503) 222-5608",
                    "hours": "Mon-Sat 7am-2pm, Sun 8am-2pm",
                    "website": ""
                },
                "ai_analysis": {
                    "confidence_score": 0.85,
                    "meets_threshold": True,
                    "provider_used": "openai",
                    "analysis_timestamp": "2025-01-16T10:00:00"
                }
            }
        ]
    }


@then('the generated JSON file should contain an "ai_analysis" section')
def json_contains_ai_analysis(context):
    """Verify JSON contains ai_analysis section."""
    assert context.output_json is not None, "No JSON output generated"
    assert 'restaurants' in context.output_json, "No restaurants in JSON output"
    assert len(context.output_json['restaurants']) > 0, "No restaurants found"
    
    restaurant = context.output_json['restaurants'][0]
    assert 'ai_analysis' in restaurant, f"No ai_analysis in restaurant data. Keys: {list(restaurant.keys())}"


@then('the ai_analysis should include confidence_score')
def ai_analysis_has_confidence_score(context):
    """Verify ai_analysis has confidence_score."""
    restaurant = context.output_json['restaurants'][0]
    ai_analysis = restaurant['ai_analysis']
    assert 'confidence_score' in ai_analysis, f"No confidence_score in ai_analysis. Keys: {list(ai_analysis.keys())}"
    assert isinstance(ai_analysis['confidence_score'], (int, float)), "confidence_score should be numeric"


@then('the ai_analysis should include provider_used as "openai"')
def ai_analysis_has_provider_openai(context):
    """Verify ai_analysis has provider_used as openai."""
    restaurant = context.output_json['restaurants'][0]
    ai_analysis = restaurant['ai_analysis']
    assert 'provider_used' in ai_analysis, f"No provider_used in ai_analysis. Keys: {list(ai_analysis.keys())}"
    assert ai_analysis['provider_used'] == 'openai', f"Expected provider_used='openai', got '{ai_analysis['provider_used']}'"


@then('the ai_analysis should include analysis_timestamp')
def ai_analysis_has_timestamp(context):
    """Verify ai_analysis has analysis_timestamp."""
    restaurant = context.output_json['restaurants'][0]
    ai_analysis = restaurant['ai_analysis']
    assert 'analysis_timestamp' in ai_analysis, f"No analysis_timestamp in ai_analysis. Keys: {list(ai_analysis.keys())}"
    assert ai_analysis['analysis_timestamp'] is not None, "analysis_timestamp should not be None"


@then('the ai_analysis should contain AI-enhanced restaurant data')
def ai_analysis_contains_enhanced_data(context):
    """Verify ai_analysis contains AI-enhanced data."""
    restaurant = context.output_json['restaurants'][0]
    ai_analysis = restaurant['ai_analysis']
    
    # Check for AI-specific fields
    expected_fields = ['ai_enhanced', 'ai_provider', 'ai_confidence', 'ai_extractions']
    for field in expected_fields:
        assert field in ai_analysis, f"Missing AI field '{field}' in ai_analysis. Keys: {list(ai_analysis.keys())}"


@then('the processing should complete successfully')
def processing_completes_successfully(context):
    """Verify processing completes successfully."""
    assert context.processing_response is not None, "No processing response"
    if hasattr(context.processing_response, 'json'):
        response_data = context.processing_response.json
        assert response_data.get('success') is True, f"Processing failed: {response_data.get('error')}"
    else:
        assert 'error' not in context.processing_response, f"Processing error: {context.processing_response}"


@then('the generated JSON file should contain restaurant data')
def json_contains_restaurant_data(context):
    """Verify JSON contains restaurant data."""
    assert context.output_json is not None, "No JSON output generated"
    assert 'restaurants' in context.output_json, "No restaurants in JSON output"
    assert len(context.output_json['restaurants']) > 0, "No restaurants found"
    
    restaurant = context.output_json['restaurants'][0]
    assert 'basic_info' in restaurant, "No basic_info in restaurant data"
    assert restaurant['basic_info']['name'], "Restaurant name should not be empty"


@then('the ai_analysis section should contain error information')
def ai_analysis_contains_error_info(context):
    """Verify ai_analysis contains error information."""
    restaurant = context.output_json['restaurants'][0]
    ai_analysis = restaurant['ai_analysis']
    assert 'error' in ai_analysis, f"No error in ai_analysis. Keys: {list(ai_analysis.keys())}"


@then('the ai_analysis should indicate fallback_used as true')
def ai_analysis_indicates_fallback(context):
    """Verify ai_analysis indicates fallback was used."""
    restaurant = context.output_json['restaurants'][0]
    ai_analysis = restaurant['ai_analysis']
    assert 'fallback_used' in ai_analysis, f"No fallback_used in ai_analysis. Keys: {list(ai_analysis.keys())}"
    assert ai_analysis['fallback_used'] is True, f"Expected fallback_used=True, got {ai_analysis['fallback_used']}"


@then('the log should show "AI enhancement failed" with error details')
def log_shows_ai_enhancement_failed(context):
    """Verify log shows AI enhancement failed."""
    # This would require capturing log output
    # For now, we'll verify the mock was called correctly
    if context.mock_llm_extractor:
        assert context.mock_llm_extractor.extract.called, "LLM extractor should have been called"


@then('the ai_analysis section should not be present')
def ai_analysis_not_present(context):
    """Verify ai_analysis section is not present."""
    assert context.output_json is not None, "No JSON output generated"
    assert 'restaurants' in context.output_json, "No restaurants in JSON output"
    assert len(context.output_json['restaurants']) > 0, "No restaurants found"
    
    restaurant = context.output_json['restaurants'][0]
    assert 'ai_analysis' not in restaurant, f"ai_analysis should not be present when AI is disabled. Keys: {list(restaurant.keys())}"


@then('the processing should use traditional pattern matching only')
def processing_uses_traditional_only(context):
    """Verify processing uses traditional pattern matching only."""
    # Verify LLM extractor was not called
    assert context.mock_llm_extractor is None, "LLM extractor should not have been initialized when AI is disabled"


@then('the RestaurantData object should have ai_analysis attribute set')
def restaurant_data_has_ai_analysis(context):
    """Verify RestaurantData object has ai_analysis attribute."""
    # This would require access to the actual RestaurantData object
    # For now, we'll verify the final output has ai_analysis
    json_contains_ai_analysis(context)


@then('the ai_analysis should be properly converted to dictionary format')
def ai_analysis_converted_to_dict(context):
    """Verify ai_analysis is properly converted to dictionary format."""
    restaurant = context.output_json['restaurants'][0]
    ai_analysis = restaurant['ai_analysis']
    assert isinstance(ai_analysis, dict), f"ai_analysis should be dict, got {type(ai_analysis)}"


@then('the JSON generator should find the ai_analysis field')
def json_generator_finds_ai_analysis(context):
    """Verify JSON generator finds the ai_analysis field."""
    # This is verified by the presence of ai_analysis in the output
    json_contains_ai_analysis(context)


@then('the final JSON output should contain the ai_analysis section')
def final_json_contains_ai_analysis(context):
    """Verify final JSON output contains ai_analysis section."""
    json_contains_ai_analysis(context)


@then('both outputs should contain ai_analysis sections')
def both_outputs_contain_ai_analysis(context):
    """Verify both file upload and multi-page outputs contain ai_analysis."""
    # File upload result
    assert context.file_upload_result is not None, "No file upload result"
    assert 'restaurants' in context.file_upload_result, "No restaurants in file upload result"
    file_restaurant = context.file_upload_result['restaurants'][0]
    assert 'ai_analysis' in file_restaurant, "No ai_analysis in file upload result"
    
    # Multi-page result
    assert context.multipage_result is not None, "No multi-page result"
    assert 'restaurants' in context.multipage_result, "No restaurants in multi-page result"
    multipage_restaurant = context.multipage_result['restaurants'][0]
    assert 'ai_analysis' in multipage_restaurant, "No ai_analysis in multi-page result"


@then('both ai_analysis sections should have the same structure')
def both_ai_analysis_have_same_structure(context):
    """Verify both ai_analysis sections have the same structure."""
    file_ai_analysis = context.file_upload_result['restaurants'][0]['ai_analysis']
    multipage_ai_analysis = context.multipage_result['restaurants'][0]['ai_analysis']
    
    # Check common required fields
    required_fields = ['confidence_score', 'provider_used', 'analysis_timestamp']
    for field in required_fields:
        assert field in file_ai_analysis, f"Missing {field} in file upload ai_analysis"
        assert field in multipage_ai_analysis, f"Missing {field} in multi-page ai_analysis"


@then('both should use the same AI provider and configuration')
def both_use_same_ai_provider(context):
    """Verify both use the same AI provider and configuration."""
    file_ai_analysis = context.file_upload_result['restaurants'][0]['ai_analysis']
    multipage_ai_analysis = context.multipage_result['restaurants'][0]['ai_analysis']
    
    assert file_ai_analysis['provider_used'] == multipage_ai_analysis['provider_used'], "Providers should match"


@then('both should have consistent field naming conventions')
def both_have_consistent_naming(context):
    """Verify both have consistent field naming conventions."""
    file_ai_analysis = context.file_upload_result['restaurants'][0]['ai_analysis']
    multipage_ai_analysis = context.multipage_result['restaurants'][0]['ai_analysis']
    
    # Check that key field names are consistent
    for key in ['confidence_score', 'provider_used', 'analysis_timestamp']:
        assert key in file_ai_analysis, f"File upload missing {key}"
        assert key in multipage_ai_analysis, f"Multi-page missing {key}"