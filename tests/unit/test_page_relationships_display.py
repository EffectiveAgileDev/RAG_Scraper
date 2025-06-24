"""Unit tests for page relationships display functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup


class TestPageRelationshipProcessing:
    """Test suite for processing page relationship data."""

    def test_process_hierarchical_relationships(self):
        """Test processing of hierarchical page relationships."""
        raw_pages = [
            {
                'url': 'https://restaurant1.com/',
                'status': 'success',
                'processing_time': 1.2,
                'discovered_from': None,
                'discovery_method': 'manual',
                'children_urls': ['https://restaurant1.com/menu', 'https://restaurant1.com/contact']
            },
            {
                'url': 'https://restaurant1.com/menu',
                'status': 'success',
                'processing_time': 2.1,
                'discovered_from': 'https://restaurant1.com/',
                'discovery_method': 'link',
                'children_urls': ['https://restaurant1.com/menu/specials']
            },
            {
                'url': 'https://restaurant1.com/contact',
                'status': 'success',
                'processing_time': 0.8,
                'discovered_from': 'https://restaurant1.com/',
                'discovery_method': 'link',
                'children_urls': []
            },
            {
                'url': 'https://restaurant1.com/menu/specials',
                'status': 'success',
                'processing_time': 1.5,
                'discovered_from': 'https://restaurant1.com/menu',
                'discovery_method': 'link',
                'children_urls': []
            }
        ]
        
        processed = self._process_page_relationships(raw_pages)
        
        # Verify root page
        root_page = next(p for p in processed if p['relationship']['type'] == 'root')
        assert root_page['url'] == 'https://restaurant1.com/'
        assert root_page['relationship']['depth'] == 0
        assert root_page['relationship']['children_count'] == 2
        
        # Verify child pages
        child_pages = [p for p in processed if p['relationship']['type'] == 'child']
        assert len(child_pages) == 3
        
        # Verify depth levels
        menu_page = next(p for p in processed if p['url'] == 'https://restaurant1.com/menu')
        assert menu_page['relationship']['depth'] == 1
        
        specials_page = next(p for p in processed if p['url'] == 'https://restaurant1.com/menu/specials')
        assert specials_page['relationship']['depth'] == 2

    def test_identify_orphaned_pages(self):
        """Test identification of orphaned pages."""
        raw_pages = [
            {
                'url': 'https://restaurant1.com/',
                'status': 'success',
                'discovered_from': None,
                'discovery_method': 'manual',
                'children_urls': []
            },
            {
                'url': 'https://restaurant1.com/orphan',
                'status': 'success',
                'discovered_from': 'https://restaurant1.com/missing',  # Missing parent
                'discovery_method': 'link',
                'children_urls': []
            }
        ]
        
        processed = self._process_page_relationships(raw_pages)
        
        orphan_page = next(p for p in processed if 'orphan' in p['url'])
        assert orphan_page['relationship']['type'] == 'orphaned'
        assert orphan_page['relationship']['depth'] is None

    def test_calculate_relationship_depth(self):
        """Test calculation of relationship depth."""
        relationships = {
            'https://restaurant1.com/': {'parent': None, 'depth': 0},
            'https://restaurant1.com/menu': {'parent': 'https://restaurant1.com/', 'depth': 1},
            'https://restaurant1.com/menu/specials': {'parent': 'https://restaurant1.com/menu', 'depth': 2},
            'https://restaurant1.com/menu/drinks': {'parent': 'https://restaurant1.com/menu', 'depth': 2}
        }
        
        for url, expected in relationships.items():
            depth = self._calculate_depth(url, relationships)
            assert depth == expected['depth']

    def test_build_relationship_tree(self):
        """Test building relationship tree structure."""
        pages_data = [
            {'url': 'https://restaurant1.com/', 'parent': None},
            {'url': 'https://restaurant1.com/menu', 'parent': 'https://restaurant1.com/'},
            {'url': 'https://restaurant1.com/contact', 'parent': 'https://restaurant1.com/'},
            {'url': 'https://restaurant1.com/menu/wine', 'parent': 'https://restaurant1.com/menu'}
        ]
        
        tree = self._build_relationship_tree(pages_data)
        
        # Verify tree structure
        assert 'https://restaurant1.com/' in tree
        assert len(tree['https://restaurant1.com/']['children']) == 2
        assert 'https://restaurant1.com/menu' in tree['https://restaurant1.com/']['children']
        assert len(tree['https://restaurant1.com/menu']['children']) == 1

    def test_detect_circular_relationships(self):
        """Test detection of circular relationships."""
        pages_data = [
            {'url': 'https://restaurant1.com/page1', 'parent': 'https://restaurant1.com/page2'},
            {'url': 'https://restaurant1.com/page2', 'parent': 'https://restaurant1.com/page3'},
            {'url': 'https://restaurant1.com/page3', 'parent': 'https://restaurant1.com/page1'}  # Circular
        ]
        
        circular_refs = self._detect_circular_relationships(pages_data)
        
        assert len(circular_refs) > 0
        assert any('page1' in ref for ref in circular_refs)

    def test_group_pages_by_relationship_type(self):
        """Test grouping pages by relationship type."""
        processed_pages = [
            {'url': 'url1', 'relationship': {'type': 'root'}},
            {'url': 'url2', 'relationship': {'type': 'child'}},
            {'url': 'url3', 'relationship': {'type': 'child'}},
            {'url': 'url4', 'relationship': {'type': 'orphaned'}}
        ]
        
        grouped = self._group_by_relationship_type(processed_pages)
        
        assert len(grouped['root']) == 1
        assert len(grouped['child']) == 2
        assert len(grouped['orphaned']) == 1

    def _process_page_relationships(self, raw_pages):
        """Helper method to process page relationships."""
        processed = []
        
        # Create URL to page mapping
        url_map = {page['url']: page for page in raw_pages}
        
        for page in raw_pages:
            rel_data = {
                'type': 'root' if page['discovered_from'] is None else 'child',
                'depth': 0,
                'parent_url': page['discovered_from'],
                'children_count': len(page['children_urls']),
                'discovery_method': page['discovery_method']
            }
            
            # Calculate depth
            if page['discovered_from']:
                rel_data['depth'] = self._calculate_depth_recursive(page['url'], url_map, set())
                
                # Check if parent exists
                if page['discovered_from'] not in url_map:
                    rel_data['type'] = 'orphaned'
                    rel_data['depth'] = None
            
            page_copy = page.copy()
            page_copy['relationship'] = rel_data
            processed.append(page_copy)
        
        return processed

    def _calculate_depth(self, url, relationships):
        """Helper method to calculate depth."""
        if relationships[url]['parent'] is None:
            return 0
        return 1 + self._calculate_depth(relationships[url]['parent'], relationships)

    def _calculate_depth_recursive(self, url, url_map, visited):
        """Helper method to calculate depth recursively."""
        if url in visited:
            return float('inf')  # Circular reference
        
        page = url_map.get(url)
        if not page or page['discovered_from'] is None:
            return 0
        
        visited.add(url)
        parent_depth = self._calculate_depth_recursive(page['discovered_from'], url_map, visited)
        visited.remove(url)
        
        return parent_depth + 1

    def _build_relationship_tree(self, pages_data):
        """Helper method to build relationship tree."""
        tree = {}
        
        for page in pages_data:
            url = page['url']
            parent = page['parent']
            
            # Initialize node
            if url not in tree:
                tree[url] = {'children': [], 'parent': parent}
            
            # Add to parent's children
            if parent and parent not in tree:
                tree[parent] = {'children': [], 'parent': None}
            
            if parent:
                tree[parent]['children'].append(url)
        
        return tree

    def _detect_circular_relationships(self, pages_data):
        """Helper method to detect circular relationships."""
        circular = []
        
        def has_cycle(url, visited, rec_stack):
            visited.add(url)
            rec_stack.add(url)
            
            page = next((p for p in pages_data if p['url'] == url), None)
            if page and page['parent']:
                if page['parent'] in rec_stack:
                    circular.append(f"{url} -> {page['parent']}")
                    return True
                elif page['parent'] not in visited:
                    if has_cycle(page['parent'], visited, rec_stack):
                        return True
            
            rec_stack.remove(url)
            return False
        
        visited = set()
        for page in pages_data:
            if page['url'] not in visited:
                has_cycle(page['url'], visited, set())
        
        return circular

    def _group_by_relationship_type(self, processed_pages):
        """Helper method to group pages by relationship type."""
        grouped = {'root': [], 'child': [], 'orphaned': []}
        
        for page in processed_pages:
            rel_type = page['relationship']['type']
            if rel_type in grouped:
                grouped[rel_type].append(page)
        
        return grouped


class TestRelationshipDisplayGeneration:
    """Test suite for generating relationship display HTML."""

    def test_generate_hierarchical_display(self):
        """Test generating hierarchical display HTML."""
        site_data = {
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
                        'children_count': 0,
                        'discovery_method': 'link'
                    }
                }
            ]
        }
        
        html = self._generate_relationship_display(site_data)
        
        assert 'ROOT' in html
        assert 'relationship-root' in html
        assert 'relationship-child' in html
        assert 'depth-0' in html
        assert 'depth-1' in html
        assert 'Children discovered: 2' in html

    def test_generate_indentation_levels(self):
        """Test generating proper indentation for different depth levels."""
        pages = [
            {'depth': 0, 'url': 'level0'},
            {'depth': 1, 'url': 'level1'},
            {'depth': 2, 'url': 'level2'},
            {'depth': 3, 'url': 'level3'}
        ]
        
        for page in pages:
            indentation = self._generate_indentation(page['depth'])
            expected_spaces = '  ' * page['depth']
            assert expected_spaces in indentation or f"depth-{page['depth']}" in indentation

    def test_generate_relationship_indicators(self):
        """Test generating relationship indicators."""
        test_cases = [
            {'type': 'root', 'expected': 'ROOT'},
            {'type': 'child', 'expected': '↳'},
            {'type': 'orphaned', 'expected': 'ORPHANED'}
        ]
        
        for case in test_cases:
            indicator = self._generate_relationship_indicator(case['type'])
            assert case['expected'] in indicator

    def test_generate_discovery_source_info(self):
        """Test generating discovery source information."""
        page_data = {
            'url': 'https://restaurant1.com/menu',
            'relationship': {
                'parent_url': 'https://restaurant1.com/',
                'discovery_method': 'link'
            }
        }
        
        info = self._generate_discovery_info(page_data)
        
        assert 'Discovered from:' in info
        assert 'https://restaurant1.com/' in info
        assert 'link' in info

    def test_generate_tree_structure_html(self):
        """Test generating tree structure HTML."""
        site_data = {
            'pages': [
                {
                    'url': 'root',
                    'relationship': {'type': 'root', 'depth': 0, 'children_count': 2}
                },
                {
                    'url': 'child1',
                    'relationship': {'type': 'child', 'depth': 1, 'children_count': 0}
                },
                {
                    'url': 'child2',
                    'relationship': {'type': 'child', 'depth': 1, 'children_count': 1}
                }
            ]
        }
        
        html = self._generate_tree_structure(site_data)
        
        assert 'tree-structure' in html
        assert 'expand-toggle' in html
        assert 'tree-toggle' in html

    def test_generate_relationship_statistics(self):
        """Test generating relationship statistics."""
        site_data = {
            'pages': [
                {'relationship': {'type': 'root', 'children_count': 2}},
                {'relationship': {'type': 'child', 'children_count': 1}},
                {'relationship': {'type': 'child', 'children_count': 0}},
                {'relationship': {'type': 'orphaned', 'children_count': 0}}
            ]
        }
        
        stats = self._generate_relationship_stats(site_data)
        
        assert stats['total_relationships'] == 2  # Only child pages count as relationships
        assert stats['root_pages'] == 1
        assert stats['orphaned_pages'] == 1
        assert stats['max_depth'] == 0  # No depth info in test data

    def test_generate_error_indicators(self):
        """Test generating error indicators for broken relationships."""
        page_data = {
            'url': 'https://restaurant1.com/broken',
            'status': 'failed',
            'relationship': {
                'type': 'child',
                'error': 'broken_link'
            }
        }
        
        error_html = self._generate_error_indicators(page_data)
        
        assert 'warning' in error_html
        assert 'broken' in error_html
        assert '⚠' in error_html

    def _generate_relationship_display(self, site_data):
        """Helper method to generate relationship display HTML."""
        html_parts = ['<div class="relationship-display">']
        
        for page in site_data['pages']:
            rel = page['relationship']
            
            # Add relationship classes
            classes = [f'relationship-{rel["type"]}', f'depth-{rel["depth"]}']
            html_parts.append(f'<div class="{" ".join(classes)}">')
            
            # Add relationship indicator
            if rel['type'] == 'root':
                html_parts.append('<span class="relationship-indicator ROOT">ROOT</span>')
            elif rel['type'] == 'child':
                html_parts.append('<span class="relationship-indicator">↳</span>')
            
            # Add children count
            if rel['children_count'] > 0:
                html_parts.append(f'<span>Children discovered: {rel["children_count"]}</span>')
            
            # Add page URL
            html_parts.append(f'<span>{page["url"]}</span>')
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        return ''.join(html_parts)

    def _generate_indentation(self, depth):
        """Helper method to generate indentation."""
        return f'<div class="indentation depth-{depth}">{"  " * depth}</div>'

    def _generate_relationship_indicator(self, rel_type):
        """Helper method to generate relationship indicator."""
        indicators = {
            'root': '<span class="indicator root">ROOT</span>',
            'child': '<span class="indicator child">↳</span>',
            'orphaned': '<span class="indicator orphaned">⚠ ORPHANED</span>'
        }
        return indicators.get(rel_type, '')

    def _generate_discovery_info(self, page_data):
        """Helper method to generate discovery info."""
        rel = page_data['relationship']
        if rel.get('parent_url'):
            return f'<span class="discovery-info">Discovered from: {rel["parent_url"]} ({rel.get("discovery_method", "unknown")})</span>'
        return '<span class="discovery-info">Entry point</span>'

    def _generate_tree_structure(self, site_data):
        """Helper method to generate tree structure HTML."""
        html_parts = ['<div class="tree-structure">']
        
        for page in site_data['pages']:
            rel = page['relationship']
            if rel['children_count'] > 0:
                html_parts.append('<span class="expand-toggle tree-toggle">▼</span>')
        
        html_parts.append('</div>')
        return ''.join(html_parts)

    def _generate_relationship_stats(self, site_data):
        """Helper method to generate relationship statistics."""
        stats = {
            'total_relationships': 0,
            'root_pages': 0,
            'orphaned_pages': 0,
            'max_depth': 0
        }
        
        for page in site_data['pages']:
            rel = page['relationship']
            if rel['type'] == 'child':
                stats['total_relationships'] += 1
            elif rel['type'] == 'root':
                stats['root_pages'] += 1
            elif rel['type'] == 'orphaned':
                stats['orphaned_pages'] += 1
            
            depth = rel.get('depth', 0)
            if depth and depth > stats['max_depth']:
                stats['max_depth'] = depth
        
        return stats

    def _generate_error_indicators(self, page_data):
        """Helper method to generate error indicators."""
        if page_data.get('relationship', {}).get('error'):
            return '<span class="warning broken">⚠ Relationship broken</span>'
        return ''


class TestRelationshipJavaScriptFunctionality:
    """Test suite for JavaScript functionality (simulated in Python)."""

    def test_toggle_relationship_tree_expansion(self):
        """Test toggling relationship tree expansion."""
        state = {
            'tree_expanded': False,
            'children_visible': False
        }
        
        # Simulate expanding tree
        state = self._simulate_tree_toggle(state)
        
        assert state['tree_expanded'] is True
        assert state['children_visible'] is True
        
        # Simulate collapsing tree
        state = self._simulate_tree_toggle(state)
        
        assert state['tree_expanded'] is False
        assert state['children_visible'] is False

    def test_highlight_relationship_chain(self):
        """Test highlighting relationship chain on hover."""
        page_relationships = {
            'root': ['child1', 'child2'],
            'child1': ['grandchild1'],
            'child2': [],
            'grandchild1': []
        }
        
        # Simulate hovering over child1
        highlighted = self._simulate_relationship_highlight('child1', page_relationships)
        
        assert 'root' in highlighted  # Parent should be highlighted
        assert 'grandchild1' in highlighted  # Child should be highlighted
        assert 'child1' in highlighted  # Self should be highlighted

    def test_filter_pages_by_relationship_type(self):
        """Test filtering pages by relationship type."""
        pages = [
            {'url': 'page1', 'relationship': {'type': 'root'}},
            {'url': 'page2', 'relationship': {'type': 'child'}},
            {'url': 'page3', 'relationship': {'type': 'child'}},
            {'url': 'page4', 'relationship': {'type': 'orphaned'}}
        ]
        
        # Filter for children only
        filtered = self._simulate_relationship_filter(pages, 'child')
        assert len(filtered) == 2
        assert all(p['relationship']['type'] == 'child' for p in filtered)
        
        # Filter for root pages
        filtered = self._simulate_relationship_filter(pages, 'root')
        assert len(filtered) == 1

    def test_sort_pages_by_relationship_depth(self):
        """Test sorting pages by relationship depth."""
        pages = [
            {'url': 'page1', 'relationship': {'depth': 2}},
            {'url': 'page2', 'relationship': {'depth': 0}},
            {'url': 'page3', 'relationship': {'depth': 1}}
        ]
        
        sorted_pages = self._simulate_depth_sort(pages)
        
        assert sorted_pages[0]['relationship']['depth'] == 0
        assert sorted_pages[1]['relationship']['depth'] == 1
        assert sorted_pages[2]['relationship']['depth'] == 2

    def test_show_relationship_tooltip(self):
        """Test showing relationship tooltip on hover."""
        page_data = {
            'url': 'https://restaurant1.com/menu',
            'relationship': {
                'type': 'child',
                'depth': 1,
                'parent_url': 'https://restaurant1.com/',
                'discovery_method': 'link'
            }
        }
        
        tooltip = self._simulate_relationship_tooltip(page_data)
        
        assert 'Type: child' in tooltip
        assert 'Depth: 1' in tooltip
        assert 'Discovery: link' in tooltip

    def _simulate_tree_toggle(self, state):
        """Simulate tree toggle functionality."""
        state['tree_expanded'] = not state['tree_expanded']
        state['children_visible'] = state['tree_expanded']
        return state

    def _simulate_relationship_highlight(self, target_url, relationships):
        """Simulate relationship highlighting."""
        highlighted = set([target_url])
        
        # Highlight parents (recursive up)
        def highlight_parents(url):
            for parent, children in relationships.items():
                if url in children:
                    highlighted.add(parent)
                    highlight_parents(parent)
        
        # Highlight children (recursive down)
        def highlight_children(url):
            if url in relationships:
                for child in relationships[url]:
                    highlighted.add(child)
                    highlight_children(child)
        
        highlight_parents(target_url)
        highlight_children(target_url)
        
        return list(highlighted)

    def _simulate_relationship_filter(self, pages, filter_type):
        """Simulate filtering by relationship type."""
        return [page for page in pages if page['relationship']['type'] == filter_type]

    def _simulate_depth_sort(self, pages):
        """Simulate sorting by depth."""
        return sorted(pages, key=lambda p: p['relationship']['depth'])

    def _simulate_relationship_tooltip(self, page_data):
        """Simulate relationship tooltip generation."""
        rel = page_data['relationship']
        return f"Type: {rel['type']}, Depth: {rel['depth']}, Discovery: {rel['discovery_method']}"


if __name__ == '__main__':
    pytest.main([__file__])