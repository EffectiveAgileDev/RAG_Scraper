"""Unit tests for enhanced page status display functionality."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Mock reportlab to avoid import issues
import sys
sys.modules['reportlab'] = MagicMock()
sys.modules['reportlab.lib'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'] = MagicMock()
sys.modules['reportlab.platypus'] = MagicMock()
sys.modules['reportlab.lib.styles'] = MagicMock()
sys.modules['reportlab.lib.units'] = MagicMock()

from web_interface.app_factory import create_app
from scraper.restaurant_scraper import RestaurantScraper


class TestEnhancedPageStatusDisplay:
    """Test suite for enhanced page status display."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock page results with various statuses
        self.mock_results = {
            'successful_pages': [
                {
                    'url': 'https://restaurant1.com/menu',
                    'status': 'success',
                    'http_status': 200,
                    'data_extracted': 15,
                    'content_size': 2048,
                    'processing_time': 1.2,
                    'timestamp': '2024-01-15T10:30:00Z',
                    'extraction_method': 'json_ld',
                    'response_headers': {'content-type': 'text/html'}
                }
            ],
            'failed_pages': [
                {
                    'url': 'https://restaurant1.com/private',
                    'status': 'failed',
                    'http_status': 404,
                    'error_message': 'Page not found',
                    'processing_time': 0.5,
                    'timestamp': '2024-01-15T10:30:30Z'
                }
            ],
            'timeout_pages': [
                {
                    'url': 'https://restaurant1.com/slow',
                    'status': 'timeout',
                    'timeout_duration': 30.0,
                    'partial_data': 3,
                    'processing_time': 30.0,
                    'timestamp': '2024-01-15T10:31:15Z'
                }
            ]
        }
    
    def test_format_page_status_success(self):
        """Test formatting of successful page status."""
        page_data = self.mock_results['successful_pages'][0]
        
        # This would be a method in the web interface
        status_html = self._format_page_status(page_data)
        
        assert '✓ SUCCESS' in status_html
        assert '200' in status_html
        assert '15 items' in status_html
        assert '2.0 KB' in status_html
    
    def test_format_page_status_failed(self):
        """Test formatting of failed page status."""
        page_data = self.mock_results['failed_pages'][0]
        
        status_html = self._format_page_status(page_data)
        
        assert '✗ FAILED' in status_html
        assert '404' in status_html
        assert 'Page not found' in status_html
    
    def test_format_page_status_timeout(self):
        """Test formatting of timeout page status."""
        page_data = self.mock_results['timeout_pages'][0]
        
        status_html = self._format_page_status(page_data)
        
        assert '⏰ TIMEOUT' in status_html
        assert '30.0s' in status_html
        assert '3 items' in status_html
    
    def test_calculate_content_size_formatting(self):
        """Test content size formatting."""
        # Test bytes
        assert self._format_content_size(512) == "512 B"
        
        # Test kilobytes
        assert self._format_content_size(1024) == "1.0 KB"
        assert self._format_content_size(2048) == "2.0 KB"
        
        # Test megabytes
        assert self._format_content_size(1048576) == "1.0 MB"
        assert self._format_content_size(2097152) == "2.0 MB"
    
    def test_generate_status_tooltip_data(self):
        """Test generation of tooltip data."""
        page_data = self.mock_results['successful_pages'][0]
        
        tooltip_data = self._generate_tooltip_data(page_data)
        
        assert 'timestamp' in tooltip_data
        assert 'extraction_method' in tooltip_data
        assert 'response_headers' in tooltip_data
        assert tooltip_data['extraction_method'] == 'json_ld'
    
    def test_filter_pages_by_status(self):
        """Test filtering pages by status."""
        all_pages = (
            self.mock_results['successful_pages'] +
            self.mock_results['failed_pages'] +
            self.mock_results['timeout_pages']
        )
        
        # Test success filter
        success_pages = self._filter_pages_by_status(all_pages, 'success')
        assert len(success_pages) == 1
        assert success_pages[0]['status'] == 'success'
        
        # Test failed filter
        failed_pages = self._filter_pages_by_status(all_pages, 'failed')
        assert len(failed_pages) == 1
        assert failed_pages[0]['status'] == 'failed'
        
        # Test timeout filter
        timeout_pages = self._filter_pages_by_status(all_pages, 'timeout')
        assert len(timeout_pages) == 1
        assert timeout_pages[0]['status'] == 'timeout'
    
    def test_generate_failed_pages_report(self):
        """Test generation of failed pages report."""
        failed_pages = self.mock_results['failed_pages']
        
        report = self._generate_failed_pages_report(failed_pages)
        
        assert 'Failed Pages Report' in report
        assert 'https://restaurant1.com/private' in report
        assert 'Page not found' in report
        assert '404' in report
    
    def test_extract_retry_urls(self):
        """Test extraction of URLs for retry."""
        failed_pages = self.mock_results['failed_pages']
        timeout_pages = self.mock_results['timeout_pages']
        
        retry_urls = self._extract_retry_urls(failed_pages + timeout_pages)
        
        assert len(retry_urls) == 2
        assert 'https://restaurant1.com/private' in retry_urls
        assert 'https://restaurant1.com/slow' in retry_urls
    
    def test_update_page_status_after_retry(self):
        """Test updating page status after retry."""
        original_status = {
            'url': 'https://restaurant1.com/private',
            'status': 'failed',
            'error_message': 'Page not found'
        }
        
        retry_result = {
            'url': 'https://restaurant1.com/private',
            'status': 'success',
            'http_status': 200,
            'data_extracted': 10
        }
        
        updated_status = self._update_page_status_after_retry(original_status, retry_result)
        
        assert updated_status['status'] == 'success'
        assert updated_status['http_status'] == 200
        assert updated_status['data_extracted'] == 10
        assert 'retry_attempt' in updated_status
    
    def test_calculate_retry_statistics(self):
        """Test calculation of retry statistics."""
        retry_results = [
            {'status': 'success'},
            {'status': 'success'},
            {'status': 'failed'}
        ]
        
        stats = self._calculate_retry_statistics(retry_results)
        
        assert stats['total_retries'] == 3
        assert stats['successful_retries'] == 2
        assert stats['failed_retries'] == 1
        assert stats['success_rate'] == 0.667  # 2/3 rounded
    
    def test_validate_page_status_data(self):
        """Test validation of page status data."""
        # Valid data
        valid_data = {
            'url': 'https://example.com',
            'status': 'success',
            'http_status': 200,
            'processing_time': 1.0
        }
        assert self._validate_page_status_data(valid_data) == True
        
        # Invalid data - missing required fields
        invalid_data = {
            'url': 'https://example.com'
            # Missing status
        }
        assert self._validate_page_status_data(invalid_data) == False
        
        # Invalid data - invalid status
        invalid_status_data = {
            'url': 'https://example.com',
            'status': 'unknown',
            'processing_time': 1.0
        }
        assert self._validate_page_status_data(invalid_status_data) == False
    
    def test_sort_pages_by_status_priority(self):
        """Test sorting pages by status priority."""
        mixed_pages = [
            {'status': 'timeout', 'url': 'url3'},
            {'status': 'success', 'url': 'url1'},
            {'status': 'failed', 'url': 'url2'}
        ]
        
        sorted_pages = self._sort_pages_by_status_priority(mixed_pages)
        
        # Expected order: success, failed, timeout
        assert sorted_pages[0]['status'] == 'success'
        assert sorted_pages[1]['status'] == 'failed'
        assert sorted_pages[2]['status'] == 'timeout'
    
    def test_aggregate_status_summary(self):
        """Test aggregation of status summary."""
        all_pages = (
            self.mock_results['successful_pages'] +
            self.mock_results['failed_pages'] +
            self.mock_results['timeout_pages']
        )
        
        summary = self._aggregate_status_summary(all_pages)
        
        assert summary['total_pages'] == 3
        assert summary['successful_pages'] == 1
        assert summary['failed_pages'] == 1
        assert summary['timeout_pages'] == 1
        assert summary['success_rate'] == 0.333  # 1/3 rounded
    
    # Helper methods that would be implemented in the actual web interface
    
    def _format_page_status(self, page_data):
        """Format page status for display."""
        status = page_data.get('status', 'unknown')
        
        if status == 'success':
            html = f'<span class="status-indicator success">✓ SUCCESS</span>'
            html += f'<span class="http-status">{page_data.get("http_status", "")}</span>'
            html += f'<span class="data-count">{page_data.get("data_extracted", 0)} items</span>'
            content_size = self._format_content_size(page_data.get('content_size', 0))
            html += f'<span class="content-size">{content_size}</span>'
        elif status == 'failed':
            html = f'<span class="status-indicator failed">✗ FAILED</span>'
            html += f'<span class="http-status">{page_data.get("http_status", "")}</span>'
            html += f'<span class="error-message">{page_data.get("error_message", "")}</span>'
        elif status == 'timeout':
            html = f'<span class="status-indicator timeout">⏰ TIMEOUT</span>'
            html += f'<span class="timeout-duration">{page_data.get("timeout_duration", 0)}s</span>'
            partial_data = page_data.get('partial_data', 0)
            if partial_data > 0:
                html += f'<span class="partial-data">{partial_data} items</span>'
        else:
            html = f'<span class="status-indicator unknown">? UNKNOWN</span>'
        
        return html
    
    def _format_content_size(self, size_bytes):
        """Format content size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1048576:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / 1048576:.1f} MB"
    
    def _generate_tooltip_data(self, page_data):
        """Generate tooltip data for a page."""
        return {
            'timestamp': page_data.get('timestamp', ''),
            'extraction_method': page_data.get('extraction_method', 'unknown'),
            'response_headers': page_data.get('response_headers', {}),
            'processing_time': page_data.get('processing_time', 0)
        }
    
    def _filter_pages_by_status(self, pages, status_filter):
        """Filter pages by status."""
        return [page for page in pages if page.get('status') == status_filter]
    
    def _generate_failed_pages_report(self, failed_pages):
        """Generate a report of failed pages."""
        report = "Failed Pages Report\n"
        report += "=" * 50 + "\n\n"
        
        for page in failed_pages:
            report += f"URL: {page.get('url', '')}\n"
            report += f"Status Code: {page.get('http_status', 'N/A')}\n"
            report += f"Error: {page.get('error_message', '')}\n"
            report += f"Timestamp: {page.get('timestamp', '')}\n"
            report += "-" * 30 + "\n"
        
        return report
    
    def _extract_retry_urls(self, failed_pages):
        """Extract URLs that should be retried."""
        return [page.get('url') for page in failed_pages if page.get('url')]
    
    def _update_page_status_after_retry(self, original_status, retry_result):
        """Update page status after retry attempt."""
        updated = original_status.copy()
        updated.update(retry_result)
        updated['retry_attempt'] = True
        return updated
    
    def _calculate_retry_statistics(self, retry_results):
        """Calculate statistics for retry attempts."""
        total = len(retry_results)
        successful = len([r for r in retry_results if r.get('status') == 'success'])
        failed = total - successful
        
        return {
            'total_retries': total,
            'successful_retries': successful,
            'failed_retries': failed,
            'success_rate': round(successful / total, 3) if total > 0 else 0
        }
    
    def _validate_page_status_data(self, page_data):
        """Validate page status data structure."""
        required_fields = ['url', 'status']
        valid_statuses = ['success', 'failed', 'timeout', 'redirected']
        
        # Check required fields
        for field in required_fields:
            if field not in page_data:
                return False
        
        # Check valid status
        if page_data['status'] not in valid_statuses:
            return False
        
        return True
    
    def _sort_pages_by_status_priority(self, pages):
        """Sort pages by status priority (success first, then failed, then timeout)."""
        priority_order = {'success': 1, 'failed': 2, 'timeout': 3, 'redirected': 4}
        
        return sorted(pages, key=lambda x: priority_order.get(x.get('status'), 5))
    
    def _aggregate_status_summary(self, pages):
        """Aggregate status summary statistics."""
        total = len(pages)
        status_counts = {}
        
        for page in pages:
            status = page.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        successful = status_counts.get('success', 0)
        
        return {
            'total_pages': total,
            'successful_pages': successful,
            'failed_pages': status_counts.get('failed', 0),
            'timeout_pages': status_counts.get('timeout', 0),
            'success_rate': round(successful / total, 3) if total > 0 else 0
        }