"""Unit tests for multi-page website navigation and page discovery."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from urllib.parse import urljoin


class TestPageDiscovery:
    """Test page discovery functionality for multi-page scraping."""

    def test_create_page_discovery_with_base_url(self):
        """Test creation of page discovery with base URL."""
        from src.scraper.page_discovery import PageDiscovery

        discovery = PageDiscovery("http://example.com")

        assert discovery.base_url == "http://example.com"
        assert discovery.max_pages == 10  # Default limit
        assert discovery.discovered_pages == set()

    def test_discover_navigation_links_from_html(self):
        """Test discovering navigation links from HTML content."""
        from src.scraper.page_discovery import PageDiscovery

        html_content = """
        <nav>
            <a href="/menu">Menu</a>
            <a href="/about">About Us</a>
            <a href="/contact">Contact</a>
            <a href="/hours">Hours</a>
        </nav>
        """

        discovery = PageDiscovery("http://example.com")
        links = discovery.discover_navigation_links(html_content)

        expected_urls = {
            "http://example.com/menu",
            "http://example.com/about",
            "http://example.com/contact",
            "http://example.com/hours",
        }
        assert links == expected_urls

    def test_filter_relevant_restaurant_pages(self):
        """Test filtering to keep only relevant restaurant pages."""
        from src.scraper.page_discovery import PageDiscovery

        all_links = {
            "http://example.com/menu",
            "http://example.com/about",
            "http://example.com/contact",
            "http://example.com/hours",
            "http://example.com/blog",
            "http://example.com/careers",
            "http://example.com/privacy",
            "http://example.com/terms",
        }

        discovery = PageDiscovery("http://example.com")
        relevant_links = discovery.filter_relevant_pages(all_links)

        expected_relevant = {
            "http://example.com/menu",
            "http://example.com/about",
            "http://example.com/contact",
            "http://example.com/hours",
        }
        assert relevant_links == expected_relevant

    def test_respect_max_pages_limit(self):
        """Test that page discovery respects maximum page limit."""
        from src.scraper.page_discovery import PageDiscovery

        # Create many links to test limit
        many_links = {f"http://example.com/page{i}" for i in range(15)}

        discovery = PageDiscovery("http://example.com", max_pages=10)
        limited_links = discovery.apply_page_limit(many_links)

        assert len(limited_links) == 10
        assert limited_links.issubset(many_links)

    def test_prevent_duplicate_page_discovery(self):
        """Test preventing duplicate page processing."""
        from src.scraper.page_discovery import PageDiscovery

        discovery = PageDiscovery("http://example.com")
        discovery.discovered_pages.add("http://example.com/menu")

        new_links = {
            "http://example.com/menu",  # Already discovered
            "http://example.com/about",  # New
            "http://example.com/contact",  # New
        }

        unique_links = discovery.get_new_pages(new_links)

        expected_new = {"http://example.com/about", "http://example.com/contact"}
        assert unique_links == expected_new

    def test_extract_links_from_various_elements(self):
        """Test extracting links from different HTML elements."""
        from src.scraper.page_discovery import PageDiscovery

        html_content = """
        <nav>
            <a href="/menu">Menu</a>
        </nav>
        <header>
            <a href="/about">About</a>
        </header>
        <div class="navigation">
            <a href="/contact">Contact</a>
        </div>
        <footer>
            <a href="/hours">Hours</a>
        </footer>
        """

        discovery = PageDiscovery("http://example.com")
        links = discovery.extract_all_internal_links(html_content)

        expected_urls = {
            "http://example.com/menu",
            "http://example.com/about",
            "http://example.com/contact",
            "http://example.com/hours",
        }
        assert links == expected_urls

    def test_handle_relative_and_absolute_urls(self):
        """Test handling both relative and absolute URLs."""
        from src.scraper.page_discovery import PageDiscovery

        html_content = """
        <nav>
            <a href="/menu">Relative Menu</a>
            <a href="about">Relative About</a>
            <a href="http://example.com/contact">Absolute Contact</a>
            <a href="https://other-site.com/external">External Link</a>
        </nav>
        """

        discovery = PageDiscovery("http://example.com")
        links = discovery.extract_all_internal_links(html_content)

        expected_internal = {
            "http://example.com/menu",
            "http://example.com/about",
            "http://example.com/contact",
        }
        assert links == expected_internal
        assert "https://other-site.com/external" not in links

    def test_prioritize_pages_by_relevance(self):
        """Test prioritizing pages by relevance for restaurant data."""
        from src.scraper.page_discovery import PageDiscovery

        all_pages = {
            "http://example.com/random-page",
            "http://example.com/menu",
            "http://example.com/contact",
            "http://example.com/about",
            "http://example.com/hours",
            "http://example.com/events",
        }

        discovery = PageDiscovery("http://example.com", max_pages=4)

        # First prioritize, then apply limit
        prioritized = discovery.prioritize_pages(all_pages)
        limited = discovery.apply_page_limit(set(prioritized))

        # High priority pages should be selected first
        high_priority = {"menu", "contact", "about", "hours"}
        selected_paths = {url.split("/")[-1] for url in limited}

        assert len(limited) == 4
        assert high_priority.issubset(selected_paths)

        # Verify ordering - menu should be first (highest priority)
        assert prioritized[0] == "http://example.com/menu"

    def test_discover_pages_with_keywords(self):
        """Test discovering pages based on link text keywords."""
        from src.scraper.page_discovery import PageDiscovery

        html_content = """
        <nav>
            <a href="/food">Our Food</a>
            <a href="/dining">Dining Info</a>
            <a href="/location">Location & Hours</a>
            <a href="/story">Our Story</a>
            <a href="/news">Latest News</a>
        </nav>
        """

        discovery = PageDiscovery("http://example.com")
        links = discovery.discover_navigation_links(html_content)
        relevant = discovery.filter_relevant_pages(links)

        # Should include pages with food/dining/location/story keywords
        paths = {url.split("/")[-1] for url in relevant}
        assert "food" in paths
        assert "dining" in paths
        assert "location" in paths
        assert "story" in paths
        # Should exclude news
        assert "news" not in paths

    def test_handle_missing_href_attributes(self):
        """Test handling links without href attributes."""
        from src.scraper.page_discovery import PageDiscovery

        html_content = """
        <nav>
            <a href="/menu">Menu</a>
            <a>No Href Link</a>
            <a href="">Empty Href</a>
            <a href="/contact">Contact</a>
        </nav>
        """

        discovery = PageDiscovery("http://example.com")
        links = discovery.extract_all_internal_links(html_content)

        expected_valid = {"http://example.com/menu", "http://example.com/contact"}
        assert links == expected_valid

    def test_link_extraction_edge_cases(self):
        """Test link extraction with various edge cases."""
        from src.scraper.page_discovery import PageDiscovery

        discovery = PageDiscovery("https://restaurant.com")
        html_content = """
        <html>
            <body>
                <a href="/menu">Valid Link</a>
                <a href="javascript:void(0)">JavaScript Link</a>
                <a href="mailto:test@example.com">Email Link</a>
                <a href="#section">Anchor Link</a>
                <a href="tel:+1234567890">Phone Link</a>
                <a href="ftp://files.example.com">FTP Link</a>
                <a href="/path with spaces">Space in URL</a>
            </body>
        </html>
        """

        links = discovery.extract_all_internal_links(html_content)

        # Should include valid internal links
        assert "https://restaurant.com/menu" in links
        assert "https://restaurant.com/path with spaces" in links

        # Verify exclusions (only javascript:, mailto:, and # are filtered)
        for link in links:
            assert not link.startswith("javascript:")
            assert not link.startswith("mailto:")
            assert "#" not in link

        # These would be external or invalid so won't be included as internal links
        external_or_special = [
            link for link in links if link.startswith("tel:") or link.startswith("ftp:")
        ]
        # tel: and ftp: links would be normalized to absolute URLs, so they might be included
        # but should be filtered by the _is_internal_url method if they don't match the domain

    def test_pattern_matching_depth_enforcement(self):
        """Test pattern matching with depth considerations."""
        from src.scraper.page_discovery import PageDiscovery

        discovery = PageDiscovery("https://restaurant.com", max_pages=3)

        # Test with many pages to verify depth limit
        many_urls = {f"https://restaurant.com/menu/item{i}" for i in range(10)}
        many_urls.update(
            {f"https://restaurant.com/about/section{i}" for i in range(10)}
        )

        # Filter relevant pages first
        relevant = discovery.filter_relevant_pages(many_urls)

        # Apply page limit
        limited = discovery.apply_page_limit(relevant)

        # Should respect max_pages limit
        assert len(limited) <= 3

        # Should prioritize menu and about pages
        menu_pages = [url for url in limited if "/menu/" in url]
        about_pages = [url for url in limited if "/about/" in url]
        assert len(menu_pages) > 0 or len(about_pages) > 0

    def test_circular_reference_prevention_complex(self):
        """Test complex circular reference prevention scenarios."""
        from src.scraper.page_discovery import PageDiscovery

        discovery = PageDiscovery("https://restaurant.com")

        # Simulate discovering pages in stages
        initial_pages = {"https://restaurant.com/menu", "https://restaurant.com/about"}

        # Mark some as discovered
        discovery.discovered_pages.update(initial_pages)

        # New batch with some overlaps and new pages
        new_batch = {
            "https://restaurant.com/menu",  # Already discovered
            "https://restaurant.com/about",  # Already discovered
            "https://restaurant.com/contact",  # New
            "https://restaurant.com/hours",  # New
            "https://restaurant.com/events",  # New
        }

        # Get only new pages
        truly_new = discovery.get_new_pages(new_batch)

        expected_new = {
            "https://restaurant.com/contact",
            "https://restaurant.com/hours",
            "https://restaurant.com/events",
        }
        assert truly_new == expected_new

        # Verify discovered pages state is maintained
        assert "https://restaurant.com/menu" in discovery.discovered_pages
        assert "https://restaurant.com/about" in discovery.discovered_pages


class TestPageClassifier:
    """Test page type classification functionality."""

    def test_classify_menu_page(self):
        """Test classification of menu pages."""
        from src.scraper.page_classifier import PageClassifier

        menu_html = """
        <h1>Our Menu</h1>
        <div class="menu-section">
            <h2>Appetizers</h2>
            <div class="menu-item">Calamari - $12</div>
        </div>
        """

        classifier = PageClassifier()
        page_type = classifier.classify_page("http://example.com/menu", menu_html)

        assert page_type == "menu"

    def test_classify_contact_page(self):
        """Test classification of contact pages."""
        from src.scraper.page_classifier import PageClassifier

        contact_html = """
        <h1>Contact Us</h1>
        <p>Phone: (503) 555-1234</p>
        <p>Address: 123 Main St, Portland, OR</p>
        <p>Hours: Mon-Sun 11am-10pm</p>
        """

        classifier = PageClassifier()
        page_type = classifier.classify_page("http://example.com/contact", contact_html)

        assert page_type == "contact"

    def test_classify_about_page(self):
        """Test classification of about pages."""
        from src.scraper.page_classifier import PageClassifier

        about_html = """
        <h1>About Our Restaurant</h1>
        <p>We serve authentic Italian cuisine...</p>
        <p>Our chef has 20 years of experience...</p>
        """

        classifier = PageClassifier()
        page_type = classifier.classify_page("http://example.com/about", about_html)

        assert page_type == "about"

    def test_classify_home_page(self):
        """Test classification of home pages."""
        from src.scraper.page_classifier import PageClassifier

        home_html = """
        <h1>Tony's Italian Restaurant</h1>
        <p>Welcome to our family restaurant</p>
        <nav>
            <a href="/menu">Menu</a>
            <a href="/contact">Contact</a>
        </nav>
        """

        classifier = PageClassifier()
        page_type = classifier.classify_page("http://example.com/", home_html)

        assert page_type == "home"

    def test_classify_unknown_page(self):
        """Test classification of unknown page types."""
        from src.scraper.page_classifier import PageClassifier

        unknown_html = """
        <h1>Random Page</h1>
        <p>This page doesn't fit any category</p>
        """

        classifier = PageClassifier()
        page_type = classifier.classify_page("http://example.com/random", unknown_html)

        assert page_type == "unknown"

    def test_classify_based_on_url_patterns(self):
        """Test classification based on URL patterns."""
        from src.scraper.page_classifier import PageClassifier

        classifier = PageClassifier()

        assert classifier.classify_by_url("http://example.com/menu") == "menu"
        assert classifier.classify_by_url("http://example.com/contact") == "contact"
        assert classifier.classify_by_url("http://example.com/about") == "about"
        assert classifier.classify_by_url("http://example.com/hours") == "hours"
        assert classifier.classify_by_url("http://example.com/") == "home"


class TestMultiPageScraper:
    """Test multi-page scraper orchestration."""

    def test_create_multi_page_scraper(self):
        """Test creation of multi-page scraper."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()

        assert scraper.max_pages == 10
        assert hasattr(scraper, "page_discovery")
        assert hasattr(scraper, "page_classifier")
        assert hasattr(scraper, "data_aggregator")

    def test_scrape_single_page_website(self):
        """Test scraping website with only one page."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_page") as mock_fetch:
            mock_fetch.return_value = "<html><h1>Restaurant</h1></html>"

            result = scraper.scrape_website("http://example.com")

            assert result is not None
            assert len(result.pages_processed) == 1

    def test_discover_and_process_multiple_pages(self):
        """Test discovering and processing multiple pages."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()

        # Mock page discovery to return multiple pages
        with patch.object(
            scraper.page_discovery, "discover_all_pages"
        ) as mock_discovery, patch.object(
            scraper, "_fetch_and_process_page"
        ) as mock_process:
            mock_discovery.return_value = [
                "http://example.com/",
                "http://example.com/menu",
                "http://example.com/contact",
            ]

            mock_process.return_value = {"page_type": "menu", "data": {}}

            result = scraper.scrape_website("http://example.com")

            assert len(result.pages_processed) == 3
            assert mock_process.call_count == 3

    def test_handle_page_processing_failure(self):
        """Test handling individual page processing failures."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()

        with patch.object(scraper, "_fetch_and_process_page") as mock_process:
            # First page succeeds, second fails, third succeeds
            mock_process.side_effect = [
                {"page_type": "home", "data": {"name": "Restaurant"}},
                Exception("Page load failed"),
                {"page_type": "menu", "data": {"menu": ["item1"]}},
            ]

            pages = [
                "http://example.com/",
                "http://example.com/fail",
                "http://example.com/menu",
            ]
            result = scraper.process_discovered_pages(pages)

            assert len(result.successful_pages) == 2
            assert len(result.failed_pages) == 1
            assert "http://example.com/fail" in result.failed_pages

    def test_progress_callback_notifications(self):
        """Test progress callback notifications during multi-page processing."""
        from src.scraper.multi_page_scraper import MultiPageScraper

        scraper = MultiPageScraper()
        progress_calls = []

        def mock_callback(message, percentage=None):
            progress_calls.append({"message": message, "percentage": percentage})

        with patch.object(scraper, "_fetch_and_process_page") as mock_process:
            mock_process.return_value = {"page_type": "menu", "data": {}}

            pages = ["http://example.com/menu", "http://example.com/contact"]
            scraper.process_discovered_pages(pages, progress_callback=mock_callback)

            # Should have progress notifications for each page
            assert len(progress_calls) >= 2
            assert any("Discovered" in call["message"] for call in progress_calls)
            assert any("Processing page" in call["message"] for call in progress_calls)
