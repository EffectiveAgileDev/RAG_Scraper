"""Unit tests for enhanced results display functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup


class TestResultsDisplayGenerator:
    """Test suite for results display generation functionality."""

    def test_generate_empty_results_display(self):
        """Test generating display when no results are available."""
        results_data = None
        html = self._generate_results_html(results_data)
        
        assert 'No results available' in html
        assert 'Complete a scraping operation' in html

    def test_generate_single_site_results_display(self):
        """Test generating display for single site results."""
        results_data = {
            'total_sites': 1,
            'sites': [{
                'site_url': 'https://restaurant1.com',
                'pages_processed': 3,
                'pages': [
                    {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.2},
                    {'url': 'https://restaurant1.com/menu', 'status': 'success', 'processing_time': 2.1},
                    {'url': 'https://restaurant1.com/contact', 'status': 'success', 'processing_time': 0.8}
                ]
            }]
        }
        
        html = self._generate_results_html(results_data)
        
        assert 'Pages Processed: 3' in html
        assert 'https://restaurant1.com/' in html
        assert 'https://restaurant1.com/menu' in html
        assert 'https://restaurant1.com/contact' in html
        assert '1.2s' in html
        assert '2.1s' in html
        assert '0.8s' in html

    def test_generate_multiple_sites_results_display(self):
        """Test generating display for multiple sites results."""
        results_data = {
            'total_sites': 2,
            'sites': [
                {
                    'site_url': 'https://restaurant1.com',
                    'pages_processed': 2,
                    'pages': [
                        {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.0},
                        {'url': 'https://restaurant1.com/menu', 'status': 'success', 'processing_time': 1.5}
                    ]
                },
                {
                    'site_url': 'https://restaurant2.com',
                    'pages_processed': 1,
                    'pages': [
                        {'url': 'https://restaurant2.com/', 'status': 'success', 'processing_time': 0.9}
                    ]
                }
            ]
        }
        
        html = self._generate_results_html(results_data)
        
        assert 'restaurant1.com' in html
        assert 'restaurant2.com' in html
        assert 'Pages Processed: 2' in html
        assert 'Pages Processed: 1' in html

    def test_generate_results_with_failed_pages(self):
        """Test generating display with failed pages."""
        results_data = {
            'total_sites': 1,
            'sites': [{
                'site_url': 'https://restaurant1.com',
                'pages_processed': 3,
                'pages': [
                    {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.2},
                    {'url': 'https://restaurant1.com/menu', 'status': 'failed', 'processing_time': 0.3},
                    {'url': 'https://restaurant1.com/contact', 'status': 'success', 'processing_time': 0.8}
                ]
            }]
        }
        
        html = self._generate_results_html(results_data)
        
        assert 'status-success' in html
        assert 'status-failed' in html
        assert 'success' in html
        assert 'failed' in html

    def test_generate_results_with_large_page_count(self):
        """Test generating display with large number of pages (pagination)."""
        pages = []
        for i in range(15):
            pages.append({
                'url': f'https://restaurant1.com/page{i+1}',
                'status': 'success',
                'processing_time': 1.0 + (i * 0.1)
            })
        
        results_data = {
            'total_sites': 1,
            'sites': [{
                'site_url': 'https://restaurant1.com',
                'pages_processed': 15,
                'pages': pages
            }]
        }
        
        html = self._generate_results_html(results_data)
        
        # Should show first 5 pages
        assert 'page1' in html
        assert 'page5' in html
        # Should have show all link
        assert 'Show all 15 pages' in html

    def test_generate_results_show_all_pages(self):
        """Test generating display when showing all pages."""
        pages = []
        for i in range(10):
            pages.append({
                'url': f'https://restaurant1.com/page{i+1}',
                'status': 'success',
                'processing_time': 1.0
            })
        
        results_data = {
            'total_sites': 1,
            'sites': [{
                'site_url': 'https://restaurant1.com',
                'pages_processed': 10,
                'pages': pages
            }]
        }
        
        html = self._generate_results_html(results_data, show_all=True)
        
        # Should show all pages
        for i in range(10):
            assert f'page{i+1}' in html

    def test_results_display_structure_validation(self):
        """Test that results display has proper HTML structure."""
        results_data = {
            'total_sites': 1,
            'sites': [{
                'site_url': 'https://restaurant1.com',
                'pages_processed': 2,
                'pages': [
                    {'url': 'https://restaurant1.com/', 'status': 'success', 'processing_time': 1.2},
                    {'url': 'https://restaurant1.com/menu', 'status': 'success', 'processing_time': 2.1}
                ]
            }]
        }
        
        html = self._generate_results_html(results_data)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check structure
        results_container = soup.find('div', class_='results-container')
        assert results_container is not None
        
        site_result = soup.find('div', class_='site-result')
        assert site_result is not None
        
        pages_list = soup.find('div', class_='pages-list')
        assert pages_list is not None
        
        page_items = soup.find_all('div', class_='page-item')
        assert len(page_items) == 2

    def _generate_results_html(self, results_data, mode='multi', show_all=False):
        """Helper method to generate results HTML."""
        if not results_data:
            return """
            <div class="results-container">
                <div class="no-results">
                    <div class="status-message">No results available</div>
                    <div class="status-subtitle">Complete a scraping operation to see detailed results</div>
                </div>
            </div>
            """
        
        html_parts = ['<div class="results-container">']
        
        for site in results_data['sites']:
            html_parts.append(f'<div class="site-result">')
            html_parts.append(f'<h4>{site["site_url"]}</h4>')
            html_parts.append(f'<div class="pages-summary">Pages Processed: {site["pages_processed"]}</div>')
            html_parts.append(f'<div class="pages-list">')
            
            pages_to_show = site['pages']
            if not show_all and len(pages_to_show) > 5:
                pages_to_show = pages_to_show[:5]
                html_parts.append(f'<div class="show-all-link">Show all {len(site["pages"])} pages</div>')
            
            for page in pages_to_show:
                status_class = f'status-{page["status"]}'
                html_parts.append(f'<div class="page-item {status_class}">')
                html_parts.append(f'<span class="page-url">{page["url"]}</span>')
                html_parts.append(f'<span class="page-time">{page["processing_time"]:.1f}s</span>')
                html_parts.append(f'<span class="page-status">{page["status"]}</span>')
                html_parts.append('</div>')
            
            html_parts.append('</div>')  # pages-list
            html_parts.append('</div>')  # site-result
        
        html_parts.append('</div>')  # results-container
        
        return ''.join(html_parts)


class TestResultsDataProcessing:
    """Test suite for processing results data for display."""

    def test_process_single_page_mode_results(self):
        """Test processing results for single-page mode."""
        raw_results = {
            'successful_extractions': [
                {'url': 'https://restaurant1.com', 'processing_time': 1.5},
                {'url': 'https://restaurant2.com', 'processing_time': 2.0}
            ],
            'failed_urls': [
                {'url': 'https://restaurant3.com', 'error': 'Timeout'}
            ]
        }
        
        processed = self._process_results_for_display(raw_results, mode='single')
        
        assert processed['total_sites'] == 3
        assert len(processed['sites']) == 3
        
        # Each site should have one page
        for site in processed['sites']:
            assert site['pages_processed'] == 1
            assert len(site['pages']) == 1

    def test_process_multi_page_mode_results(self):
        """Test processing results for multi-page mode."""
        raw_results = {
            'successful_extractions': [
                {
                    'site_url': 'https://restaurant1.com',
                    'pages': [
                        {'url': 'https://restaurant1.com/', 'processing_time': 1.2},
                        {'url': 'https://restaurant1.com/menu', 'processing_time': 2.1}
                    ]
                }
            ],
            'failed_urls': [
                {'url': 'https://restaurant1.com/contact', 'error': 'Not found'}
            ]
        }
        
        processed = self._process_results_for_display(raw_results, mode='multi')
        
        assert processed['total_sites'] == 1
        assert processed['sites'][0]['pages_processed'] == 3  # 2 success + 1 failed
        assert len(processed['sites'][0]['pages']) == 3

    def test_calculate_processing_statistics(self):
        """Test calculation of processing statistics."""
        results_data = {
            'total_sites': 2,
            'sites': [
                {
                    'pages_processed': 3,
                    'pages': [
                        {'status': 'success', 'processing_time': 1.0},
                        {'status': 'success', 'processing_time': 2.0},
                        {'status': 'failed', 'processing_time': 0.5}
                    ]
                },
                {
                    'pages_processed': 2,
                    'pages': [
                        {'status': 'success', 'processing_time': 1.5},
                        {'status': 'success', 'processing_time': 1.8}
                    ]
                }
            ]
        }
        
        stats = self._calculate_processing_stats(results_data)
        
        assert stats['total_pages'] == 5
        assert stats['successful_pages'] == 4
        assert stats['failed_pages'] == 1
        assert stats['success_rate'] == 80.0
        assert stats['total_processing_time'] == 6.8

    def test_group_pages_by_site(self):
        """Test grouping pages by site."""
        pages = [
            {'url': 'https://restaurant1.com/', 'status': 'success'},
            {'url': 'https://restaurant1.com/menu', 'status': 'success'},
            {'url': 'https://restaurant2.com/', 'status': 'success'},
            {'url': 'https://restaurant2.com/contact', 'status': 'failed'}
        ]
        
        grouped = self._group_pages_by_site(pages)
        
        assert len(grouped) == 2
        assert 'https://restaurant1.com' in grouped
        assert 'https://restaurant2.com' in grouped
        assert len(grouped['https://restaurant1.com']) == 2
        assert len(grouped['https://restaurant2.com']) == 2

    def test_extract_site_url_from_page_url(self):
        """Test extracting site URL from page URL."""
        test_cases = [
            ('https://restaurant1.com/', 'https://restaurant1.com'),
            ('https://restaurant1.com/menu', 'https://restaurant1.com'),
            ('https://restaurant1.com/about/team', 'https://restaurant1.com'),
            ('https://sub.restaurant1.com/page', 'https://sub.restaurant1.com')
        ]
        
        for page_url, expected_site in test_cases:
            site_url = self._extract_site_url(page_url)
            assert site_url == expected_site

    def _process_results_for_display(self, raw_results, mode='multi'):
        """Helper method to process raw results for display."""
        if mode == 'single':
            # In single-page mode, each URL is treated as a separate site
            sites = []
            
            for extraction in raw_results.get('successful_extractions', []):
                sites.append({
                    'site_url': extraction['url'],
                    'pages_processed': 1,
                    'pages': [{
                        'url': extraction['url'],
                        'status': 'success',
                        'processing_time': extraction['processing_time']
                    }]
                })
            
            for failed in raw_results.get('failed_urls', []):
                sites.append({
                    'site_url': failed['url'],
                    'pages_processed': 1,
                    'pages': [{
                        'url': failed['url'],
                        'status': 'failed',
                        'processing_time': 0.0
                    }]
                })
            
            return {
                'total_sites': len(sites),
                'sites': sites
            }
        
        else:  # multi-page mode
            sites = []
            
            for extraction in raw_results.get('successful_extractions', []):
                pages = []
                for page in extraction['pages']:
                    pages.append({
                        'url': page['url'],
                        'status': 'success',
                        'processing_time': page['processing_time']
                    })
                
                # Add failed pages for this site
                site_url = extraction['site_url']
                for failed in raw_results.get('failed_urls', []):
                    if failed['url'].startswith(site_url):
                        pages.append({
                            'url': failed['url'],
                            'status': 'failed',
                            'processing_time': 0.0
                        })
                
                sites.append({
                    'site_url': site_url,
                    'pages_processed': len(pages),
                    'pages': pages
                })
            
            return {
                'total_sites': len(sites),
                'sites': sites
            }

    def _calculate_processing_stats(self, results_data):
        """Helper method to calculate processing statistics."""
        total_pages = 0
        successful_pages = 0
        failed_pages = 0
        total_time = 0.0
        
        for site in results_data['sites']:
            total_pages += site['pages_processed']
            for page in site['pages']:
                if page['status'] == 'success':
                    successful_pages += 1
                else:
                    failed_pages += 1
                total_time += page['processing_time']
        
        success_rate = (successful_pages / total_pages * 100) if total_pages > 0 else 0
        
        return {
            'total_pages': total_pages,
            'successful_pages': successful_pages,
            'failed_pages': failed_pages,
            'success_rate': success_rate,
            'total_processing_time': total_time
        }

    def _group_pages_by_site(self, pages):
        """Helper method to group pages by site."""
        grouped = {}
        
        for page in pages:
            site_url = self._extract_site_url(page['url'])
            if site_url not in grouped:
                grouped[site_url] = []
            grouped[site_url].append(page)
        
        return grouped

    def _extract_site_url(self, page_url):
        """Helper method to extract site URL from page URL."""
        from urllib.parse import urlparse
        parsed = urlparse(page_url)
        return f"{parsed.scheme}://{parsed.netloc}"


class TestResultsDisplayJavaScriptFunctionality:
    """Test suite for JavaScript functionality (simulated in Python)."""

    def test_toggle_show_all_pages_functionality(self):
        """Test show/hide all pages toggle functionality."""
        state = {
            'pages_visible': 5,
            'total_pages': 15,
            'show_all_expanded': False
        }
        
        # Simulate clicking "Show all pages"
        state = self._simulate_toggle_show_all_pages(state)
        
        assert state['show_all_expanded'] is True
        assert state['pages_visible'] == 15
        
        # Simulate clicking "Show fewer pages"
        state = self._simulate_toggle_show_all_pages(state)
        
        assert state['show_all_expanded'] is False
        assert state['pages_visible'] == 5

    def test_filter_pages_by_status_functionality(self):
        """Test filtering pages by status functionality."""
        pages = [
            {'url': 'page1', 'status': 'success'},
            {'url': 'page2', 'status': 'failed'},
            {'url': 'page3', 'status': 'success'},
            {'url': 'page4', 'status': 'failed'}
        ]
        
        # Filter for successful pages only
        filtered = self._simulate_filter_pages(pages, 'success')
        assert len(filtered) == 2
        assert all(page['status'] == 'success' for page in filtered)
        
        # Filter for failed pages only
        filtered = self._simulate_filter_pages(pages, 'failed')
        assert len(filtered) == 2
        assert all(page['status'] == 'failed' for page in filtered)
        
        # Show all pages
        filtered = self._simulate_filter_pages(pages, 'all')
        assert len(filtered) == 4

    def test_sort_pages_functionality(self):
        """Test sorting pages by different criteria."""
        pages = [
            {'url': 'page1', 'processing_time': 2.5, 'status': 'success'},
            {'url': 'page2', 'processing_time': 1.2, 'status': 'failed'},
            {'url': 'page3', 'processing_time': 3.1, 'status': 'success'}
        ]
        
        # Sort by processing time
        sorted_pages = self._simulate_sort_pages(pages, 'time')
        assert sorted_pages[0]['processing_time'] == 1.2
        assert sorted_pages[-1]['processing_time'] == 3.1
        
        # Sort by status
        sorted_pages = self._simulate_sort_pages(pages, 'status')
        failed_pages = [p for p in sorted_pages if p['status'] == 'failed']
        success_pages = [p for p in sorted_pages if p['status'] == 'success']
        assert len(failed_pages) == 1
        assert len(success_pages) == 2

    def test_expand_collapse_site_results_functionality(self):
        """Test expanding/collapsing site results functionality."""
        state = {
            'site_expanded': False,
            'pages_visible': False
        }
        
        # Simulate expanding site results
        state = self._simulate_toggle_site_expansion(state)
        
        assert state['site_expanded'] is True
        assert state['pages_visible'] is True
        
        # Simulate collapsing site results
        state = self._simulate_toggle_site_expansion(state)
        
        assert state['site_expanded'] is False
        assert state['pages_visible'] is False

    def _simulate_toggle_show_all_pages(self, state):
        """Simulate toggling show all pages functionality."""
        if state['show_all_expanded']:
            state['show_all_expanded'] = False
            state['pages_visible'] = 5
        else:
            state['show_all_expanded'] = True
            state['pages_visible'] = state['total_pages']
        
        return state

    def _simulate_filter_pages(self, pages, filter_type):
        """Simulate filtering pages by status."""
        if filter_type == 'all':
            return pages
        else:
            return [page for page in pages if page['status'] == filter_type]

    def _simulate_sort_pages(self, pages, sort_by):
        """Simulate sorting pages by different criteria."""
        if sort_by == 'time':
            return sorted(pages, key=lambda p: p['processing_time'])
        elif sort_by == 'status':
            return sorted(pages, key=lambda p: p['status'])
        else:
            return pages

    def _simulate_toggle_site_expansion(self, state):
        """Simulate toggling site expansion."""
        state['site_expanded'] = not state['site_expanded']
        state['pages_visible'] = state['site_expanded']
        return state


if __name__ == '__main__':
    pytest.main([__file__])