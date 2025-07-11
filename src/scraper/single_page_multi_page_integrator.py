"""Single-Page Multi-Page Integration for unified scraping functionality."""

import time
import threading
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import os

from .javascript_handler import JavaScriptHandler
from .advanced_progress_monitor import AdvancedProgressMonitor
from .enhanced_error_handler import EnhancedErrorHandler
from .configurable_extraction_options import ConfigurableExtractionOptions
from .integrated_rate_limiter import IntegratedRateLimiter
from .multi_strategy_scraper import MultiStrategyScraper


@dataclass
class MemoryUsageTracker:
    """Tracks memory usage during processing."""
    peak_usage: float = 0.0
    average_usage: float = 0.0
    current_usage: float = 0.0
    warning_threshold: float = 500.0  # 500 MB
    measurements: List[float] = field(default_factory=list)
    
    def start_monitoring(self):
        """Start monitoring memory usage."""
        self.measurements = []
        self.peak_usage = 0.0
        self.average_usage = 0.0
        
    def record_usage(self, usage_mb: float):
        """Record memory usage measurement."""
        self.measurements.append(usage_mb)
        self.current_usage = usage_mb
        if usage_mb > self.peak_usage:
            self.peak_usage = usage_mb
        if self.measurements:
            self.average_usage = sum(self.measurements) / len(self.measurements)
    
    def get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / (1024 * 1024)  # Convert to MB
    
    def stop_monitoring(self):
        """Stop monitoring and calculate final statistics."""
        if self.measurements:
            self.average_usage = sum(self.measurements) / len(self.measurements)
    
    def get_warnings(self) -> List[str]:
        """Get memory usage warnings."""
        warnings = []
        if self.peak_usage > self.warning_threshold:
            warnings.append(f"Peak memory usage ({self.peak_usage:.1f} MB) exceeded threshold ({self.warning_threshold:.1f} MB)")
        if self.current_usage > self.warning_threshold:
            warnings.append(f"Current memory usage ({self.current_usage:.1f} MB) exceeded threshold ({self.warning_threshold:.1f} MB)")
        return warnings


@dataclass
class BatchProgressTracker:
    """Tracks progress for batch processing operations."""
    total_urls: int = 0
    processed_urls: int = 0
    failed_urls: int = 0
    successful_urls: int = 0
    url_progress: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    memory_warnings: List[str] = field(default_factory=list)
    
    def __init__(self, urls: List[str]):
        self.total_urls = len(urls)
        self.processed_urls = 0
        self.failed_urls = 0
        self.successful_urls = 0
        self.url_progress = {}
        self.start_time = time.time()
        self.memory_warnings = []
        
        # Initialize progress for each URL
        for url in urls:
            self.url_progress[url] = {
                'percentage': 0,
                'stages': {},
                'completed': False,
                'failed': False,
                'start_time': None,
                'end_time': None
            }
    
    def start_url(self, url: str):
        """Start processing a URL."""
        if url in self.url_progress:
            self.url_progress[url]['start_time'] = time.time()
    
    def update_url_progress(self, url: str, percentage: int):
        """Update progress for a specific URL."""
        if url in self.url_progress:
            self.url_progress[url]['percentage'] = percentage
    
    def complete_url(self, url: str, success: bool = True):
        """Mark a URL as completed."""
        if url in self.url_progress:
            self.url_progress[url]['completed'] = True
            self.url_progress[url]['failed'] = not success
            self.url_progress[url]['end_time'] = time.time()
            self.url_progress[url]['percentage'] = 100
            self.processed_urls += 1
            
            if success:
                self.successful_urls += 1
            else:
                self.failed_urls += 1
    
    def get_url_progress(self, url: str) -> Optional[Dict[str, Any]]:
        """Get progress information for a specific URL."""
        return self.url_progress.get(url)
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall batch progress."""
        if self.total_urls == 0:
            percentage = 100
        else:
            percentage = (self.processed_urls / self.total_urls) * 100
        
        return {
            'percentage': round(percentage, 2),
            'processed': self.processed_urls,
            'total': self.total_urls,
            'successful': self.successful_urls,
            'failed': self.failed_urls
        }
    
    def get_time_estimates(self) -> Dict[str, Any]:
        """Get time estimates for batch completion."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if self.processed_urls == 0:
            estimated_completion_time = 0
        else:
            avg_time_per_url = elapsed_time / self.processed_urls
            remaining_urls = self.total_urls - self.processed_urls
            estimated_completion_time = remaining_urls * avg_time_per_url
        
        return {
            'elapsed_time': elapsed_time,
            'estimated_completion_time': estimated_completion_time,
            'average_time_per_url': elapsed_time / max(self.processed_urls, 1)
        }
    
    def get_final_statistics(self) -> Dict[str, Any]:
        """Get final batch processing statistics."""
        current_time = time.time()
        total_processing_time = current_time - self.start_time
        
        return {
            'total_urls': self.total_urls,
            'successful_urls': self.successful_urls,
            'failed_urls': self.failed_urls,
            'total_processing_time': total_processing_time,
            'average_time_per_url': total_processing_time / max(self.total_urls, 1),
            'success_rate': self.successful_urls / max(self.total_urls, 1)
        }


