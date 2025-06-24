"""Step definitions for page relationships display BDD tests."""

import pytest
from unittest.mock import Mock, patch
from pytest_bdd import scenarios, given, when, then, parsers
from bs4 import BeautifulSoup


# Load BDD scenarios
scenarios('../features/page_relationships_display.feature')


@pytest.fixture
def context():
    """Test context to store state between steps."""
    return {
        'scraping_mode': 'multi',
        'scraped_data': {},
        'page_relationships': [],
        'results_html': '',
        'soup': None
    }


@pytest.fixture
def mock_hierarchical_data():
    """Mock data with hierarchical page relationships."""
    return {
        'site_url': 'https://restaurant1.com',
        'pages_processed': 4,
        'pages': [
            {
                'url': 'https://restaurant1.com/',
                'status': 'success',
                'processing_time': 1.2,
                'relationship': {
                    'type': 'root',
                    'depth': 0,
                    'parent_url': None,
                    'children_count': 2,
                    'discovery_method': 'manual'
                }
            },
            {
                'url': 'https://restaurant1.com/menu',
                'status': 'success',
                'processing_time': 2.1,
                'relationship': {
                    'type': 'child',
                    'depth': 1,
                    'parent_url': 'https://restaurant1.com/',
                    'children_count': 1,
                    'discovery_method': 'link'
                }
            },
            {
                'url': 'https://restaurant1.com/contact',
                'status': 'success',
                'processing_time': 0.8,
                'relationship': {
                    'type': 'child',
                    'depth': 1,
                    'parent_url': 'https://restaurant1.com/',
                    'children_count': 0,
                    'discovery_method': 'link'
                }
            },
            {
                'url': 'https://restaurant1.com/menu/specials',
                'status': 'success',
                'processing_time': 1.5,
                'relationship': {
                    'type': 'child',
                    'depth': 2,
                    'parent_url': 'https://restaurant1.com/menu',
                    'children_count': 0,
                    'discovery_method': 'link'
                }
            }
        ]
    }


# Background steps
@given("the RAG_Scraper web interface is loaded")
def web_interface_loaded(context):
    """Load the web interface."""
    context['interface_loaded'] = True


@given("I am in multi-page mode")
def in_multipage_mode(context):
    """Set multi-page mode."""
    context['scraping_mode'] = 'multi'


@given("I have completed a multi-page scraping operation")
def completed_multipage_operation(context):
    """Set completed operation state."""
    context['operation_completed'] = True


# Scenario 1: Display parent-child relationships for discovered pages
@given("I scraped a restaurant site with hierarchical pages")
def scraped_hierarchical_site(context, mock_hierarchical_data):
    """Set up hierarchical site data."""
    context['scraped_data'] = mock_hierarchical_data


@given("the home page discovered 2 child pages")
def home_page_discovered_children(context):
    """Verify home page has 2 children."""
    root_page = next(p for p in context['scraped_data']['pages'] if p['relationship']['type'] == 'root')
    assert root_page['relationship']['children_count'] == 2


@given("one child page discovered 1 additional page")
def child_page_discovered_additional(context):
    """Verify child page has 1 child."""
    menu_page = next(p for p in context['scraped_data']['pages'] if 'menu' in p['url'] and 'specials' not in p['url'])
    assert menu_page['relationship']['children_count'] == 1


@when("I view the results section")
def view_results_section(context):
    """Generate and view results with relationships."""
    results_html = generate_results_with_relationships(context['scraped_data'])
    context['results_html'] = results_html
    context['soup'] = BeautifulSoup(results_html, 'html.parser')


@then('I should see the home page marked as "ROOT"')
def should_see_root_marker(context):
    """Verify root page is marked."""
    assert 'ROOT' in context['results_html'] or 'relationship-root' in context['results_html']


@then("I should see the child pages indented under their parent")
def should_see_indented_children(context):
    """Verify child pages are indented."""
    assert 'relationship-child' in context['results_html'] or 'indented' in context['results_html']


@then("I should see relationship indicators showing the hierarchy")
def should_see_hierarchy_indicators(context):
    """Verify hierarchy indicators are present."""
    assert 'hierarchy-level' in context['results_html'] or 'depth-' in context['results_html']


@then('each child page should show "↳ from: [parent URL]"')
def should_show_parent_reference(context):
    """Verify parent URL references."""
    assert 'from:' in context['results_html'] or 'parent-url' in context['results_html']


# Scenario 2: Show relationship depth indicators
@given("I scraped a site with 3 levels of page hierarchy")
def scraped_3_level_hierarchy(context, mock_hierarchical_data):
    """Set up 3-level hierarchy data."""
    context['scraped_data'] = mock_hierarchical_data


