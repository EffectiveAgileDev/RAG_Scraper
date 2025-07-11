"""Unit tests for RestW configuration system."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import os

from src.config.restw_config import RestWConfig, RestWFieldConfig, RestWProcessingConfig


class TestRestWConfig:
    """Test RestW configuration management."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = RestWConfig()
        assert config.enabled is True
        assert config.obfuscate_wteg is True
        assert config.default_fields is not None

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        custom_config = {
            'enabled': False,
            'obfuscate_wteg': False,
            'default_fields': ['location', 'menu_items']
        }
        config = RestWConfig(custom_config)
        assert config.enabled is False
        assert config.obfuscate_wteg is False
        assert config.default_fields == ['location', 'menu_items']

    def test_is_restw_schema_selected_true(self):
        """Test detecting RestW schema selection."""
        config = RestWConfig()
        form_data = {'schema': 'RestW'}
        assert config.is_restw_schema_selected(form_data) is True

    def test_is_restw_schema_selected_false(self):
        """Test detecting non-RestW schema selection."""
        config = RestWConfig()
        form_data = {'schema': 'standard'}
        assert config.is_restw_schema_selected(form_data) is False

    def test_is_restw_schema_selected_missing(self):
        """Test detecting missing schema selection."""
        config = RestWConfig()
        form_data = {}
        assert config.is_restw_schema_selected(form_data) is False

    def test_get_extraction_fields_default(self):
        """Test getting default extraction fields."""
        config = RestWConfig()
        fields = config.get_extraction_fields()
        
        expected_fields = ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links']
        assert all(field in fields for field in expected_fields)

    def test_get_extraction_fields_custom(self):
        """Test getting custom extraction fields."""
        config = RestWConfig()
        custom_fields = ['location', 'menu_items']
        fields = config.get_extraction_fields(custom_fields)
        
        assert fields == custom_fields

    def test_get_field_configuration(self):
        """Test getting field configuration."""
        config = RestWConfig()
        field_config = config.get_field_configuration('location')
        
        assert 'display_name' in field_config
        assert 'description' in field_config
        assert 'wteg_mapping' in field_config
        assert 'WTEG' not in field_config['display_name']

    def test_get_field_configuration_invalid_field(self):
        """Test getting configuration for invalid field."""
        config = RestWConfig()
        field_config = config.get_field_configuration('invalid_field')
        
        assert field_config is None

    def test_get_processing_configuration(self):
        """Test getting processing configuration."""
        config = RestWConfig()
        proc_config = config.get_processing_configuration()
        
        assert 'use_wteg_processors' in proc_config
        assert 'obfuscate_terminology' in proc_config
        assert proc_config['use_wteg_processors'] is True
        assert proc_config['obfuscate_terminology'] is True

    def test_get_output_configuration(self):
        """Test getting output configuration."""
        config = RestWConfig()
        output_config = config.get_output_configuration()
        
        assert 'schema_name' in output_config
        assert 'field_mappings' in output_config
        assert output_config['schema_name'] == 'RestW'

    def test_obfuscate_wteg_terminology(self):
        """Test obfuscating WTEG terminology."""
        config = RestWConfig()
        
        # Test field names
        assert config.obfuscate_wteg_terminology('WTEG Location') == 'RestW Location'
        assert config.obfuscate_wteg_terminology('wteg_field') == 'restw_field'
        assert config.obfuscate_wteg_terminology('WTEGMenuItem') == 'RestWMenuItem'
        
        # Test non-WTEG text
        assert config.obfuscate_wteg_terminology('Regular text') == 'Regular text'

    def test_get_wteg_to_restw_mapping(self):
        """Test getting WTEG to RestW field mapping."""
        config = RestWConfig()
        mapping = config.get_wteg_to_restw_mapping()
        
        assert 'WTEGLocation' in mapping
        assert 'WTEGMenuItem' in mapping
        assert 'WTEGServices' in mapping
        assert mapping['WTEGLocation'] == 'RestWLocation'
        assert mapping['WTEGMenuItem'] == 'RestWMenuItem'

    def test_translate_wteg_data_to_restw(self):
        """Test translating WTEG data to RestW format."""
        config = RestWConfig()
        wteg_data = {
            'location': {'street_address': '123 Main St'},
            'menu_items': [{'item_name': 'Pizza', 'price': '$10'}],
            'services_offered': {'delivery_available': True}
        }
        
        restw_data = config.translate_wteg_data_to_restw(wteg_data)
        
        assert 'location' in restw_data
        assert 'menu_items' in restw_data
        assert 'services_offered' in restw_data
        assert restw_data['location']['street_address'] == '123 Main St'

    def test_validate_restw_configuration(self):
        """Test validating RestW configuration."""
        config = RestWConfig()
        
        # Valid configuration
        valid_config = {
            'enabled': True,
            'fields': ['location', 'menu_items']
        }
        assert config.validate_restw_configuration(valid_config) is True
        
        # Invalid configuration
        invalid_config = {
            'enabled': True,
            'fields': ['invalid_field']
        }
        assert config.validate_restw_configuration(invalid_config) is False

    def test_has_saved_configuration(self):
        """Test checking for saved configuration."""
        config = RestWConfig()
        
        # Mock saved configuration
        with patch.object(config, '_load_saved_configuration') as mock_load:
            mock_load.return_value = {'enabled': True}
            assert config.has_saved_configuration() is True
            
            mock_load.return_value = None
            assert config.has_saved_configuration() is False

    def test_save_configuration(self):
        """Test saving configuration."""
        config = RestWConfig()
        config_data = {
            'enabled': True,
            'fields': ['location', 'menu_items']
        }
        
        with patch.object(config, '_save_configuration_to_file') as mock_save:
            config.save_configuration(config_data)
            mock_save.assert_called_once_with(config_data)

    def test_load_configuration(self):
        """Test loading configuration."""
        config = RestWConfig()
        
        with patch.object(config, '_load_configuration_from_file') as mock_load:
            mock_load.return_value = {'enabled': True}
            loaded_config = config.load_configuration()
            assert loaded_config['enabled'] is True

    def test_get_batch_configuration(self):
        """Test getting batch processing configuration."""
        config = RestWConfig()
        batch_config = config.get_batch_configuration()
        
        assert 'batch_size' in batch_config
        assert 'parallel_processing' in batch_config
        assert 'use_wteg_processors' in batch_config
        assert batch_config['use_wteg_processors'] is True

    def test_get_ui_configuration(self):
        """Test getting UI configuration."""
        config = RestWConfig()
        ui_config = config.get_ui_configuration()
        
        assert 'show_restw_option' in ui_config
        assert 'available_for_industries' in ui_config
        assert 'Restaurant' in ui_config['available_for_industries']
        assert ui_config['show_restw_option'] is True

    def test_is_enabled_for_industry(self):
        """Test checking if RestW is enabled for industry."""
        config = RestWConfig()
        
        assert config.is_enabled_for_industry('Restaurant') is True
        assert config.is_enabled_for_industry('Medical') is False
        assert config.is_enabled_for_industry('Real Estate') is False

    def test_get_help_text_for_field(self):
        """Test getting help text for specific field."""
        config = RestWConfig()
        
        location_help = config.get_help_text_for_field('location')
        assert len(location_help) > 0
        assert 'WTEG' not in location_help
        assert 'address' in location_help.lower()

        menu_help = config.get_help_text_for_field('menu_items')
        assert len(menu_help) > 0
        assert 'WTEG' not in menu_help
        assert 'menu' in menu_help.lower()

    def test_get_processor_mapping(self):
        """Test getting processor mapping."""
        config = RestWConfig()
        mapping = config.get_processor_mapping()
        
        assert 'url' in mapping
        assert 'pdf' in mapping
        assert 'html' in mapping
        assert 'wteg' in mapping['url'].lower()
        assert 'wteg' in mapping['pdf'].lower()


