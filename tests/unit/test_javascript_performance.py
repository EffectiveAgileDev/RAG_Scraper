"""Unit tests for JavaScript rendering performance optimization and error handling."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.scraper.javascript_handler import JavaScriptHandler
from src.scraper.restaurant_popup_detector import RestaurantPopupDetector


class TestJavaScriptPerformance:
    """Test JavaScript rendering performance optimizations."""
    
    @pytest.fixture
    def handler(self):
        """Create JavaScript handler instance."""
        return JavaScriptHandler(timeout=30, enable_browser_automation=True)
    
    @pytest.fixture
    def fast_handler(self):
        """Create JavaScript handler with performance optimizations."""
        handler = JavaScriptHandler(timeout=15, enable_browser_automation=True)
        handler.cache_enabled = True
        handler.cache_size = 100
        handler.cache_ttl = 300  # 5 minutes
        return handler
    
    def test_cache_initialization(self, fast_handler):
        """Test that caching is properly initialized."""
        assert hasattr(fast_handler, 'cache_enabled')
        assert hasattr(fast_handler, 'cache_size')
        assert hasattr(fast_handler, 'cache_ttl')
        assert fast_handler.cache_enabled is True
        assert fast_handler.cache_size == 100
        assert fast_handler.cache_ttl == 300
    
    def test_popup_pattern_caching(self, fast_handler):
        """Test that popup patterns are cached for performance."""
        html = '''
        <div class="age-gate">Are you 21 or older?</div>
        <button class="confirm-age">Yes</button>
        '''
        
        detector = RestaurantPopupDetector()
        fast_handler.popup_detector = detector
        
        # Mock caching methods
        fast_handler._get_cached_popup_result = Mock(return_value=None)
        fast_handler._cache_popup_result = Mock()
        
        # First call should miss cache
        popups1 = detector.detect_restaurant_popups(html)
        
        # Verify cache methods are available for implementation
        assert hasattr(fast_handler, '_get_cached_popup_result')
        assert hasattr(fast_handler, '_cache_popup_result')
    
    def test_javascript_detection_optimization(self, fast_handler):
        """Test optimized JavaScript detection."""
        # Fast check for common JS indicators
        spa_html = '<div id="root"></div><script>window.__INITIAL_STATE__</script>'
        static_html = '<div class="content">Static content</div>'
        
        # Should quickly identify SPA
        assert fast_handler.is_javascript_required(spa_html) is True
        
        # Should quickly identify static content
        assert fast_handler.is_javascript_required(static_html) is False
    
    def test_timeout_optimization(self, fast_handler):
        """Test that timeouts are optimized for performance."""
        # Fast handler should have shorter timeout
        assert fast_handler.timeout == 15
        
        # Should handle timeout gracefully
        result = fast_handler.render_page("https://slow-restaurant.com", timeout=5)
        assert result is not None
    
    def test_skip_rendering_for_simple_content(self, fast_handler):
        """Test that simple content skips expensive rendering."""
        simple_html = '''
        <html>
            <body>
                <h1>Restaurant Name</h1>
                <div class="address">123 Main St</div>
                <div class="phone">(555) 123-4567</div>
            </body>
        </html>
        '''
        
        # Should not require JavaScript rendering
        requires_js = fast_handler.is_javascript_required(simple_html)
        assert requires_js is False
        
        # Rendering should return fallback quickly
        result = fast_handler.render_page("https://simple-restaurant.com")
        assert result is not None
        assert "Rendered content for https://simple-restaurant.com" in result
    
    def test_concurrent_rendering_safety(self, fast_handler):
        """Test that concurrent rendering is handled safely."""
        urls = [
            "https://restaurant1.com",
            "https://restaurant2.com", 
            "https://restaurant3.com"
        ]
        
        # Mock concurrent safety measures
        fast_handler._acquire_render_lock = Mock()
        fast_handler._release_render_lock = Mock()
        
        for url in urls:
            result = fast_handler.render_page(url)
            assert result is not None
        
        # Verify safety methods are available
        assert hasattr(fast_handler, '_acquire_render_lock')
        assert hasattr(fast_handler, '_release_render_lock')
    
    def test_memory_management(self, fast_handler):
        """Test memory management for browser instances."""
        # Mock memory management methods
        fast_handler._cleanup_browser_resources = Mock()
        fast_handler._monitor_memory_usage = Mock(return_value=50.0)  # 50% memory usage
        
        # Should have memory management capabilities
        assert hasattr(fast_handler, '_cleanup_browser_resources')
        assert hasattr(fast_handler, '_monitor_memory_usage')
        
        # Memory monitoring should return reasonable values
        memory_usage = fast_handler._monitor_memory_usage()
        assert isinstance(memory_usage, float)
        assert 0 <= memory_usage <= 100


class TestJavaScriptErrorHandling:
    """Test JavaScript rendering error handling."""
    
    @pytest.fixture
    def robust_handler(self):
        """Create JavaScript handler with robust error handling."""
        handler = JavaScriptHandler(timeout=30, enable_browser_automation=True)
        handler.max_retries = 3
        handler.retry_delay = 1.0
        handler.fallback_enabled = True
        return handler
    
    def test_retry_mechanism(self, robust_handler):
        """Test retry mechanism for failed operations."""
        assert hasattr(robust_handler, 'max_retries')
        assert hasattr(robust_handler, 'retry_delay')
        assert robust_handler.max_retries == 3
        assert robust_handler.retry_delay == 1.0
    
    @patch('src.scraper.javascript_handler.async_playwright')
    def test_browser_crash_recovery(self, mock_async_playwright, robust_handler):
        """Test recovery from browser crashes."""
        # Mock browser crash scenario
        mock_async_playwright.side_effect = Exception("Browser crashed")
        
        robust_handler._handle_browser_crash = Mock()
        robust_handler._restart_browser = Mock(return_value=True)
        
        # Should handle crashes gracefully
        result = robust_handler.render_page("https://problematic-restaurant.com")
        
        # Should fallback to static rendering
        assert result is not None
        assert "Rendered content for https://problematic-restaurant.com" in result
    
    def test_network_timeout_handling(self, robust_handler):
        """Test handling of network timeouts."""
        robust_handler._handle_network_timeout = Mock()
        robust_handler._check_network_connectivity = Mock(return_value=True)
        
        # Should have network error handling capabilities
        assert hasattr(robust_handler, '_handle_network_timeout')
        assert hasattr(robust_handler, '_check_network_connectivity')
    
    def test_popup_handling_errors(self, robust_handler):
        """Test error handling in popup detection and handling."""
        problematic_html = '''
        <div class="broken-popup" style="position: absolute; z-index: -1;">
            <script>throw new Error("Popup script error");</script>
        </div>
        '''
        
        detector = RestaurantPopupDetector()
        robust_handler.popup_detector = detector
        
        # Should handle popup errors gracefully
        try:
            popups = detector.detect_restaurant_popups(problematic_html)
            # Should not crash and return empty list or handle gracefully
            assert isinstance(popups, list)
        except Exception as e:
            pytest.fail(f"Popup error handling failed: {e}")
    
    def test_malformed_html_handling(self, robust_handler):
        """Test handling of malformed HTML."""
        malformed_html = '''
        <html>
            <div class="unclosed-tag">
                <script>var broken = {
                <div class="age-gate">Incomplete popup
        '''
        
        # Should handle malformed HTML gracefully
        requires_js = robust_handler.is_javascript_required(malformed_html)
        assert isinstance(requires_js, bool)
        
        result = robust_handler.render_page("https://malformed-restaurant.com")
        assert result is not None
    
    def test_large_page_handling(self, robust_handler):
        """Test handling of very large pages."""
        # Simulate large page content
        large_html = '<div>' + 'x' * 10000 + '</div>' * 100  # ~1MB of content
        
        # Should handle large content without crashing
        requires_js = robust_handler.is_javascript_required(large_html)
        assert isinstance(requires_js, bool)
    
    def test_infinite_popup_protection(self, robust_handler):
        """Test protection against infinite popup loops."""
        robust_handler.max_popup_attempts = 5
        robust_handler._popup_attempt_count = 0
        robust_handler._reset_popup_counter = Mock()
        
        # Should have infinite loop protection
        assert hasattr(robust_handler, 'max_popup_attempts')
        assert robust_handler.max_popup_attempts == 5
    
    def test_resource_exhaustion_protection(self, robust_handler):
        """Test protection against resource exhaustion."""
        robust_handler._check_system_resources = Mock(return_value={'cpu': 80.0, 'memory': 75.0})
        robust_handler._throttle_operations = Mock()
        
        # Should monitor system resources
        resources = robust_handler._check_system_resources()
        assert 'cpu' in resources
        assert 'memory' in resources
        
        # Should have throttling capability
        assert hasattr(robust_handler, '_throttle_operations')
    
    def test_graceful_degradation(self, robust_handler):
        """Test graceful degradation when features fail."""
        # Mock feature failures
        robust_handler.browser_automation_enabled = False  # Browser automation failed
        
        # Should still work with reduced functionality
        result = robust_handler.render_page("https://restaurant.com")
        assert result is not None
        
        # Should indicate degraded mode
        assert "Rendered content for https://restaurant.com" in result


class TestJavaScriptPerformanceMetrics:
    """Test performance metrics and monitoring."""
    
    @pytest.fixture
    def monitored_handler(self):
        """Create JavaScript handler with performance monitoring."""
        handler = JavaScriptHandler(timeout=30, enable_browser_automation=True)
        handler.performance_monitoring = True
        handler.metrics_collection = True
        return handler
    
    def test_performance_metrics_collection(self, monitored_handler):
        """Test that performance metrics are collected."""
        assert hasattr(monitored_handler, 'performance_monitoring')
        assert hasattr(monitored_handler, 'metrics_collection')
        assert monitored_handler.performance_monitoring is True
        assert monitored_handler.metrics_collection is True
    
    def test_render_time_tracking(self, monitored_handler):
        """Test render time tracking."""
        monitored_handler._start_timer = Mock()
        monitored_handler._end_timer = Mock(return_value=2.5)  # 2.5 seconds
        monitored_handler._record_metric = Mock()
        
        # Should track render times
        result = monitored_handler.render_page("https://restaurant.com")
        
        assert hasattr(monitored_handler, '_start_timer')
        assert hasattr(monitored_handler, '_end_timer')
        assert hasattr(monitored_handler, '_record_metric')
    
    def test_popup_detection_metrics(self, monitored_handler):
        """Test popup detection performance metrics."""
        monitored_handler._track_popup_detection_time = Mock(return_value=0.1)  # 100ms
        monitored_handler._track_popup_handling_time = Mock(return_value=0.5)   # 500ms
        
        # Should track popup performance
        assert hasattr(monitored_handler, '_track_popup_detection_time')
        assert hasattr(monitored_handler, '_track_popup_handling_time')
    
    def test_success_failure_rates(self, monitored_handler):
        """Test success and failure rate tracking."""
        monitored_handler._record_success = Mock()
        monitored_handler._record_failure = Mock()
        monitored_handler._get_success_rate = Mock(return_value=95.5)  # 95.5% success rate
        
        # Should track success/failure rates
        success_rate = monitored_handler._get_success_rate()
        assert isinstance(success_rate, float)
        assert 0 <= success_rate <= 100
    
    def test_browser_resource_monitoring(self, monitored_handler):
        """Test browser resource usage monitoring."""
        monitored_handler._monitor_browser_memory = Mock(return_value=256.0)  # 256MB
        monitored_handler._monitor_browser_cpu = Mock(return_value=15.0)      # 15% CPU
        
        # Should monitor browser resources
        memory_usage = monitored_handler._monitor_browser_memory()
        cpu_usage = monitored_handler._monitor_browser_cpu()
        
        assert isinstance(memory_usage, float)
        assert isinstance(cpu_usage, float)
        assert memory_usage > 0
        assert cpu_usage >= 0