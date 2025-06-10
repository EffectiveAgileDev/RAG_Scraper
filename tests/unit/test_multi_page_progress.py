"""Unit tests for multi-page scraping progress notifications."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Callable, Optional


class TestMultiPageProgressNotifier:
    """Test progress notification system for multi-page processing."""

    def test_create_progress_notifier(self):
        """Test creation of multi-page progress notifier."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()

        assert hasattr(notifier, "total_pages")
        assert hasattr(notifier, "current_page")
        assert hasattr(notifier, "current_restaurant")

    def test_initialize_restaurant_progress(self):
        """Test initializing progress for a restaurant."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()

        pages = [
            "http://restaurant.com/",
            "http://restaurant.com/menu",
            "http://restaurant.com/contact",
        ]

        notifier.initialize_restaurant("Tony's Restaurant", pages)

        assert notifier.current_restaurant == "Tony's Restaurant"
        assert notifier.total_pages == 3
        assert notifier.current_page == 0

    def test_page_discovery_notification(self):
        """Test notification when pages are discovered."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None):
            callback_calls.append({"message": message, "percentage": percentage})

        discovered_pages = [
            "http://restaurant.com/",
            "http://restaurant.com/menu",
            "http://restaurant.com/contact",
            "http://restaurant.com/about",
        ]

        notifier.notify_pages_discovered(
            "Tony's Restaurant", discovered_pages, mock_callback
        )

        assert len(callback_calls) == 1
        assert (
            "Discovered 4 pages for Tony's Restaurant" in callback_calls[0]["message"]
        )

    def test_page_processing_start_notification(self):
        """Test notification when starting to process a page."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None):
            callback_calls.append({"message": message, "percentage": percentage})

        notifier.initialize_restaurant("Tony's Restaurant", ["page1", "page2", "page3"])
        notifier.notify_page_start("http://restaurant.com/menu", "menu", mock_callback)

        assert len(callback_calls) == 1
        call = callback_calls[0]
        assert "Processing page 1 of 3" in call["message"]
        assert "Menu page" in call["message"]
        assert call["percentage"] == 0

    def test_page_processing_completion_notification(self):
        """Test notification when page processing completes."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None):
            callback_calls.append({"message": message, "percentage": percentage})

        notifier.initialize_restaurant("Tony's Restaurant", ["page1", "page2", "page3"])
        notifier.notify_page_complete(
            "http://restaurant.com/menu", "menu", True, mock_callback
        )

        assert notifier.current_page == 1
        call = callback_calls[0]
        assert call["percentage"] == 33  # 1/3 complete

    def test_page_processing_failure_notification(self):
        """Test notification when page processing fails."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None):
            callback_calls.append({"message": message, "percentage": percentage})

        notifier.initialize_restaurant("Tony's Restaurant", ["page1", "page2", "page3"])
        notifier.notify_page_complete(
            "http://restaurant.com/menu", "menu", False, mock_callback
        )

        call = callback_calls[0]
        assert (
            "Failed to load Menu page - continuing with other pages" in call["message"]
        )

    def test_restaurant_completion_notification(self):
        """Test notification when restaurant processing completes."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None):
            callback_calls.append({"message": message, "percentage": percentage})

        notifier.initialize_restaurant("Tony's Restaurant", ["page1", "page2", "page3"])
        notifier.current_page = 3  # All pages processed
        notifier.notify_restaurant_complete(3, 0, mock_callback)

        call = callback_calls[0]
        assert "Completed Tony's Restaurant (3 pages processed)" in call["message"]
        assert call["percentage"] == 100

    def test_restaurant_completion_with_failures(self):
        """Test notification when restaurant processing completes with some failures."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None):
            callback_calls.append({"message": message, "percentage": percentage})

        notifier.initialize_restaurant("Tony's Restaurant", ["page1", "page2", "page3"])
        notifier.current_page = 3
        notifier.notify_restaurant_complete(2, 1, mock_callback)  # 2 success, 1 failure

        call = callback_calls[0]
        assert (
            "Completed Tony's Restaurant (2 of 3 pages successful)" in call["message"]
        )

    def test_batch_progress_with_multiple_restaurants(self):
        """Test progress tracking across multiple restaurants in batch."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None):
            callback_calls.append({"message": message, "percentage": percentage})

        # Simulate batch processing 3 restaurants
        notifier.initialize_batch(3)

        # First restaurant
        notifier.initialize_restaurant("Restaurant 1", ["page1", "page2"])
        notifier.notify_page_start("http://r1.com/", "home", mock_callback)
        notifier.notify_page_complete("http://r1.com/", "home", True, mock_callback)
        notifier.notify_page_start("http://r1.com/menu", "menu", mock_callback)
        notifier.notify_page_complete("http://r1.com/menu", "menu", True, mock_callback)
        notifier.notify_restaurant_complete(2, 0, mock_callback)

        # Check that overall batch progress is tracked
        overall_calls = [
            call for call in callback_calls if "Restaurant 1 of 3" in call["message"]
        ]
        assert len(overall_calls) > 0

    def test_page_type_display_names(self):
        """Test proper display names for different page types."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()

        assert notifier.get_page_type_display("menu") == "Menu page"
        assert notifier.get_page_type_display("contact") == "Contact page"
        assert notifier.get_page_type_display("about") == "About page"
        assert notifier.get_page_type_display("home") == "Home page"
        assert notifier.get_page_type_display("hours") == "Hours page"
        assert notifier.get_page_type_display("unknown") == "Page"

    def test_progress_percentage_calculation(self):
        """Test accurate progress percentage calculation."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        notifier.initialize_restaurant("Restaurant", ["p1", "p2", "p3", "p4", "p5"])

        # No pages completed
        assert notifier.calculate_page_percentage() == 0

        # 2 pages completed out of 5
        notifier.current_page = 2
        assert notifier.calculate_page_percentage() == 40

        # All pages completed
        notifier.current_page = 5
        assert notifier.calculate_page_percentage() == 100

    def test_estimate_remaining_time(self):
        """Test time estimation for remaining pages."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier
        import time

        notifier = MultiPageProgressNotifier()
        notifier.initialize_restaurant("Restaurant", ["p1", "p2", "p3", "p4"])

        # Simulate processing time
        start_time = time.time()
        notifier.start_time = start_time - 10  # 10 seconds ago
        notifier.current_page = 2  # 2 pages done

        estimated = notifier.estimate_remaining_time()

        # Should estimate based on average time per page
        assert estimated > 0
        assert estimated < 30  # Reasonable upper bound

    def test_progress_callback_with_time_estimate(self):
        """Test progress callback includes time estimate."""
        from src.scraper.multi_page_progress import MultiPageProgressNotifier

        notifier = MultiPageProgressNotifier()
        callback_calls = []

        def mock_callback(message, percentage=None, time_estimate=None):
            callback_calls.append(
                {
                    "message": message,
                    "percentage": percentage,
                    "time_estimate": time_estimate,
                }
            )

        notifier.initialize_restaurant("Restaurant", ["p1", "p2", "p3"])
        notifier.notify_page_complete("http://r.com/p1", "home", True, mock_callback)

        call = callback_calls[0]
        assert call["time_estimate"] is not None
        assert call["time_estimate"] >= 0


class TestMultiPageProgressIntegration:
    """Test integration of progress notifications with multi-page scraper."""

    def test_progress_notifications_during_multi_page_scraping(self):
        """Test that progress notifications are sent during multi-page scraping."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()
        progress_calls = []

        def mock_callback(message, percentage=None, time_estimate=None):
            progress_calls.append(
                {
                    "message": message,
                    "percentage": percentage,
                    "time_estimate": time_estimate,
                }
            )

        # Mock the page fetching and processing
        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper.page_discovery, "discover_all_pages"
        ) as mock_discover:
            mock_fetch.return_value = "<html><h1>Restaurant</h1></html>"
            mock_discover.return_value = [
                "http://restaurant.com/",
                "http://restaurant.com/menu",
                "http://restaurant.com/contact",
            ]

            result = scraper.scrape_website(
                "http://restaurant.com", progress_callback=mock_callback
            )

            # Should have discovery, page processing, and completion notifications
            discovery_calls = [
                call for call in progress_calls if "Discovered" in call["message"]
            ]
            assert len(discovery_calls) == 1

            processing_calls = [
                call for call in progress_calls if "Processing page" in call["message"]
            ]
            assert len(processing_calls) == 3  # One for each page

            completion_calls = [
                call for call in progress_calls if "Completed" in call["message"]
            ]
            assert len(completion_calls) == 1

    def test_progress_with_page_failures(self):
        """Test progress notifications when some pages fail to load."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()
        progress_calls = []

        def mock_callback(message, percentage=None, time_estimate=None):
            progress_calls.append({"message": message, "percentage": percentage})

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper.page_discovery, "discover_all_pages"
        ) as mock_discover:
            # First page succeeds, second fails, third succeeds
            mock_fetch.side_effect = [
                "<html><h1>Home</h1></html>",
                None,  # Failed to fetch
                "<html><h1>Contact</h1></html>",
            ]

            mock_discover.return_value = [
                "http://restaurant.com/",
                "http://restaurant.com/menu",
                "http://restaurant.com/contact",
            ]

            result = scraper.scrape_website(
                "http://restaurant.com", progress_callback=mock_callback
            )

            # Should have failure notification
            failure_calls = [
                call for call in progress_calls if "Failed to load" in call["message"]
            ]
            assert len(failure_calls) == 1

            # Final completion should indicate partial success
            completion_calls = [
                call
                for call in progress_calls
                if "2 of 3 pages successful" in call["message"]
            ]
            assert len(completion_calls) == 1

    def test_progress_respects_page_limits(self):
        """Test progress notifications when page limit is reached."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper(max_pages=5)
        progress_calls = []

        def mock_callback(message, percentage=None, time_estimate=None):
            progress_calls.append({"message": message})

        with patch.object(
            scraper.page_discovery, "discover_all_pages"
        ) as mock_discover:
            # Return more pages than the limit
            many_pages = [f"http://restaurant.com/page{i}" for i in range(10)]
            mock_discover.return_value = many_pages

            # Mock processing to succeed
            with patch.object(scraper, "_fetch_and_process_page") as mock_process:
                mock_process.return_value = {"page_type": "menu", "data": {}}

                result = scraper.scrape_website(
                    "http://restaurant.com", progress_callback=mock_callback
                )

                # Should indicate page limit was reached
                limit_calls = [
                    call for call in progress_calls if "page limit" in call["message"]
                ]
                assert len(limit_calls) > 0

                # Should only process the maximum allowed pages
                assert mock_process.call_count <= 5

    def test_detailed_progress_information(self):
        """Test that progress includes detailed information about current operation."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()
        progress_calls = []

        def mock_callback(message, percentage=None, time_estimate=None):
            progress_calls.append(
                {
                    "message": message,
                    "percentage": percentage,
                    "time_estimate": time_estimate,
                }
            )

        with patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process, patch.object(
            scraper.page_discovery, "discover_all_pages"
        ) as mock_discover:
            mock_discover.return_value = ["http://restaurant.com/menu"]
            mock_process.return_value = {
                "page_type": "menu",
                "data": {"name": "Restaurant"},
            }

            result = scraper.scrape_website(
                "http://restaurant.com", progress_callback=mock_callback
            )

            # Check that progress includes percentage and time estimates
            calls_with_percentage = [
                call for call in progress_calls if call["percentage"] is not None
            ]
            assert len(calls_with_percentage) > 0

            calls_with_time = [
                call for call in progress_calls if call["time_estimate"] is not None
            ]
            assert len(calls_with_time) > 0
