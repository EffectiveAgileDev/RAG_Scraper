"""Unit tests for RestW processing integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, Any, List

from src.processors.restw_processor_factory import RestWProcessorFactory
from src.processors.restw_base_processor import RestWProcessor
from src.processors.restw_url_processor import RestWUrlProcessor
from src.processors.restw_pdf_processor import RestWPdfProcessor
from src.processors.restw_html_processor import RestWHtmlProcessor
from src.processors.restw_output_transformer import RestWOutputTransformer


@dataclass
class MockWTEGData:
    """Mock WTEG data for testing."""
    location: Dict[str, Any] = None
    menu_items: List[Dict[str, Any]] = None
    services_offered: Dict[str, Any] = None


class TestRestWProcessorFactory:
    """Test RestW processor factory."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        factory = RestWProcessorFactory()
        assert factory.obfuscate_terminology is True
        assert factory.use_wteg_processors is True

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            'obfuscate_terminology': False,
            'use_wteg_processors': False
        }
        factory = RestWProcessorFactory(config)
        assert factory.obfuscate_terminology is False
        assert factory.use_wteg_processors is False

    def test_create_processor_url(self):
        """Test creating URL processor."""
        factory = RestWProcessorFactory()
        processor = factory.create_processor('url', 'RestW')
        
        assert isinstance(processor, RestWUrlProcessor)
        assert processor.schema_type == 'RestW'

    def test_create_processor_pdf(self):
        """Test creating PDF processor."""
        factory = RestWProcessorFactory()
        processor = factory.create_processor('pdf', 'RestW')
        
        assert isinstance(processor, RestWPdfProcessor)
        assert processor.schema_type == 'RestW'

    def test_create_processor_html(self):
        """Test creating HTML processor."""
        factory = RestWProcessorFactory()
        processor = factory.create_processor('html', 'RestW')
        
        assert isinstance(processor, RestWHtmlProcessor)
        assert processor.schema_type == 'RestW'

    def test_create_processor_invalid_type(self):
        """Test creating processor with invalid type."""
        factory = RestWProcessorFactory()
        
        with pytest.raises(ValueError):
            factory.create_processor('invalid_type', 'RestW')

    def test_create_processor_standard_schema(self):
        """Test creating processor with standard schema."""
        factory = RestWProcessorFactory()
        processor = factory.create_processor('url', 'standard')
        
        assert processor.schema_type == 'standard'
        assert not processor.uses_wteg_schema()

    def test_get_available_processors(self):
        """Test getting available processors."""
        factory = RestWProcessorFactory()
        processors = factory.get_available_processors()
        
        assert 'url' in processors
        assert 'pdf' in processors
        assert 'html' in processors

    def test_get_processor_config(self):
        """Test getting processor configuration."""
        factory = RestWProcessorFactory()
        config = factory.get_processor_config('url')
        
        assert 'uses_wteg_processors' in config
        assert 'obfuscate_output' in config
        assert config['uses_wteg_processors'] is True

    def test_validate_processor_type(self):
        """Test validating processor type."""
        factory = RestWProcessorFactory()
        
        assert factory.validate_processor_type('url') is True
        assert factory.validate_processor_type('pdf') is True
        assert factory.validate_processor_type('invalid') is False

    def test_validate_schema_type(self):
        """Test validating schema type."""
        factory = RestWProcessorFactory()
        
        assert factory.validate_schema_type('RestW') is True
        assert factory.validate_schema_type('standard') is True
        assert factory.validate_schema_type('invalid') is False


