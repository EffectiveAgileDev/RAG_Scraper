"""Batch processing engine for memory-efficient URL processing."""
import gc
import time
import psutil
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .multi_strategy_scraper import MultiStrategyScraper, RestaurantData


@dataclass
class BatchProgress:
    """Progress tracking for batch operations."""
    current_url: str = ""
    urls_completed: int = 0
    urls_total: int = 0
    progress_percentage: float = 0.0
    estimated_time_remaining: float = 0.0
    current_operation: str = ""
    errors_count: int = 0
    memory_usage_mb: float = 0.0
    start_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'current_url': self.current_url,
            'urls_completed': self.urls_completed,
            'urls_total': self.urls_total,
            'progress_percentage': self.progress_percentage,
            'estimated_time_remaining': self.estimated_time_remaining,
            'current_operation': self.current_operation,
            'errors_count': self.errors_count,
            'memory_usage_mb': self.memory_usage_mb,
            'elapsed_time': time.time() - self.start_time if self.start_time > 0 else 0.0
        }


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    max_concurrent_requests: int = 3
    memory_limit_mb: int = 512
    chunk_size: int = 10  # Process in chunks to manage memory
    enable_memory_monitoring: bool = True
    gc_frequency: int = 5  # Run garbage collection every N URLs
    timeout_per_url: int = 30
    enable_progressive_saving: bool = True
    save_frequency: int = 20  # Save progress every N URLs


class MemoryMonitor:
    """Monitor memory usage during batch processing."""
    
    def __init__(self, limit_mb: int = 512):
        self.limit_mb = limit_mb
        self.peak_usage_mb = 0.0
        self.current_usage_mb = 0.0
        
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        usage_bytes = process.memory_info().rss
        usage_mb = usage_bytes / (1024 * 1024)
        
        self.current_usage_mb = usage_mb
        if usage_mb > self.peak_usage_mb:
            self.peak_usage_mb = usage_mb
            
        return usage_mb
    
    def is_memory_critical(self) -> bool:
        """Check if memory usage is approaching critical levels."""
        return self.get_memory_usage_mb() > (self.limit_mb * 0.9)
    
    def force_gc_if_needed(self) -> bool:
        """Force garbage collection if memory is high."""
        if self.is_memory_critical():
            gc.collect()
            return True
        return False


