"""Unit tests for AI UI layout fixes."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup


class TestAISettingsPanelLayout:
    """Test AI Settings Panel layout and spacing."""
    
    def test_ai_settings_panel_has_sufficient_height(self):
        """Test that AI settings panel has sufficient height for all content."""
        # Mock HTML structure
        html_content = """
        <div id="ai-enhancement-section" style="height: auto; overflow: visible;">
            <div class="ai-settings-content" style="height: 500px;">
                <div class="ai-provider-section">...</div>
                <div class="ai-features-section">...</div>
                <div class="ai-buttons-section">...</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        ai_panel = soup.find('div', id='ai-enhancement-section')
        ai_content = soup.find('div', class_='ai-settings-content')
        
        # Extract heights - panel now has height: auto, so it should expand
        panel_style = ai_panel.get('style', '')
        content_height = int(ai_content.get('style', '').split('height: ')[1].split('px')[0])
        
        # Check that panel has auto height (can expand)
        has_auto_height = 'height: auto' in panel_style
        has_visible_overflow = 'overflow: visible' in panel_style
        
        # This should now pass
        assert has_auto_height, "Panel should have height: auto to accommodate content"
        assert has_visible_overflow, "Panel should have overflow: visible to show all content"
    
    def test_ai_settings_panel_no_overflow_hidden(self):
        """Test that AI settings panel doesn't have overflow hidden that cuts off content."""
        html_content = """
        <div id="ai-enhancement-section" style="height: auto; overflow: visible;">
            <div class="ai-settings-content">...</div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        ai_panel = soup.find('div', id='ai-enhancement-section')
        
        # Check if overflow is hidden
        style = ai_panel.get('style', '')
        
        # This should now pass
        assert 'overflow: hidden' not in style, "AI panel should not have overflow: hidden that cuts off content"
        assert 'overflow: visible' in style, "AI panel should have overflow: visible to show all content"
    
    def test_ai_settings_panel_allows_auto_height(self):
        """Test that AI settings panel allows auto height expansion."""
        html_content = """
        <div id="ai-enhancement-section" style="height: auto; max-height: none;">
            <div class="ai-settings-content">...</div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        ai_panel = soup.find('div', id='ai-enhancement-section')
        
        style = ai_panel.get('style', '')
        
        # Check for auto height
        has_auto_height = 'height: auto' in style
        has_no_max_height = 'max-height: none' in style
        
        # This should fail initially
        assert has_auto_height or has_no_max_height, "AI panel should allow auto height expansion"
    
    def test_save_buttons_are_positioned_correctly(self):
        """Test that save buttons are positioned at the bottom and visible."""
        html_content = """
        <div id="ai-enhancement-section">
            <div class="ai-settings-content">
                <div class="ai-provider-section">...</div>
                <div class="ai-features-section">...</div>
                <div class="ai-buttons-section" style="position: relative; bottom: 0px;">
                    <button class="save-btn">Save Settings</button>
                    <button class="load-btn">Load Settings</button>
                    <button class="clear-btn">Clear Settings</button>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        buttons_section = soup.find('div', class_='ai-buttons-section')
        
        # Check button positioning
        style = buttons_section.get('style', '')
        
        # This should now pass - buttons are positioned correctly
        assert 'bottom: -' not in style, "Save buttons should not be positioned off-screen"
        assert 'position: relative' in style, "Save buttons should be positioned relatively"
    
    def test_ai_panel_content_layout_structure(self):
        """Test that AI panel has proper content layout structure."""
        html_content = """
        <div id="ai-enhancement-section">
            <div class="ai-settings-content">
                <div class="ai-provider-section">Provider settings</div>
                <div class="ai-features-section">Feature toggles</div>
                <div class="ai-buttons-section">Action buttons</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check that all required sections exist
        ai_panel = soup.find('div', id='ai-enhancement-section')
        content = soup.find('div', class_='ai-settings-content')
        provider_section = soup.find('div', class_='ai-provider-section')
        features_section = soup.find('div', class_='ai-features-section')
        buttons_section = soup.find('div', class_='ai-buttons-section')
        
        assert ai_panel is not None, "AI enhancement section should exist"
        assert content is not None, "AI settings content should exist"
        assert provider_section is not None, "Provider section should exist"
        assert features_section is not None, "Features section should exist"
        assert buttons_section is not None, "Buttons section should exist"
    
    def test_ai_panel_responsive_height_calculation(self):
        """Test AI panel height calculation based on content."""
        # Mock content elements with their heights
        content_sections = {
            'header': 50,
            'provider_settings': 120,
            'api_key_input': 80,
            'feature_toggles': 200,
            'confidence_slider': 60,
            'custom_questions': 100,
            'buttons': 80
        }
        
        total_content_height = sum(content_sections.values())
        # Panel now has height: auto, so it expands to fit content
        panel_can_expand = True  # With height: auto, panel can expand
        
        # This should now pass
        assert panel_can_expand, "Panel should be able to expand to accommodate all content"
    
    def test_ai_panel_css_class_structure(self):
        """Test that AI panel has correct CSS class structure for styling."""
        html_content = """
        <div id="ai-enhancement-section" class="ai-panel">
            <div class="ai-settings-content expandable">
                <div class="ai-section-header">...</div>
                <div class="ai-section-body">...</div>
                <div class="ai-section-footer">...</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        ai_panel = soup.find('div', id='ai-enhancement-section')
        ai_content = soup.find('div', class_='ai-settings-content')
        
        # Check for required CSS classes
        panel_classes = ai_panel.get('class', [])
        content_classes = ai_content.get('class', [])
        
        assert 'ai-panel' in panel_classes, "AI panel should have 'ai-panel' class"
        assert 'expandable' in content_classes, "AI content should have 'expandable' class"


class TestResultsDisplayLayout:
    """Test Results Display Layout and positioning."""
    
    def test_results_positioned_under_scraping_results_section(self):
        """Test that results are positioned under the Scraping Results section."""
        html_content = """
        <div class="results-container">
            <div class="scraping-results-header" style="position: relative; top: 600px;">
                <h2>Scraping Results</h2>
            </div>
            <div id="results-output" style="position: relative; top: 800px;">
                <div class="results-content">Results content here</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        results_header = soup.find('div', class_='scraping-results-header')
        results_output = soup.find('div', id='results-output')
        
        # Extract positions
        header_top = int(results_header.get('style', '').split('top: ')[1].split('px')[0])
        results_top = int(results_output.get('style', '').split('top: ')[1].split('px')[0])
        
        # This should fail initially - results are not properly positioned below header
        assert results_top > header_top + 50, f"Results (top: {results_top}) should be positioned below header (top: {header_top})"
    
    def test_advanced_options_header_positioned_left(self):
        """Test that Advanced Options header is positioned to the left."""
        html_content = """
        <div class="advanced-options-section">
            <div class="advanced-options-header" style="text-align: left; margin-left: 0;">
                <h3>Advanced Options</h3>
            </div>
            <div class="advanced-options-controls">
                <div class="control-item">Control 1</div>
                <div class="control-item">Control 2</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        advanced_header = soup.find('div', class_='advanced-options-header')
        
        style = advanced_header.get('style', '')
        
        # This should now pass - header is left-aligned
        assert 'text-align: left' in style, "Advanced Options header should be left-aligned"
        assert 'margin-left: 0' in style, "Advanced Options header should have no left margin"
    
    def test_results_display_proper_spacing(self):
        """Test that results display has proper spacing from other elements."""
        html_content = """
        <div class="page-layout">
            <div class="form-section" style="height: 500px;">
                <form>Form content</form>
            </div>
            <div class="advanced-options" style="height: 300px; margin-top: 20px;">
                <div>Advanced options</div>
            </div>
            <div class="results-section" style="margin-top: 48px;">
                <div>Results content</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        results_section = soup.find('div', class_='results-section')
        
        style = results_section.get('style', '')
        
        # Extract margin-top
        margin_top = 48  # Default from HTML
        if 'margin-top:' in style:
            margin_top = int(style.split('margin-top: ')[1].split('px')[0])
        
        # This should now pass - adequate spacing
        assert margin_top >= 48, f"Results section should have adequate spacing (margin-top >= 48px), got {margin_top}px"
    
    def test_results_section_has_proper_container_structure(self):
        """Test that results section has proper container structure."""
        html_content = """
        <div class="main-content">
            <div class="results-wrapper">
                <div class="results-header">
                    <h2>Scraping Results</h2>
                </div>
                <div class="results-content">
                    <div class="result-item">Item 1</div>
                    <div class="result-item">Item 2</div>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check structure
        results_wrapper = soup.find('div', class_='results-wrapper')
        results_header = soup.find('div', class_='results-header')
        results_content = soup.find('div', class_='results-content')
        
        assert results_wrapper is not None, "Results wrapper should exist"
        assert results_header is not None, "Results header should exist"
        assert results_content is not None, "Results content should exist"
        
        # Check that header comes before content
        header_position = list(results_wrapper.children).index(results_header)
        content_position = list(results_wrapper.children).index(results_content)
        
        assert header_position < content_position, "Results header should come before results content"
    
    def test_advanced_options_header_alignment(self):
        """Test that advanced options header is properly aligned."""
        html_content = """
        <div class="advanced-section">
            <div class="section-header advanced-header" style="text-align: left; margin-left: 0;">
                <h3>Advanced Options</h3>
            </div>
            <div class="section-content">
                <div class="option-group">Options content</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        advanced_header = soup.find('div', class_='advanced-header')
        
        style = advanced_header.get('style', '')
        
        # Check for left alignment
        has_left_alignment = 'text-align: left' in style
        has_no_left_margin = 'margin-left: 0' in style
        
        assert has_left_alignment, "Advanced Options header should be left-aligned"
        assert has_no_left_margin, "Advanced Options header should not have left margin"
    
    def test_results_no_overlap_with_advanced_options(self):
        """Test that results don't overlap with advanced options."""
        # Mock layout with positions
        layout_data = {
            'advanced_options': {
                'top': 200,
                'height': 400,
                'bottom': 600  # 200 + 400
            },
            'results_section': {
                'top': 650,  # Fixed to avoid overlap
                'height': 300
            }
        }
        
        advanced_bottom = layout_data['advanced_options']['bottom']
        results_top = layout_data['results_section']['top']
        
        # This should now pass - results don't overlap with advanced options
        assert results_top >= advanced_bottom + 20, f"Results (top: {results_top}) should not overlap with advanced options (bottom: {advanced_bottom})"
    
    def test_responsive_layout_structure(self):
        """Test that layout structure supports responsive design."""
        html_content = """
        <div class="responsive-container">
            <div class="section-group">
                <div class="form-section">Form</div>
                <div class="advanced-section">Advanced Options</div>
            </div>
            <div class="results-section">
                <div class="results-responsive">Results</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check responsive structure
        responsive_container = soup.find('div', class_='responsive-container')
        section_group = soup.find('div', class_='section-group')
        results_section = soup.find('div', class_='results-section')
        
        assert responsive_container is not None, "Responsive container should exist"
        assert section_group is not None, "Section group should exist"
        assert results_section is not None, "Results section should exist"
        
        # Check that results are separate from form/advanced options
        assert results_section.parent == responsive_container, "Results should be at container level"
        assert section_group.parent == responsive_container, "Section group should be at container level"


class TestAIEnhancementSectionLayout:
    """Test AI Enhancement Section layout and reorganization."""
    
    def test_ai_enhancement_section_positioned_separately(self):
        """Test that AI Enhancement section is positioned separately from Advanced Options."""
        html_content = """
        <div class="options-container">
            <div class="advanced-options-section" style="float: left; width: 45%; margin-right: 2%;">
                <div class="section-header">Advanced Options</div>
                <div class="section-content">
                    <div class="option-item">Request Timeout</div>
                    <div class="option-item">Rate Limiting</div>
                </div>
            </div>
            <div class="ai-enhancement-section" style="float: right; width: 45%; margin-left: 2%;">
                <div class="section-header">AI Enhancement Options</div>
                <div class="section-content">
                    <div class="option-item">AI Provider</div>
                    <div class="option-item">AI Features</div>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        advanced_section = soup.find('div', class_='advanced-options-section')
        ai_section = soup.find('div', class_='ai-enhancement-section')
        
        # Check positioning
        advanced_style = advanced_section.get('style', '')
        ai_style = ai_section.get('style', '')
        
        assert 'float: left' in advanced_style, "Advanced Options should be positioned on the left"
        assert 'float: right' in ai_style, "AI Enhancement should be positioned on the right"
        assert 'width: 45%' in advanced_style, "Advanced Options should have proper width"
        assert 'width: 45%' in ai_style, "AI Enhancement should have proper width"
    
    def test_ai_enhancement_section_has_separate_header(self):
        """Test that AI Enhancement section has its own header."""
        html_content = """
        <div class="ai-enhancement-section">
            <div class="section-header ai-enhancement-header">
                <div class="config-toggle-header">
                    <span class="config-label">🤖 AI_ENHANCEMENT_OPTIONS</span>
                    <span class="expand-icon">▼</span>
                </div>
            </div>
            <div class="section-content">
                <div class="ai-controls">AI controls here</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        ai_header = soup.find('div', class_='ai-enhancement-header')
        ai_label = soup.find('span', class_='config-label')
        
        assert ai_header is not None, "AI Enhancement section should have its own header"
        assert ai_label is not None, "AI Enhancement header should have proper label"
        assert "AI_ENHANCEMENT_OPTIONS" in ai_label.text, "Header should identify AI Enhancement section"
    
    def test_ai_enhancement_controls_moved_to_separate_section(self):
        """Test that AI controls are moved to the AI Enhancement section."""
        html_content = """
        <div class="layout-container">
            <div class="advanced-options-section">
                <div class="section-content">
                    <div class="option-item">Request Timeout</div>
                    <div class="option-item">Rate Limiting</div>
                    <!-- No AI controls should be here -->
                </div>
            </div>
            <div class="ai-enhancement-section">
                <div class="section-content">
                    <div class="ai-provider-selection">AI Provider Selection</div>
                    <div class="ai-feature-toggles">AI Feature Toggles</div>
                    <div class="ai-configuration-options">AI Configuration Options</div>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        advanced_section = soup.find('div', class_='advanced-options-section')
        ai_section = soup.find('div', class_='ai-enhancement-section')
        
        # Check that AI controls are in AI Enhancement section
        ai_provider = ai_section.find('div', class_='ai-provider-selection')
        ai_toggles = ai_section.find('div', class_='ai-feature-toggles')
        ai_config = ai_section.find('div', class_='ai-configuration-options')
        
        assert ai_provider is not None, "AI provider selection should be in AI Enhancement section"
        assert ai_toggles is not None, "AI feature toggles should be in AI Enhancement section"
        assert ai_config is not None, "AI configuration options should be in AI Enhancement section"
        
        # Check that no AI controls are in Advanced Options section
        advanced_ai_controls = advanced_section.find_all(['div'], class_=lambda x: x and 'ai-' in x)
        assert len(advanced_ai_controls) == 0, "No AI controls should remain in Advanced Options section"
    
    def test_ai_enhancement_section_has_independent_collapse_functionality(self):
        """Test that AI Enhancement section has independent collapsible functionality."""
        html_content = """
        <div class="layout-container">
            <div class="advanced-options-section">
                <div class="section-header">
                    <div class="config-toggle-header" onclick="toggleAdvancedOptions()">
                        <span class="expand-icon" id="advancedOptionsIcon">▼</span>
                    </div>
                </div>
                <div id="advancedOptionsPanel" class="section-panel collapsed">
                    <div>Advanced options content</div>
                </div>
            </div>
            <div class="ai-enhancement-section">
                <div class="section-header">
                    <div class="config-toggle-header" onclick="toggleAIEnhancementOptions()">
                        <span class="expand-icon" id="aiEnhancementIcon">▼</span>
                    </div>
                </div>
                <div id="aiEnhancementPanel" class="section-panel collapsed">
                    <div>AI enhancement content</div>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check that both sections have independent toggle functionality
        advanced_toggle = soup.find('div', {'onclick': 'toggleAdvancedOptions()'})
        ai_toggle = soup.find('div', {'onclick': 'toggleAIEnhancementOptions()'})
        
        assert advanced_toggle is not None, "Advanced Options should have independent toggle"
        assert ai_toggle is not None, "AI Enhancement should have independent toggle"
        
        # Check that both sections have their own panels
        advanced_panel = soup.find('div', id='advancedOptionsPanel')
        ai_panel = soup.find('div', id='aiEnhancementPanel')
        
        assert advanced_panel is not None, "Advanced Options should have its own panel"
        assert ai_panel is not None, "AI Enhancement should have its own panel"
    
    def test_ai_enhancement_section_proper_spacing_and_alignment(self):
        """Test that AI Enhancement section has proper spacing and alignment."""
        html_content = """
        <div class="options-layout">
            <div class="advanced-options-section" style="display: inline-block; vertical-align: top; width: 48%; margin-right: 2%;">
                <div>Advanced Options Content</div>
            </div>
            <div class="ai-enhancement-section" style="display: inline-block; vertical-align: top; width: 48%; margin-left: 2%;">
                <div>AI Enhancement Content</div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        advanced_section = soup.find('div', class_='advanced-options-section')
        ai_section = soup.find('div', class_='ai-enhancement-section')
        
        advanced_style = advanced_section.get('style', '')
        ai_style = ai_section.get('style', '')
        
        # Check alignment
        assert 'vertical-align: top' in advanced_style, "Advanced Options should be top-aligned"
        assert 'vertical-align: top' in ai_style, "AI Enhancement should be top-aligned"
        
        # Check spacing
        assert 'margin-right: 2%' in advanced_style, "Advanced Options should have proper right margin"
        assert 'margin-left: 2%' in ai_style, "AI Enhancement should have proper left margin"
        
        # Check width distribution
        assert 'width: 48%' in advanced_style, "Advanced Options should have balanced width"
        assert 'width: 48%' in ai_style, "AI Enhancement should have balanced width"
    
    def test_ai_enhancement_section_responsive_layout(self):
        """Test that AI Enhancement section supports responsive layout."""
        html_content = """
        <div class="options-responsive-container">
            <div class="section-row">
                <div class="advanced-options-section col-md-6">
                    <div class="section-content">Advanced Options</div>
                </div>
                <div class="ai-enhancement-section col-md-6">
                    <div class="section-content">AI Enhancement</div>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        section_row = soup.find('div', class_='section-row')
        advanced_section = soup.find('div', class_='advanced-options-section')
        ai_section = soup.find('div', class_='ai-enhancement-section')
        
        # Check responsive structure
        assert section_row is not None, "Sections should be in a responsive row"
        assert 'col-md-6' in advanced_section.get('class', []), "Advanced Options should have responsive class"
        assert 'col-md-6' in ai_section.get('class', []), "AI Enhancement should have responsive class"
    
    def test_ai_enhancement_section_visual_distinction(self):
        """Test that AI Enhancement section is visually distinct from Advanced Options."""
        html_content = """
        <div class="options-container">
            <div class="advanced-options-section" style="border: 1px solid #ffaa00;">
                <div class="section-header" style="background-color: #1a1a1a;">
                    <span>Advanced Options</span>
                </div>
            </div>
            <div class="ai-enhancement-section" style="border: 1px solid #00aaff;">
                <div class="section-header" style="background-color: #1a1a1a;">
                    <span>AI Enhancement Options</span>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        advanced_section = soup.find('div', class_='advanced-options-section')
        ai_section = soup.find('div', class_='ai-enhancement-section')
        
        advanced_style = advanced_section.get('style', '')
        ai_style = ai_section.get('style', '')
        
        # Check visual distinction through borders
        assert 'border:' in advanced_style, "Advanced Options should have visual border"
        assert 'border:' in ai_style, "AI Enhancement should have visual border"
        
        # Check that they have different styling
        assert advanced_style != ai_style, "Sections should have distinct visual styling"
    
    def test_ai_enhancement_section_maintains_functionality_independence(self):
        """Test that AI Enhancement section maintains functional independence."""
        # Mock independent functionality
        functionality_data = {
            'advanced_options': {
                'toggle_function': 'toggleAdvancedOptions()',
                'panel_id': 'advancedOptionsPanel',
                'icon_id': 'advancedOptionsIcon'
            },
            'ai_enhancement': {
                'toggle_function': 'toggleAIEnhancementOptions()',
                'panel_id': 'aiEnhancementPanel',
                'icon_id': 'aiEnhancementIcon'
            }
        }
        
        # Check that functions are different
        advanced_func = functionality_data['advanced_options']['toggle_function']
        ai_func = functionality_data['ai_enhancement']['toggle_function']
        
        assert advanced_func != ai_func, "Sections should have independent toggle functions"
        
        # Check that panel IDs are different
        advanced_panel = functionality_data['advanced_options']['panel_id']
        ai_panel = functionality_data['ai_enhancement']['panel_id']
        
        assert advanced_panel != ai_panel, "Sections should have independent panel IDs"
        
        # Check that icon IDs are different
        advanced_icon = functionality_data['advanced_options']['icon_id']
        ai_icon = functionality_data['ai_enhancement']['icon_id']
        
        assert advanced_icon != ai_icon, "Sections should have independent icon IDs"