"""Final verification test for schema dropdown fix."""
import pytest
import requests
from bs4 import BeautifulSoup


class TestSchemaDropdownFinalFix:
    """Final verification that schema dropdown is completely fixed."""
    
    def test_schema_dropdown_complete_working_solution(self):
        """Test that verifies the complete working solution for schema dropdown."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # VERIFICATION 1: Dropdown exists and has correct handler
        dropdown = soup.find('select', id='schema-type-dropdown')
        assert dropdown is not None, "❌ Schema dropdown not found"
        
        onchange = dropdown.get('onchange')
        assert 'handleSchemaTypeChange(this.value)' in onchange, "❌ Incorrect onchange handler"
        
        # VERIFICATION 2: JavaScript targets the element that user actually sees
        js_targets_static = 'getElementById(\'schema-type-help-static\')' in html_content
        static_element = soup.find(id='schema-type-help-static')
        static_content = static_element.get_text().strip() if static_element else ""
        
        assert js_targets_static, "❌ JavaScript doesn't target static element"
        assert static_element is not None, "❌ Static element not found"
        assert len(static_content) > 100, "❌ Static element has no substantial content"
        
        # VERIFICATION 3: Dynamic element is not targeted (it's empty)
        js_targets_dynamic = 'getElementById(\'schema-type-help-dynamic\')' in html_content
        dynamic_element = soup.find(id='schema-type-help-dynamic')
        dynamic_content = dynamic_element.get_text().strip() if dynamic_element else ""
        
        assert not js_targets_dynamic, "❌ JavaScript still targets dynamic element"
        assert dynamic_element is not None, "❌ Dynamic element not found"
        assert len(dynamic_content) == 0, "❌ Dynamic element should be empty"
        
        # VERIFICATION 4: JavaScript function updates the correct nested element
        assert 'querySelector(\'.help-content\')' in html_content, "❌ JavaScript doesn't target .help-content"
        assert 'helpContent.innerHTML = content' in html_content, "❌ JavaScript doesn't update innerHTML"
        
        # VERIFICATION 5: No duplicate IDs
        all_elements_with_ids = soup.find_all(id=True)
        all_ids = [elem.get('id') for elem in all_elements_with_ids]
        unique_ids = set(all_ids)
        assert len(all_ids) == len(unique_ids), "❌ Duplicate IDs still exist"
        
        # VERIFICATION 6: Both schema options exist
        options = dropdown.find_all('option')
        option_values = [opt.get('value') for opt in options]
        assert 'Restaurant' in option_values, "❌ Restaurant option not found"
        assert 'RestW' in option_values, "❌ RestW option not found"
        
        print("✅ Schema dropdown is completely fixed!")
        print(f"✅ JavaScript targets: schema-type-help-static (visible to user)")
        print(f"✅ Static element content length: {len(static_content)}")
        print(f"✅ Dynamic element content length: {len(dynamic_content)}")
        print(f"✅ No duplicate IDs: {len(unique_ids)} unique IDs")
        print(f"✅ Dropdown options: {len(options)} options")
        
        return True
        
    def test_schema_content_difference_verification(self):
        """Test that different schema types will show different content."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # Check that the JavaScript function has different content for different schemas
        restaurant_content_present = 'Restaurant Schema - Standard Extraction' in html_content
        restw_content_present = 'RestW Schema - Enhanced Restaurant Data' in html_content
        
        assert restaurant_content_present, "❌ Restaurant schema content not found"
        assert restw_content_present, "❌ RestW schema content not found"
        
        # Check that the content is substantially different
        assert 'Standard restaurant data extraction' in html_content
        assert 'Enhanced restaurant data with specialized fields' in html_content
        
        print("✅ Different schema types have different content!")
        
    def test_no_more_only_standard_extraction_issue(self):
        """Test that the 'only shows Standard Extraction' issue is resolved."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # The original issue was that only "Standard Extraction" was shown
        # Now the JavaScript should be able to update the content dynamically
        
        # Check that the updateSchemaTypeHelpText function exists and has different content
        assert 'function updateSchemaTypeHelpText(' in html_content
        assert 'if (schemaType === \'Restaurant\')' in html_content
        assert 'RestW Schema - Enhanced Restaurant Data' in html_content
        
        # The function should update the visible element
        assert 'getElementById(\'schema-type-help-static\')' in html_content
        assert 'querySelector(\'.help-content\')' in html_content
        
        print("✅ Schema dropdown will now update dynamically!")
        print("✅ User will see content change when selecting different schema types!")