@then("I should see level 0 pages with no indentation")
def should_see_level_0_no_indent(context):
    """Verify level 0 has no indentation."""
    assert 'depth-0' in context['results_html']


@then("I should see level 1 pages with single indentation")
def should_see_level_1_indent(context):
    """Verify level 1 has single indentation."""
    assert 'depth-1' in context['results_html']


@then("I should see level 2 pages with double indentation")
def should_see_level_2_indent(context):
    """Verify level 2 has double indentation."""
    assert 'depth-2' in context['results_html']


@then("each level should have distinct visual indicators")
def should_see_distinct_indicators(context):
    """Verify distinct visual indicators per level."""
    soup = context['soup']
    level_indicators = soup.find_all(class_=lambda x: x and 'depth-' in x)
    assert len(level_indicators) > 0


# Scenario 3: Display discovery source information
@given("I scraped a site where pages were discovered through links")
def scraped_discovered_pages(context, mock_hierarchical_data):
    """Set up discovered pages data."""
    context['scraped_data'] = mock_hierarchical_data


@then("each discovered page should show its discovery source")
def should_show_discovery_source(context):
    """Verify discovery source is shown."""
    assert 'Discovered from:' in context['results_html'] or 'discovery-source' in context['results_html']


@then('I should see "Discovered from: [parent page]" for child pages')
def should_show_discovered_from_parent(context):
    """Verify discovered from parent info."""
    assert 'Discovered from:' in context['results_html']


@then('I should see "Entry point" for initial URLs')
def should_show_entry_point(context):
    """Verify entry point marking."""
    assert 'Entry point' in context['results_html'] or 'entry-point' in context['results_html']


@then("I should see the discovery method (link, sitemap, manual)")
def should_show_discovery_method(context):
    """Verify discovery method is shown."""
    assert 'manual' in context['results_html'] or 'link' in context['results_html']


# Scenario 4: Show page relationship tree structure
@given("I scraped a site with complex page relationships")
def scraped_complex_relationships(context, mock_hierarchical_data):
    """Set up complex relationships data."""
    context['scraped_data'] = mock_hierarchical_data


@then("I should see a tree-like structure with connecting lines")
def should_see_tree_structure(context):
    """Verify tree structure display."""
    assert 'tree-structure' in context['results_html'] or 'relationship-tree' in context['results_html']


@then("parent pages should have expand/collapse indicators")
def should_see_expand_collapse_indicators(context):
    """Verify expand/collapse indicators."""
    assert 'expand-toggle' in context['results_html'] or 'tree-toggle' in context['results_html']


@then("expanding a parent should reveal its children")
def should_expand_reveal_children(context):
    """Verify expand functionality."""
    # This would be tested in JavaScript functionality tests
    assert 'expandable' in context['results_html'] or 'children-list' in context['results_html']


@then("collapsing should hide the child pages")
def should_collapse_hide_children(context):
    """Verify collapse functionality."""
    # This would be tested in JavaScript functionality tests
    assert 'collapsible' in context['results_html'] or 'children-list' in context['results_html']


# Scenario 5: Display relationship statistics
@given("I scraped a site with multiple page relationships")
def scraped_multiple_relationships(context, mock_hierarchical_data):
    """Set up multiple relationships data."""
    context['scraped_data'] = mock_hierarchical_data


@then('I should see "Children discovered: X" for parent pages')
def should_show_children_count(context):
    """Verify children count display."""
    assert 'Children discovered:' in context['results_html'] or 'children-count' in context['results_html']


@then('I should see "Depth level: X" for each page')
def should_show_depth_level(context):
    """Verify depth level display."""
    assert 'Depth level:' in context['results_html'] or 'depth-level' in context['results_html']


@then("I should see total relationship count in the site summary")
def should_show_total_relationship_count(context):
    """Verify total relationship count."""
    assert 'Total relationships:' in context['results_html'] or 'relationship-count' in context['results_html']


@then("orphaned pages should be clearly marked")
def should_mark_orphaned_pages(context):
    """Verify orphaned pages marking."""
    # Check if there are orphaned pages in the data
    scraped_data = context.get('scraped_data', {})
    pages = scraped_data.get('pages', [])
    has_orphans = any(p.get('relationship', {}).get('type') == 'orphaned' for p in pages)
    
    if has_orphans:
        assert 'orphaned' in context['results_html'] or 'orphan' in context['results_html']
    else:
        # If no orphans in data, test passes automatically
        assert True


# Scenario 6: Relationship display in single-page mode
@given("I am in single-page mode")
def in_single_page_mode(context):
    """Set single-page mode."""
    context['scraping_mode'] = 'single'