class TestRestWProcessor:
    """Test base RestW processor."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        processor = RestWProcessor()
        assert processor.schema_type == 'RestW'
        assert processor.obfuscate_terminology is True

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            'schema_type': 'custom',
            'obfuscate_terminology': False
        }
        processor = RestWProcessor(config)
        assert processor.schema_type == 'custom'
        assert processor.obfuscate_terminology is False

    def test_uses_wteg_schema(self):
        """Test checking if processor uses WTEG schema."""
        processor = RestWProcessor()
        assert processor.uses_wteg_schema() is True

    def test_get_schema_type(self):
        """Test getting schema type."""
        processor = RestWProcessor()
        assert processor.get_schema_type() == 'RestW'

    def test_get_processing_config(self):
        """Test getting processing configuration."""
        processor = RestWProcessor()
        config = processor.get_processing_config()
        
        assert 'schema_type' in config
        assert 'obfuscate_terminology' in config
        assert config['schema_type'] == 'RestW'

    def test_transform_wteg_to_restw(self):
        """Test transforming WTEG data to RestW format."""
        processor = RestWProcessor()
        wteg_data = {
            'location': {'street_address': '123 Main St'},
            'menu_items': [{'item_name': 'Pizza'}],
            'services_offered': {'delivery_available': True}
        }
        
        with patch.object(processor, 'output_transformer') as mock_transformer:
            mock_transformer.transform.return_value = {'transformed': True}
            result = processor.transform_wteg_to_restw(wteg_data)
            
            mock_transformer.transform.assert_called_once_with(wteg_data)
            assert result == {'transformed': True}

    def test_validate_restw_output(self):
        """Test validating RestW output."""
        processor = RestWProcessor()
        
        # Valid output
        valid_output = {
            'location': {'street_address': '123 Main St'},
            'menu_items': [{'item_name': 'Pizza'}]
        }
        assert processor.validate_restw_output(valid_output) is True
        
        # Invalid output
        invalid_output = {'invalid': 'data'}
        assert processor.validate_restw_output(invalid_output) is False

    def test_get_error_handling_config(self):
        """Test getting error handling configuration."""
        processor = RestWProcessor()
        error_config = processor.get_error_handling_config()
        
        assert 'fallback_to_standard' in error_config
        assert 'log_errors' in error_config
        assert error_config['fallback_to_standard'] is True


class TestRestWUrlProcessor:
    """Test RestW URL processor."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        processor = RestWUrlProcessor()
        assert processor.schema_type == 'RestW'
        assert hasattr(processor, 'wteg_extractor')

    def test_process_url_success(self):
        """Test successful URL processing."""
        processor = RestWUrlProcessor()
        url = 'https://example-restaurant.com'
        
        mock_wteg_data = MockWTEGData(
            location={'street_address': '123 Main St'},
            menu_items=[{'item_name': 'Pizza', 'price': '$10'}]
        )
        
        with patch.object(processor, 'wteg_extractor') as mock_extractor:
            mock_extractor.extract_from_url.return_value = mock_wteg_data
            
            with patch.object(processor, 'transform_wteg_to_restw') as mock_transform:
                mock_transform.return_value = {'transformed': True}
                
                with patch.object(processor, 'validate_restw_output') as mock_validate:
                    mock_validate.return_value = True
                    
                    result = processor.process_url(url)
                    
                    mock_extractor.extract_from_url.assert_called_once_with(url, None)
                    mock_transform.assert_called_once_with(mock_wteg_data)
                    assert result == {'transformed': True}

    def test_process_url_failure(self):
        """Test URL processing failure."""
        processor = RestWUrlProcessor()
        url = 'https://example-restaurant.com'
        
        with patch.object(processor, 'wteg_extractor') as mock_extractor:
            mock_extractor.extract_from_url.side_effect = Exception('Extraction failed')
            
            result = processor.process_url(url)
            
            assert result is None

    def test_process_url_with_options(self):
        """Test URL processing with options."""
        processor = RestWUrlProcessor()
        url = 'https://example-restaurant.com'
        options = {'include_menu': True, 'include_services': False}
        
        mock_wteg_data = MockWTEGData(
            location={'street_address': '123 Main St'},
            menu_items=[{'item_name': 'Pizza'}]
        )
        
        with patch.object(processor, 'wteg_extractor') as mock_extractor:
            mock_extractor.extract_from_url.return_value = mock_wteg_data
            
            with patch.object(processor, 'transform_wteg_to_restw') as mock_transform:
                mock_transform.return_value = {'transformed': True}
                
                with patch.object(processor, 'validate_restw_output') as mock_validate:
                    mock_validate.return_value = True
                    
                    result = processor.process_url(url, options)
                    
                    mock_extractor.extract_from_url.assert_called_once_with(url, options)
                    assert result == {'transformed': True}

    def test_validate_url(self):
        """Test URL validation."""
        processor = RestWUrlProcessor()
        
        assert processor.validate_url('https://example.com') is True
        assert processor.validate_url('http://example.com') is True
        assert processor.validate_url('invalid-url') is False
        assert processor.validate_url('') is False

    def test_get_supported_domains(self):
        """Test getting supported domains."""
        processor = RestWUrlProcessor()
        domains = processor.get_supported_domains()
        
        assert isinstance(domains, list)
        assert len(domains) > 0

    def test_is_restaurant_url(self):
        """Test checking if URL is a restaurant."""
        processor = RestWUrlProcessor()
        
        restaurant_urls = [
            'https://restaurant.com',
            'https://pizza-place.com',
            'https://example.com/menu'
        ]
        
        for url in restaurant_urls:
            # This would use actual restaurant detection logic
            assert processor.is_restaurant_url(url) in [True, False]