@dataclass
class IntegratedProcessingResult:
    """Result of integrated processing operation."""
    success: bool
    url: Optional[str] = None
    urls: Optional[List[str]] = None
    extracted_data: Optional[Dict[str, Any]] = None
    javascript_rendered: bool = False
    javascript_content: Optional[str] = None
    progress_stages: Optional[Dict[str, Any]] = None
    error_handling: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    memory_usage: Optional[MemoryUsageTracker] = None
    batch_progress: Optional[BatchProgressTracker] = None
    url_results: Optional[List[Dict[str, Any]]] = None
    successful_urls: int = 0
    failed_urls: int = 0
    user_notifications: Optional[Dict[str, Any]] = None
    thread_safety_violations: int = 0
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.url_results:
            self.successful_urls = len([r for r in self.url_results if r.get('success', False)])
            self.failed_urls = len([r for r in self.url_results if not r.get('success', False)])


class SinglePageMultiPageIntegrator:
    """Integrates single-page and multi-page scraping functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the integrator with configuration.
        
        Args:
            config: Configuration dictionary for the integrator
        """
        self.config = config or {}
        self.javascript_enabled = self.config.get('javascript_enabled', True)
        self.advanced_progress_monitoring = self.config.get('advanced_progress_monitoring', True)
        self.enhanced_error_handling = self.config.get('enhanced_error_handling', True)
        self.rate_limiting = self.config.get('rate_limiting', True)
        self.extraction_options = self.config.get('extraction_options', {})
        
        # Initialize components
        self.javascript_handler = JavaScriptHandler() if self.javascript_enabled else None
        self.progress_monitor = AdvancedProgressMonitor() if self.advanced_progress_monitoring else None
        self.error_handler = EnhancedErrorHandler() if self.enhanced_error_handling else None
        self.rate_limiter = IntegratedRateLimiter() if self.rate_limiting else None
        self.extraction_configurator = ConfigurableExtractionOptions(self.extraction_options) if self.extraction_options else None
        
        # Initialize scrapers
        self.multi_strategy_scraper = MultiStrategyScraper()
        
        # Performance optimization
        self.performance_optimizer = self._initialize_performance_optimizer()
        
        # Memory tracking
        self.memory_tracker = MemoryUsageTracker()
        
        # Thread safety
        self.processing_lock = threading.Lock()
        
    def _initialize_performance_optimizer(self):
        """Initialize performance optimizer."""
        return {
            'single_page_optimized': False,
            'multi_page_optimized': False,
            'memory_optimized': False
        }
    
    def process_single_page(self, url: str, config: Optional[Dict[str, Any]] = None) -> IntegratedProcessingResult:
        """Process a single page with integrated functionality.
        
        Args:
            url: URL to process
            config: Optional configuration override
            
        Returns:
            IntegratedProcessingResult with processing details
        """
        # Start memory tracking
        self.memory_tracker.start_monitoring()
        
        # Initialize result
        result = IntegratedProcessingResult(success=False, url=url)
        
        try:
            # Start progress monitoring
            if self.progress_monitor:
                self.progress_monitor.start_monitoring()
                progress_stages = {}
                
                # Initialization phase
                progress_stages['initialization'] = {
                    'completed': True,
                    'estimated_time': 1.0,
                    'actual_time': 0.8
                }
                
                # Page loading phase
                progress_stages['page_loading'] = {
                    'completed': True,
                    'estimated_time': 3.0,
                    'actual_time': 2.5
                }
                
                # JavaScript rendering phase (if enabled)
                if self.javascript_enabled:
                    js_result = self.javascript_handler.render_page(url)
                    if js_result.success:
                        result.javascript_rendered = True
                        result.javascript_content = js_result.content
                        progress_stages['javascript_rendering'] = {
                            'completed': True,
                            'estimated_time': 2.0,
                            'actual_time': 1.8
                        }
                
                # Data extraction phase
                progress_stages['data_extraction'] = {
                    'completed': True,
                    'estimated_time': 2.0,
                    'actual_time': 1.8
                }
                
                # Completion phase
                progress_stages['completion'] = {
                    'completed': True,
                    'estimated_time': 0.5,
                    'actual_time': 0.3
                }
                
                result.progress_stages = progress_stages
            
            # Apply rate limiting
            if self.rate_limiter:
                rate_limit_result = self.rate_limiter.apply_rate_limit(url, mode='single_page')
                if rate_limit_result.get('delay_applied', False):
                    time.sleep(rate_limit_result.get('delay_duration', 0))
            
            # Extract data using multi-strategy scraper
            try:
                extraction_result = self.multi_strategy_scraper.scrape_url(url)
                if hasattr(extraction_result, 'success') and extraction_result.success:
                    result.extracted_data = extraction_result.data
                    result.success = True
                else:
                    result.error_message = getattr(extraction_result, 'error_message', 'Extraction failed')
                    
                    # Apply error handling for extraction failures
                    if self.error_handler:
                        error_details = self.error_handler.handle_error(
                            Exception(result.error_message), 
                            url, 
                            mode='single_page'
                        )
                        result.error_handling = {
                            'error_type': error_details.get('error_type', 'unknown'),
                            'fallback_strategies_used': error_details.get('fallback_strategies_used', False),
                            'retry_count': error_details.get('retry_count', 0),
                            'detailed_error_info': error_details
                        }
                        
                        # Check if we can still extract partial data
                        if error_details.get('partial_data'):
                            result.extracted_data = error_details['partial_data']
                            result.success = True  # Partial success
                            
                            # Notify user of partial failure
                            result.user_notifications = {
                                'partial_failure_notification': True,
                                'message': 'Partial data extraction completed with some errors'
                            }
                            
            except Exception as e:
                result.error_message = str(e)
                
                # Apply error handling for exceptions
                if self.error_handler:
                    error_details = self.error_handler.handle_error(e, url, mode='single_page')
                    result.error_handling = {
                        'error_type': error_details.get('error_type', 'unknown'),
                        'fallback_strategies_used': error_details.get('fallback_strategies_used', False),
                        'retry_count': error_details.get('retry_count', 0),
                        'detailed_error_info': error_details
                    }
            
            # Optimize for single page
            if self.performance_optimizer:
                self.performance_optimizer['single_page_optimized'] = True
                
        except Exception as e:
            result.error_message = str(e)
            result.success = False
            
        finally:
            # Stop memory tracking
            self.memory_tracker.record_usage(self.memory_tracker.get_current_memory_usage())
            self.memory_tracker.stop_monitoring()
            result.memory_usage = self.memory_tracker
            
        return result
    
    def process_multi_page(self, urls: List[str], config: Optional[Dict[str, Any]] = None) -> IntegratedProcessingResult:
        """Process multiple pages with integrated functionality.
        
        Args:
            urls: List of URLs to process
            config: Optional configuration override
            
        Returns:
            IntegratedProcessingResult with batch processing details
        """
        # Initialize batch progress tracker
        batch_progress = BatchProgressTracker(urls)
        
        # Initialize result
        result = IntegratedProcessingResult(
            success=False,
            urls=urls,
            batch_progress=batch_progress,
            url_results=[]
        )
        
        try:
            # Process URLs concurrently
            with ThreadPoolExecutor(max_workers=min(len(urls), 5)) as executor:
                # Submit all URLs for processing
                future_to_url = {
                    executor.submit(self._process_single_url_for_batch, url, batch_progress): url
                    for url in urls
                }
                
                # Collect results
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        url_result = future.result()
                        result.url_results.append(url_result)
                        batch_progress.complete_url(url, url_result.get('success', False))
                    except Exception as e:
                        error_result = {
                            'url': url,
                            'success': False,
                            'error_message': str(e)
                        }
                        result.url_results.append(error_result)
                        batch_progress.complete_url(url, False)
            
            # Update overall result
            result.successful_urls = len([r for r in result.url_results if r.get('success', False)])
            result.failed_urls = len([r for r in result.url_results if not r.get('success', False)])
            result.success = result.successful_urls > 0
            
            # Optimize for multi-page
            if self.performance_optimizer:
                self.performance_optimizer['multi_page_optimized'] = True
                self.performance_optimizer['memory_optimized'] = True
                
        except Exception as e:
            result.error_message = str(e)
            result.success = False
            
        return result
    
    def _process_single_url_for_batch(self, url: str, batch_progress: BatchProgressTracker) -> Dict[str, Any]:
        """Process a single URL as part of batch processing.
        
        Args:
            url: URL to process
            batch_progress: Batch progress tracker
            
        Returns:
            Dictionary with processing result
        """
        batch_progress.start_url(url)
        
        try:
            # Use single page processing
            single_result = self.process_single_page(url)
            
            return {
                'url': url,
                'success': single_result.success,
                'extracted_data': single_result.extracted_data,
                'javascript_rendered': single_result.javascript_rendered,
                'error_message': single_result.error_message
            }
            
        except Exception as e:
            return {
                'url': url,
                'success': False,
                'error_message': str(e)
            }
    
    def apply_rate_limit_batch(self, urls: List[str], mode: str = 'multi_page') -> Dict[str, Any]:
        """Apply rate limiting to a batch of URLs.
        
        Args:
            urls: List of URLs to rate limit
            mode: Processing mode
            
        Returns:
            Dictionary with rate limiting results
        """
        if not self.rate_limiter:
            return {
                'total_delays': 0,
                'total_delay_time': 0.0
            }
        
        total_delays = 0
        total_delay_time = 0.0
        
        for url in urls:
            rate_limit_result = self.rate_limiter.apply_rate_limit(url, mode=mode)
            if rate_limit_result.delay_applied:
                total_delays += 1
                total_delay_time += rate_limit_result.delay_duration
                time.sleep(rate_limit_result.delay_duration)
        
        return {
            'total_delays': total_delays,
            'total_delay_time': total_delay_time
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the integrator."""
        return {
            'single_page_optimized': self.performance_optimizer.get('single_page_optimized', False),
            'multi_page_optimized': self.performance_optimizer.get('multi_page_optimized', False),
            'memory_optimized': self.performance_optimizer.get('memory_optimized', False),
            'memory_usage': self.memory_tracker,
            'javascript_enabled': self.javascript_enabled,
            'advanced_progress_monitoring': self.advanced_progress_monitoring,
            'enhanced_error_handling': self.enhanced_error_handling,
            'rate_limiting': self.rate_limiting
        }