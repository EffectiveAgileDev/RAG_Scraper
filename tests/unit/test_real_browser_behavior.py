"""Test that actually simulates browser behavior for schema dropdown."""
import pytest
import requests
from bs4 import BeautifulSoup


class TestRealBrowserBehavior:
    """Test that simulates actual browser behavior to catch real issues."""
    
    def test_schema_dropdown_change_simulation(self):
        """Test that simulates what happens when user changes dropdown in browser."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Step 1: Find the dropdown
        dropdown = soup.find('select', id='schema-type-dropdown')
        assert dropdown is not None, "Schema dropdown not found"
        
        # Step 2: Check what the onchange handler calls
        onchange = dropdown.get('onchange')
        assert 'handleSchemaTypeChange(this.value)' in onchange
        
        # Step 3: Find what element the JavaScript actually targets
        # This is the critical test - we need to see if the element exists
        
        # Look for the getElementById call in the JavaScript
        if 'getElementById(\'schema-type-help-static\')' in html_content:
            target_id = 'schema-type-help-static'
        elif 'getElementById(\'schema-type-help-dynamic\')' in html_content:
            target_id = 'schema-type-help-dynamic'
        elif 'getElementById(\'schema-type-help\')' in html_content:
            target_id = 'schema-type-help'
        else:
            pytest.fail("Cannot find getElementById call for schema help in JavaScript")
            
        # Step 4: Check if the target element actually exists in the DOM
        target_element = soup.find(id=target_id)
        
        if target_element is None:
            pytest.fail(f"REAL ISSUE FOUND: JavaScript targets '{target_id}' but this element doesn't exist in DOM!")
            
        # Step 5: Check if the target element is the one that should be updated
        # The dynamic help element should be empty initially (gets populated by JS)
        if target_id == 'schema-type-help-dynamic':
            # This should be empty initially
            content = target_element.get_text().strip()
            print(f"Dynamic element content: '{content}'")
            # If it's empty, that's good - it should be populated by JavaScript
            
        # Step 6: Check if there are multiple elements and JavaScript targets wrong one
        all_schema_help_elements = soup.find_all(id=lambda x: x and 'schema-type-help' in x)
        print(f"Found schema help elements: {[elem.get('id') for elem in all_schema_help_elements]}")
        
        if len(all_schema_help_elements) > 1:
            # Multiple elements exist - which one has content and which one is empty?
            for elem in all_schema_help_elements:
                elem_id = elem.get('id')
                elem_content = elem.get_text().strip()
                print(f"Element {elem_id}: {'HAS CONTENT' if elem_content else 'EMPTY'}")
                
                # If JavaScript targets the empty one, but user sees the one with content,
                # then the dropdown won't appear to work
                if elem_id == target_id and elem_content:
                    print(f"JavaScript targets {elem_id} which has content - this should work")
                elif elem_id == target_id and not elem_content:
                    print(f"JavaScript targets {elem_id} which is empty - check if this gets updated")
                    
        return target_id, target_element
        
    def test_which_schema_help_element_is_visible_to_user(self):
        """Test which schema help element the user actually sees."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all schema help elements
        schema_help_elements = soup.find_all(id=lambda x: x and 'schema-type-help' in x)
        
        visible_content_elements = []
        empty_elements = []
        
        for elem in schema_help_elements:
            elem_id = elem.get('id')
            elem_content = elem.get_text().strip()
            
            if elem_content and len(elem_content) > 50:  # Has substantial content
                visible_content_elements.append((elem_id, len(elem_content)))
            else:
                empty_elements.append(elem_id)
                
        print(f"Elements with visible content: {visible_content_elements}")
        print(f"Empty elements: {empty_elements}")
        
        # The user sees the element with content, but JavaScript might target an empty one
        if len(visible_content_elements) == 1 and len(empty_elements) >= 1:
            visible_id = visible_content_elements[0][0]
            
            # Check what JavaScript targets
            if 'getElementById(\'schema-type-help-dynamic\')' in html_content:
                js_target = 'schema-type-help-dynamic'
            elif 'getElementById(\'schema-type-help\')' in html_content:
                js_target = 'schema-type-help'
            else:
                js_target = 'unknown'
                
            if js_target in empty_elements:
                pytest.fail(f"REAL ISSUE: User sees content in '{visible_id}' but JavaScript updates '{js_target}' which is empty!")
                
    def test_static_vs_dynamic_content_issue(self):
        """Test if the issue is static vs dynamic content."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if there's a static help element with pre-populated content
        static_help = soup.find(id='schema-type-help-static')
        dynamic_help = soup.find(id='schema-type-help-dynamic')
        
        if static_help:
            static_content = static_help.get_text().strip()
            print(f"Static help content length: {len(static_content)}")
            print(f"Static help visible: {len(static_content) > 0}")
            
        if dynamic_help:
            dynamic_content = dynamic_help.get_text().strip()
            print(f"Dynamic help content length: {len(dynamic_content)}")
            print(f"Dynamic help visible: {len(dynamic_content) > 0}")
            
        # Check what JavaScript targets
        js_targets_dynamic = 'getElementById(\'schema-type-help-dynamic\')' in html_content
        js_targets_static = 'getElementById(\'schema-type-help-static\')' in html_content
        
        print(f"JavaScript targets dynamic: {js_targets_dynamic}")
        print(f"JavaScript targets static: {js_targets_static}")
        
        # The issue might be:
        # 1. User sees static content (which doesn't change)
        # 2. JavaScript updates dynamic content (which is hidden or empty)
        if static_help and len(static_content) > 50 and dynamic_help and len(dynamic_content) == 0:
            if js_targets_dynamic:
                pytest.fail("REAL ISSUE: User sees static content but JavaScript updates dynamic (empty) element!")
                
        return {
            'static_visible': static_help and len(static_content) > 0,
            'dynamic_visible': dynamic_help and len(dynamic_content) > 0,
            'js_targets_dynamic': js_targets_dynamic,
            'js_targets_static': js_targets_static
        }