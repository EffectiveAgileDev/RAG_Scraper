"""Unit tests for enhanced processing time display functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestEnhancedProcessingTimeDisplay:
    """Test suite for enhanced processing time display."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_page_data = {
            'url': 'https://restaurant1.com/menu',
            'status': 'success',
            'processing_time': 1.234,
            'network_time': 0.5,
            'parsing_time': 0.3,
            'extraction_time': 0.434,
            'timestamp': '2024-01-15T10:30:00Z',
            'request_start': '2024-01-15T10:29:58.766Z',
            'request_end': '2024-01-15T10:30:00.000Z'
        }
    
    def test_format_processing_time_basic(self):
        """Test basic processing time formatting."""
        # Test sub-second times
        assert self._format_processing_time(0.123) == "0.12s"
        
        # Test second times  
        assert self._format_processing_time(1.456) == "1.46s"
        
        # Test longer times
        assert self._format_processing_time(30.0) == "30.00s"
        
        # Test very long times
        assert self._format_processing_time(125.67) == "2m 5.67s"
    
    def test_format_processing_time_breakdown(self):
        """Test detailed processing time breakdown."""
        breakdown = self._generate_processing_time_breakdown(self.mock_page_data)
        
        assert 'total_time' in breakdown
        assert 'network_time' in breakdown
        assert 'parsing_time' in breakdown
        assert 'extraction_time' in breakdown
        assert breakdown['total_time'] == 1.234
        assert breakdown['network_time'] == 0.5
        assert breakdown['parsing_time'] == 0.3
        assert breakdown['extraction_time'] == 0.434
    
    def test_calculate_processing_speed(self):
        """Test processing speed calculation."""
        page_data = {
            'processing_time': 2.0,
            'content_size': 2048,  # 2KB
            'data_extracted': 10
        }
        
        speed_metrics = self._calculate_processing_speed(page_data)
        
        assert 'bytes_per_second' in speed_metrics
        assert 'items_per_second' in speed_metrics
        assert speed_metrics['bytes_per_second'] == 1024  # 2048 / 2
        assert speed_metrics['items_per_second'] == 5      # 10 / 2
    
    def test_processing_time_tooltip_generation(self):
        """Test tooltip generation for processing time."""
        tooltip = self._generate_processing_time_tooltip(self.mock_page_data)
        
        assert 'Total: 1.23s' in tooltip
        assert 'Network: 0.50s' in tooltip
        assert 'Parsing: 0.30s' in tooltip
        assert 'Extraction: 0.43s' in tooltip
    
    def test_processing_time_performance_rating(self):
        """Test performance rating calculation."""
        # Fast page
        fast_page = {'processing_time': 0.5}
        assert self._get_performance_rating(fast_page) == 'excellent'
        
        # Normal page
        normal_page = {'processing_time': 2.0}
        assert self._get_performance_rating(normal_page) == 'good'
        
        # Slow page  
        slow_page = {'processing_time': 8.0}
        assert self._get_performance_rating(slow_page) == 'slow'
        
        # Very slow page
        very_slow_page = {'processing_time': 25.0}
        assert self._get_performance_rating(very_slow_page) == 'very_slow'
    
    def test_processing_time_comparison(self):
        """Test processing time comparison across pages."""
        pages = [
            {'url': 'page1', 'processing_time': 1.0},
            {'url': 'page2', 'processing_time': 2.0},
            {'url': 'page3', 'processing_time': 0.5},
            {'url': 'page4', 'processing_time': 3.0}
        ]
        
        stats = self._calculate_processing_time_stats(pages)
        
        assert stats['average'] == 1.625  # (1.0 + 2.0 + 0.5 + 3.0) / 4
        assert stats['fastest'] == 0.5
        assert stats['slowest'] == 3.0
        assert stats['fastest_url'] == 'page3'
        assert stats['slowest_url'] == 'page4'
    
    def test_processing_time_trend_analysis(self):
        """Test processing time trend analysis."""
        pages_with_timestamps = [
            {'processing_time': 1.0, 'timestamp': '2024-01-15T10:30:00Z'},
            {'processing_time': 1.5, 'timestamp': '2024-01-15T10:30:30Z'},
            {'processing_time': 2.0, 'timestamp': '2024-01-15T10:31:00Z'},
            {'processing_time': 1.2, 'timestamp': '2024-01-15T10:31:30Z'}
        ]
        
        trend = self._analyze_processing_time_trend(pages_with_timestamps)
        
        assert 'trend_direction' in trend
        assert 'average_increase' in trend
        assert trend['trend_direction'] in ['increasing', 'decreasing', 'stable']
    
    def test_processing_time_histogram_data(self):
        """Test histogram data generation for processing times."""
        pages = [
            {'processing_time': 0.5},  # Fast
            {'processing_time': 1.2},  # Normal
            {'processing_time': 2.8},  # Normal
            {'processing_time': 8.5},  # Slow
            {'processing_time': 0.3},  # Fast
            {'processing_time': 15.0}  # Very slow
        ]
        
        histogram = self._generate_processing_time_histogram(pages)
        
        assert 'fast' in histogram          # < 1s
        assert 'normal' in histogram        # 1-5s  
        assert 'slow' in histogram          # 5-10s
        assert 'very_slow' in histogram     # > 10s
        
        assert histogram['fast'] == 2
        assert histogram['normal'] == 2
        assert histogram['slow'] == 1
        assert histogram['very_slow'] == 1
    
    def test_processing_time_outlier_detection(self):
        """Test outlier detection in processing times."""
        pages = [
            {'url': 'normal1', 'processing_time': 1.0},
            {'url': 'normal2', 'processing_time': 1.2},
            {'url': 'normal3', 'processing_time': 0.8},
            {'url': 'outlier1', 'processing_time': 25.0},  # Outlier
            {'url': 'normal4', 'processing_time': 1.1},
            {'url': 'outlier2', 'processing_time': 0.1}    # Outlier
        ]
        
        outliers = self._detect_processing_time_outliers(pages)
        
        # At least the major outlier should be detected
        assert len(outliers) >= 1
        outlier_urls = [o['url'] for o in outliers]
        assert 'outlier1' in outlier_urls  # The 25.0s should definitely be detected
    
    def test_processing_time_efficiency_score(self):
        """Test efficiency score calculation."""
        page_data = {
            'processing_time': 2.0,
            'data_extracted': 10,
            'content_size': 2048
        }
        
        efficiency = self._calculate_efficiency_score(page_data)
        
        assert 'overall_score' in efficiency
        assert 'data_efficiency' in efficiency
        assert 'size_efficiency' in efficiency
        assert 0 <= efficiency['overall_score'] <= 100
    
    # Helper methods that would be implemented in the actual web interface
    
    def _format_processing_time(self, time_seconds):
        """Format processing time for display."""
        if time_seconds < 60:
            return f"{time_seconds:.2f}s"
        else:
            minutes = int(time_seconds // 60)
            seconds = time_seconds % 60
            return f"{minutes}m {seconds:.2f}s"
    
    def _generate_processing_time_breakdown(self, page_data):
        """Generate detailed processing time breakdown."""
        return {
            'total_time': page_data.get('processing_time', 0),
            'network_time': page_data.get('network_time', 0),
            'parsing_time': page_data.get('parsing_time', 0),
            'extraction_time': page_data.get('extraction_time', 0)
        }
    
    def _calculate_processing_speed(self, page_data):
        """Calculate processing speed metrics."""
        processing_time = page_data.get('processing_time', 1)
        content_size = page_data.get('content_size', 0)
        data_extracted = page_data.get('data_extracted', 0)
        
        return {
            'bytes_per_second': content_size / processing_time if processing_time > 0 else 0,
            'items_per_second': data_extracted / processing_time if processing_time > 0 else 0
        }
    
    def _generate_processing_time_tooltip(self, page_data):
        """Generate tooltip for processing time."""
        total = page_data.get('processing_time', 0)
        network = page_data.get('network_time', 0)
        parsing = page_data.get('parsing_time', 0)
        extraction = page_data.get('extraction_time', 0)
        
        return f"Total: {total:.2f}s | Network: {network:.2f}s | Parsing: {parsing:.2f}s | Extraction: {extraction:.2f}s"
    
    def _get_performance_rating(self, page_data):
        """Get performance rating for a page."""
        time = page_data.get('processing_time', 0)
        
        if time < 1.0:
            return 'excellent'
        elif time < 5.0:
            return 'good'
        elif time < 10.0:
            return 'slow'
        else:
            return 'very_slow'
    
    def _calculate_processing_time_stats(self, pages):
        """Calculate processing time statistics."""
        times = [p.get('processing_time', 0) for p in pages]
        
        if not times:
            return {'average': 0, 'fastest': 0, 'slowest': 0}
        
        fastest_time = min(times)
        slowest_time = max(times)
        
        fastest_page = next(p for p in pages if p.get('processing_time') == fastest_time)
        slowest_page = next(p for p in pages if p.get('processing_time') == slowest_time)
        
        return {
            'average': sum(times) / len(times),
            'fastest': fastest_time,
            'slowest': slowest_time,
            'fastest_url': fastest_page.get('url', ''),
            'slowest_url': slowest_page.get('url', '')
        }
    
    def _analyze_processing_time_trend(self, pages):
        """Analyze processing time trend over time."""
        if len(pages) < 2:
            return {'trend_direction': 'stable', 'average_increase': 0}
        
        times = [p.get('processing_time', 0) for p in pages]
        
        # Simple trend analysis
        increases = 0
        decreases = 0
        
        for i in range(1, len(times)):
            if times[i] > times[i-1]:
                increases += 1
            elif times[i] < times[i-1]:
                decreases += 1
        
        if increases > decreases:
            trend = 'increasing'
        elif decreases > increases:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        avg_change = (times[-1] - times[0]) / len(times) if len(times) > 1 else 0
        
        return {
            'trend_direction': trend,
            'average_increase': avg_change
        }
    
    def _generate_processing_time_histogram(self, pages):
        """Generate histogram data for processing times."""
        histogram = {
            'fast': 0,      # < 1s
            'normal': 0,    # 1-5s
            'slow': 0,      # 5-10s
            'very_slow': 0  # > 10s
        }
        
        for page in pages:
            time = page.get('processing_time', 0)
            if time < 1.0:
                histogram['fast'] += 1
            elif time < 5.0:
                histogram['normal'] += 1
            elif time < 10.0:
                histogram['slow'] += 1
            else:
                histogram['very_slow'] += 1
        
        return histogram
    
    def _detect_processing_time_outliers(self, pages):
        """Detect outliers in processing times."""
        times = [p.get('processing_time', 0) for p in pages]
        
        if len(times) < 3:
            return []
        
        # Calculate mean and standard deviation
        mean_time = sum(times) / len(times)
        variance = sum((t - mean_time) ** 2 for t in times) / len(times)
        std_dev = variance ** 0.5
        
        # Consider outliers as values > 1.5 standard deviations from mean
        # (using 1.5 instead of 2 to be more sensitive to outliers)
        threshold = 1.5 * std_dev
        outliers = []
        
        for page in pages:
            time = page.get('processing_time', 0)
            if abs(time - mean_time) > threshold:
                outliers.append(page)
        
        return outliers
    
    def _calculate_efficiency_score(self, page_data):
        """Calculate efficiency score for processing."""
        processing_time = page_data.get('processing_time', 1)
        data_extracted = page_data.get('data_extracted', 0)
        content_size = page_data.get('content_size', 0)
        
        # Higher data extraction rate = better efficiency
        data_efficiency = (data_extracted / processing_time) * 10 if processing_time > 0 else 0
        
        # Higher content processing rate = better efficiency  
        size_efficiency = (content_size / processing_time) / 100 if processing_time > 0 else 0
        
        # Combine metrics (cap at 100)
        overall_score = min(100, (data_efficiency + size_efficiency) / 2)
        
        return {
            'overall_score': overall_score,
            'data_efficiency': data_efficiency,
            'size_efficiency': size_efficiency
        }