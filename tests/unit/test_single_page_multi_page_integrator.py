"""Unit tests for SinglePageMultiPageIntegrator."""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
import time
import threading

# Import the module we're testing
try:
    from src.scraper.single_page_multi_page_integrator import SinglePageMultiPageIntegrator
    from src.scraper.single_page_multi_page_integrator import IntegratedProcessingResult
    from src.scraper.single_page_multi_page_integrator import BatchProgressTracker
    from src.scraper.single_page_multi_page_integrator import MemoryUsageTracker
except ImportError:
    SinglePageMultiPageIntegrator = None
    IntegratedProcessingResult = None
    BatchProgressTracker = None
    MemoryUsageTracker = None


class TestSinglePageMultiPageIntegrator:
    """Test cases for SinglePageMultiPageIntegrator."""

    def test_integrator_initialization(self):
        """Test that the integrator initializes correctly."""
        if SinglePageMultiPageIntegrator is None:
            pytest.fail("SinglePageMultiPageIntegrator not implemented - TDD RED phase")
        
        integrator = SinglePageMultiPageIntegrator()
        assert integrator is not None
        assert integrator.javascript_handler is not None
        assert integrator.progress_monitor is not None
        assert integrator.error_handler is not None
        assert integrator.rate_limiter is not None

    def test_integrator_initialization_with_config(self):
        """Test integrator initialization with custom configuration."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {
            'javascript_enabled': True,
            'advanced_progress_monitoring': True,
            'enhanced_error_handling': True,
            'rate_limiting': True
        }
        
        integrator = SinglePageMultiPageIntegrator(config=config)
        assert integrator.config == config
        assert integrator.javascript_enabled is True
        assert integrator.advanced_progress_monitoring is True

    def test_process_single_page_basic(self):
        """Test basic single-page processing."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        integrator = SinglePageMultiPageIntegrator()
        url = "https://test-restaurant.com"
        
        # Mock dependencies
        with patch.object(integrator, 'javascript_handler') as mock_js:
            with patch.object(integrator, 'progress_monitor') as mock_progress:
                with patch.object(integrator, 'error_handler') as mock_error:
                    
                    # Setup mocks
                    mock_js.render_page.return_value = Mock(success=True, content="<html>test</html>")
                    mock_progress.start_monitoring.return_value = True
                    mock_error.handle_errors.return_value = True
                    
                    result = integrator.process_single_page(url)
                    
                    assert result is not None
                    assert isinstance(result, IntegratedProcessingResult)
                    assert result.success is True
                    assert result.url == url

    def test_process_single_page_with_javascript_enabled(self):
        """Test single-page processing with JavaScript enabled."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'javascript_enabled': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        url = "https://js-restaurant.com"
        
        with patch.object(integrator, 'javascript_handler') as mock_js:
            mock_js.render_page.return_value = Mock(
                success=True, 
                content="<html>JS rendered content</html>",
                javascript_rendered=True
            )
            
            result = integrator.process_single_page(url)
            
            assert result.javascript_rendered is True
            assert result.javascript_content is not None
            mock_js.render_page.assert_called_once_with(url)

    def test_process_single_page_with_advanced_progress_monitoring(self):
        """Test single-page processing with advanced progress monitoring."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'advanced_progress_monitoring': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        url = "https://test-restaurant.com"
        
        with patch.object(integrator, 'progress_monitor') as mock_progress:
            mock_progress.start_monitoring.return_value = True
            mock_progress.get_detailed_progress.return_value = {
                'initialization': {'completed': True, 'estimated_time': 1.0, 'actual_time': 0.8},
                'page_loading': {'completed': True, 'estimated_time': 3.0, 'actual_time': 2.5},
                'data_extraction': {'completed': True, 'estimated_time': 2.0, 'actual_time': 1.8},
                'completion': {'completed': True, 'estimated_time': 0.5, 'actual_time': 0.3}
            }
            
            result = integrator.process_single_page(url)
            
            assert result.progress_stages is not None
            assert 'initialization' in result.progress_stages
            assert 'page_loading' in result.progress_stages
            assert 'data_extraction' in result.progress_stages
            assert 'completion' in result.progress_stages
            mock_progress.start_monitoring.assert_called_once()

    def test_process_single_page_with_error_handling(self):
        """Test single-page processing with enhanced error handling."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'enhanced_error_handling': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        url = "https://problematic-restaurant.com"
        
        with patch.object(integrator, 'error_handler') as mock_error:
            # Simulate an error that gets handled
            mock_error.handle_errors.return_value = True
            mock_error.get_error_details.return_value = {
                'error_type': 'javascript_timeout',
                'error_message': 'JavaScript rendering timed out',
                'fallback_strategies_used': True,
                'retry_count': 2
            }
            
            result = integrator.process_single_page(url)
            
            assert result.error_handling is not None
            assert result.error_handling.fallback_strategies_used is True
            assert result.error_handling.retry_count == 2
            mock_error.handle_errors.assert_called_once()

    def test_process_multi_page_basic(self):
        """Test basic multi-page processing."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        integrator = SinglePageMultiPageIntegrator()
        urls = [
            "https://restaurant1.com",
            "https://restaurant2.com",
            "https://restaurant3.com"
        ]
        
        with patch.object(integrator, 'process_single_page') as mock_single:
            mock_single.return_value = Mock(success=True, url="test_url")
            
            result = integrator.process_multi_page(urls)
            
            assert result is not None
            assert isinstance(result, IntegratedProcessingResult)
            assert result.success is True
            assert len(result.url_results) == 3
            assert mock_single.call_count == 3

    def test_process_multi_page_with_batch_progress_tracking(self):
        """Test multi-page processing with batch progress tracking."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'advanced_progress_monitoring': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        urls = [
            "https://restaurant1.com",
            "https://restaurant2.com",
            "https://restaurant3.com",
            "https://restaurant4.com"
        ]
        
        with patch.object(integrator, 'batch_progress_tracker') as mock_tracker:
            mock_tracker.get_overall_progress.return_value = Mock(percentage=100)
            mock_tracker.get_url_progress.return_value = Mock(percentage=100)
            mock_tracker.get_final_statistics.return_value = Mock(
                total_urls=4,
                successful_urls=4,
                failed_urls=0,
                total_processing_time=15.5
            )
            
            result = integrator.process_multi_page(urls)
            
            assert result.batch_progress is not None
            assert result.batch_progress.overall_progress is not None
            assert result.batch_progress.final_statistics is not None
            assert result.batch_progress.final_statistics.total_urls == 4

    def test_process_multi_page_with_javascript_enabled(self):
        """Test multi-page processing with JavaScript enabled."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'javascript_enabled': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        urls = ["https://js-restaurant1.com", "https://js-restaurant2.com"]
        
        with patch.object(integrator, 'javascript_handler') as mock_js:
            mock_js.render_page.return_value = Mock(
                success=True,
                content="<html>JS content</html>",
                javascript_rendered=True
            )
            
            result = integrator.process_multi_page(urls)
            
            assert result.success is True
            for url_result in result.url_results:
                assert url_result.javascript_rendered is True

    def test_process_multi_page_with_rate_limiting(self):
        """Test multi-page processing with rate limiting."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'rate_limiting': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        urls = [
            "https://restaurant1.com",
            "https://restaurant2.com",
            "https://restaurant3.com"
        ]
        
        with patch.object(integrator, 'rate_limiter') as mock_limiter:
            mock_limiter.check_rate_limit.return_value = True
            mock_limiter.apply_delay.return_value = True
            
            start_time = time.time()
            result = integrator.process_multi_page(urls)
            end_time = time.time()
            
            assert result.success is True
            assert mock_limiter.check_rate_limit.call_count == 3
            assert mock_limiter.apply_delay.call_count >= 2  # At least some delays applied

    def test_process_multi_page_with_error_recovery(self):
        """Test multi-page processing with error recovery."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'enhanced_error_handling': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        urls = [
            "https://working-restaurant.com",
            "https://broken-restaurant.com",
            "https://another-working-restaurant.com"
        ]
        
        def mock_single_page_side_effect(url):
            if "broken" in url:
                return Mock(success=False, error_message="Connection failed")
            return Mock(success=True, url=url)
        
        with patch.object(integrator, 'process_single_page', side_effect=mock_single_page_side_effect):
            result = integrator.process_multi_page(urls)
            
            assert result.successful_urls == 2
            assert result.failed_urls == 1
            assert len(result.url_results) == 3

    def test_configuration_preservation_across_modes(self):
        """Test that configuration is preserved when switching between modes."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {
            'javascript_enabled': True,
            'advanced_progress_monitoring': True,
            'enhanced_error_handling': True,
            'rate_limiting': True,
            'extraction_options': {'fields': ['name', 'address', 'phone']}
        }
        
        integrator = SinglePageMultiPageIntegrator(config=config)
        
        # Test single-page mode
        with patch.object(integrator, 'process_single_page') as mock_single:
            mock_single.return_value = Mock(success=True)
            integrator.process_single_page("https://test.com")
            mock_single.assert_called_once_with("https://test.com")
        
        # Test multi-page mode with same config
        with patch.object(integrator, 'process_multi_page') as mock_multi:
            mock_multi.return_value = Mock(success=True)
            integrator.process_multi_page(["https://test1.com", "https://test2.com"])
            mock_multi.assert_called_once()
        
        # Verify config is preserved
        assert integrator.config == config

    def test_memory_usage_tracking(self):
        """Test memory usage tracking during processing."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {'advanced_progress_monitoring': True}
        integrator = SinglePageMultiPageIntegrator(config=config)
        
        with patch.object(integrator, 'memory_tracker') as mock_tracker:
            mock_tracker.get_memory_usage.return_value = Mock(
                peak_usage=150.5,
                average_usage=95.2,
                current_usage=120.3
            )
            
            result = integrator.process_single_page("https://test.com")
            
            assert result.memory_usage is not None
            assert result.memory_usage.peak_usage > 0
            assert result.memory_usage.average_usage > 0

    def test_extraction_options_configuration(self):
        """Test configurable extraction options."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        config = {
            'extraction_options': {
                'fields': ['name', 'address', 'phone'],
                'priorities': {'name': 1, 'address': 2, 'phone': 3},
                'output_format': 'json'
            }
        }
        
        integrator = SinglePageMultiPageIntegrator(config=config)
        
        with patch.object(integrator, 'extraction_configurator') as mock_config:
            mock_config.configure_extraction.return_value = True
            
            result = integrator.process_single_page("https://test.com")
            
            mock_config.configure_extraction.assert_called_once()
            assert integrator.extraction_options == config['extraction_options']

    def test_thread_safety_multi_page_processing(self):
        """Test thread safety during multi-page processing."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        integrator = SinglePageMultiPageIntegrator()
        urls = [f"https://restaurant{i}.com" for i in range(10)]
        
        def mock_process_single_page(url):
            # Simulate some processing time
            time.sleep(0.01)
            return Mock(success=True, url=url)
        
        with patch.object(integrator, 'process_single_page', side_effect=mock_process_single_page):
            result = integrator.process_multi_page(urls)
            
            assert result.success is True
            assert len(result.url_results) == 10
            assert result.thread_safety_violations == 0

    def test_performance_optimization_single_vs_multi_page(self):
        """Test performance optimization differences between single and multi-page modes."""
        if SinglePageMultiPageIntegrator is None:
            pytest.skip("SinglePageMultiPageIntegrator not implemented yet")
        
        integrator = SinglePageMultiPageIntegrator()
        
        # Test single-page optimization
        with patch.object(integrator, 'performance_optimizer') as mock_optimizer:
            mock_optimizer.optimize_for_single_page.return_value = True
            
            result = integrator.process_single_page("https://test.com")
            
            mock_optimizer.optimize_for_single_page.assert_called_once()
        
        # Test multi-page optimization
        with patch.object(integrator, 'performance_optimizer') as mock_optimizer:
            mock_optimizer.optimize_for_batch.return_value = True
            
            result = integrator.process_multi_page(["https://test1.com", "https://test2.com"])
            
            mock_optimizer.optimize_for_batch.assert_called_once()