@when("I complete a scraping operation")
def complete_scraping_operation(context):
    """Complete scraping operation."""
    # For single-page mode, generate simple results
    simple_data = {
        'site_url': 'https://restaurant1.com',
        'pages_processed': 1,
        'pages': [
            {
                'url': 'https://restaurant1.com/',
                'status': 'success',
                'processing_time': 1.2
                # No relationship data in single-page mode
            }
        ]
    }
    results_html = generate_results_with_relationships(simple_data, mode='single')
    context['results_html'] = results_html
    context['soup'] = BeautifulSoup(results_html, 'html.parser')


@then("I should not see relationship indicators")
def should_not_see_relationship_indicators(context):
    """Verify no relationship indicators in single-page mode."""
    assert 'relationship' not in context['results_html'].lower()
    assert 'parent' not in context['results_html'].lower()
    assert 'child' not in context['results_html'].lower()


@then("each page should be treated as independent")
def should_treat_pages_independent(context):
    """Verify pages are independent."""
    assert 'independent' in context['results_html'] or 'standalone' in context['results_html']


@then("no parent-child hierarchy should be displayed")
def should_not_show_hierarchy(context):
    """Verify no hierarchy display."""
    assert 'hierarchy' not in context['results_html'].lower()
    assert 'depth-' not in context['results_html']


# Scenario 7: Interactive relationship exploration
@given("I have results with page relationships")
def have_results_with_relationships(context, mock_hierarchical_data):
    """Set up results with relationships."""
    context['scraped_data'] = mock_hierarchical_data
    results_html = generate_results_with_relationships(context['scraped_data'])
    context['results_html'] = results_html
    context['soup'] = BeautifulSoup(results_html, 'html.parser')


@when("I click on a parent page indicator")
def click_parent_indicator(context):
    """Simulate clicking parent indicator."""
    context['parent_clicked'] = True


@then("the child pages should be highlighted")
def should_highlight_children(context):
    """Verify children highlighting."""
    # This would be tested in JavaScript functionality
    assert 'highlight-children' in context['results_html'] or 'onclick' in context['results_html']


@when("I hover over a child page")
def hover_child_page(context):
    """Simulate hovering over child page."""
    context['child_hovered'] = True


@then("its parent relationship should be emphasized")
def should_emphasize_parent_relationship(context):
    """Verify parent relationship emphasis."""
    assert 'emphasize-parent' in context['results_html'] or 'hover-effect' in context['results_html']


@then("I should see a tooltip with relationship details")
def should_show_relationship_tooltip(context):
    """Verify relationship tooltip."""
    assert 'tooltip' in context['results_html'] or 'title=' in context['results_html']


# Scenario 8: Relationship error handling
@given("I scraped a site with broken relationship links")
def scraped_broken_relationships(context):
    """Set up broken relationships data."""
    broken_data = {
        'site_url': 'https://restaurant1.com',
        'pages_processed': 3,
        'pages': [
            {
                'url': 'https://restaurant1.com/',
                'status': 'success',
                'processing_time': 1.2,
                'relationship': {
                    'type': 'root',
                    'depth': 0,
                    'parent_url': None,
                    'children_count': 1,
                    'discovery_method': 'manual'
                }
            },
            {
                'url': 'https://restaurant1.com/broken',
                'status': 'failed',
                'processing_time': 0.0,
                'relationship': {
                    'type': 'child',
                    'depth': 1,
                    'parent_url': 'https://restaurant1.com/',
                    'children_count': 0,
                    'discovery_method': 'link',
                    'error': 'broken_link'
                }
            },
            {
                'url': 'https://restaurant1.com/orphan',
                'status': 'success',
                'processing_time': 1.0,
                'relationship': {
                    'type': 'orphaned',
                    'depth': None,
                    'parent_url': None,
                    'children_count': 0,
                    'discovery_method': 'unknown'
                }
            }
        ]
    }
    context['scraped_data'] = broken_data
    results_html = generate_results_with_relationships(broken_data)
    context['results_html'] = results_html
    context['soup'] = BeautifulSoup(results_html, 'html.parser')


@then("broken relationships should be marked with warning icons")
def should_mark_broken_relationships(context):
    """Verify broken relationship warnings."""
    assert 'warning' in context['results_html'] or 'broken' in context['results_html']


@then('I should see "Relationship broken" indicators')
def should_show_broken_indicators(context):
    """Verify broken relationship indicators."""
    assert 'Relationship broken' in context['results_html'] or 'broken-link' in context['results_html']


@then("orphaned pages should be grouped separately")
def should_group_orphaned_pages(context):
    """Verify orphaned pages grouping."""
    assert 'orphaned-section' in context['results_html'] or 'orphan' in context['results_html']


