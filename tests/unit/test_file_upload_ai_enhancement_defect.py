"""Unit tests for file upload AI enhancement defect."""

import json
import tempfile
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.web_interface.file_upload_routes import FileUploadRoutes
from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.json_export_generator import JSONExportGenerator
from flask import Flask


class TestFileUploadAIEnhancementDefect:
    """Test class for file upload AI enhancement defect."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = self.temp_dir
        self.app.config['TESTING'] = True
        
        # Initialize file upload routes
        self.file_routes = FileUploadRoutes(self.app)
        
        # Mock PDF content
        self.pdf_content = """
        Fuller's Coffee Shop
        136 NW 9th Avenue, Pearl District, downtown Portland
        Phone: (503) 222-5608
        Hours: Mon-Sat 7am-2pm, Sun 8am-2pm
        
        Menu:
        - Famous Creamy Omelettes
        - Breakfast Steak
        - French Toast
        """
        
        # AI configuration
        self.ai_config = {
            'ai_enhancement_enabled': True,
            'llm_provider': 'openai',
            'api_key': 'sk-test-valid-key',
            'ai_features': ['nutritional_analysis', 'price_analysis'],
            'confidence_threshold': 0.7,
            'custom_questions': []
        }
        
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_restaurant_data_ai_analysis_field_existence(self):
        """Test that RestaurantData object has ai_analysis field when AI is enabled."""
        # Create RestaurantData object
        restaurant = RestaurantData(
            name="Fuller's Coffee Shop",
            address="136 NW 9th Avenue",
            phone="(503) 222-5608",
            hours="Mon-Sat 7am-2pm, Sun 8am-2pm",
            cuisine="American",
            menu_items={"breakfast": ["Omelettes", "French Toast"]},
            confidence="high",
            sources=["test_source"]
        )
        
        # Add AI analysis data
        ai_analysis_data = {
            'confidence_score': 0.85,
            'meets_threshold': True,
            'provider_used': 'openai',
            'confidence_threshold': 0.7,
            'analysis_timestamp': '2025-01-16T10:00:00',
            'ai_enhanced': True,
            'ai_provider': 'openai',
            'ai_extractions': [
                {
                    'category': 'Restaurant Info',
                    'confidence': 0.9,
                    'extracted_data': {
                        'name': "Fuller's Coffee Shop",
                        'address': "136 NW 9th Avenue",
                        'phone': "(503) 222-5608"
                    }
                }
            ]
        }
        
        restaurant.ai_analysis = ai_analysis_data
        
        # Verify ai_analysis is set
        assert hasattr(restaurant, 'ai_analysis'), "RestaurantData should have ai_analysis attribute"
        assert restaurant.ai_analysis is not None, "ai_analysis should not be None"
        assert restaurant.ai_analysis['confidence_score'] == 0.85, "AI confidence score should be preserved"
        assert restaurant.ai_analysis['provider_used'] == 'openai', "AI provider should be preserved"
    
    def test_restaurant_data_to_dict_includes_ai_analysis(self):
        """Test that RestaurantData.to_dict() includes ai_analysis field."""
        # Create RestaurantData object with AI analysis
        restaurant = RestaurantData(
            name="Test Restaurant",
            address="123 Test St",
            phone="555-0123",
            hours="9am-5pm",
            cuisine="Test Cuisine",
            menu_items={"test": ["item1", "item2"]},
            confidence="high",
            sources=["test_source"]
        )
        
        # Add AI analysis
        ai_analysis = {
            'confidence_score': 0.8,
            'provider_used': 'openai',
            'analysis_timestamp': '2025-01-16T10:00:00'
        }
        restaurant.ai_analysis = ai_analysis
        
        # Convert to dict
        restaurant_dict = restaurant.to_dict()
        
        # Verify ai_analysis is included
        assert 'ai_analysis' in restaurant_dict, f"ai_analysis missing from to_dict(). Keys: {list(restaurant_dict.keys())}"
        assert restaurant_dict['ai_analysis'] == ai_analysis, "ai_analysis should be preserved in to_dict()"
    
    def test_json_generator_processes_ai_analysis(self):
        """Test that JSON generator properly processes ai_analysis field."""
        # Create restaurant data with ai_analysis
        restaurant_data = {
            'name': "Test Restaurant",
            'address': "123 Test St",
            'phone': "555-0123",
            'hours': "9am-5pm",
            'cuisine': "Test Cuisine",
            'menu_items': {"test": ["item1", "item2"]},
            'confidence': "high",
            'sources': ["test_source"],
            'ai_analysis': {
                'confidence_score': 0.8,
                'meets_threshold': True,
                'provider_used': 'openai',
                'analysis_timestamp': '2025-01-16T10:00:00',
                'nutritional_context': {'healthy_options': ['salad', 'grilled chicken']},
                'price_analysis': {'price_range': '$$', 'average_entree': 15.99}
            }
        }
        
        # Create JSON generator
        json_generator = JSONExportGenerator()
        
        # Format restaurant data
        formatted_data = json_generator.format_restaurant_data(restaurant_data)
        
        # Verify ai_analysis is included in formatted output
        assert 'ai_analysis' in formatted_data, f"ai_analysis missing from formatted data. Keys: {list(formatted_data.keys())}"
        
        # Verify ai_analysis structure
        ai_analysis = formatted_data['ai_analysis']
        assert 'confidence_score' in ai_analysis, "confidence_score missing from ai_analysis"
        assert 'meets_threshold' in ai_analysis, "meets_threshold missing from ai_analysis"
        assert 'provider_used' in ai_analysis, "provider_used missing from ai_analysis"
        assert 'analysis_timestamp' in ai_analysis, "analysis_timestamp missing from ai_analysis"
    
    def test_json_generator_handles_missing_ai_analysis(self):
        """Test that JSON generator handles missing ai_analysis gracefully."""
        # Create restaurant data without ai_analysis
        restaurant_data = {
            'name': "Test Restaurant",
            'address': "123 Test St",
            'phone': "555-0123",
            'hours': "9am-5pm",
            'cuisine': "Test Cuisine",
            'menu_items': {"test": ["item1", "item2"]},
            'confidence': "high",
            'sources': ["test_source"]
        }
        
        # Create JSON generator
        json_generator = JSONExportGenerator()
        
        # Format restaurant data
        formatted_data = json_generator.format_restaurant_data(restaurant_data)
        
        # Verify ai_analysis is not included when not present
        assert 'ai_analysis' not in formatted_data, f"ai_analysis should not be present when missing. Keys: {list(formatted_data.keys())}"
    
    @patch('src.ai.llm_extractor.LLMExtractor')
    def test_file_upload_ai_enhancement_integration(self, mock_llm_extractor_class):
        """Test full integration of AI enhancement in file upload processing."""
        # Mock LLM extractor
        mock_llm_extractor = Mock()
        mock_llm_extractor_class.return_value = mock_llm_extractor
        
        # Mock successful AI extraction
        mock_llm_extractor.extract.return_value = {
            'success': True,
            'extractions': [
                {
                    'category': 'Restaurant Info',
                    'confidence': 0.9,
                    'extracted_data': {
                        'name': "Fuller's Coffee Shop",
                        'address': "136 NW 9th Avenue",
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
        
        # Mock PDF text extraction at the right place in the call chain
        with patch('src.web_interface.file_upload_routes.PDFTextExtractor') as mock_pdf_extractor_class:
            mock_pdf_extractor = Mock()
            mock_pdf_extractor_class.return_value = mock_pdf_extractor
            
            mock_pdf_result = Mock()
            mock_pdf_result.success = True
            mock_pdf_result.text = self.pdf_content
            mock_pdf_result.page_count = 1
            mock_pdf_result.method_used = 'pypdf'
            mock_pdf_result.error_message = None
            mock_pdf_extractor.extract_text.return_value = mock_pdf_result
            
            # Mock file upload handler
            with patch.object(self.file_routes.upload_handler, 'get_file_path') as mock_get_path:
                test_file_path = os.path.join(self.temp_dir, 'test_restaurant.pdf')
                with open(test_file_path, 'w') as f:
                    f.write(self.pdf_content)
                mock_get_path.return_value = test_file_path
                
                # Process file with AI enhancement
                with self.app.test_request_context():
                    response = self.file_routes._process_files_through_scraping_pipeline(
                        file_ids=['test_file_123'],
                        file_paths=[],
                        output_dir=self.temp_dir,
                        file_mode='single',
                        file_format='json',
                        json_field_selections=['core_fields', 'extended_fields', 'contact_fields', 'descriptive_fields'],
                        scraping_mode='single',
                        multi_page_config={},
                        industry='restaurant',
                        schema_type='Restaurant',
                        ai_config=self.ai_config
                    )
                
                # Verify response (handle tuple response from Flask)
                if isinstance(response, tuple):
                    flask_response, status_code = response
                    if hasattr(flask_response, 'json'):
                        response_data = flask_response.json
                    else:
                        response_data = flask_response.get_json()
                elif hasattr(response, 'json'):
                    response_data = response.json
                elif isinstance(response, dict):
                    response_data = response
                else:
                    raise AssertionError(f"Unexpected response type: {type(response)}")
                
                # Verify processing succeeded
                assert response_data.get('success') is True, f"Processing should succeed, got: {response_data}"
                
                # Verify output files were generated
                assert 'output_files' in response_data, "output_files should be in response"
                assert len(response_data['output_files']) > 0, "Should have generated output files"
                
                # Read generated JSON file
                output_file = response_data['output_files'][0]
                output_path = os.path.join(self.temp_dir, output_file)
                assert os.path.exists(output_path), f"Output file should exist: {output_path}"
                
                with open(output_path, 'r') as f:
                    output_json = json.load(f)
                
                # Verify JSON structure
                assert 'restaurants' in output_json, "JSON should contain restaurants"
                assert len(output_json['restaurants']) > 0, "Should have at least one restaurant"
                
                # Verify AI analysis is present
                restaurant = output_json['restaurants'][0]
                assert 'ai_analysis' in restaurant, f"Restaurant should have ai_analysis. Keys: {list(restaurant.keys())}"
                
                # Verify AI analysis structure
                ai_analysis = restaurant['ai_analysis']
                assert 'confidence_score' in ai_analysis, "AI analysis should have confidence_score"
                assert 'provider_used' in ai_analysis, "AI analysis should have provider_used"
                assert 'analysis_timestamp' in ai_analysis, "AI analysis should have analysis_timestamp"
                assert ai_analysis['provider_used'] == 'openai', "Provider should be openai"
                
                # Verify LLM extractor was called
                mock_llm_extractor.extract.assert_called_once()
    
    def test_ai_enhancement_failure_fallback(self):
        """Test that AI enhancement failure falls back gracefully."""
        # Mock LLM extractor to fail
        with patch('src.ai.llm_extractor.LLMExtractor') as mock_llm_extractor_class:
            mock_llm_extractor = Mock()
            mock_llm_extractor_class.return_value = mock_llm_extractor
            
            # Simulate API failure
            mock_llm_extractor.extract.side_effect = Exception("Malformed API response")
            
            # Mock PDF text extraction at the right place in the call chain
            with patch('src.web_interface.file_upload_routes.PDFTextExtractor') as mock_pdf_extractor_class:
                mock_pdf_extractor = Mock()
                mock_pdf_extractor_class.return_value = mock_pdf_extractor
                
                mock_pdf_result = Mock()
                mock_pdf_result.success = True
                mock_pdf_result.text = self.pdf_content
                mock_pdf_result.page_count = 1
                mock_pdf_result.method_used = 'pypdf'
                mock_pdf_result.error_message = None
                mock_pdf_extractor.extract_text.return_value = mock_pdf_result
                
                # Mock file upload handler
                with patch.object(self.file_routes.upload_handler, 'get_file_path') as mock_get_path:
                    test_file_path = os.path.join(self.temp_dir, 'test_restaurant.pdf')
                    with open(test_file_path, 'w') as f:
                        f.write(self.pdf_content)
                    mock_get_path.return_value = test_file_path
                    
                    # Process file with AI enhancement
                    with self.app.test_request_context():
                        response = self.file_routes._process_files_through_scraping_pipeline(
                            file_ids=['test_file_123'],
                            file_paths=[],
                            output_dir=self.temp_dir,
                            file_mode='single',
                            file_format='json',
                            json_field_selections=['core_fields', 'extended_fields', 'contact_fields', 'descriptive_fields'],
                            scraping_mode='single',
                            multi_page_config={},
                            industry='restaurant',
                            schema_type='Restaurant',
                            ai_config=self.ai_config
                        )
                    
                    # Verify response (handle tuple response from Flask)
                    if isinstance(response, tuple):
                        flask_response, status_code = response
                        if hasattr(flask_response, 'json'):
                            response_data = flask_response.json
                        else:
                            response_data = flask_response.get_json()
                    elif hasattr(response, 'json'):
                        response_data = response.json
                    elif isinstance(response, dict):
                        response_data = response
                    else:
                        raise AssertionError(f"Unexpected response type: {type(response)}")
                    
                    # Processing should still succeed with fallback
                    assert response_data.get('success') is True, f"Processing should succeed with fallback, got: {response_data}"
                    
                    # Verify output files were generated
                    assert 'output_files' in response_data, "output_files should be in response"
                    assert len(response_data['output_files']) > 0, "Should have generated output files"
                    
                    # Read generated JSON file
                    output_file = response_data['output_files'][0]
                    output_path = os.path.join(self.temp_dir, output_file)
                    assert os.path.exists(output_path), f"Output file should exist: {output_path}"
                    
                    with open(output_path, 'r') as f:
                        output_json = json.load(f)
                    
                    # Verify JSON structure
                    assert 'restaurants' in output_json, "JSON should contain restaurants"
                    assert len(output_json['restaurants']) > 0, "Should have at least one restaurant"
                    
                    # Verify restaurant data exists (from traditional extraction)
                    restaurant = output_json['restaurants'][0]
                    assert restaurant['basic_info']['name'], "Restaurant should have name from traditional extraction"
                    
                    # AI analysis should either be absent or contain error info
                    if 'ai_analysis' in restaurant:
                        ai_analysis = restaurant['ai_analysis']
                        assert 'error' in ai_analysis, "AI analysis should contain error information"
                        assert ai_analysis.get('fallback_used') is True, "Should indicate fallback was used"
    
    def test_ai_enhancement_disabled_no_ai_analysis(self):
        """Test that when AI enhancement is disabled, no ai_analysis is generated."""
        # Disable AI enhancement
        ai_config_disabled = {
            'ai_enhancement_enabled': False,
            'llm_provider': 'openai',
            'api_key': '',
            'ai_features': [],
            'confidence_threshold': 0.7,
            'custom_questions': []
        }
        
        # Mock PDF text extraction at the right place in the call chain
        with patch('src.web_interface.file_upload_routes.PDFTextExtractor') as mock_pdf_extractor_class:
            mock_pdf_extractor = Mock()
            mock_pdf_extractor_class.return_value = mock_pdf_extractor
            
            mock_pdf_result = Mock()
            mock_pdf_result.success = True
            mock_pdf_result.text = self.pdf_content
            mock_pdf_result.page_count = 1
            mock_pdf_result.method_used = 'pypdf'
            mock_pdf_result.error_message = None
            mock_pdf_extractor.extract_text.return_value = mock_pdf_result
            
            # Mock file upload handler
            with patch.object(self.file_routes.upload_handler, 'get_file_path') as mock_get_path:
                test_file_path = os.path.join(self.temp_dir, 'test_restaurant.pdf')
                with open(test_file_path, 'w') as f:
                    f.write(self.pdf_content)
                mock_get_path.return_value = test_file_path
                
                # Process file without AI enhancement
                with self.app.test_request_context():
                    response = self.file_routes._process_files_through_scraping_pipeline(
                        file_ids=['test_file_123'],
                        file_paths=[],
                        output_dir=self.temp_dir,
                        file_mode='single',
                        file_format='json',
                        json_field_selections=['core_fields', 'extended_fields', 'contact_fields', 'descriptive_fields'],
                        scraping_mode='single',
                        multi_page_config={},
                        industry='restaurant',
                        schema_type='Restaurant',
                        ai_config=ai_config_disabled
                    )
                
                # Verify response (handle tuple response from Flask)
                if isinstance(response, tuple):
                    flask_response, status_code = response
                    if hasattr(flask_response, 'json'):
                        response_data = flask_response.json
                    else:
                        response_data = flask_response.get_json()
                elif hasattr(response, 'json'):
                    response_data = response.json
                elif isinstance(response, dict):
                    response_data = response
                else:
                    raise AssertionError(f"Unexpected response type: {type(response)}")
                
                # Processing should succeed
                assert response_data.get('success') is True, f"Processing should succeed, got: {response_data}"
                
                # Read generated JSON file
                output_file = response_data['output_files'][0]
                output_path = os.path.join(self.temp_dir, output_file)
                
                with open(output_path, 'r') as f:
                    output_json = json.load(f)
                
                # Verify JSON structure
                restaurant = output_json['restaurants'][0]
                
                # AI analysis should NOT be present
                assert 'ai_analysis' not in restaurant, f"ai_analysis should not be present when AI is disabled. Keys: {list(restaurant.keys())}"
                
                # Traditional data should still be present
                assert restaurant['basic_info']['name'], "Restaurant should have name from traditional extraction"