class TestIntegratedProcessingResult:
    """Test cases for IntegratedProcessingResult."""

    def test_processing_result_initialization(self):
        """Test processing result initialization."""
        if IntegratedProcessingResult is None:
            pytest.skip("IntegratedProcessingResult not implemented yet")
        
        result = IntegratedProcessingResult(
            success=True,
            url="https://test.com",
            extracted_data={"name": "Test Restaurant"}
        )
        
        assert result.success is True
        assert result.url == "https://test.com"
        assert result.extracted_data is not None

    def test_processing_result_javascript_properties(self):
        """Test processing result JavaScript-related properties."""
        if IntegratedProcessingResult is None:
            pytest.skip("IntegratedProcessingResult not implemented yet")
        
        result = IntegratedProcessingResult(
            success=True,
            url="https://test.com",
            javascript_rendered=True,
            javascript_content="<div>JS content</div>"
        )
        
        assert result.javascript_rendered is True
        assert result.javascript_content is not None

    def test_processing_result_progress_tracking(self):
        """Test processing result progress tracking."""
        if IntegratedProcessingResult is None:
            pytest.skip("IntegratedProcessingResult not implemented yet")
        
        progress_stages = {
            'initialization': {'completed': True, 'estimated_time': 1.0, 'actual_time': 0.8},
            'page_loading': {'completed': True, 'estimated_time': 3.0, 'actual_time': 2.5}
        }
        
        result = IntegratedProcessingResult(
            success=True,
            url="https://test.com",
            progress_stages=progress_stages
        )
        
        assert result.progress_stages is not None
        assert 'initialization' in result.progress_stages
        assert 'page_loading' in result.progress_stages

    def test_processing_result_error_handling(self):
        """Test processing result error handling information."""
        if IntegratedProcessingResult is None:
            pytest.skip("IntegratedProcessingResult not implemented yet")
        
        error_info = Mock()
        error_info.error_type = "javascript_timeout"
        error_info.fallback_strategies_used = True
        error_info.retry_count = 2
        
        result = IntegratedProcessingResult(
            success=False,
            url="https://test.com",
            error_handling=error_info
        )
        
        assert result.success is False
        assert result.error_handling is not None
        assert result.error_handling.fallback_strategies_used is True