class TestRestWFieldConfig:
    """Test RestW field configuration."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        field_config = RestWFieldConfig('location')
        assert field_config.field_name == 'location'
        assert field_config.enabled is True
        assert field_config.required is False

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        field_config = RestWFieldConfig(
            field_name='menu_items',
            enabled=False,
            required=True,
            display_name='Custom Menu Items'
        )
        assert field_config.field_name == 'menu_items'
        assert field_config.enabled is False
        assert field_config.required is True
        assert field_config.display_name == 'Custom Menu Items'

    def test_get_display_name_default(self):
        """Test getting default display name."""
        field_config = RestWFieldConfig('location')
        assert field_config.get_display_name() == 'Location Data'

    def test_get_display_name_custom(self):
        """Test getting custom display name."""
        field_config = RestWFieldConfig('location', display_name='Custom Location')
        assert field_config.get_display_name() == 'Custom Location'

    def test_get_description(self):
        """Test getting field description."""
        field_config = RestWFieldConfig('location')
        description = field_config.get_description()
        
        assert len(description) > 0
        assert 'WTEG' not in description
        assert 'address' in description.lower()

    def test_get_wteg_mapping(self):
        """Test getting WTEG mapping for field."""
        field_config = RestWFieldConfig('location')
        mapping = field_config.get_wteg_mapping()
        
        assert 'wteg_field' in mapping
        assert 'wteg_class' in mapping
        assert 'WTEGLocation' in mapping['wteg_class']

    def test_is_valid_field_name(self):
        """Test validating field names."""
        assert RestWFieldConfig.is_valid_field_name('location') is True
        assert RestWFieldConfig.is_valid_field_name('menu_items') is True
        assert RestWFieldConfig.is_valid_field_name('invalid_field') is False

    def test_get_available_fields(self):
        """Test getting available fields."""
        fields = RestWFieldConfig.get_available_fields()
        
        expected_fields = ['location', 'menu_items', 'services_offered', 'contact_info', 'web_links']
        assert all(field in fields for field in expected_fields)

    def test_validate_field_configuration(self):
        """Test validating field configuration."""
        field_config = RestWFieldConfig('location')
        
        # Valid configuration
        valid_config = {
            'enabled': True,
            'required': False,
            'display_name': 'Location Data'
        }
        assert field_config.validate_field_configuration(valid_config) is True
        
        # Invalid configuration
        invalid_config = {
            'enabled': 'invalid_boolean'
        }
        assert field_config.validate_field_configuration(invalid_config) is False

    def test_to_dict(self):
        """Test converting field configuration to dictionary."""
        field_config = RestWFieldConfig('location', enabled=True, required=False)
        config_dict = field_config.to_dict()
        
        assert config_dict['field_name'] == 'location'
        assert config_dict['enabled'] is True
        assert config_dict['required'] is False

    def test_from_dict(self):
        """Test creating field configuration from dictionary."""
        config_dict = {
            'field_name': 'location',
            'enabled': True,
            'required': False,
            'display_name': 'Location Data'
        }
        field_config = RestWFieldConfig.from_dict(config_dict)
        
        assert field_config.field_name == 'location'
        assert field_config.enabled is True
        assert field_config.required is False
        assert field_config.display_name == 'Location Data'


class TestRestWProcessingConfig:
    """Test RestW processing configuration."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        proc_config = RestWProcessingConfig()
        assert proc_config.use_wteg_processors is True
        assert proc_config.obfuscate_terminology is True
        assert proc_config.parallel_processing is True

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        proc_config = RestWProcessingConfig(
            use_wteg_processors=False,
            obfuscate_terminology=False,
            parallel_processing=False
        )
        assert proc_config.use_wteg_processors is False
        assert proc_config.obfuscate_terminology is False
        assert proc_config.parallel_processing is False

    def test_get_processor_factory_config(self):
        """Test getting processor factory configuration."""
        proc_config = RestWProcessingConfig()
        factory_config = proc_config.get_processor_factory_config()
        
        assert 'use_wteg_processors' in factory_config
        assert 'obfuscate_output' in factory_config
        assert factory_config['use_wteg_processors'] is True
        assert factory_config['obfuscate_output'] is True

    def test_get_extraction_config(self):
        """Test getting extraction configuration."""
        proc_config = RestWProcessingConfig()
        extract_config = proc_config.get_extraction_config()
        
        assert 'field_mappings' in extract_config
        assert 'output_format' in extract_config
        assert extract_config['output_format'] == 'RestW'

    def test_get_output_transformation_config(self):
        """Test getting output transformation configuration."""
        proc_config = RestWProcessingConfig()
        transform_config = proc_config.get_output_transformation_config()
        
        assert 'terminology_mapping' in transform_config
        assert 'field_name_mapping' in transform_config
        assert 'WTEG' in transform_config['terminology_mapping']
        assert transform_config['terminology_mapping']['WTEG'] == 'RestW'

    def test_validate_processing_configuration(self):
        """Test validating processing configuration."""
        proc_config = RestWProcessingConfig()
        
        # Valid configuration
        valid_config = {
            'use_wteg_processors': True,
            'obfuscate_terminology': True,
            'parallel_processing': False
        }
        assert proc_config.validate_processing_configuration(valid_config) is True
        
        # Invalid configuration
        invalid_config = {
            'use_wteg_processors': 'invalid_boolean'
        }
        assert proc_config.validate_processing_configuration(invalid_config) is False

    def test_get_batch_processing_config(self):
        """Test getting batch processing configuration."""
        proc_config = RestWProcessingConfig()
        batch_config = proc_config.get_batch_processing_config()
        
        assert 'batch_size' in batch_config
        assert 'max_workers' in batch_config
        assert 'timeout' in batch_config
        assert batch_config['batch_size'] > 0

    def test_get_error_handling_config(self):
        """Test getting error handling configuration."""
        proc_config = RestWProcessingConfig()
        error_config = proc_config.get_error_handling_config()
        
        assert 'fallback_to_standard' in error_config
        assert 'log_wteg_errors' in error_config
        assert error_config['fallback_to_standard'] is True

    def test_to_dict(self):
        """Test converting processing configuration to dictionary."""
        proc_config = RestWProcessingConfig()
        config_dict = proc_config.to_dict()
        
        assert config_dict['use_wteg_processors'] is True
        assert config_dict['obfuscate_terminology'] is True
        assert config_dict['parallel_processing'] is True

    def test_from_dict(self):
        """Test creating processing configuration from dictionary."""
        config_dict = {
            'use_wteg_processors': False,
            'obfuscate_terminology': False,
            'parallel_processing': False
        }
        proc_config = RestWProcessingConfig.from_dict(config_dict)
        
        assert proc_config.use_wteg_processors is False
        assert proc_config.obfuscate_terminology is False
        assert proc_config.parallel_processing is False