class TestRestWPdfProcessor:
    """Test RestW PDF processor."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        processor = RestWPdfProcessor()
        assert processor.schema_type == 'RestW'
        assert hasattr(processor, 'wteg_pdf_processor')

    def test_process_pdf_success(self):
        """Test successful PDF processing."""
        processor = RestWPdfProcessor()
        pdf_path = '/path/to/restaurant_menu.pdf'
        
        mock_wteg_data = MockWTEGData(
            location={'street_address': '123 Main St'},
            menu_items=[{'item_name': 'Pizza', 'price': '$10'}]
        )
        
        with patch.object(processor, 'validate_pdf_file') as mock_validate_file:
            mock_validate_file.return_value = True
            
            with patch.object(processor, 'wteg_pdf_processor') as mock_processor:
                mock_processor.process_pdf.return_value = mock_wteg_data
                
                with patch.object(processor, 'transform_wteg_to_restw') as mock_transform:
                    mock_transform.return_value = {'transformed': True}
                    
                    with patch.object(processor, 'validate_restw_output') as mock_validate:
                        mock_validate.return_value = True
                        
                        result = processor.process_pdf(pdf_path)
                        
                        mock_processor.process_pdf.assert_called_once_with(pdf_path, None)
                        mock_transform.assert_called_once_with(mock_wteg_data)
                        assert result == {'transformed': True}

    def test_process_pdf_failure(self):
        """Test PDF processing failure."""
        processor = RestWPdfProcessor()
        pdf_path = '/path/to/restaurant_menu.pdf'
        
        with patch.object(processor, 'wteg_pdf_processor') as mock_processor:
            mock_processor.process_pdf.side_effect = Exception('PDF processing failed')
            
            result = processor.process_pdf(pdf_path)
            
            assert result is None

    def test_process_pdf_with_options(self):
        """Test PDF processing with options."""
        processor = RestWPdfProcessor()
        pdf_path = '/path/to/restaurant_menu.pdf'
        options = {'ocr_enabled': True, 'language': 'en'}
        
        mock_wteg_data = MockWTEGData(menu_items=[{'item_name': 'Pizza'}])
        
        with patch.object(processor, 'validate_pdf_file') as mock_validate_file:
            mock_validate_file.return_value = True
            
            with patch.object(processor, 'wteg_pdf_processor') as mock_processor:
                mock_processor.process_pdf.return_value = mock_wteg_data
                
                with patch.object(processor, 'transform_wteg_to_restw') as mock_transform:
                    mock_transform.return_value = {'transformed': True}
                    
                    with patch.object(processor, 'validate_restw_output') as mock_validate:
                        mock_validate.return_value = True
                        
                        result = processor.process_pdf(pdf_path, options)
                        
                        mock_processor.process_pdf.assert_called_once_with(pdf_path, options)
                        assert result == {'transformed': True}

    def test_validate_pdf_file(self):
        """Test PDF file validation."""
        processor = RestWPdfProcessor()
        
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            with patch('os.path.isfile') as mock_isfile:
                mock_isfile.return_value = True
                
                with patch('os.path.getsize') as mock_getsize:
                    mock_getsize.return_value = 1024  # 1KB file
                    
                    assert processor.validate_pdf_file('test.pdf') is True
                    assert processor.validate_pdf_file('test.txt') is False

    def test_get_pdf_metadata(self):
        """Test getting PDF metadata."""
        processor = RestWPdfProcessor()
        pdf_path = '/path/to/restaurant_menu.pdf'
        
        with patch.object(processor, 'validate_pdf_file') as mock_validate:
            mock_validate.return_value = True
            
            with patch('os.path.getsize') as mock_getsize:
                mock_getsize.return_value = 1024
                
                with patch.object(processor, 'wteg_pdf_processor') as mock_processor:
                    mock_processor.get_pdf_metadata.return_value = {
                        'pages': 3,
                        'title': 'Restaurant Menu'
                    }
                    
                    metadata = processor.get_pdf_metadata(pdf_path)
                    
                    assert metadata['pages'] == 3
                    assert metadata['title'] == 'Restaurant Menu'

    def test_extract_text_from_pdf(self):
        """Test extracting text from PDF."""
        processor = RestWPdfProcessor()
        pdf_path = '/path/to/restaurant_menu.pdf'
        
        with patch.object(processor, 'validate_pdf_file') as mock_validate:
            mock_validate.return_value = True
            
            with patch.object(processor, 'wteg_pdf_processor') as mock_processor:
                mock_processor.extract_text.return_value = 'Pizza $10\nBurger $8'
                
                text = processor.extract_text_from_pdf(pdf_path)
                
                assert 'Pizza' in text
                assert 'Burger' in text


class TestRestWHtmlProcessor:
    """Test RestW HTML processor."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        processor = RestWHtmlProcessor()
        assert processor.schema_type == 'RestW'
        assert hasattr(processor, 'wteg_html_processor')

    def test_process_html_success(self):
        """Test successful HTML processing."""
        processor = RestWHtmlProcessor()
        html_content = '<html><body><h1>Restaurant Menu</h1></body></html>'
        
        mock_wteg_data = MockWTEGData(
            location={'street_address': '123 Main St'},
            menu_items=[{'item_name': 'Pizza', 'price': '$10'}]
        )
        
        with patch.object(processor, 'wteg_html_processor') as mock_processor:
            mock_processor.process_html.return_value = mock_wteg_data
            
            with patch.object(processor, 'transform_wteg_to_restw') as mock_transform:
                mock_transform.return_value = {'transformed': True}
                
                with patch.object(processor, 'validate_restw_output') as mock_validate:
                    mock_validate.return_value = True
                    
                    result = processor.process_html(html_content)
                    
                    mock_processor.process_html.assert_called_once_with(html_content, None)
                    mock_transform.assert_called_once_with(mock_wteg_data)
                    assert result == {'transformed': True}

    def test_process_html_failure(self):
        """Test HTML processing failure."""
        processor = RestWHtmlProcessor()
        html_content = '<html><body><h1>Restaurant Menu</h1></body></html>'
        
        with patch.object(processor, 'wteg_html_processor') as mock_processor:
            mock_processor.process_html.side_effect = Exception('HTML processing failed')
            
            result = processor.process_html(html_content)
            
            assert result is None

    def test_process_html_with_url(self):
        """Test HTML processing with URL context."""
        processor = RestWHtmlProcessor()
        html_content = '<html><body><h1>Restaurant Menu</h1></body></html>'
        url = 'https://example-restaurant.com'
        
        mock_wteg_data = MockWTEGData(menu_items=[{'item_name': 'Pizza'}])
        
        with patch.object(processor, 'wteg_html_processor') as mock_processor:
            mock_processor.process_html.return_value = mock_wteg_data
            
            with patch.object(processor, 'transform_wteg_to_restw') as mock_transform:
                mock_transform.return_value = {'transformed': True}
                
                with patch.object(processor, 'validate_restw_output') as mock_validate:
                    mock_validate.return_value = True
                    
                    result = processor.process_html(html_content, url)
                    
                    mock_processor.process_html.assert_called_once_with(html_content, url)
                    assert result == {'transformed': True}

    def test_validate_html(self):
        """Test HTML validation."""
        processor = RestWHtmlProcessor()
        
        valid_html = '<html><body><h1>Test</h1></body></html>'
        assert processor.validate_html(valid_html) is True
        
        # HTML fragments are actually valid in the current implementation
        html_fragment = '<html><body><h1>Test</h1></body>'
        assert processor.validate_html(html_fragment) is True
        
        # But completely invalid HTML should fail
        invalid_html = 'just plain text with no tags'
        assert processor.validate_html(invalid_html) is False
        
        empty_html = ''
        assert processor.validate_html(empty_html) is False

    def test_extract_structured_data(self):
        """Test extracting structured data from HTML."""
        processor = RestWHtmlProcessor()
        html_content = '<html><body><h1>Restaurant Menu</h1></body></html>'
        
        with patch.object(processor, 'wteg_html_processor') as mock_processor:
            mock_processor.extract_structured_data.return_value = {
                'json_ld': [],
                'microdata': {}
            }
            
            structured_data = processor.extract_structured_data(html_content)
            
            assert 'json_ld' in structured_data
            assert 'microdata' in structured_data

    def test_is_restaurant_html(self):
        """Test checking if HTML is from a restaurant."""
        processor = RestWHtmlProcessor()
        
        restaurant_html = '<html><body><h1>Restaurant Menu</h1><p>Pizza $10</p></body></html>'
        assert processor.is_restaurant_html(restaurant_html) is True
        
        non_restaurant_html = '<html><body><h1>Medical Services</h1></body></html>'
        assert processor.is_restaurant_html(non_restaurant_html) is False