class TestBatchProgressTracker:
    """Test cases for BatchProgressTracker."""

    def test_batch_progress_tracker_initialization(self):
        """Test batch progress tracker initialization."""
        if BatchProgressTracker is None:
            pytest.skip("BatchProgressTracker not implemented yet")
        
        urls = ["https://test1.com", "https://test2.com", "https://test3.com"]
        tracker = BatchProgressTracker(urls)
        
        assert tracker.total_urls == 3
        assert tracker.processed_urls == 0
        assert tracker.failed_urls == 0

    def test_batch_progress_tracker_url_progress(self):
        """Test batch progress tracker URL progress tracking."""
        if BatchProgressTracker is None:
            pytest.skip("BatchProgressTracker not implemented yet")
        
        urls = ["https://test1.com", "https://test2.com"]
        tracker = BatchProgressTracker(urls)
        
        tracker.update_url_progress("https://test1.com", 50)
        tracker.update_url_progress("https://test2.com", 25)
        
        assert tracker.get_url_progress("https://test1.com").percentage == 50
        assert tracker.get_url_progress("https://test2.com").percentage == 25

    def test_batch_progress_tracker_overall_progress(self):
        """Test batch progress tracker overall progress calculation."""
        if BatchProgressTracker is None:
            pytest.skip("BatchProgressTracker not implemented yet")
        
        urls = ["https://test1.com", "https://test2.com", "https://test3.com"]
        tracker = BatchProgressTracker(urls)
        
        tracker.complete_url("https://test1.com")
        tracker.complete_url("https://test2.com")
        
        overall_progress = tracker.get_overall_progress()
        assert overall_progress.percentage == 66.67  # 2/3 complete

    def test_batch_progress_tracker_time_estimation(self):
        """Test batch progress tracker time estimation."""
        if BatchProgressTracker is None:
            pytest.skip("BatchProgressTracker not implemented yet")
        
        urls = ["https://test1.com", "https://test2.com", "https://test3.com"]
        tracker = BatchProgressTracker(urls)
        
        # Complete first URL in 5 seconds
        tracker.start_url("https://test1.com")
        time.sleep(0.01)  # Simulate processing time
        tracker.complete_url("https://test1.com")
        
        time_estimates = tracker.get_time_estimates()
        assert time_estimates.estimated_completion_time > 0


