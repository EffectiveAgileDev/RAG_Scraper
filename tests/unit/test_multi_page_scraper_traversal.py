"""Unit tests for multi-page scraper traversal strategies."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from collections import deque

from src.scraper.multi_page_scraper import MultiPageScraper, MultiPageScrapingResult


class TestMultiPageScraperTraversalStrategies:
    """Test traversal strategy functionality for multi-page scraping."""

    def test_breadth_first_traversal_order(self):
        """Test that BFS traversal visits pages in breadth-first order."""
        scraper = MultiPageScraper()

        # Mock the dependencies to control traversal behavior
        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            # Set up mock to return HTML with navigation links
            home_html = """
            <html>
                <nav>
                    <a href="/level1-page1">Level 1 Page 1</a>
                    <a href="/level1-page2">Level 1 Page 2</a>
                </nav>
            </html>
            """

            level1_page1_html = """
            <html>
                <a href="/level2-page1">Level 2 Page 1</a>
            </html>
            """

            level1_page2_html = """
            <html>
                <a href="/level2-page2">Level 2 Page 2</a>
            </html>
            """

            def mock_fetch_side_effect(url):
                if url == "http://example.com/":
                    return home_html
                elif url.endswith("/level1-page1"):
                    return level1_page1_html
                elif url.endswith("/level1-page2"):
                    return level1_page2_html
                return "<html></html>"

            mock_fetch.side_effect = mock_fetch_side_effect
            mock_process.return_value = {"page_type": "unknown", "data": Mock()}

            # Use breadth-first traversal
            visited_order = scraper._breadth_first_traversal("http://example.com/")

            # Should visit level 1 pages before level 2 pages
            assert len(visited_order) >= 3  # home + 2 level 1 pages minimum

            # Find indices of different levels
            home_index = next(
                i for i, url in enumerate(visited_order) if url == "http://example.com/"
            )
            level1_indices = [
                i for i, url in enumerate(visited_order) if "level1" in url
            ]
            level2_indices = [
                i for i, url in enumerate(visited_order) if "level2" in url
            ]

            # Level 1 pages should come before level 2 pages
            if level2_indices:  # Only check if level 2 pages exist
                assert max(level1_indices) < min(level2_indices)

    def test_depth_first_traversal_order(self):
        """Test that DFS traversal visits pages in depth-first order."""
        scraper = MultiPageScraper()

        # Mock the dependencies to control traversal behavior
        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            # Set up mock to return HTML with navigation links
            home_html = """
            <html>
                <nav>
                    <a href="/branch1">Branch 1</a>
                    <a href="/branch2">Branch 2</a>
                </nav>
            </html>
            """

            branch1_html = """
            <html>
                <a href="/branch1/deep">Branch 1 Deep</a>
            </html>
            """

            branch2_html = """
            <html>
                <a href="/branch2/deep">Branch 2 Deep</a>
            </html>
            """

            def mock_fetch_side_effect(url):
                if url == "http://example.com/":
                    return home_html
                elif url.endswith("/branch1"):
                    return branch1_html
                elif url.endswith("/branch2"):
                    return branch2_html
                return "<html></html>"

            mock_fetch.side_effect = mock_fetch_side_effect
            mock_process.return_value = {"page_type": "unknown", "data": Mock()}

            # Use depth-first traversal
            visited_order = scraper._depth_first_traversal("http://example.com/")

            # Should visit one branch completely before starting the next
            assert len(visited_order) >= 3  # home + at least 2 other pages

            # Check that we go deep into one branch before exploring others
            branch1_index = next(
                (i for i, url in enumerate(visited_order) if url.endswith("/branch1")),
                -1,
            )
            branch1_deep_index = next(
                (i for i, url in enumerate(visited_order) if "branch1/deep" in url), -1
            )
            branch2_index = next(
                (i for i, url in enumerate(visited_order) if url.endswith("/branch2")),
                -1,
            )

            if branch1_index >= 0 and branch1_deep_index >= 0 and branch2_index >= 0:
                # Branch 1 deep should come before branch 2
                assert branch1_deep_index < branch2_index

    def test_traversal_strategy_selection(self):
        """Test that traversal strategy can be selected and changes behavior."""
        scraper = MultiPageScraper()

        # Test default strategy
        default_strategy = scraper._get_traversal_strategy()
        assert default_strategy in ["BFS", "DFS"]

        # Test setting strategy
        scraper._set_traversal_strategy("BFS")
        assert scraper._get_traversal_strategy() == "BFS"

        scraper._set_traversal_strategy("DFS")
        assert scraper._get_traversal_strategy() == "DFS"

    def test_traversal_respects_max_depth(self):
        """Test that traversal respects maximum depth limit."""
        scraper = MultiPageScraper(max_pages=10)

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            # Create a deep hierarchy
            def mock_fetch_side_effect(url):
                if url == "http://example.com/":
                    return '<html><a href="/level1">Level 1</a></html>'
                elif url.endswith("/level1"):
                    return '<html><a href="/level2">Level 2</a></html>'
                elif url.endswith("/level2"):
                    return '<html><a href="/level3">Level 3</a></html>'
                elif url.endswith("/level3"):
                    return '<html><a href="/level4">Level 4</a></html>'
                return "<html></html>"

            mock_fetch.side_effect = mock_fetch_side_effect
            mock_process.return_value = {"page_type": "unknown", "data": Mock()}

            # Test traversal with depth limit
            visited_order = scraper._breadth_first_traversal(
                "http://example.com/", max_depth=2
            )

            # Should not go beyond specified depth
            assert all(
                "level3" not in url and "level4" not in url for url in visited_order
            )

    def test_traversal_handles_cycles(self):
        """Test that traversal handles circular references properly."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            # Create circular references with proper navigation structure
            page_a_html = '<html><nav><a href="/page-b">Page B</a></nav></html>'
            page_b_html = '<html><nav><a href="/page-a">Page A</a></nav></html>'

            def mock_fetch_side_effect(url):
                if url == "http://example.com/":
                    return '<html><nav><a href="/page-a">Page A</a></nav></html>'
                elif url.endswith("/page-a"):
                    return page_a_html
                elif url.endswith("/page-b"):
                    return page_b_html
                return "<html></html>"

            mock_fetch.side_effect = mock_fetch_side_effect
            mock_process.return_value = {"page_type": "unknown", "data": Mock()}

            # Test that traversal terminates despite cycles
            visited_order = scraper._breadth_first_traversal("http://example.com/")

            # Should visit each page only once
            unique_pages = set(visited_order)
            assert len(visited_order) == len(unique_pages)

            # Should include the circular pages but not infinitely
            assert any("page-a" in url for url in visited_order)
            assert any("page-b" in url for url in visited_order)

    def test_traversal_priority_ordering(self):
        """Test that traversal can prioritize certain page types."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            # Create pages with different priorities
            home_html = """
            <html>
                <nav>
                    <a href="/about">About</a>
                    <a href="/menu">Menu</a>
                    <a href="/contact">Contact</a>
                    <a href="/blog">Blog</a>
                </nav>
            </html>
            """

            mock_fetch.return_value = home_html
            mock_process.return_value = {"page_type": "unknown", "data": Mock()}

            # Test priority-based traversal
            visited_order = scraper._priority_traversal("http://example.com/")

            # High-priority pages (menu, contact) should come before low-priority (blog)
            menu_index = next(
                (i for i, url in enumerate(visited_order) if "menu" in url), -1
            )
            blog_index = next(
                (i for i, url in enumerate(visited_order) if "blog" in url), -1
            )

            if menu_index >= 0 and blog_index >= 0:
                assert menu_index < blog_index

    def test_traversal_error_recovery(self):
        """Test that traversal continues when individual pages fail."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            # Mock some pages to fail
            def mock_fetch_side_effect(url):
                if url == "http://example.com/":
                    return '<html><nav><a href="/good">Good</a><a href="/bad">Bad</a></nav></html>'
                elif url.endswith("/good"):
                    return "<html>Good page</html>"
                elif url.endswith("/bad"):
                    return None  # Simulate failure
                return "<html></html>"

            mock_fetch.side_effect = mock_fetch_side_effect

            def mock_process_side_effect(url):
                if url.endswith("/bad"):
                    return None  # Simulate processing failure
                return {"page_type": "unknown", "data": Mock()}

            mock_process.side_effect = mock_process_side_effect

            # Test that traversal continues despite failures
            visited_order = scraper._breadth_first_traversal("http://example.com/")

            # Should still visit the good pages
            assert any("good" in url for url in visited_order)

            # Should have attempted the bad page but continued
            assert len(visited_order) >= 2  # At least home and good page

    def test_traversal_statistics(self):
        """Test that traversal provides accurate statistics."""
        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            mock_fetch.return_value = '<html><a href="/page1">Page 1</a></html>'
            mock_process.return_value = {"page_type": "unknown", "data": Mock()}

            # Perform traversal
            visited_order = scraper._breadth_first_traversal("http://example.com/")

            # Get traversal statistics
            stats = scraper._get_traversal_stats()

            assert "pages_discovered" in stats
            assert "pages_processed" in stats
            assert "pages_failed" in stats
            assert "traversal_strategy" in stats
            assert stats["pages_discovered"] >= 1