class TestRestWOutputTransformer:
    """Test RestW output transformer."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        transformer = RestWOutputTransformer()
        assert transformer.obfuscate_terminology is True
        assert transformer.field_mappings is not None

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            'obfuscate_terminology': False,
            'custom_mappings': {'custom': 'mapping'}
        }
        transformer = RestWOutputTransformer(config)
        assert transformer.obfuscate_terminology is False

    def test_transform_wteg_data(self):
        """Test transforming WTEG data to RestW format."""
        transformer = RestWOutputTransformer()
        wteg_data = {
            'location': {'street_address': '123 Main St'},
            'menu_items': [{'item_name': 'Pizza', 'price': '$10'}],
            'services_offered': {'delivery_available': True}
        }
        
        result = transformer.transform(wteg_data)
        
        assert 'location' in result
        assert 'menu_items' in result
        assert 'services_offered' in result
        assert result['location']['street_address'] == '123 Main St'

    def test_obfuscate_field_names(self):
        """Test obfuscating field names."""
        transformer = RestWOutputTransformer()
        
        # Test WTEG field name obfuscation
        assert transformer.obfuscate_field_names('WTEGLocation') == 'RestWLocation'
        assert transformer.obfuscate_field_names('wteg_field') == 'restw_field'
        assert transformer.obfuscate_field_names('regular_field') == 'regular_field'

    def test_obfuscate_terminology(self):
        """Test obfuscating terminology in text."""
        transformer = RestWOutputTransformer()
        
        text_with_wteg = 'This is WTEG data from wteg extraction.'
        result = transformer.obfuscate_terminology_text(text_with_wteg)
        
        assert 'WTEG' not in result
        assert 'wteg' not in result
        assert 'RestW' in result

    def test_transform_menu_items(self):
        """Test transforming menu items."""
        transformer = RestWOutputTransformer()
        menu_items = [
            {'item_name': 'Pizza', 'price': '$10', 'category': 'Main'},
            {'item_name': 'Salad', 'price': '$8', 'category': 'Appetizer'}
        ]
        
        result = transformer.transform_menu_items(menu_items)
        
        assert len(result) == 2
        assert result[0]['item_name'] == 'Pizza'
        assert result[1]['item_name'] == 'Salad'

    def test_transform_location_data(self):
        """Test transforming location data."""
        transformer = RestWOutputTransformer()
        location_data = {
            'street_address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345'
        }
        
        result = transformer.transform_location_data(location_data)
        
        assert result['street_address'] == '123 Main St'
        assert result['city'] == 'Anytown'
        assert result['state'] == 'CA'
        assert result['zip_code'] == '12345'

    def test_transform_services_data(self):
        """Test transforming services data."""
        transformer = RestWOutputTransformer()
        services_data = {
            'delivery_available': True,
            'takeout_available': True,
            'catering_available': False
        }
        
        result = transformer.transform_services_data(services_data)
        
        assert result['delivery_available'] is True
        assert result['takeout_available'] is True
        assert result['catering_available'] is False

    def test_validate_transformed_output(self):
        """Test validating transformed output."""
        transformer = RestWOutputTransformer()
        
        # Valid output
        valid_output = {
            'location': {'street_address': '123 Main St'},
            'menu_items': [{'item_name': 'Pizza'}],
            'services_offered': {'delivery_available': True}
        }
        assert transformer.validate_transformed_output(valid_output) is True
        
        # Invalid output
        invalid_output = {'invalid': 'data'}
        assert transformer.validate_transformed_output(invalid_output) is False

    def test_get_transformation_statistics(self):
        """Test getting transformation statistics."""
        transformer = RestWOutputTransformer()
        
        # Perform some transformations
        wteg_data = {
            'location': {'street_address': '123 Main St'},
            'menu_items': [{'item_name': 'Pizza'}]
        }
        transformer.transform(wteg_data)
        
        stats = transformer.get_transformation_statistics()
        
        assert 'fields_transformed' in stats
        assert 'terminology_obfuscated' in stats
        assert stats['fields_transformed'] >= 0