"""Unit tests for ConfigurableExtractionOptions."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the module we're testing
try:
    from src.scraper.configurable_extraction_options import ConfigurableExtractionOptions
    from src.scraper.configurable_extraction_options import ExtractionField
    from src.scraper.configurable_extraction_options import FieldPriority
    from src.scraper.configurable_extraction_options import OutputFormat
    from src.scraper.configurable_extraction_options import ExtractionOptimizer
except ImportError:
    ConfigurableExtractionOptions = None
    ExtractionField = None
    FieldPriority = None
    OutputFormat = None
    ExtractionOptimizer = None


class TestConfigurableExtractionOptions:
    """Test cases for ConfigurableExtractionOptions."""

    def test_extraction_options_initialization(self):
        """Test that extraction options initialize correctly."""
        if ConfigurableExtractionOptions is None:
            pytest.fail("ConfigurableExtractionOptions not implemented - TDD RED phase")
        
        options = ConfigurableExtractionOptions()
        assert options is not None
        assert options.extraction_fields is not None
        assert options.field_priorities is not None
        assert options.output_format is not None
        assert options.extraction_optimizer is not None

    def test_extraction_options_initialization_with_config(self):
        """Test extraction options initialization with custom configuration."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        config = {
            'fields': ['name', 'address', 'phone', 'menu'],
            'priorities': {'name': 1, 'address': 2, 'phone': 3, 'menu': 4},
            'output_format': 'json',
            'optimization_level': 'high'
        }
        
        options = ConfigurableExtractionOptions(config=config)
        assert options.config == config
        assert 'name' in options.extraction_fields
        assert 'address' in options.extraction_fields
        assert options.field_priorities['name'] == 1
        assert options.output_format == 'json'

    def test_configure_extraction_fields_basic(self):
        """Test configuring basic extraction fields."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        fields = ['name', 'address', 'phone']
        
        options.configure_extraction_fields(fields)
        
        assert options.extraction_fields == fields
        assert len(options.extraction_fields) == 3
        assert 'name' in options.extraction_fields

    def test_configure_extraction_fields_with_priorities(self):
        """Test configuring extraction fields with priorities."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        fields = ['name', 'address', 'phone', 'menu']
        priorities = {'name': 1, 'address': 2, 'phone': 3, 'menu': 4}
        
        options.configure_extraction_fields(fields, priorities)
        
        assert options.extraction_fields == fields
        assert options.field_priorities == priorities
        assert options.field_priorities['name'] == 1
        assert options.field_priorities['menu'] == 4

    def test_configure_extraction_fields_with_field_objects(self):
        """Test configuring extraction fields with ExtractionField objects."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        name_field = ExtractionField(
            name='name',
            priority=1,
            required=True,
            extraction_method='heuristic',
            validation_rules=['not_empty', 'max_length:100']
        )
        
        address_field = ExtractionField(
            name='address',
            priority=2,
            required=True,
            extraction_method='structured',
            validation_rules=['not_empty', 'address_format']
        )
        
        fields = [name_field, address_field]
        options.configure_extraction_fields(fields)
        
        assert len(options.extraction_fields) == 2
        assert options.extraction_fields[0].name == 'name'
        assert options.extraction_fields[0].priority == 1
        assert options.extraction_fields[0].required is True

    def test_set_field_priorities_dynamic(self):
        """Test setting field priorities dynamically."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        options.configure_extraction_fields(['name', 'address', 'phone', 'menu'])
        
        # Set priorities dynamically
        options.set_field_priority('name', 1)
        options.set_field_priority('phone', 2)
        options.set_field_priority('address', 3)
        options.set_field_priority('menu', 4)
        
        assert options.field_priorities['name'] == 1
        assert options.field_priorities['phone'] == 2
        assert options.field_priorities['address'] == 3
        assert options.field_priorities['menu'] == 4

    def test_configure_output_format_json(self):
        """Test configuring JSON output format."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        options.configure_output_format('json', {
            'pretty_print': True,
            'include_metadata': True,
            'nested_structure': True
        })
        
        assert options.output_format == 'json'
        assert options.output_format_options['pretty_print'] is True
        assert options.output_format_options['include_metadata'] is True

    def test_configure_output_format_text(self):
        """Test configuring text output format."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        options.configure_output_format('text', {
            'separator': '\n---\n',
            'include_headers': True,
            'structured_sections': True
        })
        
        assert options.output_format == 'text'
        assert options.output_format_options['separator'] == '\n---\n'
        assert options.output_format_options['include_headers'] is True

    def test_configure_output_format_csv(self):
        """Test configuring CSV output format."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        options.configure_output_format('csv', {
            'delimiter': ',',
            'include_headers': True,
            'quote_character': '"',
            'escape_character': '\\'
        })
        
        assert options.output_format == 'csv'
        assert options.output_format_options['delimiter'] == ','
        assert options.output_format_options['quote_character'] == '"'

    def test_optimize_extraction_for_single_page(self):
        """Test extraction optimization for single-page processing."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        options.configure_extraction_fields(['name', 'address', 'phone'])
        
        with patch.object(options, 'extraction_optimizer') as mock_optimizer:
            mock_optimizer.optimize_for_single_page.return_value = True
            
            result = options.optimize_for_single_page()
            
            assert result is True
            mock_optimizer.optimize_for_single_page.assert_called_once()

    def test_optimize_extraction_for_multi_page(self):
        """Test extraction optimization for multi-page processing."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        options.configure_extraction_fields(['name', 'address', 'phone', 'menu'])
        
        with patch.object(options, 'extraction_optimizer') as mock_optimizer:
            mock_optimizer.optimize_for_multi_page.return_value = True
            
            result = options.optimize_for_multi_page()
            
            assert result is True
            mock_optimizer.optimize_for_multi_page.assert_called_once()

    def test_apply_extraction_configuration_to_scraper(self):
        """Test applying extraction configuration to scraper."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        options.configure_extraction_fields(['name', 'address', 'phone'])
        options.configure_output_format('json')
        
        mock_scraper = Mock()
        
        options.apply_to_scraper(mock_scraper)
        
        assert mock_scraper.configure_extraction_fields.called
        assert mock_scraper.configure_output_format.called

    def test_validate_extraction_configuration(self):
        """Test validation of extraction configuration."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        # Valid configuration
        valid_config = {
            'fields': ['name', 'address', 'phone'],
            'priorities': {'name': 1, 'address': 2, 'phone': 3},
            'output_format': 'json'
        }
        
        validation_result = options.validate_configuration(valid_config)
        
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0

    def test_validate_extraction_configuration_invalid(self):
        """Test validation of invalid extraction configuration."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        # Invalid configuration - missing required fields
        invalid_config = {
            'fields': [],  # Empty fields
            'priorities': {'name': 1},  # Priority for non-existent field
            'output_format': 'invalid_format'  # Invalid format
        }
        
        validation_result = options.validate_configuration(invalid_config)
        
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        assert any('empty fields' in error.lower() for error in validation_result.errors)

    def test_get_extraction_statistics(self):
        """Test getting extraction statistics."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        options.configure_extraction_fields(['name', 'address', 'phone', 'menu'])
        
        # Simulate some extraction results
        options.record_extraction_result('name', True, 0.95)
        options.record_extraction_result('address', True, 0.87)
        options.record_extraction_result('phone', False, 0.0)
        options.record_extraction_result('menu', True, 0.92)
        
        stats = options.get_extraction_statistics()
        
        assert stats.total_fields == 4
        assert stats.successful_extractions == 3
        assert stats.failed_extractions == 1
        assert stats.average_confidence == 0.685  # (0.95 + 0.87 + 0.0 + 0.92) / 4

    def test_field_extraction_success_rate(self):
        """Test field extraction success rate calculation."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        options.configure_extraction_fields(['name', 'address', 'phone'])
        
        # Simulate multiple extraction attempts
        for i in range(10):
            options.record_extraction_result('name', True, 0.9)
            options.record_extraction_result('address', i % 2 == 0, 0.8 if i % 2 == 0 else 0.0)
            options.record_extraction_result('phone', i % 3 == 0, 0.7 if i % 3 == 0 else 0.0)
        
        success_rates = options.get_field_success_rates()
        
        assert success_rates['name'] == 1.0  # 100% success
        assert success_rates['address'] == 0.5  # 50% success
        assert success_rates['phone'] == 0.4  # 40% success (4 out of 10)

    def test_dynamic_field_configuration_update(self):
        """Test dynamic field configuration updates."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        # Initial configuration
        options.configure_extraction_fields(['name', 'address'])
        assert len(options.extraction_fields) == 2
        
        # Add new field
        options.add_extraction_field('phone', priority=3)
        assert len(options.extraction_fields) == 3
        assert 'phone' in options.extraction_fields
        
        # Remove field
        options.remove_extraction_field('address')
        assert len(options.extraction_fields) == 2
        assert 'address' not in options.extraction_fields

    def test_extraction_field_conditional_logic(self):
        """Test conditional logic for extraction fields."""
        if ConfigurableExtractionOptions is None:
            pytest.skip("ConfigurableExtractionOptions not implemented yet")
        
        options = ConfigurableExtractionOptions()
        
        # Configure field with conditional logic
        phone_field = ExtractionField(
            name='phone',
            priority=1,
            required=True,
            conditions=['if_address_exists', 'if_contact_section_present']
        )
        
        options.configure_extraction_fields([phone_field])
        
        # Test with conditions met
        context = {
            'address_exists': True,
            'contact_section_present': True
        }
        
        should_extract = options.should_extract_field('phone', context)
        assert should_extract is True
        
        # Test with conditions not met
        context = {
            'address_exists': False,
            'contact_section_present': True
        }
        
        should_extract = options.should_extract_field('phone', context)
        assert should_extract is False


class TestExtractionField:
    """Test cases for ExtractionField."""

    def test_extraction_field_initialization(self):
        """Test extraction field initialization."""
        if ExtractionField is None:
            pytest.skip("ExtractionField not implemented yet")
        
        field = ExtractionField(
            name='restaurant_name',
            priority=1,
            required=True,
            extraction_method='heuristic',
            validation_rules=['not_empty', 'max_length:100']
        )
        
        assert field.name == 'restaurant_name'
        assert field.priority == 1
        assert field.required is True
        assert field.extraction_method == 'heuristic'
        assert 'not_empty' in field.validation_rules

    def test_extraction_field_validation_rules(self):
        """Test extraction field validation rules."""
        if ExtractionField is None:
            pytest.skip("ExtractionField not implemented yet")
        
        field = ExtractionField(
            name='phone',
            validation_rules=['not_empty', 'phone_format', 'length:10-15']
        )
        
        # Valid phone number
        assert field.validate('(555) 123-4567') is True
        
        # Invalid phone number
        assert field.validate('invalid-phone') is False
        assert field.validate('') is False  # Empty

    def test_extraction_field_extraction_methods(self):
        """Test extraction field extraction methods."""
        if ExtractionField is None:
            pytest.skip("ExtractionField not implemented yet")
        
        # Structured extraction
        structured_field = ExtractionField(
            name='address',
            extraction_method='structured',
            structured_selectors=['[itemProp="address"]', '.address']
        )
        
        assert structured_field.extraction_method == 'structured'
        assert '[itemProp="address"]' in structured_field.structured_selectors
        
        # Heuristic extraction
        heuristic_field = ExtractionField(
            name='hours',
            extraction_method='heuristic',
            heuristic_patterns=[r'hours?:?\s*(.+)', r'open:?\s*(.+)']
        )
        
        assert heuristic_field.extraction_method == 'heuristic'
        assert len(heuristic_field.heuristic_patterns) == 2

    def test_extraction_field_conditional_extraction(self):
        """Test extraction field conditional extraction."""
        if ExtractionField is None:
            pytest.skip("ExtractionField not implemented yet")
        
        field = ExtractionField(
            name='delivery_info',
            conditions=['if_delivery_mentioned', 'if_services_section_present'],
            conditional_logic='AND'
        )
        
        # Test AND logic - both conditions must be true
        context = {
            'delivery_mentioned': True,
            'services_section_present': True
        }
        
        assert field.should_extract(context) is True
        
        # Test AND logic - one condition false
        context = {
            'delivery_mentioned': True,
            'services_section_present': False
        }
        
        assert field.should_extract(context) is False

    def test_extraction_field_confidence_scoring(self):
        """Test extraction field confidence scoring."""
        if ExtractionField is None:
            pytest.skip("ExtractionField not implemented yet")
        
        field = ExtractionField(
            name='name',
            confidence_factors=[
                'structured_data_present',
                'multiple_sources_agree',
                'high_text_quality'
            ]
        )
        
        # High confidence scenario
        extraction_context = {
            'structured_data_present': True,
            'multiple_sources_agree': True,
            'high_text_quality': True,
            'extracted_value': 'Mario\'s Italian Restaurant'
        }
        
        confidence = field.calculate_confidence(extraction_context)
        assert confidence > 0.8  # Should be high confidence

    def test_extraction_field_fallback_methods(self):
        """Test extraction field fallback methods."""
        if ExtractionField is None:
            pytest.skip("ExtractionField not implemented yet")
        
        field = ExtractionField(
            name='phone',
            extraction_method='structured',
            fallback_methods=['heuristic', 'pattern_matching'],
            structured_selectors=['[itemProp="telephone"]'],
            heuristic_patterns=[r'phone:?\s*(.+)', r'call:?\s*(.+)']
        )
        
        # Test fallback when structured extraction fails
        html_content = '<div>Call us at (555) 123-4567</div>'
        
        with patch.object(field, 'extract_structured') as mock_structured:
            mock_structured.return_value = None  # Structured extraction fails
            
            with patch.object(field, 'extract_heuristic') as mock_heuristic:
                mock_heuristic.return_value = '(555) 123-4567'
                
                result = field.extract(html_content)
                
                assert result == '(555) 123-4567'
                mock_structured.assert_called_once()
                mock_heuristic.assert_called_once()


class TestFieldPriority:
    """Test cases for FieldPriority."""

    def test_field_priority_initialization(self):
        """Test field priority initialization."""
        if FieldPriority is None:
            pytest.skip("FieldPriority not implemented yet")
        
        priority = FieldPriority(field_name='name', priority=1, weight=0.9)
        
        assert priority.field_name == 'name'
        assert priority.priority == 1
        assert priority.weight == 0.9

    def test_field_priority_comparison(self):
        """Test field priority comparison."""
        if FieldPriority is None:
            pytest.skip("FieldPriority not implemented yet")
        
        high_priority = FieldPriority(field_name='name', priority=1)
        low_priority = FieldPriority(field_name='menu', priority=5)
        
        assert high_priority < low_priority  # Priority 1 < Priority 5 in sorting order
        assert low_priority > high_priority  # Priority 5 > Priority 1 in numerical comparison
        assert high_priority != low_priority

    def test_field_priority_sorting(self):
        """Test field priority sorting."""
        if FieldPriority is None:
            pytest.skip("FieldPriority not implemented yet")
        
        priorities = [
            FieldPriority(field_name='menu', priority=4),
            FieldPriority(field_name='name', priority=1),
            FieldPriority(field_name='address', priority=2),
            FieldPriority(field_name='phone', priority=3)
        ]
        
        sorted_priorities = sorted(priorities)
        
        assert sorted_priorities[0].field_name == 'name'  # Priority 1
        assert sorted_priorities[1].field_name == 'address'  # Priority 2
        assert sorted_priorities[2].field_name == 'phone'  # Priority 3
        assert sorted_priorities[3].field_name == 'menu'  # Priority 4


class TestOutputFormat:
    """Test cases for OutputFormat."""

    def test_output_format_initialization(self):
        """Test output format initialization."""
        if OutputFormat is None:
            pytest.skip("OutputFormat not implemented yet")
        
        format_obj = OutputFormat(
            format_type='json',
            options={'pretty_print': True, 'include_metadata': True}
        )
        
        assert format_obj.format_type == 'json'
        assert format_obj.options['pretty_print'] is True
        assert format_obj.options['include_metadata'] is True

    def test_output_format_json_formatting(self):
        """Test JSON output formatting."""
        if OutputFormat is None:
            pytest.skip("OutputFormat not implemented yet")
        
        format_obj = OutputFormat(
            format_type='json',
            options={'pretty_print': True, 'indent': 2}
        )
        
        data = {
            'name': 'Test Restaurant',
            'address': '123 Main St',
            'phone': '(555) 123-4567'
        }
        
        formatted_output = format_obj.format_data(data)
        
        assert '"name": "Test Restaurant"' in formatted_output
        assert '"address": "123 Main St"' in formatted_output
        assert '"phone": "(555) 123-4567"' in formatted_output

    def test_output_format_text_formatting(self):
        """Test text output formatting."""
        if OutputFormat is None:
            pytest.skip("OutputFormat not implemented yet")
        
        format_obj = OutputFormat(
            format_type='text',
            options={'separator': '\n---\n', 'include_headers': True}
        )
        
        data = {
            'name': 'Test Restaurant',
            'address': '123 Main St',
            'phone': '(555) 123-4567'
        }
        
        formatted_output = format_obj.format_data(data)
        
        assert 'Test Restaurant' in formatted_output
        assert '123 Main St' in formatted_output
        assert '(555) 123-4567' in formatted_output
        assert '---' in formatted_output

    def test_output_format_csv_formatting(self):
        """Test CSV output formatting."""
        if OutputFormat is None:
            pytest.skip("OutputFormat not implemented yet")
        
        format_obj = OutputFormat(
            format_type='csv',
            options={'delimiter': ',', 'include_headers': True}
        )
        
        data = [
            {'name': 'Restaurant 1', 'address': '123 Main St', 'phone': '(555) 123-4567'},
            {'name': 'Restaurant 2', 'address': '456 Oak Ave', 'phone': '(555) 987-6543'}
        ]
        
        formatted_output = format_obj.format_data(data)
        
        assert 'name,address,phone' in formatted_output  # Headers
        assert 'Restaurant 1,123 Main St,(555) 123-4567' in formatted_output
        assert 'Restaurant 2,456 Oak Ave,(555) 987-6543' in formatted_output


class TestExtractionOptimizer:
    """Test cases for ExtractionOptimizer."""

    def test_extraction_optimizer_initialization(self):
        """Test extraction optimizer initialization."""
        if ExtractionOptimizer is None:
            pytest.skip("ExtractionOptimizer not implemented yet")
        
        optimizer = ExtractionOptimizer()
        assert optimizer.optimization_strategies is not None
        assert optimizer.performance_metrics is not None

    def test_extraction_optimizer_single_page_optimization(self):
        """Test extraction optimizer single-page optimization."""
        if ExtractionOptimizer is None:
            pytest.skip("ExtractionOptimizer not implemented yet")
        
        optimizer = ExtractionOptimizer()
        fields = ['name', 'address', 'phone']
        
        optimization_result = optimizer.optimize_for_single_page(fields)
        
        assert optimization_result.optimized_fields is not None
        assert optimization_result.optimization_applied is True
        assert optimization_result.performance_gain > 0

    def test_extraction_optimizer_multi_page_optimization(self):
        """Test extraction optimizer multi-page optimization."""
        if ExtractionOptimizer is None:
            pytest.skip("ExtractionOptimizer not implemented yet")
        
        optimizer = ExtractionOptimizer()
        fields = ['name', 'address', 'phone', 'menu']
        
        optimization_result = optimizer.optimize_for_multi_page(fields)
        
        assert optimization_result.optimized_fields is not None
        assert optimization_result.batch_optimization_applied is True
        assert optimization_result.memory_optimization_applied is True
        assert optimization_result.performance_gain > 0

    def test_extraction_optimizer_performance_monitoring(self):
        """Test extraction optimizer performance monitoring."""
        if ExtractionOptimizer is None:
            pytest.skip("ExtractionOptimizer not implemented yet")
        
        optimizer = ExtractionOptimizer()
        
        # Simulate extraction operations
        optimizer.start_monitoring()
        
        # Simulate some processing time
        import time
        time.sleep(0.01)
        
        optimizer.stop_monitoring()
        
        metrics = optimizer.get_performance_metrics()
        
        assert metrics.total_extraction_time > 0
        assert metrics.average_field_extraction_time > 0
        assert metrics.memory_usage_peak > 0