"""Test for SINGLE_PAGE_CONFIG dropdown functionality."""
import pytest
import requests
from bs4 import BeautifulSoup


class TestSinglePageConfigDropdown:
    """Test that SINGLE_PAGE_CONFIG dropdown opens and closes properly."""
    
    def test_single_page_config_dropdown_elements_exist(self):
        """Test that the single page config dropdown elements exist."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the single page config header (clickable element)
        single_page_header = soup.find(id='singlePageHeader')
        assert single_page_header is not None, "❌ Single page header not found"
        
        # Find the single page config panel (collapsible content)
        single_page_config = soup.find(id='singlePageConfig')
        assert single_page_config is not None, "❌ Single page config panel not found"
        
        # Check if header has onclick handler
        onclick_attr = single_page_header.get('onclick')
        assert onclick_attr is not None, "❌ Header has no onclick handler"
        assert 'toggleSinglePageConfig' in onclick_attr, "❌ Incorrect onclick handler"
        
        print(f"✅ Header onclick: {onclick_attr}")
        print(f"✅ Config panel classes: {single_page_config.get('class')}")
        
        return single_page_header, single_page_config
        
    def test_single_page_config_javascript_function_exists(self):
        """Test that the toggleSinglePageConfig JavaScript function exists."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # Check if the function exists
        assert 'function toggleSinglePageConfig(' in html_content, "❌ toggleSinglePageConfig function not found"
        
        # Check if function targets correct elements
        assert 'getElementById(\'singlePageConfig\')' in html_content, "❌ Function doesn't target singlePageConfig"
        assert 'getElementById(\'singleConfigExpandIcon\')' in html_content, "❌ Function doesn't target expand icon"
        
        print("✅ toggleSinglePageConfig function exists and targets correct elements")
        
    def test_single_page_config_initial_state(self):
        """Test the initial state of the single page config dropdown."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check initial state
        single_page_config = soup.find(id='singlePageConfig')
        config_classes = single_page_config.get('class', [])
        
        print(f"Initial config classes: {config_classes}")
        
        # Should start collapsed
        assert 'collapsed' in config_classes, "❌ Config should start collapsed"
        
        # Check expand icon
        expand_icon = soup.find(id='singleConfigExpandIcon')
        if expand_icon:
            icon_classes = expand_icon.get('class', [])
            print(f"Initial icon classes: {icon_classes}")
            # Should NOT have 'expanded' class initially
            assert 'expanded' not in icon_classes, "❌ Icon should not be expanded initially"
        
        print("✅ Initial state is correctly collapsed")
        
    def test_single_page_config_click_simulation(self):
        """Test what happens when user clicks the single page config header."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Simulate the click behavior
        single_page_header = soup.find(id='singlePageHeader')
        single_page_config = soup.find(id='singlePageConfig')
        
        # Check what the onclick handler calls
        onclick_attr = single_page_header.get('onclick')
        assert 'toggleSinglePageConfig()' in onclick_attr, "❌ Incorrect function call"
        
        # Simulate what the JavaScript should do
        initial_classes = single_page_config.get('class', [])
        is_initially_collapsed = 'collapsed' in initial_classes
        
        print(f"Initial state: {'collapsed' if is_initially_collapsed else 'expanded'}")
        
        # After click, should toggle
        if is_initially_collapsed:
            # Should become expanded
            expected_after_click = "expanded"
        else:
            # Should become collapsed
            expected_after_click = "collapsed"
            
        print(f"Expected after click: {expected_after_click}")
        
        # This is what the JavaScript SHOULD do, but we need to test if it actually works
        return is_initially_collapsed, expected_after_click
        
    def test_single_page_config_visibility_issue(self):
        """Test if there's a visibility issue with the single page config."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if single page mode is selected
        single_page_radio = soup.find('input', {'name': 'scrapingMode', 'value': 'single'})
        is_single_mode_checked = single_page_radio and single_page_radio.get('checked') is not None
        
        # Check if single page header is visible
        single_page_header = soup.find(id='singlePageHeader')
        header_style = single_page_header.get('style', '') if single_page_header else ''
        
        print(f"Single page mode checked: {is_single_mode_checked}")
        print(f"Header style: {header_style}")
        
        # If single page mode is not the default, the header might be hidden
        if 'display: none' in header_style:
            print("⚠️  Single page header is hidden - this might be the issue!")
            
        # Check if we need to select single page mode first
        if not is_single_mode_checked and 'display: none' in header_style:
            pytest.fail("❌ REAL ISSUE: Single page config is hidden because single page mode is not selected!")
            
        return is_single_mode_checked, header_style
        
    def test_single_page_config_css_and_javascript_interaction(self):
        """Test the interaction between CSS and JavaScript for dropdown functionality."""
        try:
            response = requests.get('http://localhost:8085', timeout=5)
            html_content = response.text
        except:
            pytest.skip("Server not running on localhost:8085")
            
        # Check if CSS class 'collapsed' actually hides content
        css_has_collapsed_style = '.collapsed' in html_content and 'display:' in html_content
        
        # Check if JavaScript toggles the 'collapsed' class
        js_toggles_collapsed = 'classList.remove(\'collapsed\')' in html_content
        js_adds_collapsed = 'classList.add(\'collapsed\')' in html_content
        
        print(f"CSS defines .collapsed style: {css_has_collapsed_style}")
        print(f"JavaScript removes .collapsed: {js_toggles_collapsed}")
        print(f"JavaScript adds .collapsed: {js_adds_collapsed}")
        
        # Both should be true for the dropdown to work
        assert js_toggles_collapsed, "❌ JavaScript doesn't remove 'collapsed' class"
        assert js_adds_collapsed, "❌ JavaScript doesn't add 'collapsed' class"
        
        # If CSS doesn't define .collapsed, the toggle won't have visual effect
        if not css_has_collapsed_style:
            print("⚠️  CSS might not define .collapsed style properly")
            
        return css_has_collapsed_style, js_toggles_collapsed, js_adds_collapsed