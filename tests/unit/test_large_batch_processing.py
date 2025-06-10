"""Unit tests for large batch processing validation (100+ URLs)."""
import time
import pytest
from unittest.mock import Mock, patch

from src.scraper.batch_processor import BatchProcessor, BatchConfig
from src.scraper.restaurant_scraper import RestaurantScraper
from src.config.scraping_config import ScrapingConfig
from src.scraper.multi_strategy_scraper import RestaurantData


class TestLargeBatchProcessing:
    """Test large-scale batch processing capabilities."""

    def test_100_url_batch_processing_memory_efficiency(self):
        """Test that 100 URLs can be processed without memory issues."""
        # Generate 100 test URLs
        urls = [f"http://restaurant{i}.com" for i in range(1, 101)]

        # Create batch processor with conservative memory settings
        config = BatchConfig(
            max_concurrent_requests=2,  # Conservative concurrency
            memory_limit_mb=256,  # Lower memory limit for testing
            chunk_size=5,  # Smaller chunks
            enable_memory_monitoring=True,
            gc_frequency=3,  # More frequent garbage collection
        )

        processor = BatchProcessor(config)

        # Mock the scraper to avoid actual web requests
        with patch.object(processor.scraper, "scrape_url") as mock_scrape:

            def mock_scrape_func(url):
                # Simulate small processing time
                time.sleep(0.001)  # 1ms simulation
                domain = url.replace("http://", "").split(".")[0]
                return RestaurantData(
                    name=domain.title() + " Restaurant",
                    address="123 Test St",
                    phone="555-1234",
                    sources=["mock"],
                )

            mock_scrape.side_effect = mock_scrape_func

            # Track progress
            progress_updates = []

            def progress_callback(message, percentage=None, time_estimate=None):
                progress_updates.append(
                    {
                        "message": message,
                        "percentage": percentage,
                        "time_estimate": time_estimate,
                    }
                )

            # Process batch
            start_time = time.time()
            result = processor.process_batch(urls, progress_callback)
            processing_time = time.time() - start_time

            # Verify results
            assert result["total_processed"] == 100
            assert len(result["successful_extractions"]) == 100
            assert len(result["failed_urls"]) == 0
            assert len(result["errors"]) == 0

            # Verify performance
            assert processing_time < 30, f"Processing took too long: {processing_time}s"

            # Verify progress tracking
            assert len(progress_updates) > 20, "Should have multiple progress updates"

            # Verify memory monitoring
            memory_stats = processor.get_memory_stats()
            assert memory_stats["current_mb"] > 0
            assert memory_stats["peak_mb"] > 0
            assert memory_stats["usage_percentage"] < 200  # Should not exceed 2x limit

    def test_batch_processing_with_failures(self):
        """Test batch processing resilience with some failing URLs."""
        # Generate URLs with some that will fail
        urls = [f"http://restaurant{i}.com" for i in range(1, 51)]
        failing_urls = ["http://fail1.com", "http://fail2.com", "http://fail3.com"]
        all_urls = urls + failing_urls

        config = BatchConfig(chunk_size=10)
        processor = BatchProcessor(config)

        with patch.object(processor.scraper, "scrape_url") as mock_scrape:

            def mock_scrape_func(url):
                if "fail" in url:
                    raise Exception(f"Failed to process {url}")

                domain = url.replace("http://", "").split(".")[0]
                return RestaurantData(
                    name=domain.title() + " Restaurant", sources=["mock"]
                )

            mock_scrape.side_effect = mock_scrape_func

            result = processor.process_batch(all_urls)

            # Verify partial success
            assert result["total_processed"] == 53
            assert len(result["successful_extractions"]) == 50
            assert len(result["failed_urls"]) == 3
            assert len(result["errors"]) == 3

            # Verify failed URLs are correctly identified
            assert all("fail" in url for url in result["failed_urls"])

    def test_batch_processing_progress_accuracy(self):
        """Test that progress reporting is accurate for large batches."""
        urls = [f"http://restaurant{i}.com" for i in range(1, 21)]

        processor = BatchProcessor()
        progress_updates = []

        with patch.object(processor.scraper, "scrape_url") as mock_scrape:
            mock_scrape.return_value = RestaurantData(
                name="Test Restaurant", sources=["mock"]
            )

            def progress_callback(message, percentage=None, time_estimate=None):
                progress_updates.append(
                    {
                        "message": message,
                        "percentage": percentage,
                        "time_estimate": time_estimate,
                        "progress_obj": processor.get_current_progress(),
                    }
                )

            processor.process_batch(urls, progress_callback)

            # Verify progress accuracy
            percentage_updates = [
                u["percentage"] for u in progress_updates if u["percentage"] is not None
            ]

            # Should start near 0 and end at or near 100
            assert percentage_updates[0] <= 10, "Should start near 0%"
            assert percentage_updates[-1] >= 90, "Should end near 100%"

            # Progress should generally increase
            for i in range(1, len(percentage_updates)):
                assert (
                    percentage_updates[i] >= percentage_updates[i - 1]
                ), f"Progress went backwards: {percentage_updates[i-1]}% to {percentage_updates[i]}%"

            # Verify time estimates appear after first URL
            time_estimates = [
                u["time_estimate"]
                for u in progress_updates
                if u["time_estimate"] is not None
            ]
            assert len(time_estimates) > 0, "Should provide time estimates"

    def test_restaurant_scraper_large_batch_integration(self):
        """Test RestaurantScraper with large batch through batch processor."""
        urls = [f"http://restaurant{i}.com" for i in range(1, 31)]

        scraper = RestaurantScraper(enable_batch_processing=True)
        config = ScrapingConfig(urls=urls)
        config.force_batch_processing = True  # Force batch processing

        progress_updates = []

        with patch.object(scraper.multi_scraper, "scrape_url") as mock_scrape:
            mock_scrape.return_value = RestaurantData(
                name="Test Restaurant", sources=["mock"]
            )

            def progress_callback(message, percentage=None, time_estimate=None):
                progress_updates.append({"message": message, "percentage": percentage})

            result = scraper.scrape_restaurants(config, progress_callback)

            # Verify RestaurantScraper properly uses batch processor
            assert result.total_processed == 30
            assert len(result.successful_extractions) == 30
            assert len(result.failed_urls) == 0
            assert result.processing_time > 0

            # Verify progress updates were received
            assert len(progress_updates) > 5, "Should receive multiple progress updates"

    def test_memory_monitoring_accuracy(self):
        """Test memory monitoring provides accurate information."""
        processor = BatchProcessor()

        # Get initial memory stats
        initial_stats = processor.get_memory_stats()
        assert initial_stats["current_mb"] > 0
        assert initial_stats["peak_mb"] > 0
        assert initial_stats["limit_mb"] == 512  # Default limit
        assert 0 <= initial_stats["usage_percentage"] <= 100

        # Memory usage should be reasonable
        assert (
            initial_stats["current_mb"] < 200
        ), "Initial memory usage should be reasonable"

    def test_batch_processor_stop_functionality(self):
        """Test that batch processing can be stopped mid-operation."""
        urls = [f"http://restaurant{i}.com" for i in range(1, 101)]

        processor = BatchProcessor()

        with patch.object(processor.scraper, "scrape_url") as mock_scrape:

            def slow_mock_scrape(url):
                # Simulate slow processing
                time.sleep(0.1)
                return RestaurantData(name="Test Restaurant", sources=["mock"])

            mock_scrape.side_effect = slow_mock_scrape

            # Start processing in a way that we can stop it
            import threading

            result_container = {}

            def run_processing():
                result_container["result"] = processor.process_batch(urls)

            # Start processing
            thread = threading.Thread(target=run_processing)
            thread.start()

            # Stop after a short time
            time.sleep(0.5)
            processor.stop_processing()

            # Wait for thread to complete
            thread.join(timeout=2.0)

            # Verify processing was stopped
            if "result" in result_container:
                result = result_container["result"]
                # Should have processed fewer than all URLs
                assert (
                    result["total_processed"] < 100
                ), "Processing should have been stopped"