class BatchProcessor:
    """Memory-efficient batch processor for restaurant scraping."""
    
    def __init__(self, config: BatchConfig = None):
        """Initialize batch processor."""
        self.config = config or BatchConfig()
        self.scraper = MultiStrategyScraper(enable_ethical_scraping=True)
        self.memory_monitor = MemoryMonitor(self.config.memory_limit_mb)
        self.progress = BatchProgress()
        self._stop_requested = False
        
    def process_batch(self, urls: List[str], 
                     progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Process a batch of URLs with memory management."""
        self.progress = BatchProgress(
            urls_total=len(urls),
            start_time=time.time()
        )
        
        if progress_callback:
            progress_callback("Initializing batch processing...", 0)
        
        successful_extractions = []
        failed_urls = []
        errors = []
        
        try:
            # Process URLs in chunks to manage memory
            chunk_size = min(self.config.chunk_size, len(urls))
            
            for chunk_start in range(0, len(urls), chunk_size):
                if self._stop_requested:
                    break
                    
                chunk_end = min(chunk_start + chunk_size, len(urls))
                chunk_urls = urls[chunk_start:chunk_end]
                
                if progress_callback:
                    progress_callback(
                        f"Processing chunk {chunk_start//chunk_size + 1} "
                        f"({chunk_start + 1}-{chunk_end} of {len(urls)})", 
                        int((chunk_start / len(urls)) * 100)
                    )
                
                # Process chunk with memory monitoring
                chunk_results = self._process_chunk(
                    chunk_urls, 
                    chunk_start, 
                    progress_callback
                )
                
                successful_extractions.extend(chunk_results['successful'])
                failed_urls.extend(chunk_results['failed'])
                errors.extend(chunk_results['errors'])
                
                # Update progress
                self.progress.urls_completed = chunk_end
                self.progress.progress_percentage = (chunk_end / len(urls)) * 100
                
                # Memory management between chunks
                if self.config.enable_memory_monitoring:
                    self.memory_monitor.force_gc_if_needed()
                    
                # Progressive saving if enabled
                if (self.config.enable_progressive_saving and 
                    chunk_end % self.config.save_frequency == 0):
                    if progress_callback:
                        progress_callback(
                            f"Saving progress... ({chunk_end} URLs processed)", 
                            None
                        )
                    
        except Exception as e:
            errors.append(f"Batch processing error: {str(e)}")
            
        finally:
            processing_time = time.time() - self.progress.start_time
            
            if progress_callback:
                progress_callback("Batch processing completed", 100)
        
        # Return data that can be used to create ScrapingResult
        return {
            'successful_extractions': successful_extractions,
            'failed_urls': failed_urls,
            'total_processed': len(urls),
            'errors': errors,
            'processing_time': processing_time
        }
    
    def _process_chunk(self, urls: List[str], offset: int, 
                      progress_callback: Optional[Callable] = None) -> Dict[str, List]:
        """Process a chunk of URLs with detailed progress tracking."""
        results = {
            'successful': [],
            'failed': [],
            'errors': []
        }
        
        for i, url in enumerate(urls):
            if self._stop_requested:
                break
                
            global_index = offset + i
            
            try:
                # Update progress
                self.progress.current_url = url
                self.progress.current_operation = f"Scraping {url}"
                self.progress.memory_usage_mb = self.memory_monitor.get_memory_usage_mb()
                
                # Calculate time estimate
                if global_index > 0:
                    elapsed = time.time() - self.progress.start_time
                    avg_time_per_url = elapsed / global_index
                    remaining_urls = self.progress.urls_total - global_index
                    self.progress.estimated_time_remaining = avg_time_per_url * remaining_urls
                
                if progress_callback:
                    # Enhanced progress message format for batch processing
                    if self.progress.urls_total > 1:
                        message = f"Processing {global_index + 1} of {self.progress.urls_total}: {url}"
                    else:
                        message = f"Processing {url}"
                    
                    progress_callback(
                        message, 
                        int((global_index / self.progress.urls_total) * 100)
                    )
                    
                    # Add time estimation after first URL
                    if global_index == 0 and self.progress.urls_total > 1:
                        progress_callback("Estimated time remaining: calculating...", None, None)
                    elif (global_index > 0 and self.progress.estimated_time_remaining > 0 and 
                          self.progress.urls_total > 1):
                        time_str = f"{int(self.progress.estimated_time_remaining)} seconds"
                        progress_callback(f"Estimated time remaining: {time_str}", None, 
                                        self.progress.estimated_time_remaining)
                
                # Extract restaurant data
                restaurant_data = self.scraper.scrape_url(url)
                
                if restaurant_data:
                    results['successful'].append(restaurant_data)
                    if progress_callback:
                        progress_callback(
                            f"Successfully extracted data for {restaurant_data.name or 'Unknown Restaurant'}"
                        )
                else:
                    results['failed'].append(url)
                    results['errors'].append(f"No restaurant data found at {url}")
                    
            except Exception as e:
                results['failed'].append(url)
                error_msg = f"Error processing {url}: {str(e)}"
                results['errors'].append(error_msg)
                self.progress.errors_count += 1
                
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
            
            # Memory management during processing
            if ((global_index + 1) % self.config.gc_frequency == 0 and 
                self.config.enable_memory_monitoring):
                self.memory_monitor.force_gc_if_needed()
        
        return results
    
    def stop_processing(self):
        """Request to stop batch processing."""
        self._stop_requested = True
    
    def get_current_progress(self) -> BatchProgress:
        """Get current processing progress."""
        return self.progress
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        return {
            'current_mb': self.memory_monitor.current_usage_mb,
            'peak_mb': self.memory_monitor.peak_usage_mb,
            'limit_mb': self.memory_monitor.limit_mb,
            'usage_percentage': (self.memory_monitor.current_usage_mb / 
                               self.memory_monitor.limit_mb) * 100
        }