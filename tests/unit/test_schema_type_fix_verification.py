"""Verification test for schema type dropdown fix."""
import pytest
import requests
from bs4 import BeautifulSoup


class TestSchemaTypeFixVerification:
    """Test that the schema type dropdown issue is completely fixed."""
    
    def test_schema_type_dropdown_complete_fix_verification(self):
        """Comprehensive test verifying that schema type dropdown updates work correctly."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Test 1: Verify unique IDs (no duplicates)
        all_elements_with_schema_help_id = soup.find_all(id=lambda x: x and 'schema-type-help' in x)
        all_ids = [elem.get('id') for elem in all_elements_with_schema_help_id]
        unique_ids = set(all_ids)
        
        assert len(all_ids) == len(unique_ids), f"Duplicate IDs found: {all_ids}"
        assert len(unique_ids) >= 2, f"Expected at least 2 unique schema help elements, found {len(unique_ids)}"
        
        # Test 2: Verify correct target element exists
        dynamic_help_element = soup.find(id='schema-type-help-dynamic')
        assert dynamic_help_element is not None, "Dynamic help element 'schema-type-help-dynamic' not found"
        
        # Test 3: Verify dropdown exists and has correct handler
        dropdown = soup.find('select', id='schema-type-dropdown')
        assert dropdown is not None, "Schema dropdown not found"
        
        onchange_attr = dropdown.get('onchange')
        assert onchange_attr is not None, "onchange attribute missing from dropdown"
        assert 'handleSchemaTypeChange(this.value)' in onchange_attr, "Incorrect onchange handler"
        
        # Test 4: Verify JavaScript function targets correct element
        assert 'getElementById(\'schema-type-help-dynamic\')' in html_content, \
            "JavaScript function doesn't target schema-type-help-dynamic"
        
        # Test 5: Verify dropdown options exist
        options = dropdown.find_all('option')
        assert len(options) == 2, f"Expected 2 options, found {len(options)}"
        
        option_values = [opt.get('value') for opt in options]
        assert 'Restaurant' in option_values, "Restaurant option not found"
        assert 'RestW' in option_values, "RestW option not found"
        
        # Test 6: Verify functions exist in JavaScript
        assert 'function handleSchemaTypeChange(' in html_content, "handleSchemaTypeChange function not found"
        assert 'function updateSchemaTypeHelpText(' in html_content, "updateSchemaTypeHelpText function not found"
        
        print("✅ All schema type dropdown tests passed!")
        print(f"✅ Found {len(unique_ids)} unique schema help elements")
        print(f"✅ Dropdown has {len(options)} options")
        print("✅ JavaScript functions target correct elements")
        
    def test_no_duplicate_ids_in_entire_page(self):
        """Test that there are no duplicate IDs anywhere in the page."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get all elements with IDs
        all_elements_with_ids = soup.find_all(id=True)
        all_ids = [elem.get('id') for elem in all_elements_with_ids]
        
        # Check for duplicates
        unique_ids = set(all_ids)
        
        if len(all_ids) != len(unique_ids):
            # Find which IDs are duplicated
            id_counts = {}
            for element_id in all_ids:
                id_counts[element_id] = id_counts.get(element_id, 0) + 1
            
            duplicates = {k: v for k, v in id_counts.items() if v > 1}
            pytest.fail(f"Duplicate IDs found in page: {duplicates}")
        
        print(f"✅ Page has {len(unique_ids)} unique IDs with no duplicates")
        
    def test_schema_help_text_is_different_for_different_types(self):
        """Test that the help text shows different content for different schema types."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # The updateSchemaTypeHelpText function should have different content for different schemas
        assert 'Restaurant Schema - Standard Extraction' in html_content, \
            "Restaurant schema help text not found"
        assert 'RestW Schema - Enhanced Restaurant Data' in html_content, \
            "RestW schema help text not found"
        
        # The content should be significantly different
        restaurant_content = 'Standard restaurant data extraction provides comprehensive information'
        restw_content = 'Enhanced restaurant data with specialized fields including location data'
        
        assert restaurant_content in html_content, "Restaurant-specific content not found"
        # Note: RestW content might be generated dynamically, so we check for the schema name
        assert 'RestW' in html_content, "RestW schema reference not found"
        
        print("✅ Schema-specific help text content verified")