class TestMemoryUsageTracker:
    """Test cases for MemoryUsageTracker."""

    def test_memory_usage_tracker_initialization(self):
        """Test memory usage tracker initialization."""
        if MemoryUsageTracker is None:
            pytest.skip("MemoryUsageTracker not implemented yet")
        
        tracker = MemoryUsageTracker()
        assert tracker.peak_usage == 0
        assert tracker.average_usage == 0
        assert tracker.current_usage >= 0

    def test_memory_usage_tracker_monitoring(self):
        """Test memory usage tracker monitoring."""
        if MemoryUsageTracker is None:
            pytest.skip("MemoryUsageTracker not implemented yet")
        
        tracker = MemoryUsageTracker()
        tracker.start_monitoring()
        
        # Simulate some memory usage
        time.sleep(0.01)
        
        tracker.stop_monitoring()
        
        assert tracker.peak_usage > 0
        assert tracker.average_usage > 0

    def test_memory_usage_tracker_warnings(self):
        """Test memory usage tracker warnings."""
        if MemoryUsageTracker is None:
            pytest.skip("MemoryUsageTracker not implemented yet")
        
        tracker = MemoryUsageTracker(warning_threshold=100)  # 100 MB threshold
        
        # Simulate high memory usage
        tracker.record_usage(150)  # 150 MB
        
        warnings = tracker.get_warnings()
        assert len(warnings) > 0
        assert "memory usage exceeded threshold" in warnings[0].lower()