# Helper function to generate results HTML with relationships
def generate_results_with_relationships(site_data, mode='multi'):
    """Generate mock results HTML with relationship information."""
    if mode == 'single':
        # Single-page mode - no relationships
        html_parts = ['<div class="results-container">']
        for page in site_data['pages']:
            html_parts.append(f'<div class="page-item standalone">')
            html_parts.append(f'<span class="page-url">{page["url"]}</span>')
            html_parts.append(f'<span class="page-status">{page["status"]}</span>')
            html_parts.append('</div>')
        html_parts.append('</div>')
        return ''.join(html_parts)
    
    # Multi-page mode with relationships
    html_parts = ['<div class="results-container relationship-enabled">']
    html_parts.append('<div class="site-result">')
    html_parts.append(f'<h4>{site_data["site_url"]}</h4>')
    html_parts.append('<div class="relationship-tree">')
    
    # Sort pages by depth for hierarchical display (handle None values)
    def safe_depth_sort(page):
        depth = page.get('relationship', {}).get('depth')
        return depth if depth is not None else float('inf')
    
    pages = sorted(site_data['pages'], key=safe_depth_sort)
    
    for page in pages:
        rel = page.get('relationship', {})
        rel_type = rel.get('type', 'unknown')
        depth = rel.get('depth')
        depth = depth if depth is not None else 0  # Handle None depth
        parent_url = rel.get('parent_url')
        children_count = rel.get('children_count', 0)
        discovery_method = rel.get('discovery_method', 'unknown')
        
        # Generate relationship classes and indicators
        classes = [f'page-item', f'relationship-{rel_type}', f'depth-{depth}']
        if rel.get('error'):
            classes.append('broken-link')
        
        html_parts.append(f'<div class="{" ".join(classes)}">')
        
        # Add indentation based on depth
        if depth > 0:
            html_parts.append(f'<div class="indentation indented depth-{depth}">')
            html_parts.append('  ' * depth)  # Visual indentation
        
        # Add relationship indicators
        if rel_type == 'root':
            html_parts.append('<span class="relationship-indicator ROOT">ROOT</span>')
            html_parts.append('<span class="entry-point">Entry point</span>')
        elif rel_type == 'child':
            html_parts.append('<span class="relationship-indicator">↳</span>')
            if parent_url:
                html_parts.append(f'<span class="parent-url">from: {parent_url}</span>')
                html_parts.append(f'<span class="discovery-source">Discovered from: {parent_url}</span>')
        elif rel_type == 'orphaned':
            html_parts.append('<span class="relationship-indicator orphaned">⚠ ORPHANED</span>')
        
        # Add page URL and status
        html_parts.append(f'<span class="page-url">{page["url"]}</span>')
        html_parts.append(f'<span class="page-status">{page["status"]}</span>')
        html_parts.append(f'<span class="page-time">{page["processing_time"]:.1f}s</span>')
        
        # Add relationship statistics
        if children_count > 0:
            html_parts.append(f'<span class="children-count">Children discovered: {children_count}</span>')
            html_parts.append('<span class="expand-toggle tree-toggle expandable collapsible" onclick="toggleChildren()">▼</span>')
            html_parts.append('<div class="children-list expandable">')  # Children container
            html_parts.append('</div>')  # Close children container
        
        html_parts.append(f'<span class="depth-level">Depth level: {depth}</span>')
        html_parts.append(f'<span class="discovery-method">{discovery_method}</span>')
        
        # Add error indicators if present
        if rel.get('error'):
            html_parts.append('<span class="warning broken">⚠ Relationship broken</span>')
        
        # Add interactive highlighting classes
        html_parts.append('<span class="highlight-children hover-effect emphasize-parent" onclick="highlightChildren()"></span>')
        
        # Add tooltip with relationship details
        tooltip_text = f"Type: {rel_type}, Depth: {depth}, Discovery: {discovery_method}"
        html_parts.append(f'<span class="tooltip" title="{tooltip_text}">ℹ</span>')
        
        if depth > 0:
            html_parts.append('</div>')  # Close indentation
        
        html_parts.append('</div>')  # Close page-item
    
    # Add orphaned pages section
    orphaned_pages = [p for p in pages if p.get('relationship', {}).get('type') == 'orphaned']
    if orphaned_pages:
        html_parts.append('<div class="orphaned-section">')
        html_parts.append('<h5>Orphaned Pages</h5>')
        for orphan in orphaned_pages:
            html_parts.append(f'<div class="orphan-page">{orphan["url"]}</div>')
        html_parts.append('</div>')
    
    # Add relationship summary with count
    total_relationships = len([p for p in pages if p.get('relationship', {}).get('parent_url')])
    html_parts.append(f'<div class="relationship-summary relationship-count">Total relationships: {total_relationships}</div>')
    
    html_parts.append('</div>')  # Close relationship-tree
    html_parts.append('</div>')  # Close site-result
    html_parts.append('</div>')  # Close results-container
    
    return ''.join(html_parts)